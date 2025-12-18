#!/usr/bin/env python3
"""
Meta-Learning Framework (T-068) - New Build 7 Phase 2

This module provides comprehensive meta-learning capabilities:
- Learning to learn from experience
- Strategy adaptation based on task performance
- Transfer learning across domains
- Meta-optimization of learning parameters
"""

import json
import math
import threading
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from collections import defaultdict


class LearningStrategy(Enum):
    """Types of learning strategies"""
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    REINFORCEMENT = "reinforcement"
    TRANSFER = "transfer"
    FEW_SHOT = "few_shot"
    ZERO_SHOT = "zero_shot"
    META = "meta"


class TaskDomain(Enum):
    """Task domain categories"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    OPTIMIZATION = "optimization"
    REASONING = "reasoning"
    GENERATION = "generation"


@dataclass
class LearningTask:
    """Represents a learning task"""
    task_id: str
    domain: TaskDomain
    description: str
    input_dim: int
    output_dim: int
    complexity: float  # 0.0 to 1.0
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "domain": self.domain.value,
            "description": self.description,
            "input_dim": self.input_dim,
            "output_dim": self.output_dim,
            "complexity": self.complexity,
            "metadata": self.metadata
        }


@dataclass
class LearningExperience:
    """Records a learning experience"""
    task: LearningTask
    strategy: LearningStrategy
    performance: float  # 0.0 to 1.0
    learning_rate: float
    iterations: int
    convergence_time: float
    final_loss: float
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task": self.task.to_dict(),
            "strategy": self.strategy.value,
            "performance": self.performance,
            "learning_rate": self.learning_rate,
            "iterations": self.iterations,
            "convergence_time": self.convergence_time,
            "final_loss": self.final_loss,
            "timestamp": self.timestamp
        }


class ExperienceMemory:
    """Stores and retrieves learning experiences"""
    
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.experiences: List[LearningExperience] = []
        self.domain_index: Dict[TaskDomain, List[int]] = defaultdict(list)
        self.strategy_index: Dict[LearningStrategy, List[int]] = defaultdict(list)
        self.lock = threading.Lock()
    
    def add_experience(self, experience: LearningExperience):
        """Add a learning experience to memory"""
        with self.lock:
            if len(self.experiences) >= self.capacity:
                # Remove oldest experience
                old_exp = self.experiences.pop(0)
                # Update indices
                self._remove_from_indices(old_exp, 0)
                # Shift all indices down
                for domain in self.domain_index:
                    self.domain_index[domain] = [i-1 for i in self.domain_index[domain] if i > 0]
                for strategy in self.strategy_index:
                    self.strategy_index[strategy] = [i-1 for i in self.strategy_index[strategy] if i > 0]
            
            idx = len(self.experiences)
            self.experiences.append(experience)
            self.domain_index[experience.task.domain].append(idx)
            self.strategy_index[experience.strategy].append(idx)
    
    def _remove_from_indices(self, experience: LearningExperience, idx: int):
        """Remove experience from indices"""
        if idx in self.domain_index[experience.task.domain]:
            self.domain_index[experience.task.domain].remove(idx)
        if idx in self.strategy_index[experience.strategy]:
            self.strategy_index[experience.strategy].remove(idx)
    
    def get_by_domain(self, domain: TaskDomain) -> List[LearningExperience]:
        """Retrieve experiences by domain"""
        with self.lock:
            indices = self.domain_index.get(domain, [])
            return [self.experiences[i] for i in indices]
    
    def get_by_strategy(self, strategy: LearningStrategy) -> List[LearningExperience]:
        """Retrieve experiences by strategy"""
        with self.lock:
            indices = self.strategy_index.get(strategy, [])
            return [self.experiences[i] for i in indices]
    
    def get_similar_tasks(self, task: LearningTask, top_k: int = 5) -> List[LearningExperience]:
        """Find similar tasks based on characteristics"""
        with self.lock:
            domain_exps = self.get_by_domain(task.domain)
            
            # Calculate similarity scores
            scored = []
            for exp in domain_exps:
                similarity = self._calculate_similarity(task, exp.task)
                scored.append((similarity, exp))
            
            # Sort by similarity and return top k
            scored.sort(reverse=True, key=lambda x: x[0])
            return [exp for _, exp in scored[:top_k]]
    
    def _calculate_similarity(self, task1: LearningTask, task2: LearningTask) -> float:
        """Calculate similarity between two tasks"""
        # Dimension similarity
        dim_sim = 1.0 - abs(task1.input_dim - task2.input_dim) / max(task1.input_dim, task2.input_dim)
        out_sim = 1.0 - abs(task1.output_dim - task2.output_dim) / max(task1.output_dim, task2.output_dim)
        
        # Complexity similarity
        comp_sim = 1.0 - abs(task1.complexity - task2.complexity)
        
        # Weighted average
        return 0.3 * dim_sim + 0.3 * out_sim + 0.4 * comp_sim
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics"""
        with self.lock:
            return {
                "total_experiences": len(self.experiences),
                "capacity": self.capacity,
                "domains": {domain.value: len(indices) for domain, indices in self.domain_index.items()},
                "strategies": {strategy.value: len(indices) for strategy, indices in self.strategy_index.items()}
            }


class StrategySelector:
    """Selects optimal learning strategy based on task and experience"""
    
    def __init__(self, memory: ExperienceMemory):
        self.memory = memory
        self.strategy_performance: Dict[LearningStrategy, List[float]] = defaultdict(list)
        self.lock = threading.Lock()
    
    def select_strategy(self, task: LearningTask) -> Tuple[LearningStrategy, float]:
        """Select best strategy for a task"""
        # Get similar past experiences
        similar = self.memory.get_similar_tasks(task, top_k=10)
        
        if not similar:
            # No experience, use default strategy based on domain
            return self._default_strategy(task), 0.5
        
        # Analyze strategy performance on similar tasks
        strategy_scores: Dict[LearningStrategy, List[float]] = defaultdict(list)
        for exp in similar:
            strategy_scores[exp.strategy].append(exp.performance)
        
        # Calculate average performance per strategy
        avg_scores = {}
        for strategy, scores in strategy_scores.items():
            avg_scores[strategy] = sum(scores) / len(scores)
        
        # Select best strategy
        best_strategy = max(avg_scores.items(), key=lambda x: x[1])
        return best_strategy[0], best_strategy[1]
    
    def _default_strategy(self, task: LearningTask) -> LearningStrategy:
        """Return default strategy based on task domain"""
        domain_defaults = {
            TaskDomain.CLASSIFICATION: LearningStrategy.SUPERVISED,
            TaskDomain.REGRESSION: LearningStrategy.SUPERVISED,
            TaskDomain.CLUSTERING: LearningStrategy.UNSUPERVISED,
            TaskDomain.OPTIMIZATION: LearningStrategy.REINFORCEMENT,
            TaskDomain.REASONING: LearningStrategy.META,
            TaskDomain.GENERATION: LearningStrategy.TRANSFER
        }
        return domain_defaults.get(task.domain, LearningStrategy.SUPERVISED)
    
    def update_performance(self, strategy: LearningStrategy, performance: float):
        """Update strategy performance tracking"""
        with self.lock:
            self.strategy_performance[strategy].append(performance)
    
    def get_strategy_stats(self) -> Dict[str, Any]:
        """Get strategy performance statistics"""
        with self.lock:
            stats = {}
            for strategy, perfs in self.strategy_performance.items():
                if perfs:
                    stats[strategy.value] = {
                        "count": len(perfs),
                        "avg_performance": sum(perfs) / len(perfs),
                        "min": min(perfs),
                        "max": max(perfs)
                    }
            return stats


class HyperparameterOptimizer:
    """Optimizes learning hyperparameters based on meta-learning"""
    
    def __init__(self, memory: ExperienceMemory):
        self.memory = memory
        self.param_ranges = {
            "learning_rate": (0.0001, 0.1),
            "batch_size": (8, 256),
            "momentum": (0.0, 0.99),
            "weight_decay": (0.0, 0.01)
        }
        self.lock = threading.Lock()
    
    def suggest_hyperparameters(self, task: LearningTask, strategy: LearningStrategy) -> Dict[str, float]:
        """Suggest hyperparameters based on similar tasks"""
        # Get similar experiences
        similar = self.memory.get_similar_tasks(task, top_k=5)
        
        if not similar:
            # No experience, return defaults
            return self._default_hyperparameters()
        
        # Filter by strategy
        strategy_similar = [exp for exp in similar if exp.strategy == strategy]
        
        if not strategy_similar:
            strategy_similar = similar  # Fall back to all similar
        
        # Find best performing configuration
        best_exp = max(strategy_similar, key=lambda x: x.performance)
        
        # Return hyperparameters from best experience
        return {
            "learning_rate": best_exp.learning_rate,
            "iterations": best_exp.iterations
        }
    
    def _default_hyperparameters(self) -> Dict[str, float]:
        """Return default hyperparameters"""
        return {
            "learning_rate": 0.001,
            "iterations": 1000
        }
    
    def optimize_online(self, task: LearningTask, strategy: LearningStrategy,
                       current_params: Dict[str, float], performance: float) -> Dict[str, float]:
        """Adjust hyperparameters during learning"""
        new_params = current_params.copy()
        
        # Simple adaptive adjustment
        if performance < 0.5:
            # Poor performance, try different learning rate
            new_params["learning_rate"] *= 0.8
        elif performance > 0.8:
            # Good performance, try to speed up
            new_params["learning_rate"] *= 1.1
        
        # Clip to valid ranges
        lr_min, lr_max = self.param_ranges["learning_rate"]
        new_params["learning_rate"] = max(lr_min, min(lr_max, new_params["learning_rate"]))
        
        return new_params


class TransferLearningEngine:
    """Enables transfer learning across domains"""
    
    def __init__(self, memory: ExperienceMemory):
        self.memory = memory
        self.domain_embeddings: Dict[TaskDomain, List[float]] = {}
        self.lock = threading.Lock()
    
    def find_transferable_knowledge(self, target_task: LearningTask) -> List[LearningExperience]:
        """Find experiences that can transfer to target task"""
        # Get experiences from same domain
        same_domain = self.memory.get_by_domain(target_task.domain)
        
        # Get experiences from related domains
        related = []
        for domain in TaskDomain:
            if domain != target_task.domain:
                exps = self.memory.get_by_domain(domain)
                # Filter by similarity
                for exp in exps:
                    if self._is_transferable(exp.task, target_task):
                        related.append(exp)
        
        # Combine and sort by relevance
        all_candidates = same_domain + related
        scored = [(self._transfer_score(exp, target_task), exp) for exp in all_candidates]
        scored.sort(reverse=True, key=lambda x: x[0])
        
        return [exp for _, exp in scored[:10]]
    
    def _is_transferable(self, source: LearningTask, target: LearningTask) -> bool:
        """Check if knowledge can transfer between tasks"""
        # Similar complexity
        complexity_diff = abs(source.complexity - target.complexity)
        if complexity_diff > 0.3:
            return False
        
        # Compatible dimensions
        if source.input_dim > target.input_dim * 2 or target.input_dim > source.input_dim * 2:
            return False
        
        return True
    
    def _transfer_score(self, experience: LearningExperience, target: LearningTask) -> float:
        """Calculate transfer learning score"""
        # Base on task similarity and experience performance
        similarity = self.memory._calculate_similarity(experience.task, target)
        return similarity * experience.performance
    
    def apply_transfer(self, source_exp: LearningExperience, target_task: LearningTask) -> Dict[str, Any]:
        """Apply transfer learning from source to target"""
        return {
            "source_task": source_exp.task.task_id,
            "target_task": target_task.task_id,
            "transferred_strategy": source_exp.strategy.value,
            "initial_learning_rate": source_exp.learning_rate * 0.5,  # Start slower
            "expected_performance": source_exp.performance * 0.8  # Conservative estimate
        }


class MetaLearningFramework:
    """Main meta-learning framework integrating all components"""
    
    def __init__(self, memory_capacity: int = 1000):
        self.memory = ExperienceMemory(capacity=memory_capacity)
        self.strategy_selector = StrategySelector(self.memory)
        self.hyperparam_optimizer = HyperparameterOptimizer(self.memory)
        self.transfer_engine = TransferLearningEngine(self.memory)
        self.learning_history: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
    
    def learn_task(self, task: LearningTask, data: Optional[Any] = None) -> Dict[str, Any]:
        """Learn a new task using meta-learning"""
        # Select optimal strategy
        strategy, confidence = self.strategy_selector.select_strategy(task)
        
        # Get hyperparameters
        hyperparams = self.hyperparam_optimizer.suggest_hyperparameters(task, strategy)
        
        # Check for transferable knowledge
        transfer_candidates = self.transfer_engine.find_transferable_knowledge(task)
        
        # Simulate learning (in real implementation, this would train a model)
        performance = self._simulate_learning(task, strategy, hyperparams)
        
        # Create experience record
        experience = LearningExperience(
            task=task,
            strategy=strategy,
            performance=performance,
            learning_rate=hyperparams["learning_rate"],
            iterations=hyperparams["iterations"],
            convergence_time=hyperparams["iterations"] * 0.01,
            final_loss=1.0 - performance,
            timestamp=datetime.now().isoformat()
        )
        
        # Store experience
        self.memory.add_experience(experience)
        self.strategy_selector.update_performance(strategy, performance)
        
        # Record in history
        result = {
            "task_id": task.task_id,
            "strategy": strategy.value,
            "confidence": confidence,
            "hyperparameters": hyperparams,
            "transfer_used": len(transfer_candidates) > 0,
            "performance": performance,
            "timestamp": experience.timestamp
        }
        
        with self.lock:
            self.learning_history.append(result)
        
        return result
    
    def _simulate_learning(self, task: LearningTask, strategy: LearningStrategy,
                          hyperparams: Dict[str, float]) -> float:
        """Simulate learning process (placeholder for actual training)"""
        # Base performance on task complexity and strategy appropriateness
        base_perf = 0.5
        
        # Adjust for complexity
        complexity_factor = 1.0 - (task.complexity * 0.3)
        
        # Adjust for learning rate
        lr_factor = 1.0 if 0.0001 <= hyperparams["learning_rate"] <= 0.01 else 0.8
        
        # Calculate final performance
        performance = base_perf * complexity_factor * lr_factor
        
        # Add some variance
        import random
        performance += random.uniform(-0.1, 0.1)
        
        return max(0.0, min(1.0, performance))
    
    def get_meta_insights(self) -> Dict[str, Any]:
        """Get insights from meta-learning"""
        return {
            "total_tasks_learned": len(self.learning_history),
            "memory_stats": self.memory.get_statistics(),
            "strategy_stats": self.strategy_selector.get_strategy_stats(),
            "avg_performance": sum(h["performance"] for h in self.learning_history) / len(self.learning_history) if self.learning_history else 0.0,
            "transfer_usage_rate": sum(1 for h in self.learning_history if h["transfer_used"]) / len(self.learning_history) if self.learning_history else 0.0
        }
    
    def export_knowledge(self, filepath: str):
        """Export learned knowledge to file"""
        knowledge = {
            "experiences": [exp.to_dict() for exp in self.memory.experiences],
            "learning_history": self.learning_history,
            "meta_insights": self.get_meta_insights()
        }
        
        with open(filepath, 'w') as f:
            json.dump(knowledge, f, indent=2)
    
    def import_knowledge(self, filepath: str):
        """Import learned knowledge from file"""
        with open(filepath, 'r') as f:
            knowledge = json.load(f)
        
        # Reconstruct experiences
        for exp_dict in knowledge.get("experiences", []):
            task = LearningTask(
                task_id=exp_dict["task"]["task_id"],
                domain=TaskDomain(exp_dict["task"]["domain"]),
                description=exp_dict["task"]["description"],
                input_dim=exp_dict["task"]["input_dim"],
                output_dim=exp_dict["task"]["output_dim"],
                complexity=exp_dict["task"]["complexity"],
                metadata=exp_dict["task"]["metadata"]
            )
            
            experience = LearningExperience(
                task=task,
                strategy=LearningStrategy(exp_dict["strategy"]),
                performance=exp_dict["performance"],
                learning_rate=exp_dict["learning_rate"],
                iterations=exp_dict["iterations"],
                convergence_time=exp_dict["convergence_time"],
                final_loss=exp_dict["final_loss"],
                timestamp=exp_dict["timestamp"]
            )
            
            self.memory.add_experience(experience)


# Contract test interface
class MetaLearningFrameworkContract:
    """Contract interface for testing"""
    
    @staticmethod
    def create() -> MetaLearningFramework:
        """Create instance for testing"""
        return MetaLearningFramework(memory_capacity=100)
    
    @staticmethod
    def test_basic_operations(framework: MetaLearningFramework) -> bool:
        """Test basic operations"""
        # Create a test task
        task = LearningTask(
            task_id="test_task_001",
            domain=TaskDomain.CLASSIFICATION,
            description="Test classification task",
            input_dim=10,
            output_dim=2,
            complexity=0.5,
            metadata={"test": True}
        )
        
        # Learn the task
        result = framework.learn_task(task)
        
        # Verify result
        assert "task_id" in result
        assert "strategy" in result
        assert "performance" in result
        assert 0.0 <= result["performance"] <= 1.0
        
        # Get insights
        insights = framework.get_meta_insights()
        assert insights["total_tasks_learned"] == 1
        
        return True


def demo():
    """Demonstrate meta-learning framework capabilities"""
    print("=== Meta-Learning Framework Demo ===\n")
    
    # Create framework
    framework = MetaLearningFramework(memory_capacity=100)
    
    # Create various tasks
    tasks = [
        LearningTask("task_001", TaskDomain.CLASSIFICATION, "Image classification", 784, 10, 0.6, {}),
        LearningTask("task_002", TaskDomain.REGRESSION, "Price prediction", 20, 1, 0.4, {}),
        LearningTask("task_003", TaskDomain.CLASSIFICATION, "Sentiment analysis", 512, 3, 0.5, {}),
        LearningTask("task_004", TaskDomain.OPTIMIZATION, "Route optimization", 50, 50, 0.7, {}),
        LearningTask("task_005", TaskDomain.CLASSIFICATION, "Object detection", 1024, 20, 0.8, {})
    ]
    
    # Learn each task
    print("Learning tasks...")
    for task in tasks:
        result = framework.learn_task(task)
        print(f"  {task.task_id}: strategy={result['strategy']}, performance={result['performance']:.3f}")
    
    # Get meta-insights
    print("\nMeta-Learning Insights:")
    insights = framework.get_meta_insights()
    print(f"  Total tasks learned: {insights['total_tasks_learned']}")
    print(f"  Average performance: {insights['avg_performance']:.3f}")
    print(f"  Transfer usage rate: {insights['transfer_usage_rate']:.3f}")
    
    # Strategy statistics
    print("\nStrategy Performance:")
    for strategy, stats in insights['strategy_stats'].items():
        print(f"  {strategy}: avg={stats['avg_performance']:.3f}, count={stats['count']}")
    
    print("\n✓ Meta-learning framework demo complete")


if __name__ == "__main__":
    demo()
