#!/usr/bin/env python3
"""
Distributed Memory Architecture - New Build 6, Phase 2
Shared memory systems, distributed knowledge graphs, and memory synchronization
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import hashlib
from collections import defaultdict
from queue import Queue


class MemoryType(Enum):
    """Types of memory storage"""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


class SyncStrategy(Enum):
    """Memory synchronization strategies"""
    IMMEDIATE = "immediate"  # Sync immediately on write
    PERIODIC = "periodic"    # Sync at regular intervals
    ON_DEMAND = "on_demand"  # Sync only when requested
    EVENTUAL = "eventual"    # Eventually consistent


@dataclass
class MemoryEntry:
    """Represents a single memory entry"""
    key: str
    value: Any
    memory_type: MemoryType
    timestamp: float = field(default_factory=time.time)
    node_id: str = "default"
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'key': self.key,
            'value': self.value,
            'memory_type': self.memory_type.value,
            'timestamp': self.timestamp,
            'node_id': self.node_id,
            'version': self.version,
            'metadata': self.metadata
        }
    
    def get_hash(self) -> str:
        """Generate hash for conflict detection"""
        content = f"{self.key}:{self.value}:{self.version}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class KnowledgeNode:
    """Node in distributed knowledge graph"""
    node_id: str
    node_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    edges: List[str] = field(default_factory=list)  # Connected node IDs
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'node_id': self.node_id,
            'node_type': self.node_type,
            'properties': self.properties,
            'edges': self.edges,
            'timestamp': self.timestamp
        }


class SharedMemorySystem:
    """Shared memory system for distributed agents"""
    
    def __init__(self, node_id: str = "node_0"):
        self.node_id = node_id
        self.memory: Dict[str, MemoryEntry] = {}
        self.lock = threading.Lock()
        self.sync_log: List[Dict[str, Any]] = []
        
    def write(self, key: str, value: Any, memory_type: MemoryType = MemoryType.WORKING) -> bool:
        """Write to shared memory"""
        with self.lock:
            if key in self.memory:
                # Update existing entry
                entry = self.memory[key]
                entry.value = value
                entry.version += 1
                entry.timestamp = time.time()
            else:
                # Create new entry
                entry = MemoryEntry(
                    key=key,
                    value=value,
                    memory_type=memory_type,
                    node_id=self.node_id
                )
                self.memory[key] = entry
            
            self.sync_log.append({
                'action': 'write',
                'key': key,
                'timestamp': time.time(),
                'node_id': self.node_id
            })
            return True
    
    def read(self, key: str) -> Optional[Any]:
        """Read from shared memory"""
        with self.lock:
            if key in self.memory:
                self.sync_log.append({
                    'action': 'read',
                    'key': key,
                    'timestamp': time.time(),
                    'node_id': self.node_id
                })
                return self.memory[key].value
            return None
    
    def delete(self, key: str) -> bool:
        """Delete from shared memory"""
        with self.lock:
            if key in self.memory:
                del self.memory[key]
                self.sync_log.append({
                    'action': 'delete',
                    'key': key,
                    'timestamp': time.time(),
                    'node_id': self.node_id
                })
                return True
            return False
    
    def get_all(self, memory_type: Optional[MemoryType] = None) -> Dict[str, Any]:
        """Get all memory entries, optionally filtered by type"""
        with self.lock:
            if memory_type:
                return {
                    k: v.value for k, v in self.memory.items()
                    if v.memory_type == memory_type
                }
            return {k: v.value for k, v in self.memory.items()}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        with self.lock:
            type_counts = defaultdict(int)
            for entry in self.memory.values():
                type_counts[entry.memory_type.value] += 1
            
            return {
                'node_id': self.node_id,
                'total_entries': len(self.memory),
                'type_counts': dict(type_counts),
                'sync_operations': len(self.sync_log)
            }


class DistributedKnowledgeGraph:
    """Distributed knowledge graph for multi-node systems"""
    
    def __init__(self, node_id: str = "node_0"):
        self.node_id = node_id
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.lock = threading.Lock()
        
    def add_node(self, node_id: str, node_type: str, properties: Optional[Dict[str, Any]] = None) -> bool:
        """Add a node to the knowledge graph"""
        with self.lock:
            if node_id not in self.nodes:
                self.nodes[node_id] = KnowledgeNode(
                    node_id=node_id,
                    node_type=node_type,
                    properties=properties or {}
                )
                return True
            return False
    
    def add_edge(self, from_node: str, to_node: str) -> bool:
        """Add an edge between two nodes"""
        with self.lock:
            if from_node in self.nodes and to_node in self.nodes:
                if to_node not in self.nodes[from_node].edges:
                    self.nodes[from_node].edges.append(to_node)
                return True
            return False
    
    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Get a node from the graph"""
        with self.lock:
            return self.nodes.get(node_id)
    
    def get_neighbors(self, node_id: str) -> List[str]:
        """Get all neighbors of a node"""
        with self.lock:
            if node_id in self.nodes:
                return self.nodes[node_id].edges.copy()
            return []
    
    def query(self, node_type: Optional[str] = None, properties: Optional[Dict[str, Any]] = None) -> List[KnowledgeNode]:
        """Query nodes by type and/or properties"""
        with self.lock:
            results = []
            for node in self.nodes.values():
                # Filter by type
                if node_type and node.node_type != node_type:
                    continue
                
                # Filter by properties
                if properties:
                    match = all(
                        node.properties.get(k) == v
                        for k, v in properties.items()
                    )
                    if not match:
                        continue
                
                results.append(node)
            return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        with self.lock:
            type_counts = defaultdict(int)
            total_edges = 0
            for node in self.nodes.values():
                type_counts[node.node_type] += 1
                total_edges += len(node.edges)
            
            return {
                'node_id': self.node_id,
                'total_nodes': len(self.nodes),
                'total_edges': total_edges,
                'type_counts': dict(type_counts)
            }


class MemorySynchronizer:
    """Synchronizes memory across distributed nodes"""
    
    def __init__(self, strategy: SyncStrategy = SyncStrategy.EVENTUAL):
        self.strategy = strategy
        self.sync_queue: Queue = Queue()
        self.sync_history: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        
    def sync(self, source: SharedMemorySystem, target: SharedMemorySystem) -> Dict[str, Any]:
        """Synchronize memory from source to target"""
        with self.lock:
            synced_keys = []
            conflicts = []
            
            # Get all entries from source
            source_entries = source.memory.copy()
            
            for key, entry in source_entries.items():
                target_entry = target.memory.get(key)
                
                if target_entry is None:
                    # New entry - copy to target
                    target.write(key, entry.value, entry.memory_type)
                    synced_keys.append(key)
                elif target_entry.version < entry.version:
                    # Source is newer - update target
                    target.write(key, entry.value, entry.memory_type)
                    synced_keys.append(key)
                elif target_entry.version > entry.version:
                    # Target is newer - conflict
                    conflicts.append({
                        'key': key,
                        'source_version': entry.version,
                        'target_version': target_entry.version
                    })
            
            sync_result = {
                'strategy': self.strategy.value,
                'synced_keys': synced_keys,
                'conflicts': conflicts,
                'timestamp': time.time()
            }
            
            self.sync_history.append(sync_result)
            return sync_result
    
    def resolve_conflicts(self, conflicts: List[Dict[str, Any]], resolution: str = "latest") -> List[str]:
        """Resolve synchronization conflicts"""
        resolved = []
        for conflict in conflicts:
            if resolution == "latest":
                # Use the entry with the latest timestamp
                resolved.append(conflict['key'])
            elif resolution == "source":
                # Always prefer source
                resolved.append(conflict['key'])
            elif resolution == "target":
                # Always prefer target
                pass  # Do nothing
        return resolved
    
    def get_stats(self) -> Dict[str, Any]:
        """Get synchronization statistics"""
        with self.lock:
            total_syncs = len(self.sync_history)
            total_conflicts = sum(len(s['conflicts']) for s in self.sync_history)
            
            return {
                'strategy': self.strategy.value,
                'total_syncs': total_syncs,
                'total_conflicts': total_conflicts
            }


class DistributedMemory:
    """Main distributed memory architecture"""
    
    def __init__(self, node_id: str = "node_0", sync_strategy: SyncStrategy = SyncStrategy.EVENTUAL):
        self.node_id = node_id
        self.shared_memory = SharedMemorySystem(node_id)
        self.knowledge_graph = DistributedKnowledgeGraph(node_id)
        self.synchronizer = MemorySynchronizer(sync_strategy)
        
    def write_memory(self, key: str, value: Any, memory_type: MemoryType = MemoryType.WORKING) -> bool:
        """Write to distributed memory"""
        return self.shared_memory.write(key, value, memory_type)
    
    def read_memory(self, key: str) -> Optional[Any]:
        """Read from distributed memory"""
        return self.shared_memory.read(key)
    
    def add_knowledge(self, node_id: str, node_type: str, properties: Optional[Dict[str, Any]] = None) -> bool:
        """Add knowledge to distributed graph"""
        return self.knowledge_graph.add_node(node_id, node_type, properties)
    
    def link_knowledge(self, from_node: str, to_node: str) -> bool:
        """Link knowledge nodes"""
        return self.knowledge_graph.add_edge(from_node, to_node)
    
    def query_knowledge(self, node_type: Optional[str] = None, properties: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Query knowledge graph"""
        nodes = self.knowledge_graph.query(node_type, properties)
        return [node.to_dict() for node in nodes]
    
    def sync_with(self, other: 'DistributedMemory') -> Dict[str, Any]:
        """Synchronize with another distributed memory instance"""
        return self.synchronizer.sync(self.shared_memory, other.shared_memory)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        return {
            'node_id': self.node_id,
            'memory': self.shared_memory.get_stats(),
            'knowledge_graph': self.knowledge_graph.get_stats(),
            'synchronizer': self.synchronizer.get_stats()
        }
    
    def demo(self) -> Dict[str, Any]:
        """Demonstrate distributed memory capabilities"""
        print("\n=== Distributed Memory Architecture Demo ===")
        
        # 1. Write to shared memory
        print("\n1. Writing to shared memory...")
        self.write_memory("task_1", {"status": "completed", "result": 42}, MemoryType.WORKING)
        self.write_memory("task_2", {"status": "pending"}, MemoryType.SHORT_TERM)
        self.write_memory("knowledge_1", {"fact": "AI is transformative"}, MemoryType.SEMANTIC)
        print(f"   Written 3 entries to memory")
        
        # 2. Read from memory
        print("\n2. Reading from memory...")
        task_1 = self.read_memory("task_1")
        print(f"   task_1: {task_1}")
        
        # 3. Add knowledge nodes
        print("\n3. Building knowledge graph...")
        self.add_knowledge("concept_1", "concept", {"name": "Machine Learning"})
        self.add_knowledge("concept_2", "concept", {"name": "Deep Learning"})
        self.add_knowledge("concept_3", "concept", {"name": "Neural Networks"})
        self.link_knowledge("concept_1", "concept_2")
        self.link_knowledge("concept_2", "concept_3")
        print(f"   Added 3 nodes and 2 edges")
        
        # 4. Query knowledge
        print("\n4. Querying knowledge graph...")
        concepts = self.query_knowledge(node_type="concept")
        print(f"   Found {len(concepts)} concept nodes")
        
        # 5. Create second node and sync
        print("\n5. Testing synchronization...")
        node_2 = DistributedMemory("node_1", SyncStrategy.IMMEDIATE)
        node_2.write_memory("task_3", {"status": "running"}, MemoryType.WORKING)
        sync_result = self.sync_with(node_2)
        print(f"   Synced {len(sync_result['synced_keys'])} keys")
        print(f"   Conflicts: {len(sync_result['conflicts'])}")
        
        # 6. Get statistics
        print("\n6. System statistics:")
        stats = self.get_stats()
        print(f"   Memory entries: {stats['memory']['total_entries']}")
        print(f"   Knowledge nodes: {stats['knowledge_graph']['total_nodes']}")
        print(f"   Knowledge edges: {stats['knowledge_graph']['total_edges']}")
        print(f"   Sync operations: {stats['synchronizer']['total_syncs']}")
        
        print("\n=== Demo Complete ===")
        return stats


class DistributedMemoryContract:
    """Contract interface for testing"""
    
    @staticmethod
    def create() -> DistributedMemory:
        """Create a distributed memory instance"""
        return DistributedMemory()
    
    @staticmethod
    def verify() -> bool:
        """Verify distributed memory functionality"""
        dm = DistributedMemory()
        
        # Test memory operations
        dm.write_memory("test_key", "test_value")
        value = dm.read_memory("test_key")
        if value != "test_value":
            return False
        
        # Test knowledge graph
        dm.add_knowledge("node_1", "test_type")
        dm.add_knowledge("node_2", "test_type")
        dm.link_knowledge("node_1", "node_2")
        nodes = dm.query_knowledge(node_type="test_type")
        if len(nodes) != 2:
            return False
        
        # Test synchronization
        dm2 = DistributedMemory("node_1")
        dm2.write_memory("sync_test", "sync_value")
        sync_result = dm.sync_with(dm2)
        if "synced_keys" not in sync_result:
            return False
        
        return True


if __name__ == "__main__":
    # Run demo
    dm = DistributedMemory()
    dm.demo()
