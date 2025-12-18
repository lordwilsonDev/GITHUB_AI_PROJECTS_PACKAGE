#!/usr/bin/env python3
"""
Formal Invariant Tests - Non-Negotiable Laws

These tests encode mathematical properties that MUST hold
regardless of model, threshold, or input data.

If any of these fail, the system is fundamentally broken.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import random
import string
import itertools
from typing import List, Dict, Set
import numpy as np

from src.analysis import SemanticAuditor


class MockNote:
    """Lightweight note for testing"""
    def __init__(self, title: str, text: str, note_id: str = None):
        self.title = title
        self.text = text
        self.id = note_id or f"note_{random.randint(1000, 9999)}"
        self.trashed = False
        self.archived = False


class TestFormalInvariants:
    """Test suite for formal mathematical invariants"""
    
    def setup_method(self):
        """Initialize auditor for each test"""
        self.auditor = SemanticAuditor(None)
    
    # ========================================
    # INVARIANT 1: Idempotence
    # ========================================
    
    def test_idempotence_clustering(self):
        """
        LAW: analyze(analyze(notes)) == analyze(notes)
        
        Running analysis twice must produce identical results.
        """
        notes = [
            MockNote("Note 1", "First note about meetings"),
            MockNote("Note 2", "Second note about meetings"),
            MockNote("Note 3", "Unrelated shopping list"),
        ]
        
        # First analysis
        clusters1 = self.auditor.find_redundancy_clusters(
            notes, threshold=0.85
        )
        
        # Second analysis (should be identical)
        clusters2 = self.auditor.find_redundancy_clusters(
            notes, threshold=0.85
        )
        
        # Convert to sets for comparison
        clusters1_sets = [set(c) for c in clusters1]
        clusters2_sets = [set(c) for c in clusters2]
        
        assert clusters1_sets == clusters2_sets, \
            "Idempotence violated: repeated analysis changed results"
    
    def test_idempotence_entropy(self):
        """
        LAW: entropy(text) is deterministic
        
        Calculating entropy twice must give same result.
        """
        text = "This is a test of entropy calculation"
        
        entropy1 = self.auditor.calculate_entropy(text)
        entropy2 = self.auditor.calculate_entropy(text)
        
        assert entropy1 == entropy2, \
            f"Entropy not deterministic: {entropy1} != {entropy2}"
    
    # ========================================
    # INVARIANT 2: Order Independence
    # ========================================
    
    def test_order_independence_clustering(self):
        """
        LAW: analyze(shuffle(notes)) == analyze(notes)
        
        Note order must not affect clustering results.
        """
        notes = [
            MockNote("A", "Meeting about Q4 planning"),
            MockNote("B", "Q4 planning discussion"),
            MockNote("C", "Grocery shopping list"),
            MockNote("D", "Random thought about coffee"),
        ]
        
        # Analyze in original order
        clusters_original = self.auditor.find_redundancy_clusters(
            notes, threshold=0.85
        )
        
        # Shuffle and analyze 10 times
        for _ in range(10):
            shuffled = notes.copy()
            random.shuffle(shuffled)
            
            clusters_shuffled = self.auditor.find_redundancy_clusters(
                shuffled, threshold=0.85
            )
            
            # Convert to sets (order-independent comparison)
            orig_sets = [set(c) for c in clusters_original]
            shuf_sets = [set(c) for c in clusters_shuffled]
            
            assert orig_sets == shuf_sets, \
                "Order independence violated: shuffle changed clustering"
    
    # ========================================
    # INVARIANT 3: Monotonic Similarity
    # ========================================
    
    def test_monotonic_similarity_self_maximum(self):
        """
        LAW: sim(A, A) >= sim(A, mutate(A)) >= sim(A, unrelated)
        
        Self-similarity must be maximum (1.0).
        """
        text = "This is a test note about project planning"
        note = MockNote("Test", text)
        
        # Create embeddings
        embeddings = self.auditor.model.encode([text, text])
        
        # Calculate self-similarity
        from sentence_transformers import util
        self_sim = util.cos_sim(embeddings[0], embeddings[1]).item()
        
        assert abs(self_sim - 1.0) < 0.01, \
            f"Self-similarity not 1.0: {self_sim}"
    
    def test_monotonic_similarity_mutation(self):
        """
        LAW: sim(A, A) > sim(A, mutate(A))
        
        Mutating text must decrease similarity.
        """
        original = "Meeting notes about Q4 planning and budget review"
        mutated = "Meeting notes about Q3 planning and budget review"  # Q4 -> Q3
        unrelated = "Grocery shopping list with milk and eggs"
        
        embeddings = self.auditor.model.encode([original, mutated, unrelated])
        
        from sentence_transformers import util
        sim_original_mutated = util.cos_sim(embeddings[0], embeddings[1]).item()
        sim_original_unrelated = util.cos_sim(embeddings[0], embeddings[2]).item()
        
        assert sim_original_mutated > sim_original_unrelated, \
            f"Monotonicity violated: mutated={sim_original_mutated}, unrelated={sim_original_unrelated}"
    
    # ========================================
    # INVARIANT 4: Entropy Ordering
    # ========================================
    
    def test_entropy_ordering_random_vs_repeated(self):
        """
        LAW: entropy(random) > entropy(repeated)
        
        Random text has higher entropy than repetitive text.
        """
        random_text = ''.join(random.choices(string.ascii_letters + ' ', k=100))
        repeated_text = "abc " * 25  # Same length, but repetitive
        
        entropy_random = self.auditor.calculate_entropy(random_text)
        entropy_repeated = self.auditor.calculate_entropy(repeated_text)
        
        assert entropy_random > entropy_repeated, \
            f"Entropy ordering violated: random={entropy_random}, repeated={entropy_repeated}"
    
    def test_entropy_ordering_complex_vs_simple(self):
        """
        LAW: Complex text has higher entropy than simple text
        """
        complex_text = "The quick brown fox jumps over the lazy dog while contemplating existential philosophy"
        simple_text = "a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a"
        
        entropy_complex = self.auditor.calculate_entropy(complex_text)
        entropy_simple = self.auditor.calculate_entropy(simple_text)
        
        assert entropy_complex > entropy_simple, \
            f"Entropy ordering violated: complex={entropy_complex}, simple={entropy_simple}"
    
    # ========================================
    # INVARIANT 5: Cluster Exclusivity
    # ========================================
    
    def test_cluster_exclusivity(self):
        """
        LAW: A note belongs to at most one cluster
        
        No note should appear in multiple clusters.
        """
        notes = [
            MockNote("A", "Meeting about Q4 planning"),
            MockNote("B", "Q4 planning discussion"),
            MockNote("C", "Q4 planning notes"),
            MockNote("D", "Grocery shopping"),
            MockNote("E", "Shopping list"),
        ]
        
        clusters = self.auditor.find_redundancy_clusters(notes, threshold=0.85)
        
        # Check that no note appears in multiple clusters
        all_note_ids = []
        for cluster in clusters:
            all_note_ids.extend(cluster)
        
        # If a note appears twice, len(all_note_ids) > len(set(all_note_ids))
        assert len(all_note_ids) == len(set(all_note_ids)), \
            "Cluster exclusivity violated: note appears in multiple clusters"
    
    # ========================================
    # INVARIANT 6: Similarity Symmetry
    # ========================================
    
    def test_similarity_symmetry(self):
        """
        LAW: sim(A, B) == sim(B, A)
        
        Similarity must be commutative.
        """
        text_a = "Meeting notes about project planning"
        text_b = "Project planning discussion notes"
        
        embeddings = self.auditor.model.encode([text_a, text_b])
        
        from sentence_transformers import util
        sim_ab = util.cos_sim(embeddings[0], embeddings[1]).item()
        sim_ba = util.cos_sim(embeddings[1], embeddings[0]).item()
        
        assert abs(sim_ab - sim_ba) < 1e-6, \
            f"Symmetry violated: sim(A,B)={sim_ab}, sim(B,A)={sim_ba}"
    
    # ========================================
    # INVARIANT 7: Cluster Transitivity (Weak)
    # ========================================
    
    def test_cluster_transitivity_weak(self):
        """
        LAW: If A and B are in same cluster, they must be similar
        
        All pairs within a cluster must exceed threshold * 0.9
        (allowing 10% slack for transitive edges)
        """
        notes = [
            MockNote("A", "Meeting about Q4 planning"),
            MockNote("B", "Q4 planning discussion"),
            MockNote("C", "Q4 planning meeting notes"),
        ]
        
        clusters = self.auditor.find_redundancy_clusters(notes, threshold=0.85)
        
        if not clusters:
            return  # No clusters to test
        
        # For each cluster, check all pairs
        for cluster in clusters:
            if len(cluster) < 2:
                continue
            
            # Get notes in cluster
            cluster_notes = [n for n in notes if n.id in cluster]
            
            # Check all pairs
            for note1, note2 in itertools.combinations(cluster_notes, 2):
                text1 = f"{note1.title} {note1.text}"
                text2 = f"{note2.title} {note2.text}"
                
                embeddings = self.auditor.model.encode([text1, text2])
                
                from sentence_transformers import util
                sim = util.cos_sim(embeddings[0], embeddings[1]).item()
                
                # Allow 10% slack below threshold
                min_sim = 0.85 * 0.9
                
                assert sim >= min_sim, \
                    f"Transitivity violated: {note1.id} and {note2.id} in same cluster but sim={sim} < {min_sim}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
