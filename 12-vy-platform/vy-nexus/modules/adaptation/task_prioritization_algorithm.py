#!/usr/bin/env python3
"""
Task Prioritization Algorithm
Part of the Self-Evolving AI Ecosystem for vy-nexus

This module implements intelligent task prioritization based on urgency,
importance, dependencies, user preferences, and historical patterns.

Features:
- Multi-factor priority scoring
- Dynamic priority adjustment
- Dependency-aware scheduling
- Deadline management
- Resource availability consideration
- User preference learning
- Context-based prioritization
- Adaptive algorithm refinement
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
import heapq
from enum import Enum


class Priority(Enum):
    """Priority levels."""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    MINIMAL = 1


class TaskStatus(Enum):
    """Task status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPrioritizationAlgorithm:
    """
    Implements intelligent task prioritization with adaptive learning.
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/prioritization"):
        """
        Initialize the Task Prioritization Algorithm.
        
        Args:
            data_dir: Directory for storing prioritization data
        """
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Data files
        self.tasks_file = self.data_dir / "tasks.json"
        self.priorities_file = self.data_dir / "priorities.json"
        self.history_file = self.data_dir / "history.json"
        self.weights_file = self.data_dir / "weights.json"
        
        # Priority factors and their default weights
        self.default_weights = {
            "urgency": 0.25,          # Time sensitivity
            "importance": 0.25,       # Strategic value
            "effort": 0.15,           # Resource requirements
            "dependencies": 0.15,     # Blocking other tasks
            "user_preference": 0.10,  # User's stated preference
            "deadline_proximity": 0.10 # How close to deadline
        }
        
        # Load existing data
        self._load_data()
    
    def _load_data(self):
        """Load existing prioritization data."""
        self.tasks = self._load_json(self.tasks_file, {
            "active": {},
            "completed": {},
            "cancelled": {}
        })
        
        self.priorities = self._load_json(self.priorities_file, {
            "queue": [],
            "last_updated": None
        })
        
        self.history = self._load_json(self.history_file, {
            "decisions": [],
            "adjustments": []
        })
        
        self.weights = self._load_json(self.weights_file, {
            "current": self.default_weights.copy(),
            "history": []
        })
    
    def _load_json(self, filepath: Path, default: Any) -> Any:
        """Load JSON data from file or return default."""
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception:
                return default
        return default
    
    def _save_json(self, filepath: Path, data: Any):
        """Save data to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_task(
        self,
        task_id: str,
        title: str,
        description: str,
        urgency: int = 3,
        importance: int = 3,
        estimated_effort_hours: float = 1.0,
        deadline: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new task.
        
        Args:
            task_id: Unique task identifier
            title: Task title
            description: Task description
            urgency: Urgency level (1-5)
            importance: Importance level (1-5)
            estimated_effort_hours: Estimated effort in hours
            deadline: Deadline (ISO format)
            dependencies: List of task IDs this task depends on
            tags: Task tags
            metadata: Additional metadata
            
        Returns:
            Created task
        """
        task = {
            "task_id": task_id,
            "title": title,
            "description": description,
            "urgency": max(1, min(5, urgency)),
            "importance": max(1, min(5, importance)),
            "estimated_effort_hours": estimated_effort_hours,
            "deadline": deadline,
            "dependencies": dependencies or [],
            "tags": tags or [],
            "metadata": metadata or {},
            "status": TaskStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "priority_score": 0.0,
            "completion_time": None
        }
        
        # Calculate initial priority score
        task["priority_score"] = self._calculate_priority_score(task)
        
        # Add to active tasks
        self.tasks["active"][task_id] = task
        self._save_json(self.tasks_file, self.tasks)
        
        # Update priority queue
        self._update_priority_queue()
        
        return task
    
    def _calculate_priority_score(
        self,
        task: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate priority score for a task.
        
        Args:
            task: Task dictionary
            context: Additional context for scoring
            
        Returns:
            Priority score (0-100)
        """
        weights = self.weights["current"]
        scores = {}
        
        # 1. Urgency score (1-5 scale)
        scores["urgency"] = (task["urgency"] / 5.0) * 100
        
        # 2. Importance score (1-5 scale)
        scores["importance"] = (task["importance"] / 5.0) * 100
        
        # 3. Effort score (inverse - lower effort = higher priority)
        max_effort = 40.0  # Assume max 40 hours
        effort_factor = 1.0 - min(task["estimated_effort_hours"] / max_effort, 1.0)
        scores["effort"] = effort_factor * 100
        
        # 4. Dependencies score (tasks blocking others get higher priority)
        blocking_count = self._count_blocking_tasks(task["task_id"])
        scores["dependencies"] = min(blocking_count * 20, 100)
        
        # 5. User preference score
        scores["user_preference"] = self._get_user_preference_score(task)
        
        # 6. Deadline proximity score
        scores["deadline_proximity"] = self._calculate_deadline_score(task)
        
        # Calculate weighted sum
        total_score = sum(
            scores[factor] * weights[factor]
            for factor in weights.keys()
        )
        
        # Apply context modifiers
        if context:
            if context.get("urgent_mode"):
                total_score *= 1.2
            if context.get("focus_area") in task.get("tags", []):
                total_score *= 1.1
        
        return min(100.0, max(0.0, total_score))
    
    def _count_blocking_tasks(self, task_id: str) -> int:
        """Count how many tasks are blocked by this task."""
        count = 0
        for other_task in self.tasks["active"].values():
            if task_id in other_task.get("dependencies", []):
                count += 1
        return count
    
    def _get_user_preference_score(self, task: Dict[str, Any]) -> float:
        """Get user preference score based on task characteristics."""
        # Simple heuristic based on tags and metadata
        score = 50.0  # Default neutral score
        
        # Check for high-priority tags
        high_priority_tags = ["critical", "urgent", "important", "blocker"]
        for tag in task.get("tags", []):
            if tag.lower() in high_priority_tags:
                score += 10.0
        
        # Check metadata for user priority
        if task.get("metadata", {}).get("user_priority"):
            user_priority = task["metadata"]["user_priority"]
            if user_priority == "high":
                score += 20.0
            elif user_priority == "low":
                score -= 20.0
        
        return min(100.0, max(0.0, score))
    
    def _calculate_deadline_score(self, task: Dict[str, Any]) -> float:
        """Calculate score based on deadline proximity."""
        if not task.get("deadline"):
            return 30.0  # Default score for tasks without deadline
        
        try:
            deadline = datetime.fromisoformat(task["deadline"])
            now = datetime.now()
            time_until_deadline = (deadline - now).total_seconds() / 3600  # hours
            
            if time_until_deadline < 0:
                return 100.0  # Overdue
            elif time_until_deadline < 24:
                return 90.0  # Due within 24 hours
            elif time_until_deadline < 72:
                return 70.0  # Due within 3 days
            elif time_until_deadline < 168:
                return 50.0  # Due within 1 week
            else:
                return 30.0  # Due later
        except Exception:
            return 30.0
    
    def _update_priority_queue(self):
        """Update the priority queue based on current tasks."""
        queue = []
        
        for task_id, task in self.tasks["active"].items():
            if task["status"] == TaskStatus.PENDING.value:
                # Check if dependencies are met
                if self._are_dependencies_met(task):
                    # Use negative score for max heap behavior
                    heapq.heappush(queue, (-task["priority_score"], task_id, task))
        
        self.priorities["queue"] = [
            {"task_id": tid, "priority_score": -score, "title": t["title"]}
            for score, tid, t in sorted(queue)
        ]
        self.priorities["last_updated"] = datetime.now().isoformat()
        self._save_json(self.priorities_file, self.priorities)
    
    def _are_dependencies_met(self, task: Dict[str, Any]) -> bool:
        """Check if all task dependencies are completed."""
        for dep_id in task.get("dependencies", []):
            if dep_id in self.tasks["active"]:
                dep_task = self.tasks["active"][dep_id]
                if dep_task["status"] != TaskStatus.COMPLETED.value:
                    return False
            elif dep_id not in self.tasks["completed"]:
                # Dependency doesn't exist
                return False
        return True
    
    def get_next_task(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the next highest priority task.
        
        Args:
            context: Current context for prioritization
            
        Returns:
            Next task to work on, or None if no tasks available
        """
        self._update_priority_queue()
        
        if not self.priorities["queue"]:
            return None
        
        # Get highest priority task
        next_task_info = self.priorities["queue"][0]
        task_id = next_task_info["task_id"]
        
        if task_id in self.tasks["active"]:
            task = self.tasks["active"][task_id]
            
            # Record decision
            self._record_decision(task, context)
            
            return task
        
        return None
    
    def _record_decision(
        self,
        task: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ):
        """Record a prioritization decision."""
        decision = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task["task_id"],
            "priority_score": task["priority_score"],
            "context": context or {},
            "factors": {
                "urgency": task["urgency"],
                "importance": task["importance"],
                "deadline": task.get("deadline")
            }
        }
        
        self.history["decisions"].append(decision)
        self._save_json(self.history_file, self.history)
    
    def update_task_status(
        self,
        task_id: str,
        status: str,
        completion_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Update task status.
        
        Args:
            task_id: Task identifier
            status: New status
            completion_time: Actual completion time in hours (if completed)
            
        Returns:
            Updated task
        """
        if task_id not in self.tasks["active"]:
            return {"error": "Task not found", "task_id": task_id}
        
        task = self.tasks["active"][task_id]
        old_status = task["status"]
        task["status"] = status
        task["updated_at"] = datetime.now().isoformat()
        
        if status == TaskStatus.COMPLETED.value:
            task["completion_time"] = completion_time
            task["completed_at"] = datetime.now().isoformat()
            
            # Move to completed
            self.tasks["completed"][task_id] = task
            del self.tasks["active"][task_id]
            
            # Learn from completion
            self._learn_from_completion(task)
        
        elif status == TaskStatus.CANCELLED.value:
            self.tasks["cancelled"][task_id] = task
            del self.tasks["active"][task_id]
        
        self._save_json(self.tasks_file, self.tasks)
        self._update_priority_queue()
        
        return task
    
    def _learn_from_completion(
        self,
        task: Dict[str, Any]
    ):
        """Learn from task completion to improve prioritization."""
        # Compare estimated vs actual effort
        if task.get("completion_time"):
            estimated = task["estimated_effort_hours"]
            actual = task["completion_time"]
            
            # If estimation was significantly off, adjust weights
            if abs(actual - estimated) / estimated > 0.5:
                # Increase weight of effort factor
                self._adjust_weight("effort", 0.02)
    
    def _adjust_weight(
        self,
        factor: str,
        adjustment: float
    ):
        """Adjust weight for a priority factor."""
        if factor in self.weights["current"]:
            old_weight = self.weights["current"][factor]
            new_weight = max(0.05, min(0.5, old_weight + adjustment))
            self.weights["current"][factor] = new_weight
            
            # Normalize weights to sum to 1.0
            total = sum(self.weights["current"].values())
            for f in self.weights["current"]:
                self.weights["current"][f] /= total
            
            # Record adjustment
            self.history["adjustments"].append({
                "timestamp": datetime.now().isoformat(),
                "factor": factor,
                "old_weight": old_weight,
                "new_weight": new_weight
            })
            
            self._save_json(self.weights_file, self.weights)
            self._save_json(self.history_file, self.history)
    
    def reprioritize_all(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Recalculate priorities for all active tasks.
        
        Args:
            context: Current context
            
        Returns:
            Reprioritization summary
        """
        changes = []
        
        for task_id, task in self.tasks["active"].items():
            old_score = task["priority_score"]
            new_score = self._calculate_priority_score(task, context)
            
            if abs(new_score - old_score) > 5.0:
                changes.append({
                    "task_id": task_id,
                    "title": task["title"],
                    "old_score": old_score,
                    "new_score": new_score,
                    "change": new_score - old_score
                })
            
            task["priority_score"] = new_score
            task["updated_at"] = datetime.now().isoformat()
        
        self._save_json(self.tasks_file, self.tasks)
        self._update_priority_queue()
        
        return {
            "reprioritized_at": datetime.now().isoformat(),
            "total_tasks": len(self.tasks["active"]),
            "significant_changes": len(changes),
            "changes": changes
        }
    
    def get_priority_queue(
        self,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get the current priority queue.
        
        Args:
            limit: Maximum number of tasks to return
            
        Returns:
            List of tasks in priority order
        """
        self._update_priority_queue()
        queue = self.priorities["queue"]
        
        if limit:
            queue = queue[:limit]
        
        # Enrich with full task details
        enriched_queue = []
        for item in queue:
            task_id = item["task_id"]
            if task_id in self.tasks["active"]:
                task = self.tasks["active"][task_id].copy()
                enriched_queue.append(task)
        
        return enriched_queue
    
    def get_blocked_tasks(self) -> List[Dict[str, Any]]:
        """Get tasks that are blocked by dependencies."""
        blocked = []
        
        for task_id, task in self.tasks["active"].items():
            if not self._are_dependencies_met(task):
                unmet_deps = []
                for dep_id in task.get("dependencies", []):
                    if dep_id in self.tasks["active"]:
                        dep_task = self.tasks["active"][dep_id]
                        if dep_task["status"] != TaskStatus.COMPLETED.value:
                            unmet_deps.append({
                                "task_id": dep_id,
                                "title": dep_task["title"],
                                "status": dep_task["status"]
                            })
                
                blocked.append({
                    "task": task,
                    "unmet_dependencies": unmet_deps
                })
        
        return blocked
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get prioritization statistics."""
        active_count = len(self.tasks["active"])
        completed_count = len(self.tasks["completed"])
        cancelled_count = len(self.tasks["cancelled"])
        
        # Calculate average completion time
        completion_times = [
            t["completion_time"]
            for t in self.tasks["completed"].values()
            if t.get("completion_time")
        ]
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        
        # Count by priority level
        priority_distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0, "minimal": 0}
        for task in self.tasks["active"].values():
            score = task["priority_score"]
            if score >= 80:
                priority_distribution["critical"] += 1
            elif score >= 60:
                priority_distribution["high"] += 1
            elif score >= 40:
                priority_distribution["medium"] += 1
            elif score >= 20:
                priority_distribution["low"] += 1
            else:
                priority_distribution["minimal"] += 1
        
        return {
            "active_tasks": active_count,
            "completed_tasks": completed_count,
            "cancelled_tasks": cancelled_count,
            "total_tasks": active_count + completed_count + cancelled_count,
            "avg_completion_time_hours": avg_completion_time,
            "priority_distribution": priority_distribution,
            "current_weights": self.weights["current"],
            "total_decisions": len(self.history["decisions"]),
            "total_adjustments": len(self.history["adjustments"])
        }


def test_task_prioritization():
    """Test the Task Prioritization Algorithm."""
    print("Testing Task Prioritization Algorithm...")
    
    algo = TaskPrioritizationAlgorithm()
    
    # Test 1: Create tasks
    print("\n1. Creating tasks...")
    task1 = algo.create_task(
        task_id="task_001",
        title="Fix critical bug",
        description="Fix production bug affecting users",
        urgency=5,
        importance=5,
        estimated_effort_hours=2.0,
        deadline=(datetime.now() + timedelta(hours=12)).isoformat(),
        tags=["critical", "bug"]
    )
    print(f"   Task 1 created: {task1['title']} (score: {task1['priority_score']:.1f})")
    
    task2 = algo.create_task(
        task_id="task_002",
        title="Implement new feature",
        description="Add requested feature",
        urgency=3,
        importance=4,
        estimated_effort_hours=8.0,
        tags=["feature"]
    )
    print(f"   Task 2 created: {task2['title']} (score: {task2['priority_score']:.1f})")
    
    task3 = algo.create_task(
        task_id="task_003",
        title="Update documentation",
        description="Update user documentation",
        urgency=2,
        importance=2,
        estimated_effort_hours=3.0,
        dependencies=["task_002"]
    )
    print(f"   Task 3 created: {task3['title']} (score: {task3['priority_score']:.1f})")
    
    # Test 2: Get next task
    print("\n2. Getting next task...")
    next_task = algo.get_next_task()
    if next_task:
        print(f"   Next task: {next_task['title']}")
        print(f"   Priority score: {next_task['priority_score']:.1f}")
    
    # Test 3: Get priority queue
    print("\n3. Getting priority queue...")
    queue = algo.get_priority_queue(limit=5)
    print(f"   Tasks in queue: {len(queue)}")
    for i, task in enumerate(queue, 1):
        print(f"   {i}. {task['title']} (score: {task['priority_score']:.1f})")
    
    # Test 4: Update task status
    print("\n4. Updating task status...")
    updated = algo.update_task_status(
        task_id="task_001",
        status=TaskStatus.COMPLETED.value,
        completion_time=1.5
    )
    print(f"   Task completed: {updated['title']}")
    print(f"   Completion time: {updated['completion_time']} hours")
    
    # Test 5: Get blocked tasks
    print("\n5. Getting blocked tasks...")
    blocked = algo.get_blocked_tasks()
    print(f"   Blocked tasks: {len(blocked)}")
    for item in blocked:
        print(f"   - {item['task']['title']} (blocked by {len(item['unmet_dependencies'])} tasks)")
    
    # Test 6: Reprioritize all
    print("\n6. Reprioritizing all tasks...")
    result = algo.reprioritize_all(context={"urgent_mode": True})
    print(f"   Total tasks: {result['total_tasks']}")
    print(f"   Significant changes: {result['significant_changes']}")
    
    # Test 7: Get statistics
    print("\n7. Getting statistics...")
    stats = algo.get_statistics()
    print(f"   Active tasks: {stats['active_tasks']}")
    print(f"   Completed tasks: {stats['completed_tasks']}")
    print(f"   Priority distribution: {stats['priority_distribution']}")
    print(f"   Total decisions: {stats['total_decisions']}")
    
    print("\n✅ All tests completed successfully!")


if __name__ == "__main__":
    test_task_prioritization()
