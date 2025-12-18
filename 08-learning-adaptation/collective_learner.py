#!/usr/bin/env python3
"""
Collective Learning Mechanisms - New Build 6, Phase 2
Federated learning integration, knowledge sharing protocols, and collective model improvement
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
from collections import defaultdict
import copy


class LearningMode(Enum):
    """Learning modes"""
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    REINFORCEMENT = "reinforcement"
    FEDERATED = "federated"
    TRANSFER = "transfer"


class AggregationStrategy(Enum):
    """Model aggregation strategies"""
    AVERAGE = "average"              # Simple averaging
    WEIGHTED = "weighted"            # Weighted by performance
    FEDAVG = "fedavg"               # Federated averaging
    FEDPROX = "fedprox"             # Federated proximal
    ADAPTIVE = "adaptive"            # Adaptive aggregation


@dataclass
class ModelUpdate:
    """Represents a model update from a learning node"""
    node_id: str
    update_id: str
    parameters: Dict[str, Any]  # Model parameters/weights
    performance: float  # Validation performance
    samples_used: int
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'node_id': self.node_id,
            'update_id': self.update_id,
            'parameters': self.parameters,
            'performance': self.performance,
            'samples_used': self.samples_used,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }
    
    def get_hash(self) -> str:
        """Generate hash for update verification"""
        content = f"{self.node_id}:{self.update_id}:{self.timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class KnowledgePacket:
    """Packet of knowledge to share between nodes"""
    packet_id: str
    source_node: str
    knowledge_type: str  # "pattern", "rule", "insight", etc.
    content: Dict[str, Any]
    confidence: float
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'packet_id': self.packet_id,
            'source_node': self.source_node,
            'knowledge_type': self.knowledge_type,
            'content': self.content,
            'confidence': self.confidence,
            'timestamp': self.timestamp
        }


class LearningNode:
    """Individual learning node in collective system"""
    
    def __init__(self, node_id: str, learning_mode: LearningMode = LearningMode.SUPERVISED):
        self.node_id = node_id
        self.learning_mode = learning_mode
        self.model_parameters: Dict[str, Any] = {}
        self.learning_history: List[Dict[str, Any]] = []
        self.knowledge_base: List[KnowledgePacket] = []
        self.performance_metrics: Dict[str, float] = {}
        
    def train(self, data: List[Any], labels: Optional[List[Any]] = None) -> ModelUpdate:
        """Train on local data"""
        # Simulate training
        update_id = f"update_{len(self.learning_history)}"
        
        # Simulate parameter updates
        new_params = {
            f"layer_{i}": {"weights": [0.1 * (i + 1)] * 10, "bias": 0.01}
            for i in range(3)
        }
        
        # Simulate performance improvement
        performance = 0.7 + (len(self.learning_history) * 0.05)
        performance = min(performance, 0.95)  # Cap at 95%
        
        self.model_parameters = new_params
        self.performance_metrics['accuracy'] = performance
        
        update = ModelUpdate(
            node_id=self.node_id,
            update_id=update_id,
            parameters=copy.deepcopy(new_params),
            performance=performance,
            samples_used=len(data)
        )
        
        self.learning_history.append({
            'update_id': update_id,
            'performance': performance,
            'samples': len(data),
            'timestamp': time.time()
        })
        
        return update
    
    def update_model(self, parameters: Dict[str, Any]) -> bool:
        """Update model with new parameters"""
        self.model_parameters = copy.deepcopy(parameters)
        return True
    
    def extract_knowledge(self) -> KnowledgePacket:
        """Extract learned knowledge to share"""
        packet_id = f"knowledge_{self.node_id}_{len(self.knowledge_base)}"
        
        # Extract patterns from learning history
        avg_performance = sum(
            h['performance'] for h in self.learning_history
        ) / len(self.learning_history) if self.learning_history else 0.0
        
        knowledge = KnowledgePacket(
            packet_id=packet_id,
            source_node=self.node_id,
            knowledge_type="pattern",
            content={
                'average_performance': avg_performance,
                'training_rounds': len(self.learning_history),
                'best_performance': max((h['performance'] for h in self.learning_history), default=0.0)
            },
            confidence=avg_performance
        )
        
        self.knowledge_base.append(knowledge)
        return knowledge
    
    def receive_knowledge(self, packet: KnowledgePacket) -> bool:
        """Receive and integrate knowledge from other nodes"""
        self.knowledge_base.append(packet)
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get node statistics"""
        return {
            'node_id': self.node_id,
            'learning_mode': self.learning_mode.value,
            'training_rounds': len(self.learning_history),
            'current_performance': self.performance_metrics.get('accuracy', 0.0),
            'knowledge_packets': len(self.knowledge_base)
        }


class ModelAggregator:
    """Aggregates model updates from multiple nodes"""
    
    def __init__(self, strategy: AggregationStrategy = AggregationStrategy.FEDAVG):
        self.strategy = strategy
        self.aggregation_history: List[Dict[str, Any]] = []
        
    def aggregate(self, updates: List[ModelUpdate]) -> Dict[str, Any]:
        """Aggregate model updates"""
        if not updates:
            return {}
        
        if self.strategy == AggregationStrategy.AVERAGE:
            return self._simple_average(updates)
        elif self.strategy == AggregationStrategy.WEIGHTED:
            return self._weighted_average(updates)
        elif self.strategy == AggregationStrategy.FEDAVG:
            return self._federated_average(updates)
        elif self.strategy == AggregationStrategy.FEDPROX:
            return self._federated_proximal(updates)
        else:
            return self._adaptive_aggregation(updates)
    
    def _simple_average(self, updates: List[ModelUpdate]) -> Dict[str, Any]:
        """Simple parameter averaging"""
        aggregated = {}
        
        # Get all parameter keys from first update
        if updates:
            param_keys = updates[0].parameters.keys()
            
            for key in param_keys:
                # Average each parameter
                values = [u.parameters[key] for u in updates]
                
                # Handle dict parameters
                if isinstance(values[0], dict):
                    aggregated[key] = {}
                    for sub_key in values[0].keys():
                        sub_values = [v[sub_key] for v in values]
                        if isinstance(sub_values[0], list):
                            # Average lists element-wise
                            aggregated[key][sub_key] = [
                                sum(sv[i] for sv in sub_values) / len(sub_values)
                                for i in range(len(sub_values[0]))
                            ]
                        else:
                            aggregated[key][sub_key] = sum(sub_values) / len(sub_values)
                else:
                    aggregated[key] = sum(values) / len(values)
        
        self.aggregation_history.append({
            'strategy': 'average',
            'num_updates': len(updates),
            'timestamp': time.time()
        })
        
        return aggregated
    
    def _weighted_average(self, updates: List[ModelUpdate]) -> Dict[str, Any]:
        """Weighted averaging by performance"""
        total_weight = sum(u.performance for u in updates)
        
        if total_weight == 0:
            return self._simple_average(updates)
        
        aggregated = {}
        
        if updates:
            param_keys = updates[0].parameters.keys()
            
            for key in param_keys:
                values = [u.parameters[key] for u in updates]
                weights = [u.performance / total_weight for u in updates]
                
                if isinstance(values[0], dict):
                    aggregated[key] = {}
                    for sub_key in values[0].keys():
                        sub_values = [v[sub_key] for v in values]
                        if isinstance(sub_values[0], list):
                            aggregated[key][sub_key] = [
                                sum(sv[i] * weights[j] for j, sv in enumerate(sub_values))
                                for i in range(len(sub_values[0]))
                            ]
                        else:
                            aggregated[key][sub_key] = sum(
                                sv * weights[j] for j, sv in enumerate(sub_values)
                            )
                else:
                    aggregated[key] = sum(v * weights[i] for i, v in enumerate(values))
        
        self.aggregation_history.append({
            'strategy': 'weighted',
            'num_updates': len(updates),
            'total_weight': total_weight,
            'timestamp': time.time()
        })
        
        return aggregated
    
    def _federated_average(self, updates: List[ModelUpdate]) -> Dict[str, Any]:
        """Federated averaging (FedAvg) - weighted by sample count"""
        total_samples = sum(u.samples_used for u in updates)
        
        if total_samples == 0:
            return self._simple_average(updates)
        
        aggregated = {}
        
        if updates:
            param_keys = updates[0].parameters.keys()
            
            for key in param_keys:
                values = [u.parameters[key] for u in updates]
                weights = [u.samples_used / total_samples for u in updates]
                
                if isinstance(values[0], dict):
                    aggregated[key] = {}
                    for sub_key in values[0].keys():
                        sub_values = [v[sub_key] for v in values]
                        if isinstance(sub_values[0], list):
                            aggregated[key][sub_key] = [
                                sum(sv[i] * weights[j] for j, sv in enumerate(sub_values))
                                for i in range(len(sub_values[0]))
                            ]
                        else:
                            aggregated[key][sub_key] = sum(
                                sv * weights[j] for j, sv in enumerate(sub_values)
                            )
                else:
                    aggregated[key] = sum(v * weights[i] for i, v in enumerate(values))
        
        self.aggregation_history.append({
            'strategy': 'fedavg',
            'num_updates': len(updates),
            'total_samples': total_samples,
            'timestamp': time.time()
        })
        
        return aggregated
    
    def _federated_proximal(self, updates: List[ModelUpdate]) -> Dict[str, Any]:
        """Federated proximal (FedProx) - similar to FedAvg with regularization"""
        # For simplicity, use FedAvg (full FedProx requires global model)
        return self._federated_average(updates)
    
    def _adaptive_aggregation(self, updates: List[ModelUpdate]) -> Dict[str, Any]:
        """Adaptive aggregation based on update quality"""
        # Use weighted average by performance
        return self._weighted_average(updates)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get aggregation statistics"""
        return {
            'strategy': self.strategy.value,
            'total_aggregations': len(self.aggregation_history)
        }


class KnowledgeSharingProtocol:
    """Protocol for sharing knowledge between nodes"""
    
    def __init__(self):
        self.shared_knowledge: List[KnowledgePacket] = []
        self.sharing_history: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        
    def share(self, packet: KnowledgePacket) -> bool:
        """Share knowledge packet"""
        with self.lock:
            self.shared_knowledge.append(packet)
            self.sharing_history.append({
                'packet_id': packet.packet_id,
                'source': packet.source_node,
                'type': packet.knowledge_type,
                'timestamp': time.time()
            })
            return True
    
    def retrieve(self, knowledge_type: Optional[str] = None, min_confidence: float = 0.0) -> List[KnowledgePacket]:
        """Retrieve knowledge packets"""
        with self.lock:
            results = []
            for packet in self.shared_knowledge:
                if knowledge_type and packet.knowledge_type != knowledge_type:
                    continue
                if packet.confidence < min_confidence:
                    continue
                results.append(packet)
            return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get sharing statistics"""
        with self.lock:
            type_counts = defaultdict(int)
            for packet in self.shared_knowledge:
                type_counts[packet.knowledge_type] += 1
            
            return {
                'total_packets': len(self.shared_knowledge),
                'type_counts': dict(type_counts),
                'sharing_events': len(self.sharing_history)
            }


class CollectiveLearner:
    """Main collective learning system"""
    
    def __init__(self, num_nodes: int = 4, aggregation_strategy: AggregationStrategy = AggregationStrategy.FEDAVG):
        self.num_nodes = num_nodes
        self.nodes = [LearningNode(f"node_{i}") for i in range(num_nodes)]
        self.aggregator = ModelAggregator(aggregation_strategy)
        self.knowledge_protocol = KnowledgeSharingProtocol()
        self.global_model: Dict[str, Any] = {}
        self.training_rounds: int = 0
        
    def train_round(self, data_per_node: List[List[Any]], labels_per_node: Optional[List[List[Any]]] = None) -> Dict[str, Any]:
        """Execute one round of collective training"""
        updates = []
        
        # Each node trains on local data
        for i, node in enumerate(self.nodes):
            if i < len(data_per_node):
                labels = labels_per_node[i] if labels_per_node else None
                update = node.train(data_per_node[i], labels)
                updates.append(update)
        
        # Aggregate updates
        self.global_model = self.aggregator.aggregate(updates)
        
        # Distribute global model to all nodes
        for node in self.nodes:
            node.update_model(self.global_model)
        
        self.training_rounds += 1
        
        # Calculate average performance
        avg_performance = sum(u.performance for u in updates) / len(updates) if updates else 0.0
        
        return {
            'round': self.training_rounds,
            'num_updates': len(updates),
            'average_performance': avg_performance,
            'global_model_size': len(self.global_model)
        }
    
    def share_knowledge(self) -> int:
        """Nodes share learned knowledge"""
        shared_count = 0
        
        for node in self.nodes:
            knowledge = node.extract_knowledge()
            self.knowledge_protocol.share(knowledge)
            shared_count += 1
        
        # Distribute knowledge to all nodes
        all_knowledge = self.knowledge_protocol.retrieve()
        for node in self.nodes:
            for packet in all_knowledge:
                if packet.source_node != node.node_id:
                    node.receive_knowledge(packet)
        
        return shared_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        node_stats = [node.get_stats() for node in self.nodes]
        
        avg_performance = sum(
            s['current_performance'] for s in node_stats
        ) / len(node_stats) if node_stats else 0.0
        
        return {
            'num_nodes': self.num_nodes,
            'training_rounds': self.training_rounds,
            'average_performance': avg_performance,
            'aggregator': self.aggregator.get_stats(),
            'knowledge_sharing': self.knowledge_protocol.get_stats(),
            'nodes': node_stats
        }
    
    def demo(self) -> Dict[str, Any]:
        """Demonstrate collective learning capabilities"""
        print("\n=== Collective Learning Mechanisms Demo ===")
        
        # 1. Initial training round
        print("\n1. First training round...")
        data_per_node = [[f"sample_{i}_{j}" for j in range(10)] for i in range(self.num_nodes)]
        result1 = self.train_round(data_per_node)
        print(f"   Round {result1['round']}: Avg performance = {result1['average_performance']:.2f}")
        
        # 2. Second training round
        print("\n2. Second training round...")
        result2 = self.train_round(data_per_node)
        print(f"   Round {result2['round']}: Avg performance = {result2['average_performance']:.2f}")
        print(f"   Improvement: {result2['average_performance'] - result1['average_performance']:.2f}")
        
        # 3. Knowledge sharing
        print("\n3. Sharing knowledge between nodes...")
        shared = self.share_knowledge()
        print(f"   Shared {shared} knowledge packets")
        
        # 4. Third training round after knowledge sharing
        print("\n4. Training after knowledge sharing...")
        result3 = self.train_round(data_per_node)
        print(f"   Round {result3['round']}: Avg performance = {result3['average_performance']:.2f}")
        
        # 5. Get statistics
        print("\n5. System statistics:")
        stats = self.get_stats()
        print(f"   Total training rounds: {stats['training_rounds']}")
        print(f"   Average performance: {stats['average_performance']:.2f}")
        print(f"   Knowledge packets shared: {stats['knowledge_sharing']['total_packets']}")
        print(f"   Aggregation strategy: {stats['aggregator']['strategy']}")
        
        print("\n=== Demo Complete ===")
        return stats


class CollectiveLearnerContract:
    """Contract interface for testing"""
    
    @staticmethod
    def create() -> CollectiveLearner:
        """Create a collective learner instance"""
        return CollectiveLearner()
    
    @staticmethod
    def verify() -> bool:
        """Verify collective learner functionality"""
        cl = CollectiveLearner(num_nodes=2)
        
        # Test training round
        data = [["sample_1", "sample_2"] for _ in range(2)]
        result = cl.train_round(data)
        if result['num_updates'] != 2:
            return False
        
        # Test knowledge sharing
        shared = cl.share_knowledge()
        if shared != 2:
            return False
        
        # Test statistics
        stats = cl.get_stats()
        if stats['training_rounds'] != 1:
            return False
        
        return True


if __name__ == "__main__":
    # Run demo
    cl = CollectiveLearner()
    cl.demo()
