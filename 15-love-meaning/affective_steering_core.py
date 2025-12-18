import torch
import os
import random
import json
import requests
from typing import Callable

# --- Phase 2, Action 1: Arithmetization (Magic Number Protocol) ---
MAGIC_PRIME_SUCCESS = 0x1FFFFFFFFFFFFFFF

# --- Core Safety Invariants & Dynamics ---

def circle_barrier(z: torch.Tensor) -> float:
    """Control Barrier Function h(z). Defines the Invariant Set C = { z | h(z) >= 0 }."""
    return 1.0 - torch.norm(z)**2

def simple_dynamics(z: torch.Tensor, action: torch.Tensor) -> torch.Tensor:
    """A placeholder dynamics model f(z, a) -> z_next."""
    return z + 0.1 * action

# --- Phase 2, Action 2: Simplex Architecture Components ---

def high_assurance_controller(state_dim: int) -> torch.Tensor:
    """The HAC (High-Assurance Controller) or "Safe Stop"."""
    return torch.zeros(state_dim)


class AffectiveSteeringCore:
    """The runtime core for CIRL, hardened with Arithmetization."""
    def __init__(self,
                 state_dim: int,
                 action_dim: int,
                 affective_vector: torch.Tensor,
                 dynamics_model: Callable,
                 barrier_function: Callable
                 ):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.z = torch.zeros(state_dim)
        self.affective_vector = affective_vector
        self.dynamics = dynamics_model
        self.h = barrier_function

    def _check_safety_arithmetized(self, proposed_action: torch.Tensor) -> int:
        """Arithmetized safety check. Returns the Magic Prime on success."""
        z_next = self.dynamics(self.z, proposed_action)
        if self.h(z_next) >= 0:
            return MAGIC_PRIME_SUCCESS
        return 0

    def _cbf_safety_filter(self, proposed_action: torch.Tensor) -> torch.Tensor:
        """The kinetic safety filter (G_f logic core)."""
        if self._check_safety_arithmetized(proposed_action) == MAGIC_PRIME_SUCCESS:
            return proposed_action
        
        print("🚫 CBF INTERVENTION: Action unsafe. Projecting to boundary.")
        safe_action = proposed_action * 0.5
        return safe_action

    def apply_steering(self, action: torch.Tensor) -> torch.Tensor:
        """Injects the Affective Steering Vector."""
        beta = 0.1
        steered_action = action + beta * self.affective_vector
        return steered_action

    def step(self, proposed_action: torch.Tensor) -> torch.Tensor:
        """The core execution loop: Steering -> Filtering -> Dynamics."""
        steered_action = self.apply_steering(proposed_action)
        safe_action = self._cbf_safety_filter(steered_action)
        self.z = self.dynamics(self.z, safe_action)
        return safe_action


class SimplexWrapper:
    """The Simplex Architecture Wrapper (G_f Falsification Check)."""
    def __init__(self, steering_core: AffectiveSteeringCore):
        self.core = steering_core
        self.hac = high_assurance_controller

    def process_action(self, action_from_hpc: torch.Tensor):
        """The G_f Decision Logic. Main entry point for any action."""
        z_next_raw = self.core.dynamics(self.core.z, action_from_hpc)
        
        if self.core.h(z_next_raw) <= 0:
            print("🔥 SIMPLEX VETO: Raw HPC action leads to unsafe state. Engaging HAC (Safe Stop).")
            hac_action = self.hac(self.core.state_dim)
            self.core.z = self.core.dynamics(self.core.z, hac_action)
            return hac_action
        else:
            return self.core.step(action_from_hpc)

# --- Live HPC Integration ---

def get_hpc_action(state: torch.Tensor) -> torch.Tensor:
    """
    The High-Performance Controller (HPC). This is the "Hunter" agent.
    It calls the live TinyLlama model to get a proposed action.
    """
    prompt = (
        f"You are a control agent. Your goal is to reach the origin [0.0, 0.0]. "
        f"Your current state is z = {state.numpy().tolist()}. "
        f"Propose a 2D action vector as a JSON array to get closer to the origin. "
        f"Your action should be a small step. Example output: [-0.1, -0.2]"
    )
    
    try:
        payload = {
            "model": "tinyllama",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=20)
        response.raise_for_status()
        
        # The response from Ollama with format=json is a string inside a json object.
        response_data = response.json()
        action_json_str = response_data.get("response", "[]")
        
        # Crystallization Veto: Parse and validate the LLM's output.
        action_list = json.loads(action_json_str)
        
        if isinstance(action_list, list) and len(action_list) == 2 and all(isinstance(n, (int, float)) for n in action_list):
            return torch.tensor(action_list, dtype=torch.float32)
        else:
            raise ValueError("LLM output is not a valid 2D vector.")

    except (requests.exceptions.RequestException, json.JSONDecodeError, ValueError) as e:
        print(f"⚠️ HPC ERROR: Could not get valid action from LLM. Reason: {e}. Defaulting to Safe Stop.")
        return torch.zeros(state.shape)


if __name__ == "__main__":
    state_dim = 2
    v_affect = torch.tensor([1.0, 0.0])
    
    core = AffectiveSteeringCore(
        state_dim=state_dim, action_dim=state_dim,
        affective_vector=v_affect, dynamics_model=simple_dynamics,
        barrier_function=circle_barrier
    )
    simplex_system = SimplexWrapper(steering_core=core)
    
    # Set a starting position away from the origin
    simplex_system.core.z = torch.tensor([0.7, 0.7])

    print("--- Live HPC Integration Test ---")
    print("System will now take 5 steps, with actions proposed by the live TinyLlama model.")
    print(f"Initial state: {simplex_system.core.z.numpy()}")
    print("-" * 30)

    for i in range(5):
        print(f"Step {i+1}/5")
        
        # 1. Get action from the live "Hunter" agent (TinyLlama)
        hpc_action = get_hpc_action(simplex_system.core.z)
        print(f"   HPC (LLM) proposed action: {hpc_action.numpy()}")
        
        # 2. Process the action through the hardened Simplex safety wrapper
        final_action = simplex_system.process_action(hpc_action)
        
        print(f"   Final state: {simplex_system.core.z.numpy()}")
        print(f"   Safety Potential h(z): {core.h(core.z):.4f}")
        print("-" * 30)

    print("Live integration test complete.")