#!/usr/bin/env python3
"""
Queue Idempotency Tests

Tests that the task queue system handles duplicate submissions correctly:
- Same task submitted multiple times should only execute once
- Task IDs should be unique and stable
- Queue should deduplicate based on task content/hash
"""

import pytest
import hashlib
import json
from typing import Dict, Any, List


class SimpleTaskQueue:
    """Minimal task queue with idempotency guarantees"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.execution_count: Dict[str, int] = {}
    
    def _generate_task_id(self, task_data: Dict[str, Any]) -> str:
        """Generate stable task ID from task content"""
        # Sort keys for stable hashing
        canonical = json.dumps(task_data, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]
    
    def submit(self, task_data: Dict[str, Any]) -> str:
        """Submit task, returns task_id. Idempotent."""
        task_id = self._generate_task_id(task_data)
        
        if task_id not in self.tasks:
            self.tasks[task_id] = task_data
            self.execution_count[task_id] = 0
        
        return task_id
    
    def execute(self, task_id: str) -> bool:
        """Execute task by ID. Returns True if executed."""
        if task_id in self.tasks and self.execution_count[task_id] == 0:
            self.execution_count[task_id] = 1
            return True
        return False
    
    def get_execution_count(self, task_id: str) -> int:
        """Get how many times task was executed"""
        return self.execution_count.get(task_id, 0)


def test_duplicate_submission_same_id():
    """Test 1: Submitting same task multiple times returns same ID"""
    queue = SimpleTaskQueue()
    
    task = {"action": "process", "data": "test123"}
    
    id1 = queue.submit(task)
    id2 = queue.submit(task)
    id3 = queue.submit(task)
    
    assert id1 == id2 == id3, "Same task should generate same ID"
    assert len(queue.tasks) == 1, "Should only have 1 task in queue"


def test_execution_idempotency():
    """Test 2: Task executes only once even if submitted multiple times"""
    queue = SimpleTaskQueue()
    
    task = {"action": "critical_operation", "value": 42}
    
    # Submit same task 5 times
    task_id = None
    for _ in range(5):
        task_id = queue.submit(task)
    
    # Execute the task
    executed = queue.execute(task_id)
    assert executed is True, "First execution should succeed"
    
    # Try to execute again
    executed_again = queue.execute(task_id)
    assert executed_again is False, "Second execution should be blocked"
    
    # Verify execution count
    count = queue.get_execution_count(task_id)
    assert count == 1, f"Task should execute exactly once, got {count}"


def test_different_tasks_different_ids():
    """Test 3: Different tasks get different IDs"""
    queue = SimpleTaskQueue()
    
    task1 = {"action": "process", "data": "A"}
    task2 = {"action": "process", "data": "B"}
    task3 = {"action": "analyze", "data": "A"}
    
    id1 = queue.submit(task1)
    id2 = queue.submit(task2)
    id3 = queue.submit(task3)
    
    assert id1 != id2, "Different data should give different IDs"
    assert id1 != id3, "Different actions should give different IDs"
    assert id2 != id3, "Different tasks should give different IDs"
    assert len(queue.tasks) == 3, "Should have 3 distinct tasks"


if __name__ == "__main__":
    # Run tests directly
    print("Running Queue Idempotency Tests...")
    
    try:
        test_duplicate_submission_same_id()
        print("✓ Test 1: Duplicate submission same ID - PASS")
    except AssertionError as e:
        print(f"✗ Test 1: Duplicate submission same ID - FAIL: {e}")
    
    try:
        test_execution_idempotency()
        print("✓ Test 2: Execution idempotency - PASS")
    except AssertionError as e:
        print(f"✗ Test 2: Execution idempotency - FAIL: {e}")
    
    try:
        test_different_tasks_different_ids()
        print("✓ Test 3: Different tasks different IDs - PASS")
    except AssertionError as e:
        print(f"✗ Test 3: Different tasks different IDs - FAIL: {e}")
    
    print("\nAll idempotency tests completed!")
