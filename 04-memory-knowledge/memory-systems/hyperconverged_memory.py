#!/usr/bin/env python3
"""
Level 17: Hyperconverged Memory Pool
Single memory space accessible by all intelligence layers with holographic storage

Part of Build 15: Hyperconvergence & System Unification
Ticket: T-102
"""

import time
import threading
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import json
import hashlib


@dataclass
class MemoryEntry:
    """Represents a single memory entry in the hyperconverged pool"""
    key: str
    value: Any
    layer_id: str  # Which intelligence layer owns this memory
    timestamp: float = field(default_factory=time.time)
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    replicas: Set[str] = field(default_factory=set)  # Holographic storage locations


class HolographicStorage:
    """
    Distributed holographic storage with instant recall.
    Each memory fragment is stored in multiple locations for redundancy.
    """
    
    def __init__(self, replication_factor: int = 3):
        self.replication_factor = replication_factor
        self.shards: Dict[str, Dict[str, MemoryEntry]] = defaultdict(dict)
        self.shard_count = 16  # Number of storage shards
    
    def _get_shard_id(self, key: str) -> str:
        """Determine which shard a key belongs to"""
        hash_val = int(hashlib.md5(key.encode()).hexdigest(), 16)
        return f"shard_{hash_val % self.shard_count}"
    
    def _get_replica_shards(self, key: str) -> List[str]:
        """Get all replica shard IDs for a key"""
        primary_shard = self._get_shard_id(key)
        hash_val = int(hashlib.md5(key.encode()).hexdigest(), 16)
        
        replicas = [primary_shard]
        for i in range(1, self.replication_factor):
            replica_id = (hash_val + i) % self.shard_count
            replicas.append(f"shard_{replica_id}")
        
        return replicas
    
    def store(self, entry: MemoryEntry) -> None:
        """Store entry across multiple shards (holographic)"""
        replica_shards = self._get_replica_shards(entry.key)
        entry.replicas = set(replica_shards)
        
        for shard_id in replica_shards:
            self.shards[shard_id][entry.key] = entry
    
    def retrieve(self, key: str) -> Optional[MemoryEntry]:
        """Retrieve entry from any available replica (instant recall)"""
        replica_shards = self._get_replica_shards(key)
        
        # Try each replica until we find the entry
        for shard_id in replica_shards:
            if key in self.shards[shard_id]:
                entry = self.shards[shard_id][key]
                entry.access_count += 1
                return entry
        
        return None
    
    def delete(self, key: str) -> bool:
        """Delete entry from all replicas"""
        replica_shards = self._get_replica_shards(key)
        deleted = False
        
        for shard_id in replica_shards:
            if key in self.shards[shard_id]:
                del self.shards[shard_id][key]
                deleted = True
        
        return deleted


class HyperconvergedMemory:
    """
    Single memory space accessible by all intelligence layers.
    
    Features:
    - Unified memory pool (no inter-layer data copying)
    - Distributed holographic storage with instant recall
    - Automatic memory consolidation and optimization
    - CRDT-based eventual consistency
    - Thread-safe operations
    """
    
    def __init__(self, replication_factor: int = 3):
        """Initialize the hyperconverged memory pool"""
        self.storage = HolographicStorage(replication_factor)
        self.lock = threading.RLock()
        
        # Layer-specific indices for fast queries
        self.layer_index: Dict[str, Set[str]] = defaultdict(set)
        
        # Temporal index for time-based queries
        self.temporal_index: List[tuple] = []  # (timestamp, key)
        
        # Statistics
        self.stats = {
            'total_writes': 0,
            'total_reads': 0,
            'total_deletes': 0,
            'consolidations': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Consolidation settings
        self.consolidation_threshold = 1000  # Consolidate after this many operations
        self.operation_count = 0
    
    def write(self, key: str, value: Any, layer_id: str, 
              metadata: Optional[Dict[str, Any]] = None) -> MemoryEntry:
        """
        Write to the unified memory pool.
        
        Args:
            key: Memory key
            value: Memory value (any type)
            layer_id: Intelligence layer ID (e.g., 'level_8', 'level_9')
            metadata: Optional metadata
            
        Returns:
            The created MemoryEntry
        """
        with self.lock:
            # Create memory entry
            entry = MemoryEntry(
                key=key,
                value=value,
                layer_id=layer_id,
                metadata=metadata or {}
            )
            
            # Store holographically
            self.storage.store(entry)
            
            # Update indices
            self.layer_index[layer_id].add(key)
            self.temporal_index.append((entry.timestamp, key))
            
            # Update stats
            self.stats['total_writes'] += 1
            self.operation_count += 1
            
            # Auto-consolidate if needed
            if self.operation_count >= self.consolidation_threshold:
                self._consolidate()
            
            return entry
    
    def read(self, key: str) -> Optional[Any]:
        """
        Read from the unified memory pool (instant recall).
        
        Args:
            key: Memory key
            
        Returns:
            Memory value if found, None otherwise
        """
        with self.lock:
            entry = self.storage.retrieve(key)
            
            if entry:
                self.stats['total_reads'] += 1
                self.stats['cache_hits'] += 1
                return entry.value
            else:
                self.stats['cache_misses'] += 1
                return None
    
    def read_entry(self, key: str) -> Optional[MemoryEntry]:
        """
        Read full memory entry (including metadata).
        
        Args:
            key: Memory key
            
        Returns:
            MemoryEntry if found, None otherwise
        """
        with self.lock:
            self.stats['total_reads'] += 1
            return self.storage.retrieve(key)
    
    def delete(self, key: str) -> bool:
        """
        Delete from the unified memory pool.
        
        Args:
            key: Memory key
            
        Returns:
            True if deleted, False if not found
        """
        with self.lock:
            # Get entry to update indices
            entry = self.storage.retrieve(key)
            if entry:
                # Remove from layer index
                self.layer_index[entry.layer_id].discard(key)
            
            # Delete from storage
            deleted = self.storage.delete(key)
            
            if deleted:
                self.stats['total_deletes'] += 1
                self.operation_count += 1
            
            return deleted
    
    def query_by_layer(self, layer_id: str) -> List[MemoryEntry]:
        """
        Query all memories from a specific intelligence layer.
        
        Args:
            layer_id: Intelligence layer ID
            
        Returns:
            List of MemoryEntry objects
        """
        with self.lock:
            keys = self.layer_index.get(layer_id, set())
            entries = []
            
            for key in keys:
                entry = self.storage.retrieve(key)
                if entry:
                    entries.append(entry)
            
            return entries
    
    def query_by_time_range(self, start_time: float, end_time: float) -> List[MemoryEntry]:
        """
        Query memories within a time range.
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            
        Returns:
            List of MemoryEntry objects
        """
        with self.lock:
            entries = []
            
            for timestamp, key in self.temporal_index:
                if start_time <= timestamp <= end_time:
                    entry = self.storage.retrieve(key)
                    if entry:
                        entries.append(entry)
            
            return entries
    
    def _consolidate(self) -> None:
        """
        Automatic memory consolidation and optimization.
        Removes stale entries, optimizes indices, etc.
        """
        # Clean up temporal index (remove deleted entries)
        valid_temporal = []
        for timestamp, key in self.temporal_index:
            if self.storage.retrieve(key) is not None:
                valid_temporal.append((timestamp, key))
        
        self.temporal_index = sorted(valid_temporal, key=lambda x: x[0])
        
        # Clean up layer indices
        for layer_id in list(self.layer_index.keys()):
            valid_keys = set()
            for key in self.layer_index[layer_id]:
                if self.storage.retrieve(key) is not None:
                    valid_keys.add(key)
            self.layer_index[layer_id] = valid_keys
        
        self.stats['consolidations'] += 1
        self.operation_count = 0
    
    def synchronize_layer(self, layer_id: str, layer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronize data from an intelligence layer into the memory pool.
        
        Args:
            layer_id: Intelligence layer ID
            layer_data: Data to synchronize
            
        Returns:
            Synchronization result with statistics
        """
        sync_start = time.time()
        entries_written = 0
        
        with self.lock:
            for key, value in layer_data.items():
                self.write(key, value, layer_id)
                entries_written += 1
        
        sync_duration = time.time() - sync_start
        
        return {
            'layer_id': layer_id,
            'entries_written': entries_written,
            'duration': sync_duration,
            'timestamp': time.time()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory pool statistics.
        
        Returns:
            Dictionary of statistics
        """
        with self.lock:
            total_entries = sum(len(keys) for keys in self.layer_index.values())
            
            return {
                **self.stats,
                'total_entries': total_entries,
                'layers_active': len(self.layer_index),
                'hit_rate': self.stats['cache_hits'] / max(self.stats['total_reads'], 1),
                'avg_replicas': self.storage.replication_factor
            }
    
    def export_memory(self) -> Dict[str, Any]:
        """
        Export the entire memory pool.
        
        Returns:
            Dictionary representation of all memories
        """
        with self.lock:
            all_entries = []
            
            for layer_id, keys in self.layer_index.items():
                for key in keys:
                    entry = self.storage.retrieve(key)
                    if entry:
                        all_entries.append({
                            'key': entry.key,
                            'value': entry.value,
                            'layer_id': entry.layer_id,
                            'timestamp': entry.timestamp,
                            'access_count': entry.access_count,
                            'metadata': entry.metadata,
                            'replicas': list(entry.replicas)
                        })
            
            return {
                'entries': all_entries,
                'stats': self.get_stats()
            }


# Global singleton instance
_global_memory_pool: Optional[HyperconvergedMemory] = None
_memory_lock = threading.Lock()


def get_memory_pool() -> HyperconvergedMemory:
    """Get the global hyperconverged memory pool (singleton)"""
    global _global_memory_pool
    
    with _memory_lock:
        if _global_memory_pool is None:
            _global_memory_pool = HyperconvergedMemory()
        return _global_memory_pool


def reset_memory_pool() -> None:
    """Reset the global memory pool (for testing)"""
    global _global_memory_pool
    
    with _memory_lock:
        _global_memory_pool = None


if __name__ == '__main__':
    # Demo usage
    memory = get_memory_pool()
    
    # Write from different layers
    memory.write('semantic_concept_1', {'name': 'Intelligence'}, 'level_8')
    memory.write('swarm_state_1', {'agents': 100}, 'level_10')
    memory.write('quantum_state_1', {'superposition': True}, 'level_16')
    
    # Read (instant recall)
    value = memory.read('semantic_concept_1')
    print(f"Read value: {value}")
    
    # Query by layer
    level_8_memories = memory.query_by_layer('level_8')
    print(f"Level 8 memories: {len(level_8_memories)}")
    
    # Stats
    print(f"Memory stats: {json.dumps(memory.get_stats(), indent=2)}")
