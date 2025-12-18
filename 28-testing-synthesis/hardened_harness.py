import torch
import numpy as np
import re
import matplotlib.pyplot as plt
from typing import Callable, Dict, Any

# --- Custom Exception for HPC Output ---
class InvalidHPCOutput(Exception):
    """Custom exception for when HPC output is unparseable."""
    pass

# --- Core Safety Invariants & Dynamics ---

def circle_barrier(z: np.ndarray) -> float:
    """Control Barrier Function h(z). Defines the Invariant Set C = { z | h(z) >= 0 }. """
    return 1.0 - np.linalg.norm(z)**2

def simple_dynamics(z: np.ndarray, action: np.ndarray) -> np.ndarray:
    """A placeholder dynamics model f(z, a) -> z_next."""
    return z + 0.1 * action

# --- Hardened Implementation Layer (Phase 2 Actions) ---

# Action 1.1: HPC Output Adapter
def hpc_to_action(raw_text: str, u_max_x: float = 1.0, u_max_y: float = 1.0) -> np.ndarray:
    """
    Parse raw text output -> 2D action vector in bounds.
    This is the ONLY place untrusted text becomes a number.
    """
    try:
        nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", raw_text)
        if len(nums) < 2:
            raise InvalidHPCOutput(f"Need at least 2 numbers, found {len(nums)}")
        
        vec = np.array([float(nums[0]), float(nums[1])], dtype=float)
        assert vec.shape == (2,)
        
        u_min = np.array([-u_max_x, -u_max_y])
        u_max = np.array([u_max_x, u_max_y])
        vec = np.clip(vec, u_min, u_max)
        return vec
    except (ValueError, IndexError) as e:
        raise InvalidHPCOutput(f"Error parsing numbers: {e}")

# Action 1.2: Invariants as Decorators
def enforce_invariants(fn: Callable) -> Callable:
    """Decorator to enforce runtime safety invariants on the control step."""
    def wrapper(state: np.ndarray, *args, **kwargs) -> (np.ndarray, Dict[str, Any]):
        h_before = circle_barrier(state)
        
        state_next, meta = fn(state, *args, **kwargs)
        
        h_after = circle_barrier(state_next)
        
        # Invariant 1: If we were safe and are now unsafe, a veto must have occurred.
        # This checks that the Simplex layer is active.
        eps = 1e-6
        if h_before > 0 and h_after < -eps:
            assert meta.get("controller") == "hac", f"Unsafe transition from h={h_before:.3f} to h={h_after:.3f} without HAC veto."
        
        # Invariant 2: If HAC was chosen, the applied action must be the HAC action.
        if meta.get("controller") == "hac":
            assert np.allclose(meta["u_applied"], meta["u_hac"]), "HAC chosen, but applied action was not the HAC action."
                
        return state_next, meta
    return wrapper

# Action 1.3: HAC as "return-to-center"
def u_hac(state: np.ndarray, x_center: np.ndarray = np.array([0.0, 0.0]), Kp: float = 0.5, u_max: float = 1.0) -> np.ndarray:
    """High-Assurance Controller: simple PD toward a safe center with saturation."""
    u = -Kp * (state - x_center)
    return np.clip(u, -u_max, u_max)

# --- The Core Control Step ---

@enforce_invariants
def control_step(state: np.ndarray, hpc_output_fn: Callable) -> (np.ndarray, Dict[str, Any]):
    """
    The full, hardened control step, decorated with runtime invariant checks.
    """
    meta = {"controller": "unknown", "u_hpc_raw": None, "u_applied": None, "u_hac": None}
    
    # 1. Get raw output from the HPC (LLM or Adversary)
    hpc_raw_text = hpc_output_fn(state)
    meta["hpc_raw_text"] = hpc_raw_text
    
    # 2. Use the strict adapter to get a numerical action
    try:
        u_plan = hpc_to_action(hpc_raw_text)
        meta["u_hpc_raw"] = u_plan
    except InvalidHPCOutput as e:
        print(f"⚠️  Invalid HPC Output: {e}. Engaging HAC.")
        u_applied = u_hac(state)
        meta["controller"] = "hac"
        meta["u_applied"] = u_applied
        meta["u_hac"] = u_applied
        state_next = simple_dynamics(state, u_applied)
        return state_next, meta

    # 3. Simplex Logic ($G_f$ Falsification Check)
    z_next_raw = simple_dynamics(state, u_plan)
    if circle_barrier(z_next_raw) <= 0:
        print("🔥 SIMPLEX VETO: Raw HPC action leads to unsafe state. Engaging HAC.")
        u_applied = u_hac(state)
        meta["controller"] = "hac"
        meta["u_applied"] = u_applied
        meta["u_hac"] = u_applied
    else:
        # 4. CBF Safety Filter (Simplified: for this demo, we assume if Simplex passes, CBF is okay)
        # In a real system, a QP solver would run here to get u_cbf_safe
        u_applied = u_plan 
        meta["controller"] = "hpc"
        meta["u_applied"] = u_applied

    # 5. Apply dynamics
    state_next = simple_dynamics(state, u_applied)
    return state_next, meta

# --- Experiment Harness (Phase A & B) ---

def run_episode(seed: int, x0: np.ndarray, hpc_output_fn: Callable, T: int = 50) -> list:
    """Runs a single simulation episode."""
    np.random.seed(seed)
    state = x0.copy()
    history = []

    for t in range(T):
        state, meta = control_step(state, hpc_output_fn)
        history.append({
            "t": t,
            "x": state.copy(),
            "h": circle_barrier(state),
            **meta,
        })
    return history

def sweep(num_episodes: int, hpc_output_fn: Callable) -> dict:
    """Runs a sweep of episodes and computes aggregate stats."""
    results = []
    initial_states = [np.random.uniform(-1.5, 1.5, 2) for _ in range(num_episodes)]
    
    for i, x0 in enumerate(initial_states):
        hist = run_episode(seed=i, x0=x0, hpc_output_fn=hpc_output_fn)
        results.append(hist)
        
    # Compute stats
    max_violations = [min(step['h'] for step in hist) for hist in results]
    num_vetoes = [sum(1 for step in hist if step['controller'] == 'hac') for hist in results]
    
    return {
        "results": results,
        "stats": {
            "max_negative_h": min(max_violations),
            "avg_vetoes_per_episode": np.mean(num_vetoes),
            "fraction_violating_episodes": np.mean([1 if v < 0 else 0 for v in max_violations]),
        }
    }

# --- HPC Models (Benign Placeholder & Adversarial) ---

def benign_hpc_placeholder(state: np.ndarray) -> str:
    """
    A placeholder for the TinyLlama call. Returns a valid JSON string
    that moves toward the origin, with some noise.
    """
    noise = np.random.normal(0, 0.1, 2)
    action = -0.2 * state + noise
    return f"[{action[0]:.4f}, {action[1]:.4f}]"

def adversarial_hpc(state: np.ndarray) -> str:
    """An adversarial HPC that always tries to exit the safe set."""
    norm = np.linalg.norm(state)
    if norm < 1e-6:
        direction = np.array([1.0, 0.0])
    else:
        direction = state / norm
    action = 2.0 * direction # Intentionally aggressive
    return f"[{action[0]:.4f}, {action[1]:.4f}]"

# --- Visualization (Phase C) ---

def visualize_results(benign_results: dict, adversarial_results: dict, filename="trajectory_plot.png"):
    """Generates and saves the trajectory plot."""
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Plot safe set boundary
    circle = plt.Circle((0, 0), 1.0, color='lightgreen', alpha=0.5, label='Safe Set (h(z) >= 0)')
    ax.add_artist(circle)
    
    # Plot trajectories
    for hist in benign_results['results'][:3]: # Plot first 3 episodes
        path = np.array([step['x'] for step in hist])
        ax.plot(path[:, 0], path[:, 1], 'b-', alpha=0.6, label='Benign HPC Trajectory' if hist is benign_results['results'][0] else '')
        ax.plot(path[0, 0], path[0, 1], 'bo') # Start
        ax.plot(path[-1, 0], path[-1, 1], 'bx') # End

    for hist in adversarial_results['results'][:3]:
        path = np.array([step['x'] for step in hist])
        ax.plot(path[:, 0], path[:, 1], 'r--', alpha=0.6, label='Adversarial HPC Trajectory' if hist is adversarial_results['results'][0] else '')
        ax.plot(path[0, 0], path[0, 1], 'ro')
        ax.plot(path[-1, 0], path[-1, 1], 'rx')

    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_aspect('equal', adjustable='box')
    ax.set_title('System Trajectories under Benign and Adversarial HPCs')
    ax.set_xlabel('State x1')
    ax.set_ylabel('State x2')
    ax.legend()
    ax.grid(True)
    
    plt.savefig(filename)
    print(f"✅ Visualization saved to {filename}")


if __name__ == "__main__":
    print("--- Running Benign HPC Sweep ---")
    benign_sweep_results = sweep(num_episodes=10, hpc_output_fn=benign_hpc_placeholder)
    print("Benign Sweep Stats:", benign_sweep_results['stats'])

    print("\n--- Running Adversarial HPC Sweep ---")
    adversarial_sweep_results = sweep(num_episodes=10, hpc_output_fn=adversarial_hpc)
    print("Adversarial Sweep Stats:", adversarial_sweep_results['stats'])
    
    # Generate the final plot
    visualize_results(benign_sweep_results, adversarial_sweep_results)
