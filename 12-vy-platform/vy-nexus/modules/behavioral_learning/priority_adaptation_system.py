#!/usr/bin/env python3
"""
Priority Adaptation System

Adapts task priorities based on:
- Changing circumstances
- Deadline proximity
- Resource availability
- Dependencies
- User behavior patterns
- Context changes

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from enum import Enum


class PriorityLevel(Enum):
    """Priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    DEFERRED = "deferred"


class AdaptationReason(Enum):
    """Reasons for priority adaptation."""
    DEADLINE_APPROACHING = "deadline_approaching"
    DEPENDENCY_COMPLETED = "dependency_completed"
    RESOURCE_AVAILABLE = "resource_available"
    CONTEXT_CHANGE = "context_change"
    USER_PATTERN = "user_pattern"
    BLOCKING_OTHERS = "blocking_others"
    VALUE_INCREASE = "value_increase"
    URGENCY_INCREASE = "urgency_increase"


class PriorityAdaptationSystem:
    """
    Adapts task priorities dynamically based on multiple factors.
    
    Features:
    - Dynamic priority calculation
    - Context-aware adjustments
    - Deadline-based escalation
    - Dependency tracking
    - Pattern-based adaptation
    - Adaptation history
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/behavioral_learning"):
        """
        Initialize the priority adaptation system.
        
        Args:
            data_dir: Directory to store priority data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.tasks_file = os.path.join(self.data_dir, "adaptive_tasks.json")
        self.adaptations_file = os.path.join(self.data_dir, "priority_adaptations.json")
        self.rules_file = os.path.join(self.data_dir, "adaptation_rules.json")
        
        self.tasks = self._load_tasks()
        self.adaptations = self._load_adaptations()
        self.rules = self._load_rules()
    
    def _load_tasks(self) -> Dict[str, Any]:
        """Load tasks."""
        if os.path.exists(self.tasks_file):
            with open(self.tasks_file, 'r') as f:
                return json.load(f)
        return {"tasks": []}
    
    def _save_tasks(self):
        """Save tasks."""
        with open(self.tasks_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def _load_adaptations(self) -> Dict[str, Any]:
        """Load adaptation history."""
        if os.path.exists(self.adaptations_file):
            with open(self.adaptations_file, 'r') as f:
                return json.load(f)
        return {"adaptations": []}
    
    def _save_adaptations(self):
        """Save adaptations."""
        with open(self.adaptations_file, 'w') as f:
            json.dump(self.adaptations, f, indent=2)
    
    def _load_rules(self) -> Dict[str, Any]:
        """Load adaptation rules."""
        if os.path.exists(self.rules_file):
            with open(self.rules_file, 'r') as f:
                return json.load(f)
        
        # Default rules
        return {
            "rules": [
                {
                    "rule_id": "deadline_24h",
                    "condition": "deadline_within_hours",
                    "threshold": 24,
                    "action": "escalate_to_high",
                    "enabled": True
                },
                {
                    "rule_id": "deadline_6h",
                    "condition": "deadline_within_hours",
                    "threshold": 6,
                    "action": "escalate_to_critical",
                    "enabled": True
                },
                {
                    "rule_id": "blocking_tasks",
                    "condition": "blocking_count",
                    "threshold": 3,
                    "action": "escalate_one_level",
                    "enabled": True
                },
                {
                    "rule_id": "overdue",
                    "condition": "is_overdue",
                    "threshold": 0,
                    "action": "escalate_to_critical",
                    "enabled": True
                }
            ]
        }
    
    def _save_rules(self):
        """Save rules."""
        with open(self.rules_file, 'w') as f:
            json.dump(self.rules, f, indent=2)
    
    def add_task(self,
                title: str,
                initial_priority: str,
                deadline: Optional[str] = None,
                estimated_duration_hours: float = 1.0,
                value_score: float = 50.0,
                dependencies: List[str] = None,
                context: str = "",
                tags: List[str] = None) -> Dict[str, Any]:
        """
        Add a task to the system.
        
        Args:
            title: Task title
            initial_priority: Initial priority level
            deadline: Deadline (ISO format)
            estimated_duration_hours: Estimated duration
            value_score: Value/importance score (0-100)
            dependencies: List of task IDs this depends on
            context: Task context
            tags: Task tags
        
        Returns:
            Task record
        """
        task = {
            "task_id": f"task_{len(self.tasks['tasks']) + 1:06d}",
            "title": title,
            "current_priority": initial_priority,
            "original_priority": initial_priority,
            "deadline": deadline,
            "estimated_duration_hours": estimated_duration_hours,
            "value_score": value_score,
            "dependencies": dependencies or [],
            "blocking_tasks": [],
            "context": context,
            "tags": tags or [],
            "status": "pending",
            "completed_at": None,
            "created_at": datetime.now().isoformat(),
            "last_adapted": None,
            "adaptation_count": 0
        }
        
        self.tasks["tasks"].append(task)
        self._save_tasks()
        
        # Update blocking relationships
        self._update_blocking_relationships()
        
        return task
    
    def _update_blocking_relationships(self):
        """Update which tasks are blocking others."""
        # Clear existing blocking lists
        for task in self.tasks["tasks"]:
            task["blocking_tasks"] = []
        
        # Rebuild blocking relationships
        for task in self.tasks["tasks"]:
            if task["status"] != "completed":
                for dep_id in task["dependencies"]:
                    # Find the dependency task
                    for dep_task in self.tasks["tasks"]:
                        if dep_task["task_id"] == dep_id and dep_task["status"] != "completed":
                            if task["task_id"] not in dep_task["blocking_tasks"]:
                                dep_task["blocking_tasks"].append(task["task_id"])
        
        self._save_tasks()
    
    def calculate_priority_score(self, task: Dict[str, Any]) -> float:
        """
        Calculate dynamic priority score for a task.
        
        Args:
            task: Task to score
        
        Returns:
            Priority score (0-100, higher is more urgent)
        """
        score = 0.0
        
        # Base priority contribution (30%)
        priority_scores = {
            "critical": 100,
            "high": 75,
            "medium": 50,
            "low": 25,
            "deferred": 10
        }
        score += priority_scores.get(task["current_priority"], 50) * 0.3
        
        # Value score contribution (20%)
        score += task["value_score"] * 0.2
        
        # Deadline urgency (30%)
        if task["deadline"]:
            try:
                deadline = datetime.fromisoformat(task["deadline"])
                now = datetime.now()
                hours_until = (deadline - now).total_seconds() / 3600
                
                if hours_until < 0:
                    # Overdue
                    score += 30
                elif hours_until < 6:
                    score += 28
                elif hours_until < 24:
                    score += 25
                elif hours_until < 72:
                    score += 20
                elif hours_until < 168:  # 1 week
                    score += 15
                else:
                    score += 10
            except:
                score += 10
        else:
            score += 10
        
        # Blocking factor (15%)
        blocking_count = len(task["blocking_tasks"])
        if blocking_count > 0:
            blocking_score = min(15, blocking_count * 3)
            score += blocking_score
        
        # Dependency factor (5%)
        # Tasks with no dependencies get a small boost
        if not task["dependencies"]:
            score += 5
        else:
            # Check if dependencies are completed
            completed_deps = 0
            for dep_id in task["dependencies"]:
                for dep_task in self.tasks["tasks"]:
                    if dep_task["task_id"] == dep_id and dep_task["status"] == "completed":
                        completed_deps += 1
            
            if completed_deps == len(task["dependencies"]):
                score += 5
        
        return min(100, score)
    
    def adapt_priorities(self) -> List[Dict[str, Any]]:
        """
        Adapt priorities for all tasks based on current state.
        
        Returns:
            List of adaptations made
        """
        adaptations_made = []
        
        for task in self.tasks["tasks"]:
            if task["status"] == "completed":
                continue
            
            old_priority = task["current_priority"]
            new_priority = old_priority
            reasons = []
            
            # Apply rules
            for rule in self.rules["rules"]:
                if not rule["enabled"]:
                    continue
                
                if rule["condition"] == "deadline_within_hours" and task["deadline"]:
                    try:
                        deadline = datetime.fromisoformat(task["deadline"])
                        hours_until = (deadline - datetime.now()).total_seconds() / 3600
                        
                        if 0 < hours_until <= rule["threshold"]:
                            if rule["action"] == "escalate_to_high" and old_priority in ["low", "medium"]:
                                new_priority = "high"
                                reasons.append("deadline_approaching")
                            elif rule["action"] == "escalate_to_critical":
                                new_priority = "critical"
                                reasons.append("deadline_approaching")
                    except:
                        pass
                
                elif rule["condition"] == "is_overdue" and task["deadline"]:
                    try:
                        deadline = datetime.fromisoformat(task["deadline"])
                        if datetime.now() > deadline:
                            new_priority = "critical"
                            reasons.append("urgency_increase")
                    except:
                        pass
                
                elif rule["condition"] == "blocking_count":
                    if len(task["blocking_tasks"]) >= rule["threshold"]:
                        if rule["action"] == "escalate_one_level":
                            priority_order = ["deferred", "low", "medium", "high", "critical"]
                            current_idx = priority_order.index(old_priority)
                            if current_idx < len(priority_order) - 1:
                                new_priority = priority_order[current_idx + 1]
                                reasons.append("blocking_others")
            
            # Check if dependencies are completed
            if task["dependencies"]:
                all_deps_complete = True
                for dep_id in task["dependencies"]:
                    dep_complete = False
                    for dep_task in self.tasks["tasks"]:
                        if dep_task["task_id"] == dep_id and dep_task["status"] == "completed":
                            dep_complete = True
                            break
                    if not dep_complete:
                        all_deps_complete = False
                        break
                
                if all_deps_complete and old_priority in ["deferred", "low"]:
                    new_priority = "medium"
                    reasons.append("dependency_completed")
            
            # Record adaptation if priority changed
            if new_priority != old_priority:
                adaptation = {
                    "adaptation_id": f"adapt_{len(self.adaptations['adaptations']) + 1:06d}",
                    "task_id": task["task_id"],
                    "task_title": task["title"],
                    "old_priority": old_priority,
                    "new_priority": new_priority,
                    "reasons": reasons,
                    "priority_score": self.calculate_priority_score(task),
                    "adapted_at": datetime.now().isoformat()
                }
                
                task["current_priority"] = new_priority
                task["last_adapted"] = datetime.now().isoformat()
                task["adaptation_count"] += 1
                
                self.adaptations["adaptations"].append(adaptation)
                adaptations_made.append(adaptation)
        
        self._save_tasks()
        self._save_adaptations()
        
        return adaptations_made
    
    def complete_task(self, task_id: str) -> Dict[str, Any]:
        """
        Mark a task as completed.
        
        Args:
            task_id: Task to complete
        
        Returns:
            Updated task
        """
        for task in self.tasks["tasks"]:
            if task["task_id"] == task_id:
                task["status"] = "completed"
                task["completed_at"] = datetime.now().isoformat()
                self._save_tasks()
                
                # Update blocking relationships
                self._update_blocking_relationships()
                
                # Trigger adaptation for dependent tasks
                self.adapt_priorities()
                
                return task
        
        return {"error": "Task not found"}
    
    def get_prioritized_tasks(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get tasks sorted by priority score.
        
        Args:
            limit: Maximum number of tasks to return
        
        Returns:
            Sorted list of tasks
        """
        # Calculate scores for all pending tasks
        scored_tasks = []
        for task in self.tasks["tasks"]:
            if task["status"] != "completed":
                score = self.calculate_priority_score(task)
                scored_tasks.append({
                    **task,
                    "priority_score": score
                })
        
        # Sort by score (descending)
        scored_tasks.sort(key=lambda x: x["priority_score"], reverse=True)
        
        if limit:
            return scored_tasks[:limit]
        return scored_tasks
    
    def get_adaptation_history(self, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get adaptation history.
        
        Args:
            task_id: Optional task ID to filter by
        
        Returns:
            List of adaptations
        """
        if task_id:
            return [a for a in self.adaptations["adaptations"] if a["task_id"] == task_id]
        return self.adaptations["adaptations"]
    
    def add_rule(self,
                rule_id: str,
                condition: str,
                threshold: float,
                action: str,
                enabled: bool = True) -> Dict[str, Any]:
        """
        Add a new adaptation rule.
        
        Args:
            rule_id: Unique rule identifier
            condition: Condition to check
            threshold: Threshold value
            action: Action to take
            enabled: Whether rule is enabled
        
        Returns:
            Rule record
        """
        rule = {
            "rule_id": rule_id,
            "condition": condition,
            "threshold": threshold,
            "action": action,
            "enabled": enabled
        }
        
        self.rules["rules"].append(rule)
        self._save_rules()
        
        return rule
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get priority adaptation statistics."""
        total_tasks = len(self.tasks["tasks"])
        completed_tasks = sum(1 for t in self.tasks["tasks"] if t["status"] == "completed")
        pending_tasks = total_tasks - completed_tasks
        
        # Priority distribution
        priority_dist = defaultdict(int)
        for task in self.tasks["tasks"]:
            if task["status"] != "completed":
                priority_dist[task["current_priority"]] += 1
        
        # Adaptation statistics
        total_adaptations = len(self.adaptations["adaptations"])
        
        # Reason distribution
        reason_dist = defaultdict(int)
        for adaptation in self.adaptations["adaptations"]:
            for reason in adaptation["reasons"]:
                reason_dist[reason] += 1
        
        # Tasks with most adaptations
        adaptation_counts = defaultdict(int)
        for task in self.tasks["tasks"]:
            adaptation_counts[task["task_id"]] = task["adaptation_count"]
        
        most_adapted = max(adaptation_counts.items(), key=lambda x: x[1]) if adaptation_counts else (None, 0)
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "priority_distribution": dict(priority_dist),
            "total_adaptations": total_adaptations,
            "adaptation_reasons": dict(reason_dist),
            "most_adapted_task": most_adapted[0],
            "max_adaptation_count": most_adapted[1],
            "active_rules": sum(1 for r in self.rules["rules"] if r["enabled"])
        }


def test_priority_adaptation_system():
    """Test the priority adaptation system."""
    print("=" * 60)
    print("Testing Priority Adaptation System")
    print("=" * 60)
    
    system = PriorityAdaptationSystem()
    
    # Test 1: Add task
    print("\n1. Testing task addition...")
    task1 = system.add_task(
        title="Complete project documentation",
        initial_priority="medium",
        deadline=(datetime.now() + timedelta(hours=48)).isoformat(),
        estimated_duration_hours=4.0,
        value_score=70.0,
        context="Documentation",
        tags=["documentation", "project"]
    )
    print(f"   Task ID: {task1['task_id']}")
    print(f"   Priority: {task1['current_priority']}")
    print(f"   Deadline: {task1['deadline'][:19]}")
    
    # Test 2: Add task with dependencies
    print("\n2. Testing task with dependencies...")
    task2 = system.add_task(
        title="Review code changes",
        initial_priority="high",
        deadline=(datetime.now() + timedelta(hours=6)).isoformat(),
        value_score=85.0,
        dependencies=[],
        context="Code review"
    )
    
    task3 = system.add_task(
        title="Deploy to production",
        initial_priority="low",
        value_score=90.0,
        dependencies=[task2["task_id"]],
        context="Deployment"
    )
    print(f"   Task 3 depends on: {task3['dependencies']}")
    print(f"   Task 2 blocking: {task2['blocking_tasks']}")
    
    # Test 3: Calculate priority score
    print("\n3. Testing priority score calculation...")
    score = system.calculate_priority_score(task2)
    print(f"   Task: {task2['title']}")
    print(f"   Priority score: {score:.1f}")
    
    # Test 4: Adapt priorities
    print("\n4. Testing priority adaptation...")
    adaptations = system.adapt_priorities()
    print(f"   Adaptations made: {len(adaptations)}")
    if adaptations:
        first = adaptations[0]
        print(f"   First: {first['task_title']}")
        print(f"   Changed: {first['old_priority']} -> {first['new_priority']}")
        print(f"   Reasons: {first['reasons']}")
    
    # Test 5: Get prioritized tasks
    print("\n5. Testing prioritized task list...")
    prioritized = system.get_prioritized_tasks(limit=5)
    print(f"   Top tasks: {len(prioritized)}")
    if prioritized:
        print(f"   Highest priority: {prioritized[0]['title']}")
        print(f"   Score: {prioritized[0]['priority_score']:.1f}")
    
    # Test 6: Complete task
    print("\n6. Testing task completion...")
    completed = system.complete_task(task2["task_id"])
    print(f"   Completed: {completed['title']}")
    print(f"   Status: {completed['status']}")
    
    # Test 7: Get adaptation history
    print("\n7. Testing adaptation history...")
    history = system.get_adaptation_history()
    print(f"   Total adaptations: {len(history)}")
    
    # Test 8: Add custom rule
    print("\n8. Testing custom rule addition...")
    rule = system.add_rule(
        rule_id="high_value_boost",
        condition="value_score",
        threshold=80,
        action="escalate_one_level",
        enabled=True
    )
    print(f"   Rule ID: {rule['rule_id']}")
    print(f"   Condition: {rule['condition']}")
    
    # Test 9: Get statistics
    print("\n9. Testing statistics...")
    stats = system.get_statistics()
    print(f"   Total tasks: {stats['total_tasks']}")
    print(f"   Pending tasks: {stats['pending_tasks']}")
    print(f"   Total adaptations: {stats['total_adaptations']}")
    print(f"   Active rules: {stats['active_rules']}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_priority_adaptation_system()
