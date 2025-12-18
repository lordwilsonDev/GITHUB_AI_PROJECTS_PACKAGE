#!/usr/bin/env python3
"""
Unit tests for Productivity Metrics Analyzer

Author: VY-NEXUS Self-Evolving AI System
Date: December 15, 2025
"""

import unittest
import os
import tempfile
import shutil
import json
import sys
import time
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.learning.productivity_metrics_analyzer import (
    ProductivityMetricsAnalyzer,
    ProductivityPeriod,
    TaskCategory,
    TimeEntry
)


class TestProductivityMetricsAnalyzer(unittest.TestCase):
    """Test cases for ProductivityMetricsAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.analyzer = ProductivityMetricsAnalyzer(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_start_task(self):
        """Test starting a task."""
        entry_id = self.analyzer.start_task(
            task_name="Test Task",
            task_category=TaskCategory.DEVELOPMENT
        )
        
        self.assertIsNotNone(entry_id)
        self.assertIn(entry_id, self.analyzer._active_entries)
        
        entry = self.analyzer._active_entries[entry_id]
        self.assertEqual(entry.task_name, "Test Task")
        self.assertEqual(entry.task_category, TaskCategory.DEVELOPMENT)
    
    def test_end_task(self):
        """Test ending a task."""
        entry_id = self.analyzer.start_task(
            task_name="Test Task",
            task_category=TaskCategory.DEVELOPMENT
        )
        
        time.sleep(0.1)  # Small delay
        
        success = self.analyzer.end_task(entry_id, completed=True)
        self.assertTrue(success)
        
        # Should be moved to buffer
        self.assertNotIn(entry_id, self.analyzer._active_entries)
        self.assertEqual(len(self.analyzer._entry_buffer), 1)
        
        entry = self.analyzer._entry_buffer[0]
        self.assertTrue(entry.completed)
        self.assertIsNotNone(entry.duration_seconds)
        self.assertGreater(entry.duration_seconds, 0)
    
    def test_record_interruption(self):
        """Test recording interruptions."""
        entry_id = self.analyzer.start_task(
            task_name="Test Task",
            task_category=TaskCategory.DEVELOPMENT
        )
        
        # Record interruptions
        self.analyzer.record_interruption(entry_id)
        self.analyzer.record_interruption(entry_id)
        
        entry = self.analyzer._active_entries[entry_id]
        self.assertEqual(entry.interruptions, 2)
    
    def test_buffer_flushing(self):
        """Test automatic buffer flushing."""
        # Create more entries than buffer size
        for i in range(55):
            entry_id = self.analyzer.start_task(
                task_name=f"Task {i}",
                task_category=TaskCategory.DEVELOPMENT
            )
            time.sleep(0.01)
            self.analyzer.end_task(entry_id, completed=True)
        
        # Should have auto-flushed
        self.assertTrue(os.path.exists(self.analyzer.entries_file))
        
        # Load and verify
        entries = self.analyzer.load_entries()
        self.assertGreaterEqual(len(entries), 50)
    
    def test_load_entries_with_filters(self):
        """Test loading entries with filters."""
        # Create entries with different categories and times
        now = datetime.now()
        
        # Development task
        entry_id1 = self.analyzer.start_task(
            task_name="Dev Task",
            task_category=TaskCategory.DEVELOPMENT
        )
        time.sleep(0.01)
        self.analyzer.end_task(entry_id1, completed=True)
        
        # Communication task
        entry_id2 = self.analyzer.start_task(
            task_name="Meeting",
            task_category=TaskCategory.COMMUNICATION
        )
        time.sleep(0.01)
        self.analyzer.end_task(entry_id2, completed=True)
        
        self.analyzer.flush()
        
        # Filter by category
        dev_entries = self.analyzer.load_entries(category=TaskCategory.DEVELOPMENT)
        self.assertEqual(len(dev_entries), 1)
        self.assertEqual(dev_entries[0].task_category, TaskCategory.DEVELOPMENT)
        
        comm_entries = self.analyzer.load_entries(category=TaskCategory.COMMUNICATION)
        self.assertEqual(len(comm_entries), 1)
        self.assertEqual(comm_entries[0].task_category, TaskCategory.COMMUNICATION)
    
    def test_calculate_daily_metrics(self):
        """Test calculating daily metrics."""
        # Create some completed and incomplete tasks
        for i in range(5):
            entry_id = self.analyzer.start_task(
                task_name=f"Task {i}",
                task_category=TaskCategory.DEVELOPMENT
            )
            time.sleep(0.01)
            completed = i < 3  # First 3 completed
            self.analyzer.end_task(entry_id, completed=completed)
        
        self.analyzer.flush()
        
        # Calculate metrics
        metrics = self.analyzer.calculate_metrics(ProductivityPeriod.DAILY)
        
        self.assertEqual(metrics.tasks_started, 5)
        self.assertEqual(metrics.tasks_completed, 3)
        self.assertEqual(metrics.completion_rate, 60.0)
        self.assertGreater(metrics.total_time_seconds, 0)
        self.assertGreater(metrics.productivity_score, 0)
    
    def test_productivity_score_calculation(self):
        """Test productivity score calculation."""
        # Create high-quality work session
        for i in range(10):
            entry_id = self.analyzer.start_task(
                task_name=f"Task {i}",
                task_category=TaskCategory.DEVELOPMENT
            )
            time.sleep(0.01)
            self.analyzer.end_task(entry_id, completed=True, interruptions=0)
        
        self.analyzer.flush()
        
        metrics = self.analyzer.calculate_metrics(ProductivityPeriod.DAILY)
        
        # Should have high score (100% completion, no interruptions)
        self.assertGreater(metrics.productivity_score, 70)
    
    def test_low_productivity_score(self):
        """Test low productivity score with interruptions."""
        # Create low-quality work session
        for i in range(10):
            entry_id = self.analyzer.start_task(
                task_name=f"Task {i}",
                task_category=TaskCategory.DEVELOPMENT
            )
            time.sleep(0.01)
            completed = i < 3  # Only 30% completion
            interruptions = 5 if not completed else 0
            self.analyzer.end_task(entry_id, completed=completed, interruptions=interruptions)
        
        self.analyzer.flush()
        
        metrics = self.analyzer.calculate_metrics(ProductivityPeriod.DAILY)
        
        # Should have lower score
        self.assertLess(metrics.productivity_score, 50)
    
    def test_category_breakdown(self):
        """Test category breakdown in metrics."""
        # Create tasks in different categories
        categories = [
            TaskCategory.DEVELOPMENT,
            TaskCategory.DEVELOPMENT,
            TaskCategory.COMMUNICATION,
            TaskCategory.PLANNING
        ]
        
        for i, category in enumerate(categories):
            entry_id = self.analyzer.start_task(
                task_name=f"Task {i}",
                task_category=category
            )
            time.sleep(0.01)
            self.analyzer.end_task(entry_id, completed=True)
        
        self.analyzer.flush()
        
        metrics = self.analyzer.calculate_metrics(ProductivityPeriod.DAILY)
        
        # Should have breakdown by category
        self.assertIn(TaskCategory.DEVELOPMENT.value, metrics.category_breakdown)
        self.assertIn(TaskCategory.COMMUNICATION.value, metrics.category_breakdown)
        self.assertIn(TaskCategory.PLANNING.value, metrics.category_breakdown)
    
    def test_peak_productivity_hour(self):
        """Test peak productivity hour detection."""
        # Create tasks at specific hours
        now = datetime.now()
        
        # Manually create entries at different hours
        for hour in [9, 10, 14, 15]:
            entry = TimeEntry(
                entry_id=f"entry_{hour}",
                task_name=f"Task at {hour}",
                task_category=TaskCategory.DEVELOPMENT,
                start_time=now.replace(hour=hour, minute=0).isoformat(),
                end_time=now.replace(hour=hour, minute=30).isoformat(),
                duration_seconds=1800,  # 30 minutes
                completed=True
            )
            self.analyzer._entry_buffer.append(entry)
        
        # Add more time at hour 10 (should be peak)
        for i in range(3):
            entry = TimeEntry(
                entry_id=f"entry_10_{i}",
                task_name=f"Task at 10 #{i}",
                task_category=TaskCategory.DEVELOPMENT,
                start_time=now.replace(hour=10, minute=i*10).isoformat(),
                end_time=now.replace(hour=10, minute=i*10+10).isoformat(),
                duration_seconds=600,
                completed=True
            )
            self.analyzer._entry_buffer.append(entry)
        
        self.analyzer.flush()
        
        metrics = self.analyzer.calculate_metrics(ProductivityPeriod.DAILY)
        
        # Peak should be hour 10
        self.assertEqual(metrics.peak_productivity_hour, 10)
    
    def test_analyze_trends(self):
        """Test trend analysis."""
        # Create entries for multiple days
        for day_offset in range(7):
            date = datetime.now() - timedelta(days=day_offset)
            
            for i in range(5):
                entry = TimeEntry(
                    entry_id=f"entry_{day_offset}_{i}",
                    task_name=f"Task {i}",
                    task_category=TaskCategory.DEVELOPMENT,
                    start_time=date.replace(hour=10, minute=i*10).isoformat(),
                    end_time=date.replace(hour=10, minute=i*10+10).isoformat(),
                    duration_seconds=600,
                    completed=True
                )
                self.analyzer._entry_buffer.append(entry)
        
        self.analyzer.flush()
        
        trends = self.analyzer.analyze_trends(days=7)
        
        self.assertIn("trend", trends)
        self.assertIn("avg_productivity_score", trends)
        self.assertIn("consistency_score", trends)
    
    def test_identify_bottlenecks_high_interruptions(self):
        """Test identifying high interruption bottlenecks."""
        # Create tasks with high interruptions
        for i in range(5):
            entry = TimeEntry(
                entry_id=f"entry_{i}",
                task_name="Problematic Task",
                task_category=TaskCategory.DEVELOPMENT,
                start_time=datetime.now().isoformat(),
                end_time=(datetime.now() + timedelta(minutes=30)).isoformat(),
                duration_seconds=1800,
                completed=True,
                interruptions=5  # High interruptions
            )
            self.analyzer._entry_buffer.append(entry)
        
        self.analyzer.flush()
        
        bottlenecks = self.analyzer.identify_bottlenecks(days=7)
        
        # Should identify high interruption bottleneck
        high_int_bottlenecks = [b for b in bottlenecks if b["type"] == "high_interruptions"]
        self.assertGreater(len(high_int_bottlenecks), 0)
    
    def test_identify_bottlenecks_low_completion(self):
        """Test identifying low completion rate bottlenecks."""
        # Create tasks with low completion rate
        for i in range(10):
            entry = TimeEntry(
                entry_id=f"entry_{i}",
                task_name="Difficult Task",
                task_category=TaskCategory.DEVELOPMENT,
                start_time=datetime.now().isoformat(),
                end_time=(datetime.now() + timedelta(minutes=30)).isoformat(),
                duration_seconds=1800,
                completed=i < 2  # Only 20% completion
            )
            self.analyzer._entry_buffer.append(entry)
        
        self.analyzer.flush()
        
        bottlenecks = self.analyzer.identify_bottlenecks(days=7)
        
        # Should identify low completion bottleneck
        low_comp_bottlenecks = [b for b in bottlenecks if b["type"] == "low_completion_rate"]
        self.assertGreater(len(low_comp_bottlenecks), 0)
    
    def test_generate_insights(self):
        """Test insight generation."""
        # Create some tasks
        for i in range(5):
            entry_id = self.analyzer.start_task(
                task_name=f"Task {i}",
                task_category=TaskCategory.DEVELOPMENT
            )
            time.sleep(0.01)
            self.analyzer.end_task(entry_id, completed=i < 3)
        
        self.analyzer.flush()
        
        insights = self.analyzer.generate_insights(days=7)
        
        # Should generate some insights
        self.assertGreater(len(insights), 0)
        
        # Check insight structure
        for insight in insights:
            self.assertIsNotNone(insight.insight_id)
            self.assertIn(insight.category, ["bottleneck", "opportunity", "trend", "recommendation"])
            self.assertIn(insight.priority, ["high", "medium", "low"])
            self.assertIsNotNone(insight.title)
            self.assertIsNotNone(insight.description)
            self.assertIsInstance(insight.actionable_steps, list)
    
    def test_productivity_report(self):
        """Test comprehensive productivity report generation."""
        # Create some tasks
        for i in range(10):
            entry_id = self.analyzer.start_task(
                task_name=f"Task {i}",
                task_category=TaskCategory.DEVELOPMENT
            )
            time.sleep(0.01)
            self.analyzer.end_task(entry_id, completed=True)
        
        self.analyzer.flush()
        
        report = self.analyzer.get_productivity_report(days=7)
        
        # Verify report structure
        self.assertIn("report_date", report)
        self.assertIn("current_day_metrics", report)
        self.assertIn("weekly_metrics", report)
        self.assertIn("trends", report)
        self.assertIn("bottlenecks", report)
        self.assertIn("insights", report)
        self.assertIn("summary", report)
        
        # Verify summary
        summary = report["summary"]
        self.assertIn("productivity_score", summary)
        self.assertIn("completion_rate", summary)
        self.assertIn("trend", summary)
    
    def test_time_entry_serialization(self):
        """Test TimeEntry serialization/deserialization."""
        entry = TimeEntry(
            entry_id="test_001",
            task_name="Test Task",
            task_category=TaskCategory.DEVELOPMENT,
            start_time=datetime.now().isoformat(),
            end_time=(datetime.now() + timedelta(minutes=30)).isoformat(),
            duration_seconds=1800,
            completed=True,
            interruptions=2,
            context={"project": "test"}
        )
        
        # Serialize
        data = entry.to_dict()
        
        # Deserialize
        restored = TimeEntry.from_dict(data)
        
        # Verify
        self.assertEqual(restored.entry_id, entry.entry_id)
        self.assertEqual(restored.task_name, entry.task_name)
        self.assertEqual(restored.task_category, entry.task_category)
        self.assertEqual(restored.completed, entry.completed)
        self.assertEqual(restored.interruptions, entry.interruptions)
    
    def test_weekly_metrics(self):
        """Test weekly metrics calculation."""
        # Create entries across multiple days
        for day in range(7):
            date = datetime.now() - timedelta(days=day)
            
            for i in range(3):
                entry = TimeEntry(
                    entry_id=f"entry_{day}_{i}",
                    task_name=f"Task {i}",
                    task_category=TaskCategory.DEVELOPMENT,
                    start_time=date.replace(hour=10, minute=i*10).isoformat(),
                    end_time=date.replace(hour=10, minute=i*10+10).isoformat(),
                    duration_seconds=600,
                    completed=True
                )
                self.analyzer._entry_buffer.append(entry)
        
        self.analyzer.flush()
        
        metrics = self.analyzer.calculate_metrics(ProductivityPeriod.WEEKLY)
        
        # Should aggregate all week's data
        self.assertGreater(metrics.tasks_completed, 10)
        self.assertGreater(metrics.total_time_seconds, 0)
    
    def test_empty_metrics(self):
        """Test metrics calculation with no data."""
        metrics = self.analyzer.calculate_metrics(ProductivityPeriod.DAILY)
        
        # Should return zero metrics
        self.assertEqual(metrics.total_time_seconds, 0)
        self.assertEqual(metrics.tasks_completed, 0)
        self.assertEqual(metrics.productivity_score, 0.0)


if __name__ == "__main__":
    unittest.main()
