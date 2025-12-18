#!/usr/bin/env python3
"""
Unit tests for Success/Failure Tracker

Author: VY-NEXUS Self-Evolving AI System
Date: December 15, 2025
"""

import unittest
import os
import tempfile
import shutil
from datetime import datetime, timedelta
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.learning.success_failure_tracker import (
    SuccessFailureTracker,
    TaskOutcome,
    FailureCategory,
    TaskExecution
)


class TestSuccessFailureTracker(unittest.TestCase):
    """Test cases for SuccessFailureTracker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.tracker = SuccessFailureTracker(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_record_execution(self):
        """Test recording a task execution."""
        start = datetime.now()
        end = start + timedelta(seconds=2)
        
        self.tracker.record_execution(
            task_id="test_001",
            task_type="test_task",
            outcome=TaskOutcome.SUCCESS,
            start_time=start,
            end_time=end,
            user_satisfaction=5
        )
        
        self.tracker.flush()
        
        # Verify execution was recorded
        executions = self.tracker.load_executions()
        self.assertEqual(len(executions), 1)
        self.assertEqual(executions[0].task_id, "test_001")
        self.assertEqual(executions[0].outcome, TaskOutcome.SUCCESS)
    
    def test_record_failure(self):
        """Test recording a failed execution."""
        start = datetime.now()
        end = start + timedelta(seconds=1)
        
        self.tracker.record_execution(
            task_id="test_002",
            task_type="test_task",
            outcome=TaskOutcome.FAILURE,
            start_time=start,
            end_time=end,
            error_message="Test error",
            failure_category=FailureCategory.SYSTEM_ERROR,
            retry_count=3
        )
        
        self.tracker.flush()
        
        executions = self.tracker.load_executions()
        self.assertEqual(len(executions), 1)
        self.assertEqual(executions[0].outcome, TaskOutcome.FAILURE)
        self.assertEqual(executions[0].error_message, "Test error")
        self.assertEqual(executions[0].failure_category, FailureCategory.SYSTEM_ERROR)
        self.assertEqual(executions[0].retry_count, 3)
    
    def test_buffer_flushing(self):
        """Test automatic buffer flushing."""
        start = datetime.now()
        
        # Record more than buffer size
        for i in range(60):
            self.tracker.record_execution(
                task_id=f"test_{i:03d}",
                task_type="test_task",
                outcome=TaskOutcome.SUCCESS,
                start_time=start,
                end_time=start + timedelta(seconds=1)
            )
        
        # Should have auto-flushed
        executions = self.tracker.load_executions()
        self.assertGreaterEqual(len(executions), 50)
    
    def test_load_executions_with_filters(self):
        """Test loading executions with filters."""
        now = datetime.now()
        
        # Record different task types
        self.tracker.record_execution(
            task_id="test_001",
            task_type="type_a",
            outcome=TaskOutcome.SUCCESS,
            start_time=now - timedelta(days=2),
            end_time=now - timedelta(days=2, seconds=-1)
        )
        
        self.tracker.record_execution(
            task_id="test_002",
            task_type="type_b",
            outcome=TaskOutcome.SUCCESS,
            start_time=now - timedelta(days=1),
            end_time=now - timedelta(days=1, seconds=-1)
        )
        
        self.tracker.flush()
        
        # Filter by task type
        type_a_execs = self.tracker.load_executions(task_type="type_a")
        self.assertEqual(len(type_a_execs), 1)
        self.assertEqual(type_a_execs[0].task_type, "type_a")
        
        # Filter by time
        recent_execs = self.tracker.load_executions(
            since=now - timedelta(days=1, hours=12)
        )
        self.assertEqual(len(recent_execs), 1)
        self.assertEqual(recent_execs[0].task_id, "test_002")
    
    def test_calculate_metrics(self):
        """Test metrics calculation."""
        now = datetime.now()
        
        # Record mix of successes and failures
        for i in range(10):
            outcome = TaskOutcome.SUCCESS if i < 7 else TaskOutcome.FAILURE
            self.tracker.record_execution(
                task_id=f"test_{i:03d}",
                task_type="test_task",
                outcome=outcome,
                start_time=now,
                end_time=now + timedelta(seconds=1),
                user_satisfaction=4 if outcome == TaskOutcome.SUCCESS else 2
            )
        
        self.tracker.flush()
        
        metrics = self.tracker.calculate_metrics()
        self.assertIn("test_task", metrics)
        
        task_metrics = metrics["test_task"]
        self.assertEqual(task_metrics.total_executions, 10)
        self.assertEqual(task_metrics.successful, 7)
        self.assertEqual(task_metrics.failed, 3)
        self.assertEqual(task_metrics.success_rate, 70.0)
    
    def test_trend_calculation(self):
        """Test trend calculation."""
        now = datetime.now()
        
        # Record improving trend (failures first, then successes)
        for i in range(20):
            outcome = TaskOutcome.FAILURE if i < 5 else TaskOutcome.SUCCESS
            self.tracker.record_execution(
                task_id=f"test_{i:03d}",
                task_type="improving_task",
                outcome=outcome,
                start_time=now + timedelta(seconds=i),
                end_time=now + timedelta(seconds=i+1)
            )
        
        self.tracker.flush()
        
        metrics = self.tracker.calculate_metrics()
        self.assertEqual(metrics["improving_task"].trend, "improving")
    
    def test_analyze_failures(self):
        """Test failure analysis."""
        now = datetime.now()
        
        # Record various failures
        for i in range(5):
            self.tracker.record_execution(
                task_id=f"test_{i:03d}",
                task_type="test_task",
                outcome=TaskOutcome.FAILURE,
                start_time=now,
                end_time=now + timedelta(seconds=1),
                error_message="Database timeout",
                failure_category=FailureCategory.TIMEOUT_ERROR
            )
        
        for i in range(3):
            self.tracker.record_execution(
                task_id=f"test_{i+5:03d}",
                task_type="test_task",
                outcome=TaskOutcome.SUCCESS,
                start_time=now,
                end_time=now + timedelta(seconds=1)
            )
        
        self.tracker.flush()
        
        analysis = self.tracker.analyze_failures()
        self.assertEqual(analysis["total_failures"], 5)
        self.assertAlmostEqual(analysis["failure_rate"], 62.5, places=1)
        self.assertIn("timeout_error", analysis["categories"])
        self.assertEqual(analysis["categories"]["timeout_error"], 5)
    
    def test_generate_improvement_suggestions(self):
        """Test improvement suggestion generation."""
        now = datetime.now()
        
        # Create a task with low success rate
        for i in range(20):
            outcome = TaskOutcome.SUCCESS if i < 5 else TaskOutcome.FAILURE
            self.tracker.record_execution(
                task_id=f"test_{i:03d}",
                task_type="problematic_task",
                outcome=outcome,
                start_time=now,
                end_time=now + timedelta(seconds=1)
            )
        
        self.tracker.flush()
        
        suggestions = self.tracker.generate_improvement_suggestions()
        
        # Should have at least one suggestion for low success rate
        self.assertGreater(len(suggestions), 0)
        
        # Check for low success rate suggestion
        low_success_suggestions = [
            s for s in suggestions 
            if "success rate" in s.description.lower()
        ]
        self.assertGreater(len(low_success_suggestions), 0)
    
    def test_performance_report(self):
        """Test performance report generation."""
        now = datetime.now()
        
        # Record some executions
        for i in range(10):
            self.tracker.record_execution(
                task_id=f"test_{i:03d}",
                task_type="test_task",
                outcome=TaskOutcome.SUCCESS,
                start_time=now,
                end_time=now + timedelta(seconds=1),
                user_satisfaction=4
            )
        
        self.tracker.flush()
        
        report = self.tracker.get_performance_report()
        
        # Verify report structure
        self.assertIn("report_date", report)
        self.assertIn("overall_statistics", report)
        self.assertIn("metrics_by_task", report)
        self.assertIn("failure_analysis", report)
        self.assertIn("improvement_suggestions", report)
        
        # Verify statistics
        self.assertEqual(report["overall_statistics"]["total_executions"], 10)
        self.assertEqual(report["overall_statistics"]["success_rate"], 100.0)
    
    def test_slow_task_suggestion(self):
        """Test suggestion for slow tasks."""
        now = datetime.now()
        
        # Create a slow task (>5 seconds)
        for i in range(15):
            self.tracker.record_execution(
                task_id=f"test_{i:03d}",
                task_type="slow_task",
                outcome=TaskOutcome.SUCCESS,
                start_time=now,
                end_time=now + timedelta(seconds=10),  # 10 seconds
                user_satisfaction=3
            )
        
        self.tracker.flush()
        
        suggestions = self.tracker.generate_improvement_suggestions()
        
        # Should have performance suggestion
        perf_suggestions = [
            s for s in suggestions 
            if s.category == "performance"
        ]
        self.assertGreater(len(perf_suggestions), 0)
    
    def test_low_satisfaction_suggestion(self):
        """Test suggestion for low user satisfaction."""
        now = datetime.now()
        
        # Create tasks with low satisfaction
        for i in range(15):
            self.tracker.record_execution(
                task_id=f"test_{i:03d}",
                task_type="unsatisfying_task",
                outcome=TaskOutcome.SUCCESS,
                start_time=now,
                end_time=now + timedelta(seconds=1),
                user_satisfaction=2  # Low satisfaction
            )
        
        self.tracker.flush()
        
        suggestions = self.tracker.generate_improvement_suggestions()
        
        # Should have usability suggestion
        usability_suggestions = [
            s for s in suggestions 
            if s.category == "usability"
        ]
        self.assertGreater(len(usability_suggestions), 0)
    
    def test_metrics_caching(self):
        """Test metrics caching mechanism."""
        now = datetime.now()
        
        # Record some executions
        for i in range(5):
            self.tracker.record_execution(
                task_id=f"test_{i:03d}",
                task_type="test_task",
                outcome=TaskOutcome.SUCCESS,
                start_time=now,
                end_time=now + timedelta(seconds=1)
            )
        
        self.tracker.flush()
        
        # First call should populate cache
        metrics1 = self.tracker.calculate_metrics()
        
        # Second call should use cache
        metrics2 = self.tracker.calculate_metrics()
        
        # Should be the same object (from cache)
        self.assertEqual(metrics1, metrics2)
    
    def test_task_execution_serialization(self):
        """Test TaskExecution serialization/deserialization."""
        now = datetime.now()
        
        execution = TaskExecution(
            task_id="test_001",
            task_type="test_task",
            outcome=TaskOutcome.SUCCESS,
            start_time=now.isoformat(),
            end_time=(now + timedelta(seconds=1)).isoformat(),
            duration_ms=1000.0,
            error_message="Test error",
            failure_category=FailureCategory.SYSTEM_ERROR,
            user_satisfaction=4,
            retry_count=2,
            context={"key": "value"}
        )
        
        # Serialize
        data = execution.to_dict()
        
        # Deserialize
        restored = TaskExecution.from_dict(data)
        
        # Verify
        self.assertEqual(restored.task_id, execution.task_id)
        self.assertEqual(restored.outcome, execution.outcome)
        self.assertEqual(restored.failure_category, execution.failure_category)
        self.assertEqual(restored.context, execution.context)


if __name__ == "__main__":
    unittest.main()
