#!/usr/bin/env python3
"""
Tests for Repetitive Task Identifier Module
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

from modules.task_identifier import (
    RepetitiveTaskIdentifier,
    TaskSignature
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def task_identifier(temp_db):
    """Create a task identifier with test data"""
    # Create tasks table
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
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
    
    return RepetitiveTaskIdentifier(temp_db)


class TestTaskSignature:
    """Test suite for TaskSignature"""
    
    def test_generate_signature(self):
        """Test signature generation"""
        sig1 = TaskSignature.generate("test_task", {"tools_used": ["vim", "git"]})
        sig2 = TaskSignature.generate("test_task", {"tools_used": ["vim", "git"]})
        
        # Same inputs should produce same signature
        assert sig1 == sig2
        assert len(sig1) == 32  # MD5 hash length
    
    def test_different_signatures(self):
        """Test that different tasks produce different signatures"""
        sig1 = TaskSignature.generate("task1", {"tools_used": ["vim"]})
        sig2 = TaskSignature.generate("task2", {"tools_used": ["vim"]})
        
        assert sig1 != sig2
    
    def test_signature_similarity_exact(self):
        """Test exact signature similarity"""
        sig = TaskSignature.generate("test_task")
        similarity = TaskSignature.similarity(sig, sig)
        
        assert similarity == 1.0
    
    def test_signature_similarity_tools(self):
        """Test similarity based on tools"""
        metadata1 = {"tools_used": ["vim", "git", "python"]}
        metadata2 = {"tools_used": ["vim", "git"]}
        
        sig1 = TaskSignature.generate("task", metadata1)
        sig2 = TaskSignature.generate("task", metadata2)
        
        similarity = TaskSignature.similarity(sig1, sig2, metadata1, metadata2)
        
        # Jaccard similarity: 2 common / 3 total = 0.666...
        assert 0.6 < similarity < 0.7


class TestRepetitiveTaskIdentifier:
    """Test suite for RepetitiveTaskIdentifier"""
    
    def test_initialization(self, task_identifier):
        """Test that identifier initializes correctly"""
        assert task_identifier.db_path is not None
        
        # Check tables exist
        conn = sqlite3.connect(task_identifier.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('task_signatures', 'automation_candidates', 'task_patterns')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert 'task_signatures' in tables
        assert 'automation_candidates' in tables
        assert 'task_patterns' in tables
    
    def test_analyze_task_new(self, task_identifier):
        """Test analyzing a new task"""
        # Insert a test task
        conn = sqlite3.connect(task_identifier.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO tasks (task_type, status, duration_seconds, metadata)
            VALUES ('test_task', 'completed', 300, ?)
        """, (json.dumps({"tools_used": ["vim"]}),))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Analyze the task
        result = task_identifier.analyze_task(task_id)
        
        assert result["status"] == "success"
        assert "signature_id" in result
        assert "automation_score" in result
    
    def test_analyze_task_repeated(self, task_identifier):
        """Test analyzing repeated tasks increases occurrence count"""
        conn = sqlite3.connect(task_identifier.db_path)
        cursor = conn.cursor()
        
        # Insert multiple identical tasks
        for i in range(5):
            cursor.execute("""
                INSERT INTO tasks (task_type, status, duration_seconds, metadata)
                VALUES ('repeated_task', 'completed', 300, ?)
            """, (json.dumps({"tools_used": ["vim"]}),))
        
        conn.commit()
        
        # Get task IDs
        cursor.execute("SELECT id FROM tasks WHERE task_type = 'repeated_task'")
        task_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Analyze all tasks
        for task_id in task_ids:
            task_identifier.analyze_task(task_id)
        
        # Check that signature has correct occurrence count
        conn = sqlite3.connect(task_identifier.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT occurrence_count FROM task_signatures
            WHERE task_type = 'repeated_task'
        """)
        result = cursor.fetchone()
        conn.close()
        
        assert result[0] == 5
    
    def test_calculate_automation_score(self, task_identifier):
        """Test automation score calculation"""
        # High frequency, long duration, high success rate
        score1 = task_identifier._calculate_automation_score(10, 600, 1.0)
        
        # Low frequency, short duration, low success rate
        score2 = task_identifier._calculate_automation_score(1, 60, 0.5)
        
        assert score1 > score2
        assert 0 <= score1 <= 1
        assert 0 <= score2 <= 1
    
    def test_identify_repetitive_tasks(self, task_identifier):
        """Test identifying repetitive tasks"""
        conn = sqlite3.connect(task_identifier.db_path)
        cursor = conn.cursor()
        
        # Insert repetitive tasks
        for i in range(5):
            cursor.execute("""
                INSERT INTO tasks (task_type, status, duration_seconds, metadata)
                VALUES ('automation_task', 'completed', 400, ?)
            """, (json.dumps({"tools_used": ["python"]}),))
        
        # Insert non-repetitive task
        cursor.execute("""
            INSERT INTO tasks (task_type, status, duration_seconds)
            VALUES ('one_time_task', 'completed', 100)
        """)
        
        conn.commit()
        
        # Get task IDs and analyze
        cursor.execute("SELECT id FROM tasks")
        task_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        for task_id in task_ids:
            task_identifier.analyze_task(task_id)
        
        # Identify repetitive tasks (min 3 occurrences)
        repetitive = task_identifier.identify_repetitive_tasks(min_occurrences=3)
        
        assert len(repetitive) == 1
        assert repetitive[0]["task_type"] == "automation_task"
        assert repetitive[0]["occurrence_count"] == 5
    
    def test_create_automation_candidate(self, task_identifier):
        """Test creating an automation candidate"""
        # First create a task signature
        conn = sqlite3.connect(task_identifier.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO task_signatures
            (signature_hash, task_type, occurrence_count, avg_duration_seconds)
            VALUES ('test_hash', 'test_task', 5, 300)
        """)
        
        sig_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Create automation candidate
        candidate_id = task_identifier.create_automation_candidate(
            sig_id,
            "Automate Test Task",
            "This task can be automated with a script",
            automation_type="script",
            priority=8
        )
        
        assert candidate_id > 0
        
        # Verify it was created
        candidates = task_identifier.get_automation_candidates(min_priority=1)
        assert len(candidates) == 1
        assert candidates[0]["name"] == "Automate Test Task"
    
    def test_identify_task_patterns_sequential(self, task_identifier):
        """Test identifying sequential task patterns"""
        conn = sqlite3.connect(task_identifier.db_path)
        cursor = conn.cursor()
        
        # Insert sequential pattern: task_a -> task_b (repeated 5 times)
        base_time = datetime.now()
        for i in range(5):
            time1 = (base_time + timedelta(hours=i*2)).isoformat()
            time2 = (base_time + timedelta(hours=i*2, minutes=5)).isoformat()
            
            cursor.execute("""
                INSERT INTO tasks (task_type, status, created_at)
                VALUES ('task_a', 'completed', ?)
            """, (time1,))
            
            cursor.execute("""
                INSERT INTO tasks (task_type, status, created_at)
                VALUES ('task_b', 'completed', ?)
            """, (time2,))
        
        conn.commit()
        conn.close()
        
        # Identify patterns
        patterns = task_identifier.identify_task_patterns(days=30)
        
        # Should find the sequential pattern
        sequential_patterns = [p for p in patterns if p["type"] == "sequential"]
        assert len(sequential_patterns) > 0
        assert any("task_a" in p["description"] and "task_b" in p["description"] 
                   for p in sequential_patterns)
    
    def test_identify_task_patterns_temporal(self, task_identifier):
        """Test identifying temporal task patterns"""
        conn = sqlite3.connect(task_identifier.db_path)
        cursor = conn.cursor()
        
        # Insert tasks at the same hour on different days
        base_time = datetime.now().replace(hour=9, minute=0, second=0)
        for i in range(5):
            time = (base_time + timedelta(days=i)).isoformat()
            cursor.execute("""
                INSERT INTO tasks (task_type, status, created_at)
                VALUES ('morning_task', 'completed', ?)
            """, (time,))
        
        conn.commit()
        conn.close()
        
        # Identify patterns
        patterns = task_identifier.identify_task_patterns(days=30)
        
        # Should find the temporal pattern
        temporal_patterns = [p for p in patterns if p["type"] == "temporal"]
        assert len(temporal_patterns) > 0
        assert any("morning_task" in p["description"] for p in temporal_patterns)
    
    def test_get_automation_candidates(self, task_identifier):
        """Test getting automation candidates"""
        # Create task signatures and candidates
        conn = sqlite3.connect(task_identifier.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO task_signatures
            (signature_hash, task_type, occurrence_count, avg_duration_seconds)
            VALUES ('hash1', 'task1', 5, 300)
        """)
        sig_id1 = cursor.lastrowid
        
        cursor.execute("""
            INSERT INTO task_signatures
            (signature_hash, task_type, occurrence_count, avg_duration_seconds)
            VALUES ('hash2', 'task2', 3, 200)
        """)
        sig_id2 = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        # Create candidates with different priorities
        task_identifier.create_automation_candidate(
            sig_id1, "High Priority", "Important", priority=9
        )
        task_identifier.create_automation_candidate(
            sig_id2, "Low Priority", "Less important", priority=3
        )
        
        # Get high priority candidates
        candidates = task_identifier.get_automation_candidates(min_priority=5)
        assert len(candidates) == 1
        assert candidates[0]["name"] == "High Priority"
        
        # Get all candidates
        all_candidates = task_identifier.get_automation_candidates(min_priority=1)
        assert len(all_candidates) == 2
    
    def test_generate_automation_report(self, task_identifier):
        """Test generating comprehensive automation report"""
        conn = sqlite3.connect(task_identifier.db_path)
        cursor = conn.cursor()
        
        # Insert repetitive tasks
        for i in range(5):
            cursor.execute("""
                INSERT INTO tasks (task_type, status, duration_seconds, metadata)
                VALUES ('report_task', 'completed', 300, ?)
            """, (json.dumps({"tools_used": ["python"]}),))
        
        conn.commit()
        
        # Get task IDs and analyze
        cursor.execute("SELECT id FROM tasks")
        task_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        for task_id in task_ids:
            task_identifier.analyze_task(task_id)
        
        # Generate report
        report = task_identifier.generate_automation_report(days=30)
        
        assert "report_date" in report
        assert "summary" in report
        assert "top_opportunities" in report
        assert "patterns" in report
        assert "automation_candidates" in report
        
        # Check summary
        assert report["summary"]["total_repetitive_tasks"] > 0
        assert report["summary"]["total_potential_time_savings_seconds"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
