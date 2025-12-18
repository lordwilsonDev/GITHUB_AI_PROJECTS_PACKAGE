"""
Level 21: Fractal Scaling Engine
Enables self-similar scaling patterns, infinite recursion capabilities, and dimension-independent growth.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Tuple
from datetime import datetime
import threading
import json
import random
import math
from enum import Enum
from collections import defaultdict


class ScalingPattern(Enum):
    """Types of fractal scaling patterns"""
    SELF_SIMILAR = "self_similar"
    HIERARCHICAL = "hierarchical"
    RECURSIVE = "recursive"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"


class DimensionType(Enum):
    """Dimension types for scaling"""
    SPATIAL = "spatial"
    TEMPORAL = "temporal"
    COMPUTATIONAL = "computational"
    CONCEPTUAL = "conceptual"
    INFINITE = "infinite"


@dataclass
class FractalNode:
    """Represents a node in the fractal structure"""
    node_id: str
    level: int
    parent_id: Optional[str]
    children: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    scale_factor: float = 1.0
    dimension: DimensionType = DimensionType.SPATIAL
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScalingConfig:
    """Configuration for fractal scaling"""
    max_recursion_depth: int = 100
    branching_factor: int = 3
    scale_ratio: float = 0.5
    enable_infinite_recursion: bool = True
    dimension_independence: bool = True
    self_similarity_threshold: float = 0.8


@dataclass
class ScalingMetrics:
    """Metrics for scaling operations"""
    total_nodes: int = 0
    max_depth: int = 0
    total_branches: int = 0
    scale_efficiency: float = 1.0
    dimension_count: int = 1
    timestamp: datetime = field(default_factory=datetime.now)


class FractalStructure:
    """Manages fractal structure and self-similar patterns"""
    
    def __init__(self, config: ScalingConfig):
        self.config = config
        self.nodes: Dict[str, FractalNode] = {}
        self.root_nodes: List[str] = []
        self.lock = threading.Lock()
    
    def create_root(
        self,
        node_id: str,
        data: Optional[Dict[str, Any]] = None,
        dimension: DimensionType = DimensionType.SPATIAL
    ) -> FractalNode:
        """Create a root node"""
        with self.lock:
            node = FractalNode(
                node_id=node_id,
                level=0,
                parent_id=None,
                data=data or {},
                dimension=dimension
            )
            
            self.nodes[node_id] = node
            self.root_nodes.append(node_id)
            return node
    
    def spawn_children(
        self,
        parent_id: str,
        count: Optional[int] = None,
        pattern: ScalingPattern = ScalingPattern.SELF_SIMILAR
    ) -> List[FractalNode]:
        """Spawn child nodes from parent"""
        with self.lock:
            parent = self.nodes.get(parent_id)
            if not parent:
                return []
            
            # Check recursion depth
            if parent.level >= self.config.max_recursion_depth:
                return []
            
            # Determine number of children
            if count is None:
                count = self.config.branching_factor
            
            children = []
            for i in range(count):
                child_id = f"{parent_id}_child_{i}"
                
                # Apply scaling pattern
                if pattern == ScalingPattern.SELF_SIMILAR:
                    scale_factor = parent.scale_factor * self.config.scale_ratio
                    child_data = self._apply_self_similar_transform(parent.data)
                elif pattern == ScalingPattern.EXPONENTIAL:
                    scale_factor = parent.scale_factor * (2 ** (parent.level + 1))
                    child_data = parent.data.copy()
                elif pattern == ScalingPattern.LOGARITHMIC:
                    scale_factor = parent.scale_factor * math.log(parent.level + 2)
                    child_data = parent.data.copy()
                else:
                    scale_factor = parent.scale_factor * self.config.scale_ratio
                    child_data = parent.data.copy()
                
                child = FractalNode(
                    node_id=child_id,
                    level=parent.level + 1,
                    parent_id=parent_id,
                    data=child_data,
                    scale_factor=scale_factor,
                    dimension=parent.dimension
                )
                
                self.nodes[child_id] = child
                parent.children.append(child_id)
                children.append(child)
            
            return children
    
    def _apply_self_similar_transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply self-similar transformation to data"""
        transformed = {}
        for key, value in data.items():
            if isinstance(value, (int, float)):
                transformed[key] = value * self.config.scale_ratio
            elif isinstance(value, dict):
                transformed[key] = self._apply_self_similar_transform(value)
            else:
                transformed[key] = value
        return transformed
    
    def recursive_expand(
        self,
        node_id: str,
        depth: int,
        pattern: ScalingPattern = ScalingPattern.SELF_SIMILAR
    ) -> int:
        """Recursively expand node to specified depth"""
        if depth <= 0:
            return 0
        
        children = self.spawn_children(node_id, pattern=pattern)
        total_spawned = len(children)
        
        for child in children:
            total_spawned += self.recursive_expand(child.node_id, depth - 1, pattern)
        
        return total_spawned
    
    def get_subtree(self, node_id: str) -> List[str]:
        """Get all nodes in subtree"""
        with self.lock:
            node = self.nodes.get(node_id)
            if not node:
                return []
            
            subtree = [node_id]
            for child_id in node.children:
                subtree.extend(self.get_subtree(child_id))
            
            return subtree
    
    def calculate_self_similarity(self, node1_id: str, node2_id: str) -> float:
        """Calculate self-similarity between two nodes"""
        with self.lock:
            node1 = self.nodes.get(node1_id)
            node2 = self.nodes.get(node2_id)
            
            if not node1 or not node2:
                return 0.0
            
            # Compare structure
            structure_similarity = 1.0 if len(node1.children) == len(node2.children) else 0.5
            
            # Compare scale factors
            scale_diff = abs(node1.scale_factor - node2.scale_factor)
            scale_similarity = 1.0 / (1.0 + scale_diff)
            
            # Compare dimensions
            dimension_similarity = 1.0 if node1.dimension == node2.dimension else 0.0
            
            return (structure_similarity + scale_similarity + dimension_similarity) / 3


class InfiniteRecursion:
    """Handles infinite recursion capabilities"""
    
    def __init__(self, structure: FractalStructure):
        self.structure = structure
        self.recursion_cache: Dict[str, List[str]] = {}
        self.lock = threading.Lock()
    
    def lazy_expand(
        self,
        node_id: str,
        generator: Callable[[str, int], List[FractalNode]]
    ) -> None:
        """Lazily expand node using generator function"""
        with self.lock:
            if node_id in self.recursion_cache:
                return
            
            node = self.structure.nodes.get(node_id)
            if not node:
                return
            
            # Generate children on-demand
            children = generator(node_id, node.level)
            child_ids = [c.node_id for c in children]
            
            self.recursion_cache[node_id] = child_ids
    
    def infinite_iterator(
        self,
        root_id: str,
        pattern: ScalingPattern = ScalingPattern.SELF_SIMILAR
    ):
        """Create infinite iterator over fractal structure"""
        visited = set()
        queue = [root_id]
        
        while queue:
            node_id = queue.pop(0)
            
            if node_id in visited:
                continue
            
            visited.add(node_id)
            yield node_id
            
            # Expand if needed
            node = self.structure.nodes.get(node_id)
            if node:
                if not node.children:
                    # Spawn children on-demand
                    children = self.structure.spawn_children(node_id, pattern=pattern)
                    queue.extend([c.node_id for c in children])
                else:
                    queue.extend(node.children)
    
    def bounded_infinite_expansion(
        self,
        root_id: str,
        max_nodes: int,
        pattern: ScalingPattern = ScalingPattern.SELF_SIMILAR
    ) -> int:
        """Expand infinitely up to max nodes"""
        count = 0
        for node_id in self.infinite_iterator(root_id, pattern):
            count += 1
            if count >= max_nodes:
                break
        
        return count


class DimensionIndependentScaler:
    """Handles dimension-independent scaling"""
    
    def __init__(self, structure: FractalStructure):
        self.structure = structure
        self.dimension_mappings: Dict[DimensionType, Dict[str, Any]] = {}
        self.lock = threading.Lock()
    
    def scale_across_dimensions(
        self,
        node_id: str,
        target_dimensions: List[DimensionType]
    ) -> Dict[DimensionType, str]:
        """Scale node across multiple dimensions"""
        with self.lock:
            node = self.structure.nodes.get(node_id)
            if not node:
                return {}
            
            projections = {}
            
            for dimension in target_dimensions:
                # Create projection in target dimension
                projection_id = f"{node_id}_dim_{dimension.value}"
                
                projection = FractalNode(
                    node_id=projection_id,
                    level=node.level,
                    parent_id=node.parent_id,
                    data=node.data.copy(),
                    scale_factor=node.scale_factor,
                    dimension=dimension
                )
                
                self.structure.nodes[projection_id] = projection
                projections[dimension] = projection_id
            
            return projections
    
    def cross_dimensional_sync(
        self,
        source_id: str,
        target_dimension: DimensionType
    ) -> Optional[str]:
        """Synchronize node across dimensions"""
        with self.lock:
            source = self.structure.nodes.get(source_id)
            if not source:
                return None
            
            # Find or create projection
            projection_id = f"{source_id}_dim_{target_dimension.value}"
            
            if projection_id not in self.structure.nodes:
                projection = FractalNode(
                    node_id=projection_id,
                    level=source.level,
                    parent_id=source.parent_id,
                    data=source.data.copy(),
                    scale_factor=source.scale_factor,
                    dimension=target_dimension
                )
                self.structure.nodes[projection_id] = projection
            else:
                # Sync data
                projection = self.structure.nodes[projection_id]
                projection.data.update(source.data)
            
            return projection_id


class FractalScalerManager:
    """High-level manager for fractal scaling system"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config = ScalingConfig()
            self.structure = FractalStructure(self.config)
            self.infinite_recursion = InfiniteRecursion(self.structure)
            self.dimension_scaler = DimensionIndependentScaler(self.structure)
            self.initialized = True
    
    def create_fractal_root(
        self,
        root_id: str,
        data: Optional[Dict[str, Any]] = None,
        dimension: DimensionType = DimensionType.SPATIAL
    ) -> FractalNode:
        """Create fractal root node"""
        return self.structure.create_root(root_id, data, dimension)
    
    def expand_fractal(
        self,
        node_id: str,
        depth: int,
        pattern: ScalingPattern = ScalingPattern.SELF_SIMILAR
    ) -> int:
        """Expand fractal structure"""
        return self.structure.recursive_expand(node_id, depth, pattern)
    
    def scale_infinitely(
        self,
        root_id: str,
        max_nodes: int,
        pattern: ScalingPattern = ScalingPattern.SELF_SIMILAR
    ) -> int:
        """Scale infinitely up to limit"""
        return self.infinite_recursion.bounded_infinite_expansion(root_id, max_nodes, pattern)
    
    def scale_across_dimensions(
        self,
        node_id: str,
        dimensions: List[DimensionType]
    ) -> Dict[DimensionType, str]:
        """Scale across multiple dimensions"""
        return self.dimension_scaler.scale_across_dimensions(node_id, dimensions)
    
    def get_metrics(self) -> ScalingMetrics:
        """Get scaling metrics"""
        total_nodes = len(self.structure.nodes)
        max_depth = max((n.level for n in self.structure.nodes.values()), default=0)
        total_branches = sum(len(n.children) for n in self.structure.nodes.values())
        
        # Calculate dimension count
        dimensions = set(n.dimension for n in self.structure.nodes.values())
        
        return ScalingMetrics(
            total_nodes=total_nodes,
            max_depth=max_depth,
            total_branches=total_branches,
            dimension_count=len(dimensions)
        )


# Contract class for testing
class Contract:
    """Testing interface for fractal scaler"""
    
    @staticmethod
    def self_similar_scaling() -> bool:
        """Test: Self-similar scaling patterns"""
        manager = FractalScalerManager()
        root = manager.create_fractal_root("root", {"value": 100})
        expanded = manager.expand_fractal("root", depth=3, pattern=ScalingPattern.SELF_SIMILAR)
        return expanded > 0
    
    @staticmethod
    def infinite_recursion() -> bool:
        """Test: Infinite recursion capabilities"""
        manager = FractalScalerManager()
        root = manager.create_fractal_root("infinite_root", {"data": "test"})
        nodes_created = manager.scale_infinitely("infinite_root", max_nodes=100)
        return nodes_created >= 100
    
    @staticmethod
    def dimension_independent_growth() -> bool:
        """Test: Dimension-independent growth"""
        manager = FractalScalerManager()
        root = manager.create_fractal_root("multi_dim", {"value": 1})
        
        dimensions = [DimensionType.SPATIAL, DimensionType.TEMPORAL, DimensionType.COMPUTATIONAL]
        projections = manager.scale_across_dimensions("multi_dim", dimensions)
        
        return len(projections) == 3
    
    @staticmethod
    def fractal_metrics() -> bool:
        """Test: Fractal metrics calculation"""
        manager = FractalScalerManager()
        root = manager.create_fractal_root("metrics_root")
        manager.expand_fractal("metrics_root", depth=2)
        
        metrics = manager.get_metrics()
        return metrics.total_nodes > 1 and metrics.max_depth >= 2


def demo():
    """Demonstrate fractal scaling capabilities"""
    print("=== Fractal Scaling Engine Demo ===\n")
    
    manager = FractalScalerManager()
    
    # Demo 1: Create fractal root
    print("1. Creating fractal root:")
    root = manager.create_fractal_root("system_root", {"capacity": 1000, "load": 0})
    print(f"   Created root: {root.node_id}")
    print(f"   Initial data: {root.data}")
    
    # Demo 2: Self-similar expansion
    print("\n2. Self-similar fractal expansion:")
    expanded = manager.expand_fractal("system_root", depth=4, pattern=ScalingPattern.SELF_SIMILAR)
    print(f"   Expanded {expanded} nodes")
    metrics = manager.get_metrics()
    print(f"   Total nodes: {metrics.total_nodes}")
    print(f"   Max depth: {metrics.max_depth}")
    
    # Demo 3: Infinite scaling
    print("\n3. Infinite scaling (bounded):")
    infinite_root = manager.create_fractal_root("infinite_system", {"id": 0})
    nodes = manager.scale_infinitely("infinite_system", max_nodes=50, pattern=ScalingPattern.EXPONENTIAL)
    print(f"   Created {nodes} nodes through infinite scaling")
    
    # Demo 4: Dimension-independent scaling
    print("\n4. Dimension-independent scaling:")
    multi_root = manager.create_fractal_root("multi_dimensional", {"value": 100})
    dimensions = [
        DimensionType.SPATIAL,
        DimensionType.TEMPORAL,
        DimensionType.COMPUTATIONAL,
        DimensionType.CONCEPTUAL
    ]
    projections = manager.scale_across_dimensions("multi_dimensional", dimensions)
    print(f"   Scaled across {len(projections)} dimensions:")
    for dim, proj_id in projections.items():
        print(f"      {dim.value}: {proj_id}")
    
    # Demo 5: Different scaling patterns
    print("\n5. Testing different scaling patterns:")
    patterns = [
        ScalingPattern.SELF_SIMILAR,
        ScalingPattern.EXPONENTIAL,
        ScalingPattern.LOGARITHMIC
    ]
    
    for pattern in patterns:
        pattern_root = manager.create_fractal_root(f"pattern_{pattern.value}", {"x": 1})
        count = manager.expand_fractal(f"pattern_{pattern.value}", depth=3, pattern=pattern)
        print(f"   {pattern.value}: {count} nodes")
    
    # Demo 6: Final metrics
    print("\n6. Final system metrics:")
    final_metrics = manager.get_metrics()
    print(f"   Total nodes: {final_metrics.total_nodes}")
    print(f"   Max depth: {final_metrics.max_depth}")
    print(f"   Total branches: {final_metrics.total_branches}")
    print(f"   Dimensions: {final_metrics.dimension_count}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    demo()
