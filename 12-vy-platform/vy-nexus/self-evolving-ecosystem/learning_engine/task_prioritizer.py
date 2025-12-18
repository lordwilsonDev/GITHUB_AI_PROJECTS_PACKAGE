#!/usr/bin/env python3
"""
Task Prioritization Algorithm
Dynamically prioritizes tasks based on multiple factors and learning
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
from collections import defaultdict
import math

@dataclass
class Task:
    """Represents a task to be prioritized"""
    id: str
    name: str
    description: str
    category: str
    created_at: str
    deadline: Optional[str] = None
    estimated_duration: Optional[float] = None  # in minutes
    importance: int = 5  # 1-10
    urgency: int = 5  # 1-10
    user_priority: Optional[int] = None  # 1-10, explicit user priority
    dependencies: List[str] = field(default_factory=list)
    required_resources: List[str] = field(default_factory=list)
    context: str = "general"
    tags: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed, blocked
    completion_value: float = 5.0  # Expected value of completing this task
    failure_cost: float = 3.0  # Cost of not completing this task
    learning_opportunity: float = 0.0  # How much can be learned from this task
    automation_potential: float = 0.0  # Potential for automation
    
@dataclass
class PriorityScore:
    """Priority score breakdown"""
    task_id: str
    total_score: float
    urgency_score: float
    importance_score: float
    deadline_score: float
    value_score: float
    dependency_score: float
    context_score: float
    learning_score: float
    user_priority_score: float
    calculated_at: str
    reasoning: str

class TaskPrioritizer:
    """Intelligent task prioritization system"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_dir = Path("/Users/lordwilson/vy-nexus/self-evolving-ecosystem/data/prioritization")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.tasks_file = self.base_dir / "tasks.jsonl"
        self.priorities_file = self.base_dir / "priority_scores.jsonl"
        self.completions_file = self.base_dir / "task_completions.jsonl"
        self.weights_file = self.base_dir / "priority_weights.json"
        
        self.tasks: Dict[str, Task] = {}
        self.priority_weights = self._load_weights()
        self.context_preferences: Dict[str, float] = {}  # Context -> preference multiplier
        
        self.load_tasks()
        
        self._initialized = True
    
    def _load_weights(self) -> Dict[str, float]:
        """Load priority calculation weights"""
        default_weights = {
            "urgency": 0.20,
            "importance": 0.20,
            "deadline": 0.15,
            "value": 0.15,
            "dependency": 0.10,
            "context": 0.05,
            "learning": 0.05,
            "user_priority": 0.10
        }
        
        if self.weights_file.exists():
            with open(self.weights_file, 'r') as f:
                return json.load(f)
        else:
            self._save_weights(default_weights)
            return default_weights
    
    def _save_weights(self, weights: Dict[str, float]):
        """Save priority weights"""
        with open(self.weights_file, 'w') as f:
            json.dump(weights, f, indent=2)
    
    def load_tasks(self):
        """Load tasks from storage"""
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        # Handle default factory fields
                        if 'dependencies' not in data:
                            data['dependencies'] = []
                        if 'required_resources' not in data:
                            data['required_resources'] = []
                        if 'tags' not in data:
                            data['tags'] = []
                        task = Task(**data)
                        self.tasks[task.id] = task
    
    def add_task(self, task_id: str, name: str, description: str,
                category: str, **kwargs) -> Task:
        """Add a new task"""
        if task_id in self.tasks:
            return self.update_task(task_id, **kwargs)
        
        task = Task(
            id=task_id,
            name=name,
            description=description,
            category=category,
            created_at=datetime.now().isoformat(),
            **kwargs
        )
        
        self.tasks[task_id] = task
        self._save_task(task)
        
        return task
    
    def update_task(self, task_id: str, **updates) -> Optional[Task]:
        """Update task information"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        for key, value in updates.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)
        
        self._save_task(task)
        return task
    
    def calculate_priority(self, task_id: str) -> PriorityScore:
        """Calculate priority score for a task"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        
        # Calculate individual scores (0-10 scale)
        urgency_score = float(task.urgency)
        importance_score = float(task.importance)
        deadline_score = self._calculate_deadline_score(task)
        value_score = task.completion_value
        dependency_score = self._calculate_dependency_score(task)
        context_score = self._calculate_context_score(task)
        learning_score = task.learning_opportunity
        user_priority_score = float(task.user_priority) if task.user_priority else 5.0
        
        # Apply weights and calculate total
        total_score = (
            urgency_score * self.priority_weights["urgency"] +
            importance_score * self.priority_weights["importance"] +
            deadline_score * self.priority_weights["deadline"] +
            value_score * self.priority_weights["value"] +
            dependency_score * self.priority_weights["dependency"] +
            context_score * self.priority_weights["context"] +
            learning_score * self.priority_weights["learning"] +
            user_priority_score * self.priority_weights["user_priority"]
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            task, urgency_score, importance_score, deadline_score,
            value_score, dependency_score, context_score, learning_score,
            user_priority_score
        )
        
        priority_score = PriorityScore(
            task_id=task_id,
            total_score=round(total_score, 2),
            urgency_score=urgency_score,
            importance_score=importance_score,
            deadline_score=deadline_score,
            value_score=value_score,
            dependency_score=dependency_score,
            context_score=context_score,
            learning_score=learning_score,
            user_priority_score=user_priority_score,
            calculated_at=datetime.now().isoformat(),
            reasoning=reasoning
        )
        
        # Save priority score
        with open(self.priorities_file, 'a') as f:
            f.write(json.dumps(asdict(priority_score)) + '\n')
        
        return priority_score
    
    def _calculate_deadline_score(self, task: Task) -> float:
        """Calculate urgency based on deadline"""
        if not task.deadline:
            return 5.0  # Neutral score
        
        try:
            deadline = datetime.fromisoformat(task.deadline)
            now = datetime.now()
            time_remaining = (deadline - now).total_seconds() / 3600  # hours
            
            if time_remaining < 0:
                return 10.0  # Overdue - highest priority
            elif time_remaining < 1:
                return 9.5  # Less than 1 hour
            elif time_remaining < 4:
                return 9.0  # Less than 4 hours
            elif time_remaining < 24:
                return 8.0  # Less than 1 day
            elif time_remaining < 72:
                return 6.5  # Less than 3 days
            elif time_remaining < 168:
                return 5.0  # Less than 1 week
            else:
                return 3.0  # More than 1 week
        except:
            return 5.0
    
    def _calculate_dependency_score(self, task: Task) -> float:
        """Calculate score based on dependencies"""
        if not task.dependencies:
            return 5.0  # No dependencies - neutral
        
        # Check if dependencies are completed
        blocked_count = 0
        for dep_id in task.dependencies:
            if dep_id in self.tasks:
                dep_task = self.tasks[dep_id]
                if dep_task.status != "completed":
                    blocked_count += 1
        
        if blocked_count > 0:
            return 2.0  # Blocked - lower priority
        else:
            return 7.0  # Dependencies met - higher priority
    
    def _calculate_context_score(self, task: Task) -> float:
        """Calculate score based on current context"""
        # Use learned context preferences
        if task.context in self.context_preferences:
            return self.context_preferences[task.context]
        return 5.0  # Neutral
    
    def _generate_reasoning(self, task: Task, urgency: float, importance: float,
                           deadline: float, value: float, dependency: float,
                           context: float, learning: float, user_priority: float) -> str:
        """Generate human-readable reasoning for priority"""
        reasons = []
        
        if urgency >= 8:
            reasons.append("High urgency")
        if importance >= 8:
            reasons.append("High importance")
        if deadline >= 8:
            reasons.append("Approaching deadline")
        if value >= 8:
            reasons.append("High completion value")
        if dependency <= 3:
            reasons.append("Blocked by dependencies")
        if learning >= 7:
            reasons.append("Significant learning opportunity")
        if user_priority and user_priority >= 8:
            reasons.append("User-specified high priority")
        
        if not reasons:
            reasons.append("Standard priority task")
        
        return "; ".join(reasons)
    
    def get_prioritized_tasks(self, limit: int = None,
                            status: str = "pending",
                            category: str = None) -> List[Tuple[Task, PriorityScore]]:
        """Get tasks sorted by priority"""
        # Filter tasks
        filtered_tasks = [t for t in self.tasks.values() if t.status == status]
        
        if category:
            filtered_tasks = [t for t in filtered_tasks if t.category == category]
        
        # Calculate priorities
        task_priorities = []
        for task in filtered_tasks:
            priority = self.calculate_priority(task.id)
            task_priorities.append((task, priority))
        
        # Sort by priority score (descending)
        task_priorities.sort(key=lambda x: x[1].total_score, reverse=True)
        
        if limit:
            return task_priorities[:limit]
        return task_priorities
    
    def get_next_task(self, context: str = None) -> Optional[Tuple[Task, PriorityScore]]:
        """Get the next highest priority task"""
        tasks = self.get_prioritized_tasks(limit=1)
        
        if context:
            # Filter by context
            context_tasks = [(t, p) for t, p in self.get_prioritized_tasks()
                           if t.context == context]
            if context_tasks:
                return context_tasks[0]
        
        return tasks[0] if tasks else None
    
    def complete_task(self, task_id: str, actual_duration: float = None,
                     actual_value: float = None, notes: str = ""):
        """Mark task as completed and record metrics"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = "completed"
        
        # Record completion
        completion = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "task_name": task.name,
            "category": task.category,
            "estimated_duration": task.estimated_duration,
            "actual_duration": actual_duration,
            "expected_value": task.completion_value,
            "actual_value": actual_value,
            "notes": notes
        }
        
        with open(self.completions_file, 'a') as f:
            f.write(json.dumps(completion) + '\n')
        
        self._save_task(task)
        
        # Learn from completion
        self._learn_from_completion(task, actual_duration, actual_value)
        
        return True
    
    def _learn_from_completion(self, task: Task, actual_duration: float = None,
                              actual_value: float = None):
        """Learn from task completion to improve future prioritization"""
        # Update context preferences
        if task.context not in self.context_preferences:
            self.context_preferences[task.context] = 5.0
        
        # If task was valuable, increase context preference
        if actual_value and actual_value > task.completion_value:
            self.context_preferences[task.context] = min(10.0,
                self.context_preferences[task.context] + 0.5)
        
        # Adjust weights based on outcomes (simplified learning)
        # This could be expanded with more sophisticated ML
    
    def adjust_weights(self, weight_adjustments: Dict[str, float]):
        """Manually adjust priority weights"""
        for key, value in weight_adjustments.items():
            if key in self.priority_weights:
                self.priority_weights[key] = max(0.0, min(1.0, value))
        
        # Normalize weights to sum to 1.0
        total = sum(self.priority_weights.values())
        if total > 0:
            for key in self.priority_weights:
                self.priority_weights[key] /= total
        
        self._save_weights(self.priority_weights)
    
    def get_prioritization_stats(self) -> Dict:
        """Get statistics about task prioritization"""
        total_tasks = len(self.tasks)
        by_status = defaultdict(int)
        by_category = defaultdict(int)
        
        for task in self.tasks.values():
            by_status[task.status] += 1
            by_category[task.category] += 1
        
        # Calculate average priority scores
        pending_tasks = [t for t in self.tasks.values() if t.status == "pending"]
        avg_urgency = sum(t.urgency for t in pending_tasks) / len(pending_tasks) if pending_tasks else 0
        avg_importance = sum(t.importance for t in pending_tasks) / len(pending_tasks) if pending_tasks else 0
        
        return {
            "total_tasks": total_tasks,
            "by_status": dict(by_status),
            "by_category": dict(by_category),
            "pending_count": by_status.get("pending", 0),
            "completed_count": by_status.get("completed", 0),
            "avg_urgency": round(avg_urgency, 2),
            "avg_importance": round(avg_importance, 2),
            "current_weights": self.priority_weights
        }
    
    def _save_task(self, task: Task):
        """Save task to storage"""
        with open(self.tasks_file, 'a') as f:
            f.write(json.dumps(asdict(task)) + '\n')
    
    def export_prioritization_report(self) -> Dict:
        """Export complete prioritization report"""
        prioritized = self.get_prioritized_tasks(limit=20)
        
        return {
            "generated_at": datetime.now().isoformat(),
            "stats": self.get_prioritization_stats(),
            "top_priority_tasks": [
                {
                    "task": asdict(task),
                    "priority": asdict(priority)
                }
                for task, priority in prioritized
            ],
            "weights": self.priority_weights,
            "context_preferences": self.context_preferences
        }

def get_prioritizer() -> TaskPrioritizer:
    """Get singleton instance of task prioritizer"""
    return TaskPrioritizer()

if __name__ == "__main__":
    # Example usage
    prioritizer = get_prioritizer()
    
    # Add tasks
    task1 = prioritizer.add_task(
        task_id="task_001",
        name="Fix critical bug",
        description="Fix production bug affecting users",
        category="development",
        urgency=9,
        importance=10,
        deadline=(datetime.now() + timedelta(hours=2)).isoformat(),
        completion_value=9.0
    )
    
    task2 = prioritizer.add_task(
        task_id="task_002",
        name="Write documentation",
        description="Document new features",
        category="documentation",
        urgency=4,
        importance=6,
        completion_value=5.0,
        learning_opportunity=3.0
    )
    
    # Get prioritized tasks
    prioritized = prioritizer.get_prioritized_tasks(limit=5)
    for task, priority in prioritized:
        print(f"Task: {task.name}")
        print(f"Priority Score: {priority.total_score}")
        print(f"Reasoning: {priority.reasoning}")
        print()
    
    # Get stats
    stats = prioritizer.get_prioritization_stats()
    print(f"Stats: {stats}")
