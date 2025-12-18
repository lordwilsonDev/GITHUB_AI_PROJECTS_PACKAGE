"""
Level 21: Infinite Graph Engine
Enables unbounded graph expansion, dynamic restructuring, and infinite relationship management.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Callable, Tuple
from datetime import datetime
import threading
import json
import random
import math
from enum import Enum
from collections import defaultdict, deque


class NodeType(Enum):
    """Types of graph nodes"""
    ENTITY = "entity"
    CONCEPT = "concept"
    EVENT = "event"
    RELATION = "relation"
    CLUSTER = "cluster"
    VIRTUAL = "virtual"


class EdgeType(Enum):
    """Types of graph edges"""
    DIRECTED = "directed"
    UNDIRECTED = "undirected"
    BIDIRECTIONAL = "bidirectional"
    WEIGHTED = "weighted"
    TEMPORAL = "temporal"


class GraphOperation(Enum):
    """Graph operations"""
    ADD_NODE = "add_node"
    REMOVE_NODE = "remove_node"
    ADD_EDGE = "add_edge"
    REMOVE_EDGE = "remove_edge"
    MERGE_NODES = "merge_nodes"
    SPLIT_NODE = "split_node"
    RESTRUCTURE = "restructure"


@dataclass
class GraphNode:
    """Represents a node in the infinite graph"""
    node_id: str
    node_type: NodeType
    data: Dict[str, Any] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)
    edges: Set[str] = field(default_factory=set)
    incoming_edges: Set[str] = field(default_factory=set)
    outgoing_edges: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    """Represents an edge in the infinite graph"""
    edge_id: str
    edge_type: EdgeType
    source_id: str
    target_id: str
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphCluster:
    """Represents a cluster of nodes"""
    cluster_id: str
    node_ids: Set[str] = field(default_factory=set)
    centroid: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class GraphMetrics:
    """Metrics for the graph"""
    total_nodes: int = 0
    total_edges: int = 0
    average_degree: float = 0.0
    density: float = 0.0
    clusters: int = 0
    diameter: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)


class InfiniteGraphManager:
    """Manages an infinite, dynamically restructuring graph"""
    
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, GraphEdge] = {}
        self.clusters: Dict[str, GraphCluster] = {}
        self.node_counter = 0
        self.edge_counter = 0
        self.cluster_counter = 0
        self.lock = threading.Lock()
        self.operation_history: List[Tuple[GraphOperation, Dict[str, Any]]] = []
        self.index: Dict[str, Set[str]] = defaultdict(set)  # Property-based index
        
    def add_node(self, node_type: NodeType, data: Optional[Dict[str, Any]] = None,
                 properties: Optional[Dict[str, Any]] = None) -> str:
        """Add a new node to the graph"""
        with self.lock:
            self.node_counter += 1
            node_id = f"node_{self.node_counter}_{node_type.value}"
            
            node = GraphNode(
                node_id=node_id,
                node_type=node_type,
                data=data or {},
                properties=properties or {}
            )
            
            self.nodes[node_id] = node
            
            # Update index
            for key, value in (properties or {}).items():
                self.index[f"{key}:{value}"].add(node_id)
            
            self.operation_history.append((GraphOperation.ADD_NODE, {"node_id": node_id}))
            return node_id
    
    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the graph"""
        with self.lock:
            if node_id not in self.nodes:
                return False
            
            node = self.nodes[node_id]
            
            # Remove all connected edges
            edges_to_remove = list(node.edges | node.incoming_edges | node.outgoing_edges)
            for edge_id in edges_to_remove:
                self.remove_edge(edge_id)
            
            # Update index
            for key, value in node.properties.items():
                self.index[f"{key}:{value}"].discard(node_id)
            
            del self.nodes[node_id]
            self.operation_history.append((GraphOperation.REMOVE_NODE, {"node_id": node_id}))
            return True
    
    def add_edge(self, source_id: str, target_id: str, edge_type: EdgeType,
                 weight: float = 1.0, properties: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Add an edge between two nodes"""
        with self.lock:
            if source_id not in self.nodes or target_id not in self.nodes:
                return None
            
            self.edge_counter += 1
            edge_id = f"edge_{self.edge_counter}"
            
            edge = GraphEdge(
                edge_id=edge_id,
                edge_type=edge_type,
                source_id=source_id,
                target_id=target_id,
                weight=weight,
                properties=properties or {}
            )
            
            self.edges[edge_id] = edge
            
            # Update node connections
            self.nodes[source_id].edges.add(edge_id)
            self.nodes[source_id].outgoing_edges.add(edge_id)
            self.nodes[target_id].edges.add(edge_id)
            self.nodes[target_id].incoming_edges.add(edge_id)
            
            if edge_type == EdgeType.BIDIRECTIONAL or edge_type == EdgeType.UNDIRECTED:
                self.nodes[target_id].outgoing_edges.add(edge_id)
                self.nodes[source_id].incoming_edges.add(edge_id)
            
            self.operation_history.append((GraphOperation.ADD_EDGE, {"edge_id": edge_id}))
            return edge_id
    
    def remove_edge(self, edge_id: str) -> bool:
        """Remove an edge from the graph"""
        with self.lock:
            if edge_id not in self.edges:
                return False
            
            edge = self.edges[edge_id]
            
            # Update node connections
            if edge.source_id in self.nodes:
                self.nodes[edge.source_id].edges.discard(edge_id)
                self.nodes[edge.source_id].outgoing_edges.discard(edge_id)
                self.nodes[edge.source_id].incoming_edges.discard(edge_id)
            
            if edge.target_id in self.nodes:
                self.nodes[edge.target_id].edges.discard(edge_id)
                self.nodes[edge.target_id].incoming_edges.discard(edge_id)
                self.nodes[edge.target_id].outgoing_edges.discard(edge_id)
            
            del self.edges[edge_id]
            self.operation_history.append((GraphOperation.REMOVE_EDGE, {"edge_id": edge_id}))
            return True
    
    def merge_nodes(self, node_ids: List[str], merged_type: NodeType) -> Optional[str]:
        """Merge multiple nodes into a single node"""
        with self.lock:
            if not all(nid in self.nodes for nid in node_ids):
                return None
            
            # Create merged node
            merged_data = {}
            merged_properties = {}
            all_edges = set()
            
            for node_id in node_ids:
                node = self.nodes[node_id]
                merged_data.update(node.data)
                merged_properties.update(node.properties)
                all_edges.update(node.edges)
            
            merged_id = self.add_node(merged_type, merged_data, merged_properties)
            
            # Reconnect edges
            for edge_id in all_edges:
                if edge_id in self.edges:
                    edge = self.edges[edge_id]
                    new_source = merged_id if edge.source_id in node_ids else edge.source_id
                    new_target = merged_id if edge.target_id in node_ids else edge.target_id
                    
                    if new_source != new_target:  # Avoid self-loops
                        self.add_edge(new_source, new_target, edge.edge_type, 
                                    edge.weight, edge.properties)
            
            # Remove original nodes
            for node_id in node_ids:
                self.remove_node(node_id)
            
            self.operation_history.append((GraphOperation.MERGE_NODES, 
                                          {"merged_id": merged_id, "source_ids": node_ids}))
            return merged_id
    
    def split_node(self, node_id: str, split_criteria: Callable[[Dict[str, Any]], int]) -> List[str]:
        """Split a node into multiple nodes based on criteria"""
        with self.lock:
            if node_id not in self.nodes:
                return []
            
            node = self.nodes[node_id]
            
            # Partition data based on criteria
            partitions = defaultdict(dict)
            for key, value in node.data.items():
                partition_id = split_criteria({key: value})
                partitions[partition_id][key] = value
            
            # Create new nodes
            new_node_ids = []
            for partition_data in partitions.values():
                new_id = self.add_node(node.node_type, partition_data, node.properties.copy())
                new_node_ids.append(new_id)
            
            # Distribute edges
            for edge_id in list(node.edges):
                if edge_id in self.edges:
                    edge = self.edges[edge_id]
                    # Connect to first new node (simple strategy)
                    if new_node_ids:
                        new_source = new_node_ids[0] if edge.source_id == node_id else edge.source_id
                        new_target = new_node_ids[0] if edge.target_id == node_id else edge.target_id
                        self.add_edge(new_source, new_target, edge.edge_type, 
                                    edge.weight, edge.properties)
            
            # Remove original node
            self.remove_node(node_id)
            
            self.operation_history.append((GraphOperation.SPLIT_NODE, 
                                          {"original_id": node_id, "new_ids": new_node_ids}))
            return new_node_ids
    
    def find_nodes(self, criteria: Dict[str, Any]) -> List[str]:
        """Find nodes matching criteria"""
        with self.lock:
            # Use index for efficient lookup
            result_sets = []
            for key, value in criteria.items():
                index_key = f"{key}:{value}"
                if index_key in self.index:
                    result_sets.append(self.index[index_key])
            
            if not result_sets:
                # Fallback to full scan
                matching = []
                for node_id, node in self.nodes.items():
                    if all(node.properties.get(k) == v for k, v in criteria.items()):
                        matching.append(node_id)
                return matching
            
            # Intersection of all matching sets
            return list(set.intersection(*result_sets))
    
    def get_neighbors(self, node_id: str, depth: int = 1) -> Set[str]:
        """Get neighbors of a node up to specified depth"""
        with self.lock:
            if node_id not in self.nodes:
                return set()
            
            visited = set()
            current_level = {node_id}
            
            for _ in range(depth):
                next_level = set()
                for nid in current_level:
                    if nid in self.nodes:
                        node = self.nodes[nid]
                        for edge_id in node.edges:
                            if edge_id in self.edges:
                                edge = self.edges[edge_id]
                                neighbor = edge.target_id if edge.source_id == nid else edge.source_id
                                if neighbor not in visited:
                                    next_level.add(neighbor)
                
                visited.update(current_level)
                current_level = next_level
            
            visited.discard(node_id)
            return visited
    
    def find_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """Find shortest path between two nodes using BFS"""
        with self.lock:
            if source_id not in self.nodes or target_id not in self.nodes:
                return None
            
            if source_id == target_id:
                return [source_id]
            
            queue = deque([(source_id, [source_id])])
            visited = {source_id}
            
            while queue:
                current, path = queue.popleft()
                
                if current in self.nodes:
                    node = self.nodes[current]
                    for edge_id in node.outgoing_edges:
                        if edge_id in self.edges:
                            edge = self.edges[edge_id]
                            neighbor = edge.target_id
                            
                            if neighbor == target_id:
                                return path + [neighbor]
                            
                            if neighbor not in visited:
                                visited.add(neighbor)
                                queue.append((neighbor, path + [neighbor]))
            
            return None
    
    def create_cluster(self, node_ids: Set[str]) -> str:
        """Create a cluster from a set of nodes"""
        with self.lock:
            self.cluster_counter += 1
            cluster_id = f"cluster_{self.cluster_counter}"
            
            # Find centroid (node with most connections within cluster)
            centroid = None
            max_internal_edges = 0
            
            for node_id in node_ids:
                if node_id in self.nodes:
                    internal_edges = sum(1 for edge_id in self.nodes[node_id].edges
                                       if edge_id in self.edges and
                                       (self.edges[edge_id].source_id in node_ids and
                                        self.edges[edge_id].target_id in node_ids))
                    if internal_edges > max_internal_edges:
                        max_internal_edges = internal_edges
                        centroid = node_id
            
            cluster = GraphCluster(
                cluster_id=cluster_id,
                node_ids=node_ids,
                centroid=centroid
            )
            
            self.clusters[cluster_id] = cluster
            return cluster_id
    
    def detect_clusters(self, min_size: int = 3) -> List[str]:
        """Detect clusters in the graph using simple connected components"""
        with self.lock:
            visited = set()
            clusters = []
            
            for node_id in self.nodes:
                if node_id not in visited:
                    # BFS to find connected component
                    component = set()
                    queue = deque([node_id])
                    
                    while queue:
                        current = queue.popleft()
                        if current not in visited:
                            visited.add(current)
                            component.add(current)
                            
                            if current in self.nodes:
                                neighbors = self.get_neighbors(current, depth=1)
                                queue.extend(neighbors - visited)
                    
                    if len(component) >= min_size:
                        cluster_id = self.create_cluster(component)
                        clusters.append(cluster_id)
            
            return clusters
    
    def restructure(self, strategy: str = "optimize_density"):
        """Restructure the graph based on strategy"""
        with self.lock:
            if strategy == "optimize_density":
                # Remove low-weight edges
                edges_to_remove = []
                for edge_id, edge in self.edges.items():
                    if edge.weight < 0.3:
                        edges_to_remove.append(edge_id)
                
                for edge_id in edges_to_remove:
                    self.remove_edge(edge_id)
            
            elif strategy == "cluster_based":
                # Detect and formalize clusters
                self.detect_clusters()
            
            elif strategy == "prune_isolated":
                # Remove isolated nodes
                nodes_to_remove = []
                for node_id, node in self.nodes.items():
                    if len(node.edges) == 0:
                        nodes_to_remove.append(node_id)
                
                for node_id in nodes_to_remove:
                    self.remove_node(node_id)
            
            self.operation_history.append((GraphOperation.RESTRUCTURE, {"strategy": strategy}))
    
    def get_metrics(self) -> GraphMetrics:
        """Calculate graph metrics"""
        with self.lock:
            total_nodes = len(self.nodes)
            total_edges = len(self.edges)
            
            if total_nodes == 0:
                return GraphMetrics()
            
            # Calculate average degree
            total_degree = sum(len(node.edges) for node in self.nodes.values())
            average_degree = total_degree / total_nodes if total_nodes > 0 else 0
            
            # Calculate density
            max_edges = total_nodes * (total_nodes - 1) / 2
            density = total_edges / max_edges if max_edges > 0 else 0
            
            return GraphMetrics(
                total_nodes=total_nodes,
                total_edges=total_edges,
                average_degree=average_degree,
                density=density,
                clusters=len(self.clusters)
            )
    
    def export_graph(self) -> Dict[str, Any]:
        """Export graph structure"""
        with self.lock:
            return {
                "nodes": [
                    {
                        "id": node.node_id,
                        "type": node.node_type.value,
                        "data": node.data,
                        "properties": node.properties
                    }
                    for node in self.nodes.values()
                ],
                "edges": [
                    {
                        "id": edge.edge_id,
                        "type": edge.edge_type.value,
                        "source": edge.source_id,
                        "target": edge.target_id,
                        "weight": edge.weight
                    }
                    for edge in self.edges.values()
                ],
                "clusters": [
                    {
                        "id": cluster.cluster_id,
                        "nodes": list(cluster.node_ids),
                        "centroid": cluster.centroid
                    }
                    for cluster in self.clusters.values()
                ]
            }


# Singleton instance
_graph_manager = None
_graph_lock = threading.Lock()


def get_graph_manager() -> InfiniteGraphManager:
    """Get the singleton graph manager instance"""
    global _graph_manager
    if _graph_manager is None:
        with _graph_lock:
            if _graph_manager is None:
                _graph_manager = InfiniteGraphManager()
    return _graph_manager


class Contract:
    """Testing contract for infinite graph"""
    
    @staticmethod
    def test_node_operations():
        """Test adding and removing nodes"""
        manager = InfiniteGraphManager()
        node_id = manager.add_node(NodeType.ENTITY, {"name": "test"})
        assert node_id in manager.nodes
        assert manager.remove_node(node_id)
        assert node_id not in manager.nodes
        return True
    
    @staticmethod
    def test_edge_operations():
        """Test adding and removing edges"""
        manager = InfiniteGraphManager()
        n1 = manager.add_node(NodeType.ENTITY)
        n2 = manager.add_node(NodeType.ENTITY)
        edge_id = manager.add_edge(n1, n2, EdgeType.DIRECTED)
        assert edge_id in manager.edges
        return True
    
    @staticmethod
    def test_path_finding():
        """Test finding paths between nodes"""
        manager = InfiniteGraphManager()
        n1 = manager.add_node(NodeType.ENTITY)
        n2 = manager.add_node(NodeType.ENTITY)
        n3 = manager.add_node(NodeType.ENTITY)
        manager.add_edge(n1, n2, EdgeType.DIRECTED)
        manager.add_edge(n2, n3, EdgeType.DIRECTED)
        
        path = manager.find_path(n1, n3)
        assert path is not None
        assert len(path) == 3
        return True
    
    @staticmethod
    def test_clustering():
        """Test cluster detection"""
        manager = InfiniteGraphManager()
        nodes = [manager.add_node(NodeType.ENTITY) for _ in range(5)]
        
        # Create connected cluster
        for i in range(len(nodes) - 1):
            manager.add_edge(nodes[i], nodes[i+1], EdgeType.UNDIRECTED)
        
        clusters = manager.detect_clusters(min_size=3)
        assert len(clusters) > 0
        return True


def demo():
    """Demonstrate infinite graph capabilities"""
    print("=== Infinite Graph Demo ===")
    
    manager = get_graph_manager()
    
    # Create knowledge graph
    print("\n1. Building knowledge graph...")
    entities = []
    for i in range(10):
        node_id = manager.add_node(
            NodeType.ENTITY,
            data={"name": f"Entity_{i}", "value": random.randint(1, 100)},
            properties={"category": f"cat_{i % 3}"}
        )
        entities.append(node_id)
    
    print(f"   Created {len(entities)} entities")
    
    # Add relationships
    print("\n2. Adding relationships...")
    edges_created = 0
    for i in range(len(entities)):
        for j in range(i + 1, min(i + 4, len(entities))):
            manager.add_edge(entities[i], entities[j], EdgeType.WEIGHTED, 
                           weight=random.random())
            edges_created += 1
    
    print(f"   Created {edges_created} edges")
    
    # Find paths
    print("\n3. Finding paths...")
    path = manager.find_path(entities[0], entities[-1])
    if path:
        print(f"   Path from {entities[0]} to {entities[-1]}: {len(path)} nodes")
    
    # Detect clusters
    print("\n4. Detecting clusters...")
    clusters = manager.detect_clusters(min_size=2)
    print(f"   Found {len(clusters)} clusters")
    
    # Get metrics
    print("\n5. Graph metrics:")
    metrics = manager.get_metrics()
    print(f"   Total nodes: {metrics.total_nodes}")
    print(f"   Total edges: {metrics.total_edges}")
    print(f"   Average degree: {metrics.average_degree:.2f}")
    print(f"   Density: {metrics.density:.3f}")
    
    # Restructure
    print("\n6. Restructuring graph...")
    manager.restructure("optimize_density")
    new_metrics = manager.get_metrics()
    print(f"   Edges after optimization: {new_metrics.total_edges}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    # Run contract tests
    print("Running contract tests...")
    assert Contract.test_node_operations()
    assert Contract.test_edge_operations()
    assert Contract.test_path_finding()
    assert Contract.test_clustering()
    print("All tests passed!\n")
    
    # Run demo
    demo()
