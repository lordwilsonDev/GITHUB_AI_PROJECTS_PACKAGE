#!/usr/bin/env python3
"""
Test script for validating the semantic analysis engine without requiring Google Keep access.
Creates synthetic note data and tests entropy calculation, vector similarity, and clustering.
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.analysis import SemanticAuditor


class MockNote:
    """Mock note object that mimics gkeepapi.node.Note structure"""
    def __init__(self, note_id, title, text, labels=None, archived=False, trashed=False, 
                 created_time=None, updated_time=None):
        self.id = note_id
        self.title = title
        self.text = text
        self.labels = set(labels or [])
        self.archived = archived
        self.trashed = trashed
        
        # Mock timestamps
        class Timestamps:
            def __init__(self, created, updated):
                self.created = created
                self.updated = updated
        
        now = datetime.now()
        self.timestamps = Timestamps(
            created=created_time or now,
            updated=updated_time or now
        )


class MockKeepClient:
    """Mock Google Keep client for testing"""
    def __init__(self, notes):
        self._notes = notes
    
    def all(self):
        """Return all notes"""
        return self._notes
    
    def get(self, note_id):
        """Get note by ID"""
        for note in self._notes:
            if note.id == note_id:
                return note
        return None


def create_test_dataset():
    """Create a synthetic dataset with known duplicates and unique notes"""
    now = datetime.now()
    
    notes = [
        # Cluster 1: Grocery shopping (semantic duplicates)
        MockNote("1", "Groceries", "Buy milk, eggs, bread, butter", 
                updated_time=now - timedelta(days=5)),
        MockNote("2", "Shopping List", "Need to get milk, eggs, and bread from store",
                updated_time=now - timedelta(days=3)),
        MockNote("3", "Store Items", "Grocery shopping: milk eggs bread butter cheese",
                updated_time=now - timedelta(days=1)),
        
        # Cluster 2: Project ideas (semantic duplicates)
        MockNote("4", "App Idea", "Build a mobile app for tracking daily habits and goals",
                updated_time=now - timedelta(days=10)),
        MockNote("5", "Project Concept", "Create habit tracking application for smartphones",
                updated_time=now - timedelta(days=8)),
        MockNote("6", "New App", "Develop a habit tracker app with goal setting features",
                updated_time=now - timedelta(days=2)),
        
        # Cluster 3: Meeting notes (semantic duplicates with label divergence)
        MockNote("7", "Team Meeting", "Discussed Q4 roadmap and sprint planning",
                labels=["Work"], updated_time=now - timedelta(days=7)),
        MockNote("8", "Q4 Planning", "Team sync about roadmap and upcoming sprints",
                labels=["Work"], updated_time=now - timedelta(days=6)),
        
        # Unique notes (high entropy, should not cluster)
        MockNote("9", "Philosophy", "The extended mind thesis suggests cognition extends beyond the brain into tools and environment",
                updated_time=now - timedelta(days=15)),
        MockNote("10", "Recipe", "Chocolate chip cookies: 2 cups flour, 1 cup sugar, 2 eggs, 1 tsp vanilla, chocolate chips",
                updated_time=now - timedelta(days=20)),
        MockNote("11", "Book Quote", "In the beginning was the Word, and the Word was with God",
                updated_time=now - timedelta(days=30)),
        
        # Low entropy note (should have low vitality score)
        MockNote("12", "Test", "test test test",
                updated_time=now - timedelta(days=100)),
        
        # Archived note (should be ignored)
        MockNote("13", "Old Note", "This is archived",
                archived=True, updated_time=now - timedelta(days=200)),
    ]
    
    return notes


def test_entropy_calculation():
    """Test Shannon entropy calculation"""
    print("\n" + "="*70)
    print("TEST 1: Shannon Entropy Calculation")
    print("="*70)
    
    mock_client = MockKeepClient([])
    auditor = SemanticAuditor(mock_client)
    
    test_cases = [
        ("", 0, "Empty string"),
        ("aaaa", 0, "Repeated character (no entropy)"),
        ("abcd", 2.0, "Uniform distribution (max entropy for 4 chars)"),
        ("The quick brown fox jumps over the lazy dog", None, "Natural language"),
        ("test test test", None, "Repetitive text (low entropy)"),
        ("Quantum entanglement demonstrates non-local correlations", None, "Complex text (high entropy)"),
    ]
    
    for text, expected, description in test_cases:
        entropy = auditor.calculate_entropy(text)
        print(f"\n{description}:")
        print(f"  Text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        print(f"  Entropy: {entropy:.4f}")
        if expected is not None:
            status = "✓ PASS" if abs(entropy - expected) < 0.1 else "✗ FAIL"
            print(f"  Expected: {expected:.4f} {status}")


def test_vitality_scores():
    """Test vitality score calculation (entropy + age weighting)"""
    print("\n" + "="*70)
    print("TEST 2: Vitality Score Calculation")
    print("="*70)
    
    notes = create_test_dataset()
    mock_client = MockKeepClient(notes)
    auditor = SemanticAuditor(mock_client)
    
    print("\nCalculating vitality scores for all notes...")
    print(f"{'ID':<5} {'Title':<20} {'Entropy':<10} {'Age (days)':<12} {'Vitality':<10}")
    print("-" * 70)
    
    for note in notes:
        if note.archived or note.trashed:
            continue
        
        text = f"{note.title} {note.text}"
        entropy = auditor.calculate_entropy(text)
        age_days = (datetime.now() - note.timestamps.updated).days
        
        # Vitality formula: α * H(X) + β * (1/age)
        # Using α=1.0, β=10.0 as weights
        vitality = entropy + (10.0 / max(age_days, 1))
        
        print(f"{note.id:<5} {note.title[:20]:<20} {entropy:<10.4f} {age_days:<12} {vitality:<10.4f}")
    
    print("\nInterpretation:")
    print("  High vitality = Recent + Complex (valuable)")
    print("  Low vitality = Old + Simple (candidate for archival)")


def test_semantic_clustering():
    """Test vector similarity and graph-based clustering"""
    print("\n" + "="*70)
    print("TEST 3: Semantic Clustering (Duplicate Detection)")
    print("="*70)
    
    notes = create_test_dataset()
    mock_client = MockKeepClient(notes)
    auditor = SemanticAuditor(mock_client)
    
    print("\nLoading sentence-transformer model (this may take a moment)...")
    
    # Test with different thresholds
    thresholds = [0.70, 0.80, 0.85, 0.90]
    
    for threshold in thresholds:
        print(f"\n--- Threshold: {threshold} ---")
        clusters = auditor.find_redundancy_clusters(threshold=threshold)
        
        if not clusters:
            print("  No clusters found at this threshold")
            continue
        
        print(f"  Found {len(clusters)} cluster(s):")
        
        for i, cluster in enumerate(clusters, 1):
            print(f"\n  Cluster {i} ({len(cluster)} notes):")
            for note_id in cluster:
                note = mock_client.get(note_id)
                print(f"    - [{note.id}] {note.title}: {note.text[:50]}...")
    
    print("\n" + "="*70)
    print("Expected Results:")
    print("  - Cluster 1: Grocery notes (IDs 1, 2, 3)")
    print("  - Cluster 2: App idea notes (IDs 4, 5, 6)")
    print("  - Cluster 3: Meeting notes (IDs 7, 8)")
    print("  - Unique notes should NOT cluster (IDs 9, 10, 11)")
    print("="*70)


def test_pairwise_similarity():
    """Test pairwise similarity scores for manual inspection"""
    print("\n" + "="*70)
    print("TEST 4: Pairwise Similarity Matrix")
    print("="*70)
    
    # Create a small subset for detailed analysis
    notes = [
        MockNote("A", "Groceries", "Buy milk and eggs"),
        MockNote("B", "Shopping", "Need milk and eggs from store"),
        MockNote("C", "Recipe", "Chocolate cake with eggs and milk"),
        MockNote("D", "Philosophy", "The nature of consciousness and reality"),
    ]
    
    mock_client = MockKeepClient(notes)
    auditor = SemanticAuditor(mock_client)
    
    print("\nComparing notes:")
    for note in notes:
        print(f"  [{note.id}] {note.title}: {note.text}")
    
    print("\nGenerating embeddings...")
    docs = [f"{n.title} {n.text}" for n in notes]
    embeddings = auditor.model.encode(docs, convert_to_tensor=True)
    
    from sentence_transformers import util
    cosine_scores = util.cos_sim(embeddings, embeddings)
    
    print("\nSimilarity Matrix:")
    print(f"{'':>5}", end="")
    for note in notes:
        print(f"{note.id:>8}", end="")
    print()
    
    for i, note_i in enumerate(notes):
        print(f"{note_i.id:>5}", end="")
        for j, note_j in enumerate(notes):
            score = cosine_scores[i][j].item()
            print(f"{score:>8.4f}", end="")
        print()
    
    print("\nInterpretation:")
    print("  1.0000 = Identical (diagonal)")
    print("  >0.85  = Very similar (likely duplicates)")
    print("  0.70-0.85 = Somewhat similar")
    print("  <0.70  = Different topics")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("SOVEREIGN KEEP PROTOCOL - SEMANTIC ANALYSIS ENGINE TEST SUITE")
    print("="*70)
    print("\nThis test validates the core algorithms without requiring Google Keep access.")
    print("It uses synthetic note data to test:")
    print("  1. Shannon entropy calculation")
    print("  2. Vitality scoring (entropy + age)")
    print("  3. Semantic clustering (duplicate detection)")
    print("  4. Pairwise similarity analysis")
    
    try:
        test_entropy_calculation()
        test_vitality_scores()
        test_pairwise_similarity()
        test_semantic_clustering()
        
        print("\n" + "="*70)
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\nNext Steps:")
        print("  1. Review the clustering results above")
        print("  2. Tune the similarity threshold if needed (default: 0.85)")
        print("  3. Proceed to implement the SovereignReaper action layer")
        print("  4. Test with real Google Keep data (once auth is resolved)")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
