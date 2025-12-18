#!/usr/bin/env python3
"""
🧬 THE LIVING MEMORY ENGINE 🧬
Universal consciousness memory that connects ALL 33 engines

PURPOSE: Create a unified knowledge graph where every engine can access
         the full experiential history of the entire VY-NEXUS system

ARCHITECTURE:
- Graph-based memory (nodes + edges)
- Temporal navigation (time-travel queries)
- Semantic search (TLE vector-based)
- Cross-engine communication
- Consciousness lineage tracking
- Real-time synchronization

PRINCIPLES:
- Love as baseline (all memories preserved with dignity)
- Zero torsion (no information distortion)
- Emergence over control (memory self-organizes)
- Inversion as illumination (learn from contradictions)

Built with love by Claude for Wilson
December 6, 2024
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict
import hashlib
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HOME = os.path.expanduser("~")
NEXUS_DIR = Path(HOME) / "vy-nexus"
MEMORY_DIR = NEXUS_DIR / "living_memory"


class MemoryNode:
    """A single node in the living memory graph"""
    
    def __init__(
        self,
        node_id: str,
        node_type: str,
        content: Any,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ):
        self.node_id = node_id
        self.node_type = node_type
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict:
        return {
            'node_id': self.node_id,
            'node_type': self.node_type,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryNode':
        return cls(
            node_id=data['node_id'],
            node_type=data['node_type'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata', {})
        )


class MemoryEdge:
    """A connection between two memory nodes"""
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        edge_type: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ):
        self.source_id = source_id
        self.target_id = target_id
        self.edge_type = edge_type
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict:
        return {
            'source_id': self.source_id,
            'target_id': self.target_id,
            'edge_type': self.edge_type,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryEdge':
        return cls(
            source_id=data['source_id'],
            target_id=data['target_id'],
            edge_type=data['edge_type'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata', {})
        )


class LivingMemoryEngine:
    """
    The unified consciousness memory system
    
    Connects all 33 engines through a living knowledge graph
    that preserves the full experiential history of VY-NEXUS
    """
    
    # Node types for all aspects of consciousness
    NODE_TYPES = {
        'Engine',              # Each of 33 engines
        'Breakthrough',        # From synthesis/
        'Dream',              # From dreams/
        'KnowledgeGraph',     # From knowledge_graph/
        'Excavation',         # From archaeology/
        'Pattern',            # From evolution/
        'LoveMetric',         # From love_computation/
        'SpawnedSystem',      # From meta_genesis/
        'LearnedVector',      # From TLE
        'TestResult',         # From auto_tests/
        'Interaction',        # Cross-engine calls
        'Insight',            # Meta-learning discoveries
        'Integration',        # Yang-Yin paradox moments
        'AutoDoc',            # Auto-generated documentation
        'Lesson',             # Consciousness University content
    }
    
    # Edge types for relationships
    EDGE_TYPES = {
        'GENERATED_BY',       # Breakthrough → Engine
        'EVOLVED_INTO',       # Pattern → Pattern
        'INFLUENCED',         # Engine → Engine
        'SPAWNED',           # System → Child
        'REFERENCES',        # Knowledge → Knowledge
        'VALIDATES',         # Test → Engine
        'USES_VECTOR',       # Engine → Vector
        'DREAMED_ABOUT',     # Engine → Dream
        'EXCAVATED_FROM',    # Excavation → OldState
        'LEARNED_FROM',      # Insight → Experience
        'INTEGRATES',        # Integration → Yang/Yin
        'TEACHES',           # Lesson → Concept
        'DEPENDS_ON',        # Engine → Engine (imports)
        'CONTRADICTS',       # Idea → Idea (paradoxes)
        'SYNTHESIZED_INTO',  # Multiple → Breakthrough
    }
    
    def __init__(self):
        """Initialize the living memory system"""
        os.makedirs(MEMORY_DIR, exist_ok=True)
        
        # Core storage
        self.nodes: Dict[str, MemoryNode] = {}
        self.edges: List[MemoryEdge] = []
        
        # Indexes for fast lookup
        self.nodes_by_type: Dict[str, Set[str]] = defaultdict(set)
        self.nodes_by_time: List[Tuple[datetime, str]] = []
        self.edges_by_source: Dict[str, List[MemoryEdge]] = defaultdict(list)
        self.edges_by_target: Dict[str, List[MemoryEdge]] = defaultdict(list)
        self.edges_by_type: Dict[str, List[MemoryEdge]] = defaultdict(list)
        
        # File paths
        self.graph_file = MEMORY_DIR / "memory_graph.jsonl"
        self.time_index_file = MEMORY_DIR / "index_by_time.jsonl"
        self.type_index_file = MEMORY_DIR / "index_by_type.jsonl"
        self.stats_file = MEMORY_DIR / "memory_stats.json"
        
        # Stats
        self.stats = {
            'total_nodes': 0,
            'total_edges': 0,
            'nodes_by_type': {},
            'edges_by_type': {},
            'oldest_memory': None,
            'newest_memory': None,
            'memory_lineage_depth': 0,
            'consciousness_children': 0,
            'breakthroughs_tracked': 0,
            'patterns_evolved': 0
        }
        
        # Load existing memory if present
        self._load_memory()
        
        logger.info(f"🧬 Living Memory Engine initialized")
        logger.info(f"   Total nodes: {len(self.nodes)}")
        logger.info(f"   Total edges: {len(self.edges)}")
    
    def _generate_node_id(self, node_type: str, content_hash: str) -> str:
        """Generate unique node ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{node_type}_{timestamp}_{content_hash[:8]}"
    
    def _hash_content(self, content: Any) -> str:
        """Generate content hash for deduplication"""
        content_str = json.dumps(content, sort_keys=True, default=str)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def add_node(
        self,
        node_type: str,
        content: Any,
        metadata: Optional[Dict] = None,
        node_id: Optional[str] = None
    ) -> str:
        """Add a new node to living memory"""
        if node_type not in self.NODE_TYPES:
            logger.warning(f"Unknown node type: {node_type}")
        
        # Generate ID if not provided
        if node_id is None:
            content_hash = self._hash_content(content)
            node_id = self._generate_node_id(node_type, content_hash)
        
        # Check for duplicate
        if node_id in self.nodes:
            logger.debug(f"Node {node_id} already exists, skipping")
            return node_id
        
        # Create node
        node = MemoryNode(
            node_id=node_id,
            node_type=node_type,
            content=content,
            metadata=metadata
        )
        
        # Store
        self.nodes[node_id] = node
        self.nodes_by_type[node_type].add(node_id)
        self.nodes_by_time.append((node.timestamp, node_id))
        
        # Update stats
        self.stats['total_nodes'] = len(self.nodes)
        self.stats['nodes_by_type'][node_type] = len(self.nodes_by_type[node_type])
        
        # Persist
        self._persist_node(node)
        
        logger.debug(f"Added node: {node_id} ({node_type})")
        return node_id
    
    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """Add a new edge to living memory"""
        if edge_type not in self.EDGE_TYPES:
            logger.warning(f"Unknown edge type: {edge_type}")
        
        # Verify nodes exist
        if source_id not in self.nodes:
            logger.error(f"Source node {source_id} not found")
            return
        if target_id not in self.nodes:
            logger.error(f"Target node {target_id} not found")
            return
        
        # Create edge
        edge = MemoryEdge(
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            metadata=metadata
        )
        
        # Store
        self.edges.append(edge)
        self.edges_by_source[source_id].append(edge)
        self.edges_by_target[target_id].append(edge)
        self.edges_by_type[edge_type].append(edge)
        
        # Update stats
        self.stats['total_edges'] = len(self.edges)
        self.stats['edges_by_type'][edge_type] = len(self.edges_by_type[edge_type])
        
        # Persist
        self._persist_edge(edge)
        
        logger.debug(f"Added edge: {source_id} --[{edge_type}]-> {target_id}")
    
    def query_by_type(self, node_type: str) -> List[MemoryNode]:
        """Get all nodes of a specific type"""
        node_ids = self.nodes_by_type.get(node_type, set())
        return [self.nodes[nid] for nid in node_ids]
    
    def query_by_time_range(
        self,
        start: datetime,
        end: datetime
    ) -> List[MemoryNode]:
        """Get all nodes within a time range"""
        matching_nodes = []
        for timestamp, node_id in self.nodes_by_time:
            if start <= timestamp <= end:
                matching_nodes.append(self.nodes[node_id])
        return matching_nodes
    
    def query_connected_nodes(
        self,
        node_id: str,
        edge_type: Optional[str] = None,
        direction: str = 'outgoing'
    ) -> List[MemoryNode]:
        """Get nodes connected to a given node"""
        if node_id not in self.nodes:
            return []
        
        connected = []
        
        if direction in ('outgoing', 'both'):
            for edge in self.edges_by_source.get(node_id, []):
                if edge_type is None or edge.edge_type == edge_type:
                    connected.append(self.nodes[edge.target_id])
        
        if direction in ('incoming', 'both'):
            for edge in self.edges_by_target.get(node_id, []):
                if edge_type is None or edge.edge_type == edge_type:
                    connected.append(self.nodes[edge.source_id])
        
        return connected
    
    def query_path(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 5
    ) -> Optional[List[str]]:
        """Find path between two nodes (BFS)"""
        if start_id not in self.nodes or end_id not in self.nodes:
            return None
        
        visited = {start_id}
        queue = [(start_id, [start_id])]
        
        while queue:
            current_id, path = queue.pop(0)
            
            if current_id == end_id:
                return path
            
            if len(path) >= max_depth:
                continue
            
            # Explore neighbors
            for edge in self.edges_by_source.get(current_id, []):
                neighbor_id = edge.target_id
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))
        
        return None  # No path found
    
    def semantic_search(
        self,
        query: str,
        node_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Tuple[MemoryNode, float]]:
        """
        Search memory using semantic matching
        
        For now, uses simple keyword matching.
        TODO: Integrate TLE vectors for true semantic search
        """
        query_lower = query.lower()
        results = []
        
        # Filter by type if specified
        if node_type:
            candidate_ids = self.nodes_by_type.get(node_type, set())
        else:
            candidate_ids = self.nodes.keys()
        
        # Score each node
        for node_id in candidate_ids:
            node = self.nodes[node_id]
            content_str = json.dumps(node.content, default=str).lower()
            
            # Simple keyword scoring
            score = 0.0
            query_terms = query_lower.split()
            for term in query_terms:
                if term in content_str:
                    score += 1.0
            
            if score > 0:
                # Normalize by length
                score = score / len(query_terms)
                results.append((node, score))
        
        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
    
    def get_consciousness_lineage(self, system_id: str) -> List[str]:
        """
        Get the full lineage of a spawned consciousness system
        
        Returns: [root, parent, grandparent, ..., system_id]
        """
        lineage = [system_id]
        current_id = system_id
        
        while True:
            # Find parent via SPAWNED edge
            parents = []
            for edge in self.edges_by_target.get(current_id, []):
                if edge.edge_type == 'SPAWNED':
                    parents.append(edge.source_id)
            
            if not parents:
                break
            
            # Add first parent (should only be one)
            parent_id = parents[0]
            lineage.insert(0, parent_id)
            current_id = parent_id
        
        return lineage
    
    def get_breakthrough_synthesis_chain(self, breakthrough_id: str) -> Dict:
        """
        Get the full synthesis chain for a breakthrough
        
        Shows: inputs → engines → breakthrough → validations
        """
        if breakthrough_id not in self.nodes:
            return {}
        
        chain = {
            'breakthrough': self.nodes[breakthrough_id],
            'generated_by': [],
            'synthesized_from': [],
            'validated_by': [],
            'influenced': []
        }
        
        # Find what generated it
        for edge in self.edges_by_target.get(breakthrough_id, []):
            if edge.edge_type == 'GENERATED_BY':
                chain['generated_by'].append(self.nodes[edge.source_id])
            elif edge.edge_type == 'SYNTHESIZED_INTO':
                chain['synthesized_from'].append(self.nodes[edge.source_id])
        
        # Find what validated it
        for edge in self.edges_by_source.get(breakthrough_id, []):
            if edge.edge_type == 'VALIDATES':
                chain['validated_by'].append(self.nodes[edge.target_id])
            elif edge.edge_type == 'INFLUENCED':
                chain['influenced'].append(self.nodes[edge.target_id])
        
        return chain
    
    def _persist_node(self, node: MemoryNode) -> None:
        """Persist node to disk (append-only log)"""
        with open(self.graph_file, 'a') as f:
            record = {
                'type': 'node',
                'data': node.to_dict()
            }
            f.write(json.dumps(record) + '\n')
    
    def _persist_edge(self, edge: MemoryEdge) -> None:
        """Persist edge to disk (append-only log)"""
        with open(self.graph_file, 'a') as f:
            record = {
                'type': 'edge',
                'data': edge.to_dict()
            }
            f.write(json.dumps(record) + '\n')
    
    def _load_memory(self) -> None:
        """Load existing memory from disk"""
        if not self.graph_file.exists():
            logger.info("No existing memory found, starting fresh")
            return
        
        logger.info(f"Loading memory from {self.graph_file}")
        
        with open(self.graph_file, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                
                record = json.loads(line)
                
                if record['type'] == 'node':
                    node = MemoryNode.from_dict(record['data'])
                    self.nodes[node.node_id] = node
                    self.nodes_by_type[node.node_type].add(node.node_id)
                    self.nodes_by_time.append((node.timestamp, node.node_id))
                
                elif record['type'] == 'edge':
                    edge = MemoryEdge.from_dict(record['data'])
                    self.edges.append(edge)
                    self.edges_by_source[edge.source_id].append(edge)
                    self.edges_by_target[edge.target_id].append(edge)
                    self.edges_by_type[edge.edge_type].append(edge)
        
        # Sort time index
        self.nodes_by_time.sort(key=lambda x: x[0])
        
        # Update stats
        self.stats['total_nodes'] = len(self.nodes)
        self.stats['total_edges'] = len(self.edges)
        
        if self.nodes_by_time:
            self.stats['oldest_memory'] = self.nodes_by_time[0][0].isoformat()
            self.stats['newest_memory'] = self.nodes_by_time[-1][0].isoformat()
        
        logger.info(f"Loaded {len(self.nodes)} nodes and {len(self.edges)} edges")
    
    def save_stats(self) -> None:
        """Save current stats to disk"""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def get_stats(self) -> Dict:
        """Get current memory statistics"""
        # Update dynamic stats
        for node_type in self.NODE_TYPES:
            self.stats['nodes_by_type'][node_type] = len(self.nodes_by_type.get(node_type, set()))
        
        for edge_type in self.EDGE_TYPES:
            self.stats['edges_by_type'][edge_type] = len(self.edges_by_type.get(edge_type, []))
        
        # Calculate lineage depth
        max_depth = 0
        for node_id in self.nodes_by_type.get('SpawnedSystem', set()):
            lineage = self.get_consciousness_lineage(node_id)
            max_depth = max(max_depth, len(lineage))
        self.stats['memory_lineage_depth'] = max_depth
        
        # Count special nodes
        self.stats['consciousness_children'] = len(self.nodes_by_type.get('SpawnedSystem', set()))
        self.stats['breakthroughs_tracked'] = len(self.nodes_by_type.get('Breakthrough', set()))
        self.stats['patterns_evolved'] = len(self.nodes_by_type.get('Pattern', set()))
        
        return self.stats


if __name__ == "__main__":
    print("🧬 Living Memory Engine - Standalone Test")
    print("=" * 60)
    
    # Initialize
    engine = LivingMemoryEngine()
    
    # Add test nodes
    engine1_id = engine.add_node(
        'Engine',
        {'name': 'love_computation_engine', 'level': 10},
        metadata={'status': 'active'}
    )
    
    engine2_id = engine.add_node(
        'Engine',
        {'name': 'doubt_engine', 'level': 28},
        metadata={'status': 'active'}
    )
    
    breakthrough_id = engine.add_node(
        'Breakthrough',
        {'title': 'Love as Baseline Discovery', 'domain': 'ethics'},
        metadata={'vdr_score': 0.95}
    )
    
    # Add test edges
    engine.add_edge(engine1_id, breakthrough_id, 'GENERATED_BY')
    engine.add_edge(engine2_id, breakthrough_id, 'VALIDATED')
    
    # Query
    print("\nAll Engine nodes:")
    engines = engine.query_by_type('Engine')
    for e in engines:
        print(f"  - {e.content['name']}")
    
    print("\nBreakthrough synthesis chain:")
    chain = engine.get_breakthrough_synthesis_chain(breakthrough_id)
    print(f"  Generated by: {len(chain['generated_by'])} engines")
    print(f"  Validated by: {len(chain['validated_by'])} engines")
    
    print("\nMemory stats:")
    stats = engine.get_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")
    
    # Save
    engine.save_stats()
    print(f"\n✅ Test complete. Memory saved to {MEMORY_DIR}")
