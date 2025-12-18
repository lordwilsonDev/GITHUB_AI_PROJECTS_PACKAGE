#!/usr/bin/env python3
"""
Tests for Research Automation and Productivity Metrics Modules
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

from modules.research_automation import (
    ResearchAutomation,
    LearningObjectiveManager,
    TrendAnalyzer,
    ResearchTopic
)
from modules.productivity_metrics import ProductivityMetricsAnalyzer


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def research_automation(temp_db):
    """Create a research automation instance"""
    return ResearchAutomation(temp_db)


@pytest.fixture
def productivity_analyzer(temp_db):
    """Create a productivity analyzer with test data"""
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
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_type TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    
    return ProductivityMetricsAnalyzer(temp_db)


class TestResearchAutomation:
    """Test suite for ResearchAutomation"""
    
    def test_initialization(self, research_automation):
        """Test that research automation initializes correctly"""
        assert research_automation.db_path is not None
        
        # Check tables exist
        conn = sqlite3.connect(research_automation.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('research_topics', 'research_findings', 'learning_objectives', 'knowledge_base')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert 'research_topics' in tables
        assert 'research_findings' in tables
        assert 'learning_objectives' in tables
        assert 'knowledge_base' in tables
    
    def test_add_research_topic(self, research_automation):
        """Test adding a research topic"""
        topic_id = research_automation.add_research_topic(
            ResearchTopic.TOOLS,
            "AI Code Assistants",
            priority=8,
            metadata={"reason": "Improve development efficiency"}
        )
        
        assert topic_id > 0
        
        # Verify it was stored
        topics = research_automation.get_priority_research_topics(limit=10)
        assert len(topics) == 1
        assert topics[0]["topic_name"] == "AI Code Assistants"
        assert topics[0]["priority"] == 8
    
    def test_add_duplicate_topic_updates_priority(self, research_automation):
        """Test that adding duplicate topic updates priority if higher"""
        # Add initial topic
        research_automation.add_research_topic(
            ResearchTopic.TOOLS,
            "Test Tool",
            priority=5
        )
        
        # Add same topic with higher priority
        research_automation.add_research_topic(
            ResearchTopic.TOOLS,
            "Test Tool",
            priority=9
        )
        
        topics = research_automation.get_priority_research_topics(limit=10)
        assert len(topics) == 1
        assert topics[0]["priority"] == 9
    
    def test_record_finding(self, research_automation):
        """Test recording a research finding"""
        topic_id = research_automation.add_research_topic(
            ResearchTopic.TOOLS,
            "AI Tools",
            priority=7
        )
        
        finding_id = research_automation.record_finding(
            topic_id,
            "tool",
            "GitHub Copilot",
            "AI-powered code completion",
            source="GitHub",
            relevance_score=0.9
        )
        
        assert finding_id > 0
        
        # Verify finding was stored
        findings = research_automation.get_findings_for_topic(topic_id)
        assert len(findings) == 1
        assert findings[0]["title"] == "GitHub Copilot"
        assert findings[0]["relevance_score"] == 0.9
    
    def test_add_to_knowledge_base(self, research_automation):
        """Test adding knowledge to knowledge base"""
        knowledge_id = research_automation.add_to_knowledge_base(
            "tools",
            "AI Code Assistants",
            "GitHub Copilot uses OpenAI Codex",
            confidence_score=0.8,
            tags=["ai", "coding"]
        )
        
        assert knowledge_id > 0
        
        # Search for it
        results = research_automation.search_knowledge_base("Copilot")
        assert len(results) == 1
        assert "Copilot" in results[0]["content"]
    
    def test_search_knowledge_base(self, research_automation):
        """Test searching the knowledge base"""
        # Add multiple entries
        research_automation.add_to_knowledge_base(
            "tools", "AI Tools", "GitHub Copilot is great", confidence_score=0.8
        )
        research_automation.add_to_knowledge_base(
            "tools", "Editors", "VS Code is popular", confidence_score=0.9
        )
        research_automation.add_to_knowledge_base(
            "techniques", "Coding", "Test-driven development", confidence_score=0.7
        )
        
        # Search all (case-insensitive search for "code")
        results = research_automation.search_knowledge_base("code")
        assert len(results) == 1  # Only VS Code matches
        
        # Search for something that matches multiple
        results = research_automation.search_knowledge_base("development")
        assert len(results) == 1  # Test-driven development
        
        # Search with category filter
        results = research_automation.search_knowledge_base("code", category="techniques")
        assert len(results) == 0  # No match in techniques category
    
    def test_get_priority_research_topics(self, research_automation):
        """Test getting priority research topics"""
        # Add topics with different priorities
        research_automation.add_research_topic(ResearchTopic.TOOLS, "Low Priority", priority=3)
        research_automation.add_research_topic(ResearchTopic.TOOLS, "High Priority", priority=9)
        research_automation.add_research_topic(ResearchTopic.TOOLS, "Medium Priority", priority=6)
        
        topics = research_automation.get_priority_research_topics(limit=10)
        
        # Should be sorted by priority descending
        assert topics[0]["topic_name"] == "High Priority"
        assert topics[1]["topic_name"] == "Medium Priority"
        assert topics[2]["topic_name"] == "Low Priority"


class TestLearningObjectiveManager:
    """Test suite for LearningObjectiveManager"""
    
    def test_create_objective(self, temp_db):
        """Test creating a learning objective"""
        manager = LearningObjectiveManager(temp_db)
        
        obj_id = manager.create_objective(
            "technical",
            "Learn Python",
            "Master Python programming",
            priority=8
        )
        
        assert obj_id > 0
        
        objectives = manager.get_active_objectives()
        assert len(objectives) == 1
        assert objectives[0]["objective_name"] == "Learn Python"
    
    def test_update_progress(self, temp_db):
        """Test updating objective progress"""
        manager = LearningObjectiveManager(temp_db)
        
        obj_id = manager.create_objective(
            "technical",
            "Learn Python",
            "Master Python",
            priority=8
        )
        
        # Update progress
        manager.update_progress(obj_id, 0.5)
        
        objectives = manager.get_active_objectives()
        assert objectives[0]["progress"] == 0.5
        
        # Complete the objective
        manager.update_progress(obj_id, 1.0)
        
        # Should no longer be in active objectives
        objectives = manager.get_active_objectives()
        assert len(objectives) == 0
    
    def test_generate_daily_learning_plan(self, temp_db):
        """Test generating a daily learning plan"""
        manager = LearningObjectiveManager(temp_db)
        research = ResearchAutomation(temp_db)
        
        # Add objectives and research topics
        manager.create_objective("technical", "Learn Python", "Master Python", priority=9)
        manager.create_objective("technical", "Learn Docker", "Master Docker", priority=7)
        research.add_research_topic(ResearchTopic.TOOLS, "AI Tools", priority=8)
        
        plan = manager.generate_daily_learning_plan()
        
        assert "priority_objectives" in plan
        assert "research_topics" in plan
        assert "estimated_time_hours" in plan
        assert len(plan["priority_objectives"]) > 0
        assert plan["estimated_time_hours"] > 0


class TestProductivityMetricsAnalyzer:
    """Test suite for ProductivityMetricsAnalyzer"""
    
    def test_initialization(self, productivity_analyzer):
        """Test that analyzer initializes correctly"""
        assert productivity_analyzer.db_path is not None
        
        # Check tables exist
        conn = sqlite3.connect(productivity_analyzer.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('productivity_metrics', 'bottlenecks', 'performance_snapshots')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert 'productivity_metrics' in tables
        assert 'bottlenecks' in tables
        assert 'performance_snapshots' in tables
    
    def test_record_metric(self, productivity_analyzer):
        """Test recording a productivity metric"""
        metric_id = productivity_analyzer.record_metric(
            "completion_rate",
            "daily_completion",
            0.85,
            metadata={"tasks": 20}
        )
        
        assert metric_id > 0
    
    def test_record_bottleneck(self, productivity_analyzer):
        """Test recording a bottleneck"""
        bottleneck_id = productivity_analyzer.record_bottleneck(
            "time",
            "Tasks taking too long",
            severity="high",
            impact_score=0.8
        )
        
        assert bottleneck_id > 0
    
    def test_analyze_task_completion_rate(self, productivity_analyzer):
        """Test task completion rate analysis"""
        # Add test tasks
        conn = sqlite3.connect(productivity_analyzer.db_path)
        cursor = conn.cursor()
        
        for i in range(10):
            status = "completed" if i < 7 else "failed"
            cursor.execute("""
                INSERT INTO tasks (task_type, status, duration_seconds)
                VALUES ('test', ?, 300)
            """, (status,))
        
        conn.commit()
        conn.close()
        
        result = productivity_analyzer.analyze_task_completion_rate(days=7)
        
        assert result["status"] == "success"
        assert result["total_tasks"] == 10
        assert result["completed_tasks"] == 7
        assert result["completion_rate"] == 0.7
    
    def test_analyze_time_efficiency(self, productivity_analyzer):
        """Test time efficiency analysis"""
        # Add test tasks with durations
        conn = sqlite3.connect(productivity_analyzer.db_path)
        cursor = conn.cursor()
        
        for i in range(5):
            cursor.execute("""
                INSERT INTO tasks (task_type, status, duration_seconds)
                VALUES ('automation', 'completed', ?)
            """, (300 + i * 50,))
        
        conn.commit()
        conn.close()
        
        result = productivity_analyzer.analyze_time_efficiency(days=7)
        
        assert result["status"] == "success"
        assert "efficiency_by_type" in result
        assert "automation" in result["efficiency_by_type"]
        assert result["efficiency_by_type"]["automation"]["task_count"] == 5
    
    def test_identify_bottlenecks(self, productivity_analyzer):
        """Test bottleneck identification"""
        # Add tasks with low completion rate
        conn = sqlite3.connect(productivity_analyzer.db_path)
        cursor = conn.cursor()
        
        for i in range(10):
            status = "completed" if i < 4 else "failed"  # 40% completion rate
            cursor.execute("""
                INSERT INTO tasks (task_type, status, duration_seconds)
                VALUES ('test', ?, 300)
            """, (status,))
        
        conn.commit()
        conn.close()
        
        bottlenecks = productivity_analyzer.identify_bottlenecks(days=7)
        
        assert len(bottlenecks) > 0
        # Should identify low completion rate
        assert any(b["type"] == "low_completion_rate" for b in bottlenecks)
    
    def test_create_daily_snapshot(self, productivity_analyzer):
        """Test creating a daily performance snapshot"""
        # Add tasks for today
        conn = sqlite3.connect(productivity_analyzer.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date().isoformat()
        for i in range(5):
            status = "completed" if i < 4 else "failed"
            cursor.execute("""
                INSERT INTO tasks (task_type, status, duration_seconds, created_at)
                VALUES ('test', ?, 300, ?)
            """, (status, today))
        
        conn.commit()
        conn.close()
        
        snapshot_id = productivity_analyzer.create_daily_snapshot()
        
        assert snapshot_id > 0
        
        # Verify snapshot was created
        conn = sqlite3.connect(productivity_analyzer.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tasks_completed, tasks_failed, efficiency_score
            FROM performance_snapshots
            WHERE id = ?
        """, (snapshot_id,))
        result = cursor.fetchone()
        conn.close()
        
        assert result[0] == 4  # completed
        assert result[1] == 1  # failed
        assert result[2] > 0  # efficiency score
    
    def test_generate_productivity_report(self, productivity_analyzer):
        """Test generating a comprehensive productivity report"""
        # Add test data
        conn = sqlite3.connect(productivity_analyzer.db_path)
        cursor = conn.cursor()
        
        for i in range(10):
            status = "completed" if i < 8 else "failed"
            cursor.execute("""
                INSERT INTO tasks (task_type, status, duration_seconds)
                VALUES ('test', ?, 300)
            """, (status,))
        
        conn.commit()
        conn.close()
        
        report = productivity_analyzer.generate_productivity_report(days=7)
        
        assert "report_date" in report
        assert "completion_analysis" in report
        assert "time_efficiency" in report
        assert "bottlenecks" in report
        assert "summary" in report
        assert "overall_status" in report["summary"]


class TestTrendAnalyzer:
    """Test suite for TrendAnalyzer"""
    
    def test_analyze_tool_usage_trends(self, temp_db):
        """Test tool usage trend analysis"""
        # Create interactions table with tool usage
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
        
        # Add tool usage data
        for i in range(10):
            tool = "vim" if i < 6 else "vscode"
            cursor.execute("""
                INSERT INTO interactions (interaction_type, metadata)
                VALUES ('tool_usage', ?)
            """, (json.dumps({"tool_used": tool}),))
        
        conn.commit()
        conn.close()
        
        analyzer = TrendAnalyzer(temp_db)
        result = analyzer.analyze_tool_usage_trends(days=7)
        
        assert result["status"] == "success"
        assert len(result["top_tools"]) == 2
        assert result["top_tools"][0]["tool"] == "vim"
        assert result["top_tools"][0]["usage_count"] == 6
    
    def test_identify_knowledge_gaps(self, temp_db):
        """Test knowledge gap identification"""
        research = ResearchAutomation(temp_db)
        
        # Add knowledge with varying confidence
        research.add_to_knowledge_base(
            "tools", "Low Confidence Topic", "Some content", confidence_score=0.3
        )
        research.add_to_knowledge_base(
            "tools", "High Confidence Topic", "More content", confidence_score=0.9
        )
        
        analyzer = TrendAnalyzer(temp_db)
        gaps = analyzer.identify_knowledge_gaps()
        
        assert len(gaps) > 0
        # Should identify the low confidence topic
        assert any(g["topic"] == "Low Confidence Topic" for g in gaps)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
