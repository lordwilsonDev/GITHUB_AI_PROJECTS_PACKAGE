#!/usr/bin/env python3
"""
Fractal Reasoning Engine - New Build 12 (T-096)
Self-similar reasoning patterns with multi-scale problem solving.
Implements recursive abstraction layers for fractal intelligence.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from collections import deque


class ReasoningScale(Enum):
    """Scales of reasoning."""
    MICRO = "micro"  # Fine-grained details
    MESO = "meso"  # Medium-scale patterns
    MACRO = "macro"  # Large-scale structures
    META = "meta"  # Meta-level reasoning


class AbstractionLevel(Enum):
    """Levels of abstraction."""
    CONCRETE = 0  # Concrete facts
    PATTERN = 1  # Patterns in facts
    PRINCIPLE = 2  # Principles from patterns
    THEORY = 3  # Theories from principles
    PARADIGM = 4  # Paradigms from theories


@dataclass
class ReasoningNode:
    """Node in fractal reasoning tree."""
    node_id: str
    scale: ReasoningScale
    abstraction_level: AbstractionLevel
    content: Any
    children: List[str] = field(default_factory=list)
    parent: Optional[str] = None
    self_similarity: float = 0.0  # How similar to parent
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'node_id': self.node_id,
            'scale': self.scale.value,
            'abstraction_level': self.abstraction_level.value,
            'content': str(self.content),
            'children': self.children,
            'parent': self.parent,
            'self_similarity': float(self.self_similarity),
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }


@dataclass
class ReasoningPath:
    """Path through reasoning space."""
    path_id: str
    nodes: List[str]
    scales_traversed: List[ReasoningScale]
    abstraction_depth: int
    fractal_dimension: float
    confidence: float
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'path_id': self.path_id,
            'nodes': self.nodes,
            'scales_traversed': [s.value for s in self.scales_traversed],
            'abstraction_depth': self.abstraction_depth,
            'fractal_dimension': float(self.fractal_dimension),
            'confidence': float(self.confidence),
            'timestamp': self.timestamp
        }


class FractalReasoning:
    """
    Fractal reasoning engine with self-similar patterns and multi-scale solving.
    
    Features:
    - Self-similar reasoning patterns
    - Multi-scale problem solving
    - Recursive abstraction layers
    - Fractal dimension analysis
    - Scale-invariant insights
    """
    
    def __init__(
        self,
        max_abstraction_depth: int = 5,
        self_similarity_threshold: float = 0.7
    ):
        self.nodes: Dict[str, ReasoningNode] = {}
        self.max_abstraction_depth = max_abstraction_depth
        self.self_similarity_threshold = self_similarity_threshold
        
        self.reasoning_paths: List[ReasoningPath] = []
        self.fractal_patterns: Dict[str, List[str]] = {}  # Pattern -> nodes
        
    def add_reasoning_node(
        self,
        node_id: str,
        content: Any,
        scale: ReasoningScale = ReasoningScale.MESO,
        abstraction_level: AbstractionLevel = AbstractionLevel.CONCRETE,
        parent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ReasoningNode:
        """Add a reasoning node to the fractal tree."""
        node = ReasoningNode(
            node_id=node_id,
            scale=scale,
            abstraction_level=abstraction_level,
            content=content,
            parent=parent,
            metadata=metadata or {}
        )
        
        # Calculate self-similarity with parent
        if parent and parent in self.nodes:
            node.self_similarity = self._calculate_self_similarity(
                node,
                self.nodes[parent]
            )
            # Add to parent's children
            self.nodes[parent].children.append(node_id)
        
        self.nodes[node_id] = node
        return node
    
    def _calculate_self_similarity(self, node1: ReasoningNode, node2: ReasoningNode) -> float:
        """Calculate self-similarity between nodes."""
        # Similarity based on structure and content
        
        # Scale similarity
        scale_match = 1.0 if node1.scale == node2.scale else 0.5
        
        # Abstraction level similarity (adjacent levels are similar)
        level_diff = abs(node1.abstraction_level.value - node2.abstraction_level.value)
        level_similarity = 1.0 / (1.0 + level_diff)
        
        # Content similarity (simplified - based on string representation)
        content1_str = str(node1.content)
        content2_str = str(node2.content)
        
        # Jaccard similarity on words
        words1 = set(content1_str.lower().split())
        words2 = set(content2_str.lower().split())
        
        if words1 or words2:
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            content_similarity = intersection / union if union > 0 else 0.0
        else:
            content_similarity = 0.0
        
        # Weighted combination
        return 0.3 * scale_match + 0.3 * level_similarity + 0.4 * content_similarity
    
    def abstract_upward(
        self,
        node_id: str,
        abstraction_function: Optional[Callable[[Any], Any]] = None
    ) -> Optional[ReasoningNode]:
        """
        Create higher abstraction from a node.
        
        Args:
            node_id: Node to abstract from
            abstraction_function: Function to generate abstraction
            
        Returns:
            New abstracted node or None if max depth reached
        """
        if node_id not in self.nodes:
            return None
        
        node = self.nodes[node_id]
        
        # Check if we can go higher
        if node.abstraction_level.value >= self.max_abstraction_depth:
            return None
        
        # Generate abstraction
        if abstraction_function:
            abstract_content = abstraction_function(node.content)
        else:
            # Default abstraction: extract key concepts
            abstract_content = self._default_abstraction(node.content)
        
        # Determine new level
        new_level = AbstractionLevel(node.abstraction_level.value + 1)
        
        # Determine new scale (go up one level)
        scale_progression = {
            ReasoningScale.MICRO: ReasoningScale.MESO,
            ReasoningScale.MESO: ReasoningScale.MACRO,
            ReasoningScale.MACRO: ReasoningScale.META,
            ReasoningScale.META: ReasoningScale.META
        }
        new_scale = scale_progression[node.scale]
        
        # Create new node
        abstract_id = f"{node_id}_abstract_{new_level.value}"
        abstract_node = self.add_reasoning_node(
            node_id=abstract_id,
            content=abstract_content,
            scale=new_scale,
            abstraction_level=new_level,
            parent=node_id
        )
        
        return abstract_node
    
    def _default_abstraction(self, content: Any) -> str:
        """Default abstraction function."""
        # Extract key concepts (simplified)
        content_str = str(content)
        words = content_str.split()
        
        # Take first few words as abstraction
        key_words = words[:min(5, len(words))]
        return " ".join(key_words) + " [abstracted]"
    
    def concretize_downward(
        self,
        node_id: str,
        concretization_function: Optional[Callable[[Any], List[Any]]] = None,
        num_children: int = 3
    ) -> List[ReasoningNode]:
        """
        Create more concrete instances from a node.
        
        Args:
            node_id: Node to concretize from
            concretization_function: Function to generate concrete instances
            num_children: Number of concrete instances to create
            
        Returns:
            List of new concrete nodes
        """
        if node_id not in self.nodes:
            return []
        
        node = self.nodes[node_id]
        
        # Check if we can go lower
        if node.abstraction_level.value <= 0:
            return []
        
        # Generate concrete instances
        if concretization_function:
            concrete_contents = concretization_function(node.content)
        else:
            # Default concretization: add details
            concrete_contents = self._default_concretization(node.content, num_children)
        
        # Determine new level
        new_level = AbstractionLevel(node.abstraction_level.value - 1)
        
        # Determine new scale (go down one level)
        scale_progression = {
            ReasoningScale.META: ReasoningScale.MACRO,
            ReasoningScale.MACRO: ReasoningScale.MESO,
            ReasoningScale.MESO: ReasoningScale.MICRO,
            ReasoningScale.MICRO: ReasoningScale.MICRO
        }
        new_scale = scale_progression[node.scale]
        
        # Create new nodes
        concrete_nodes = []
        for i, content in enumerate(concrete_contents):
            concrete_id = f"{node_id}_concrete_{i}"
            concrete_node = self.add_reasoning_node(
                node_id=concrete_id,
                content=content,
                scale=new_scale,
                abstraction_level=new_level,
                parent=node_id
            )
            concrete_nodes.append(concrete_node)
        
        return concrete_nodes
    
    def _default_concretization(self, content: Any, num_children: int) -> List[str]:
        """Default concretization function."""
        # Generate concrete instances (simplified)
        base = str(content)
        return [f"{base} - instance {i+1}" for i in range(num_children)]
    
    def find_fractal_patterns(self) -> Dict[str, List[str]]:
        """
        Identify fractal (self-similar) patterns in reasoning tree.
        
        Returns:
            Dictionary mapping pattern signatures to node lists
        """
        patterns = {}
        
        # Group nodes by self-similarity
        for node_id, node in self.nodes.items():
            if node.parent and node.self_similarity >= self.self_similarity_threshold:
                # This node is self-similar to its parent
                parent = self.nodes[node.parent]
                
                # Create pattern signature
                signature = f"{node.scale.value}_{node.abstraction_level.value}"
                
                if signature not in patterns:
                    patterns[signature] = []
                patterns[signature].append(node_id)
        
        self.fractal_patterns = patterns
        return patterns
    
    def calculate_fractal_dimension(self, root_node_id: str) -> float:
        """
        Calculate fractal dimension of reasoning subtree.
        
        Uses box-counting method approximation.
        """
        if root_node_id not in self.nodes:
            return 0.0
        
        # Count nodes at each depth level
        depth_counts = {}
        
        def count_at_depth(node_id: str, depth: int):
            if node_id not in self.nodes:
                return
            
            if depth not in depth_counts:
                depth_counts[depth] = 0
            depth_counts[depth] += 1
            
            # Recurse to children
            for child_id in self.nodes[node_id].children:
                count_at_depth(child_id, depth + 1)
        
        count_at_depth(root_node_id, 0)
        
        if len(depth_counts) < 2:
            return 1.0  # Linear
        
        # Calculate fractal dimension using log-log slope
        depths = np.array(list(depth_counts.keys()))
        counts = np.array(list(depth_counts.values()))
        
        # Avoid log(0)
        depths = depths[counts > 0]
        counts = counts[counts > 0]
        
        if len(depths) < 2:
            return 1.0
        
        # Linear regression in log-log space
        log_depths = np.log(depths + 1)
        log_counts = np.log(counts)
        
        # Fit line
        slope, _ = np.polyfit(log_depths, log_counts, 1)
        
        # Fractal dimension is the slope
        return abs(slope)
    
    def reason_across_scales(
        self,
        start_node_id: str,
        target_scale: ReasoningScale
    ) -> Optional[ReasoningPath]:
        """
        Reason from one scale to another.
        
        Args:
            start_node_id: Starting node
            target_scale: Target scale to reach
            
        Returns:
            ReasoningPath or None
        """
        if start_node_id not in self.nodes:
            return None
        
        start_node = self.nodes[start_node_id]
        
        # BFS to find path to target scale
        queue = deque([(start_node_id, [start_node_id], [start_node.scale])])
        visited = {start_node_id}
        
        while queue:
            current_id, path, scales = queue.popleft()
            current_node = self.nodes[current_id]
            
            # Check if we reached target scale
            if current_node.scale == target_scale:
                # Calculate path properties
                abstraction_depth = max(
                    self.nodes[nid].abstraction_level.value for nid in path
                )
                
                fractal_dim = self.calculate_fractal_dimension(start_node_id)
                
                # Calculate confidence based on self-similarity along path
                similarities = []
                for i in range(1, len(path)):
                    node = self.nodes[path[i]]
                    similarities.append(node.self_similarity)
                
                confidence = np.mean(similarities) if similarities else 0.5
                
                reasoning_path = ReasoningPath(
                    path_id=f"path_{len(self.reasoning_paths)}",
                    nodes=path,
                    scales_traversed=scales,
                    abstraction_depth=abstraction_depth,
                    fractal_dimension=fractal_dim,
                    confidence=confidence
                )
                
                self.reasoning_paths.append(reasoning_path)
                return reasoning_path
            
            # Explore neighbors (parent and children)
            neighbors = []
            if current_node.parent:
                neighbors.append(current_node.parent)
            neighbors.extend(current_node.children)
            
            for neighbor_id in neighbors:
                if neighbor_id not in visited and neighbor_id in self.nodes:
                    visited.add(neighbor_id)
                    neighbor_node = self.nodes[neighbor_id]
                    queue.append((
                        neighbor_id,
                        path + [neighbor_id],
                        scales + [neighbor_node.scale]
                    ))
        
        return None  # No path found
    
    def get_tree_depth(self, root_node_id: str) -> int:
        """Calculate maximum depth of reasoning tree."""
        if root_node_id not in self.nodes:
            return 0
        
        def max_depth(node_id: str) -> int:
            if node_id not in self.nodes:
                return 0
            
            node = self.nodes[node_id]
            if not node.children:
                return 1
            
            return 1 + max(max_depth(child_id) for child_id in node.children)
        
        return max_depth(root_node_id)
    
    def export_state(self) -> Dict[str, Any]:
        """Export complete reasoning state."""
        return {
            'nodes': {
                nid: node.to_dict() for nid, node in self.nodes.items()
            },
            'reasoning_paths': [
                path.to_dict() for path in self.reasoning_paths
            ],
            'fractal_patterns': {
                sig: nodes for sig, nodes in self.fractal_patterns.items()
            },
            'max_abstraction_depth': self.max_abstraction_depth,
            'self_similarity_threshold': float(self.self_similarity_threshold)
        }


# Integration interface
def create_fractal_reasoning(
    max_abstraction_depth: int = 5,
    self_similarity_threshold: float = 0.7
) -> FractalReasoning:
    """Factory function for creating fractal reasoning engine."""
    return FractalReasoning(
        max_abstraction_depth=max_abstraction_depth,
        self_similarity_threshold=self_similarity_threshold
    )


def test_fractal_reasoning():
    """Test fractal reasoning engine."""
    engine = create_fractal_reasoning()
    
    # Test 1: Add root node
    root = engine.add_reasoning_node(
        'root',
        'Problem: Optimize system performance',
        scale=ReasoningScale.MACRO,
        abstraction_level=AbstractionLevel.CONCRETE
    )
    assert root.node_id == 'root'
    
    # Test 2: Abstract upward
    abstract = engine.abstract_upward('root')
    assert abstract is not None
    assert abstract.abstraction_level.value > root.abstraction_level.value
    
    # Test 3: Concretize downward
    concretes = engine.concretize_downward('root', num_children=3)
    assert len(concretes) == 3
    assert all(c.abstraction_level.value < root.abstraction_level.value for c in concretes)
    
    # Test 4: Find fractal patterns
    patterns = engine.find_fractal_patterns()
    assert isinstance(patterns, dict)
    
    # Test 5: Calculate fractal dimension
    dimension = engine.calculate_fractal_dimension('root')
    assert dimension > 0
    
    # Test 6: Reason across scales
    path = engine.reason_across_scales('root', ReasoningScale.META)
    # May or may not find path depending on tree structure
    
    # Test 7: Tree depth
    depth = engine.get_tree_depth('root')
    assert depth > 0
    
    # Test 8: Export state
    state = engine.export_state()
    assert 'nodes' in state
    assert 'fractal_patterns' in state
    
    return True


if __name__ == '__main__':
    success = test_fractal_reasoning()
    print(f"Fractal Reasoning Engine test: {'PASSED' if success else 'FAILED'}")
