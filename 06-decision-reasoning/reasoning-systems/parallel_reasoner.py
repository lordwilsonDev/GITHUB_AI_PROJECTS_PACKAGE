#!/usr/bin/env python3
"""
Parallel Reasoning Framework - New Build 6, Phase 2
Multi-node reasoning, distributed inference, and result aggregation
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import hashlib
from collections import defaultdict


class ReasoningType(Enum):
    """Types of reasoning"""
    DEDUCTIVE = "deductive"      # From general to specific
    INDUCTIVE = "inductive"      # From specific to general
    ABDUCTIVE = "abductive"      # Best explanation
    ANALOGICAL = "analogical"    # By analogy
    CAUSAL = "causal"           # Cause and effect


class InferenceStrategy(Enum):
    """Inference execution strategies"""
    SEQUENTIAL = "sequential"    # One at a time
    PARALLEL = "parallel"        # All at once
    PIPELINE = "pipeline"        # Staged execution
    ADAPTIVE = "adaptive"        # Choose based on load


@dataclass
class ReasoningTask:
    """Represents a reasoning task"""
    task_id: str
    reasoning_type: ReasoningType
    premises: List[str]
    goal: str
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'task_id': self.task_id,
            'reasoning_type': self.reasoning_type.value,
            'premises': self.premises,
            'goal': self.goal,
            'context': self.context,
            'priority': self.priority
        }


@dataclass
class InferenceResult:
    """Result of an inference operation"""
    task_id: str
    conclusion: str
    confidence: float  # 0.0 to 1.0
    reasoning_chain: List[str] = field(default_factory=list)
    node_id: str = "default"
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'task_id': self.task_id,
            'conclusion': self.conclusion,
            'confidence': self.confidence,
            'reasoning_chain': self.reasoning_chain,
            'node_id': self.node_id,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }


class ReasoningEngine:
    """Single-node reasoning engine"""
    
    def __init__(self, node_id: str = "node_0"):
        self.node_id = node_id
        self.reasoning_history: List[InferenceResult] = []
        
    def reason(self, task: ReasoningTask) -> InferenceResult:
        """Perform reasoning on a task"""
        # Simulate reasoning based on type
        if task.reasoning_type == ReasoningType.DEDUCTIVE:
            return self._deductive_reasoning(task)
        elif task.reasoning_type == ReasoningType.INDUCTIVE:
            return self._inductive_reasoning(task)
        elif task.reasoning_type == ReasoningType.ABDUCTIVE:
            return self._abductive_reasoning(task)
        elif task.reasoning_type == ReasoningType.ANALOGICAL:
            return self._analogical_reasoning(task)
        elif task.reasoning_type == ReasoningType.CAUSAL:
            return self._causal_reasoning(task)
        else:
            return InferenceResult(
                task_id=task.task_id,
                conclusion="Unknown reasoning type",
                confidence=0.0,
                node_id=self.node_id
            )
    
    def _deductive_reasoning(self, task: ReasoningTask) -> InferenceResult:
        """Deductive reasoning: general to specific"""
        reasoning_chain = [
            f"Given premises: {', '.join(task.premises)}",
            f"Applying deductive logic",
            f"Deriving conclusion for: {task.goal}"
        ]
        
        # Simple deductive inference
        conclusion = f"Deductive conclusion: {task.goal} follows from premises"
        confidence = 0.9 if len(task.premises) >= 2 else 0.7
        
        result = InferenceResult(
            task_id=task.task_id,
            conclusion=conclusion,
            confidence=confidence,
            reasoning_chain=reasoning_chain,
            node_id=self.node_id
        )
        
        self.reasoning_history.append(result)
        return result
    
    def _inductive_reasoning(self, task: ReasoningTask) -> InferenceResult:
        """Inductive reasoning: specific to general"""
        reasoning_chain = [
            f"Observing specific cases: {', '.join(task.premises)}",
            f"Identifying patterns",
            f"Generalizing to: {task.goal}"
        ]
        
        conclusion = f"Inductive generalization: {task.goal} likely holds"
        confidence = min(0.8, 0.5 + (len(task.premises) * 0.1))
        
        result = InferenceResult(
            task_id=task.task_id,
            conclusion=conclusion,
            confidence=confidence,
            reasoning_chain=reasoning_chain,
            node_id=self.node_id
        )
        
        self.reasoning_history.append(result)
        return result
    
    def _abductive_reasoning(self, task: ReasoningTask) -> InferenceResult:
        """Abductive reasoning: best explanation"""
        reasoning_chain = [
            f"Observations: {', '.join(task.premises)}",
            f"Seeking best explanation",
            f"Hypothesis: {task.goal}"
        ]
        
        conclusion = f"Best explanation: {task.goal}"
        confidence = 0.75
        
        result = InferenceResult(
            task_id=task.task_id,
            conclusion=conclusion,
            confidence=confidence,
            reasoning_chain=reasoning_chain,
            node_id=self.node_id
        )
        
        self.reasoning_history.append(result)
        return result
    
    def _analogical_reasoning(self, task: ReasoningTask) -> InferenceResult:
        """Analogical reasoning: by similarity"""
        reasoning_chain = [
            f"Source domain: {task.premises[0] if task.premises else 'unknown'}",
            f"Mapping to target domain",
            f"Analogical inference: {task.goal}"
        ]
        
        conclusion = f"By analogy: {task.goal}"
        confidence = 0.7
        
        result = InferenceResult(
            task_id=task.task_id,
            conclusion=conclusion,
            confidence=confidence,
            reasoning_chain=reasoning_chain,
            node_id=self.node_id
        )
        
        self.reasoning_history.append(result)
        return result
    
    def _causal_reasoning(self, task: ReasoningTask) -> InferenceResult:
        """Causal reasoning: cause and effect"""
        reasoning_chain = [
            f"Causes: {', '.join(task.premises)}",
            f"Analyzing causal relationships",
            f"Effect: {task.goal}"
        ]
        
        conclusion = f"Causal inference: {task.goal} is caused by premises"
        confidence = 0.85
        
        result = InferenceResult(
            task_id=task.task_id,
            conclusion=conclusion,
            confidence=confidence,
            reasoning_chain=reasoning_chain,
            node_id=self.node_id
        )
        
        self.reasoning_history.append(result)
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get reasoning statistics"""
        type_counts = defaultdict(int)
        total_confidence = 0.0
        
        for result in self.reasoning_history:
            total_confidence += result.confidence
        
        avg_confidence = total_confidence / len(self.reasoning_history) if self.reasoning_history else 0.0
        
        return {
            'node_id': self.node_id,
            'total_inferences': len(self.reasoning_history),
            'average_confidence': avg_confidence
        }


class ResultAggregator:
    """Aggregates results from multiple reasoning nodes"""
    
    def __init__(self):
        self.aggregation_history: List[Dict[str, Any]] = []
        
    def aggregate(self, results: List[InferenceResult], method: str = "weighted_vote") -> InferenceResult:
        """Aggregate multiple inference results"""
        if not results:
            return InferenceResult(
                task_id="unknown",
                conclusion="No results to aggregate",
                confidence=0.0
            )
        
        if method == "weighted_vote":
            return self._weighted_vote(results)
        elif method == "max_confidence":
            return self._max_confidence(results)
        elif method == "consensus":
            return self._consensus(results)
        else:
            return results[0]  # Default to first result
    
    def _weighted_vote(self, results: List[InferenceResult]) -> InferenceResult:
        """Aggregate by weighted voting based on confidence"""
        # Group by conclusion
        conclusion_weights = defaultdict(float)
        conclusion_chains = defaultdict(list)
        
        for result in results:
            conclusion_weights[result.conclusion] += result.confidence
            conclusion_chains[result.conclusion].extend(result.reasoning_chain)
        
        # Find conclusion with highest weight
        best_conclusion = max(conclusion_weights.items(), key=lambda x: x[1])
        
        # Calculate aggregated confidence
        total_weight = sum(conclusion_weights.values())
        aggregated_confidence = best_conclusion[1] / total_weight if total_weight > 0 else 0.0
        
        aggregated_result = InferenceResult(
            task_id=results[0].task_id,
            conclusion=best_conclusion[0],
            confidence=aggregated_confidence,
            reasoning_chain=conclusion_chains[best_conclusion[0]],
            node_id="aggregator",
            metadata={
                'method': 'weighted_vote',
                'num_results': len(results),
                'total_weight': total_weight
            }
        )
        
        self.aggregation_history.append(aggregated_result.to_dict())
        return aggregated_result
    
    def _max_confidence(self, results: List[InferenceResult]) -> InferenceResult:
        """Select result with maximum confidence"""
        best_result = max(results, key=lambda r: r.confidence)
        best_result.metadata['method'] = 'max_confidence'
        best_result.metadata['num_results'] = len(results)
        
        self.aggregation_history.append(best_result.to_dict())
        return best_result
    
    def _consensus(self, results: List[InferenceResult]) -> InferenceResult:
        """Require consensus among results"""
        # Count conclusions
        conclusion_counts = defaultdict(int)
        for result in results:
            conclusion_counts[result.conclusion] += 1
        
        # Check for majority
        majority_threshold = len(results) / 2
        consensus_conclusion = None
        
        for conclusion, count in conclusion_counts.items():
            if count > majority_threshold:
                consensus_conclusion = conclusion
                break
        
        if consensus_conclusion:
            # Find results with consensus conclusion
            consensus_results = [r for r in results if r.conclusion == consensus_conclusion]
            avg_confidence = sum(r.confidence for r in consensus_results) / len(consensus_results)
            
            aggregated_result = InferenceResult(
                task_id=results[0].task_id,
                conclusion=consensus_conclusion,
                confidence=avg_confidence,
                reasoning_chain=["Consensus reached"],
                node_id="aggregator",
                metadata={
                    'method': 'consensus',
                    'num_results': len(results),
                    'consensus_count': len(consensus_results)
                }
            )
        else:
            # No consensus - use weighted vote
            aggregated_result = self._weighted_vote(results)
            aggregated_result.metadata['consensus_failed'] = True
        
        self.aggregation_history.append(aggregated_result.to_dict())
        return aggregated_result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get aggregation statistics"""
        return {
            'total_aggregations': len(self.aggregation_history)
        }


class ParallelReasoner:
    """Main parallel reasoning framework"""
    
    def __init__(self, num_nodes: int = 4, strategy: InferenceStrategy = InferenceStrategy.PARALLEL):
        self.num_nodes = num_nodes
        self.strategy = strategy
        self.engines = [ReasoningEngine(f"node_{i}") for i in range(num_nodes)]
        self.aggregator = ResultAggregator()
        self.executor = ThreadPoolExecutor(max_workers=num_nodes)
        
    def infer(self, task: ReasoningTask, num_nodes: Optional[int] = None) -> InferenceResult:
        """Perform distributed inference"""
        nodes_to_use = num_nodes or self.num_nodes
        
        if self.strategy == InferenceStrategy.SEQUENTIAL:
            return self._sequential_inference(task, nodes_to_use)
        elif self.strategy == InferenceStrategy.PARALLEL:
            return self._parallel_inference(task, nodes_to_use)
        elif self.strategy == InferenceStrategy.PIPELINE:
            return self._pipeline_inference(task, nodes_to_use)
        else:
            return self._adaptive_inference(task, nodes_to_use)
    
    def _sequential_inference(self, task: ReasoningTask, num_nodes: int) -> InferenceResult:
        """Sequential inference across nodes"""
        results = []
        for i in range(min(num_nodes, len(self.engines))):
            result = self.engines[i].reason(task)
            results.append(result)
        
        return self.aggregator.aggregate(results)
    
    def _parallel_inference(self, task: ReasoningTask, num_nodes: int) -> InferenceResult:
        """Parallel inference across nodes"""
        futures = []
        for i in range(min(num_nodes, len(self.engines))):
            future = self.executor.submit(self.engines[i].reason, task)
            futures.append(future)
        
        results = [future.result() for future in as_completed(futures)]
        return self.aggregator.aggregate(results)
    
    def _pipeline_inference(self, task: ReasoningTask, num_nodes: int) -> InferenceResult:
        """Pipeline inference - each node refines previous result"""
        current_task = task
        results = []
        
        for i in range(min(num_nodes, len(self.engines))):
            result = self.engines[i].reason(current_task)
            results.append(result)
            
            # Update task with refined conclusion
            current_task = ReasoningTask(
                task_id=f"{task.task_id}_refined_{i}",
                reasoning_type=task.reasoning_type,
                premises=task.premises + [result.conclusion],
                goal=task.goal,
                context=task.context
            )
        
        # Return the final refined result
        return results[-1] if results else InferenceResult(
            task_id=task.task_id,
            conclusion="Pipeline failed",
            confidence=0.0
        )
    
    def _adaptive_inference(self, task: ReasoningTask, num_nodes: int) -> InferenceResult:
        """Adaptive inference - choose strategy based on task"""
        # Simple heuristic: use parallel for high priority, sequential otherwise
        if task.priority > 5:
            return self._parallel_inference(task, num_nodes)
        else:
            return self._sequential_inference(task, num_nodes)
    
    def batch_infer(self, tasks: List[ReasoningTask]) -> List[InferenceResult]:
        """Perform inference on multiple tasks"""
        futures = []
        for task in tasks:
            future = self.executor.submit(self.infer, task)
            futures.append(future)
        
        return [future.result() for future in as_completed(futures)]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        engine_stats = [engine.get_stats() for engine in self.engines]
        
        total_inferences = sum(s['total_inferences'] for s in engine_stats)
        avg_confidence = sum(s['average_confidence'] for s in engine_stats) / len(engine_stats) if engine_stats else 0.0
        
        return {
            'num_nodes': self.num_nodes,
            'strategy': self.strategy.value,
            'total_inferences': total_inferences,
            'average_confidence': avg_confidence,
            'aggregator': self.aggregator.get_stats(),
            'engines': engine_stats
        }
    
    def demo(self) -> Dict[str, Any]:
        """Demonstrate parallel reasoning capabilities"""
        print("\n=== Parallel Reasoning Framework Demo ===")
        
        # 1. Single task inference
        print("\n1. Single task parallel inference...")
        task1 = ReasoningTask(
            task_id="task_1",
            reasoning_type=ReasoningType.DEDUCTIVE,
            premises=["All humans are mortal", "Socrates is human"],
            goal="Socrates is mortal"
        )
        result1 = self.infer(task1)
        print(f"   Conclusion: {result1.conclusion}")
        print(f"   Confidence: {result1.confidence:.2f}")
        print(f"   Nodes used: {self.num_nodes}")
        
        # 2. Different reasoning types
        print("\n2. Testing different reasoning types...")
        task2 = ReasoningTask(
            task_id="task_2",
            reasoning_type=ReasoningType.INDUCTIVE,
            premises=["Swan 1 is white", "Swan 2 is white", "Swan 3 is white"],
            goal="All swans are white"
        )
        result2 = self.infer(task2)
        print(f"   Inductive conclusion: {result2.conclusion}")
        print(f"   Confidence: {result2.confidence:.2f}")
        
        # 3. Batch inference
        print("\n3. Batch inference on multiple tasks...")
        tasks = [
            ReasoningTask(f"batch_{i}", ReasoningType.ABDUCTIVE, [f"Observation {i}"], f"Explanation {i}")
            for i in range(5)
        ]
        batch_results = self.batch_infer(tasks)
        print(f"   Processed {len(batch_results)} tasks")
        print(f"   Average confidence: {sum(r.confidence for r in batch_results) / len(batch_results):.2f}")
        
        # 4. Get statistics
        print("\n4. System statistics:")
        stats = self.get_stats()
        print(f"   Total inferences: {stats['total_inferences']}")
        print(f"   Average confidence: {stats['average_confidence']:.2f}")
        print(f"   Strategy: {stats['strategy']}")
        print(f"   Aggregations: {stats['aggregator']['total_aggregations']}")
        
        print("\n=== Demo Complete ===")
        return stats
    
    def shutdown(self):
        """Shutdown the executor"""
        self.executor.shutdown(wait=True)


class ParallelReasonerContract:
    """Contract interface for testing"""
    
    @staticmethod
    def create() -> ParallelReasoner:
        """Create a parallel reasoner instance"""
        return ParallelReasoner()
    
    @staticmethod
    def verify() -> bool:
        """Verify parallel reasoner functionality"""
        pr = ParallelReasoner(num_nodes=2)
        
        # Test single inference
        task = ReasoningTask(
            task_id="test_1",
            reasoning_type=ReasoningType.DEDUCTIVE,
            premises=["A", "B"],
            goal="C"
        )
        result = pr.infer(task)
        if result.confidence <= 0.0:
            pr.shutdown()
            return False
        
        # Test batch inference
        tasks = [
            ReasoningTask(f"test_{i}", ReasoningType.INDUCTIVE, ["X"], "Y")
            for i in range(3)
        ]
        results = pr.batch_infer(tasks)
        if len(results) != 3:
            pr.shutdown()
            return False
        
        # Test statistics
        stats = pr.get_stats()
        if stats['total_inferences'] <= 0:
            pr.shutdown()
            return False
        
        pr.shutdown()
        return True


if __name__ == "__main__":
    # Run demo
    pr = ParallelReasoner()
    pr.demo()
    pr.shutdown()
