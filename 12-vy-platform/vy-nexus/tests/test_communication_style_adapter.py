#!/usr/bin/env python3
"""
Comprehensive test suite for Communication Style Adapter
Tests all functionality including style adaptation, feedback processing, and pattern learning.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import json
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.adaptation.communication_style_adapter import CommunicationStyleAdapter


class TestCommunicationStyleAdapter(unittest.TestCase):
    """Test suite for Communication Style Adapter."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.adapter = CommunicationStyleAdapter(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    # ===== Initialization Tests =====
    
    def test_initialization(self):
        """Test adapter initialization."""
        self.assertIsNotNone(self.adapter)
        self.assertTrue(Path(self.test_dir).exists())
        self.assertIn("tone", self.adapter.dimensions)
        self.assertIn("verbosity", self.adapter.dimensions)
    
    def test_default_style_loaded(self):
        """Test that default style is properly loaded."""
        self.assertEqual(self.adapter.default_style["tone"], "professional")
        self.assertEqual(self.adapter.default_style["verbosity"], "moderate")
        self.assertEqual(self.adapter.default_style["technical_depth"], "intermediate")
    
    def test_data_files_created(self):
        """Test that data files are created."""
        self.assertTrue(self.adapter.profiles_file.parent.exists())
        self.assertTrue(self.adapter.interactions_file.parent.exists())
    
    # ===== User Profile Tests =====
    
    def test_create_user_profile(self):
        """Test creating a user profile."""
        profile = self.adapter.create_user_profile("user_001")
        
        self.assertEqual(profile["user_id"], "user_001")
        self.assertIn("style", profile)
        self.assertIn("confidence_scores", profile)
        self.assertEqual(profile["interaction_count"], 0)
    
    def test_create_profile_with_preferences(self):
        """Test creating profile with initial preferences."""
        prefs = {"tone": "casual", "verbosity": "concise"}
        profile = self.adapter.create_user_profile("user_002", prefs)
        
        self.assertEqual(profile["style"]["tone"], "casual")
        self.assertEqual(profile["style"]["verbosity"], "concise")
    
    def test_profile_persistence(self):
        """Test that profiles are persisted."""
        self.adapter.create_user_profile("user_003")
        
        # Create new adapter instance
        new_adapter = CommunicationStyleAdapter(data_dir=self.test_dir)
        
        self.assertIn("user_003", new_adapter.profiles["users"])
    
    # ===== Interaction Recording Tests =====
    
    def test_record_interaction(self):
        """Test recording an interaction."""
        self.adapter.create_user_profile("user_001")
        
        interaction = self.adapter.record_interaction(
            user_id="user_001",
            message="Hello, how are you?",
            response="I'm doing well, thank you!"
        )
        
        self.assertEqual(interaction["user_id"], "user_001")
        self.assertIn("timestamp", interaction)
        self.assertIn("analysis", interaction)
    
    def test_interaction_analysis(self):
        """Test interaction analysis."""
        self.adapter.create_user_profile("user_001")
        
        interaction = self.adapter.record_interaction(
            user_id="user_001",
            message="Can you help with API integration?",
            response="Sure, I can help with that."
        )
        
        analysis = interaction["analysis"]
        self.assertIn("message_length", analysis)
        self.assertIn("detected_tone", analysis)
        self.assertIn("technical_terms", analysis)
    
    def test_interaction_count_increment(self):
        """Test that interaction count increments."""
        self.adapter.create_user_profile("user_001")
        
        self.adapter.record_interaction("user_001", "Hi", "Hello")
        self.adapter.record_interaction("user_001", "Thanks", "You're welcome")
        
        profile = self.adapter.profiles["users"]["user_001"]
        self.assertEqual(profile["interaction_count"], 2)
    
    def test_interaction_with_context(self):
        """Test recording interaction with context."""
        self.adapter.create_user_profile("user_001")
        
        interaction = self.adapter.record_interaction(
            user_id="user_001",
            message="Help needed",
            response="I'm here to help",
            context={"urgency": "high", "task_type": "technical"}
        )
        
        self.assertEqual(interaction["context"]["urgency"], "high")
        self.assertEqual(interaction["context"]["task_type"], "technical")
    
    # ===== Analysis Tests =====
    
    def test_complexity_assessment(self):
        """Test text complexity assessment."""
        simple_text = "Hi there"
        complex_text = "The implementation requires sophisticated algorithmic optimization. We need to consider performance implications."
        
        simple_complexity = self.adapter._assess_complexity(simple_text)
        complex_complexity = self.adapter._assess_complexity(complex_text)
        
        self.assertIn(simple_complexity, ["low", "medium", "high"])
        self.assertIn(complex_complexity, ["low", "medium", "high"])
    
    def test_tone_detection(self):
        """Test tone detection."""
        formal_text = "Please kindly assist me with this matter"
        casual_text = "Hey, thanks for the help!"
        urgent_text = "Need this ASAP, it's urgent"
        
        self.assertEqual(self.adapter._detect_tone(formal_text), "formal")
        self.assertEqual(self.adapter._detect_tone(casual_text), "casual")
        self.assertEqual(self.adapter._detect_tone(urgent_text), "urgent")
    
    def test_technical_term_counting(self):
        """Test technical term counting."""
        technical_text = "Use API with snake_case variables and camelCase methods"
        simple_text = "Hello world"
        
        tech_count = self.adapter._count_technical_terms(technical_text)
        simple_count = self.adapter._count_technical_terms(simple_text)
        
        self.assertGreater(tech_count, simple_count)
    
    # ===== Feedback Tests =====
    
    def test_record_explicit_feedback(self):
        """Test recording explicit feedback."""
        self.adapter.create_user_profile("user_001")
        
        feedback = self.adapter.record_feedback(
            user_id="user_001",
            feedback_type="too_verbose",
            feedback_data={"message": "Response was too long"},
            is_explicit=True
        )
        
        self.assertEqual(feedback["type"], "too_verbose")
        self.assertTrue(feedback["is_explicit"])
        self.assertEqual(len(self.adapter.feedback["explicit"]), 1)
    
    def test_record_implicit_feedback(self):
        """Test recording implicit feedback."""
        self.adapter.create_user_profile("user_001")
        
        feedback = self.adapter.record_feedback(
            user_id="user_001",
            feedback_type="quick_response_preferred",
            feedback_data={"inferred_from": "user_behavior"},
            is_explicit=False
        )
        
        self.assertFalse(feedback["is_explicit"])
        self.assertEqual(len(self.adapter.feedback["implicit"]), 1)
    
    def test_feedback_triggers_adaptation(self):
        """Test that feedback triggers style adaptation."""
        profile = self.adapter.create_user_profile("user_001")
        original_verbosity = profile["style"]["verbosity"]
        
        self.adapter.record_feedback(
            user_id="user_001",
            feedback_type="too_verbose",
            feedback_data={}
        )
        
        updated_profile = self.adapter.profiles["users"]["user_001"]
        # Verbosity should decrease
        self.assertNotEqual(updated_profile["style"]["verbosity"], original_verbosity)
    
    def test_too_technical_feedback(self):
        """Test adaptation to 'too technical' feedback."""
        profile = self.adapter.create_user_profile(
            "user_001",
            {"technical_depth": "expert"}
        )
        
        self.adapter.record_feedback(
            user_id="user_001",
            feedback_type="too_technical",
            feedback_data={}
        )
        
        updated_profile = self.adapter.profiles["users"]["user_001"]
        # Technical depth should decrease
        self.assertNotEqual(
            updated_profile["style"]["technical_depth"],
            "expert"
        )
    
    def test_needs_more_detail_feedback(self):
        """Test adaptation to 'needs more detail' feedback."""
        profile = self.adapter.create_user_profile(
            "user_001",
            {"verbosity": "concise"}
        )
        
        self.adapter.record_feedback(
            user_id="user_001",
            feedback_type="needs_more_detail",
            feedback_data={}
        )
        
        updated_profile = self.adapter.profiles["users"]["user_001"]
        # Verbosity should increase
        self.assertNotEqual(updated_profile["style"]["verbosity"], "concise")
    
    # ===== Style Retrieval Tests =====
    
    def test_get_style_for_user(self):
        """Test getting style for a user."""
        self.adapter.create_user_profile(
            "user_001",
            {"tone": "friendly", "verbosity": "detailed"}
        )
        
        style_config = self.adapter.get_style_for_user("user_001")
        
        self.assertEqual(style_config["user_id"], "user_001")
        self.assertEqual(style_config["style"]["tone"], "friendly")
        self.assertEqual(style_config["style"]["verbosity"], "detailed")
    
    def test_get_style_creates_profile_if_missing(self):
        """Test that getting style creates profile if it doesn't exist."""
        style_config = self.adapter.get_style_for_user("new_user")
        
        self.assertEqual(style_config["user_id"], "new_user")
        self.assertIn("new_user", self.adapter.profiles["users"])
    
    def test_context_based_style_adjustment(self):
        """Test context-based style adjustments."""
        self.adapter.create_user_profile("user_001")
        
        # High urgency context
        urgent_style = self.adapter.get_style_for_user(
            "user_001",
            context={"urgency": "high"}
        )
        
        self.assertEqual(urgent_style["style"]["verbosity"], "concise")
        self.assertEqual(urgent_style["style"]["response_format"], "bullet_points")
        self.assertTrue(urgent_style["context_adjusted"])
    
    def test_technical_context_adjustment(self):
        """Test technical task context adjustment."""
        self.adapter.create_user_profile("user_001")
        
        tech_style = self.adapter.get_style_for_user(
            "user_001",
            context={"task_type": "technical"}
        )
        
        self.assertEqual(tech_style["style"]["technical_depth"], "advanced")
        self.assertEqual(tech_style["style"]["explanation_style"], "step_by_step")
    
    def test_creative_context_adjustment(self):
        """Test creative task context adjustment."""
        self.adapter.create_user_profile("user_001")
        
        creative_style = self.adapter.get_style_for_user(
            "user_001",
            context={"task_type": "creative"}
        )
        
        self.assertEqual(creative_style["style"]["tone"], "friendly")
        self.assertEqual(creative_style["style"]["emoji_usage"], "moderate")
    
    # ===== Pattern Learning Tests =====
    
    def test_learn_from_patterns_insufficient_data(self):
        """Test learning with insufficient interaction history."""
        self.adapter.create_user_profile("user_001")
        
        learning = self.adapter.learn_from_patterns("user_001")
        
        self.assertEqual(learning["user_id"], "user_001")
        self.assertIn("Insufficient", learning["message"])
    
    def test_learn_from_patterns_brief_messages(self):
        """Test learning from brief message patterns."""
        self.adapter.create_user_profile("user_001")
        
        # Record several brief interactions
        for i in range(10):
            self.adapter.record_interaction(
                user_id="user_001",
                message="Hi",
                response="Hello"
            )
        
        learning = self.adapter.learn_from_patterns("user_001")
        
        self.assertGreater(learning["interactions_analyzed"], 0)
        self.assertGreater(len(learning["insights"]), 0)
    
    def test_learn_from_patterns_detailed_messages(self):
        """Test learning from detailed message patterns."""
        self.adapter.create_user_profile("user_001")
        
        # Record several detailed interactions
        long_message = "This is a very detailed message with lots of information " * 10
        for i in range(10):
            self.adapter.record_interaction(
                user_id="user_001",
                message=long_message,
                response="Response"
            )
        
        learning = self.adapter.learn_from_patterns("user_001")
        
        # Should suggest detailed verbosity
        suggestions = learning["suggestions"]
        verbosity_suggestions = [
            s for s in suggestions if s["dimension"] == "verbosity"
        ]
        self.assertGreater(len(verbosity_suggestions), 0)
    
    def test_learn_from_patterns_technical_content(self):
        """Test learning from technical content patterns."""
        self.adapter.create_user_profile("user_001")
        
        # Record technical interactions
        for i in range(10):
            self.adapter.record_interaction(
                user_id="user_001",
                message="Need help with API integration using snake_case variables",
                response="Response"
            )
        
        learning = self.adapter.learn_from_patterns("user_001")
        
        # Should suggest advanced technical depth
        suggestions = learning["suggestions"]
        tech_suggestions = [
            s for s in suggestions if s["dimension"] == "technical_depth"
        ]
        self.assertGreater(len(tech_suggestions), 0)
    
    def test_learn_from_patterns_tone_detection(self):
        """Test tone learning from patterns."""
        self.adapter.create_user_profile("user_001")
        
        # Record formal interactions
        for i in range(10):
            self.adapter.record_interaction(
                user_id="user_001",
                message="Please kindly assist me with this matter",
                response="Response"
            )
        
        learning = self.adapter.learn_from_patterns("user_001")
        
        # Should detect formal tone
        insights = learning["insights"]
        formal_insights = [i for i in insights if "formal" in i.lower()]
        self.assertGreater(len(formal_insights), 0)
    
    # ===== Suggestion Application Tests =====
    
    def test_apply_learning_suggestions(self):
        """Test applying learning suggestions."""
        self.adapter.create_user_profile("user_001")
        
        suggestions = [
            {
                "dimension": "verbosity",
                "suggested_value": "detailed",
                "reason": "User provides detailed messages"
            },
            {
                "dimension": "tone",
                "suggested_value": "friendly",
                "reason": "User uses casual language"
            }
        ]
        
        result = self.adapter.apply_learning_suggestions("user_001", suggestions)
        
        self.assertEqual(result["total_applied"], 2)
        self.assertEqual(len(result["adjustments"]), 2)
    
    def test_apply_suggestions_updates_confidence(self):
        """Test that applying suggestions increases confidence scores."""
        profile = self.adapter.create_user_profile("user_001")
        initial_confidence = profile["confidence_scores"]["verbosity"]
        
        suggestions = [{
            "dimension": "verbosity",
            "suggested_value": "detailed",
            "reason": "Test"
        }]
        
        self.adapter.apply_learning_suggestions("user_001", suggestions)
        
        updated_profile = self.adapter.profiles["users"]["user_001"]
        new_confidence = updated_profile["confidence_scores"]["verbosity"]
        
        self.assertGreater(new_confidence, initial_confidence)
    
    def test_apply_suggestions_creates_profile_if_missing(self):
        """Test that applying suggestions creates profile if needed."""
        suggestions = [{
            "dimension": "tone",
            "suggested_value": "professional",
            "reason": "Test"
        }]
        
        result = self.adapter.apply_learning_suggestions("new_user", suggestions)
        
        self.assertIn("new_user", self.adapter.profiles["users"])
        self.assertEqual(result["total_applied"], 1)
    
    # ===== Dimension Adjustment Tests =====
    
    def test_adjust_dimension_increase(self):
        """Test increasing a dimension value."""
        result = self.adapter._adjust_dimension("verbosity", "concise", 1)
        self.assertEqual(result, "moderate")
    
    def test_adjust_dimension_decrease(self):
        """Test decreasing a dimension value."""
        result = self.adapter._adjust_dimension("verbosity", "detailed", -1)
        self.assertEqual(result, "moderate")
    
    def test_adjust_dimension_at_boundary(self):
        """Test adjusting at dimension boundaries."""
        # At minimum
        result = self.adapter._adjust_dimension("verbosity", "concise", -1)
        self.assertEqual(result, "concise")
        
        # At maximum
        result = self.adapter._adjust_dimension("verbosity", "comprehensive", 1)
        self.assertEqual(result, "comprehensive")
    
    def test_adjust_invalid_dimension(self):
        """Test adjusting invalid dimension."""
        result = self.adapter._adjust_dimension("invalid", "value", 1)
        self.assertEqual(result, "value")
    
    # ===== Adaptation Summary Tests =====
    
    def test_get_adaptation_summary_all_users(self):
        """Test getting adaptation summary for all users."""
        # Create some adaptations
        self.adapter.create_user_profile("user_001")
        self.adapter.record_feedback("user_001", "too_verbose", {})
        
        summary = self.adapter.get_adaptation_summary()
        
        self.assertIn("total_adaptations", summary)
        self.assertIn("by_dimension", summary)
        self.assertIn("recent_adaptations", summary)
    
    def test_get_adaptation_summary_specific_user(self):
        """Test getting adaptation summary for specific user."""
        self.adapter.create_user_profile("user_001")
        self.adapter.create_user_profile("user_002")
        
        self.adapter.record_feedback("user_001", "too_verbose", {})
        self.adapter.record_feedback("user_002", "too_technical", {})
        
        summary = self.adapter.get_adaptation_summary("user_001")
        
        # Should only include user_001's adaptations
        self.assertGreater(summary["total_adaptations"], 0)
    
    def test_adaptation_summary_by_dimension(self):
        """Test adaptation summary grouped by dimension."""
        self.adapter.create_user_profile("user_001")
        
        # Multiple adaptations
        self.adapter.record_feedback("user_001", "too_verbose", {})
        self.adapter.record_feedback("user_001", "too_technical", {})
        
        summary = self.adapter.get_adaptation_summary("user_001")
        
        self.assertIn("by_dimension", summary)
        self.assertGreater(len(summary["by_dimension"]), 0)
    
    # ===== Data Persistence Tests =====
    
    def test_profiles_persistence(self):
        """Test that profiles persist across instances."""
        self.adapter.create_user_profile("user_001", {"tone": "casual"})
        
        # Create new instance
        new_adapter = CommunicationStyleAdapter(data_dir=self.test_dir)
        
        self.assertIn("user_001", new_adapter.profiles["users"])
        self.assertEqual(
            new_adapter.profiles["users"]["user_001"]["style"]["tone"],
            "casual"
        )
    
    def test_interactions_persistence(self):
        """Test that interactions persist."""
        self.adapter.create_user_profile("user_001")
        self.adapter.record_interaction("user_001", "Hi", "Hello")
        
        new_adapter = CommunicationStyleAdapter(data_dir=self.test_dir)
        
        self.assertGreater(len(new_adapter.interactions["history"]), 0)
    
    def test_feedback_persistence(self):
        """Test that feedback persists."""
        self.adapter.create_user_profile("user_001")
        self.adapter.record_feedback("user_001", "too_verbose", {})
        
        new_adapter = CommunicationStyleAdapter(data_dir=self.test_dir)
        
        self.assertGreater(len(new_adapter.feedback["explicit"]), 0)
    
    def test_adaptations_persistence(self):
        """Test that adaptations persist."""
        self.adapter.create_user_profile("user_001")
        self.adapter.record_feedback("user_001", "too_verbose", {})
        
        new_adapter = CommunicationStyleAdapter(data_dir=self.test_dir)
        
        self.assertGreater(len(new_adapter.adaptations["history"]), 0)
    
    # ===== Edge Cases =====
    
    def test_empty_message_analysis(self):
        """Test analyzing empty messages."""
        self.adapter.create_user_profile("user_001")
        
        interaction = self.adapter.record_interaction(
            user_id="user_001",
            message="",
            response=""
        )
        
        self.assertIn("analysis", interaction)
        self.assertEqual(interaction["analysis"]["message_length"], 0)
    
    def test_multiple_users(self):
        """Test handling multiple users."""
        self.adapter.create_user_profile("user_001")
        self.adapter.create_user_profile("user_002")
        self.adapter.create_user_profile("user_003")
        
        self.assertEqual(len(self.adapter.profiles["users"]), 3)
    
    def test_rapid_adaptations(self):
        """Test rapid successive adaptations."""
        self.adapter.create_user_profile("user_001")
        
        for i in range(10):
            self.adapter.record_feedback("user_001", "too_verbose", {})
        
        # Should handle multiple adaptations gracefully
        summary = self.adapter.get_adaptation_summary("user_001")
        self.assertGreater(summary["total_adaptations"], 0)


if __name__ == "__main__":
    unittest.main()
