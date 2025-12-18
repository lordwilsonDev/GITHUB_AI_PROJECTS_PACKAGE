#!/usr/bin/env python3
"""
Unit tests for the Learning Engine module.
"""

import pytest
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.learning_engine import InteractionMonitor, PatternRecognizer, LearningEngine


class TestInteractionMonitor:
    """Test cases for InteractionMonitor class."""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create a temporary database for testing."""
        db_path = tmp_path / "test_interactions.db"
        return str(db_path)
    
    @pytest.fixture
    def monitor(self, temp_db):
        """Create an InteractionMonitor instance for testing."""
        return InteractionMonitor(db_path=temp_db)
    
    def test_database_initialization(self, monitor, temp_db):
        """Test that database is initialized with correct tables."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Check that tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('interactions', 'tasks', 'patterns')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'interactions' in tables
        assert 'tasks' in tables
        assert 'patterns' in tables
        
        conn.close()
    
    def test_log_interaction(self, monitor):
        """Test logging an interaction."""
        interaction_id = monitor.log_interaction(
            interaction_type="command",
            user_input="test command",
            system_response="test response",
            outcome="success",
            success=True,
            duration=1.5,
            context={"test": "context"},
            metadata={"test": "metadata"}
        )
        
        assert interaction_id > 0
        
        # Verify the interaction was stored
        interactions = monitor.get_recent_interactions(limit=1)
        assert len(interactions) == 1
        assert interactions[0]['interaction_type'] == "command"
        assert interactions[0]['user_input'] == "test command"
    
    def test_log_task(self, monitor):
        """Test logging a task."""
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=10)
        
        task_id = monitor.log_task(
            task_description="Test task",
            status="completed",
            start_time=start_time,
            end_time=end_time,
            steps_count=5,
            success=True,
            context={"test": "context"}
        )
        
        assert task_id is not None
        assert len(task_id) == 16  # MD5 hash truncated to 16 chars
    
    def test_get_task_statistics(self, monitor):
        """Test retrieving task statistics."""
        start_time = datetime.now()
        
        # Log some successful tasks
        for i in range(3):
            monitor.log_task(
                task_description=f"Task {i}",
                status="completed",
                start_time=start_time,
                end_time=start_time + timedelta(seconds=5),
                steps_count=3,
                success=True
            )
        
        # Log a failed task
        monitor.log_task(
            task_description="Failed task",
            status="failed",
            start_time=start_time,
            end_time=start_time + timedelta(seconds=2),
            steps_count=1,
            success=False,
            failure_reason="Test failure"
        )
        
        stats = monitor.get_task_statistics()
        
        assert stats['total_tasks'] == 4
        assert stats['successful_tasks'] == 3
        assert stats['failed_tasks'] == 1
        assert stats['success_rate'] == 75.0


class TestPatternRecognizer:
    """Test cases for PatternRecognizer class."""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create a temporary database for testing."""
        db_path = tmp_path / "test_patterns.db"
        # Initialize database
        monitor = InteractionMonitor(db_path=str(db_path))
        return str(db_path)
    
    @pytest.fixture
    def recognizer(self, temp_db):
        """Create a PatternRecognizer instance for testing."""
        return PatternRecognizer(db_path=temp_db)
    
    @pytest.fixture
    def populated_db(self, temp_db):
        """Create a database with sample data."""
        monitor = InteractionMonitor(db_path=temp_db)
        start_time = datetime.now()
        
        # Add recurring tasks
        for i in range(5):
            monitor.log_task(
                task_description="Daily backup",
                status="completed",
                start_time=start_time + timedelta(hours=i),
                end_time=start_time + timedelta(hours=i, seconds=30),
                steps_count=3,
                success=True
            )
        
        # Add another recurring task
        for i in range(3):
            monitor.log_task(
                task_description="Check emails",
                status="completed",
                start_time=start_time + timedelta(hours=i),
                end_time=start_time + timedelta(hours=i, seconds=15),
                steps_count=2,
                success=True
            )
        
        return temp_db
    
    def test_identify_recurring_tasks(self, recognizer, populated_db):
        """Test identification of recurring tasks."""
        patterns = recognizer.identify_recurring_tasks(min_frequency=3)
        
        assert len(patterns) >= 2
        
        # Check that "Daily backup" is identified (frequency 5)
        backup_pattern = next((p for p in patterns if p['task_description'] == "Daily backup"), None)
        assert backup_pattern is not None
        assert backup_pattern['frequency'] == 5
        assert backup_pattern['success_rate'] == 100.0
    
    def test_store_pattern(self, recognizer):
        """Test storing a pattern."""
        pattern_data = {
            'task': 'Daily backup',
            'frequency': 5,
            'avg_duration': 30
        }
        
        pattern_hash = recognizer.store_pattern(
            pattern_type="recurring_task",
            pattern_data=pattern_data,
            confidence=0.9
        )
        
        assert pattern_hash is not None
        assert len(pattern_hash) == 16


class TestLearningEngine:
    """Test cases for LearningEngine class."""
    
    @pytest.fixture
    def temp_config(self, tmp_path):
        """Create a temporary config file."""
        config_path = tmp_path / "test_config.json"
        config = {
            "learning_engine": {
                "enabled": True,
                "monitoring_interval": 60
            }
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)
        return str(config_path)
    
    def test_process_interaction(self, temp_config):
        """Test processing an interaction through the learning engine."""
        engine = LearningEngine(config_path=temp_config)
        
        interaction_id = engine.process_interaction(
            interaction_type="query",
            user_input="What is the weather?",
            system_response="Sunny, 72°F",
            success=True
        )
        
        assert interaction_id > 0
    
    def test_analyze_patterns(self, temp_config):
        """Test pattern analysis."""
        engine = LearningEngine(config_path=temp_config)
        
        # Add some sample data
        start_time = datetime.now()
        for i in range(5):
            engine.monitor.log_task(
                task_description="Test automation",
                status="completed",
                start_time=start_time,
                end_time=start_time + timedelta(seconds=10),
                steps_count=3,
                success=True
            )
        
        analysis = engine.analyze_patterns()
        
        assert 'timestamp' in analysis
        assert 'recurring_tasks' in analysis
        assert 'task_statistics' in analysis
        assert 'automation_opportunities' in analysis
    
    def test_generate_learning_report(self, temp_config):
        """Test learning report generation."""
        engine = LearningEngine(config_path=temp_config)
        
        report = engine.generate_learning_report()
        
        assert "LEARNING ENGINE REPORT" in report
        assert "TASK STATISTICS" in report
        assert "RECURRING TASKS" in report
        assert "AUTOMATION OPPORTUNITIES" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
