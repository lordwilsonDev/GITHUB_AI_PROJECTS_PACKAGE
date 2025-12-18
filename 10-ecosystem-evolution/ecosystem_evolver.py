#!/usr/bin/env python3
"""
Ecosystem Evolver - New Build 6, Phase 4
Co-evolution mechanisms, adaptive ecosystem dynamics, and long-term sustainability
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import random
import math


class EvolutionStrategy(Enum):
    """Evolution strategies"""
    COMPETITIVE = "competitive"      # Competition-driven evolution
    COOPERATIVE = "cooperative"      # Cooperation-driven evolution
    COEVOLUTIONARY = "coevolutionary"  # Mutual evolution
    ADAPTIVE = "adaptive"            # Environment-driven adaptation
    SYMBIOTIC = "symbiotic"          # Symbiotic relationships


class FitnessMetric(Enum):
    """Fitness evaluation metrics"""
    PERFORMANCE = "performance"
    EFFICIENCY = "efficiency"
    ADAPTABILITY = "adaptability"
    RESILIENCE = "resilience"
    SUSTAINABILITY = "sustainability"


class EvolutionPhase(Enum):
    """Phases of ecosystem evolution"""
    INITIALIZATION = "initialization"
    GROWTH = "growth"
    MATURATION = "maturation"
    OPTIMIZATION = "optimization"
    SUSTAINABILITY = "sustainability"


@dataclass
class EcosystemEntity:
    """Represents an entity in the ecosystem"""
    entity_id: str
    entity_type: str
    genome: Dict[str, float]  # Genetic traits
    fitness: float = 0.0
    age: int = 0
    generation: int = 0
    relationships: List[str] = field(default_factory=list)  # Connected entities
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'genome': self.genome,
            'fitness': self.fitness,
            'age': self.age,
            'generation': self.generation,
            'relationships': self.relationships,
            'metadata': self.metadata
        }
    
    def mutate(self, mutation_rate: float = 0.1, mutation_strength: float = 0.2) -> 'EcosystemEntity':
        """Create mutated offspring"""
        new_genome = {}
        for trait, value in self.genome.items():
            if random.random() < mutation_rate:
                # Mutate trait
                delta = random.uniform(-mutation_strength, mutation_strength)
                new_genome[trait] = max(0.0, min(1.0, value + delta))
            else:
                new_genome[trait] = value
        
        offspring = EcosystemEntity(
            entity_id=f"{self.entity_id}_offspring_{random.randint(1000, 9999)}",
            entity_type=self.entity_type,
            genome=new_genome,
            generation=self.generation + 1
        )
        
        return offspring
    
    def crossover(self, other: 'EcosystemEntity') -> 'EcosystemEntity':
        """Create offspring through crossover"""
        new_genome = {}
        for trait in self.genome.keys():
            if trait in other.genome:
                # Random crossover
                if random.random() < 0.5:
                    new_genome[trait] = self.genome[trait]
                else:
                    new_genome[trait] = other.genome[trait]
            else:
                new_genome[trait] = self.genome[trait]
        
        offspring = EcosystemEntity(
            entity_id=f"cross_{self.entity_id}_{other.entity_id}_{random.randint(1000, 9999)}",
            entity_type=self.entity_type,
            genome=new_genome,
            generation=max(self.generation, other.generation) + 1
        )
        
        return offspring


@dataclass
class EvolutionEvent:
    """Represents an evolution event"""
    event_id: str
    event_type: str  # mutation, crossover, selection, extinction, etc.
    entities_involved: List[str]
    generation: int
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'entities_involved': self.entities_involved,
            'generation': self.generation,
            'timestamp': self.timestamp,
            'details': self.details
        }


class FitnessEvaluator:
    """Evaluates entity fitness"""
    
    def __init__(self, metrics: List[FitnessMetric]):
        self.metrics = metrics
        self.evaluation_count = 0
        
    def evaluate(self, entity: EcosystemEntity, environment: Dict[str, Any]) -> float:
        """Evaluate entity fitness"""
        self.evaluation_count += 1
        
        fitness_scores = []
        
        for metric in self.metrics:
            if metric == FitnessMetric.PERFORMANCE:
                # Performance based on genome traits
                score = sum(entity.genome.values()) / len(entity.genome) if entity.genome else 0.0
                fitness_scores.append(score)
            
            elif metric == FitnessMetric.EFFICIENCY:
                # Efficiency based on resource usage
                resource_usage = entity.genome.get('resource_usage', 0.5)
                score = 1.0 - resource_usage  # Lower usage = higher efficiency
                fitness_scores.append(score)
            
            elif metric == FitnessMetric.ADAPTABILITY:
                # Adaptability based on genome diversity
                variance = sum((v - 0.5)**2 for v in entity.genome.values()) / len(entity.genome) if entity.genome else 0.0
                score = 1.0 - variance  # Lower variance = more balanced = more adaptable
                fitness_scores.append(score)
            
            elif metric == FitnessMetric.RESILIENCE:
                # Resilience based on age and relationships
                age_score = min(entity.age / 100.0, 1.0)
                relationship_score = min(len(entity.relationships) / 10.0, 1.0)
                score = (age_score + relationship_score) / 2.0
                fitness_scores.append(score)
            
            elif metric == FitnessMetric.SUSTAINABILITY:
                # Sustainability based on balance
                balance = 1.0 - abs(sum(entity.genome.values()) / len(entity.genome) - 0.5) * 2 if entity.genome else 0.0
                fitness_scores.append(balance)
        
        # Average fitness across all metrics
        fitness = sum(fitness_scores) / len(fitness_scores) if fitness_scores else 0.0
        entity.fitness = fitness
        
        return fitness
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'metrics': [m.value for m in self.metrics],
            'evaluation_count': self.evaluation_count
        }


class SelectionMechanism:
    """Implements selection mechanisms"""
    
    def __init__(self, selection_pressure: float = 0.5):
        self.selection_pressure = selection_pressure  # 0 = no pressure, 1 = maximum pressure
        self.selection_history: List[Dict[str, Any]] = []
        
    def select_survivors(self, entities: List[EcosystemEntity], survival_rate: float = 0.5) -> List[EcosystemEntity]:
        """Select entities that survive to next generation"""
        if not entities:
            return []
        
        # Sort by fitness
        sorted_entities = sorted(entities, key=lambda e: e.fitness, reverse=True)
        
        # Calculate number of survivors
        num_survivors = max(1, int(len(entities) * survival_rate))
        
        # Apply selection pressure
        if self.selection_pressure > 0.5:
            # High pressure: only top performers survive
            survivors = sorted_entities[:num_survivors]
        else:
            # Low pressure: some randomness in selection
            survivors = []
            for i, entity in enumerate(sorted_entities):
                # Probability of survival decreases with rank
                prob = 1.0 - (i / len(sorted_entities)) * self.selection_pressure
                if random.random() < prob and len(survivors) < num_survivors:
                    survivors.append(entity)
            
            # Ensure minimum survivors
            while len(survivors) < num_survivors and sorted_entities:
                survivors.append(sorted_entities[len(survivors)])
        
        self.selection_history.append({
            'total_entities': len(entities),
            'survivors': len(survivors),
            'avg_fitness': sum(e.fitness for e in survivors) / len(survivors) if survivors else 0.0,
            'timestamp': time.time()
        })
        
        return survivors
    
    def tournament_selection(self, entities: List[EcosystemEntity], tournament_size: int = 3) -> EcosystemEntity:
        """Select entity through tournament"""
        tournament = random.sample(entities, min(tournament_size, len(entities)))
        return max(tournament, key=lambda e: e.fitness)
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'selection_pressure': self.selection_pressure,
            'total_selections': len(self.selection_history)
        }


class CoevolutionEngine:
    """Manages co-evolution between entities"""
    
    def __init__(self):
        self.coevolution_pairs: List[Tuple[str, str]] = []
        self.interaction_history: List[Dict[str, Any]] = []
        
    def establish_relationship(self, entity1: EcosystemEntity, entity2: EcosystemEntity, 
                              relationship_type: str = "cooperative") -> bool:
        """Establish co-evolutionary relationship"""
        if entity2.entity_id not in entity1.relationships:
            entity1.relationships.append(entity2.entity_id)
        if entity1.entity_id not in entity2.relationships:
            entity2.relationships.append(entity1.entity_id)
        
        self.coevolution_pairs.append((entity1.entity_id, entity2.entity_id))
        
        self.interaction_history.append({
            'entity1': entity1.entity_id,
            'entity2': entity2.entity_id,
            'type': relationship_type,
            'timestamp': time.time()
        })
        
        return True
    
    def coevolve(self, entity1: EcosystemEntity, entity2: EcosystemEntity) -> Tuple[float, float]:
        """Co-evolve two entities based on their interaction"""
        # Mutual fitness boost based on compatibility
        compatibility = self._calculate_compatibility(entity1, entity2)
        
        fitness_boost = compatibility * 0.1
        entity1.fitness += fitness_boost
        entity2.fitness += fitness_boost
        
        return entity1.fitness, entity2.fitness
    
    def _calculate_compatibility(self, entity1: EcosystemEntity, entity2: EcosystemEntity) -> float:
        """Calculate compatibility between entities"""
        if not entity1.genome or not entity2.genome:
            return 0.0
        
        # Calculate genome similarity
        common_traits = set(entity1.genome.keys()) & set(entity2.genome.keys())
        if not common_traits:
            return 0.0
        
        differences = [abs(entity1.genome[t] - entity2.genome[t]) for t in common_traits]
        avg_difference = sum(differences) / len(differences)
        
        # Compatibility is inverse of difference
        compatibility = 1.0 - avg_difference
        return compatibility
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'total_relationships': len(self.coevolution_pairs),
            'total_interactions': len(self.interaction_history)
        }


class EcosystemEvolver:
    """Main ecosystem evolution system"""
    
    def __init__(self, strategy: EvolutionStrategy = EvolutionStrategy.COEVOLUTIONARY):
        self.strategy = strategy
        self.entities: Dict[str, EcosystemEntity] = {}
        self.fitness_evaluator = FitnessEvaluator([FitnessMetric.PERFORMANCE, FitnessMetric.ADAPTABILITY])
        self.selection_mechanism = SelectionMechanism()
        self.coevolution_engine = CoevolutionEngine()
        self.evolution_events: List[EvolutionEvent] = []
        self.current_generation = 0
        self.current_phase = EvolutionPhase.INITIALIZATION
        self.lock = threading.Lock()
        self.event_counter = 0
        
    def add_entity(self, entity: EcosystemEntity) -> bool:
        """Add entity to ecosystem"""
        with self.lock:
            self.entities[entity.entity_id] = entity
            return True
    
    def remove_entity(self, entity_id: str) -> bool:
        """Remove entity from ecosystem"""
        with self.lock:
            if entity_id in self.entities:
                del self.entities[entity_id]
                return True
            return False
    
    def evolve_generation(self, mutation_rate: float = 0.1, crossover_rate: float = 0.3) -> int:
        """Evolve ecosystem by one generation"""
        with self.lock:
            entities_list = list(self.entities.values())
        
        if not entities_list:
            return 0
        
        # 1. Evaluate fitness
        environment = {'generation': self.current_generation}
        for entity in entities_list:
            self.fitness_evaluator.evaluate(entity, environment)
            entity.age += 1
        
        # 2. Selection
        survivors = self.selection_mechanism.select_survivors(entities_list, survival_rate=0.6)
        
        # 3. Create offspring
        offspring = []
        
        # Mutation
        for entity in survivors:
            if random.random() < mutation_rate:
                mutant = entity.mutate(mutation_rate=0.2)
                offspring.append(mutant)
                
                self._record_event("mutation", [entity.entity_id, mutant.entity_id])
        
        # Crossover
        if len(survivors) >= 2:
            num_crossovers = int(len(survivors) * crossover_rate)
            for _ in range(num_crossovers):
                parent1 = self.selection_mechanism.tournament_selection(survivors)
                parent2 = self.selection_mechanism.tournament_selection(survivors)
                if parent1.entity_id != parent2.entity_id:
                    child = parent1.crossover(parent2)
                    offspring.append(child)
                    
                    self._record_event("crossover", [parent1.entity_id, parent2.entity_id, child.entity_id])
        
        # 4. Update population
        with self.lock:
            self.entities.clear()
            for entity in survivors + offspring:
                self.entities[entity.entity_id] = entity
        
        # 5. Co-evolution (if applicable)
        if self.strategy == EvolutionStrategy.COEVOLUTIONARY:
            self._apply_coevolution()
        
        self.current_generation += 1
        self._update_phase()
        
        return len(self.entities)
    
    def _apply_coevolution(self):
        """Apply co-evolutionary dynamics"""
        entities_list = list(self.entities.values())
        
        # Establish new relationships
        if len(entities_list) >= 2:
            for _ in range(min(5, len(entities_list) // 2)):
                entity1 = random.choice(entities_list)
                entity2 = random.choice(entities_list)
                if entity1.entity_id != entity2.entity_id:
                    self.coevolution_engine.establish_relationship(entity1, entity2)
                    self.coevolution_engine.coevolve(entity1, entity2)
    
    def _record_event(self, event_type: str, entities: List[str]):
        """Record evolution event"""
        self.event_counter += 1
        event = EvolutionEvent(
            event_id=f"event_{self.event_counter}",
            event_type=event_type,
            entities_involved=entities,
            generation=self.current_generation
        )
        self.evolution_events.append(event)
    
    def _update_phase(self):
        """Update evolution phase based on generation"""
        if self.current_generation < 5:
            self.current_phase = EvolutionPhase.INITIALIZATION
        elif self.current_generation < 15:
            self.current_phase = EvolutionPhase.GROWTH
        elif self.current_generation < 30:
            self.current_phase = EvolutionPhase.MATURATION
        elif self.current_generation < 50:
            self.current_phase = EvolutionPhase.OPTIMIZATION
        else:
            self.current_phase = EvolutionPhase.SUSTAINABILITY
    
    def get_population_stats(self) -> Dict[str, Any]:
        """Get population statistics"""
        with self.lock:
            if not self.entities:
                return {
                    'population_size': 0,
                    'avg_fitness': 0.0,
                    'max_fitness': 0.0,
                    'avg_age': 0.0,
                    'max_generation': 0
                }
            
            entities_list = list(self.entities.values())
            
            return {
                'population_size': len(entities_list),
                'avg_fitness': sum(e.fitness for e in entities_list) / len(entities_list),
                'max_fitness': max(e.fitness for e in entities_list),
                'avg_age': sum(e.age for e in entities_list) / len(entities_list),
                'max_generation': max(e.generation for e in entities_list)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        return {
            'strategy': self.strategy.value,
            'current_generation': self.current_generation,
            'current_phase': self.current_phase.value,
            'population': self.get_population_stats(),
            'fitness_evaluator': self.fitness_evaluator.get_stats(),
            'selection_mechanism': self.selection_mechanism.get_stats(),
            'coevolution_engine': self.coevolution_engine.get_stats(),
            'total_events': len(self.evolution_events)
        }
    
    def demo(self) -> Dict[str, Any]:
        """Demonstrate ecosystem evolution capabilities"""
        print("\n=== Ecosystem Evolver Demo ===")
        
        # 1. Initialize population
        print("\n1. Initializing population...")
        for i in range(10):
            entity = EcosystemEntity(
                entity_id=f"entity_{i}",
                entity_type="agent",
                genome={
                    'speed': random.random(),
                    'strength': random.random(),
                    'intelligence': random.random(),
                    'resource_usage': random.random()
                }
            )
            self.add_entity(entity)
        print(f"   Initialized {len(self.entities)} entities")
        
        # 2. Show initial stats
        print("\n2. Initial population statistics:")
        initial_stats = self.get_population_stats()
        print(f"   Population size: {initial_stats['population_size']}")
        print(f"   Average fitness: {initial_stats['avg_fitness']:.3f}")
        
        # 3. Evolve for multiple generations
        print("\n3. Evolving ecosystem...")
        generations_to_evolve = 10
        for gen in range(generations_to_evolve):
            pop_size = self.evolve_generation(mutation_rate=0.15, crossover_rate=0.3)
            if (gen + 1) % 3 == 0:
                stats = self.get_population_stats()
                print(f"   Generation {self.current_generation}: {pop_size} entities, avg fitness: {stats['avg_fitness']:.3f}")
        
        # 4. Show final stats
        print("\n4. Final population statistics:")
        final_stats = self.get_population_stats()
        print(f"   Population size: {final_stats['population_size']}")
        print(f"   Average fitness: {final_stats['avg_fitness']:.3f}")
        print(f"   Max fitness: {final_stats['max_fitness']:.3f}")
        print(f"   Average age: {final_stats['avg_age']:.1f}")
        print(f"   Max generation: {final_stats['max_generation']}")
        print(f"   Fitness improvement: {final_stats['avg_fitness'] - initial_stats['avg_fitness']:.3f}")
        
        # 5. Show evolution events
        print("\n5. Evolution events:")
        event_types = defaultdict(int)
        for event in self.evolution_events:
            event_types[event.event_type] += 1
        for event_type, count in event_types.items():
            print(f"   {event_type}: {count} events")
        
        # 6. Show current phase
        print(f"\n6. Current evolution phase: {self.current_phase.value}")
        
        # 7. Get comprehensive statistics
        print("\n7. System statistics:")
        stats = self.get_stats()
        print(f"   Strategy: {stats['strategy']}")
        print(f"   Total generations: {stats['current_generation']}")
        print(f"   Total evolution events: {stats['total_events']}")
        print(f"   Fitness evaluations: {stats['fitness_evaluator']['evaluation_count']}")
        print(f"   Co-evolutionary relationships: {stats['coevolution_engine']['total_relationships']}")
        
        print("\n=== Demo Complete ===")
        return stats


class EcosystemEvolverContract:
    """Contract interface for testing"""
    
    @staticmethod
    def create() -> EcosystemEvolver:
        """Create an ecosystem evolver instance"""
        return EcosystemEvolver()
    
    @staticmethod
    def verify() -> bool:
        """Verify ecosystem evolver functionality"""
        ee = EcosystemEvolver()
        
        # Test entity addition
        entity = EcosystemEntity(
            entity_id="test_entity",
            entity_type="test",
            genome={'trait1': 0.5, 'trait2': 0.7}
        )
        if not ee.add_entity(entity):
            return False
        
        # Test evolution
        pop_size = ee.evolve_generation()
        if pop_size == 0:
            return False
        
        # Test statistics
        stats = ee.get_population_stats()
        if stats['population_size'] == 0:
            return False
        
        # Test comprehensive stats
        full_stats = ee.get_stats()
        if full_stats['current_generation'] == 0:
            return False
        
        return True


if __name__ == "__main__":
    # Run demo
    ee = EcosystemEvolver(EvolutionStrategy.COEVOLUTIONARY)
    ee.demo()
