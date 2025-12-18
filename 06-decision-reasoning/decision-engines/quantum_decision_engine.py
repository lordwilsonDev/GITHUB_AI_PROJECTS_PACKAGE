#!/usr/bin/env python3
"""
Quantum Decision Engine - New Build 12 (T-091)
Quantum-inspired decision making with probability amplitude optimization.
Uses quantum interference and amplitude amplification for optimal decisions.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import time


class DecisionStrategy(Enum):
    """Decision-making strategies."""
    AMPLITUDE_AMPLIFICATION = "amplitude_amplification"  # Grover-like amplification
    QUANTUM_ANNEALING = "quantum_annealing"  # Simulated quantum annealing
    INTERFERENCE_OPTIMIZATION = "interference_optimization"  # Quantum interference
    SUPERPOSITION_SAMPLING = "superposition_sampling"  # Sample from superposition


@dataclass
class Decision:
    """Represents a decision option."""
    option_id: str
    description: str
    amplitude: complex
    probability: float = 0.0
    utility: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate probability from amplitude."""
        self.probability = abs(self.amplitude) ** 2
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'option_id': self.option_id,
            'description': self.description,
            'probability': float(self.probability),
            'utility': float(self.utility),
            'metadata': self.metadata
        }


@dataclass
class DecisionContext:
    """Context for decision-making."""
    context_id: str
    objectives: List[str]
    constraints: Dict[str, Any]
    preferences: Dict[str, float]
    timestamp: float = field(default_factory=time.time)


class QuantumDecisionEngine:
    """
    Quantum-inspired decision engine using probability amplitude optimization.
    Implements quantum interference and amplitude amplification for decision-making.
    """
    
    def __init__(self, num_qubits: int = 8):
        self.num_qubits = num_qubits
        self.state_dimension = 2 ** num_qubits
        self.decision_history: List[Dict[str, Any]] = []
        self.utility_function: Optional[Callable] = None
        self.learning_rate = 0.1
        
    def create_decision_superposition(self, options: List[str]) -> np.ndarray:
        """
        Create a quantum superposition of decision options.
        
        Args:
            options: List of decision option identifiers
        
        Returns:
            Quantum state vector in superposition
        """
        n_options = len(options)
        
        # Create uniform superposition
        state = np.zeros(self.state_dimension, dtype=complex)
        
        # Distribute amplitude equally across options
        amplitude = 1.0 / np.sqrt(n_options)
        for i in range(min(n_options, self.state_dimension)):
            state[i] = amplitude
        
        return state
    
    def apply_quantum_interference(self, 
                                   state: np.ndarray,
                                   preferences: Dict[str, float]) -> np.ndarray:
        """
        Apply quantum interference based on preferences.
        
        Args:
            state: Current quantum state
            preferences: Preference weights for options
        
        Returns:
            State after interference
        """
        # Create interference operator based on preferences
        interference_matrix = np.eye(len(state), dtype=complex)
        
        for idx, (option_id, weight) in enumerate(preferences.items()):
            if idx < len(state):
                # Apply phase shift based on preference
                phase = weight * np.pi
                interference_matrix[idx, idx] = np.exp(1j * phase)
        
        # Apply interference
        new_state = interference_matrix @ state
        
        # Normalize
        norm = np.linalg.norm(new_state)
        if norm > 0:
            new_state = new_state / norm
        
        return new_state
    
    def amplitude_amplification(self,
                               state: np.ndarray,
                               target_indices: List[int],
                               iterations: int = 3) -> np.ndarray:
        """
        Grover-like amplitude amplification for target options.
        
        Args:
            state: Current quantum state
            target_indices: Indices of options to amplify
            iterations: Number of amplification iterations
        
        Returns:
            State with amplified target amplitudes
        """
        current_state = state.copy()
        n = len(state)
        
        for _ in range(iterations):
            # Oracle: flip phase of target states
            oracle = np.eye(n, dtype=complex)
            for idx in target_indices:
                if idx < n:
                    oracle[idx, idx] = -1
            
            # Apply oracle
            current_state = oracle @ current_state
            
            # Diffusion operator: inversion about average
            avg = np.mean(current_state)
            diffusion = 2 * avg * np.ones(n, dtype=complex) - current_state
            
            current_state = diffusion
            
            # Normalize
            norm = np.linalg.norm(current_state)
            if norm > 0:
                current_state = current_state / norm
        
        return current_state
    
    def quantum_annealing_decision(self,
                                  options: List[str],
                                  utility_scores: Dict[str, float],
                                  temperature: float = 1.0,
                                  cooling_rate: float = 0.95,
                                  iterations: int = 100) -> str:
        """
        Use simulated quantum annealing for decision-making.
        
        Args:
            options: List of decision options
            utility_scores: Utility score for each option
            temperature: Initial temperature
            cooling_rate: Rate of temperature decrease
            iterations: Number of annealing iterations
        
        Returns:
            Selected option ID
        """
        # Initialize with random option
        current_option = np.random.choice(options)
        current_utility = utility_scores.get(current_option, 0.0)
        best_option = current_option
        best_utility = current_utility
        
        temp = temperature
        
        for _ in range(iterations):
            # Propose new option
            new_option = np.random.choice(options)
            new_utility = utility_scores.get(new_option, 0.0)
            
            # Calculate energy difference (negative because we maximize utility)
            delta_e = -(new_utility - current_utility)
            
            # Quantum tunneling probability
            if delta_e < 0 or np.random.random() < np.exp(-delta_e / temp):
                current_option = new_option
                current_utility = new_utility
                
                if current_utility > best_utility:
                    best_option = current_option
                    best_utility = current_utility
            
            # Cool down
            temp *= cooling_rate
        
        return best_option
    
    def make_decision(self,
                     options: List[str],
                     context: DecisionContext,
                     strategy: DecisionStrategy = DecisionStrategy.AMPLITUDE_AMPLIFICATION) -> Decision:
        """
        Make a quantum-inspired decision.
        
        Args:
            options: List of decision option identifiers
            context: Decision context with objectives and preferences
            strategy: Decision-making strategy to use
        
        Returns:
            Selected Decision object
        """
        if not options:
            raise ValueError("No options provided for decision")
        
        # Calculate utility scores
        utility_scores = self._calculate_utilities(options, context)
        
        if strategy == DecisionStrategy.AMPLITUDE_AMPLIFICATION:
            # Create superposition
            state = self.create_decision_superposition(options)
            
            # Apply interference based on preferences
            if context.preferences:
                state = self.apply_quantum_interference(state, context.preferences)
            
            # Identify high-utility options for amplification
            sorted_options = sorted(utility_scores.items(), key=lambda x: x[1], reverse=True)
            top_k = max(1, len(options) // 3)  # Amplify top 1/3
            target_indices = [options.index(opt) for opt, _ in sorted_options[:top_k]]
            
            # Amplify
            state = self.amplitude_amplification(state, target_indices)
            
            # Measure (sample from probability distribution)
            probabilities = np.abs(state[:len(options)]) ** 2
            probabilities = probabilities / np.sum(probabilities)  # Normalize
            
            selected_idx = np.random.choice(len(options), p=probabilities)
            selected_option = options[selected_idx]
            amplitude = state[selected_idx]
        
        elif strategy == DecisionStrategy.QUANTUM_ANNEALING:
            selected_option = self.quantum_annealing_decision(options, utility_scores)
            amplitude = complex(1.0, 0.0)
        
        elif strategy == DecisionStrategy.INTERFERENCE_OPTIMIZATION:
            # Create superposition
            state = self.create_decision_superposition(options)
            
            # Apply multiple interference rounds
            for _ in range(5):
                state = self.apply_quantum_interference(state, context.preferences)
            
            # Measure
            probabilities = np.abs(state[:len(options)]) ** 2
            probabilities = probabilities / np.sum(probabilities)
            
            selected_idx = np.random.choice(len(options), p=probabilities)
            selected_option = options[selected_idx]
            amplitude = state[selected_idx]
        
        else:  # SUPERPOSITION_SAMPLING
            # Simple sampling from superposition
            state = self.create_decision_superposition(options)
            probabilities = np.abs(state[:len(options)]) ** 2
            probabilities = probabilities / np.sum(probabilities)
            
            selected_idx = np.random.choice(len(options), p=probabilities)
            selected_option = options[selected_idx]
            amplitude = state[selected_idx]
        
        # Create decision object
        decision = Decision(
            option_id=selected_option,
            description=f"Decision: {selected_option}",
            amplitude=amplitude,
            utility=utility_scores.get(selected_option, 0.0),
            metadata={
                'strategy': strategy.value,
                'context_id': context.context_id,
                'timestamp': time.time()
            }
        )
        
        # Record decision
        self.decision_history.append({
            'decision': decision.to_dict(),
            'options': options,
            'context': context.context_id,
            'strategy': strategy.value
        })
        
        return decision
    
    def _calculate_utilities(self,
                           options: List[str],
                           context: DecisionContext) -> Dict[str, float]:
        """
        Calculate utility scores for options.
        
        Args:
            options: List of decision options
            context: Decision context
        
        Returns:
            Dictionary mapping option IDs to utility scores
        """
        utilities = {}
        
        if self.utility_function:
            # Use custom utility function
            for option in options:
                utilities[option] = self.utility_function(option, context)
        else:
            # Default: use preferences as utilities
            for option in options:
                utilities[option] = context.preferences.get(option, 0.5)
        
        return utilities
    
    def set_utility_function(self, func: Callable[[str, DecisionContext], float]):
        """
        Set a custom utility function.
        
        Args:
            func: Function that takes (option_id, context) and returns utility score
        """
        self.utility_function = func
    
    def multi_objective_decision(self,
                                options: List[str],
                                objectives: Dict[str, Callable],
                                weights: Dict[str, float],
                                context: DecisionContext) -> Decision:
        """
        Make a decision optimizing multiple objectives.
        
        Args:
            options: List of decision options
            objectives: Dictionary of objective functions
            weights: Weights for each objective
            context: Decision context
        
        Returns:
            Selected Decision object
        """
        # Calculate weighted utility for each option
        utility_scores = {}
        
        for option in options:
            total_utility = 0.0
            for obj_name, obj_func in objectives.items():
                obj_value = obj_func(option, context)
                weight = weights.get(obj_name, 1.0)
                total_utility += weight * obj_value
            
            utility_scores[option] = total_utility
        
        # Update context preferences with calculated utilities
        context.preferences = utility_scores
        
        # Make decision using amplitude amplification
        return self.make_decision(options, context, DecisionStrategy.AMPLITUDE_AMPLIFICATION)
    
    def get_decision_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about decision-making performance.
        
        Returns:
            Dictionary of metrics
        """
        if not self.decision_history:
            return {
                'total_decisions': 0,
                'average_utility': 0.0,
                'strategy_distribution': {}
            }
        
        total_decisions = len(self.decision_history)
        
        # Calculate average utility
        utilities = [d['decision']['utility'] for d in self.decision_history]
        avg_utility = float(np.mean(utilities)) if utilities else 0.0
        max_utility = float(np.max(utilities)) if utilities else 0.0
        min_utility = float(np.min(utilities)) if utilities else 0.0
        
        # Strategy distribution
        strategy_counts = {}
        for d in self.decision_history:
            strategy = d['strategy']
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        return {
            'total_decisions': total_decisions,
            'average_utility': avg_utility,
            'max_utility': max_utility,
            'min_utility': min_utility,
            'strategy_distribution': strategy_counts
        }
    
    def export_state(self) -> Dict[str, Any]:
        """
        Export the decision engine state.
        
        Returns:
            Dictionary containing state information
        """
        return {
            'num_qubits': self.num_qubits,
            'state_dimension': self.state_dimension,
            'decision_history': self.decision_history[-100:],  # Last 100 decisions
            'metrics': self.get_decision_metrics()
        }


if __name__ == "__main__":
    # Demonstration
    print("Quantum Decision Engine - Demonstration")
    print("=" * 50)
    
    engine = QuantumDecisionEngine(num_qubits=6)
    
    # Example 1: Simple decision with preferences
    print("\n1. Simple decision with amplitude amplification...")
    options = ["option_a", "option_b", "option_c", "option_d"]
    context = DecisionContext(
        context_id="demo_1",
        objectives=["maximize_value"],
        constraints={},
        preferences={
            "option_a": 0.3,
            "option_b": 0.8,
            "option_c": 0.5,
            "option_d": 0.6
        }
    )
    
    decision = engine.make_decision(options, context, DecisionStrategy.AMPLITUDE_AMPLIFICATION)
    print(f"   Selected: {decision.option_id}")
    print(f"   Probability: {decision.probability:.3f}")
    print(f"   Utility: {decision.utility:.3f}")
    
    # Example 2: Quantum annealing
    print("\n2. Decision using quantum annealing...")
    context2 = DecisionContext(
        context_id="demo_2",
        objectives=["minimize_cost"],
        constraints={},
        preferences={
            "option_a": 0.4,
            "option_b": 0.9,
            "option_c": 0.6,
            "option_d": 0.7
        }
    )
    
    decision2 = engine.make_decision(options, context2, DecisionStrategy.QUANTUM_ANNEALING)
    print(f"   Selected: {decision2.option_id}")
    print(f"   Utility: {decision2.utility:.3f}")
    
    # Example 3: Multi-objective decision
    print("\n3. Multi-objective decision...")
    
    def cost_objective(option: str, ctx: DecisionContext) -> float:
        costs = {"option_a": 0.2, "option_b": 0.8, "option_c": 0.5, "option_d": 0.3}
        return 1.0 - costs.get(option, 0.5)  # Minimize cost = maximize (1 - cost)
    
    def quality_objective(option: str, ctx: DecisionContext) -> float:
        quality = {"option_a": 0.6, "option_b": 0.9, "option_c": 0.7, "option_d": 0.5}
        return quality.get(option, 0.5)
    
    objectives = {
        "cost": cost_objective,
        "quality": quality_objective
    }
    
    weights = {"cost": 0.4, "quality": 0.6}
    
    context3 = DecisionContext(
        context_id="demo_3",
        objectives=["minimize_cost", "maximize_quality"],
        constraints={},
        preferences={}
    )
    
    decision3 = engine.multi_objective_decision(options, objectives, weights, context3)
    print(f"   Selected: {decision3.option_id}")
    print(f"   Combined utility: {decision3.utility:.3f}")
    
    # Get metrics
    print("\n4. Decision engine metrics:")
    metrics = engine.get_decision_metrics()
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    print("\n" + "=" * 50)
    print("Quantum Decision Engine operational.")
