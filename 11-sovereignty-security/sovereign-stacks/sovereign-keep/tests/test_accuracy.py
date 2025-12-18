#!/usr/bin/env python3
"""
Accuracy Tests for Sovereign Keep Protocol
Measures precision, recall, and F1 score for duplicate detection.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from typing import List, Tuple, Set
import networkx as nx
from sentence_transformers import SentenceTransformer, util

from src.analysis import SemanticAuditor


class MockKeepClient:
    """Mock Keep client for testing."""
    pass


class MockNote:
    """Mock note for testing."""
    def __init__(self, note_id, title, text):
        self.id = note_id
        self.title = title
        self.text = text


# ============================================================================
# TEST DATA: LABELED DUPLICATES
# ============================================================================

def get_labeled_dataset() -> Tuple[List[MockNote], Set[Tuple[str, str]]]:
    """
    Create a labeled dataset with known duplicate pairs.
    
    Returns:
        Tuple of (notes, true_duplicate_pairs)
    """
    notes = [
        # Cluster 1: Shopping (duplicates)
        MockNote('1', 'Shopping List', 'Milk, Eggs, Bread, Butter'),
        MockNote('2', 'Grocery Shopping', 'Eggs, Milk, Bread, Butter'),
        MockNote('3', 'Buy Groceries', 'Need to get milk, eggs, and bread'),
        
        # Cluster 2: Meeting notes (duplicates)
        MockNote('4', 'Q4 Planning Meeting', 'Discussed quarterly goals and budget'),
        MockNote('5', 'Meeting Notes - Q4', 'Quarterly planning session, budget review'),
        
        # Cluster 3: Book recommendations (duplicates)
        MockNote('6', 'Books to Read', 'Sapiens, Thinking Fast and Slow, Atomic Habits'),
        MockNote('7', 'Reading List', 'Sapiens by Harari, Thinking Fast and Slow, Atomic Habits'),
        
        # Unique notes (not duplicates)
        MockNote('8', 'Workout Routine', 'Monday: Chest, Tuesday: Back, Wednesday: Legs'),
        MockNote('9', 'Password Reset', 'Need to reset password for email account'),
        MockNote('10', 'Dentist Appointment', 'Appointment on Friday at 2pm'),
        
        # Hard negatives (similar topic, not duplicates)
        MockNote('11', 'Meal Prep Ideas', 'Chicken, Rice, Vegetables, Salad'),  # Similar to shopping but different
        MockNote('12', 'Q1 Planning Meeting', 'First quarter goals and objectives'),  # Similar to Q4 but different
        MockNote('13', 'Podcast Recommendations', 'Huberman Lab, Lex Fridman, Tim Ferriss'),  # Similar to books but different
    ]
    
    # True duplicate pairs (ground truth)
    true_duplicates = {
        ('1', '2'), ('1', '3'), ('2', '3'),  # Shopping cluster
        ('4', '5'),  # Meeting cluster
        ('6', '7'),  # Books cluster
    }
    
    return notes, true_duplicates


# ============================================================================
# ACCURACY METRICS
# ============================================================================

def calculate_metrics(predicted_pairs: Set[Tuple[str, str]], 
                     true_pairs: Set[Tuple[str, str]]) -> dict:
    """
    Calculate precision, recall, and F1 score.
    
    Args:
        predicted_pairs: Set of predicted duplicate pairs
        true_pairs: Set of true duplicate pairs
        
    Returns:
        Dict with precision, recall, f1, tp, fp, fn
    """
    # Normalize pairs (ensure consistent ordering)
    predicted_pairs = {tuple(sorted(p)) for p in predicted_pairs}
    true_pairs = {tuple(sorted(p)) for p in true_pairs}
    
    tp = len(predicted_pairs & true_pairs)  # True positives
    fp = len(predicted_pairs - true_pairs)  # False positives
    fn = len(true_pairs - predicted_pairs)  # False negatives
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'tp': tp,
        'fp': fp,
        'fn': fn
    }


def find_duplicate_pairs(notes: List[MockNote], threshold: float) -> Set[Tuple[str, str]]:
    """
    Find duplicate pairs using the semantic auditor logic.
    
    Args:
        notes: List of notes
        threshold: Similarity threshold
        
    Returns:
        Set of duplicate pairs (note_id, note_id)
    """
    auditor = SemanticAuditor(MockKeepClient())
    
    # Create documents
    docs = [f"{n.title} {n.text}" for n in notes]
    
    # Generate embeddings
    embeddings = auditor.model.encode(docs, convert_to_tensor=True)
    
    # Calculate similarity matrix
    cosine_scores = util.cos_sim(embeddings, embeddings)
    
    # Find pairs above threshold
    pairs = set()
    for i in range(len(notes)):
        for j in range(i + 1, len(notes)):
            if cosine_scores[i][j] >= threshold:
                pairs.add((notes[i].id, notes[j].id))
    
    return pairs


# ============================================================================
# ACCURACY TESTS
# ============================================================================

def test_accuracy_at_default_threshold():
    """
    Test accuracy at default threshold (0.85).
    """
    notes, true_duplicates = get_labeled_dataset()
    predicted_duplicates = find_duplicate_pairs(notes, threshold=0.85)
    
    metrics = calculate_metrics(predicted_duplicates, true_duplicates)
    
    print(f"\n=== Accuracy at threshold 0.85 ===")
    print(f"Precision: {metrics['precision']:.2%}")
    print(f"Recall: {metrics['recall']:.2%}")
    print(f"F1 Score: {metrics['f1']:.2%}")
    print(f"True Positives: {metrics['tp']}")
    print(f"False Positives: {metrics['fp']}")
    print(f"False Negatives: {metrics['fn']}")
    
    # Assertions: We expect high precision and reasonable recall
    assert metrics['precision'] >= 0.70, f"Precision too low: {metrics['precision']:.2%}"
    assert metrics['recall'] >= 0.50, f"Recall too low: {metrics['recall']:.2%}"
    assert metrics['f1'] >= 0.60, f"F1 score too low: {metrics['f1']:.2%}"


def test_threshold_sweep():
    """
    Test accuracy across different thresholds.
    """
    notes, true_duplicates = get_labeled_dataset()
    
    thresholds = [0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
    results = []
    
    print("\n=== Threshold Sweep ===")
    print(f"{'Threshold':<12} {'Precision':<12} {'Recall':<12} {'F1':<12} {'TP':<6} {'FP':<6} {'FN':<6}")
    print("-" * 72)
    
    for threshold in thresholds:
        predicted = find_duplicate_pairs(notes, threshold)
        metrics = calculate_metrics(predicted, true_duplicates)
        results.append((threshold, metrics))
        
        print(f"{threshold:<12.2f} {metrics['precision']:<12.2%} {metrics['recall']:<12.2%} "
              f"{metrics['f1']:<12.2%} {metrics['tp']:<6} {metrics['fp']:<6} {metrics['fn']:<6}")
    
    # Find best F1 score
    best_threshold, best_metrics = max(results, key=lambda x: x[1]['f1'])
    
    print(f"\nBest threshold: {best_threshold:.2f} (F1: {best_metrics['f1']:.2%})")
    
    # Assert that we can achieve reasonable F1 at some threshold
    assert best_metrics['f1'] >= 0.60, "Cannot achieve F1 >= 0.60 at any threshold"


def test_no_false_positives_at_high_threshold():
    """
    Test that high threshold (0.95) produces no false positives.
    """
    notes, true_duplicates = get_labeled_dataset()
    predicted = find_duplicate_pairs(notes, threshold=0.95)
    
    metrics = calculate_metrics(predicted, true_duplicates)
    
    # At very high threshold, we should have high precision (few false positives)
    assert metrics['precision'] >= 0.80 or metrics['fp'] <= 1, \
        f"Too many false positives at threshold 0.95: {metrics['fp']}"


def test_high_recall_at_low_threshold():
    """
    Test that low threshold (0.70) captures most duplicates.
    """
    notes, true_duplicates = get_labeled_dataset()
    predicted = find_duplicate_pairs(notes, threshold=0.70)
    
    metrics = calculate_metrics(predicted, true_duplicates)
    
    # At low threshold, we should have high recall (catch most duplicates)
    assert metrics['recall'] >= 0.70, \
        f"Recall too low at threshold 0.70: {metrics['recall']:.2%}"


def test_exact_duplicates_always_detected():
    """
    Test that exact duplicates are always detected.
    """
    exact_notes = [
        MockNote('1', 'Test', 'This is a test note'),
        MockNote('2', 'Test', 'This is a test note'),  # Exact duplicate
        MockNote('3', 'Different', 'This is completely different'),
    ]
    
    predicted = find_duplicate_pairs(exact_notes, threshold=0.85)
    
    # Should detect the exact duplicate
    assert ('1', '2') in predicted or ('2', '1') in predicted, \
        "Failed to detect exact duplicate"


def test_unrelated_notes_not_matched():
    """
    Test that completely unrelated notes are not matched.
    """
    unrelated_notes = [
        MockNote('1', 'Shopping', 'Milk, Eggs, Bread'),
        MockNote('2', 'Math Homework', 'Solve equations 1-10'),
        MockNote('3', 'Dentist', 'Appointment on Friday'),
    ]
    
    predicted = find_duplicate_pairs(unrelated_notes, threshold=0.85)
    
    # Should find no duplicates
    assert len(predicted) == 0, \
        f"Found false duplicates in unrelated notes: {predicted}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
