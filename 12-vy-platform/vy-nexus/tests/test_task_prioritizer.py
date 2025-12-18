#!/usr/bin/env python3
"""
Test suite for Dynamic Task Prioritizer

Tests all functionality of the task prioritization system.
"""

import unittest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.adaptation.task_prioritizer import (
    DynamicTaskPrioritizer,
    Task,
    TaskPriority,
    TaskStatus,
    UrgencyLevel,
    PrioritizationContext
)


class TestTaskPrioritizer(unittest.TestCase):
    """Test cases for DynamicTaskPrioritizer"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.prioritizer = DynamicTaskPrioritizer(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test prioritizer initialization"""
        self.assertIsNotNone(self.prioritizer)
        self.assertEqual(len(self.prioritizer.tasks), 0)
        self.assertTrue(Path(self.test_dir).exists())
    
    def test_add_task(self):
        """Test adding a task"""
        task = self.prioritizer.add_task(
            title="Test Task",
            description="Test description",
            impact_score=75,
            effort_estimate=2.0,
            category="development"
        )
        
        self.assertIsNotNone(task)
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.impact_score, 75)
        self.assertEqual(task.effort_estimate, 2.0)
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertIn(task.id, self.prioritizer.tasks)
    
    def test_add_task_with_deadline(self):
        """Test adding task with deadline"""
        deadline = datetime.now() + timedelta(hours=3)
        task = self.prioritizer.add_task(
            title="Urgent Task",
            description="Needs to be done soon",
            impact_score=80,
            effort_estimate=1.0,
            deadline=deadline
        )
        
        self.assertEqual(task.urgency, UrgencyLevel.IMMEDIATE)
        self.assertEqual(task.priority, TaskPriority.CRITICAL)
    
    def test_urgency_calculation(self):
        """Test urgency level calculation"""
        # Immediate (< 6 hours)
        deadline = datetime.now() + timedelta(hours=3)
        urgency = self.prioritizer._calculate_urgency(deadline)
        self.assertEqual(urgency, UrgencyLevel.IMMEDIATE)
        
        # Urgent (< 48 hours)
        deadline = datetime.now() + timedelta(hours=24)
        urgency = self.prioritizer._calculate_urgency(deadline)
        self.assertEqual(urgency, UrgencyLevel.URGENT)
        
        # Soon (< 1 week)
        deadline = datetime.now() + timedelta(days=3)
        urgency = self.prioritizer._calculate_urgency(deadline)
        self.assertEqual(urgency, UrgencyLevel.SOON)
        
        # Flexible (> 1 week)
        deadline = datetime.now() + timedelta(days=10)
        urgency = self.prioritizer._calculate_urgency(deadline)
        self.assertEqual(urgency, UrgencyLevel.FLEXIBLE)
        
        # No deadline
        urgency = self.prioritizer._calculate_urgency(None)
        self.assertEqual(urgency, UrgencyLevel.NORMAL)
    
    def test_priority_score_calculation(self):
        """Test priority score calculation"""
        task = self.prioritizer.add_task(
            title="High Impact Task",
            description="Important work",
            impact_score=90,
            effort_estimate=2.0,
            deadline=datetime.now() + timedelta(hours=4)
        )
        
        score = self.prioritizer.calculate_priority_score(task)
        
        # Should have high score due to:
        # - High urgency (IMMEDIATE = 30 points)
        # - High impact (90/100 * 30 = 27 points)
        # - Good efficiency (90/2 = 45, capped at 15 points)
        # - No dependencies (10 points)
        # Total should be > 80
        self.assertGreater(score, 80)
        self.assertEqual(task.priority_score, score)
    
    def test_priority_score_with_context(self):
        """Test priority score with context"""
        task = self.prioritizer.add_task(
            title="Development Task",
            description="Code work",
            impact_score=70,
            effort_estimate=3.0,
            category="development"
        )
        
        context = PrioritizationContext(
            current_time=datetime.now(),
            user_focus_area="development",
            available_time=4.0,
            energy_level="high",
            preferred_categories=["development"]
        )
        
        score = self.prioritizer.calculate_priority_score(task, context)
        
        # Should have context boost
        self.assertGreater(task.context_boost, 0)
        self.assertGreater(score, 50)
    
    def test_prioritize_tasks(self):
        """Test task prioritization"""
        # Add multiple tasks
        task1 = self.prioritizer.add_task(
            title="Critical Task",
            description="Very urgent",
            impact_score=95,
            effort_estimate=1.0,
            deadline=datetime.now() + timedelta(hours=2)
        )
        
        task2 = self.prioritizer.add_task(
            title="Important Task",
            description="High impact",
            impact_score=80,
            effort_estimate=3.0
        )
        
        task3 = self.prioritizer.add_task(
            title="Low Priority Task",
            description="Can wait",
            impact_score=30,
            effort_estimate=5.0
        )
        
        # Prioritize
        prioritized = self.prioritizer.prioritize_tasks()
        
        # Should be sorted by priority score
        self.assertEqual(len(prioritized), 3)
        self.assertEqual(prioritized[0].id, task1.id)  # Highest priority
        self.assertGreater(
            prioritized[0].priority_score,
            prioritized[1].priority_score
        )
        self.assertGreater(
            prioritized[1].priority_score,
            prioritized[2].priority_score
        )
    
    def test_prioritize_with_limit(self):
        """Test prioritization with limit"""
        for i in range(5):
            self.prioritizer.add_task(
                title=f"Task {i}",
                description=f"Description {i}",
                impact_score=50 + i * 10,
                effort_estimate=2.0
            )
        
        prioritized = self.prioritizer.prioritize_tasks(limit=3)
        self.assertEqual(len(prioritized), 3)
    
    def test_get_next_task(self):
        """Test getting next task"""
        task1 = self.prioritizer.add_task(
            title="High Priority",
            description="Do first",
            impact_score=90,
            effort_estimate=1.0
        )
        
        task2 = self.prioritizer.add_task(
            title="Low Priority",
            description="Do later",
            impact_score=40,
            effort_estimate=2.0
        )
        
        next_task = self.prioritizer.get_next_task()
        self.assertIsNotNone(next_task)
        self.assertEqual(next_task.id, task1.id)
    
    def test_update_task_status(self):
        """Test updating task status"""
        task = self.prioritizer.add_task(
            title="Test Task",
            description="Test",
            impact_score=60,
            effort_estimate=2.0
        )
        
        self.prioritizer.update_task_status(
            task.id,
            TaskStatus.IN_PROGRESS
        )
        
        updated_task = self.prioritizer.get_task(task.id)
        self.assertEqual(updated_task.status, TaskStatus.IN_PROGRESS)
    
    def test_complete_task(self):
        """Test completing a task"""
        task = self.prioritizer.add_task(
            title="Test Task",
            description="Test",
            impact_score=60,
            effort_estimate=2.0,
            category="testing"
        )
        
        self.prioritizer.update_task_status(
            task.id,
            TaskStatus.COMPLETED,
            completion_time=2.5
        )
        
        updated_task = self.prioritizer.get_task(task.id)
        self.assertEqual(updated_task.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(updated_task.completed_at)
        
        # Check learning
        self.assertIn("testing", self.prioritizer.completion_patterns)
        pattern = self.prioritizer.completion_patterns["testing"]
        self.assertEqual(pattern["total_tasks"], 1)
    
    def test_task_dependencies(self):
        """Test task dependencies"""
        task1 = self.prioritizer.add_task(
            title="Foundation Task",
            description="Must do first",
            impact_score=70,
            effort_estimate=2.0
        )
        
        task2 = self.prioritizer.add_task(
            title="Dependent Task",
            description="Depends on task1",
            impact_score=80,
            effort_estimate=3.0,
            dependencies=[task1.id]
        )
        
        # Task2 should have lower score due to incomplete dependency
        score1 = self.prioritizer.calculate_priority_score(task1)
        score2 = self.prioritizer.calculate_priority_score(task2)
        
        # Complete task1
        self.prioritizer.update_task_status(task1.id, TaskStatus.COMPLETED)
        
        # Recalculate task2 score - should be higher now
        score2_after = self.prioritizer.calculate_priority_score(task2)
        self.assertGreater(score2_after, score2)
    
    def test_get_blocked_tasks(self):
        """Test getting blocked tasks"""
        task1 = self.prioritizer.add_task(
            title="Blocker",
            description="Blocks others",
            impact_score=60,
            effort_estimate=1.0
        )
        
        task2 = self.prioritizer.add_task(
            title="Blocked",
            description="Waiting",
            impact_score=70,
            effort_estimate=2.0,
            dependencies=[task1.id]
        )
        
        blocked = self.prioritizer.get_blocked_tasks()
        self.assertEqual(len(blocked), 1)
        self.assertEqual(blocked[0].id, task2.id)
    
    def test_get_ready_tasks(self):
        """Test getting ready tasks"""
        task1 = self.prioritizer.add_task(
            title="Ready Task",
            description="No dependencies",
            impact_score=60,
            effort_estimate=1.0
        )
        
        task2 = self.prioritizer.add_task(
            title="Blocked Task",
            description="Has dependencies",
            impact_score=70,
            effort_estimate=2.0,
            dependencies=["nonexistent"]
        )
        
        ready = self.prioritizer.get_ready_tasks()
        self.assertGreaterEqual(len(ready), 1)
        self.assertIn(task1.id, [t.id for t in ready])
    
    def test_get_tasks_by_category(self):
        """Test getting tasks by category"""
        self.prioritizer.add_task(
            title="Dev Task 1",
            description="Development",
            impact_score=60,
            effort_estimate=2.0,
            category="development"
        )
        
        self.prioritizer.add_task(
            title="Dev Task 2",
            description="Development",
            impact_score=70,
            effort_estimate=3.0,
            category="development"
        )
        
        self.prioritizer.add_task(
            title="Design Task",
            description="Design",
            impact_score=50,
            effort_estimate=1.0,
            category="design"
        )
        
        dev_tasks = self.prioritizer.get_tasks_by_category("development")
        self.assertEqual(len(dev_tasks), 2)
    
    def test_get_statistics(self):
        """Test getting statistics"""
        self.prioritizer.add_task(
            title="Task 1",
            description="Test",
            impact_score=60,
            effort_estimate=2.0,
            category="development"
        )
        
        task2 = self.prioritizer.add_task(
            title="Task 2",
            description="Test",
            impact_score=70,
            effort_estimate=3.0,
            category="design"
        )
        
        self.prioritizer.update_task_status(task2.id, TaskStatus.COMPLETED)
        
        stats = self.prioritizer.get_statistics()
        
        self.assertEqual(stats["total_tasks"], 2)
        self.assertEqual(stats["by_status"][TaskStatus.PENDING.value], 1)
        self.assertEqual(stats["by_status"][TaskStatus.COMPLETED.value], 1)
        self.assertIn("development", stats["by_category"])
        self.assertIn("design", stats["by_category"])
    
    def test_task_serialization(self):
        """Test task to/from dict"""
        task = self.prioritizer.add_task(
            title="Serialization Test",
            description="Test serialization",
            impact_score=75,
            effort_estimate=2.0,
            deadline=datetime.now() + timedelta(days=1),
            category="testing",
            tags=["test", "serialization"]
        )
        
        # Convert to dict
        task_dict = task.to_dict()
        self.assertIsInstance(task_dict, dict)
        self.assertEqual(task_dict["title"], "Serialization Test")
        
        # Convert back
        restored_task = Task.from_dict(task_dict)
        self.assertEqual(restored_task.title, task.title)
        self.assertEqual(restored_task.impact_score, task.impact_score)
        self.assertEqual(restored_task.status, task.status)
    
    def test_persistence(self):
        """Test data persistence"""
        task = self.prioritizer.add_task(
            title="Persistent Task",
            description="Should persist",
            impact_score=65,
            effort_estimate=2.0
        )
        
        task_id = task.id
        
        # Create new prioritizer instance
        new_prioritizer = DynamicTaskPrioritizer(data_dir=self.test_dir)
        
        # Task should be loaded
        loaded_task = new_prioritizer.get_task(task_id)
        self.assertIsNotNone(loaded_task)
        self.assertEqual(loaded_task.title, "Persistent Task")
    
    def test_completion_pattern_learning(self):
        """Test learning from task completion"""
        task = self.prioritizer.add_task(
            title="Learning Task",
            description="Test learning",
            impact_score=60,
            effort_estimate=2.0,
            category="learning"
        )
        
        # Complete with actual time
        self.prioritizer.update_task_status(
            task.id,
            TaskStatus.COMPLETED,
            completion_time=2.5
        )
        
        # Check pattern was learned
        self.assertIn("learning", self.prioritizer.completion_patterns)
        pattern = self.prioritizer.completion_patterns["learning"]
        self.assertEqual(pattern["total_tasks"], 1)
        self.assertGreater(pattern["avg_estimate_accuracy"], 0)
    
    def test_context_energy_matching(self):
        """Test energy level context matching"""
        high_impact_task = self.prioritizer.add_task(
            title="High Impact",
            description="Requires focus",
            impact_score=90,
            effort_estimate=4.0
        )
        
        quick_task = self.prioritizer.add_task(
            title="Quick Task",
            description="Easy win",
            impact_score=40,
            effort_estimate=0.5
        )
        
        # High energy context
        high_energy_context = PrioritizationContext(
            current_time=datetime.now(),
            energy_level="high"
        )
        
        score_high_impact = self.prioritizer.calculate_priority_score(
            high_impact_task,
            high_energy_context
        )
        
        # Low energy context
        low_energy_context = PrioritizationContext(
            current_time=datetime.now(),
            energy_level="low"
        )
        
        score_quick = self.prioritizer.calculate_priority_score(
            quick_task,
            low_energy_context
        )
        
        # Both should have context boost
        self.assertGreater(high_impact_task.context_boost, 0)
        self.assertGreater(quick_task.context_boost, 0)
    
    def test_multiple_tasks_prioritization(self):
        """Test prioritization with many tasks"""
        # Create 10 tasks with varying properties
        for i in range(10):
            deadline = None
            if i % 3 == 0:
                deadline = datetime.now() + timedelta(hours=i + 1)
            
            self.prioritizer.add_task(
                title=f"Task {i}",
                description=f"Description {i}",
                impact_score=30 + i * 7,
                effort_estimate=1.0 + i * 0.5,
                deadline=deadline,
                category=f"category_{i % 3}"
            )
        
        # Prioritize all
        prioritized = self.prioritizer.prioritize_tasks()
        
        self.assertEqual(len(prioritized), 10)
        
        # Verify sorting
        for i in range(len(prioritized) - 1):
            self.assertGreaterEqual(
                prioritized[i].priority_score,
                prioritized[i + 1].priority_score
            )
    
    def test_empty_prioritization(self):
        """Test prioritization with no tasks"""
        prioritized = self.prioritizer.prioritize_tasks()
        self.assertEqual(len(prioritized), 0)
        
        next_task = self.prioritizer.get_next_task()
        self.assertIsNone(next_task)


if __name__ == '__main__':
    unittest.main()
