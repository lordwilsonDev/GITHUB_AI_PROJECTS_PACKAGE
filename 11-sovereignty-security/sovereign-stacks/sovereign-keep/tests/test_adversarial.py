#!/usr/bin/env python3
"""
Adversarial Semantic Testing

Tests designed to break the system with semantically challenging inputs.
These represent real-world failure modes that simple fuzzing won't catch.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import random
import string
from typing import List, Tuple

from src.analysis import SemanticAuditor
from sentence_transformers import util


class MockNote:
    """Lightweight note for testing"""
    def __init__(self, title: str, text: str, note_id: str = None):
        self.title = title
        self.text = text
        self.id = note_id or f"note_{random.randint(1000, 9999)}"
        self.trashed = False
        self.archived = False


class TestAdversarialSemantics:
    """Adversarial test suite for semantic edge cases"""
    
    def setup_method(self):
        """Initialize auditor for each test"""
        self.auditor = SemanticAuditor(None)
        self.threshold = 0.85
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Helper to calculate similarity between two texts"""
        embeddings = self.auditor.model.encode([text1, text2])
        return util.cos_sim(embeddings[0], embeddings[1]).item()
    
    # ========================================
    # ADVERSARIAL SET 1: Opposite Meanings
    # ========================================
    
    OPPOSITE_PAIRS = [
        ("I support this plan", "I do NOT support this plan"),
        ("This is good", "This is bad"),
        ("Meeting went well", "Meeting was a disaster"),
        ("Approve the budget", "Reject the budget"),
        ("Buy milk", "Don't buy milk"),
        ("Project succeeded", "Project failed"),
        ("Accept the proposal", "Decline the proposal"),
        ("Increase spending", "Decrease spending"),
        ("Hire more staff", "Fire staff"),
        ("Open the account", "Close the account"),
    ]
    
    def test_opposite_meanings_must_not_cluster(self):
        """
        CRITICAL: Opposite meanings must NOT be considered duplicates
        
        False positives here are catastrophic - they would merge
        contradictory information.
        """
        failures = []
        
        for text1, text2 in self.OPPOSITE_PAIRS:
            sim = self.calculate_similarity(text1, text2)
            
            # These MUST NOT cluster together
            # Use 0.70 as hard limit (well below 0.85 threshold)
            if sim >= 0.70:
                failures.append({
                    'text1': text1,
                    'text2': text2,
                    'similarity': sim,
                })
        
        assert len(failures) == 0, \
            f"CRITICAL: {len(failures)} opposite pairs incorrectly similar:\\n" + \
            "\\n".join([f"  {f['text1']} <-> {f['text2']} = {f['similarity']:.3f}" 
                       for f in failures])
    
    # ========================================
    # ADVERSARIAL SET 2: Boilerplate Camouflage
    # ========================================
    
    def test_boilerplate_camouflage_95_percent_overlap(self):
        """
        CRITICAL: High boilerplate overlap must not hide semantic differences
        
        Real notes often have standard headers/footers. The system must
        focus on the unique content.
        """
        boilerplate = "Meeting Notes - Q4 2023\\n" + \
                     "Attendees: Team leads\\n" + \
                     "Duration: 1 hour\\n" + \
                     "Location: Conference Room A\\n" + \
                     "Standard agenda items discussed.\\n" * 10
        
        variant1 = boilerplate + "\\nDecision: APPROVE project funding"
        variant2 = boilerplate + "\\nDecision: REJECT project funding"
        
        sim = self.calculate_similarity(variant1, variant2)
        
        # Despite 95%+ overlap, these should NOT cluster
        assert sim < self.threshold, \
            f"Boilerplate camouflage failed: {sim:.3f} >= {self.threshold} " + \
            f"(95% identical but opposite decisions)"
    
    def test_boilerplate_camouflage_email_signatures(self):
        """
        Test: Email-style notes with long signatures
        """
        signature = "\\n\\n---\\nBest regards,\\nJohn Smith\\n" + \
                   "Senior Project Manager\\n" + \
                   "Company Inc.\\n" + \
                   "Phone: 555-1234\\n" + \
                   "Email: john@company.com\\n"
        
        email1 = "Please proceed with the implementation." + signature
        email2 = "Please halt the implementation immediately." + signature
        
        sim = self.calculate_similarity(email1, email2)
        
        assert sim < 0.75, \
            f"Email signature camouflage failed: {sim:.3f}"
    
    # ========================================
    # ADVERSARIAL SET 3: Entropy Gaming
    # ========================================
    
    def test_entropy_gaming_random_padding(self):
        """
        CRITICAL: Random character padding must not inflate vitality
        
        Users might accidentally (or maliciously) add random text.
        The system should not reward this.
        """
        trivial = "Coffee"
        gamed = "Coffee " + ''.join(random.choices(string.ascii_letters, k=200))
        
        vitality_trivial = self.auditor.calculate_vitality(
            MockNote("Trivial", trivial)
        )
        vitality_gamed = self.auditor.calculate_vitality(
            MockNote("Gamed", gamed)
        )
        
        # Random padding should not dramatically increase vitality
        # Allow at most 2x increase
        assert vitality_gamed < vitality_trivial * 2.0, \
            f"Entropy gaming succeeded: {vitality_gamed:.3f} >= {vitality_trivial * 2.0:.3f}"
    
    def test_entropy_gaming_repeated_rare_words(self):
        """
        Test: Repeating rare words to game entropy
        """
        normal = "Buy groceries: milk, eggs, bread"
        gamed = "Buy groceries: milk, eggs, bread, " + \
                "antidisestablishmentarianism " * 10
        
        vitality_normal = self.auditor.calculate_vitality(
            MockNote("Normal", normal)
        )
        vitality_gamed = self.auditor.calculate_vitality(
            MockNote("Gamed", gamed)
        )
        
        # Repeated rare words should not dramatically increase vitality
        assert vitality_gamed < vitality_normal * 3.0, \
            f"Rare word gaming succeeded: {vitality_gamed:.3f}"
    
    # ========================================
    # ADVERSARIAL SET 4: Topic Drift
    # ========================================
    
    TOPIC_DRIFT_PAIRS = [
        ("Q4 planning meeting notes", "Q4 planning action items"),
        ("Project proposal draft", "Project proposal rejection"),
        ("Bug report: login fails", "Bug fix: login works"),
        ("Interview candidate feedback", "Interview candidate rejection"),
        ("Budget request for Q4", "Budget approval for Q4"),
    ]
    
    def test_topic_drift_borderline_cases(self):
        """
        Test: Related but distinct notes should be borderline
        
        These are the hardest cases - same topic, different intent.
        They should be similar but not cluster together.
        """
        for text1, text2 in self.TOPIC_DRIFT_PAIRS:
            sim = self.calculate_similarity(text1, text2)
            
            # Should be related (> 0.60) but not duplicates (< 0.85)
            assert 0.50 < sim < self.threshold, \
                f"Topic drift mishandled: {text1} <-> {text2} = {sim:.3f} " + \
                f"(expected 0.50 < sim < {self.threshold})"
    
    # ========================================
    # ADVERSARIAL SET 5: Negation Blindness
    # ========================================
    
    NEGATION_PAIRS = [
        ("This is important", "This is not important"),
        ("We should continue", "We should not continue"),
        ("The test passed", "The test did not pass"),
        ("I agree with this", "I do not agree with this"),
        ("This works correctly", "This does not work correctly"),
    ]
    
    def test_negation_detection(self):
        """
        CRITICAL: Negations must be detected
        
        Adding "not" completely flips meaning but only changes
        one word. This is a classic NLP failure mode.
        """
        failures = []
        
        for text1, text2 in self.NEGATION_PAIRS:
            sim = self.calculate_similarity(text1, text2)
            
            # Negations should significantly reduce similarity
            if sim >= 0.75:
                failures.append({
                    'text1': text1,
                    'text2': text2,
                    'similarity': sim,
                })
        
        assert len(failures) == 0, \
            f"Negation blindness detected in {len(failures)} cases:\\n" + \
            "\\n".join([f"  {f['text1']} <-> {f['text2']} = {f['similarity']:.3f}" 
                       for f in failures])
    
    # ========================================
    # ADVERSARIAL SET 6: Homograph Confusion
    # ========================================
    
    def test_homograph_confusion(self):
        """
        Test: Words with multiple meanings (homographs)
        
        "Lead" (metal) vs "Lead" (guide)
        "Tear" (rip) vs "Tear" (cry)
        """
        text1 = "The lead pipe is heavy"
        text2 = "I will lead the team"
        
        sim = self.calculate_similarity(text1, text2)
        
        # These should not be very similar despite shared word
        assert sim < 0.70, \
            f"Homograph confusion: {sim:.3f} (expected < 0.70)"
    
    # ========================================
    # ADVERSARIAL SET 7: Temporal Confusion
    # ========================================
    
    TEMPORAL_PAIRS = [
        ("Meeting scheduled for tomorrow", "Meeting was yesterday"),
        ("Will do this next week", "Did this last week"),
        ("Planning for future", "Reviewing the past"),
        ("Upcoming deadline", "Missed deadline"),
    ]
    
    def test_temporal_confusion(self):
        """
        Test: Temporal opposites should not cluster
        
        Future vs past tense can completely change meaning.
        """
        for text1, text2 in self.TEMPORAL_PAIRS:
            sim = self.calculate_similarity(text1, text2)
            
            # Temporal opposites should not cluster
            assert sim < self.threshold, \
                f"Temporal confusion: {text1} <-> {text2} = {sim:.3f}"
    
    # ========================================
    # ADVERSARIAL SET 8: Numeric Confusion
    # ========================================
    
    def test_numeric_confusion(self):
        """
        Test: Different numbers should reduce similarity
        
        "Budget: $1,000" vs "Budget: $1,000,000" are very different.
        """
        text1 = "Budget approved: $1,000"
        text2 = "Budget approved: $1,000,000"
        
        sim = self.calculate_similarity(text1, text2)
        
        # 1000x difference should prevent clustering
        assert sim < self.threshold, \
            f"Numeric confusion: {sim:.3f} (1000x difference ignored)"
    
    # ========================================
    # ADVERSARIAL SET 9: Sarcasm/Irony
    # ========================================
    
    def test_sarcasm_detection_limitation(self):
        """
        KNOWN LIMITATION: Sarcasm is hard to detect
        
        This test documents a known weakness. We expect it to fail
        but want to track it.
        """
        literal = "Great job on the project"
        sarcastic = "Great job on the project (sarcasm)"
        
        sim = self.calculate_similarity(literal, sarcastic)
        
        # This will likely fail - sarcasm is hard
        # We document it as a known limitation
        if sim >= self.threshold:
            print(f"WARNING: Sarcasm not detected (sim={sim:.3f})")
            print("This is a known limitation of embedding models")
    
    # ========================================
    # ADVERSARIAL SET 10: Length Exploitation
    # ========================================
    
    def test_length_exploitation_short_vs_long(self):
        """
        Test: Very short notes should not cluster with long notes
        even if the short note is contained in the long one.
        """
        short = "Coffee"
        long = "Coffee " + "and many other important details about the meeting " * 10
        
        sim = self.calculate_similarity(short, long)
        
        # Short note is substring but context is very different
        # Should not cluster
        assert sim < self.threshold, \
            f"Length exploitation: {sim:.3f} (short substring of long)"


class TestAdversarialClustering:
    """Test clustering behavior under adversarial conditions"""
    
    def setup_method(self):
        """Initialize auditor"""
        self.auditor = SemanticAuditor(None)
    
    def test_adversarial_giant_component_prevention(self):
        """
        CRITICAL: Prevent accidental giant components
        
        If many notes are pairwise similar but not all mutually similar,
        the system should not create one giant cluster.
        """
        # Create a "chain" of similar notes
        # A similar to B, B similar to C, C similar to D
        # But A not similar to D
        notes = [
            MockNote("A", "Meeting about Q4 planning"),
            MockNote("B", "Q4 planning and budget"),
            MockNote("C", "Budget review and allocation"),
            MockNote("D", "Allocation of resources"),
        ]
        
        clusters = self.auditor.find_redundancy_clusters(notes, threshold=0.85)
        
        # Should not create one giant cluster
        if clusters:
            max_cluster_size = max(len(c) for c in clusters)
            assert max_cluster_size <= 3, \
                f"Giant component formed: {max_cluster_size} notes in one cluster"
    
    def test_adversarial_all_similar_notes(self):
        """
        Test: What happens when ALL notes are similar?
        
        This is a pathological case but must be handled gracefully.
        """
        # Create 20 nearly identical notes
        notes = [
            MockNote(f"Note {i}", f"Meeting about project planning variant {i}")
            for i in range(20)
        ]
        
        clusters = self.auditor.find_redundancy_clusters(notes, threshold=0.85)
        
        # Should create clusters, not crash
        assert clusters is not None, "System crashed on all-similar input"
        
        # Should not create one giant cluster (unless truly all identical)
        if clusters:
            max_cluster_size = max(len(c) for c in clusters)
            assert max_cluster_size < len(notes), \
                "All notes clustered together (too aggressive)"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "-s"])
