#!/usr/bin/env python3
"""
Adaptive Task Management Algorithms

Intelligent task management that adapts based on:
- User behavior patterns
- Task completion history
- Resource availability
- Priority changes
- Context and timing

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import math


class AdaptiveTaskManagement:
    """
    Adaptive task management system that learns and optimizes.
    
    Features:
    - Dynamic priority adjustment
    - Context-aware scheduling
    - Resource-based allocation
    - Deadline prediction
    - Workload balancing
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/task_management"):
        """
        Initialize the adaptive task management system.
        
        Args:
            data_dir: Directory to store task data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.tasks_file = os.path.join(self.data_dir, "tasks.json")
        self.history_file = os.path.join(self.data_dir, "task_history.json")
        self.patterns_file = os.path.join(self.data_dir, "patterns.json")
        self.config_file = os.path.join(self.data_dir, "config.json")
        
        self.tasks = self._load_tasks()
        self.history = self._load_history()
        self.patterns = self._load_patterns()
        self.config = self._load_config()
    
    def _load_tasks(self) -> Dict[str, Any]:
        """Load tasks from file."""
        if os.path.exists(self.tasks_file):
            with open(self.tasks_file, 'r') as f:
                return json.load(f)
        return {"tasks": [], "metadata": {"total_tasks": 0, "completed_tasks": 0}}
    
    def _save_tasks(self):
        """Save tasks to file."""
        with open(self.tasks_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def _load_history(self) -> Dict[str, Any]:
        """Load task history from file."""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return {"completed_tasks": []}
    
    def _save_history(self):
        """Save history to file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load learned patterns from file."""
        if os.path.exists(self.patterns_file):
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        return {
            "task_type_durations": {},
            "optimal_times": {},
            "success_factors": {},
            "dependency_patterns": {}
        }
    
    def _save_patterns(self):
        """Save patterns to file."""
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        
        config = {
            "priority_weights": {
                "urgency": 0.4,
                "importance": 0.3,
                "effort": 0.15,
                "dependencies": 0.15
            },
            "adaptation_rate": 0.1,
            "min_confidence": 0.6,
            "workload_threshold": 0.8
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def create_task(self,
                   title: str,
                   description: str,
                   task_type: str,
                   priority: int = 5,
                   estimated_duration: int = None,
                   deadline: str = None,
                   dependencies: List[str] = None,
                   context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a new task.
        
        Args:
            title: Task title
            description: Task description
            task_type: Type of task
            priority: Initial priority (1-10)
            estimated_duration: Estimated duration in minutes
            deadline: Deadline timestamp
            dependencies: List of task IDs this depends on
            context: Additional context information
        
        Returns:
            Created task
        """
        task_id = f"task_{len(self.tasks['tasks']) + 1:06d}"
        
        # Predict duration if not provided
        if estimated_duration is None:
            estimated_duration = self._predict_duration(task_type, context or {})
        
        task = {
            "task_id": task_id,
            "title": title,
            "description": description,
            "task_type": task_type,
            "status": "pending",
            "priority": priority,
            "adaptive_priority": priority,
            "estimated_duration": estimated_duration,
            "actual_duration": None,
            "deadline": deadline,
            "dependencies": dependencies or [],
            "context": context or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "attempts": 0,
            "success_probability": 0.5
        }
        
        self.tasks["tasks"].append(task)
        self.tasks["metadata"]["total_tasks"] += 1
        self._save_tasks()
        
        # Update adaptive priority
        self._update_adaptive_priority(task_id)
        
        return task
    
    def _predict_duration(self, task_type: str, context: Dict[str, Any]) -> int:
        """
        Predict task duration based on historical data.
        
        Args:
            task_type: Type of task
            context: Task context
        
        Returns:
            Predicted duration in minutes
        """
        if task_type in self.patterns["task_type_durations"]:
            durations = self.patterns["task_type_durations"][task_type]
            if durations:
                avg_duration = sum(durations) / len(durations)
                return int(avg_duration)
        
        # Default estimates by complexity
        complexity = context.get("complexity", "medium")
        defaults = {"low": 15, "medium": 30, "high": 60}
        return defaults.get(complexity, 30)
    
    def _update_adaptive_priority(self, task_id: str):
        """
        Update task's adaptive priority based on multiple factors.
        
        Args:
            task_id: ID of task
        """
        task = self._get_task(task_id)
        if not task:
            return
        
        weights = self.config["priority_weights"]
        
        # Factor 1: Urgency (based on deadline)
        urgency_score = self._calculate_urgency(task)
        
        # Factor 2: Importance (base priority)
        importance_score = task["priority"] / 10.0
        
        # Factor 3: Effort (inverse - prefer quick wins)
        effort_score = 1.0 - (min(task["estimated_duration"], 120) / 120.0)
        
        # Factor 4: Dependencies (tasks blocking others get higher priority)
        dependency_score = self._calculate_dependency_score(task_id)
        
        # Calculate weighted adaptive priority
        adaptive_priority = (
            urgency_score * weights["urgency"] +
            importance_score * weights["importance"] +
            effort_score * weights["effort"] +
            dependency_score * weights["dependencies"]
        ) * 10
        
        task["adaptive_priority"] = round(adaptive_priority, 2)
        task["updated_at"] = datetime.now().isoformat()
        self._save_tasks()
    
    def _calculate_urgency(self, task: Dict[str, Any]) -> float:
        """
        Calculate urgency score based on deadline.
        
        Args:
            task: Task dictionary
        
        Returns:
            Urgency score (0-1)
        """
        if not task["deadline"]:
            return 0.5  # Medium urgency if no deadline
        
        try:
            deadline = datetime.fromisoformat(task["deadline"])
            now = datetime.now()
            time_remaining = (deadline - now).total_seconds() / 3600  # hours
            
            if time_remaining <= 0:
                return 1.0  # Overdue
            elif time_remaining <= 24:
                return 0.9  # Due within 24 hours
            elif time_remaining <= 72:
                return 0.7  # Due within 3 days
            elif time_remaining <= 168:
                return 0.5  # Due within 1 week
            else:
                return 0.3  # More than 1 week away
        except:
            return 0.5
    
    def _calculate_dependency_score(self, task_id: str) -> float:
        """
        Calculate dependency score (how many tasks depend on this one).
        
        Args:
            task_id: ID of task
        
        Returns:
            Dependency score (0-1)
        """
        # Count how many tasks depend on this one
        dependent_count = sum(
            1 for t in self.tasks["tasks"]
            if task_id in t.get("dependencies", [])
        )
        
        # Normalize (assume max 5 dependent tasks)
        return min(dependent_count / 5.0, 1.0)
    
    def start_task(self, task_id: str) -> bool:
        """
        Mark task as started.
        
        Args:
            task_id: ID of task
        
        Returns:
            True if started successfully
        """
        task = self._get_task(task_id)
        if not task or task["status"] != "pending":
            return False
        
        # Check dependencies
        if not self._check_dependencies(task_id):
            return False
        
        task["status"] = "in_progress"
        task["started_at"] = datetime.now().isoformat()
        task["attempts"] += 1
        task["updated_at"] = datetime.now().isoformat()
        self._save_tasks()
        
        return True
    
    def _check_dependencies(self, task_id: str) -> bool:
        """
        Check if all dependencies are completed.
        
        Args:
            task_id: ID of task
        
        Returns:
            True if all dependencies met
        """
        task = self._get_task(task_id)
        if not task:
            return False
        
        for dep_id in task.get("dependencies", []):
            dep_task = self._get_task(dep_id)
            if not dep_task or dep_task["status"] != "completed":
                return False
        
        return True
    
    def complete_task(self, task_id: str, success: bool = True, notes: str = "") -> bool:
        """
        Mark task as completed.
        
        Args:
            task_id: ID of task
            success: Whether task was successful
            notes: Completion notes
        
        Returns:
            True if completed successfully
        """
        task = self._get_task(task_id)
        if not task or task["status"] != "in_progress":
            return False
        
        # Calculate actual duration
        if task["started_at"]:
            started = datetime.fromisoformat(task["started_at"])
            completed = datetime.now()
            actual_duration = (completed - started).total_seconds() / 60  # minutes
            task["actual_duration"] = round(actual_duration, 2)
        
        task["status"] = "completed" if success else "failed"
        task["completed_at"] = datetime.now().isoformat()
        task["completion_notes"] = notes
        task["updated_at"] = datetime.now().isoformat()
        
        if success:
            self.tasks["metadata"]["completed_tasks"] += 1
        
        self._save_tasks()
        
        # Learn from completion
        self._learn_from_completion(task)
        
        # Move to history
        self.history["completed_tasks"].append(task.copy())
        self._save_history()
        
        return True
    
    def _learn_from_completion(self, task: Dict[str, Any]):
        """
        Learn patterns from completed task.
        
        Args:
            task: Completed task
        """
        task_type = task["task_type"]
        
        # Learn duration patterns
        if task["actual_duration"]:
            if task_type not in self.patterns["task_type_durations"]:
                self.patterns["task_type_durations"][task_type] = []
            
            self.patterns["task_type_durations"][task_type].append(task["actual_duration"])
            
            # Keep only recent 20 samples
            if len(self.patterns["task_type_durations"][task_type]) > 20:
                self.patterns["task_type_durations"][task_type] = \
                    self.patterns["task_type_durations"][task_type][-20:]
        
        # Learn optimal completion times
        if task["completed_at"]:
            completed_time = datetime.fromisoformat(task["completed_at"])
            hour = completed_time.hour
            
            if task_type not in self.patterns["optimal_times"]:
                self.patterns["optimal_times"][task_type] = {}
            
            hour_key = str(hour)
            if hour_key not in self.patterns["optimal_times"][task_type]:
                self.patterns["optimal_times"][task_type][hour_key] = {"count": 0, "success_rate": 0}
            
            stats = self.patterns["optimal_times"][task_type][hour_key]
            stats["count"] += 1
            
            # Update success rate
            if task["status"] == "completed":
                stats["success_rate"] = ((stats["success_rate"] * (stats["count"] - 1)) + 1) / stats["count"]
        
        self._save_patterns()
    
    def get_next_task(self, context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Get the next recommended task based on adaptive priorities.
        
        Args:
            context: Current context (time, resources, etc.)
        
        Returns:
            Recommended task or None
        """
        context = context or {}
        
        # Get pending tasks with met dependencies
        available_tasks = [
            t for t in self.tasks["tasks"]
            if t["status"] == "pending" and self._check_dependencies(t["task_id"])
        ]
        
        if not available_tasks:
            return None
        
        # Update all adaptive priorities
        for task in available_tasks:
            self._update_adaptive_priority(task["task_id"])
        
        # Consider context
        current_hour = datetime.now().hour
        
        # Score tasks based on adaptive priority and context
        scored_tasks = []
        for task in available_tasks:
            score = task["adaptive_priority"]
            
            # Boost score if this is an optimal time for this task type
            task_type = task["task_type"]
            if task_type in self.patterns["optimal_times"]:
                hour_key = str(current_hour)
                if hour_key in self.patterns["optimal_times"][task_type]:
                    success_rate = self.patterns["optimal_times"][task_type][hour_key]["success_rate"]
                    score *= (1 + success_rate * 0.2)  # Up to 20% boost
            
            # Consider available time
            if "available_time" in context:
                if task["estimated_duration"] <= context["available_time"]:
                    score *= 1.1  # Boost tasks that fit in available time
            
            scored_tasks.append((score, task))
        
        # Sort by score and return highest
        scored_tasks.sort(key=lambda x: x[0], reverse=True)
        return scored_tasks[0][1] if scored_tasks else None
    
    def rebalance_workload(self) -> Dict[str, Any]:
        """
        Rebalance task priorities based on current workload.
        
        Returns:
            Rebalancing summary
        """
        pending_tasks = [t for t in self.tasks["tasks"] if t["status"] == "pending"]
        in_progress_tasks = [t for t in self.tasks["tasks"] if t["status"] == "in_progress"]
        
        # Calculate current workload
        total_estimated_time = sum(t["estimated_duration"] for t in pending_tasks)
        in_progress_time = sum(t["estimated_duration"] for t in in_progress_tasks)
        
        # Check for overdue tasks
        overdue_tasks = []
        for task in pending_tasks:
            if task["deadline"]:
                try:
                    deadline = datetime.fromisoformat(task["deadline"])
                    if deadline < datetime.now():
                        overdue_tasks.append(task)
                except:
                    pass
        
        # Boost priority of overdue tasks
        adjustments = 0
        for task in overdue_tasks:
            if task["adaptive_priority"] < 9:
                task["adaptive_priority"] = min(10, task["adaptive_priority"] + 2)
                adjustments += 1
        
        if adjustments > 0:
            self._save_tasks()
        
        return {
            "total_pending": len(pending_tasks),
            "in_progress": len(in_progress_tasks),
            "overdue": len(overdue_tasks),
            "total_estimated_time": total_estimated_time,
            "adjustments_made": adjustments,
            "workload_status": "high" if total_estimated_time > 480 else "normal"
        }
    
    def _get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID."""
        for task in self.tasks["tasks"]:
            if task["task_id"] == task_id:
                return task
        return None
    
    def get_task_recommendations(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Get top N recommended tasks.
        
        Args:
            n: Number of recommendations
        
        Returns:
            List of recommended tasks
        """
        available_tasks = [
            t for t in self.tasks["tasks"]
            if t["status"] == "pending" and self._check_dependencies(t["task_id"])
        ]
        
        # Update priorities
        for task in available_tasks:
            self._update_adaptive_priority(task["task_id"])
        
        # Sort by adaptive priority
        sorted_tasks = sorted(available_tasks, key=lambda x: x["adaptive_priority"], reverse=True)
        
        return sorted_tasks[:n]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get task management statistics.
        
        Returns:
            Statistics dictionary
        """
        tasks = self.tasks["tasks"]
        
        # Count by status
        status_counts = {}
        for task in tasks:
            status = task["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate completion rate
        total = len(tasks)
        completed = status_counts.get("completed", 0)
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        # Calculate average duration accuracy
        completed_tasks = [t for t in tasks if t["status"] == "completed" and t["actual_duration"]]
        if completed_tasks:
            duration_errors = [
                abs(t["actual_duration"] - t["estimated_duration"]) / t["estimated_duration"]
                for t in completed_tasks if t["estimated_duration"] > 0
            ]
            avg_error = sum(duration_errors) / len(duration_errors) if duration_errors else 0
            duration_accuracy = max(0, (1 - avg_error) * 100)
        else:
            duration_accuracy = 0
        
        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "status_counts": status_counts,
            "completion_rate": round(completion_rate, 2),
            "duration_accuracy": round(duration_accuracy, 2),
            "learned_task_types": len(self.patterns["task_type_durations"]),
            "total_history_entries": len(self.history["completed_tasks"])
        }


def test_adaptive_task_management():
    """Test the adaptive task management system."""
    print("Testing Adaptive Task Management...")
    print("=" * 60)
    
    # Initialize system
    system = AdaptiveTaskManagement()
    
    # Test 1: Create tasks
    print("\n1. Testing task creation...")
    task1 = system.create_task(
        title="Write documentation",
        description="Write API documentation",
        task_type="documentation",
        priority=7,
        estimated_duration=60,
        deadline=(datetime.now() + timedelta(days=2)).isoformat(),
        context={"complexity": "medium"}
    )
    print(f"   Created task: {task1['task_id']}")
    print(f"   Adaptive priority: {task1['adaptive_priority']}")
    
    task2 = system.create_task(
        title="Fix critical bug",
        description="Fix production bug",
        task_type="bugfix",
        priority=9,
        estimated_duration=30,
        deadline=(datetime.now() + timedelta(hours=4)).isoformat(),
        context={"complexity": "high"}
    )
    print(f"   Created urgent task: {task2['task_id']}")
    print(f"   Adaptive priority: {task2['adaptive_priority']}")
    
    # Test 2: Get next task
    print("\n2. Testing next task recommendation...")
    next_task = system.get_next_task({"available_time": 45})
    print(f"   Recommended task: {next_task['title']}")
    print(f"   Priority: {next_task['adaptive_priority']}")
    
    # Test 3: Start task
    print("\n3. Testing task start...")
    started = system.start_task(next_task["task_id"])
    print(f"   Task started: {started}")
    
    # Test 4: Complete task
    print("\n4. Testing task completion...")
    completed = system.complete_task(next_task["task_id"], success=True, notes="Completed successfully")
    print(f"   Task completed: {completed}")
    
    # Test 5: Create dependent tasks
    print("\n5. Testing task dependencies...")
    task3 = system.create_task(
        title="Deploy to production",
        description="Deploy after testing",
        task_type="deployment",
        priority=8,
        dependencies=[task1["task_id"]],
        context={"complexity": "low"}
    )
    print(f"   Created dependent task: {task3['task_id']}")
    print(f"   Dependencies met: {system._check_dependencies(task3['task_id'])}")
    
    # Test 6: Get recommendations
    print("\n6. Testing task recommendations...")
    recommendations = system.get_task_recommendations(n=3)
    print(f"   Top {len(recommendations)} recommendations:")
    for i, task in enumerate(recommendations, 1):
        print(f"      {i}. {task['title']} (Priority: {task['adaptive_priority']:.2f})")
    
    # Test 7: Rebalance workload
    print("\n7. Testing workload rebalancing...")
    rebalance = system.rebalance_workload()
    print(f"   Pending tasks: {rebalance['total_pending']}")
    print(f"   In progress: {rebalance['in_progress']}")
    print(f"   Workload status: {rebalance['workload_status']}")
    
    # Test 8: Get statistics
    print("\n8. Testing statistics...")
    stats = system.get_statistics()
    print(f"   Total tasks: {stats['total_tasks']}")
    print(f"   Completed: {stats['completed_tasks']}")
    print(f"   Completion rate: {stats['completion_rate']}%")
    print(f"   Status counts: {stats['status_counts']}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_adaptive_task_management()
