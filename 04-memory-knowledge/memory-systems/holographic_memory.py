#!/usr/bin/env python3
"""
Holographic Memory System - New Build 12 (T-095)
Distributed information storage with associative recall mechanisms.
Implements holographic principles for fault-tolerant, high-density memory.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import hashlib


class MemoryEncoding(Enum):
    """Holographic encoding schemes."""
    FOURIER = "fourier"  # Fourier transform encoding
    WAVELET = "wavelet"  # Wavelet transform encoding
    DISTRIBUTED = "distributed"  # Distributed representation
    SPARSE = "sparse"  # Sparse coding


class RecallMode(Enum):
    """Memory recall modes."""
    EXACT = "exact"  # Exact pattern matching
    ASSOCIATIVE = "associative"  # Associative recall
    PARTIAL = "partial"  # Partial cue recall
    SEMANTIC = "semantic"  # Semantic similarity


@dataclass
class MemoryPattern:
    """Represents a memory pattern."""
    pattern_id: str
    data: np.ndarray  # Original data
    encoding: np.ndarray  # Holographic encoding
    encoding_type: MemoryEncoding
    associations: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    access_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'pattern_id': self.pattern_id,
            'data_shape': list(self.data.shape),
            'encoding_shape': list(self.encoding.shape),
            'encoding_type': self.encoding_type.value,
            'associations': list(self.associations),
            'metadata': self.metadata,
            'timestamp': self.timestamp,
            'access_count': self.access_count
        }


@dataclass
class RecallResult:
    """Result of a memory recall operation."""
    pattern_id: str
    recalled_data: np.ndarray
    confidence: float  # 0.0 to 1.0
    similarity: float  # Similarity to query
    mode: RecallMode
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'pattern_id': self.pattern_id,
            'recalled_shape': list(self.recalled_data.shape),
            'confidence': float(self.confidence),
            'similarity': float(self.similarity),
            'mode': self.mode.value,
            'timestamp': self.timestamp
        }


class HolographicMemory:
    """
    Holographic memory system with distributed storage and associative recall.
    
    Features:
    - Distributed information storage
    - Associative recall mechanisms
    - Fault tolerance through redundancy
    - High information density
    - Partial cue recall
    """
    
    def __init__(
        self,
        memory_size: int = 1024,
        encoding_type: MemoryEncoding = MemoryEncoding.FOURIER,
        redundancy_factor: float = 2.0
    ):
        self.memory_size = memory_size
        self.encoding_type = encoding_type
        self.redundancy_factor = redundancy_factor
        
        # Holographic storage plate (complex-valued)
        self.hologram = np.zeros(memory_size, dtype=complex)
        
        # Pattern registry
        self.patterns: Dict[str, MemoryPattern] = {}
        
        # Association graph
        self.associations: Dict[str, Set[str]] = {}
        
        # Recall history
        self.recall_history: List[RecallResult] = []
        
        # Statistics
        self.total_stores = 0
        self.total_recalls = 0
        
    def store_pattern(
        self,
        pattern_id: str,
        data: np.ndarray,
        associations: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MemoryPattern:
        """
        Store a pattern in holographic memory.
        
        Args:
            pattern_id: Unique identifier
            data: Pattern data to store
            associations: Associated pattern IDs
            metadata: Additional metadata
            
        Returns:
            MemoryPattern object
        """
        # Encode pattern
        encoding = self._encode_pattern(data)
        
        # Create memory pattern
        pattern = MemoryPattern(
            pattern_id=pattern_id,
            data=data.copy(),
            encoding=encoding,
            encoding_type=self.encoding_type,
            associations=associations or set(),
            metadata=metadata or {}
        )
        
        # Store in hologram (superposition)
        self._add_to_hologram(encoding)
        
        # Register pattern
        self.patterns[pattern_id] = pattern
        
        # Update associations
        if associations:
            self.associations[pattern_id] = associations
            for assoc_id in associations:
                if assoc_id not in self.associations:
                    self.associations[assoc_id] = set()
                self.associations[assoc_id].add(pattern_id)
        
        self.total_stores += 1
        return pattern
    
    def _encode_pattern(self, data: np.ndarray) -> np.ndarray:
        """Encode pattern using holographic encoding."""
        # Flatten data
        flat_data = data.flatten()
        
        if self.encoding_type == MemoryEncoding.FOURIER:
            # Fourier transform encoding
            # Pad or truncate to memory size
            if len(flat_data) < self.memory_size:
                padded = np.pad(flat_data, (0, self.memory_size - len(flat_data)))
            else:
                padded = flat_data[:self.memory_size]
            
            # Apply FFT
            encoding = np.fft.fft(padded)
            
        elif self.encoding_type == MemoryEncoding.WAVELET:
            # Simplified wavelet encoding
            # Use Haar wavelet-like transform
            padded = self._pad_to_power_of_2(flat_data)
            encoding = self._haar_transform(padded)
            
            # Resize to memory size
            if len(encoding) < self.memory_size:
                encoding = np.pad(encoding, (0, self.memory_size - len(encoding)))
            else:
                encoding = encoding[:self.memory_size]
                
        elif self.encoding_type == MemoryEncoding.DISTRIBUTED:
            # Distributed representation
            # Random projection
            if len(flat_data) < self.memory_size:
                padded = np.pad(flat_data, (0, self.memory_size - len(flat_data)))
            else:
                padded = flat_data[:self.memory_size]
            
            # Add random phase for distribution
            phases = np.random.uniform(0, 2*np.pi, self.memory_size)
            encoding = padded * np.exp(1j * phases)
            
        else:  # SPARSE
            # Sparse coding
            encoding = np.zeros(self.memory_size, dtype=complex)
            # Select sparse indices
            n_active = max(1, int(self.memory_size * 0.1))  # 10% sparsity
            indices = np.random.choice(self.memory_size, n_active, replace=False)
            
            # Distribute data across sparse indices
            for i, idx in enumerate(indices):
                if i < len(flat_data):
                    encoding[idx] = flat_data[i]
        
        return encoding
    
    def _pad_to_power_of_2(self, data: np.ndarray) -> np.ndarray:
        """Pad array to next power of 2."""
        n = len(data)
        next_pow2 = 2 ** int(np.ceil(np.log2(n)))
        return np.pad(data, (0, next_pow2 - n))
    
    def _haar_transform(self, data: np.ndarray) -> np.ndarray:
        """Simple Haar wavelet transform."""
        result = data.copy().astype(complex)
        n = len(result)
        
        while n > 1:
            n = n // 2
            for i in range(n):
                avg = (result[2*i] + result[2*i + 1]) / 2
                diff = (result[2*i] - result[2*i + 1]) / 2
                result[i] = avg
                result[n + i] = diff
        
        return result
    
    def _add_to_hologram(self, encoding: np.ndarray):
        """Add encoding to hologram through superposition."""
        # Normalize encoding
        norm = np.linalg.norm(encoding)
        if norm > 0:
            normalized = encoding / norm
        else:
            normalized = encoding
        
        # Add to hologram (superposition principle)
        self.hologram += normalized * self.redundancy_factor
    
    def recall_pattern(
        self,
        query: np.ndarray,
        mode: RecallMode = RecallMode.ASSOCIATIVE,
        threshold: float = 0.5
    ) -> Optional[RecallResult]:
        """
        Recall a pattern from holographic memory.
        
        Args:
            query: Query pattern (can be partial)
            mode: Recall mode
            threshold: Minimum similarity threshold
            
        Returns:
            RecallResult or None if no match
        """
        # Encode query
        query_encoding = self._encode_pattern(query)
        
        # Find best match
        best_match = None
        best_similarity = 0.0
        
        for pattern_id, pattern in self.patterns.items():
            if mode == RecallMode.EXACT:
                similarity = self._exact_match(query_encoding, pattern.encoding)
            elif mode == RecallMode.ASSOCIATIVE:
                similarity = self._associative_match(query_encoding, pattern.encoding)
            elif mode == RecallMode.PARTIAL:
                similarity = self._partial_match(query_encoding, pattern.encoding)
            else:  # SEMANTIC
                similarity = self._semantic_match(query_encoding, pattern.encoding)
            
            if similarity > best_similarity and similarity >= threshold:
                best_similarity = similarity
                best_match = pattern
        
        if best_match is None:
            return None
        
        # Calculate confidence
        confidence = self._calculate_confidence(best_similarity, mode)
        
        # Create recall result
        result = RecallResult(
            pattern_id=best_match.pattern_id,
            recalled_data=best_match.data.copy(),
            confidence=confidence,
            similarity=best_similarity,
            mode=mode
        )
        
        # Update statistics
        best_match.access_count += 1
        self.recall_history.append(result)
        self.total_recalls += 1
        
        return result
    
    def _exact_match(self, query: np.ndarray, stored: np.ndarray) -> float:
        """Calculate exact match similarity."""
        # Normalized correlation
        correlation = np.abs(np.dot(query.conj(), stored))
        norm_query = np.linalg.norm(query)
        norm_stored = np.linalg.norm(stored)
        
        if norm_query > 0 and norm_stored > 0:
            return correlation / (norm_query * norm_stored)
        return 0.0
    
    def _associative_match(self, query: np.ndarray, stored: np.ndarray) -> float:
        """Calculate associative match similarity."""
        # Use phase correlation for associative matching
        cross_power = query * stored.conj()
        norm = np.abs(cross_power) + 1e-10
        normalized_cross_power = cross_power / norm
        
        # Inverse FFT to get correlation
        correlation = np.fft.ifft(normalized_cross_power)
        
        # Peak correlation value
        return np.max(np.abs(correlation))
    
    def _partial_match(self, query: np.ndarray, stored: np.ndarray) -> float:
        """Calculate partial cue match similarity."""
        # Partial matching allows for incomplete queries
        # Use cosine similarity on magnitude spectrum
        query_mag = np.abs(query)
        stored_mag = np.abs(stored)
        
        dot_product = np.dot(query_mag, stored_mag)
        norm_query = np.linalg.norm(query_mag)
        norm_stored = np.linalg.norm(stored_mag)
        
        if norm_query > 0 and norm_stored > 0:
            return dot_product / (norm_query * norm_stored)
        return 0.0
    
    def _semantic_match(self, query: np.ndarray, stored: np.ndarray) -> float:
        """Calculate semantic similarity."""
        # Use both magnitude and phase information
        mag_similarity = self._partial_match(query, stored)
        
        # Phase similarity
        query_phase = np.angle(query)
        stored_phase = np.angle(stored)
        phase_diff = np.abs(query_phase - stored_phase)
        phase_similarity = 1.0 - np.mean(phase_diff) / np.pi
        
        # Combine
        return 0.7 * mag_similarity + 0.3 * phase_similarity
    
    def _calculate_confidence(self, similarity: float, mode: RecallMode) -> float:
        """Calculate recall confidence."""
        # Base confidence from similarity
        confidence = similarity
        
        # Adjust based on mode
        if mode == RecallMode.EXACT:
            # Exact mode requires high similarity
            confidence = confidence ** 2
        elif mode == RecallMode.PARTIAL:
            # Partial mode is more lenient
            confidence = min(1.0, confidence * 1.2)
        
        return confidence
    
    def recall_by_association(
        self,
        pattern_id: str,
        max_results: int = 5
    ) -> List[RecallResult]:
        """
        Recall patterns associated with a given pattern.
        
        Args:
            pattern_id: Pattern to find associations for
            max_results: Maximum number of results
            
        Returns:
            List of associated patterns
        """
        if pattern_id not in self.patterns:
            return []
        
        # Get direct associations
        associated_ids = self.associations.get(pattern_id, set())
        
        results = []
        for assoc_id in associated_ids:
            if assoc_id in self.patterns:
                pattern = self.patterns[assoc_id]
                
                # Calculate association strength
                similarity = self._associative_match(
                    self.patterns[pattern_id].encoding,
                    pattern.encoding
                )
                
                result = RecallResult(
                    pattern_id=assoc_id,
                    recalled_data=pattern.data.copy(),
                    confidence=similarity,
                    similarity=similarity,
                    mode=RecallMode.ASSOCIATIVE
                )
                results.append(result)
                
                pattern.access_count += 1
        
        # Sort by similarity
        results.sort(key=lambda r: r.similarity, reverse=True)
        
        return results[:max_results]
    
    def get_memory_density(self) -> float:
        """Calculate information density in hologram."""
        # Ratio of stored patterns to memory size
        if self.memory_size == 0:
            return 0.0
        
        return len(self.patterns) / self.memory_size
    
    def get_fault_tolerance(self) -> float:
        """Estimate fault tolerance level."""
        # Based on redundancy factor and pattern overlap
        base_tolerance = min(1.0, self.redundancy_factor / 10.0)
        
        # Adjust for pattern count (more patterns = more interference)
        if len(self.patterns) > 0:
            interference_factor = 1.0 / (1.0 + len(self.patterns) / 100.0)
            return base_tolerance * interference_factor
        
        return base_tolerance
    
    def export_state(self) -> Dict[str, Any]:
        """Export complete memory state."""
        return {
            'memory_size': self.memory_size,
            'encoding_type': self.encoding_type.value,
            'redundancy_factor': float(self.redundancy_factor),
            'patterns': {
                pid: pattern.to_dict() for pid, pattern in self.patterns.items()
            },
            'associations': {
                pid: list(assocs) for pid, assocs in self.associations.items()
            },
            'total_stores': self.total_stores,
            'total_recalls': self.total_recalls,
            'memory_density': float(self.get_memory_density()),
            'fault_tolerance': float(self.get_fault_tolerance()),
            'recall_history': [
                r.to_dict() for r in self.recall_history[-100:]  # Last 100
            ]
        }


# Integration interface
def create_holographic_memory(
    memory_size: int = 1024,
    encoding_type: MemoryEncoding = MemoryEncoding.FOURIER
) -> HolographicMemory:
    """Factory function for creating holographic memory."""
    return HolographicMemory(
        memory_size=memory_size,
        encoding_type=encoding_type
    )


def test_holographic_memory():
    """Test holographic memory functionality."""
    memory = create_holographic_memory(memory_size=512)
    
    # Test 1: Store patterns
    pattern1 = np.random.random(64)
    pattern2 = np.random.random(64)
    
    mem1 = memory.store_pattern('pattern_1', pattern1)
    mem2 = memory.store_pattern('pattern_2', pattern2, associations={'pattern_1'})
    
    assert len(memory.patterns) == 2
    assert 'pattern_1' in mem2.associations
    
    # Test 2: Exact recall
    result = memory.recall_pattern(pattern1, mode=RecallMode.EXACT)
    assert result is not None
    assert result.pattern_id == 'pattern_1'
    assert result.confidence > 0.5
    
    # Test 3: Partial recall
    partial_query = pattern1[:32]  # Only half the pattern
    padded_query = np.pad(partial_query, (0, 32))
    result = memory.recall_pattern(padded_query, mode=RecallMode.PARTIAL, threshold=0.3)
    assert result is not None
    
    # Test 4: Associative recall
    results = memory.recall_by_association('pattern_1')
    assert len(results) > 0
    assert results[0].pattern_id == 'pattern_2'
    
    # Test 5: Memory density
    density = memory.get_memory_density()
    assert density > 0
    
    # Test 6: Fault tolerance
    tolerance = memory.get_fault_tolerance()
    assert 0 <= tolerance <= 1
    
    # Test 7: Export state
    state = memory.export_state()
    assert 'patterns' in state
    assert 'memory_density' in state
    assert state['total_stores'] == 2
    
    return True


if __name__ == '__main__':
    success = test_holographic_memory()
    print(f"Holographic Memory test: {'PASSED' if success else 'FAILED'}")
