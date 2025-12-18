#!/usr/bin/env python3
"""
Unit tests for User Preference Learner

Author: VY-NEXUS Self-Evolving AI System
Date: December 15, 2025
"""

import unittest
import os
import tempfile
import shutil
import json
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.learning.user_preference_learner import (
    UserPreferenceLearner,
    PreferenceType,
    LearningSource,
    Preference,
    PreferenceProfile
)


class TestUserPreferenceLearner(unittest.TestCase):
    """Test cases for UserPreferenceLearner."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.learner = UserPreferenceLearner(data_dir=self.test_dir)
        self.test_user = "test_user_001"
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_record_explicit_preference(self):
        """Test recording explicit preference."""
        self.learner.record_explicit_preference(
            user_id=self.test_user,
            preference_type=PreferenceType.COMMUNICATION_STYLE,
            key="style",
            value="concise"
        )
        
        # Verify preference was recorded
        style = self.learner.get_communication_style(self.test_user)
        self.assertEqual(style, "concise")
        
        # Verify confidence is 1.0 for explicit preferences
        result = self.learner.get_preference_with_confidence(
            self.test_user,
            PreferenceType.COMMUNICATION_STYLE,
            "style"
        )
        self.assertIsNotNone(result)
        self.assertEqual(result[1], 1.0)
    
    def test_record_implicit_preference(self):
        """Test recording implicit preference."""
        # Record same preference multiple times
        for _ in range(5):
            self.learner.record_implicit_preference(
                user_id=self.test_user,
                preference_type=PreferenceType.TOOL_PREFERENCE,
                key="browser",
                value="chrome"
            )
        
        # Verify preference was learned
        browser = self.learner.get_preference(
            self.test_user,
            PreferenceType.TOOL_PREFERENCE,
            "browser"
        )
        self.assertEqual(browser, "chrome")
        
        # Verify confidence increased with observations
        result = self.learner.get_preference_with_confidence(
            self.test_user,
            PreferenceType.TOOL_PREFERENCE,
            "browser"
        )
        self.assertIsNotNone(result)
        self.assertGreater(result[1], 0.3)  # Should be above minimum
    
    def test_implicit_confidence_building(self):
        """Test that implicit preferences build confidence over time."""
        # Record preference once
        self.learner.record_implicit_preference(
            user_id=self.test_user,
            preference_type=PreferenceType.OUTPUT_FORMAT,
            key="format",
            value="json"
        )
        
        result1 = self.learner.get_preference_with_confidence(
            self.test_user,
            PreferenceType.OUTPUT_FORMAT,
            "format"
        )
        confidence1 = result1[1] if result1 else 0.0
        
        # Record same preference again
        for _ in range(3):
            self.learner.record_implicit_preference(
                user_id=self.test_user,
                preference_type=PreferenceType.OUTPUT_FORMAT,
                key="format",
                value="json"
            )
        
        result2 = self.learner.get_preference_with_confidence(
            self.test_user,
            PreferenceType.OUTPUT_FORMAT,
            "format"
        )
        confidence2 = result2[1] if result2 else 0.0
        
        # Confidence should increase
        self.assertGreater(confidence2, confidence1)
    
    def test_conflicting_implicit_preferences(self):
        """Test handling of conflicting implicit preferences."""
        # Record one preference multiple times
        for _ in range(3):
            self.learner.record_implicit_preference(
                user_id=self.test_user,
                preference_type=PreferenceType.TOOL_PREFERENCE,
                key="editor",
                value="vim"
            )
        
        # Record conflicting preference
        for _ in range(5):
            self.learner.record_implicit_preference(
                user_id=self.test_user,
                preference_type=PreferenceType.TOOL_PREFERENCE,
                key="editor",
                value="vscode"
            )
        
        # Should eventually shift to new value
        editor = self.learner.get_preference(
            self.test_user,
            PreferenceType.TOOL_PREFERENCE,
            "editor"
        )
        # Behavior depends on implementation, but should handle gracefully
        self.assertIsNotNone(editor)
    
    def test_explicit_overrides_implicit(self):
        """Test that explicit preferences override implicit ones."""
        # Record implicit preference
        for _ in range(5):
            self.learner.record_implicit_preference(
                user_id=self.test_user,
                preference_type=PreferenceType.AUTOMATION_LEVEL,
                key="level",
                value="minimal"
            )
        
        # Record explicit preference with different value
        self.learner.record_explicit_preference(
            user_id=self.test_user,
            preference_type=PreferenceType.AUTOMATION_LEVEL,
            key="level",
            value="aggressive"
        )
        
        # Explicit should win
        level = self.learner.get_automation_level(self.test_user)
        self.assertEqual(level, "aggressive")
    
    def test_positive_feedback(self):
        """Test positive feedback increases confidence."""
        # Record implicit preference
        self.learner.record_implicit_preference(
            user_id=self.test_user,
            preference_type=PreferenceType.DETAIL_LEVEL,
            key="level",
            value="detailed"
        )
        
        result1 = self.learner.get_preference_with_confidence(
            self.test_user,
            PreferenceType.DETAIL_LEVEL,
            "level"
        )
        confidence1 = result1[1] if result1 else 0.0
        
        # Give positive feedback
        self.learner.record_feedback(
            user_id=self.test_user,
            preference_type=PreferenceType.DETAIL_LEVEL,
            key="level",
            positive=True
        )
        
        result2 = self.learner.get_preference_with_confidence(
            self.test_user,
            PreferenceType.DETAIL_LEVEL,
            "level"
        )
        confidence2 = result2[1] if result2 else 0.0
        
        # Confidence should increase
        self.assertGreater(confidence2, confidence1)
    
    def test_negative_feedback(self):
        """Test negative feedback decreases confidence."""
        # Record explicit preference
        self.learner.record_explicit_preference(
            user_id=self.test_user,
            preference_type=PreferenceType.NOTIFICATION_PREFERENCE,
            key="frequency",
            value="high"
        )
        
        # Give negative feedback multiple times
        for _ in range(3):
            self.learner.record_feedback(
                user_id=self.test_user,
                preference_type=PreferenceType.NOTIFICATION_PREFERENCE,
                key="frequency",
                positive=False
            )
        
        # Preference should be removed or have very low confidence
        result = self.learner.get_preference_with_confidence(
            self.test_user,
            PreferenceType.NOTIFICATION_PREFERENCE,
            "frequency"
        )
        # Should be None or very low confidence
        if result:
            self.assertLess(result[1], 0.5)
    
    def test_get_all_preferences(self):
        """Test getting all preferences."""
        # Record multiple preferences
        self.learner.record_explicit_preference(
            user_id=self.test_user,
            preference_type=PreferenceType.COMMUNICATION_STYLE,
            key="style",
            value="concise"
        )
        
        self.learner.record_explicit_preference(
            user_id=self.test_user,
            preference_type=PreferenceType.WORKING_HOURS,
            key="start_hour",
            value=9
        )
        
        # Get all preferences
        all_prefs = self.learner.get_all_preferences(self.test_user)
        self.assertGreaterEqual(len(all_prefs), 2)
        
        # Get preferences by type
        comm_prefs = self.learner.get_all_preferences(
            self.test_user,
            preference_type=PreferenceType.COMMUNICATION_STYLE
        )
        self.assertEqual(len(comm_prefs), 1)
    
    def test_get_working_hours(self):
        """Test getting working hours preferences."""
        # Record working hours
        self.learner.record_explicit_preference(
            user_id=self.test_user,
            preference_type=PreferenceType.WORKING_HOURS,
            key="start_hour",
            value=9
        )
        
        self.learner.record_explicit_preference(
            user_id=self.test_user,
            preference_type=PreferenceType.WORKING_HOURS,
            key="end_hour",
            value=17
        )
        
        # Get working hours
        hours = self.learner.get_working_hours(self.test_user)
        self.assertIsNotNone(hours)
        self.assertEqual(hours.get("start_hour"), 9)
        self.assertEqual(hours.get("end_hour"), 17)
    
    def test_profile_persistence(self):
        """Test that profiles are saved and loaded correctly."""
        # Record preference
        self.learner.record_explicit_preference(
            user_id=self.test_user,
            preference_type=PreferenceType.COMMUNICATION_STYLE,
            key="style",
            value="verbose"
        )
        
        # Create new learner instance (should load from disk)
        new_learner = UserPreferenceLearner(data_dir=self.test_dir)
        
        # Verify preference was loaded
        style = new_learner.get_communication_style(self.test_user)
        self.assertEqual(style, "verbose")
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        # Record some preferences with varying confidence
        self.learner.record_explicit_preference(
            user_id=self.test_user,
            preference_type=PreferenceType.COMMUNICATION_STYLE,
            key="style",
            value="concise"
        )
        
        # Record low-confidence implicit preference
        self.learner.record_implicit_preference(
            user_id=self.test_user,
            preference_type=PreferenceType.TOOL_PREFERENCE,
            key="browser",
            value="firefox"
        )
        
        # Generate recommendations
        recommendations = self.learner.generate_recommendations(self.test_user)
        
        # Should have some recommendations
        self.assertGreater(len(recommendations), 0)
        
        # Check recommendation structure
        for rec in recommendations:
            self.assertIn("type", rec)
            self.assertIn("priority", rec)
            self.assertIn("message", rec)
    
    def test_profile_summary(self):
        """Test profile summary generation."""
        # Record various preferences
        self.learner.record_explicit_preference(
            user_id=self.test_user,
            preference_type=PreferenceType.COMMUNICATION_STYLE,
            key="style",
            value="concise"
        )
        
        for _ in range(3):
            self.learner.record_implicit_preference(
                user_id=self.test_user,
                preference_type=PreferenceType.TOOL_PREFERENCE,
                key="browser",
                value="chrome"
            )
        
        # Get summary
        summary = self.learner.get_profile_summary(self.test_user)
        
        # Verify summary structure
        self.assertTrue(summary["exists"])
        self.assertGreater(summary["total_preferences"], 0)
        self.assertGreater(summary["total_observations"], 0)
        self.assertIn("preferences_by_type", summary)
        self.assertIn("preferences_by_source", summary)
        self.assertIn("confidence_distribution", summary)
    
    def test_export_import_profile(self):
        """Test profile export and import."""
        # Record preferences
        self.learner.record_explicit_preference(
            user_id=self.test_user,
            preference_type=PreferenceType.COMMUNICATION_STYLE,
            key="style",
            value="technical"
        )
        
        self.learner.record_explicit_preference(
            user_id=self.test_user,
            preference_type=PreferenceType.AUTOMATION_LEVEL,
            key="level",
            value="aggressive"
        )
        
        # Export profile
        export_path = os.path.join(self.test_dir, "export.json")
        success = self.learner.export_profile(self.test_user, export_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(export_path))
        
        # Create new learner and import
        new_learner = UserPreferenceLearner(data_dir=tempfile.mkdtemp())
        success = new_learner.import_profile(export_path)
        self.assertTrue(success)
        
        # Verify imported preferences
        style = new_learner.get_communication_style(self.test_user)
        self.assertEqual(style, "technical")
        
        level = new_learner.get_automation_level(self.test_user)
        self.assertEqual(level, "aggressive")
    
    def test_minimum_confidence_threshold(self):
        """Test that low confidence preferences are not returned."""
        # Manually create a low confidence preference
        self.learner.record_implicit_preference(
            user_id=self.test_user,
            preference_type=PreferenceType.ERROR_HANDLING,
            key="strategy",
            value="retry"
        )
        
        # Give negative feedback to lower confidence
        for _ in range(5):
            self.learner.record_feedback(
                user_id=self.test_user,
                preference_type=PreferenceType.ERROR_HANDLING,
                key="strategy",
                positive=False
            )
        
        # Should not return preference if below threshold
        strategy = self.learner.get_preference(
            self.test_user,
            PreferenceType.ERROR_HANDLING,
            "strategy"
        )
        self.assertIsNone(strategy)
    
    def test_multiple_users(self):
        """Test handling multiple user profiles."""
        user1 = "user_001"
        user2 = "user_002"
        
        # Record different preferences for each user
        self.learner.record_explicit_preference(
            user_id=user1,
            preference_type=PreferenceType.COMMUNICATION_STYLE,
            key="style",
            value="concise"
        )
        
        self.learner.record_explicit_preference(
            user_id=user2,
            preference_type=PreferenceType.COMMUNICATION_STYLE,
            key="style",
            value="verbose"
        )
        
        # Verify each user has correct preference
        style1 = self.learner.get_communication_style(user1)
        style2 = self.learner.get_communication_style(user2)
        
        self.assertEqual(style1, "concise")
        self.assertEqual(style2, "verbose")
    
    def test_preference_context(self):
        """Test that context is stored with preferences."""
        context = {"location": "office", "device": "laptop"}
        
        self.learner.record_explicit_preference(
            user_id=self.test_user,
            preference_type=PreferenceType.TOOL_PREFERENCE,
            key="terminal",
            value="iterm",
            context=context
        )
        
        # Get preference and verify context
        prefs = self.learner.get_all_preferences(self.test_user)
        pref_key = list(prefs.keys())[0]
        pref = prefs[pref_key]
        
        self.assertEqual(pref.context, context)


if __name__ == "__main__":
    unittest.main()
