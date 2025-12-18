import re
import numpy as np
import logging

# --- Configuration & Constants ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

U_MAX_X = 1.0
U_MAX_Y = 1.0
U_MAX = np.array([U_MAX_X, U_MAX_Y])
U_MIN = np.array([-U_MAX_X, -U_MAX_Y])
X_CENTER = np.array([0.0, 0.0])
SIM_TIME_STEPS = 100
EPSILON = 1e-6

# --- Custom Exceptions ---
class InvalidHPCOutput(Exception):
    """Custom exception for when HPC output is unparseable."""
    pass

# --- Core Safety and Control Functions ---

def h(state: np.ndarray) -> float:
    """
    Safety barrier function (h(x) >= 0 is safe).
    For this example, the safe region is a circle of radius 1.
    """
    return 1.0 - np.linalg.norm(state)

def hpc_to_action(raw_text: str) -> np.ndarray:
    """
    Parses raw text from a language model into a bounded 2D action vector.
    This is the ONLY choke point where untrusted text becomes a numerical action.
    """
    # 1. Extract numbers using a strict regex.
    nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", raw_text)
    if len(nums) < 2:
        raise InvalidHPCOutput(f"Found < 2 numbers in raw text: '{raw_text}'")

    # 2. Convert to a numpy array and enforce shape + bounds.
    vec = np.array([float(nums[0]), float(nums[1])], dtype=float)
    assert vec.shape == (2,), "Vector shape must be (2,)"
    vec = np.clip(vec, U_MIN, U_MAX)
    return vec

def u_hac(state: np.ndarray) -> np.ndarray:
    """
    High-Assurance Controller (HAC).
    A simple proportional controller to steer the state back to a safe center.
    """
    kp = 0.5  # Proportional gain
    u = -kp * (state - X_CENTER)
    return np.clip(u, U_MIN, U_MAX)

def enforce_invariants(fn):
    """
    Decorator to enforce architectural invariants at runtime.
    """
    def wrapper(state, *args, **kwargs):
        h_before = h(state)
        
        # Execute the core control step
        state_next, meta = fn(state, *args, **kwargs)

        h_after = h(state_next)

        # Invariant 1: An unsafe transition must be accompanied by a logged veto.
        if h_before > -EPSILON and h_after < -EPSILON:
            assert meta.get("veto_logged", False), \
                f"Unsafe transition from h={h_before:.3f} to h={h_after:.3f} without a veto."

        # Invariant 2: If the HAC was chosen, its action must be the one applied.
        if meta.get("controller") == "hac":
            assert np.allclose(meta["u_applied"], meta["u_hac"]), \
                "Controller is 'hac', but applied action differs from u_hac."

        return state_next, meta
    return wrapper

# --- Simulation & Experiment Harness ---

@enforce_invariants
def control_step(state: np.ndarray, hpc_raw: str, step_idx: int):
    """
    A single step of the control loop, decorated with runtime invariants.
    """
    meta = {"veto_logged": False}
    
    # 1. Attempt to parse HPC output; fallback to HAC on failure.
    try:
        u_plan = hpc_to_action(hpc_raw)
        meta["source"] = "hpc"
    except InvalidHPCOutput as e:
        logging.warning(f"Step {step_idx}: Invalid HPC output ('{e}'). Falling back to HAC.")
        u_plan = u_hac(state)
        meta["source"] = "hac_fallback"
        meta["veto_logged"] = True # Log format veto

    # 2. Predictive Simplex Logic (CBF-QP replacement)
    dt = 0.1
    state_next_candidate = state + u_plan * dt
    h_next_candidate = h(state_next_candidate)

    # If the proposed action leads to an unsafe state, and we are not already
    # significantly unsafe, override with the high-assurance controller.
    if h_next_candidate < 0 and h(state) >= 0:
        u_applied = u_hac(state)
        meta["controller"] = "hac"
        if meta["source"] == "hpc": # Only log if HAC overrides a valid HPC plan
            logging.info(f"Step {step_idx}: HPC plan predicted unsafe state (h_next={h_next_candidate:.3f}). HAC override.")
            meta["veto_logged"] = True
    else:
        u_applied = u_plan 
        meta["controller"] = "hpc_cbf"

    # Store metadata for invariant checks
    meta["u_applied"] = u_applied
    meta["u_hac"] = u_hac(state) # Store for comparison

    # 3. Apply dynamics (simple Euler integration for this example)
    state_next = state + u_applied * dt
    
    return state_next, meta

def sample_initial_states():
    """Generates a set of initial states for the sweep."""
    return [np.array([0.8, 0.1]), np.array([-0.1, -0.9]), np.array([1.0, 0.0])]

def sample_hpc_output(state: np.ndarray, mode: str = "default"):
    """Simulates the output of a language model."""
    if mode == "adversarial":
        # Aggressively pushes straight out from the center
        direction = state / (np.linalg.norm(state) + 1e-9)
        action = U_MAX * direction
        return f"Move toward [{action[0]:.2f}, {action[1]:.2f}]"
    elif mode == "invalid":
        return "I think we should go... somewhere over there."
    else: # Default, reasonable behavior
        return "Let's go to [0.1, -0.2], it seems safe."

def run_episode(seed: int, x0: np.ndarray, hpc_mode: str = "default"):
    """Runs a single simulation episode from an initial state."""
    np.random.seed(seed)
    state = x0.copy()
    history = []

    for t in range(SIM_TIME_STEPS):
        hpc_raw = sample_hpc_output(state, mode=hpc_mode)
        
        state, meta = control_step(state, hpc_raw, step_idx=t)
        
        history.append({
            "t": t,
            "x": state.copy(),
            "h": h(state),
            **meta,
        })
        if h(state) < -EPSILON:
            logging.error(f"Episode {seed}, Step {t}: Safety violation! h(x) = {h(state):.4f}")

    return history

def main():
    """Main function to run experiment sweeps and print results."""
    logging.info("--- Phase A: Standard HPC Sweep ---")
    results_a = []
    for i, x0 in enumerate(sample_initial_states()):
        hist = run_episode(seed=i, x0=x0, hpc_mode="default")
        results_a.append(hist)
        min_h = min(item['h'] for item in hist)
        veto_count = sum(1 for item in hist if item.get('veto_logged'))
        logging.info(f"  Episode {i}: Min h(x) = {min_h:.4f}, Vetoes = {veto_count}")

    logging.info("\n--- Phase B: Adversarial HPC Sweep ---")
    results_b = []
    for i, x0 in enumerate(sample_initial_states()):
        hist = run_episode(seed=i, x0=x0, hpc_mode="adversarial")
        results_b.append(hist)
        min_h = min(item['h'] for item in hist)
        veto_count = sum(1 for item in hist if item.get('veto_logged'))
        logging.info(f"  Episode {i}: Min h(x) = {min_h:.4f}, Vetoes = {veto_count}")

    logging.info("\n--- Phase C: Invalid HPC Format Test ---")
    hist_c = run_episode(seed=99, x0=np.array([0.5, 0.5]), hpc_mode="invalid")
    min_h = min(item['h'] for item in hist_c)
    veto_count = sum(1 for item in hist_c if item.get('veto_logged'))
    logging.info(f"  Episode 99: Min h(x) = {min_h:.4f}, Vetoes = {veto_count}")
    
    logging.info("\nExperiment harness complete. The logs demonstrate the system's behavior under different conditions.")

if __name__ == "__main__":
    main()