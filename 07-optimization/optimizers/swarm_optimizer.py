#!/usr/bin/env python3
"""
Swarm Intelligence Optimizer - New Build 6, Phase 1
Swarm behavior algorithms, emergent collective intelligence, and self-organizing systems
"""

import random
import math
import time
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading


class SwarmBehavior(Enum):
    """Types of swarm behaviors"""
    FLOCKING = "flocking"
    FORAGING = "foraging"
    CLUSTERING = "clustering"
    EXPLORATION = "exploration"
    CONVERGENCE = "convergence"


@dataclass
class Agent:
    """Individual agent in the swarm"""
    agent_id: str
    position: List[float]
    velocity: List[float]
    best_position: List[float]
    best_fitness: float = float('inf')
    fitness: float = float('inf')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'agent_id': self.agent_id,
            'position': self.position,
            'velocity': self.velocity,
            'fitness': self.fitness,
            'best_fitness': self.best_fitness
        }


@dataclass
class SwarmState:
    """Current state of the swarm"""
    iteration: int
    global_best_position: List[float]
    global_best_fitness: float
    average_fitness: float
    diversity: float
    convergence_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'iteration': self.iteration,
            'global_best_position': self.global_best_position,
            'global_best_fitness': self.global_best_fitness,
            'average_fitness': self.average_fitness,
            'diversity': self.diversity,
            'convergence_rate': self.convergence_rate
        }


class ParticleSwarmOptimizer:
    """Particle Swarm Optimization algorithm"""
    
    def __init__(self, dimensions: int = 2, swarm_size: int = 30,
                 inertia: float = 0.7, cognitive: float = 1.5, social: float = 1.5):
        self.dimensions = dimensions
        self.swarm_size = swarm_size
        self.inertia = inertia
        self.cognitive = cognitive
        self.social = social
        self.agents: List[Agent] = []
        self.global_best_position: List[float] = [0.0] * dimensions
        self.global_best_fitness = float('inf')
        self.iteration = 0
        
    def initialize_swarm(self, bounds: Tuple[float, float] = (-10.0, 10.0)):
        """Initialize swarm with random positions"""
        self.agents = []
        for i in range(self.swarm_size):
            position = [random.uniform(bounds[0], bounds[1]) for _ in range(self.dimensions)]
            velocity = [random.uniform(-1, 1) for _ in range(self.dimensions)]
            
            agent = Agent(
                agent_id=f"particle_{i}",
                position=position.copy(),
                velocity=velocity,
                best_position=position.copy()
            )
            self.agents.append(agent)
    
    def evaluate_fitness(self, fitness_function: Callable[[List[float]], float]):
        """Evaluate fitness for all agents"""
        for agent in self.agents:
            agent.fitness = fitness_function(agent.position)
            
            # Update personal best
            if agent.fitness < agent.best_fitness:
                agent.best_fitness = agent.fitness
                agent.best_position = agent.position.copy()
            
            # Update global best
            if agent.fitness < self.global_best_fitness:
                self.global_best_fitness = agent.fitness
                self.global_best_position = agent.position.copy()
    
    def update_velocities(self):
        """Update agent velocities based on PSO formula"""
        for agent in self.agents:
            for d in range(self.dimensions):
                r1, r2 = random.random(), random.random()
                
                cognitive_component = self.cognitive * r1 * (agent.best_position[d] - agent.position[d])
                social_component = self.social * r2 * (self.global_best_position[d] - agent.position[d])
                
                agent.velocity[d] = (self.inertia * agent.velocity[d] + 
                                    cognitive_component + social_component)
                
                # Velocity clamping
                max_velocity = 2.0
                agent.velocity[d] = max(-max_velocity, min(max_velocity, agent.velocity[d]))
    
    def update_positions(self):
        """Update agent positions"""
        for agent in self.agents:
            for d in range(self.dimensions):
                agent.position[d] += agent.velocity[d]
    
    def optimize(self, fitness_function: Callable[[List[float]], float], 
                iterations: int = 100) -> SwarmState:
        """Run optimization"""
        self.initialize_swarm()
        
        for i in range(iterations):
            self.iteration = i
            self.evaluate_fitness(fitness_function)
            self.update_velocities()
            self.update_positions()
        
        # Calculate final metrics
        avg_fitness = sum(a.fitness for a in self.agents) / len(self.agents)
        diversity = self._calculate_diversity()
        convergence = 1.0 - (self.global_best_fitness / (avg_fitness + 1e-10))
        
        return SwarmState(
            iteration=self.iteration,
            global_best_position=self.global_best_position,
            global_best_fitness=self.global_best_fitness,
            average_fitness=avg_fitness,
            diversity=diversity,
            convergence_rate=convergence
        )
    
    def _calculate_diversity(self) -> float:
        """Calculate swarm diversity"""
        if not self.agents:
            return 0.0
        
        center = [sum(a.position[d] for a in self.agents) / len(self.agents) 
                 for d in range(self.dimensions)]
        
        distances = []
        for agent in self.agents:
            dist = math.sqrt(sum((agent.position[d] - center[d])**2 
                               for d in range(self.dimensions)))
            distances.append(dist)
        
        return sum(distances) / len(distances) if distances else 0.0


class AntColonyOptimizer:
    """Ant Colony Optimization for path finding"""
    
    def __init__(self, num_ants: int = 20, num_nodes: int = 10,
                 alpha: float = 1.0, beta: float = 2.0, evaporation: float = 0.5):
        self.num_ants = num_ants
        self.num_nodes = num_nodes
        self.alpha = alpha  # Pheromone importance
        self.beta = beta    # Distance importance
        self.evaporation = evaporation
        self.pheromones = [[1.0 for _ in range(num_nodes)] for _ in range(num_nodes)]
        self.best_path: List[int] = []
        self.best_distance = float('inf')
    
    def optimize(self, distance_matrix: List[List[float]], iterations: int = 50) -> Dict[str, Any]:
        """Run ACO optimization"""
        for iteration in range(iterations):
            paths = []
            distances = []
            
            # Each ant constructs a path
            for ant in range(self.num_ants):
                path = self._construct_path(distance_matrix)
                distance = self._calculate_path_distance(path, distance_matrix)
                paths.append(path)
                distances.append(distance)
                
                # Update best path
                if distance < self.best_distance:
                    self.best_distance = distance
                    self.best_path = path
            
            # Update pheromones
            self._update_pheromones(paths, distances)
        
        return {
            'best_path': self.best_path,
            'best_distance': self.best_distance,
            'iterations': iterations
        }
    
    def _construct_path(self, distance_matrix: List[List[float]]) -> List[int]:
        """Construct path for one ant"""
        path = [0]  # Start at node 0
        unvisited = set(range(1, self.num_nodes))
        
        while unvisited:
            current = path[-1]
            next_node = self._select_next_node(current, unvisited, distance_matrix)
            path.append(next_node)
            unvisited.remove(next_node)
        
        return path
    
    def _select_next_node(self, current: int, unvisited: set, 
                         distance_matrix: List[List[float]]) -> int:
        """Select next node based on pheromones and distance"""
        probabilities = []
        
        for node in unvisited:
            pheromone = self.pheromones[current][node] ** self.alpha
            distance = (1.0 / (distance_matrix[current][node] + 1e-10)) ** self.beta
            probabilities.append((node, pheromone * distance))
        
        total = sum(p[1] for p in probabilities)
        if total == 0:
            return random.choice(list(unvisited))
        
        probabilities = [(n, p/total) for n, p in probabilities]
        
        # Roulette wheel selection
        r = random.random()
        cumulative = 0.0
        for node, prob in probabilities:
            cumulative += prob
            if r <= cumulative:
                return node
        
        return probabilities[-1][0]
    
    def _calculate_path_distance(self, path: List[int], 
                                 distance_matrix: List[List[float]]) -> float:
        """Calculate total path distance"""
        distance = 0.0
        for i in range(len(path) - 1):
            distance += distance_matrix[path[i]][path[i+1]]
        return distance
    
    def _update_pheromones(self, paths: List[List[int]], distances: List[float]):
        """Update pheromone trails"""
        # Evaporation
        for i in range(self.num_nodes):
            for j in range(self.num_nodes):
                self.pheromones[i][j] *= (1 - self.evaporation)
        
        # Add new pheromones
        for path, distance in zip(paths, distances):
            pheromone_deposit = 1.0 / (distance + 1e-10)
            for i in range(len(path) - 1):
                self.pheromones[path[i]][path[i+1]] += pheromone_deposit


class SwarmOptimizer:
    """Main swarm intelligence optimization system"""
    
    def __init__(self):
        self.pso = ParticleSwarmOptimizer()
        self.aco = AntColonyOptimizer()
        self.optimization_history: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
    
    def optimize_continuous(self, fitness_function: Callable[[List[float]], float],
                          dimensions: int = 2, iterations: int = 100) -> SwarmState:
        """Optimize continuous problem using PSO"""
        self.pso = ParticleSwarmOptimizer(dimensions=dimensions)
        result = self.pso.optimize(fitness_function, iterations)
        
        with self.lock:
            self.optimization_history.append({
                'type': 'PSO',
                'result': result.to_dict(),
                'timestamp': time.time()
            })
        
        return result
    
    def optimize_discrete(self, distance_matrix: List[List[float]], 
                         iterations: int = 50) -> Dict[str, Any]:
        """Optimize discrete problem using ACO"""
        num_nodes = len(distance_matrix)
        self.aco = AntColonyOptimizer(num_nodes=num_nodes)
        result = self.aco.optimize(distance_matrix, iterations)
        
        with self.lock:
            self.optimization_history.append({
                'type': 'ACO',
                'result': result,
                'timestamp': time.time()
            })
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        with self.lock:
            return {
                'total_optimizations': len(self.optimization_history),
                'pso_runs': len([h for h in self.optimization_history if h['type'] == 'PSO']),
                'aco_runs': len([h for h in self.optimization_history if h['type'] == 'ACO'])
            }
    
    def demo(self) -> Dict[str, Any]:
        """Demonstration of swarm intelligence optimization"""
        print("\n🐝 Swarm Intelligence Optimizer Demo")
        print("=" * 60)
        
        # Demo 1: PSO for continuous optimization
        print("\n[1] Particle Swarm Optimization (PSO)")
        print("    Optimizing Sphere function: f(x) = sum(x_i^2)")
        
        def sphere_function(position: List[float]) -> float:
            return sum(x**2 for x in position)
        
        pso_result = self.optimize_continuous(sphere_function, dimensions=3, iterations=50)
        
        print(f"    ✅ Optimization Complete:")
        print(f"       Best Position: [{', '.join(f'{x:.4f}' for x in pso_result.global_best_position)}]")
        print(f"       Best Fitness: {pso_result.global_best_fitness:.6f}")
        print(f"       Average Fitness: {pso_result.average_fitness:.6f}")
        print(f"       Swarm Diversity: {pso_result.diversity:.4f}")
        print(f"       Convergence Rate: {pso_result.convergence_rate:.2%}")
        
        # Demo 2: ACO for discrete optimization
        print("\n[2] Ant Colony Optimization (ACO)")
        print("    Solving Traveling Salesman Problem (5 cities)")
        
        # Create random distance matrix
        num_cities = 5
        distance_matrix = [[0.0 for _ in range(num_cities)] for _ in range(num_cities)]
        for i in range(num_cities):
            for j in range(i+1, num_cities):
                dist = random.uniform(1.0, 10.0)
                distance_matrix[i][j] = dist
                distance_matrix[j][i] = dist
        
        aco_result = self.optimize_discrete(distance_matrix, iterations=30)
        
        print(f"    ✅ Optimization Complete:")
        print(f"       Best Path: {' -> '.join(map(str, aco_result['best_path']))}")
        print(f"       Best Distance: {aco_result['best_distance']:.4f}")
        print(f"       Iterations: {aco_result['iterations']}")
        
        # Get statistics
        stats = self.get_statistics()
        print(f"\n📊 System Statistics:")
        print(f"   Total Optimizations: {stats['total_optimizations']}")
        print(f"   PSO Runs: {stats['pso_runs']}")
        print(f"   ACO Runs: {stats['aco_runs']}")
        
        print("\n✅ Swarm Intelligence Optimizer operational")
        
        return {
            'pso_result': pso_result.to_dict(),
            'aco_result': aco_result,
            'statistics': stats
        }


# Contract test interface
class SwarmOptimizerContract:
    """Contract interface for testing"""
    
    @staticmethod
    def create() -> SwarmOptimizer:
        """Create instance"""
        return SwarmOptimizer()
    
    @staticmethod
    def test_basic_operations() -> bool:
        """Test basic operations"""
        optimizer = SwarmOptimizer()
        
        # Test PSO
        def simple_function(pos: List[float]) -> float:
            return sum(x**2 for x in pos)
        
        pso_result = optimizer.optimize_continuous(simple_function, dimensions=2, iterations=10)
        assert pso_result.global_best_fitness >= 0
        assert len(pso_result.global_best_position) == 2
        
        # Test ACO
        distance_matrix = [[0, 1, 2], [1, 0, 3], [2, 3, 0]]
        aco_result = optimizer.optimize_discrete(distance_matrix, iterations=5)
        assert len(aco_result['best_path']) == 3
        assert aco_result['best_distance'] > 0
        
        return True


if __name__ == '__main__':
    # Run demo
    optimizer = SwarmOptimizer()
    optimizer.demo()
