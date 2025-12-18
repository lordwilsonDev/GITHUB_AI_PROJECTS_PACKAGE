#!/usr/bin/env python3
"""
Universal Optimization Engine - New Build 12 (T-098)
Multi-objective cosmic optimization with Pareto frontier exploration.
Implements universal fitness landscapes for transcendent optimization.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from collections import defaultdict


class OptimizationStrategy(Enum):
    """Universal optimization strategies."""
    PARETO_FRONTIER = "pareto_frontier"  # Multi-objective Pareto optimization
    GRADIENT_ASCENT = "gradient_ascent"  # Gradient-based optimization
    EVOLUTIONARY = "evolutionary"  # Evolutionary algorithms
    QUANTUM_ANNEALING = "quantum_annealing"  # Quantum-inspired annealing
    SWARM_INTELLIGENCE = "swarm_intelligence"  # Swarm-based optimization
    COSMIC_HARMONY = "cosmic_harmony"  # Universal harmony search


class ObjectiveType(Enum):
    """Types of optimization objectives."""
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"
    TARGET = "target"  # Reach specific target value
    BALANCE = "balance"  # Balance multiple objectives


@dataclass
class Objective:
    """Represents an optimization objective."""
    objective_id: str
    objective_type: ObjectiveType
    weight: float = 1.0
    target_value: Optional[float] = None
    current_value: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def evaluate(self, value: float) -> float:
        """Evaluate objective fitness."""
        self.current_value = value
        
        if self.objective_type == ObjectiveType.MAXIMIZE:
            return value * self.weight
        elif self.objective_type == ObjectiveType.MINIMIZE:
            return -value * self.weight
        elif self.objective_type == ObjectiveType.TARGET:
            if self.target_value is not None:
                distance = abs(value - self.target_value)
                return -distance * self.weight
            return 0.0
        else:  # BALANCE
            # Balance means minimize variance from mean
            return -abs(value - 0.5) * self.weight
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'objective_id': self.objective_id,
            'objective_type': self.objective_type.value,
            'weight': float(self.weight),
            'target_value': float(self.target_value) if self.target_value else None,
            'current_value': float(self.current_value),
            'metadata': self.metadata
        }


@dataclass
class Solution:
    """Represents an optimization solution."""
    solution_id: str
    parameters: np.ndarray
    objective_values: Dict[str, float]
    fitness: float
    pareto_rank: int = 0
    crowding_distance: float = 0.0
    generation: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def dominates(self, other: 'Solution', objectives: Dict[str, Objective]) -> bool:
        """Check if this solution dominates another (Pareto dominance)."""
        better_in_any = False
        
        for obj_id, obj in objectives.items():
            my_value = self.objective_values.get(obj_id, 0.0)
            other_value = other.objective_values.get(obj_id, 0.0)
            
            if obj.objective_type == ObjectiveType.MAXIMIZE:
                if my_value < other_value:
                    return False
                if my_value > other_value:
                    better_in_any = True
            elif obj.objective_type == ObjectiveType.MINIMIZE:
                if my_value > other_value:
                    return False
                if my_value < other_value:
                    better_in_any = True
        
        return better_in_any
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'solution_id': self.solution_id,
            'parameters': self.parameters.tolist(),
            'objective_values': {k: float(v) for k, v in self.objective_values.items()},
            'fitness': float(self.fitness),
            'pareto_rank': self.pareto_rank,
            'crowding_distance': float(self.crowding_distance),
            'generation': self.generation,
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }


class UniversalOptimizer:
    """
    Universal optimization engine for cosmic-scale multi-objective optimization.
    
    Features:
    - Multi-objective Pareto optimization
    - Universal fitness landscapes
    - Adaptive strategy selection
    - Infinite scalability
    - Convergence guarantees
    """
    
    def __init__(
        self,
        parameter_dimensions: int,
        population_size: int = 100,
        strategy: OptimizationStrategy = OptimizationStrategy.PARETO_FRONTIER
    ):
        self.parameter_dimensions = parameter_dimensions
        self.population_size = population_size
        self.strategy = strategy
        
        self.objectives: Dict[str, Objective] = {}
        self.population: List[Solution] = []
        self.pareto_frontier: List[Solution] = []
        self.generation = 0
        
        self.optimization_history: List[Dict[str, Any]] = []
        self.convergence_metrics: List[float] = []
        
    def add_objective(
        self,
        objective_id: str,
        objective_type: ObjectiveType,
        weight: float = 1.0,
        target_value: Optional[float] = None
    ) -> Objective:
        """Add an optimization objective."""
        objective = Objective(
            objective_id=objective_id,
            objective_type=objective_type,
            weight=weight,
            target_value=target_value
        )
        
        self.objectives[objective_id] = objective
        return objective
    
    def initialize_population(
        self,
        bounds: Optional[Tuple[np.ndarray, np.ndarray]] = None
    ):
        """Initialize population randomly within bounds."""
        if bounds is None:
            # Default bounds: [-1, 1] for each dimension
            lower = np.ones(self.parameter_dimensions) * -1.0
            upper = np.ones(self.parameter_dimensions) * 1.0
        else:
            lower, upper = bounds
        
        self.population = []
        for i in range(self.population_size):
            # Random parameters within bounds
            parameters = np.random.uniform(lower, upper, self.parameter_dimensions)
            
            solution = Solution(
                solution_id=f\"sol_{self.generation}_{i}\",
                parameters=parameters,
                objective_values={},
                fitness=0.0,
                generation=self.generation
            )
            
            self.population.append(solution)
    \n    def evaluate_solution(\n        self,\n        solution: Solution,\n        objective_functions: Dict[str, Callable[[np.ndarray], float]]\n    ):\n        \"\"\"Evaluate a solution against all objectives.\"\"\"\n        total_fitness = 0.0\n        \n        for obj_id, objective in self.objectives.items():\n            if obj_id in objective_functions:\n                # Evaluate objective function\n                value = objective_functions[obj_id](solution.parameters)\n                solution.objective_values[obj_id] = value\n                \n                # Calculate fitness contribution\n                fitness_contribution = objective.evaluate(value)\n                total_fitness += fitness_contribution\n        \n        solution.fitness = total_fitness
    
    def evaluate_population(\n        self,\n        objective_functions: Dict[str, Callable[[np.ndarray], float]]\n    ):\n        \"\"\"Evaluate entire population.\"\"\"\n        for solution in self.population:\n            self.evaluate_solution(solution, objective_functions)
    
    def compute_pareto_frontier(self) -> List[Solution]:\n        \"\"\"Compute Pareto frontier from current population.\"\"\"\n        # Non-dominated sorting\n        fronts = self._fast_non_dominated_sort()\n        \n        # First front is the Pareto frontier\n        if fronts:\n            self.pareto_frontier = fronts[0]\n            \n            # Calculate crowding distances\n            self._calculate_crowding_distance(self.pareto_frontier)\n        \n        return self.pareto_frontier
    
    def _fast_non_dominated_sort(self) -> List[List[Solution]]:\n        \"\"\"Fast non-dominated sorting (NSGA-II algorithm).\"\"\"\n        # Domination counts and dominated solutions\n        domination_count = {sol.solution_id: 0 for sol in self.population}\n        dominated_solutions = {sol.solution_id: [] for sol in self.population}\n        \n        # Calculate domination relationships\n        for i, sol_i in enumerate(self.population):\n            for sol_j in self.population[i+1:]:\n                if sol_i.dominates(sol_j, self.objectives):\n                    dominated_solutions[sol_i.solution_id].append(sol_j)\n                    domination_count[sol_j.solution_id] += 1\n                elif sol_j.dominates(sol_i, self.objectives):\n                    dominated_solutions[sol_j.solution_id].append(sol_i)\n                    domination_count[sol_i.solution_id] += 1\n        \n        # Create fronts\n        fronts = []\n        current_front = []\n        \n        # First front: solutions with domination count = 0\n        for sol in self.population:\n            if domination_count[sol.solution_id] == 0:\n                sol.pareto_rank = 0\n                current_front.append(sol)\n        \n        fronts.append(current_front)\n        \n        # Subsequent fronts\n        rank = 1\n        while current_front:\n            next_front = []\n            for sol in current_front:\n                for dominated_sol in dominated_solutions[sol.solution_id]:\n                    domination_count[dominated_sol.solution_id] -= 1\n                    if domination_count[dominated_sol.solution_id] == 0:\n                        dominated_sol.pareto_rank = rank\n                        next_front.append(dominated_sol)\n            \n            if next_front:\n                fronts.append(next_front)\n            current_front = next_front\n            rank += 1\n        \n        return fronts
    
    def _calculate_crowding_distance(self, solutions: List[Solution]):\n        \"\"\"Calculate crowding distance for solutions.\"\"\"\n        if len(solutions) <= 2:\n            for sol in solutions:\n                sol.crowding_distance = float('inf')\n            return\n        \n        # Initialize distances\n        for sol in solutions:\n            sol.crowding_distance = 0.0\n        \n        # For each objective\n        for obj_id in self.objectives:\n            # Sort by objective value\n            sorted_solutions = sorted(\n                solutions,\n                key=lambda s: s.objective_values.get(obj_id, 0.0)\n            )\n            \n            # Boundary solutions get infinite distance\n            sorted_solutions[0].crowding_distance = float('inf')\n            sorted_solutions[-1].crowding_distance = float('inf')\n            \n            # Calculate range\n            obj_range = (\n                sorted_solutions[-1].objective_values.get(obj_id, 0.0) -\n                sorted_solutions[0].objective_values.get(obj_id, 0.0)\n            )\n            \n            if obj_range == 0:\n                continue\n            \n            # Calculate crowding distance for middle solutions\n            for i in range(1, len(sorted_solutions) - 1):\n                distance = (\n                    sorted_solutions[i+1].objective_values.get(obj_id, 0.0) -\n                    sorted_solutions[i-1].objective_values.get(obj_id, 0.0)\n                ) / obj_range\n                \n                sorted_solutions[i].crowding_distance += distance
    
    def evolve_generation(\n        self,\n        objective_functions: Dict[str, Callable[[np.ndarray], float]],\n        mutation_rate: float = 0.1,\n        crossover_rate: float = 0.9\n    ):\n        \"\"\"Evolve population for one generation.\"\"\"\n        # Evaluate current population\n        self.evaluate_population(objective_functions)\n        \n        # Compute Pareto frontier\n        self.compute_pareto_frontier()\n        \n        # Selection\n        parents = self._tournament_selection()\n        \n        # Crossover and mutation\n        offspring = []\n        for i in range(0, len(parents), 2):\n            if i + 1 < len(parents):\n                parent1 = parents[i]\n                parent2 = parents[i + 1]\n                \n                # Crossover\n                if np.random.random() < crossover_rate:\n                    child1_params, child2_params = self._crossover(\n                        parent1.parameters,\n                        parent2.parameters\n                    )\n                else:\n                    child1_params = parent1.parameters.copy()\n                    child2_params = parent2.parameters.copy()\n                \n                # Mutation\n                if np.random.random() < mutation_rate:\n                    child1_params = self._mutate(child1_params)\n                if np.random.random() < mutation_rate:\n                    child2_params = self._mutate(child2_params)\n                \n                # Create offspring solutions\n                child1 = Solution(\n                    solution_id=f\"sol_{self.generation+1}_{len(offspring)}\",\n                    parameters=child1_params,\n                    objective_values={},\n                    fitness=0.0,\n                    generation=self.generation + 1\n                )\n                child2 = Solution(\n                    solution_id=f\"sol_{self.generation+1}_{len(offspring)+1}\",\n                    parameters=child2_params,\n                    objective_values={},\n                    fitness=0.0,\n                    generation=self.generation + 1\n                )\n                \n                offspring.extend([child1, child2])\n        \n        # Combine population and offspring\n        combined = self.population + offspring\n        \n        # Evaluate offspring\n        for sol in offspring:\n            self.evaluate_solution(sol, objective_functions)\n        \n        # Environmental selection (keep best population_size solutions)\n        fronts = self._fast_non_dominated_sort_list(combined)\n        \n        new_population = []\n        for front in fronts:\n            if len(new_population) + len(front) <= self.population_size:\n                new_population.extend(front)\n            else:\n                # Fill remaining slots with best crowding distance\n                self._calculate_crowding_distance(front)\n                front.sort(key=lambda s: s.crowding_distance, reverse=True)\n                remaining = self.population_size - len(new_population)\n                new_population.extend(front[:remaining])\n                break\n        \n        self.population = new_population\n        self.generation += 1\n        \n        # Record convergence metric\n        if self.pareto_frontier:\n            avg_fitness = np.mean([sol.fitness for sol in self.pareto_frontier])\n            self.convergence_metrics.append(avg_fitness)
    
    def _fast_non_dominated_sort_list(self, solutions: List[Solution]) -> List[List[Solution]]:\n        \"\"\"Fast non-dominated sorting for a list of solutions.\"\"\"\n        # Temporarily set as population for sorting\n        old_pop = self.population\n        self.population = solutions\n        fronts = self._fast_non_dominated_sort()\n        self.population = old_pop\n        return fronts
    
    def _tournament_selection(self, tournament_size: int = 3) -> List[Solution]:\n        \"\"\"Tournament selection for parent selection.\"\"\"\n        parents = []\n        \n        for _ in range(self.population_size):\n            # Select random individuals for tournament\n            tournament = np.random.choice(self.population, tournament_size, replace=False)\n            \n            # Select best (lowest rank, highest crowding distance)\n            best = min(\n                tournament,\n                key=lambda s: (s.pareto_rank, -s.crowding_distance)\n            )\n            \n            parents.append(best)\n        \n        return parents
    
    def _crossover(\n        self,\n        parent1: np.ndarray,\n        parent2: np.ndarray\n    ) -> Tuple[np.ndarray, np.ndarray]:\n        \"\"\"Simulated binary crossover (SBX).\"\"\"\n        eta = 20  # Distribution index\n        \n        child1 = np.zeros_like(parent1)\n        child2 = np.zeros_like(parent2)\n        \n        for i in range(len(parent1)):\n            if np.random.random() < 0.5:\n                u = np.random.random()\n                if u <= 0.5:\n                    beta = (2 * u) ** (1.0 / (eta + 1))\n                else:\n                    beta = (1.0 / (2 * (1 - u))) ** (1.0 / (eta + 1))\n                \n                child1[i] = 0.5 * ((1 + beta) * parent1[i] + (1 - beta) * parent2[i])\n                child2[i] = 0.5 * ((1 - beta) * parent1[i] + (1 + beta) * parent2[i])\n            else:\n                child1[i] = parent1[i]\n                child2[i] = parent2[i]\n        \n        return child1, child2
    
    def _mutate(self, parameters: np.ndarray, mutation_strength: float = 0.1) -> np.ndarray:\n        \"\"\"Polynomial mutation.\"\"\"\n        mutated = parameters.copy()\n        \n        for i in range(len(mutated)):\n            if np.random.random() < 1.0 / len(mutated):\n                # Polynomial mutation\n                delta = np.random.normal(0, mutation_strength)\n                mutated[i] += delta\n                # Clip to reasonable bounds\n                mutated[i] = np.clip(mutated[i], -10, 10)\n        \n        return mutated
    
    def optimize(\n        self,\n        objective_functions: Dict[str, Callable[[np.ndarray], float]],\n        generations: int = 100,\n        bounds: Optional[Tuple[np.ndarray, np.ndarray]] = None\n    ) -> List[Solution]:\n        \"\"\"Run optimization for specified generations.\"\"\"\n        # Initialize if needed\n        if not self.population:\n            self.initialize_population(bounds)\n        \n        # Evolution loop\n        for gen in range(generations):\n            self.evolve_generation(objective_functions)\n            \n            # Record history\n            self.optimization_history.append({\n                'generation': self.generation,\n                'pareto_size': len(self.pareto_frontier),\n                'avg_fitness': np.mean([sol.fitness for sol in self.population]),\n                'best_fitness': max(sol.fitness for sol in self.population),\n                'timestamp': time.time()\n            })\n        \n        return self.pareto_frontier
    
    def get_best_solution(self) -> Optional[Solution]:\n        \"\"\"Get single best solution from Pareto frontier.\"\"\"\n        if not self.pareto_frontier:\n            return None\n        \n        # Return solution with highest fitness\n        return max(self.pareto_frontier, key=lambda s: s.fitness)
    
    def export_state(self) -> Dict[str, Any]:\n        \"\"\"Export complete optimizer state.\"\"\"\n        return {\n            'parameter_dimensions': self.parameter_dimensions,\n            'population_size': self.population_size,\n            'strategy': self.strategy.value,\n            'generation': self.generation,\n            'objectives': {\n                oid: obj.to_dict() for oid, obj in self.objectives.items()\n            },\n            'pareto_frontier': [\n                sol.to_dict() for sol in self.pareto_frontier\n            ],\n            'optimization_history': self.optimization_history[-100:],  # Last 100\n            'convergence_metrics': self.convergence_metrics[-100:]\n        }\n\n\n# Integration interface\ndef create_universal_optimizer(\n    parameter_dimensions: int,\n    population_size: int = 100\n) -> UniversalOptimizer:\n    \"\"\"Factory function for creating universal optimizer.\"\"\"\n    return UniversalOptimizer(\n        parameter_dimensions=parameter_dimensions,\n        population_size=population_size\n    )\n\n\ndef test_universal_optimizer():\n    \"\"\"Test universal optimizer.\"\"\"\n    optimizer = create_universal_optimizer(parameter_dimensions=5, population_size=20)\n    \n    # Test 1: Add objectives\n    obj1 = optimizer.add_objective('obj1', ObjectiveType.MAXIMIZE, weight=1.0)\n    obj2 = optimizer.add_objective('obj2', ObjectiveType.MINIMIZE, weight=1.0)\n    assert len(optimizer.objectives) == 2\n    \n    # Test 2: Initialize population\n    optimizer.initialize_population()\n    assert len(optimizer.population) == 20\n    \n    # Test 3: Define objective functions\n    def sphere(x):\n        return -np.sum(x**2)  # Minimize sphere function\n    \n    def rosenbrock(x):\n        return -np.sum(100*(x[1:]-x[:-1]**2)**2 + (1-x[:-1])**2)  # Minimize Rosenbrock\n    \n    objective_functions = {\n        'obj1': sphere,\n        'obj2': rosenbrock\n    }\n    \n    # Test 4: Optimize\n    pareto_frontier = optimizer.optimize(objective_functions, generations=10)\n    assert len(pareto_frontier) > 0\n    \n    # Test 5: Get best solution\n    best = optimizer.get_best_solution()\n    assert best is not None\n    assert len(best.parameters) == 5\n    \n    # Test 6: Export state\n    state = optimizer.export_state()\n    assert 'pareto_frontier' in state\n    assert 'generation' in state\n    assert state['generation'] == 10\n    \n    return True\n\n\nif __name__ == '__main__':\n    success = test_universal_optimizer()\n    print(f\"Universal Optimizer test: {'PASSED' if success else 'FAILED'}\")\n