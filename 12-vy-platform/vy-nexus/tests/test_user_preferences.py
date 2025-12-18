#!/usr/bin/env python3
"""
Tests for User Preference Tracking Module
"""

import pytest
import sqlite3
import json
import os
import tempfile
from datetime import datetime, timedelta
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.user_preferences import (
    UserPreferenceTracker,
    WorkingStyleAnalyzer,
    PreferenceRecommendationEngine,
    PreferenceCategory
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def preference_tracker(temp_db):
    """Create a preference tracker with temporary database"""
    return UserPreferenceTracker(temp_db)


@pytest.fixture
def working_style_analyzer(temp_db):
    """Create a working style analyzer with temporary database"""
    # First create the interactions and tasks tables
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_type TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_type TEXT,
            status TEXT,
            duration_seconds INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    
    return WorkingStyleAnalyzer(temp_db)


class TestUserPreferenceTracker:
    """Test suite for UserPreferenceTracker"""
    
    def test_initialization(self, preference_tracker):
        """Test that tracker initializes correctly"""
        assert preference_tracker.db_path is not None
        
        # Check tables exist
        conn = sqlite3.connect(preference_tracker.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('user_preferences', 'preference_evidence', 'user_feedback')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert 'user_preferences' in tables
        assert 'preference_evidence' in tables
        assert 'user_feedback' in tables
    
    def test_record_new_preference(self, preference_tracker):
        """Test recording a new preference"""
        pref_id = preference_tracker.record_preference(
            category=PreferenceCategory.COMMUNICATION,
            preference_key="response_style",
            preference_value="concise",
            evidence_type="observed",
            confidence=0.7
        )
        
        assert pref_id > 0
        
        # Verify it was stored
        pref = preference_tracker.get_preference(
            PreferenceCategory.COMMUNICATION,
            "response_style"
        )
        
        assert pref is not None
        assert pref["value"] == "concise"
        assert pref["confidence"] == 0.7
    
    def test_update_existing_preference_reinforcement(self, preference_tracker):
        """Test that reinforcing a preference increases confidence"""
        # Record initial preference
        preference_tracker.record_preference(
            category=PreferenceCategory.TOOLS,
            preference_key="preferred_editor",
            preference_value="vim",
            confidence=0.5
        )
        
        initial_pref = preference_tracker.get_preference(
            PreferenceCategory.TOOLS,
            "preferred_editor",
            min_confidence=0.0
        )
        initial_confidence = initial_pref["confidence"]
        
        # Reinforce the same preference
        preference_tracker.record_preference(
            category=PreferenceCategory.TOOLS,
            preference_key="preferred_editor",
            preference_value="vim",
            confidence=0.6
        )
        
        updated_pref = preference_tracker.get_preference(
            PreferenceCategory.TOOLS,
            "preferred_editor",
            min_confidence=0.0
        )
        
        assert updated_pref["confidence"] > initial_confidence
        assert updated_pref["evidence_count"] == 2
    
    def test_conflicting_preference(self, preference_tracker):
        """Test that conflicting preferences reduce confidence"""
        # Record initial preference
        preference_tracker.record_preference(
            category=PreferenceCategory.TIMING,
            preference_key="preferred_time",
            preference_value="morning",
            confidence=0.7
        )
        
        initial_pref = preference_tracker.get_preference(
            PreferenceCategory.TIMING,
            "preferred_time",
            min_confidence=0.0
        )
        initial_confidence = initial_pref["confidence"]
        
        # Record conflicting preference
        preference_tracker.record_preference(
            category=PreferenceCategory.TIMING,
            preference_key="preferred_time",
            preference_value="evening",
            confidence=0.5
        )
        
        updated_pref = preference_tracker.get_preference(
            PreferenceCategory.TIMING,
            "preferred_time",
            min_confidence=0.0
        )
        
        assert updated_pref["confidence"] < initial_confidence
    
    def test_record_feedback(self, preference_tracker):
        """Test recording user feedback"""
        preference_tracker.record_feedback(
            feedback_type="positive",
            subject="task_completion",
            sentiment="satisfied",
            feedback_text="Great job on automating that workflow!",
            metadata={"task_id": 123}
        )
        
        # Verify feedback was stored
        conn = sqlite3.connect(preference_tracker.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM user_feedback")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 1
    
    def test_get_all_preferences(self, preference_tracker):
        """Test retrieving all preferences"""
        # Record multiple preferences
        preference_tracker.record_preference(
            PreferenceCategory.COMMUNICATION, "style", "concise", confidence=0.8
        )
        preference_tracker.record_preference(
            PreferenceCategory.TOOLS, "editor", "vim", confidence=0.7
        )
        preference_tracker.record_preference(
            PreferenceCategory.TIMING, "time", "morning", confidence=0.6
        )
        
        all_prefs = preference_tracker.get_all_preferences(min_confidence=0.5)
        assert len(all_prefs) == 3
        
        # Test category filter
        comm_prefs = preference_tracker.get_all_preferences(
            category=PreferenceCategory.COMMUNICATION,
            min_confidence=0.5
        )
        assert len(comm_prefs) == 1
        assert comm_prefs[0]["category"] == PreferenceCategory.COMMUNICATION
    
    def test_min_confidence_filter(self, preference_tracker):
        """Test that min_confidence filter works"""
        preference_tracker.record_preference(
            PreferenceCategory.WORKFLOW, "task_type", "automation", confidence=0.9
        )
        preference_tracker.record_preference(
            PreferenceCategory.WORKFLOW, "complexity", "simple", confidence=0.4
        )
        
        # Should only get high confidence preference
        high_conf_prefs = preference_tracker.get_all_preferences(min_confidence=0.7)
        assert len(high_conf_prefs) == 1
        assert high_conf_prefs[0]["key"] == "task_type"
        
        # Should get both with lower threshold
        all_prefs = preference_tracker.get_all_preferences(min_confidence=0.3)
        assert len(all_prefs) == 2


class TestWorkingStyleAnalyzer:
    """Test suite for WorkingStyleAnalyzer"""
    
    def test_analyze_communication_style_insufficient_data(self, working_style_analyzer):
        """Test communication analysis with no data"""
        result = working_style_analyzer.analyze_communication_style()
        assert result["status"] == "insufficient_data"
    
    def test_analyze_communication_style_concise(self, working_style_analyzer):
        """Test detection of concise communication style"""
        conn = sqlite3.connect(working_style_analyzer.db_path)
        cursor = conn.cursor()
        
        # Insert short messages
        for i in range(10):
            cursor.execute("""
                INSERT INTO interactions (interaction_type, metadata)
                VALUES ('user_message', ?)
            """, (json.dumps({"message_length": 30 + i}),))
        
        conn.commit()
        conn.close()
        
        result = working_style_analyzer.analyze_communication_style()
        assert result["style"] == "concise"
        assert result["avg_message_length"] < 50
    
    def test_analyze_communication_style_detailed(self, working_style_analyzer):
        """Test detection of detailed communication style"""
        conn = sqlite3.connect(working_style_analyzer.db_path)
        cursor = conn.cursor()
        
        # Insert long messages
        for i in range(10):
            cursor.execute("""
                INSERT INTO interactions (interaction_type, metadata)
                VALUES ('user_message', ?)
            """, (json.dumps({"message_length": 200 + i * 10}),))
        
        conn.commit()
        conn.close()
        
        result = working_style_analyzer.analyze_communication_style()
        assert result["style"] == "detailed"
        assert result["avg_message_length"] > 150
    
    def test_analyze_task_preferences(self, working_style_analyzer):
        """Test task preference analysis"""
        conn = sqlite3.connect(working_style_analyzer.db_path)
        cursor = conn.cursor()
        
        # Insert various tasks
        task_data = [
            ("automation", "completed", 300),
            ("automation", "completed", 250),
            ("automation", "completed", 400),
            ("research", "completed", 600),
            ("research", "failed", 200),
            ("coding", "completed", 500),
        ]
        
        for task_type, status, duration in task_data:
            cursor.execute("""
                INSERT INTO tasks (task_type, status, duration_seconds)
                VALUES (?, ?, ?)
            """, (task_type, status, duration))
        
        conn.commit()
        conn.close()
        
        result = working_style_analyzer.analyze_task_preferences()
        assert result["most_common_task_type"] == "automation"
        assert "automation" in result["preferred_task_types"]  # 100% completion rate
        assert result["total_tasks"] == 6
    
    def test_analyze_timing_preferences(self, working_style_analyzer):
        """Test timing preference analysis"""
        conn = sqlite3.connect(working_style_analyzer.db_path)
        cursor = conn.cursor()
        
        # Insert interactions at morning hours (keep them all in morning)
        base_time = datetime.now().replace(hour=9, minute=0, second=0)
        for i in range(10):  # Reduced to 10 to stay in morning (9:00-11:30)
            timestamp = (base_time + timedelta(minutes=i * 15)).isoformat()
            cursor.execute("""
                INSERT INTO interactions (timestamp)
                VALUES (?)
            """, (timestamp,))
        
        conn.commit()
        conn.close()
        
        result = working_style_analyzer.analyze_timing_preferences()
        assert result["preferred_time"] == "morning"
        assert 9 in result["peak_hours"]


class TestPreferenceRecommendationEngine:
    """Test suite for PreferenceRecommendationEngine"""
    
    def test_generate_recommendations_empty(self, temp_db):
        """Test recommendation generation with no preferences"""
        engine = PreferenceRecommendationEngine(temp_db)
        recommendations = engine.generate_recommendations()
        assert len(recommendations) == 0
    
    def test_generate_recommendations(self, temp_db):
        """Test recommendation generation with preferences"""
        tracker = UserPreferenceTracker(temp_db)
        engine = PreferenceRecommendationEngine(temp_db)
        
        # Add some preferences
        tracker.record_preference(
            PreferenceCategory.COMMUNICATION,
            "response_style",
            "concise",
            confidence=0.8
        )
        tracker.record_preference(
            PreferenceCategory.TIMING,
            "preferred_work_time",
            "morning",
            confidence=0.75
        )
        
        recommendations = engine.generate_recommendations()
        assert len(recommendations) > 0
        
        # Check that recommendations are sorted by priority and confidence
        for i in range(len(recommendations) - 1):
            current = recommendations[i]
            next_rec = recommendations[i + 1]
            
            priority_order = {"high": 3, "medium": 2, "low": 1}
            current_score = (priority_order.get(current["priority"], 0), current["confidence"])
            next_score = (priority_order.get(next_rec["priority"], 0), next_rec["confidence"])
            
            assert current_score >= next_score
    
    def test_get_preference_summary(self, temp_db):
        """Test preference summary generation"""
        tracker = UserPreferenceTracker(temp_db)
        engine = PreferenceRecommendationEngine(temp_db)
        
        # Add preferences across categories
        tracker.record_preference(
            PreferenceCategory.COMMUNICATION, "style", "concise", confidence=0.9
        )
        tracker.record_preference(
            PreferenceCategory.TOOLS, "editor", "vim", confidence=0.7
        )
        tracker.record_preference(
            PreferenceCategory.TIMING, "time", "morning", confidence=0.6
        )
        
        summary = engine.get_preference_summary()
        
        assert summary["total_preferences"] == 3
        assert summary["high_confidence_count"] == 1  # Only the 0.9 confidence one
        assert len(summary["by_category"]) == 3
        assert "recommendations" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
