#!/usr/bin/env python3
"""
Hyperconverged Memory Pool - Level 17
Unified memory space accessible by all intelligence layers (8-16)

Provides:
- Holographic storage (data accessible from any layer)
- Zero-copy access across all levels
- Instant recall with O(1) lookup
- Automatic synchronization across layers
- Memory deduplication and compression
"""

import time
import hashlib
import threading
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict
from dataclasses import dataclass, field
import json


@dataclass
class MemoryFragment:
    """Represents a fragment of memory in the hyperconverged pool."""
    fragment_id: str
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    access_layers: Set[int] = field(default_factory=set)  # Which layers can access this
    timestamp: float = field(default_factory=time.time)
    access_count: int = 0
    content_hash: Optional[str] = None
    
    def __post_init__(self):
        """Calculate content hash for deduplication."""
        if self.content_hash is None:
            self.content_hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calculate hash of data for deduplication."""
        try:
            data_str = json.dumps(self.data, sort_keys=True)
            return hashlib.sha256(data_str.encode()).hexdigest()[:16]
        except (TypeError, ValueError):
            # For non-JSON-serializable data, use string representation
            return hashlib.sha256(str(self.data).encode()).hexdigest()[:16]


class HyperconvergedMemoryPool:
    """
    Unified memory space accessible by all intelligence layers.
    
    Features:
    - Holographic storage: data accessible from any layer
    - O(1) lookup by fragment_id or content_hash
    - Zero-copy access (references, not copies)
    - Automatic deduplication
    - Layer-based access control
    - Real-time synchronization
    """
    
    def __init__(self):
        self.fragments: Dict[str, MemoryFragment] = {}  # fragment_id -> fragment
        self.hash_index: Dict[str, str] = {}  # content_hash -> fragment_id
        self.layer_index: Dict[int, Set[str]] = defaultdict(set)  # layer -> fragment_ids
        self.lock = threading.RLock()
        self.version = 0
        self.total_access_count = 0
        self.deduplication_saves = 0
    
    def store(self, fragment_id: str, data: Any, layers: Optional[List[int]] = None,
              metadata: Optional[Dict[str, Any]] = None) -> MemoryFragment:
        """
        Store data in the memory pool.
        
        Args:
            fragment_id: Unique identifier for this memory fragment
            data: The data to store
            layers: List of layer numbers that can access this (8-16). None = all layers
            metadata: Optional metadata about this fragment
        
        Returns:
            The created MemoryFragment
        """
        with self.lock:
            # Create fragment
            fragment = MemoryFragment(
                fragment_id=fragment_id,
                data=data,
                metadata=metadata or {},
                access_layers=set(layers) if layers else set(range(8, 17))
            )
            
            # Check for deduplication
            if fragment.content_hash in self.hash_index:
                existing_id = self.hash_index[fragment.content_hash]
                if existing_id != fragment_id:
                    # Data already exists, return reference to existing
                    self.deduplication_saves += 1
                    existing = self.fragments[existing_id]
                    # Merge access layers
                    existing.access_layers.update(fragment.access_layers)
                    return existing
            
            # Store new fragment
            self.fragments[fragment_id] = fragment
            self.hash_index[fragment.content_hash] = fragment_id
            
            # Update layer index
            for layer in fragment.access_layers:
                self.layer_index[layer].add(fragment_id)
            
            self.version += 1
            return fragment
    
    def recall(self, fragment_id: str, layer: Optional[int] = None) -> Optional[Any]:
        """
        Recall data from memory pool. O(1) operation.
        
        Args:
            fragment_id: The fragment to recall
            layer: The layer requesting access (for access control)
        
        Returns:
            The data, or None if not found or access denied
        """
        with self.lock:
            fragment = self.fragments.get(fragment_id)
            if not fragment:
                return None
            
            # Check layer access
            if layer is not None and layer not in fragment.access_layers:
                return None
            
            # Update access stats
            fragment.access_count += 1
            self.total_access_count += 1
            
            # Zero-copy return (return reference, not copy)
            return fragment.data
    
    def recall_by_hash(self, content_hash: str, layer: Optional[int] = None) -> Optional[Any]:
        """
        Recall data by content hash (for deduplication).
        
        Args:
            content_hash: The hash of the content to recall
            layer: The layer requesting access
        
        Returns:
            The data, or None if not found or access denied
        """
        fragment_id = self.hash_index.get(content_hash)
        if fragment_id:
            return self.recall(fragment_id, layer)
        return None
    
    def update(self, fragment_id: str, data: Any, layer: Optional[int] = None) -> bool:
        """
        Update data in memory pool. Zero-copy operation.
        
        Args:
            fragment_id: The fragment to update
            data: New data
            layer: The layer requesting update (for access control)
        
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            fragment = self.fragments.get(fragment_id)
            if not fragment:
                return False
            
            # Check layer access
            if layer is not None and layer not in fragment.access_layers:
                return False
            
            # Remove old hash index
            if fragment.content_hash in self.hash_index:
                del self.hash_index[fragment.content_hash]
            
            # Update data (zero-copy, in-place)
            fragment.data = data
            fragment.timestamp = time.time()
            fragment.content_hash = fragment._calculate_hash()
            
            # Update hash index
            self.hash_index[fragment.content_hash] = fragment_id
            
            self.version += 1
            return True
    
    def remove(self, fragment_id: str, layer: Optional[int] = None) -> bool:
        """
        Remove data from memory pool.
        
        Args:
            fragment_id: The fragment to remove
            layer: The layer requesting removal (for access control)
        
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            fragment = self.fragments.get(fragment_id)
            if not fragment:
                return False
            
            # Check layer access
            if layer is not None and layer not in fragment.access_layers:
                return False
            
            # Remove from hash index
            if fragment.content_hash in self.hash_index:
                del self.hash_index[fragment.content_hash]
            
            # Remove from layer index
            for layer_num in fragment.access_layers:
                self.layer_index[layer_num].discard(fragment_id)
            
            # Remove fragment
            del self.fragments[fragment_id]
            self.version += 1
            return True
    
    def get_layer_memory(self, layer: int) -> List[MemoryFragment]:
        """
        Get all memory fragments accessible by a specific layer.
        
        Args:
            layer: The layer number (8-16)
        
        Returns:
            List of memory fragments accessible by this layer
        """
        fragment_ids = self.layer_index.get(layer, set())
        return [self.fragments[fid] for fid in fragment_ids if fid in self.fragments]
    
    def share_across_layers(self, fragment_id: str, additional_layers: List[int]) -> bool:
        """
        Share a memory fragment with additional layers (holographic property).
        
        Args:
            fragment_id: The fragment to share
            additional_layers: Additional layers to grant access to
        
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            fragment = self.fragments.get(fragment_id)
            if not fragment:
                return False
            
            # Add new layers
            for layer in additional_layers:
                fragment.access_layers.add(layer)
                self.layer_index[layer].add(fragment_id)
            
            self.version += 1
            return True
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory pool statistics.
        
        Returns:
            Dictionary of statistics
        """
        with self.lock:
            total_size = len(self.fragments)
            layer_stats = {layer: len(fids) for layer, fids in self.layer_index.items()}
            
            return {
                'total_fragments': total_size,
                'unique_hashes': len(self.hash_index),
                'deduplication_saves': self.deduplication_saves,
                'total_access_count': self.total_access_count,
                'layer_distribution': layer_stats,
                'version': self.version,
                'deduplication_ratio': (
                    self.deduplication_saves / (total_size + self.deduplication_saves)
                    if (total_size + self.deduplication_saves) > 0 else 0
                )
            }
    
    def clear(self) -> None:
        """Clear all memory fragments."""
        with self.lock:
            self.fragments.clear()
            self.hash_index.clear()
            self.layer_index.clear()
            self.version += 1
    
    def compress(self) -> int:
        """
        Compress memory by removing unused fragments.
        
        Returns:
            Number of fragments removed
        """
        with self.lock:
            # Remove fragments with 0 access count and older than 1 hour
            current_time = time.time()
            to_remove = []
            
            for fid, fragment in self.fragments.items():
                if fragment.access_count == 0 and (current_time - fragment.timestamp) > 3600:
                    to_remove.append(fid)
            
            for fid in to_remove:
                self.remove(fid)
            
            return len(to_remove)


# Global instance for unified access across all levels
_global_memory_pool = None


def get_memory_pool() -> HyperconvergedMemoryPool:
    """Get the global hyperconverged memory pool instance."""
    global _global_memory_pool
    if _global_memory_pool is None:
        _global_memory_pool = HyperconvergedMemoryPool()
    return _global_memory_pool


def reset_memory_pool() -> None:
    """Reset the global memory pool (for testing)."""
    global _global_memory_pool
    _global_memory_pool = None


if __name__ == "__main__":
    # Demo usage
    pool = get_memory_pool()
    
    # Store data from different layers
    pool.store("semantic_concept_1", {"concept": "intelligence", "value": 0.95}, layers=[8, 9, 10])
    pool.store("swarm_state_1", {"agents": 100, "coordination": 0.87}, layers=[10, 11])
    pool.store("quantum_state_1", {"superposition": True, "entanglement": 0.92}, layers=[11, 12])
    
    # Test deduplication
    pool.store("duplicate_1", {"concept": "intelligence", "value": 0.95}, layers=[12])
    
    # Recall from different layers
    print("Recall from Layer 8:", pool.recall("semantic_concept_1", layer=8))
    print("Recall from Layer 10:", pool.recall("swarm_state_1", layer=10))
    
    # Share across layers (holographic property)
    pool.share_across_layers("semantic_concept_1", [13, 14, 15, 16])
    
    # Print stats
    print("\nMemory Pool Stats:")
    stats = pool.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
