#!/usr/bin/env python3
"""
Adaptive Algorithms - Vy-Nexus Self-Improvement Cycle

Algorithms that adapt and improve based on performance data and feedback.
Implements multi-armed bandits, parameter tuning, and strategy selection.

Author: Vy-Nexus Self-Evolving AI
Created: December 15, 2025
"""

import json
import os
import math
import random
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict
import statistics


class AdaptationStrategy(Enum):
    """Strategies for adaptation."""
    EPSILON_GREEDY = "epsilon_greedy"
    UCB = "ucb"  # Upper Confidence Bound
    THOMPSON_SAMPLING = "thompson_sampling"
    GRADIENT_DESCENT = "gradient_descent"
    SIMULATED_ANNEALING = "simulated_annealing"


class ConvergenceStatus(Enum):
    """Status of algorithm convergence."""
    NOT_STARTED = "not_started"
    EXPLORING = "exploring"
    CONVERGING = "converging"
    CONVERGED = "converged"
    DIVERGING = "diverging"


@dataclass
class AlgorithmState:
    """State of an adaptive algorithm."""
    algorithm_id: str
    algorithm_type: str
    parameters: Dict[str, Any]
    performance_history: List[float] = field(default_factory=list)
    iteration: int = 0
    convergence_status: str = ConvergenceStatus.NOT_STARTED.value
    best_performance: float = float('-inf')
    best_parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BanditArm:
    """Represents an arm in a multi-armed bandit."""
    arm_id: str
    name: str
    pulls: int = 0
    total_reward: float = 0.0
    rewards: List[float] = field(default_factory=list)
    
    @property
    def average_reward(self) -> float:
        """Calculate average reward."""
        return self.total_reward / self.pulls if self.pulls > 0 else 0.0


@dataclass
class AdaptationResult:
    """Result of an adaptation step."""
    algorithm_id: str
    iteration: int
    selected_action: Any
    performance: float
    parameters_updated: Dict[str, Any]
    convergence_status: str
    reasoning: List[str]
    timestamp: str


class AdaptiveAlgorithms:
    """Adaptive algorithms that learn and improve over time."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/adaptive_algorithms"):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.algorithms_file = os.path.join(self.data_dir, "algorithms.json")
        self.bandits_file = os.path.join(self.data_dir, "bandits.json")
        self.results_file = os.path.join(self.data_dir, "adaptation_results.json")
        
        self.algorithms = self._load_algorithms()
        self.bandits = self._load_bandits()
        self.results = self._load_results()
    
    def _load_algorithms(self) -> Dict[str, Dict]:
        """Load algorithm states."""
        if os.path.exists(self.algorithms_file):
            with open(self.algorithms_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_algorithms(self):
        """Save algorithm states."""
        with open(self.algorithms_file, 'w') as f:
            json.dump(self.algorithms, f, indent=2)
    
    def _load_bandits(self) -> Dict[str, Dict]:
        """Load bandit states."""
        if os.path.exists(self.bandits_file):
            with open(self.bandits_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_bandits(self):
        """Save bandit states."""
        with open(self.bandits_file, 'w') as f:
            json.dump(self.bandits, f, indent=2)
    
    def _load_results(self) -> List[Dict]:
        """Load adaptation results."""
        if os.path.exists(self.results_file):
            with open(self.results_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_results(self):
        """Save adaptation results."""
        with open(self.results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
    
    def create_algorithm(self, algorithm_id: str, algorithm_type: str,
                        initial_parameters: Dict[str, Any]) -> AlgorithmState:
        """Create a new adaptive algorithm."""
        state = AlgorithmState(
            algorithm_id=algorithm_id,
            algorithm_type=algorithm_type,
            parameters=initial_parameters.copy(),
            best_parameters=initial_parameters.copy()
        )
        
        self.algorithms[algorithm_id] = asdict(state)
        self._save_algorithms()
        
        return state
    
    def create_bandit(self, bandit_id: str, arms: List[str]) -> Dict[str, BanditArm]:
        """Create a multi-armed bandit."""
        bandit_arms = {}
        
        for arm_name in arms:
            arm = BanditArm(
                arm_id=f"{bandit_id}_{arm_name}",
                name=arm_name
            )
            bandit_arms[arm_name] = asdict(arm)
        
        self.bandits[bandit_id] = {
            'bandit_id': bandit_id,
            'arms': bandit_arms,
            'total_pulls': 0,
            'strategy': AdaptationStrategy.EPSILON_GREEDY.value,
            'epsilon': 0.1
        }
        
        self._save_bandits()
        
        return bandit_arms
    
    def select_arm_epsilon_greedy(self, bandit_id: str, epsilon: float = 0.1) -> str:
        """Select arm using epsilon-greedy strategy."""
        if bandit_id not in self.bandits:
            raise ValueError(f"Bandit {bandit_id} not found")
        
        bandit = self.bandits[bandit_id]
        arms = bandit['arms']
        
        # Epsilon-greedy: explore with probability epsilon
        if random.random() < epsilon:
            # Explore: random selection
            return random.choice(list(arms.keys()))
        else:
            # Exploit: select best arm
            best_arm = max(arms.items(), 
                          key=lambda x: x[1]['total_reward'] / max(x[1]['pulls'], 1))
            return best_arm[0]
    
    def select_arm_ucb(self, bandit_id: str, c: float = 2.0) -> str:
        """Select arm using Upper Confidence Bound (UCB) strategy."""
        if bandit_id not in self.bandits:
            raise ValueError(f"Bandit {bandit_id} not found")
        
        bandit = self.bandits[bandit_id]
        arms = bandit['arms']
        total_pulls = bandit['total_pulls']
        
        # If any arm hasn't been pulled, pull it
        for arm_name, arm_data in arms.items():
            if arm_data['pulls'] == 0:
                return arm_name
        
        # Calculate UCB for each arm
        ucb_values = {}
        for arm_name, arm_data in arms.items():
            avg_reward = arm_data['total_reward'] / arm_data['pulls']
            exploration_bonus = c * math.sqrt(math.log(total_pulls) / arm_data['pulls'])
            ucb_values[arm_name] = avg_reward + exploration_bonus
        
        # Select arm with highest UCB
        return max(ucb_values.items(), key=lambda x: x[1])[0]
    
    def update_bandit(self, bandit_id: str, arm_name: str, reward: float):
        """Update bandit after pulling an arm."""
        if bandit_id not in self.bandits:
            raise ValueError(f"Bandit {bandit_id} not found")
        
        bandit = self.bandits[bandit_id]
        
        if arm_name not in bandit['arms']:
            raise ValueError(f"Arm {arm_name} not found in bandit {bandit_id}")
        
        arm = bandit['arms'][arm_name]
        arm['pulls'] += 1
        arm['total_reward'] += reward
        arm['rewards'].append(reward)
        
        bandit['total_pulls'] += 1
        
        self._save_bandits()
    
    def adapt_parameters_gradient(self, algorithm_id: str, 
                                 performance: float,
                                 learning_rate: float = 0.01) -> Dict[str, Any]:
        """Adapt parameters using gradient-based approach."""
        if algorithm_id not in self.algorithms:
            raise ValueError(f"Algorithm {algorithm_id} not found")
        
        algo = self.algorithms[algorithm_id]
        
        # Update performance history
        algo['performance_history'].append(performance)
        algo['iteration'] += 1
        
        # Update best performance
        if performance > algo['best_performance']:
            algo['best_performance'] = performance
            algo['best_parameters'] = algo['parameters'].copy()
        
        # Simple gradient estimation (finite differences)
        if len(algo['performance_history']) >= 2:
            performance_change = algo['performance_history'][-1] - algo['performance_history'][-2]
            
            # Adjust parameters based on performance change
            for param_name, param_value in algo['parameters'].items():
                if isinstance(param_value, (int, float)):
                    # Increase parameter if performance improved, decrease otherwise
                    adjustment = learning_rate * performance_change * param_value
                    algo['parameters'][param_name] = param_value + adjustment
        
        # Check convergence
        algo['convergence_status'] = self._check_convergence(
            algo['performance_history']
        ).value
        
        self._save_algorithms()
        
        return algo['parameters']
    
    def adapt_parameters_simulated_annealing(self, algorithm_id: str,
                                            performance: float,
                                            temperature: float = 1.0,
                                            cooling_rate: float = 0.95) -> Dict[str, Any]:
        """Adapt parameters using simulated annealing."""
        if algorithm_id not in self.algorithms:
            raise ValueError(f"Algorithm {algorithm_id} not found")
        
        algo = self.algorithms[algorithm_id]
        
        # Update performance history
        algo['performance_history'].append(performance)
        algo['iteration'] += 1
        
        # Update best performance
        if performance > algo['best_performance']:
            algo['best_performance'] = performance
            algo['best_parameters'] = algo['parameters'].copy()
        
        # Generate neighbor solution (perturb parameters)
        new_parameters = {}
        for param_name, param_value in algo['parameters'].items():
            if isinstance(param_value, (int, float)):
                # Random perturbation scaled by temperature
                perturbation = random.gauss(0, temperature * abs(param_value) * 0.1)
                new_parameters[param_name] = param_value + perturbation
            else:
                new_parameters[param_name] = param_value
        
        # Accept or reject based on performance and temperature
        if len(algo['performance_history']) >= 2:
            delta = performance - algo['performance_history'][-2]
            
            # Accept if better, or with probability based on temperature
            if delta > 0 or random.random() < math.exp(delta / temperature):
                algo['parameters'] = new_parameters
        
        # Update temperature
        if 'temperature' not in algo['metadata']:
            algo['metadata']['temperature'] = temperature
        algo['metadata']['temperature'] *= cooling_rate
        
        # Check convergence
        algo['convergence_status'] = self._check_convergence(
            algo['performance_history']
        ).value
        
        self._save_algorithms()
        
        return algo['parameters']
    
    def _check_convergence(self, performance_history: List[float],
                          window_size: int = 10,
                          threshold: float = 0.01) -> ConvergenceStatus:
        """Check if algorithm has converged."""
        if len(performance_history) < window_size:
            return ConvergenceStatus.EXPLORING
        
        # Get recent performance
        recent = performance_history[-window_size:]
        
        # Calculate variance
        if len(recent) > 1:
            variance = statistics.variance(recent)
            mean = statistics.mean(recent)
            
            # Coefficient of variation
            cv = math.sqrt(variance) / abs(mean) if mean != 0 else float('inf')
            
            if cv < threshold:
                return ConvergenceStatus.CONVERGED
            elif cv < threshold * 5:
                return ConvergenceStatus.CONVERGING
            else:
                # Check if diverging (performance getting worse)
                if len(performance_history) >= window_size * 2:
                    older = performance_history[-window_size*2:-window_size]
                    if statistics.mean(recent) < statistics.mean(older) * 0.9:
                        return ConvergenceStatus.DIVERGING
                
                return ConvergenceStatus.EXPLORING
        
        return ConvergenceStatus.EXPLORING
    
    def auto_tune_parameter(self, algorithm_id: str, parameter_name: str,
                           min_value: float, max_value: float,
                           performance_function: Callable[[float], float],
                           iterations: int = 20) -> Tuple[float, float]:
        """Automatically tune a parameter to optimize performance."""
        
        # Golden section search for optimization
        phi = (1 + math.sqrt(5)) / 2  # Golden ratio
        resphi = 2 - phi
        
        a = min_value
        b = max_value
        tol = 1e-5
        
        # Initial points
        x1 = a + resphi * (b - a)
        x2 = b - resphi * (b - a)
        
        f1 = performance_function(x1)
        f2 = performance_function(x2)
        
        history = [(x1, f1), (x2, f2)]
        
        for i in range(iterations):
            if f1 > f2:
                b = x2
                x2 = x1
                f2 = f1
                x1 = a + resphi * (b - a)
                f1 = performance_function(x1)
            else:
                a = x1
                x1 = x2
                f1 = f2
                x2 = b - resphi * (b - a)
                f2 = performance_function(x2)
            
            history.append((x1, f1))
            
            if abs(b - a) < tol:
                break
        
        # Return best value and performance
        best = max(history, key=lambda x: x[1])
        
        # Update algorithm parameters
        if algorithm_id in self.algorithms:
            self.algorithms[algorithm_id]['parameters'][parameter_name] = best[0]
            self._save_algorithms()
        
        return best[0], best[1]
    
    def select_strategy_dynamically(self, context: Dict[str, Any],
                                   available_strategies: List[str],
                                   bandit_id: Optional[str] = None) -> str:
        """Dynamically select best strategy based on context."""
        
        # Create bandit if it doesn't exist
        if bandit_id is None:
            bandit_id = "strategy_selector"
        
        if bandit_id not in self.bandits:
            self.create_bandit(bandit_id, available_strategies)
        
        # Use UCB for strategy selection
        selected_strategy = self.select_arm_ucb(bandit_id, c=1.5)
        
        return selected_strategy
    
    def record_adaptation_result(self, algorithm_id: str, 
                                selected_action: Any,
                                performance: float,
                                parameters_updated: Dict[str, Any]) -> AdaptationResult:
        """Record the result of an adaptation step."""
        
        if algorithm_id in self.algorithms:
            algo = self.algorithms[algorithm_id]
            iteration = algo['iteration']
            convergence_status = algo['convergence_status']
        else:
            iteration = 0
            convergence_status = ConvergenceStatus.NOT_STARTED.value
        
        reasoning = [
            f"Iteration {iteration}",
            f"Performance: {performance:.4f}",
            f"Convergence: {convergence_status}"
        ]
        
        result = AdaptationResult(
            algorithm_id=algorithm_id,
            iteration=iteration,
            selected_action=selected_action,
            performance=performance,
            parameters_updated=parameters_updated,
            convergence_status=convergence_status,
            reasoning=reasoning,
            timestamp=datetime.now().isoformat()
        )
        
        self.results.append(asdict(result))
        self._save_results()
        
        return result
    
    def get_algorithm_state(self, algorithm_id: str) -> Optional[Dict]:
        """Get current state of an algorithm."""
        return self.algorithms.get(algorithm_id)
    
    def get_bandit_state(self, bandit_id: str) -> Optional[Dict]:
        """Get current state of a bandit."""
        return self.bandits.get(bandit_id)
    
    def get_best_arm(self, bandit_id: str) -> Tuple[str, float]:
        """Get the best performing arm."""
        if bandit_id not in self.bandits:
            raise ValueError(f"Bandit {bandit_id} not found")
        
        bandit = self.bandits[bandit_id]
        arms = bandit['arms']
        
        best_arm = max(
            arms.items(),
            key=lambda x: x[1]['total_reward'] / max(x[1]['pulls'], 1)
        )
        
        avg_reward = best_arm[1]['total_reward'] / max(best_arm[1]['pulls'], 1)
        
        return best_arm[0], avg_reward
    
    def get_performance_summary(self, algorithm_id: str) -> Dict[str, Any]:
        """Get performance summary for an algorithm."""
        if algorithm_id not in self.algorithms:
            return {'error': 'Algorithm not found'}
        
        algo = self.algorithms[algorithm_id]
        history = algo['performance_history']
        
        if not history:
            return {
                'algorithm_id': algorithm_id,
                'iterations': 0,
                'performance': 'No data'
            }
        
        return {
            'algorithm_id': algorithm_id,
            'iterations': algo['iteration'],
            'current_performance': history[-1],
            'best_performance': algo['best_performance'],
            'average_performance': statistics.mean(history),
            'performance_std': statistics.stdev(history) if len(history) > 1 else 0,
            'convergence_status': algo['convergence_status'],
            'improvement': history[-1] - history[0] if len(history) > 1 else 0,
            'current_parameters': algo['parameters'],
            'best_parameters': algo['best_parameters']
        }
    
    def reset_algorithm(self, algorithm_id: str, keep_history: bool = False):
        """Reset an algorithm to initial state."""
        if algorithm_id not in self.algorithms:
            raise ValueError(f"Algorithm {algorithm_id} not found")
        
        algo = self.algorithms[algorithm_id]
        
        if not keep_history:
            algo['performance_history'] = []
        
        algo['iteration'] = 0
        algo['convergence_status'] = ConvergenceStatus.NOT_STARTED.value
        algo['best_performance'] = float('-inf')
        
        self._save_algorithms()
    
    def compare_strategies(self, bandit_id: str) -> List[Dict[str, Any]]:
        """Compare performance of different strategies/arms."""
        if bandit_id not in self.bandits:
            raise ValueError(f"Bandit {bandit_id} not found")
        
        bandit = self.bandits[bandit_id]
        arms = bandit['arms']
        
        comparison = []
        
        for arm_name, arm_data in arms.items():
            if arm_data['pulls'] > 0:
                avg_reward = arm_data['total_reward'] / arm_data['pulls']
                std_reward = statistics.stdev(arm_data['rewards']) if len(arm_data['rewards']) > 1 else 0
                
                comparison.append({
                    'strategy': arm_name,
                    'pulls': arm_data['pulls'],
                    'average_reward': avg_reward,
                    'std_reward': std_reward,
                    'total_reward': arm_data['total_reward'],
                    'confidence_interval': (avg_reward - 1.96 * std_reward, avg_reward + 1.96 * std_reward)
                })
        
        # Sort by average reward
        comparison.sort(key=lambda x: x['average_reward'], reverse=True)
        
        return comparison


if __name__ == "__main__":
    # Example usage
    adaptive = AdaptiveAlgorithms()
    
    # Create a multi-armed bandit for strategy selection
    strategies = ['strategy_a', 'strategy_b', 'strategy_c']
    adaptive.create_bandit('test_bandit', strategies)
    
    # Simulate pulling arms and getting rewards
    print("\nMulti-Armed Bandit Simulation:")
    for i in range(100):
        # Select arm using UCB
        arm = adaptive.select_arm_ucb('test_bandit')
        
        # Simulate reward (strategy_b is best)
        if arm == 'strategy_a':
            reward = random.gauss(0.5, 0.1)
        elif arm == 'strategy_b':
            reward = random.gauss(0.8, 0.1)  # Best strategy
        else:
            reward = random.gauss(0.6, 0.1)
        
        adaptive.update_bandit('test_bandit', arm, reward)
    
    # Get best arm
    best_arm, best_reward = adaptive.get_best_arm('test_bandit')
    print(f"Best strategy: {best_arm} with average reward: {best_reward:.3f}")
    
    # Compare strategies
    comparison = adaptive.compare_strategies('test_bandit')
    print("\nStrategy Comparison:")
    for comp in comparison:
        print(f"{comp['strategy']}: {comp['average_reward']:.3f} (pulls: {comp['pulls']})")
    
    # Create adaptive algorithm
    algo_id = 'test_algo'
    adaptive.create_algorithm(algo_id, 'gradient_descent', {'learning_rate': 0.01, 'momentum': 0.9})
    
    # Simulate adaptation
    print("\nAdaptive Algorithm Simulation:")
    for i in range(50):
        # Simulate performance (improves over time)
        performance = 0.5 + 0.01 * i + random.gauss(0, 0.05)
        
        # Adapt parameters
        new_params = adaptive.adapt_parameters_gradient(algo_id, performance, learning_rate=0.01)
    
    # Get performance summary
    summary = adaptive.get_performance_summary(algo_id)
    print(f"\nAlgorithm Performance:")
    print(f"Iterations: {summary['iterations']}")
    print(f"Best performance: {summary['best_performance']:.3f}")
    print(f"Current performance: {summary['current_performance']:.3f}")
    print(f"Convergence: {summary['convergence_status']}")
    print(f"Improvement: {summary['improvement']:.3f}")
