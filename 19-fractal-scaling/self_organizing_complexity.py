#!/usr/bin/env python3
"""
Self-Organizing Complexity Engine - New Build 12 (T-093)
Autonomous complexity growth with edge-of-chaos optimization.
Maintains criticality for optimal adaptability and emergent behavior.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from collections import defaultdict, deque


class ComplexityRegime(Enum):
    """System complexity regimes."""
    ORDERED = "ordered"  # Too simple, predictable
    CRITICAL = "critical"  # Edge of chaos, optimal
    CHAOTIC = "chaotic"  # Too complex, unpredictable


class SelfOrganizationMode(Enum):
    """Self-organization modes."""
    GROWTH = "growth"  # Increasing complexity
    PRUNING = "pruning"  # Reducing complexity
    STABILIZATION = "stabilization"  # Maintaining criticality
    EXPLORATION = "exploration"  # Searching for new patterns


@dataclass
class ComplexityMetrics:
    """Metrics for measuring system complexity."""
    entropy: float  # Information entropy
    connectivity: float  # Network connectivity
    modularity: float  # Modular organization
    hierarchy: float  # Hierarchical depth
    adaptability: float  # Rate of adaptation
    criticality: float  # Distance from critical point
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'entropy': float(self.entropy),
            'connectivity': float(self.connectivity),
            'modularity': float(self.modularity),
            'hierarchy': float(self.hierarchy),
            'adaptability': float(self.adaptability),
            'criticality': float(self.criticality),
            'timestamp': self.timestamp
        }


@dataclass
class ComplexityNode:
    """Node in the complexity network."""
    node_id: str
    activation: float = 0.0
    connections: Set[str] = field(default_factory=set)
    weight_sum: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_connection(self, target_id: str, weight: float = 1.0):
        """Add connection to another node."""
        self.connections.add(target_id)
        self.weight_sum += weight
    
    def remove_connection(self, target_id: str, weight: float = 1.0):
        """Remove connection to another node."""
        if target_id in self.connections:
            self.connections.remove(target_id)
            self.weight_sum -= weight


class SelfOrganizingComplexity:
    """
    Self-organizing complexity engine with autonomous growth and criticality maintenance.
    
    Features:
    - Autonomous complexity growth
    - Edge-of-chaos optimization
    - Criticality maintenance
    - Adaptive network topology
    - Emergent pattern formation
    """
    
    def __init__(
        self,
        target_criticality: float = 0.5,
        criticality_tolerance: float = 0.1,
        growth_rate: float = 0.1,
        pruning_threshold: float = 0.01
    ):
        self.nodes: Dict[str, ComplexityNode] = {}
        self.edges: Dict[Tuple[str, str], float] = {}  # (source, target) -> weight
        self.target_criticality = target_criticality
        self.criticality_tolerance = criticality_tolerance
        self.growth_rate = growth_rate
        self.pruning_threshold = pruning_threshold
        
        self.current_mode = SelfOrganizationMode.STABILIZATION
        self.metrics_history: List[ComplexityMetrics] = []
        self.organization_events: List[Dict[str, Any]] = []
        
        # Criticality parameters
        self.critical_exponent = 2.0  # Power-law exponent
        self.correlation_length = 10.0  # Spatial correlation
        
    def add_node(self, node_id: str, metadata: Optional[Dict[str, Any]] = None) -> ComplexityNode:
        """Add a new node to the complexity network."""
        if node_id in self.nodes:
            return self.nodes[node_id]
        
        node = ComplexityNode(
            node_id=node_id,
            activation=np.random.random(),
            metadata=metadata or {}
        )
        self.nodes[node_id] = node
        
        # Record organization event
        self.organization_events.append({
            'type': 'node_added',
            'node_id': node_id,
            'timestamp': time.time()
        })
        
        return node
    
    def add_edge(
        self,
        source_id: str,
        target_id: str,
        weight: float = 1.0
    ) -> bool:
        """Add an edge between nodes."""
        if source_id not in self.nodes or target_id not in self.nodes:
            return False
        
        edge_key = (source_id, target_id)
        self.edges[edge_key] = weight
        
        # Update node connections
        self.nodes[source_id].add_connection(target_id, weight)
        
        # Record event
        self.organization_events.append({
            'type': 'edge_added',
            'source': source_id,
            'target': target_id,
            'weight': weight,
            'timestamp': time.time()
        })
        
        return True
    
    def remove_edge(self, source_id: str, target_id: str) -> bool:
        """Remove an edge between nodes."""
        edge_key = (source_id, target_id)
        if edge_key not in self.edges:
            return False
        
        weight = self.edges[edge_key]
        del self.edges[edge_key]
        
        # Update node connections
        if source_id in self.nodes:
            self.nodes[source_id].remove_connection(target_id, weight)
        
        # Record event
        self.organization_events.append({
            'type': 'edge_removed',
            'source': source_id,
            'target': target_id,
            'timestamp': time.time()
        })
        
        return True
    
    def calculate_metrics(self) -> ComplexityMetrics:
        """Calculate current complexity metrics."""
        if not self.nodes:
            return ComplexityMetrics(
                entropy=0.0,
                connectivity=0.0,
                modularity=0.0,
                hierarchy=0.0,
                adaptability=0.0,
                criticality=0.0
            )
        
        # Entropy: activation distribution
        activations = np.array([n.activation for n in self.nodes.values()])
        activations = activations / (np.sum(activations) + 1e-10)
        entropy = -np.sum(activations * np.log2(activations + 1e-10))
        
        # Connectivity: average degree
        degrees = [len(n.connections) for n in self.nodes.values()]
        connectivity = np.mean(degrees) if degrees else 0.0
        
        # Modularity: clustering coefficient approximation
        modularity = self._calculate_modularity()
        
        # Hierarchy: depth of longest path
        hierarchy = self._calculate_hierarchy()
        
        # Adaptability: recent change rate
        adaptability = self._calculate_adaptability()
        
        # Criticality: distance from critical point
        criticality = self._calculate_criticality()
        
        metrics = ComplexityMetrics(
            entropy=entropy,
            connectivity=connectivity,
            modularity=modularity,
            hierarchy=hierarchy,
            adaptability=adaptability,
            criticality=criticality
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    def _calculate_modularity(self) -> float:
        """Calculate network modularity (simplified)."""
        if not self.edges:
            return 0.0
        
        # Simple clustering coefficient
        total_clustering = 0.0
        for node in self.nodes.values():
            if len(node.connections) < 2:
                continue
            
            # Count triangles
            neighbors = list(node.connections)
            triangles = 0
            for i, n1 in enumerate(neighbors):
                for n2 in neighbors[i+1:]:
                    if (n1, n2) in self.edges or (n2, n1) in self.edges:
                        triangles += 1
            
            # Clustering coefficient for this node
            k = len(neighbors)
            possible_triangles = k * (k - 1) / 2
            if possible_triangles > 0:
                total_clustering += triangles / possible_triangles
        
        return total_clustering / len(self.nodes) if self.nodes else 0.0
    
    def _calculate_hierarchy(self) -> float:
        """Calculate hierarchical depth."""
        if not self.nodes:
            return 0.0
        
        # BFS to find maximum depth
        max_depth = 0
        for start_node in self.nodes:
            visited = {start_node}
            queue = deque([(start_node, 0)])
            
            while queue:
                node_id, depth = queue.popleft()
                max_depth = max(max_depth, depth)
                
                if node_id in self.nodes:
                    for neighbor in self.nodes[node_id].connections:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append((neighbor, depth + 1))
        
        return float(max_depth)
    
    def _calculate_adaptability(self) -> float:
        """Calculate recent adaptation rate."""
        if len(self.organization_events) < 2:
            return 0.0
        
        # Count recent events (last 10)
        recent_events = self.organization_events[-10:]
        time_span = recent_events[-1]['timestamp'] - recent_events[0]['timestamp']
        
        if time_span == 0:
            return 0.0
        
        return len(recent_events) / time_span
    
    def _calculate_criticality(self) -> float:
        """Calculate criticality measure (0 = critical, 1 = far from critical)."""
        if not self.nodes:
            return 1.0
        
        # Use connectivity distribution as criticality indicator
        degrees = [len(n.connections) for n in self.nodes.values()]
        if not degrees:
            return 1.0
        
        # Power-law fit quality (simplified)
        degree_counts = defaultdict(int)
        for d in degrees:
            degree_counts[d] += 1
        
        if len(degree_counts) < 2:
            return 1.0
        
        # Calculate variance in log-log space (power-law indicator)
        x = np.array(list(degree_counts.keys()))
        y = np.array(list(degree_counts.values()))
        
        log_x = np.log(x + 1)
        log_y = np.log(y + 1)
        
        # Linear fit in log-log space
        if len(log_x) > 1:
            slope, _ = np.polyfit(log_x, log_y, 1)
            # Critical systems have slope around -2 to -3
            criticality_score = abs(slope + self.critical_exponent) / self.critical_exponent
            return min(criticality_score, 1.0)
        
        return 1.0
    
    def self_organize(self, iterations: int = 1) -> List[ComplexityMetrics]:
        """
        Perform self-organization to maintain criticality.
        
        Returns:
            List of metrics after each iteration
        """
        iteration_metrics = []
        
        for _ in range(iterations):
            # Calculate current state
            metrics = self.calculate_metrics()
            iteration_metrics.append(metrics)
            
            # Determine regime
            regime = self._determine_regime(metrics)
            
            # Select organization mode
            self.current_mode = self._select_mode(metrics, regime)
            
            # Execute organization step
            if self.current_mode == SelfOrganizationMode.GROWTH:
                self._grow_complexity()
            elif self.current_mode == SelfOrganizationMode.PRUNING:
                self._prune_complexity()
            elif self.current_mode == SelfOrganizationMode.EXPLORATION:
                self._explore_patterns()
            else:  # STABILIZATION
                self._stabilize_criticality()
            
            # Update activations
            self._update_activations()
        
        return iteration_metrics
    
    def _determine_regime(self, metrics: ComplexityMetrics) -> ComplexityRegime:
        """Determine current complexity regime."""
        if metrics.criticality < self.target_criticality - self.criticality_tolerance:
            return ComplexityRegime.ORDERED
        elif metrics.criticality > self.target_criticality + self.criticality_tolerance:
            return ComplexityRegime.CHAOTIC
        else:
            return ComplexityRegime.CRITICAL
    
    def _select_mode(self, metrics: ComplexityMetrics, regime: ComplexityRegime) -> SelfOrganizationMode:
        """Select self-organization mode based on current state."""
        if regime == ComplexityRegime.ORDERED:
            # Too simple, need to grow
            return SelfOrganizationMode.GROWTH
        elif regime == ComplexityRegime.CHAOTIC:
            # Too complex, need to prune
            return SelfOrganizationMode.PRUNING
        else:
            # At criticality, explore or stabilize
            if np.random.random() < 0.3:  # 30% exploration
                return SelfOrganizationMode.EXPLORATION
            else:
                return SelfOrganizationMode.STABILIZATION
    
    def _grow_complexity(self):
        """Grow network complexity."""
        # Add new nodes
        n_new_nodes = max(1, int(len(self.nodes) * self.growth_rate))
        for i in range(n_new_nodes):
            new_id = f"node_{len(self.nodes)}_{i}"
            self.add_node(new_id)
            
            # Connect to existing nodes (preferential attachment)
            if self.nodes:
                # Select nodes with probability proportional to degree
                degrees = {nid: len(n.connections) + 1 for nid, n in self.nodes.items() if nid != new_id}
                if degrees:
                    total_degree = sum(degrees.values())
                    probs = {nid: d/total_degree for nid, d in degrees.items()}
                    
                    # Add 1-3 connections
                    n_connections = np.random.randint(1, 4)
                    targets = np.random.choice(
                        list(probs.keys()),
                        size=min(n_connections, len(probs)),
                        replace=False,
                        p=list(probs.values())
                    )
                    
                    for target in targets:
                        self.add_edge(new_id, target)
    
    def _prune_complexity(self):
        """Prune network complexity."""
        # Remove weak edges
        edges_to_remove = []
        for edge_key, weight in self.edges.items():
            if weight < self.pruning_threshold:
                edges_to_remove.append(edge_key)
        
        for source, target in edges_to_remove:
            self.remove_edge(source, target)
        
        # Remove isolated nodes
        nodes_to_remove = []
        for node_id, node in self.nodes.items():
            if len(node.connections) == 0:
                # Check if any edges point to this node
                has_incoming = any(target == node_id for _, target in self.edges.keys())
                if not has_incoming:
                    nodes_to_remove.append(node_id)
        
        for node_id in nodes_to_remove:
            del self.nodes[node_id]
    
    def _explore_patterns(self):
        """Explore new organizational patterns."""
        # Randomly rewire some edges
        if not self.edges:
            return
        
        n_rewire = max(1, int(len(self.edges) * 0.1))  # Rewire 10%
        edges_list = list(self.edges.keys())
        
        for _ in range(n_rewire):
            if not edges_list:
                break
            
            # Select random edge
            edge_idx = np.random.randint(len(edges_list))
            source, old_target = edges_list[edge_idx]
            
            # Select new target
            possible_targets = [nid for nid in self.nodes.keys() if nid != source]
            if possible_targets:
                new_target = np.random.choice(possible_targets)
                
                # Rewire
                weight = self.edges[(source, old_target)]
                self.remove_edge(source, old_target)
                self.add_edge(source, new_target, weight)
    
    def _stabilize_criticality(self):
        """Maintain current criticality."""
        # Small adjustments to edge weights
        for edge_key in list(self.edges.keys()):
            # Add small random perturbation
            perturbation = np.random.normal(0, 0.01)
            self.edges[edge_key] = max(0.01, self.edges[edge_key] + perturbation)
    
    def _update_activations(self):
        """Update node activations based on network dynamics."""
        if not self.nodes:
            return
        
        # Calculate new activations
        new_activations = {}
        for node_id, node in self.nodes.items():
            # Sum weighted inputs from connected nodes
            total_input = 0.0
            for neighbor_id in node.connections:
                edge_key = (node_id, neighbor_id)
                if edge_key in self.edges and neighbor_id in self.nodes:
                    weight = self.edges[edge_key]
                    total_input += weight * self.nodes[neighbor_id].activation
            
            # Apply activation function (sigmoid)
            new_activation = 1.0 / (1.0 + np.exp(-total_input))
            new_activations[node_id] = new_activation
        
        # Update all activations
        for node_id, activation in new_activations.items():
            self.nodes[node_id].activation = activation
    
    def get_regime(self) -> ComplexityRegime:
        """Get current complexity regime."""
        metrics = self.calculate_metrics()
        return self._determine_regime(metrics)
    
    def export_state(self) -> Dict[str, Any]:
        """Export complete engine state."""
        return {
            'nodes': {
                nid: {
                    'node_id': n.node_id,
                    'activation': n.activation,
                    'connections': list(n.connections),
                    'weight_sum': n.weight_sum,
                    'metadata': n.metadata
                }
                for nid, n in self.nodes.items()
            },
            'edges': {
                f"{s}->{t}": w for (s, t), w in self.edges.items()
            },
            'current_mode': self.current_mode.value,
            'metrics_history': [m.to_dict() for m in self.metrics_history[-100:]],  # Last 100
            'organization_events': self.organization_events[-100:]  # Last 100
        }


# Integration interface
def create_self_organizing_complexity(
    target_criticality: float = 0.5,
    criticality_tolerance: float = 0.1
) -> SelfOrganizingComplexity:
    """Factory function for creating self-organizing complexity engine."""
    return SelfOrganizingComplexity(
        target_criticality=target_criticality,
        criticality_tolerance=criticality_tolerance
    )


def test_self_organizing_complexity():
    """Test self-organizing complexity engine."""
    engine = create_self_organizing_complexity()
    
    # Test 1: Add nodes
    for i in range(10):
        engine.add_node(f"node_{i}")
    assert len(engine.nodes) == 10
    
    # Test 2: Add edges
    for i in range(9):
        engine.add_edge(f"node_{i}", f"node_{i+1}", weight=1.0)
    assert len(engine.edges) == 9
    
    # Test 3: Calculate metrics
    metrics = engine.calculate_metrics()
    assert metrics.entropy >= 0
    assert metrics.connectivity >= 0
    assert 0 <= metrics.criticality <= 1
    
    # Test 4: Self-organize
    iteration_metrics = engine.self_organize(iterations=5)
    assert len(iteration_metrics) == 5
    
    # Test 5: Regime detection
    regime = engine.get_regime()
    assert regime in [ComplexityRegime.ORDERED, ComplexityRegime.CRITICAL, ComplexityRegime.CHAOTIC]
    
    # Test 6: Export state
    state = engine.export_state()
    assert 'nodes' in state
    assert 'edges' in state
    assert 'current_mode' in state
    
    return True


if __name__ == '__main__':
    success = test_self_organizing_complexity()
    print(f"Self-Organizing Complexity Engine test: {'PASSED' if success else 'FAILED'}")
