#!/usr/bin/env python3
"""
Global Optimization Engine - New Build 6, Phase 4
Multi-objective optimization, system-wide resource allocation, and Pareto frontier exploration
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import random
import math


class OptimizationObjective(Enum):
    """Optimization objectives"""
    MINIMIZE_COST = "minimize_cost"
    MAXIMIZE_THROUGHPUT = "maximize_throughput"
    MINIMIZE_LATENCY = "minimize_latency"
    MAXIMIZE_RELIABILITY = "maximize_reliability"
    MINIMIZE_ENERGY = "minimize_energy"
    MAXIMIZE_UTILIZATION = "maximize_utilization"


class OptimizationAlgorithm(Enum):
    """Optimization algorithms"""
    GREEDY = "greedy"
    GENETIC = "genetic"
    SIMULATED_ANNEALING = "simulated_annealing"
    PARTICLE_SWARM = "particle_swarm"
    GRADIENT_DESCENT = "gradient_descent"


@dataclass
class OptimizationVariable:
    """Represents an optimization variable"""
    name: str
    min_value: float
    max_value: float
    current_value: float
    step_size: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'current_value': self.current_value,
            'step_size': self.step_size
        }
    
    def randomize(self) -> float:
        """Set to random value within bounds"""
        self.current_value = random.uniform(self.min_value, self.max_value)
        return self.current_value
    
    def mutate(self, mutation_rate: float = 0.1) -> float:
        """Mutate value slightly"""
        if random.random() < mutation_rate:
            delta = random.uniform(-self.step_size, self.step_size)
            self.current_value = max(self.min_value, min(self.max_value, self.current_value + delta))
        return self.current_value


@dataclass
class OptimizationSolution:
    """Represents a solution in the optimization space"""
    solution_id: str
    variables: Dict[str, float]
    objectives: Dict[OptimizationObjective, float]
    fitness: float = 0.0
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'solution_id': self.solution_id,
            'variables': self.variables,
            'objectives': {k.value: v for k, v in self.objectives.items()},
            'fitness': self.fitness,
            'timestamp': self.timestamp
        }
    
    def dominates(self, other: 'OptimizationSolution') -> bool:
        """Check if this solution dominates another (Pareto dominance)"""
        better_in_one = False
        
        for objective in self.objectives.keys():
            if objective not in other.objectives:
                continue
            
            # For minimize objectives, lower is better
            if "minimize" in objective.value:
                if self.objectives[objective] > other.objectives[objective]:
                    return False
                if self.objectives[objective] < other.objectives[objective]:
                    better_in_one = True
            # For maximize objectives, higher is better
            else:
                if self.objectives[objective] < other.objectives[objective]:
                    return False
                if self.objectives[objective] > other.objectives[objective]:
                    better_in_one = True
        
        return better_in_one


class ObjectiveFunction:
    """Evaluates optimization objectives"""
    
    def __init__(self):
        self.evaluation_count = 0
        
    def evaluate(self, variables: Dict[str, float], objectives: List[OptimizationObjective]) -> Dict[OptimizationObjective, float]:
        """Evaluate objectives for given variables"""
        self.evaluation_count += 1
        results = {}
        
        for objective in objectives:
            if objective == OptimizationObjective.MINIMIZE_COST:
                # Simulate cost calculation
                results[objective] = sum(v * 0.5 for v in variables.values())
            
            elif objective == OptimizationObjective.MAXIMIZE_THROUGHPUT:
                # Simulate throughput calculation
                results[objective] = sum(v * 2.0 for v in variables.values()) / len(variables)
            
            elif objective == OptimizationObjective.MINIMIZE_LATENCY:
                # Simulate latency calculation
                results[objective] = max(variables.values()) * 10.0
            
            elif objective == OptimizationObjective.MAXIMIZE_RELIABILITY:
                # Simulate reliability calculation
                product = 1.0
                for v in variables.values():
                    product *= (v / 100.0)  # Assume values are percentages
                results[objective] = product * 100.0
            
            elif objective == OptimizationObjective.MINIMIZE_ENERGY:
                # Simulate energy calculation
                results[objective] = sum(v ** 2 for v in variables.values()) * 0.1
            
            elif objective == OptimizationObjective.MAXIMIZE_UTILIZATION:
                # Simulate utilization calculation
                results[objective] = sum(variables.values()) / (len(variables) * 100.0) * 100.0
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        return {'evaluation_count': self.evaluation_count}


class ParetoFrontier:
    """Manages Pareto-optimal solutions"""
    
    def __init__(self):
        self.solutions: List[OptimizationSolution] = []
        self.lock = threading.Lock()
        
    def add_solution(self, solution: OptimizationSolution) -> bool:
        """Add solution to frontier if non-dominated"""
        with self.lock:
            # Check if solution is dominated by any existing solution
            for existing in self.solutions:
                if existing.dominates(solution):
                    return False
            
            # Remove solutions dominated by new solution
            self.solutions = [s for s in self.solutions if not solution.dominates(s)]
            
            # Add new solution
            self.solutions.append(solution)
            return True
    
    def get_solutions(self) -> List[OptimizationSolution]:
        """Get all Pareto-optimal solutions"""
        with self.lock:
            return self.solutions.copy()
    
    def get_best_for_objective(self, objective: OptimizationObjective) -> Optional[OptimizationSolution]:
        """Get best solution for a specific objective"""
        with self.lock:
            if not self.solutions:
                return None
            
            solutions_with_objective = [s for s in self.solutions if objective in s.objectives]
            if not solutions_with_objective:
                return None
            
            # For minimize objectives, find minimum
            if "minimize" in objective.value:
                return min(solutions_with_objective, key=lambda s: s.objectives[objective])
            # For maximize objectives, find maximum
            else:
                return max(solutions_with_objective, key=lambda s: s.objectives[objective])
    
    def get_stats(self) -> Dict[str, Any]:
        with self.lock:
            return {
                'frontier_size': len(self.solutions)
            }


class ResourceAllocator:
    """Allocates resources optimally across system"""
    
    def __init__(self):
        self.allocations: Dict[str, Dict[str, float]] = {}
        self.allocation_history: List[Dict[str, Any]] = []
        
    def allocate(self, resources: Dict[str, float], demands: Dict[str, float]) -> Dict[str, float]:
        """Allocate resources to meet demands optimally"""
        allocation = {}
        
        # Calculate total demand
        total_demand = sum(demands.values())
        
        if total_demand == 0:
            return {k: 0.0 for k in demands.keys()}
        
        # Allocate proportionally to demand
        for component, demand in demands.items():
            proportion = demand / total_demand
            
            # Allocate from each resource type
            allocation[component] = {}
            for resource_type, available in resources.items():
                allocation[component][resource_type] = available * proportion
        
        self.allocation_history.append({
            'allocation': allocation,
            'timestamp': time.time()
        })
        
        return allocation
    
    def optimize_allocation(self, resources: Dict[str, float], demands: Dict[str, float], 
                          priorities: Dict[str, int]) -> Dict[str, float]:
        """Optimize allocation considering priorities"""
        allocation = {}
        
        # Calculate weighted demand
        weighted_demands = {k: v * priorities.get(k, 1) for k, v in demands.items()}
        total_weighted = sum(weighted_demands.values())
        
        if total_weighted == 0:
            return {k: 0.0 for k in demands.keys()}
        
        # Allocate based on weighted demand
        for component, weighted_demand in weighted_demands.items():
            proportion = weighted_demand / total_weighted
            
            allocation[component] = {}
            for resource_type, available in resources.items():
                allocation[component][resource_type] = available * proportion
        
        return allocation
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'total_allocations': len(self.allocation_history)
        }


class GlobalOptimizer:
    """Main global optimization engine"""
    
    def __init__(self, algorithm: OptimizationAlgorithm = OptimizationAlgorithm.GENETIC):
        self.algorithm = algorithm
        self.objective_function = ObjectiveFunction()
        self.pareto_frontier = ParetoFrontier()
        self.resource_allocator = ResourceAllocator()
        self.optimization_history: List[OptimizationSolution] = []
        self.lock = threading.Lock()
        
    def optimize(self, variables: List[OptimizationVariable], 
                objectives: List[OptimizationObjective],
                max_iterations: int = 100) -> OptimizationSolution:
        """Run optimization"""
        if self.algorithm == OptimizationAlgorithm.GREEDY:
            return self._greedy_optimize(variables, objectives, max_iterations)
        elif self.algorithm == OptimizationAlgorithm.GENETIC:
            return self._genetic_optimize(variables, objectives, max_iterations)
        elif self.algorithm == OptimizationAlgorithm.SIMULATED_ANNEALING:
            return self._simulated_annealing(variables, objectives, max_iterations)
        else:
            return self._greedy_optimize(variables, objectives, max_iterations)
    
    def _greedy_optimize(self, variables: List[OptimizationVariable], 
                        objectives: List[OptimizationObjective],
                        max_iterations: int) -> OptimizationSolution:
        """Greedy optimization"""
        best_solution = None
        best_fitness = float('-inf')
        
        for iteration in range(max_iterations):
            # Try random values
            var_values = {v.name: v.randomize() for v in variables}
            
            # Evaluate objectives
            obj_values = self.objective_function.evaluate(var_values, objectives)
            
            # Calculate fitness (simple weighted sum)
            fitness = sum(obj_values.values())
            
            solution = OptimizationSolution(
                solution_id=f"greedy_{iteration}",
                variables=var_values.copy(),
                objectives=obj_values,
                fitness=fitness
            )
            
            # Update best
            if fitness > best_fitness:
                best_fitness = fitness
                best_solution = solution
            
            # Add to Pareto frontier
            self.pareto_frontier.add_solution(solution)
            
            with self.lock:
                self.optimization_history.append(solution)
        
        return best_solution
    
    def _genetic_optimize(self, variables: List[OptimizationVariable], 
                         objectives: List[OptimizationObjective],
                         max_iterations: int) -> OptimizationSolution:
        """Genetic algorithm optimization"""
        population_size = 20
        mutation_rate = 0.1
        
        # Initialize population
        population = []
        for i in range(population_size):
            var_values = {v.name: v.randomize() for v in variables}
            obj_values = self.objective_function.evaluate(var_values, objectives)
            fitness = sum(obj_values.values())
            
            solution = OptimizationSolution(
                solution_id=f"gen0_ind{i}",
                variables=var_values.copy(),
                objectives=obj_values,
                fitness=fitness
            )
            population.append(solution)
        
        best_solution = max(population, key=lambda s: s.fitness)
        
        # Evolution
        for generation in range(max_iterations // population_size):
            # Selection (tournament)
            selected = []
            for _ in range(population_size):
                tournament = random.sample(population, 3)
                winner = max(tournament, key=lambda s: s.fitness)
                selected.append(winner)
            
            # Crossover and mutation
            new_population = []
            for i in range(0, len(selected), 2):
                if i + 1 < len(selected):
                    parent1 = selected[i]
                    parent2 = selected[i + 1]
                    
                    # Crossover
                    child_vars = {}
                    for var in variables:
                        if random.random() < 0.5:
                            child_vars[var.name] = parent1.variables[var.name]
                        else:
                            child_vars[var.name] = parent2.variables[var.name]
                        
                        # Mutation
                        if random.random() < mutation_rate:
                            var.current_value = child_vars[var.name]
                            child_vars[var.name] = var.mutate(mutation_rate)
                    
                    # Evaluate child
                    obj_values = self.objective_function.evaluate(child_vars, objectives)
                    fitness = sum(obj_values.values())
                    
                    child = OptimizationSolution(
                        solution_id=f"gen{generation+1}_ind{i}",
                        variables=child_vars,
                        objectives=obj_values,
                        fitness=fitness
                    )
                    
                    new_population.append(child)
                    self.pareto_frontier.add_solution(child)
                    
                    with self.lock:
                        self.optimization_history.append(child)
                    
                    if child.fitness > best_solution.fitness:
                        best_solution = child
            
            population = new_population
        
        return best_solution
    
    def _simulated_annealing(self, variables: List[OptimizationVariable], 
                            objectives: List[OptimizationObjective],
                            max_iterations: int) -> OptimizationSolution:
        """Simulated annealing optimization"""
        # Initialize with random solution
        current_vars = {v.name: v.randomize() for v in variables}
        current_objs = self.objective_function.evaluate(current_vars, objectives)
        current_fitness = sum(current_objs.values())
        
        current_solution = OptimizationSolution(
            solution_id="sa_0",
            variables=current_vars.copy(),
            objectives=current_objs,
            fitness=current_fitness
        )
        
        best_solution = current_solution
        temperature = 100.0
        cooling_rate = 0.95
        
        for iteration in range(max_iterations):
            # Generate neighbor
            neighbor_vars = current_vars.copy()
            var_to_change = random.choice(variables)
            var_to_change.current_value = neighbor_vars[var_to_change.name]
            neighbor_vars[var_to_change.name] = var_to_change.mutate(0.3)
            
            # Evaluate neighbor
            neighbor_objs = self.objective_function.evaluate(neighbor_vars, objectives)
            neighbor_fitness = sum(neighbor_objs.values())
            
            neighbor_solution = OptimizationSolution(
                solution_id=f"sa_{iteration+1}",
                variables=neighbor_vars.copy(),
                objectives=neighbor_objs,
                fitness=neighbor_fitness
            )
            
            # Accept or reject
            delta = neighbor_fitness - current_fitness
            if delta > 0 or random.random() < math.exp(delta / temperature):
                current_vars = neighbor_vars
                current_fitness = neighbor_fitness
                current_solution = neighbor_solution
                
                if current_fitness > best_solution.fitness:
                    best_solution = current_solution
            
            self.pareto_frontier.add_solution(neighbor_solution)
            
            with self.lock:
                self.optimization_history.append(neighbor_solution)
            
            # Cool down
            temperature *= cooling_rate
        
        return best_solution
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        with self.lock:
            return {
                'algorithm': self.algorithm.value,
                'total_solutions_explored': len(self.optimization_history),
                'objective_function': self.objective_function.get_stats(),
                'pareto_frontier': self.pareto_frontier.get_stats(),
                'resource_allocator': self.resource_allocator.get_stats()
            }
    
    def demo(self) -> Dict[str, Any]:
        """Demonstrate global optimization capabilities"""
        print("\n=== Global Optimization Engine Demo ===")
        
        # 1. Define optimization variables
        print("\n1. Defining optimization variables...")
        variables = [
            OptimizationVariable("cpu_allocation", 0.0, 100.0, 50.0, 5.0),
            OptimizationVariable("memory_allocation", 0.0, 100.0, 50.0, 5.0),
            OptimizationVariable("network_bandwidth", 0.0, 100.0, 50.0, 5.0)
        ]
        print(f"   Defined {len(variables)} variables")
        
        # 2. Define objectives
        print("\n2. Defining optimization objectives...")
        objectives = [
            OptimizationObjective.MINIMIZE_COST,
            OptimizationObjective.MAXIMIZE_THROUGHPUT,
            OptimizationObjective.MINIMIZE_LATENCY
        ]
        print(f"   Defined {len(objectives)} objectives")
        
        # 3. Run optimization
        print(f"\n3. Running {self.algorithm.value} optimization...")
        start_time = time.time()
        best_solution = self.optimize(variables, objectives, max_iterations=50)
        duration = time.time() - start_time
        print(f"   Optimization completed in {duration:.3f}s")
        print(f"   Best fitness: {best_solution.fitness:.2f}")
        
        # 4. Show best solution
        print("\n4. Best solution found:")
        for var_name, value in best_solution.variables.items():
            print(f"   {var_name}: {value:.2f}")
        print("   Objectives:")
        for obj, value in best_solution.objectives.items():
            print(f"   {obj.value}: {value:.2f}")
        
        # 5. Show Pareto frontier
        print("\n5. Pareto frontier:")
        frontier_solutions = self.pareto_frontier.get_solutions()
        print(f"   Frontier size: {len(frontier_solutions)} solutions")
        for obj in objectives:
            best_for_obj = self.pareto_frontier.get_best_for_objective(obj)
            if best_for_obj:
                print(f"   Best for {obj.value}: {best_for_obj.objectives[obj]:.2f}")
        
        # 6. Resource allocation
        print("\n6. Optimizing resource allocation...")
        resources = {'cpu': 100.0, 'memory': 256.0, 'storage': 1000.0}
        demands = {'service_a': 30.0, 'service_b': 50.0, 'service_c': 20.0}
        priorities = {'service_a': 2, 'service_b': 1, 'service_c': 3}
        
        allocation = self.resource_allocator.optimize_allocation(resources, demands, priorities)
        print(f"   Allocated resources to {len(allocation)} services")
        
        # 7. Get statistics
        print("\n7. System statistics:")
        stats = self.get_stats()
        print(f"   Solutions explored: {stats['total_solutions_explored']}")
        print(f"   Objective evaluations: {stats['objective_function']['evaluation_count']}")
        print(f"   Pareto frontier size: {stats['pareto_frontier']['frontier_size']}")
        
        print("\n=== Demo Complete ===")
        return stats


class GlobalOptimizerContract:
    """Contract interface for testing"""
    
    @staticmethod
    def create() -> GlobalOptimizer:
        """Create a global optimizer instance"""
        return GlobalOptimizer()
    
    @staticmethod
    def verify() -> bool:
        """Verify global optimizer functionality"""
        go = GlobalOptimizer(OptimizationAlgorithm.GREEDY)
        
        # Test optimization
        variables = [
            OptimizationVariable("x", 0.0, 10.0, 5.0),
            OptimizationVariable("y", 0.0, 10.0, 5.0)
        ]
        objectives = [OptimizationObjective.MINIMIZE_COST]
        
        solution = go.optimize(variables, objectives, max_iterations=10)
        if not solution:
            return False
        
        # Test Pareto frontier
        frontier = go.pareto_frontier.get_solutions()
        if len(frontier) == 0:
            return False
        
        # Test resource allocation
        resources = {'cpu': 100.0}
        demands = {'a': 50.0, 'b': 50.0}
        priorities = {'a': 1, 'b': 1}
        allocation = go.resource_allocator.optimize_allocation(resources, demands, priorities)
        if len(allocation) != 2:
            return False
        
        # Test statistics
        stats = go.get_stats()
        if stats['total_solutions_explored'] == 0:
            return False
        
        return True


if __name__ == "__main__":
    # Run demo
    go = GlobalOptimizer(OptimizationAlgorithm.GENETIC)
    go.demo()
