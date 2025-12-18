#!/usr/bin/env python3
"""
Unit tests for Task Management Optimizer

Tests task prioritization, resource allocation, scheduling,
and adaptive learning components.
"""

import unittest
import os
import shutil
from datetime import datetime, timedelta
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from self_improvement.task_management_optimizer import (
    Task, Resource, TaskPriority, TaskStatus, ResourceType,
    TaskPriorityOptimizer, ResourceAllocator, ScheduleOptimizer,
    AdaptiveLearner, TaskManagementOptimizer
)


class TestTaskPriorityOptimizer(unittest.TestCase):
    """Test task priority optimization."""
    
    def setUp(self):
        self.optimizer = TaskPriorityOptimizer()
    
    def test_calculate_priority_score(self):
        """Test priority score calculation."""
        task = Task(
            task_id="t1",
            name="Test Task",
            description="Test",
            priority=TaskPriority.HIGH.value
        )
        
        score = self.optimizer.calculate_priority_score(task)
        self.assertGreater(score, 0)
        self.assertLess(score, 15)
    
    def test_critical_priority_higher_than_low(self):
        """Test that critical tasks have higher priority than low."""
        critical_task = Task("t1", "Critical", "Test", priority=TaskPriority.CRITICAL.value)
        low_task = Task("t2", "Low", "Test", priority=TaskPriority.LOW.value)
        
        critical_score = self.optimizer.calculate_priority_score(critical_task)
        low_score = self.optimizer.calculate_priority_score(low_task)
        
        self.assertGreater(critical_score, low_score)
    
    def test_deadline_proximity_increases_priority(self):
        """Test that approaching deadlines increase priority."""
        now = datetime.now()
        
        task_soon = Task(
            "t1", "Soon", "Test",
            deadline=(now + timedelta(hours=2)).isoformat()
        )
        task_later = Task(
            "t2", "Later", "Test",
            deadline=(now + timedelta(days=7)).isoformat()
        )
        
        score_soon = self.optimizer.calculate_priority_score(task_soon, now)
        score_later = self.optimizer.calculate_priority_score(task_later, now)
        
        self.assertGreater(score_soon, score_later)
    
    def test_prioritize_tasks(self):
        """Test task prioritization."""
        tasks = [
            Task("t1", "Low", "Test", priority=TaskPriority.LOW.value),
            Task("t2", "High", "Test", priority=TaskPriority.HIGH.value),
            Task("t3", "Critical", "Test", priority=TaskPriority.CRITICAL.value)
        ]
        
        prioritized = self.optimizer.prioritize_tasks(tasks)
        
        self.assertEqual(len(prioritized), 3)
        # Critical should be first
        self.assertEqual(prioritized[0][0].name, "Critical")
        # Low should be last
        self.assertEqual(prioritized[-1][0].name, "Low")


class TestResourceAllocator(unittest.TestCase):
    """Test resource allocation."""
    
    def setUp(self):
        self.resources = [
            Resource("cpu1", "CPU 1", ResourceType.COMPUTE.value, 100, 100),
            Resource("mem1", "Memory 1", ResourceType.MEMORY.value, 1000, 1000)
        ]
        self.allocator = ResourceAllocator(self.resources)
    
    def test_can_allocate_sufficient_resources(self):
        """Test checking if resources can be allocated."""
        task = Task(
            "t1", "Test", "Test",
            required_resources={ResourceType.COMPUTE.value: 50}
        )
        
        self.assertTrue(self.allocator.can_allocate(task))
    
    def test_cannot_allocate_insufficient_resources(self):
        """Test that allocation fails when resources insufficient."""
        task = Task(
            "t1", "Test", "Test",
            required_resources={ResourceType.COMPUTE.value: 200}
        )
        
        self.assertFalse(self.allocator.can_allocate(task))
    
    def test_allocate_resources(self):
        """Test resource allocation."""
        task = Task(
            "t1", "Test", "Test",
            required_resources={ResourceType.COMPUTE.value: 50}
        )
        
        allocation = self.allocator.allocate_resources(task)
        
        self.assertGreater(len(allocation), 0)
        self.assertEqual(self.resources[0].available, 50)
    
    def test_release_resources(self):
        """Test resource release."""
        task = Task(
            "t1", "Test", "Test",
            required_resources={ResourceType.COMPUTE.value: 50}
        )
        
        allocation = self.allocator.allocate_resources(task)
        self.assertEqual(self.resources[0].available, 50)
        
        self.allocator.release_resources(task.task_id)
        self.assertEqual(self.resources[0].available, 100)
    
    def test_resource_utilization(self):
        """Test resource utilization calculation."""
        task = Task(
            "t1", "Test", "Test",
            required_resources={ResourceType.COMPUTE.value: 50}
        )
        
        self.allocator.allocate_resources(task)
        utilization = self.allocator.get_resource_utilization()
        
        self.assertIn("cpu1", utilization)
        self.assertAlmostEqual(utilization["cpu1"], 0.5, places=2)


class TestScheduleOptimizer(unittest.TestCase):
    """Test schedule optimization."""
    
    def setUp(self):
        self.optimizer = ScheduleOptimizer()
        self.resources = [
            Resource("cpu1", "CPU 1", ResourceType.COMPUTE.value, 100, 100)
        ]
        self.allocator = ResourceAllocator(self.resources)
    
    def test_generate_schedule(self):
        """Test schedule generation."""
        tasks = [
            (Task("t1", "Task 1", "Test", estimated_duration_minutes=30), 10.0),
            (Task("t2", "Task 2", "Test", estimated_duration_minutes=20), 8.0)
        ]
        
        schedule = self.optimizer.generate_schedule(tasks, self.allocator)
        
        self.assertEqual(len(schedule), 2)
        self.assertIsNotNone(schedule[0].start_time)
        self.assertIsNotNone(schedule[0].end_time)
    
    def test_schedule_respects_dependencies(self):
        """Test that schedule respects task dependencies."""
        task1 = Task("t1", "Task 1", "Test", estimated_duration_minutes=30)
        task2 = Task("t2", "Task 2", "Test", estimated_duration_minutes=20, dependencies=["t1"])
        
        tasks = [(task1, 10.0), (task2, 8.0)]
        schedule = self.optimizer.generate_schedule(tasks, self.allocator)
        
        # Task 1 should be scheduled before Task 2
        t1_scheduled = next((s for s in schedule if s.task.task_id == "t1"), None)
        t2_scheduled = next((s for s in schedule if s.task.task_id == "t2"), None)
        
        if t1_scheduled and t2_scheduled:
            t1_end = datetime.fromisoformat(t1_scheduled.end_time)
            t2_start = datetime.fromisoformat(t2_scheduled.start_time)
            self.assertLessEqual(t1_end, t2_start)
    
    def test_get_completion_time(self):
        """Test getting completion time."""
        tasks = [
            (Task("t1", "Task 1", "Test", estimated_duration_minutes=30), 10.0)
        ]
        
        self.optimizer.generate_schedule(tasks, self.allocator)
        completion_time = self.optimizer.get_completion_time()
        
        self.assertIsNotNone(completion_time)
        self.assertIsInstance(completion_time, datetime)


class TestAdaptiveLearner(unittest.TestCase):
    """Test adaptive learning."""
    
    def setUp(self):
        self.learner = AdaptiveLearner(learning_rate=0.2)
    
    def test_record_task_completion(self):
        """Test recording task completion."""
        task = Task("t1", "Test", "Test", estimated_duration_minutes=30)
        
        self.learner.record_task_completion(task, 35, True)
        
        self.assertEqual(len(self.learner.task_history), 1)
    
    def test_get_improved_estimate(self):
        """Test getting improved estimates."""
        task = Task("t1", "Test", "Test", estimated_duration_minutes=30)
        task.metadata['type'] = 'code_review'
        
        # Record several completions
        for actual in [35, 40, 38, 37]:
            self.learner.record_task_completion(task, actual, True)
        
        # New task of same type
        new_task = Task("t2", "Test 2", "Test", estimated_duration_minutes=30)
        new_task.metadata['type'] = 'code_review'
        
        improved = self.learner.get_improved_estimate(new_task)
        
        # Should be closer to historical average (37.5) than original (30)
        self.assertGreater(improved, 30)
        self.assertLess(improved, 40)
    
    def test_get_success_rate(self):
        """Test getting success rate."""
        task = Task("t1", "Test", "Test")
        task.metadata['type'] = 'deployment'
        
        # Record 3 successes, 1 failure
        self.learner.record_task_completion(task, 30, True)
        self.learner.record_task_completion(task, 30, True)
        self.learner.record_task_completion(task, 30, False)
        self.learner.record_task_completion(task, 30, True)
        
        success_rate = self.learner.get_success_rate('deployment')
        self.assertAlmostEqual(success_rate, 0.75, places=2)
    
    def test_suggest_priority_adjustment(self):
        """Test priority adjustment suggestions."""
        task = Task("t1", "Test", "Test", priority=TaskPriority.MEDIUM.value)
        task.metadata['type'] = 'risky_task'
        
        # Record low success rate
        for _ in range(10):
            self.learner.record_task_completion(task, 30, False)
        
        suggestion = self.learner.suggest_priority_adjustment(task)
        self.assertEqual(suggestion, "increase")


class TestTaskManagementOptimizer(unittest.TestCase):
    """Test main task management optimizer."""
    
    def setUp(self):
        self.optimizer = TaskManagementOptimizer()
        
        # Add resources
        self.optimizer.add_resource(
            Resource("cpu1", "CPU 1", ResourceType.COMPUTE.value, 100, 100)
        )
    
    def test_add_task(self):
        """Test adding tasks."""
        task = Task("t1", "Test", "Test")
        self.optimizer.add_task(task)
        
        self.assertIn("t1", self.optimizer.tasks)
    
    def test_add_resource(self):
        """Test adding resources."""
        resource = Resource("mem1", "Memory", ResourceType.MEMORY.value, 1000, 1000)
        self.optimizer.add_resource(resource)
        
        self.assertIn("mem1", self.optimizer.resources)
    
    def test_optimize_and_schedule(self):
        """Test optimization and scheduling."""
        tasks = [
            Task("t1", "Task 1", "Test", priority=TaskPriority.HIGH.value),
            Task("t2", "Task 2", "Test", priority=TaskPriority.LOW.value)
        ]
        
        for task in tasks:
            self.optimizer.add_task(task)
        
        schedule = self.optimizer.optimize_and_schedule()
        
        self.assertGreater(len(schedule), 0)
        # High priority task should be scheduled first
        self.assertEqual(schedule[0].task.name, "Task 1")
    
    def test_record_completion(self):
        """Test recording task completion."""
        task = Task("t1", "Test", "Test", estimated_duration_minutes=30)
        self.optimizer.add_task(task)
        
        self.optimizer.record_completion("t1", 35, True)
        
        self.assertEqual(self.optimizer.tasks["t1"].status, TaskStatus.COMPLETED.value)
        self.assertEqual(len(self.optimizer.adaptive_learner.task_history), 1)
    
    def test_get_optimization_report(self):
        """Test getting optimization report."""
        task = Task("t1", "Test", "Test")
        self.optimizer.add_task(task)
        
        report = self.optimizer.get_optimization_report()
        
        self.assertIn('total_tasks', report)
        self.assertIn('pending_tasks', report)
        self.assertIn('resource_utilization', report)
        self.assertEqual(report['total_tasks'], 1)
    
    def test_learning_improves_estimates(self):
        """Test that learning improves duration estimates."""
        # Add task with initial estimate
        task1 = Task("t1", "Code Review", "Test", estimated_duration_minutes=30)
        task1.metadata['type'] = 'code_review'
        self.optimizer.add_task(task1)
        
        # Record actual durations (consistently 45 minutes)
        for i in range(5):
            self.optimizer.record_completion(f"t{i+1}", 45, True)
            if i < 4:
                task = Task(f"t{i+2}", "Code Review", "Test", estimated_duration_minutes=30)
                task.metadata['type'] = 'code_review'
                self.optimizer.add_task(task)
        
        # Add new task - estimate should be improved
        new_task = Task("t_new", "Code Review", "Test", estimated_duration_minutes=30)
        new_task.metadata['type'] = 'code_review'
        self.optimizer.add_task(new_task)
        
        # Estimate should be closer to 45 than 30
        improved_estimate = self.optimizer.tasks["t_new"].estimated_duration_minutes
        self.assertGreater(improved_estimate, 30)


if __name__ == '__main__':
    unittest.main()
