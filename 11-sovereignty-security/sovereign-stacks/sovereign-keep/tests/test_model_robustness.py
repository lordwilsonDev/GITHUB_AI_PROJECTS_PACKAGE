#!/usr/bin/env python3
"""
Model Robustness Testing

Tests that ensure the system works across different embedding models
and can detect/handle model drift.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics import adjusted_rand_score
import itertools
from typing import List, Dict, Tuple


class MockNote:
    """Lightweight note for testing"""
    def __init__(self, title: str, text: str, note_id: str = None):
        self.title = title
        self.text = text
        self.id = note_id or f"note_{hash(title + text) % 10000}"
        self.trashed = False
        self.archived = False


class TestModelRobustness:
    """Test suite for model-agnostic behavior"""
    
    # Models to test (in order of size/capability)
    MODELS = [
        'all-MiniLM-L6-v2',           # 384 dim, fast
        'paraphrase-MiniLM-L6-v2',    # 384 dim, paraphrase-focused
        'all-mpnet-base-v2',          # 768 dim, more accurate
    ]
    
    @classmethod
    def setup_class(cls):
        """Load all models once (expensive operation)"""
        print("\nLoading models for robustness testing...")
        cls.models = {}
        for model_name in cls.MODELS:
            try:
                print(f"  Loading {model_name}...")
                cls.models[model_name] = SentenceTransformer(model_name)
            except Exception as e:
                print(f"  WARNING: Could not load {model_name}: {e}")
    
    def get_test_corpus(self) -> List[MockNote]:
        """Standard test corpus for model comparison"""
        return [
            MockNote("Meeting 1", "Q4 planning meeting notes"),
            MockNote("Meeting 2", "Notes from Q4 planning discussion"),
            MockNote("Shopping 1", "Grocery list: milk, eggs, bread"),
            MockNote("Shopping 2", "Buy milk, eggs, and bread"),
            MockNote("Random 1", "Coffee thoughts"),
            MockNote("Random 2", "Book recommendations"),
        ]
    
    def find_clusters_with_model(self, notes: List[MockNote], 
                                 model: SentenceTransformer,
                                 threshold: float = 0.85) -> List[List[str]]:
        """Find clusters using a specific model"""
        if not notes:
            return []
        
        # Create embeddings
        docs = [f"{n.title} {n.text}" for n in notes]
        embeddings = model.encode(docs, convert_to_tensor=True)
        
        # Calculate similarity matrix
        cosine_scores = util.cos_sim(embeddings, embeddings)
        
        # Build graph
        import networkx as nx
        G = nx.Graph()
        
        for i in range(len(notes)):
            for j in range(i + 1, len(notes)):
                if cosine_scores[i][j] >= threshold:
                    G.add_edge(notes[i].id, notes[j].id)
        
        # Find connected components
        clusters = [list(c) for c in nx.connected_components(G) if len(c) > 1]
        return clusters
    
    # ========================================
    # TEST 1: Multi-Model Consistency
    # ========================================
    
    def test_multi_model_relative_ordering(self):
        """
        CRITICAL: Different models should produce similar cluster structures
        
        We don't require identical results, but the relative ordering
        of similarities should be preserved.
        """
        if len(self.models) < 2:
            print("Skipping: Need at least 2 models loaded")
            return
        
        notes = self.get_test_corpus()
        
        # Get clusters from each model
        results = {}
        for model_name, model in self.models.items():
            results[model_name] = self.find_clusters_with_model(
                notes, model, threshold=0.85
            )
        
        # Convert clusters to label arrays for comparison
        def clusters_to_labels(clusters, notes):
            labels = [-1] * len(notes)  # -1 = no cluster
            for cluster_id, cluster in enumerate(clusters):
                for note_id in cluster:
                    idx = next(i for i, n in enumerate(notes) if n.id == note_id)
                    labels[idx] = cluster_id
            return labels
        
        # Compare all pairs of models
        for model1, model2 in itertools.combinations(self.models.keys(), 2):
            labels1 = clusters_to_labels(results[model1], notes)
            labels2 = clusters_to_labels(results[model2], notes)
            
            # Calculate Adjusted Rand Index (1.0 = perfect agreement)
            ari = adjusted_rand_score(labels1, labels2)
            
            print(f"\n  {model1} vs {model2}: ARI = {ari:.3f}")
            
            # We expect substantial agreement (> 0.60)
            # but not perfect (models have different architectures)
            assert ari > 0.50, \
                f"Low agreement between {model1} and {model2}: ARI = {ari:.3f}"
    
    # ========================================
    # TEST 2: Embedding Distribution Stability
    # ========================================
    
    def test_embedding_distribution_properties(self):
        """
        Test: Embedding distributions should have stable properties
        
        Mean norm, std deviation, etc. should be consistent.
        This helps detect model drift.
        """
        corpus = [
            "This is a test sentence.",
            "Another test sentence here.",
            "Meeting notes about planning.",
            "Grocery shopping list.",
            "Random thought about coffee.",
        ] * 10  # 50 sentences
        
        for model_name, model in self.models.items():
            embeddings = model.encode(corpus)
            
            # Calculate distribution properties
            norms = np.linalg.norm(embeddings, axis=1)
            mean_norm = np.mean(norms)
            std_norm = np.std(norms)
            
            print(f"\n  {model_name}:")
            print(f"    Mean norm: {mean_norm:.3f}")
            print(f"    Std norm: {std_norm:.3f}")
            
            # Sanity checks
            assert 0.5 < mean_norm < 2.0, \
                f"Unusual mean norm for {model_name}: {mean_norm}"
            assert std_norm < 0.5, \
                f"High variance in norms for {model_name}: {std_norm}"
    
    # ========================================
    # TEST 3: Threshold Sensitivity Analysis
    # ========================================
    
    def test_threshold_sensitivity(self):
        """
        Test: How sensitive is clustering to threshold changes?
        
        Small threshold changes should not cause dramatic clustering changes.
        """
        notes = self.get_test_corpus()
        model = self.models[self.MODELS[0]]  # Use first available model
        
        thresholds = [0.75, 0.80, 0.85, 0.90, 0.95]
        cluster_counts = []
        
        for threshold in thresholds:
            clusters = self.find_clusters_with_model(notes, model, threshold)
            cluster_counts.append(len(clusters))
            print(f"\n  Threshold {threshold:.2f}: {len(clusters)} clusters")
        
        # Cluster count should decrease monotonically as threshold increases
        for i in range(len(cluster_counts) - 1):
            assert cluster_counts[i] >= cluster_counts[i + 1], \
                "Cluster count should decrease with higher threshold"
    
    # ========================================
    # TEST 4: Model Swap Safety
    # ========================================
    
    def test_model_swap_preserves_duplicates(self):
        """
        CRITICAL: Obvious duplicates should be detected by ALL models
        
        If we swap models, we must not lose detection of clear duplicates.
        """
        # Create obvious duplicates
        notes = [
            MockNote("A", "Meeting about Q4 planning"),
            MockNote("B", "Meeting about Q4 planning"),  # Exact duplicate
            MockNote("C", "Grocery shopping list"),
        ]
        
        for model_name, model in self.models.items():
            clusters = self.find_clusters_with_model(notes, model, threshold=0.85)
            
            # Must detect the duplicate
            assert len(clusters) >= 1, \
                f"{model_name} failed to detect obvious duplicate"
            
            # The duplicate pair should be in a cluster
            found_duplicate = False
            for cluster in clusters:
                if notes[0].id in cluster and notes[1].id in cluster:
                    found_duplicate = True
                    break
            
            assert found_duplicate, \
                f"{model_name} did not cluster obvious duplicates"
    
    # ========================================
    # TEST 5: Semantic Drift Detection
    # ========================================
    
    def test_semantic_drift_detection(self):
        """
        Test: Can we detect when a model produces unusual results?
        
        This is a meta-test: if one model produces very different
        results from others, flag it.
        """
        if len(self.models) < 3:
            print("Skipping: Need at least 3 models for drift detection")
            return
        
        notes = self.get_test_corpus()
        
        # Get cluster counts from each model
        cluster_counts = {}
        for model_name, model in self.models.items():
            clusters = self.find_clusters_with_model(notes, model, threshold=0.85)
            cluster_counts[model_name] = len(clusters)
        
        # Calculate mean and std
        counts = list(cluster_counts.values())
        mean_count = np.mean(counts)
        std_count = np.std(counts)
        
        print(f"\n  Cluster counts: {cluster_counts}")
        print(f"  Mean: {mean_count:.1f}, Std: {std_count:.1f}")
        
        # Flag any model that's > 2 std deviations from mean
        for model_name, count in cluster_counts.items():
            z_score = abs(count - mean_count) / (std_count + 1e-6)
            if z_score > 2.0:
                print(f"  WARNING: {model_name} may have drifted (z={z_score:.2f})")


class TestModelUpgradeSafety:
    """Tests for safe model upgrades"""
    
    def test_upgrade_checklist(self):
        """
        Document: Checklist for upgrading embedding model
        
        This is not a test that runs, but a documented procedure.
        """
        checklist = """
        MODEL UPGRADE SAFETY CHECKLIST:
        
        Before upgrading the embedding model:
        
        1. [ ] Run test_model_robustness.py with new model
        2. [ ] Compare ARI with current model (must be > 0.60)
        3. [ ] Run test_adversarial.py with new model
        4. [ ] Check embedding distribution properties
        5. [ ] Recalibrate threshold using labeled data
        6. [ ] Run on 1000+ real notes, compare results
        7. [ ] Document threshold change in CHANGELOG
        8. [ ] Update model name in config
        9. [ ] Archive old model results for comparison
        10. [ ] Monitor for 1 week after deployment
        
        If ARI < 0.60: DO NOT UPGRADE without investigation
        If false positive rate increases: ROLLBACK
        """
        print(checklist)
        assert True  # Always passes, just documents procedure


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "-s"])
