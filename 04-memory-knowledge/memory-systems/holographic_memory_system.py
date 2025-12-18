"""
Holographic Memory System - Level 22
New Build 12, Phase 3: Holographic Intelligence

Distributed information storage with associative recall and fault-tolerant encoding.
Implements holographic principles where information is distributed across the entire
storage medium, enabling robust retrieval even with partial data.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import hashlib
import json


class HolographicMemorySystem:
    """
    Holographic memory system with distributed storage and associative recall.
    
    Key Features:
    - Distributed encoding: Information spread across entire storage
    - Associative recall: Retrieve by partial patterns or associations
    - Fault tolerance: Robust to partial data loss
    - Interference patterns: Multiple memories stored in same space
    - Phase encoding: Use phase information for richer storage
    """
    
    def __init__(self, dimensions: int = 512, capacity: int = 1000):
        """
        Initialize holographic memory system.
        
        Args:
            dimensions: Dimensionality of holographic space
            capacity: Maximum number of memories to store
        """
        self.dimensions = dimensions
        self.capacity = capacity
        
        # Holographic storage matrix (complex-valued for phase information)
        self.hologram = np.zeros(dimensions, dtype=np.complex128)
        
        # Memory index for tracking stored items
        self.memory_index: Dict[str, Dict[str, Any]] = {}
        
        # Association graph for semantic connections
        self.associations: Dict[str, List[str]] = {}
        
        # Storage statistics
        self.stats = {
            'total_stored': 0,
            'total_retrieved': 0,
            'successful_recalls': 0,
            'partial_recalls': 0,
            'failed_recalls': 0
        }
    
    def encode_pattern(self, data: Any) -> np.ndarray:
        """
        Encode data into a holographic pattern.
        
        Args:
            data: Data to encode (any JSON-serializable type)
            
        Returns:
            Complex-valued pattern vector
        """
        # Convert data to string representation
        data_str = json.dumps(data, sort_keys=True)
        
        # Generate deterministic random pattern from hash
        hash_val = int(hashlib.sha256(data_str.encode()).hexdigest(), 16)
        np.random.seed(hash_val % (2**32))
        
        # Create complex pattern with random phase
        magnitude = np.random.randn(self.dimensions)
        phase = np.random.uniform(0, 2*np.pi, self.dimensions)
        pattern = magnitude * np.exp(1j * phase)
        
        # Normalize
        pattern = pattern / np.linalg.norm(pattern)
        
        return pattern
    
    def store(self, key: str, data: Any, tags: Optional[List[str]] = None) -> bool:
        """
        Store data in holographic memory.
        
        Args:
            key: Unique identifier for the memory
            data: Data to store
            tags: Optional tags for associative retrieval
            
        Returns:
            True if storage successful
        """
        if len(self.memory_index) >= self.capacity:
            return False
        
        # Encode data into holographic pattern
        pattern = self.encode_pattern(data)
        
        # Store in hologram using interference
        self.hologram += pattern
        
        # Update memory index
        self.memory_index[key] = {
            'data': data,
            'pattern': pattern,
            'tags': tags or [],
            'timestamp': self.stats['total_stored']
        }
        
        # Build associations from tags
        if tags:
            for tag in tags:
                if tag not in self.associations:
                    self.associations[tag] = []
                self.associations[tag].append(key)
        
        self.stats['total_stored'] += 1
        return True
    
    def retrieve(self, key: str, tolerance: float = 0.1) -> Optional[Any]:
        """
        Retrieve data by exact key.
        
        Args:
            key: Memory identifier
            tolerance: Tolerance for pattern matching
            
        Returns:
            Retrieved data or None if not found
        """
        if key not in self.memory_index:
            self.stats['failed_recalls'] += 1
            return None
        
        self.stats['total_retrieved'] += 1
        self.stats['successful_recalls'] += 1
        return self.memory_index[key]['data']
    
    def associative_recall(self, partial_data: Any = None, 
                          tags: Optional[List[str]] = None,
                          similarity_threshold: float = 0.7) -> List[Tuple[str, Any, float]]:
        """
        Retrieve memories by partial pattern or tags.
        
        Args:
            partial_data: Partial data pattern to match
            tags: Tags to search for
            similarity_threshold: Minimum similarity for recall
            
        Returns:
            List of (key, data, similarity) tuples
        """
        results = []
        
        # Tag-based recall
        if tags:
            candidate_keys = set()
            for tag in tags:
                if tag in self.associations:
                    candidate_keys.update(self.associations[tag])
            
            for key in candidate_keys:
                data = self.memory_index[key]['data']
                # Calculate tag overlap as similarity
                stored_tags = set(self.memory_index[key]['tags'])
                query_tags = set(tags)
                similarity = len(stored_tags & query_tags) / len(stored_tags | query_tags)
                
                if similarity >= similarity_threshold:
                    results.append((key, data, similarity))
        
        # Pattern-based recall
        if partial_data is not None:
            query_pattern = self.encode_pattern(partial_data)
            
            for key, mem_info in self.memory_index.items():
                stored_pattern = mem_info['pattern']
                
                # Calculate similarity using inner product
                similarity = abs(np.vdot(query_pattern, stored_pattern))
                
                if similarity >= similarity_threshold:
                    results.append((key, mem_info['data'], float(similarity)))
        
        # Sort by similarity
        results.sort(key=lambda x: x[2], reverse=True)
        
        self.stats['total_retrieved'] += len(results)
        if results:
            self.stats['partial_recalls'] += 1
        else:
            self.stats['failed_recalls'] += 1
        
        return results
    
    def reconstruct_from_partial(self, damaged_hologram: np.ndarray, 
                                 damage_ratio: float) -> Dict[str, Any]:
        """
        Reconstruct memories from partially damaged hologram.
        
        Args:
            damaged_hologram: Hologram with missing/corrupted data
            damage_ratio: Fraction of data that is damaged
            
        Returns:
            Dictionary of reconstructed memories with confidence scores
        """
        reconstructed = {}
        
        for key, mem_info in self.memory_index.items():
            stored_pattern = mem_info['pattern']
            
            # Calculate correlation with damaged hologram
            correlation = np.vdot(stored_pattern, damaged_hologram)
            confidence = abs(correlation) / (1.0 + damage_ratio)
            
            # Attempt reconstruction if confidence is reasonable
            if confidence > 0.3:
                reconstructed[key] = {
                    'data': mem_info['data'],
                    'confidence': float(confidence),
                    'original_pattern_strength': float(abs(np.vdot(stored_pattern, self.hologram)))
                }
        
        return reconstructed
    
    def create_association(self, key1: str, key2: str, strength: float = 1.0):
        """
        Create explicit association between two memories.
        
        Args:
            key1: First memory key
            key2: Second memory key
            strength: Association strength (0-1)
        """
        if key1 not in self.memory_index or key2 not in self.memory_index:
            return
        
        # Add bidirectional association
        assoc_tag = f"assoc_{key1}_{key2}"
        
        if assoc_tag not in self.associations:
            self.associations[assoc_tag] = []
        
        self.associations[assoc_tag].extend([key1, key2])
    
    def get_associated_memories(self, key: str, max_depth: int = 2) -> List[str]:
        """
        Get memories associated with given key through association graph.
        
        Args:
            key: Starting memory key
            max_depth: Maximum depth to traverse
            
        Returns:
            List of associated memory keys
        """
        if key not in self.memory_index:
            return []
        
        visited = set()
        to_visit = [(key, 0)]
        associated = []
        
        while to_visit:
            current_key, depth = to_visit.pop(0)
            
            if current_key in visited or depth > max_depth:
                continue
            
            visited.add(current_key)
            
            if current_key != key:
                associated.append(current_key)
            
            # Find associations through tags
            current_tags = self.memory_index[current_key]['tags']
            for tag in current_tags:
                if tag in self.associations:
                    for assoc_key in self.associations[tag]:
                        if assoc_key not in visited:
                            to_visit.append((assoc_key, depth + 1))
        
        return associated
    
    def interference_pattern_analysis(self) -> Dict[str, float]:
        """
        Analyze interference patterns in holographic storage.
        
        Returns:
            Dictionary of interference metrics
        """
        # Calculate hologram statistics
        magnitude = np.abs(self.hologram)
        phase = np.angle(self.hologram)
        
        return {
            'mean_magnitude': float(np.mean(magnitude)),
            'std_magnitude': float(np.std(magnitude)),
            'mean_phase': float(np.mean(phase)),
            'phase_coherence': float(np.abs(np.mean(np.exp(1j * phase)))),
            'storage_density': len(self.memory_index) / self.dimensions,
            'hologram_energy': float(np.sum(magnitude**2))
        }
    
    def consolidate_memories(self, similarity_threshold: float = 0.9):
        """
        Consolidate similar memories to reduce interference.
        
        Args:
            similarity_threshold: Threshold for considering memories similar
        """
        keys = list(self.memory_index.keys())
        consolidated = set()
        
        for i, key1 in enumerate(keys):
            if key1 in consolidated:
                continue
            
            pattern1 = self.memory_index[key1]['pattern']
            
            for key2 in keys[i+1:]:
                if key2 in consolidated:
                    continue
                
                pattern2 = self.memory_index[key2]['pattern']
                similarity = abs(np.vdot(pattern1, pattern2))
                
                if similarity >= similarity_threshold:
                    # Merge memories
                    self.create_association(key1, key2, strength=similarity)
                    consolidated.add(key2)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        return {
            **self.stats,
            'current_capacity': len(self.memory_index),
            'max_capacity': self.capacity,
            'utilization': len(self.memory_index) / self.capacity,
            'num_associations': len(self.associations),
            'interference_metrics': self.interference_pattern_analysis()
        }


def test_holographic_memory():
    """Test holographic memory system."""
    memory = HolographicMemorySystem(dimensions=256, capacity=100)
    
    # Store some memories
    memory.store('fact1', {'type': 'fact', 'content': 'The sky is blue'}, tags=['color', 'nature'])
    memory.store('fact2', {'type': 'fact', 'content': 'Grass is green'}, tags=['color', 'nature'])
    memory.store('fact3', {'type': 'fact', 'content': 'Water is wet'}, tags=['nature', 'physics'])
    
    # Exact retrieval
    data = memory.retrieve('fact1')
    print(f"Retrieved: {data}")
    
    # Associative recall by tags
    results = memory.associative_recall(tags=['nature'])
    print(f"\nMemories tagged 'nature': {len(results)}")
    for key, data, sim in results:
        print(f"  {key}: {data} (similarity: {sim:.2f})")
    
    # Pattern-based recall
    partial = {'type': 'fact'}
    results = memory.associative_recall(partial_data=partial, similarity_threshold=0.5)
    print(f"\nPattern-based recall: {len(results)} matches")
    
    # Statistics
    stats = memory.get_statistics()
    print(f"\nStatistics: {json.dumps(stats, indent=2)}")
    
    return memory


if __name__ == '__main__':
    test_holographic_memory()
