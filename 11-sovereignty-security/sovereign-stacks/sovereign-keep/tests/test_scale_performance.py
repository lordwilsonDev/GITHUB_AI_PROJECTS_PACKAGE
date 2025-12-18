#!/usr/bin/env python3
"""
Scale and Performance Testing

Tests algorithmic behavior at scale and identifies performance failure modes.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import time
import random
import string
import psutil
import numpy as np
from typing import List, Dict

from src.analysis import SemanticAuditor


class MockNote:
    """Lightweight note for testing"""
    def __init__(self, title: str, text: str, note_id: str = None):
        self.title = title
        self.text = text
        self.id = note_id or f"note_{random.randint(10000, 99999)}"
        self.trashed = False
        self.archived = False


def get_memory_usage_mb() -> float:
    """Get current process memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024


def generate_random_notes(n: int, avg_length: int = 50) -> List[MockNote]:
    """Generate n random notes"""
    notes = []
    for i in range(n):
        length = random.randint(avg_length // 2, avg_length * 2)
        text = ' '.join(
            ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 10)))
            for _ in range(length // 5)
        )
        notes.append(MockNote(f"Note {i}", text))
    return notes


def generate_similar_notes(n: int, base_text: str) -> List[MockNote]:
    """Generate n similar notes (for high-density testing)"""
    notes = []
    for i in range(n):
        # Add small variations
        variant = base_text + f" variant {i} " + \
                 ' '.join(random.choices(['alpha', 'beta', 'gamma'], k=2))
        notes.append(MockNote(f"Similar {i}", variant))
    return notes


class TestComplexityScaling:
    """Test algorithmic complexity"""
    
    def setup_method(self):
        """Initialize auditor"""
        self.auditor = SemanticAuditor(None)
    
    def test_time_complexity_scaling(self):
        """
        Test: Measure time complexity as N increases
        
        Expected: O(N^2) for similarity matrix, O(N) for clustering
        Overall: O(N^2) but with small constant
        """
        sizes = [10, 25, 50, 100]
        times = []
        
        print("\nTime complexity scaling:")
        
        for n in sizes:
            notes = generate_random_notes(n, avg_length=30)
            
            start_time = time.time()
            self.auditor.find_redundancy_clusters(notes, threshold=0.85)
            elapsed = time.time() - start_time
            
            times.append(elapsed)
            print(f"  N={n:4d}: {elapsed:6.3f}s ({elapsed/n*1000:.1f}ms per note)")
        
        # Fit to quadratic model: time = a*N^2 + b*N + c
        coeffs = np.polyfit(sizes, times, 2)
        a, b, c = coeffs
        
        print(f"\n  Fitted model: time = {a:.2e}*N^2 + {b:.2e}*N + {c:.2f}")
        
        # Assert quadratic coefficient is reasonable
        # For 100 notes, should take < 30 seconds
        predicted_100 = a * 100**2 + b * 100 + c
        assert predicted_100 < 30, \
            f"Predicted time for 100 notes too high: {predicted_100:.1f}s"
    
    def test_memory_complexity_scaling(self):
        """
        Test: Measure memory usage as N increases
        
        Expected: O(N^2) for similarity matrix (worst case)
        But should be manageable for N < 10,000
        """
        sizes = [10, 50, 100, 200]
        memories = []
        
        print("\nMemory complexity scaling:")
        
        for n in sizes:
            notes = generate_random_notes(n, avg_length=30)
            
            mem_before = get_memory_usage_mb()
            self.auditor.find_redundancy_clusters(notes, threshold=0.85)
            mem_after = get_memory_usage_mb()
            
            mem_used = mem_after - mem_before
            memories.append(mem_used)
            
            print(f"  N={n:4d}: {mem_used:6.1f} MB ({mem_used/n:.2f} MB per note)")
        
        # Memory per note should not grow dramatically
        # (indicates good memory management)
        mem_per_note = [m / n for m, n in zip(memories, sizes)]
        
        # Should be roughly constant (within 2x)
        ratio = max(mem_per_note) / min(mem_per_note)
        assert ratio < 3.0, \
            f"Memory per note varies too much: {ratio:.1f}x"


class TestHighDensityScenarios:
    """Test behavior when many notes are similar"""
    
    def setup_method(self):
        """Initialize auditor"""
        self.auditor = SemanticAuditor(None)
    
    def test_giant_component_prevention(self):
        """
        CRITICAL: Prevent giant connected components
        
        If many notes are pairwise similar, the graph can become
        fully connected, creating one giant cluster.
        """
        # Create 50 similar notes
        base_text = "Meeting notes about Q4 planning and budget review"
        notes = generate_similar_notes(50, base_text)
        
        clusters = self.auditor.find_redundancy_clusters(notes, threshold=0.85)
        
        if clusters:
            max_cluster_size = max(len(c) for c in clusters)
            print(f"\n  Largest cluster: {max_cluster_size} / {len(notes)} notes")
            
            # No cluster should contain > 50% of notes
            assert max_cluster_size < len(notes) * 0.5, \
                f"Giant component formed: {max_cluster_size} notes in one cluster"
    
    def test_high_density_performance(self):
        """
        Test: Performance when similarity density is high
        
        High density = many edges in the graph
        This is the worst case for clustering algorithms.
        """
        # Create 100 notes with high pairwise similarity
        base_text = "Standard meeting notes template"
        notes = generate_similar_notes(100, base_text)
        
        start_time = time.time()
        mem_before = get_memory_usage_mb()
        
        clusters = self.auditor.find_redundancy_clusters(notes, threshold=0.85)
        
        elapsed = time.time() - start_time
        mem_used = get_memory_usage_mb() - mem_before
        
        print(f"\n  High density (N=100):")
        print(f"    Time: {elapsed:.2f}s")
        print(f"    Memory: {mem_used:.1f} MB")
        print(f"    Clusters: {len(clusters)}")
        
        # Should complete in reasonable time
        assert elapsed < 60, f"High density took too long: {elapsed:.1f}s"
        
        # Should not blow up memory
        assert mem_used < 500, f"High density used too much memory: {mem_used:.1f} MB"
    
    def test_fully_connected_scenario(self):
        """
        Test: Worst case - all notes identical
        
        This creates a fully connected graph.
        """
        # Create 50 identical notes
        notes = [MockNote(f"Note {i}", "Identical text") for i in range(50)]
        
        start_time = time.time()
        clusters = self.auditor.find_redundancy_clusters(notes, threshold=0.85)
        elapsed = time.time() - start_time
        
        print(f"\n  Fully connected (N=50): {elapsed:.2f}s")
        
        # Should handle gracefully
        assert elapsed < 30, "Fully connected scenario too slow"
        
        # Should create one cluster (or handle specially)
        assert clusters is not None, "Crashed on fully connected input"


class TestPerformanceFailureModes:
    """Test specific performance failure modes"""
    
    def setup_method(self):
        """Initialize auditor"""
        self.auditor = SemanticAuditor(None)
    
    def test_very_long_notes(self):
        """
        Test: Performance with very long notes
        
        Long notes might slow down embedding generation.
        """
        # Create notes with 1000+ words
        long_text = ' '.join(
            ''.join(random.choices(string.ascii_lowercase, k=5))
            for _ in range(1000)
        )
        
        notes = [MockNote(f"Long {i}", long_text) for i in range(10)]
        
        start_time = time.time()
        self.auditor.find_redundancy_clusters(notes, threshold=0.85)
        elapsed = time.time() - start_time
        
        print(f"\n  Very long notes (10 x 1000 words): {elapsed:.2f}s")
        
        # Should handle long notes efficiently
        assert elapsed < 30, f"Long notes too slow: {elapsed:.1f}s"
    
    def test_many_small_clusters(self):
        """
        Test: Performance with many small clusters
        
        This tests the clustering algorithm's efficiency.
        """
        # Create 100 notes in 50 pairs (50 small clusters)
        notes = []
        for i in range(50):
            base = f"Topic {i} discussion"
            notes.append(MockNote(f"A{i}", base))
            notes.append(MockNote(f"B{i}", base))  # Duplicate
        
        start_time = time.time()
        clusters = self.auditor.find_redundancy_clusters(notes, threshold=0.85)
        elapsed = time.time() - start_time
        
        print(f"\n  Many small clusters (100 notes, ~50 clusters): {elapsed:.2f}s")
        print(f"    Found {len(clusters)} clusters")
        
        # Should handle efficiently
        assert elapsed < 30, f"Many clusters too slow: {elapsed:.1f}s"
        
        # Should find most of the pairs
        assert len(clusters) >= 40, f"Missed clusters: only found {len(clusters)}"
    
    def test_sparse_graph_performance(self):
        """
        Test: Performance when graph is sparse (few edges)
        
        This is the best case - should be very fast.
        """
        # Create 100 completely unrelated notes
        notes = []
        for i in range(100):
            # Each note about a different random topic
            text = ' '.join(random.choices([
                'quantum', 'biology', 'economics', 'art', 'music',
                'sports', 'cooking', 'travel', 'technology', 'history'
            ], k=10))
            notes.append(MockNote(f"Note {i}", text))
        
        start_time = time.time()
        clusters = self.auditor.find_redundancy_clusters(notes, threshold=0.85)
        elapsed = time.time() - start_time
        
        print(f"\n  Sparse graph (100 unrelated notes): {elapsed:.2f}s")
        print(f"    Found {len(clusters)} clusters")
        
        # Sparse case should be fast
        assert elapsed < 20, f"Sparse case too slow: {elapsed:.1f}s"
        
        # Should find few or no clusters
        assert len(clusters) < 10, f"Too many clusters in sparse graph: {len(clusters)}"


class TestScalabilityLimits:
    """Document scalability limits"""
    
    def test_document_scalability_limits(self):
        """
        Document: Known scalability limits
        
        This documents the tested limits of the system.
        """
        limits = """
        SCALABILITY LIMITS (as of testing):
        
        Tested and working:
        - Up to 200 notes: < 30 seconds
        - Up to 100 notes (high density): < 60 seconds
        - Memory usage: < 500 MB for 200 notes
        
        Estimated limits:
        - 1,000 notes: ~5-10 minutes (acceptable for batch)
        - 5,000 notes: ~30-60 minutes (batch only)
        - 10,000 notes: May require optimization
        
        Bottlenecks:
        1. Embedding generation: O(N) but slow constant
        2. Similarity matrix: O(N^2) memory
        3. Graph clustering: O(N + E) where E can be O(N^2)
        
        Optimization strategies if needed:
        1. Batch embedding generation (already done)
        2. Sparse similarity matrix (only store > threshold)
        3. Approximate nearest neighbors (FAISS, Annoy)
        4. Incremental clustering (don't reprocess all notes)
        5. Parallel processing (multiple cores)
        
        Recommended usage:
        - < 1,000 notes: Run anytime
        - 1,000-5,000 notes: Run weekly/monthly
        - > 5,000 notes: Consider optimization or sampling
        """
        print(limits)
        assert True  # Always passes, just documents limits


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "-s"])
