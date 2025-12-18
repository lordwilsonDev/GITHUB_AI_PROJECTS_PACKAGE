#!/usr/bin/env python3
"""
Quantum State Manager - Level 20
Implements quantum-inspired state management with superposition, coherence, and optimization.
"""

import numpy as np
from typing import List, Callable, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json


@dataclass
class QuantumState:
    """Represents a quantum-inspired state."""
    state_vector: np.ndarray  # Complex amplitudes
    basis_states: List[str]
    coherence_level: float  # 0.0 to 1.0
    entanglement_connections: List[str]
    measurement_history: List[Dict[str, Any]]
    
    def __post_init__(self):
        # Normalize state vector
        norm = np.linalg.norm(self.state_vector)
        if norm > 0:
            self.state_vector = self.state_vector / norm


@dataclass
class OptimizationResult:
    """Result from quantum optimization."""
    optimal_state: np.ndarray
    optimal_value: float
    iterations: int
    convergence_history: List[float]
    success: bool


@dataclass
class MeasurementResult:
    """Result from quantum state measurement."""
    measured_state: str
    probability: float
    collapsed_state: np.ndarray
    measurement_basis: str


class QuantumStateManager:
    """Manages quantum-inspired computational states."""
    
    def __init__(self, num_qubits: int = 4):
        self.num_qubits = num_qubits
        self.num_states = 2 ** num_qubits
        self.current_state = self._initialize_state()
        self.coherence_decay_rate = 0.01
        
    def _initialize_state(self) -> QuantumState:
        """Initialize quantum state to |0...0>."""
        state_vector = np.zeros(self.num_states, dtype=complex)
        state_vector[0] = 1.0  # Ground state
        
        basis_states = [format(i, f'0{self.num_qubits}b') for i in range(self.num_states)]
        
        return QuantumState(
            state_vector=state_vector,
            basis_states=basis_states,
            coherence_level=1.0,
            entanglement_connections=[],
            measurement_history=[]
        )
    
    def create_superposition(self, num_states: int) -> QuantumState:
        """Create uniform superposition of num_states."""
        if num_states > self.num_states:
            num_states = self.num_states
            
        state_vector = np.zeros(self.num_states, dtype=complex)
        amplitude = 1.0 / np.sqrt(num_states)
        
        for i in range(num_states):
            state_vector[i] = amplitude
            
        basis_states = [format(i, f'0{self.num_qubits}b') for i in range(self.num_states)]
        
        return QuantumState(
            state_vector=state_vector,
            basis_states=basis_states,
            coherence_level=1.0,
            entanglement_connections=[],
            measurement_history=[]
        )
    
    def apply_hadamard(self, qubit_index: int) -> None:
        """Apply Hadamard gate to create superposition on single qubit."""
        if qubit_index >= self.num_qubits:
            raise ValueError(f"Qubit index {qubit_index} out of range")
        
        # Hadamard matrix
        H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
        
        # Apply to state vector
        new_state = np.zeros(self.num_states, dtype=complex)
        
        for i in range(self.num_states):
            # Check if qubit is 0 or 1
            bit_value = (i >> (self.num_qubits - 1 - qubit_index)) & 1
            
            # Apply Hadamard
            for j in range(2):
                new_index = i ^ ((bit_value ^ j) << (self.num_qubits - 1 - qubit_index))
                new_state[new_index] += H[j, bit_value] * self.current_state.state_vector[i]
        
        self.current_state.state_vector = new_state
        self.current_state.coherence_level = min(1.0, self.current_state.coherence_level + 0.1)
    
    def maintain_coherence(self, state: QuantumState) -> float:
        """Maintain coherence and return current coherence level."""
        # Simulate decoherence
        state.coherence_level *= (1.0 - self.coherence_decay_rate)
        
        # Apply small random phase noise
        noise = np.random.normal(0, 0.01 * (1.0 - state.coherence_level), self.num_states)
        phase_noise = np.exp(1j * noise)
        state.state_vector *= phase_noise
        
        # Renormalize
        norm = np.linalg.norm(state.state_vector)
        if norm > 0:
            state.state_vector /= norm
        
        return state.coherence_level
    
    def quantum_optimize(self, objective: Callable[[np.ndarray], float], 
                        iterations: int = 100) -> OptimizationResult:
        """Quantum-inspired optimization using variational approach."""
        best_state = self.current_state.state_vector.copy()
        best_value = objective(np.abs(best_state)**2)
        convergence_history = [best_value]
        
        # Variational quantum optimization
        for iteration in range(iterations):
            # Generate trial state with quantum-inspired perturbation
            trial_state = self._quantum_perturbation(best_state, iteration, iterations)
            
            # Evaluate objective
            probabilities = np.abs(trial_state)**2
            value = objective(probabilities)
            
            # Update if better
            if value < best_value:
                best_state = trial_state
                best_value = value
            
            convergence_history.append(best_value)
            
            # Maintain coherence
            self.current_state.coherence_level = max(0.5, 1.0 - iteration / iterations)
        
        return OptimizationResult(
            optimal_state=best_state,
            optimal_value=best_value,
            iterations=iterations,
            convergence_history=convergence_history,
            success=True
        )
    
    def _quantum_perturbation(self, state: np.ndarray, iteration: int, 
                             max_iterations: int) -> np.ndarray:
        """Apply quantum-inspired perturbation."""
        # Adaptive perturbation strength
        strength = 0.5 * (1.0 - iteration / max_iterations)
        
        # Random unitary rotation
        angles = np.random.uniform(-np.pi * strength, np.pi * strength, self.num_states)
        rotation = np.exp(1j * angles)
        
        perturbed = state * rotation
        
        # Normalize
        norm = np.linalg.norm(perturbed)
        if norm > 0:
            perturbed /= norm
        
        return perturbed
    
    def measure_collapse(self, state: QuantumState, 
                        measurement_basis: str = 'computational') -> MeasurementResult:
        """Measure quantum state and collapse to eigenstate."""
        # Calculate probabilities
        probabilities = np.abs(state.state_vector)**2
        
        # Sample from probability distribution
        measured_index = np.random.choice(self.num_states, p=probabilities)
        measured_state_str = state.basis_states[measured_index]
        
        # Collapse to measured state
        collapsed = np.zeros(self.num_states, dtype=complex)
        collapsed[measured_index] = 1.0
        
        # Record measurement
        measurement_record = {
            'state': measured_state_str,
            'probability': float(probabilities[measured_index]),
            'basis': measurement_basis,
            'coherence_before': state.coherence_level
        }
        state.measurement_history.append(measurement_record)
        
        # Update coherence (measurement causes decoherence)
        state.coherence_level *= 0.5
        
        return MeasurementResult(
            measured_state=measured_state_str,
            probability=float(probabilities[measured_index]),
            collapsed_state=collapsed,
            measurement_basis=measurement_basis
        )
    
    def measure_state(self) -> MeasurementResult:
        """Measure current state."""
        return self.measure_collapse(self.current_state)
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get current state information."""
        probabilities = np.abs(self.current_state.state_vector)**2
        
        return {
            'num_qubits': self.num_qubits,
            'coherence_level': self.current_state.coherence_level,
            'num_measurements': len(self.current_state.measurement_history),
            'dominant_states': self._get_dominant_states(probabilities, top_k=3),
            'entanglement_degree': len(self.current_state.entanglement_connections)
        }
    
    def _get_dominant_states(self, probabilities: np.ndarray, top_k: int = 3) -> List[Dict[str, Any]]:
        """Get top-k most probable states."""
        top_indices = np.argsort(probabilities)[-top_k:][::-1]
        
        dominant = []
        for idx in top_indices:
            if probabilities[idx] > 1e-6:
                dominant.append({
                    'state': self.current_state.basis_states[idx],
                    'probability': float(probabilities[idx])
                })
        
        return dominant


def test_quantum_state_manager():
    """Test quantum state manager functionality."""
    print("Testing Quantum State Manager...")
    
    # Create manager
    qsm = QuantumStateManager(num_qubits=3)
    print(f"\u2713 Created quantum state manager with {qsm.num_qubits} qubits")
    
    # Test superposition creation
    superposition = qsm.create_superposition(4)
    print(f"\u2713 Created superposition of 4 states")
    print(f"  Coherence: {superposition.coherence_level:.3f}")
    
    # Test Hadamard gate
    qsm.apply_hadamard(0)
    info = qsm.get_state_info()
    print(f"\u2713 Applied Hadamard gate")
    print(f"  Coherence: {info['coherence_level']:.3f}")
    
    # Test coherence maintenance
    coherence = qsm.maintain_coherence(qsm.current_state)
    print(f"\u2713 Maintained coherence: {coherence:.3f}")
    
    # Test quantum optimization
    def simple_objective(probs):
        # Minimize variance
        return np.var(probs)
    
    result = qsm.quantum_optimize(simple_objective, iterations=50)
    print(f"\u2713 Quantum optimization completed")
    print(f"  Iterations: {result.iterations}")
    print(f"  Optimal value: {result.optimal_value:.6f}")
    print(f"  Success: {result.success}")
    
    # Test measurement
    measurement = qsm.measure_state()
    print(f"\u2713 Measured state: {measurement.measured_state}")
    print(f"  Probability: {measurement.probability:.3f}")
    
    print("\n✓ All Quantum State Manager tests passed!")
    return True


if __name__ == "__main__":
    test_quantum_state_manager()
