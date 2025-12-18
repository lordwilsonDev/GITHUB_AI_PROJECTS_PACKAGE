#!/usr/bin/env python3
"""
Dynamic Task Prioritization System

Adaptively prioritizes tasks based on multiple factors including:
- Urgency and deadlines
- User context and preferences
- Task dependencies
- Historical completion patterns
- Resource availability
- Impact and value

Part of the VY-NEXUS Self-Evolving AI Ecosystem - Phase 4.2
"""

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import hashlib


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = "critical"  # Must do now
    HIGH = "high"  # Should do soon
    MEDIUM = "medium"  # Can do later
    LOW = "low"  # Nice to have
    DEFERRED = "deferred"  # Postponed


class TaskStatus(Enum):
    """Task status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class UrgencyLevel(Enum):
    """Urgency classification"""
    IMMEDIATE = "immediate"  # Within hours
    URGENT = "urgent"  # Within 1-2 days
    SOON = "soon"  # Within a week
    NORMAL = "normal"  # No specific deadline
    FLEXIBLE = "flexible"  # Can wait


@dataclass
class Task:
    """Represents a task with prioritization metadata"""
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    urgency: UrgencyLevel
    
    # Scoring factors
    impact_score: float  # 0-100: Expected impact/value
    effort_estimate: float  # Hours estimated
    deadline: Optional[datetime] = None
    
    # Context
    category: str = "general"
    tags: List[str] = None
    dependencies: List[str] = None  # Task IDs this depends on
    blocked_by: List[str] = None  # Task IDs blocking this
    
    # Metadata
    created_at: datetime = None
    updated_at: datetime = None
    completed_at: Optional[datetime] = None
    
    # Prioritization
    priority_score: float = 0.0  # Calculated priority score
    context_boost: float = 0.0  # Context-based adjustment
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []
        if self.blocked_by is None:
            self.blocked_by = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        data['urgency'] = self.urgency.value
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        data['deadline'] = self.deadline.isoformat() if self.deadline else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        """Create from dictionary"""
        data = data.copy()
        data['status'] = TaskStatus(data['status'])
        data['priority'] = TaskPriority(data['priority'])
        data['urgency'] = UrgencyLevel(data['urgency'])
        
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if data.get('completed_at'):
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        if data.get('deadline'):
            data['deadline'] = datetime.fromisoformat(data['deadline'])
        
        return cls(**data)


@dataclass
class PrioritizationContext:
    """Context for prioritization decisions"""
    current_time: datetime
    user_focus_area: Optional[str] = None  # Current focus category
    available_time: Optional[float] = None  # Hours available
    energy_level: Optional[str] = None  # high, medium, low
    interruption_tolerance: Optional[str] = None  # high, medium, low
    preferred_categories: List[str] = None
    
    def __post_init__(self):
        if self.preferred_categories is None:
            self.preferred_categories = []


class DynamicTaskPrioritizer:
    """
    Dynamically prioritizes tasks based on multiple factors and context.
    
    Prioritization algorithm considers:
    1. Urgency (deadline proximity)
    2. Impact (expected value)
    3. Effort (time required)
    4. Dependencies (blocking/blocked)
    5. Context (user focus, energy, time available)
    6. Historical patterns (completion rates, preferences)
    """
    
    def __init__(self, data_dir: str = None):
        """Initialize the task prioritizer"""
        if data_dir is None:
            data_dir = os.path.expanduser("~/vy_data/task_prioritization")
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.tasks_file = self.data_dir / "tasks.jsonl"
        self.history_file = self.data_dir / "prioritization_history.jsonl"
        self.patterns_file = self.data_dir / "completion_patterns.json"
        
        self.tasks: Dict[str, Task] = {}
        self.completion_patterns: Dict[str, Dict] = {}
        
        self._load_tasks()
        self._load_patterns()
    
    def _load_tasks(self):
        """Load tasks from file"""
        if not self.tasks_file.exists():
            return
        
        with open(self.tasks_file, 'r') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    task = Task.from_dict(data)
                    self.tasks[task.id] = task
    
    def _save_task(self, task: Task):
        """Append task to file"""
        with open(self.tasks_file, 'a') as f:
            f.write(json.dumps(task.to_dict()) + '\n')
    
    def _load_patterns(self):
        """Load completion patterns"""
        if not self.patterns_file.exists():
            return
        
        with open(self.patterns_file, 'r') as f:
            self.completion_patterns = json.load(f)
    
    def _save_patterns(self):
        """Save completion patterns"""
        with open(self.patterns_file, 'w') as f:
            json.dump(self.completion_patterns, f, indent=2)
    
    def add_task(
        self,
        title: str,
        description: str,
        impact_score: float,
        effort_estimate: float,
        deadline: Optional[datetime] = None,
        category: str = "general",
        tags: List[str] = None,
        dependencies: List[str] = None
    ) -> Task:
        """
        Add a new task to the system.
        
        Args:
            title: Task title
            description: Task description
            impact_score: Expected impact (0-100)
            effort_estimate: Estimated hours
            deadline: Optional deadline
            category: Task category
            tags: Optional tags
            dependencies: Task IDs this depends on
        
        Returns:
            Created Task object
        """
        # Generate unique ID
        task_id = hashlib.md5(
            f"{title}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
        
        # Determine initial urgency based on deadline
        urgency = self._calculate_urgency(deadline)
        
        # Determine initial priority
        priority = self._determine_initial_priority(impact_score, urgency)
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            priority=priority,
            urgency=urgency,
            impact_score=impact_score,
            effort_estimate=effort_estimate,
            deadline=deadline,
            category=category,
            tags=tags or [],
            dependencies=dependencies or []
        )
        
        self.tasks[task_id] = task
        self._save_task(task)
        
        return task
    
    def _calculate_urgency(self, deadline: Optional[datetime]) -> UrgencyLevel:
        """Calculate urgency based on deadline"""
        if deadline is None:
            return UrgencyLevel.NORMAL
        
        time_until = deadline - datetime.now()
        hours_until = time_until.total_seconds() / 3600
        
        if hours_until < 6:
            return UrgencyLevel.IMMEDIATE
        elif hours_until < 48:
            return UrgencyLevel.URGENT
        elif hours_until < 168:  # 1 week
            return UrgencyLevel.SOON
        else:
            return UrgencyLevel.FLEXIBLE
    
    def _determine_initial_priority(self, impact: float, urgency: UrgencyLevel) -> TaskPriority:
        """Determine initial priority from impact and urgency"""
        if urgency == UrgencyLevel.IMMEDIATE or impact >= 90:
            return TaskPriority.CRITICAL
        elif urgency == UrgencyLevel.URGENT or impact >= 70:
            return TaskPriority.HIGH
        elif urgency == UrgencyLevel.SOON or impact >= 40:
            return TaskPriority.MEDIUM
        else:
            return TaskPriority.LOW
    
    def calculate_priority_score(
        self,
        task: Task,
        context: Optional[PrioritizationContext] = None
    ) -> float:
        """
        Calculate comprehensive priority score (0-100).
        
        Scoring factors:
        - Urgency: 0-30 points
        - Impact: 0-30 points
        - Effort efficiency: 0-15 points (impact/effort ratio)
        - Dependencies: 0-10 points (ready to start bonus)
        - Context match: 0-15 points (matches user focus/preferences)
        
        Args:
            task: Task to score
            context: Optional prioritization context
        
        Returns:
            Priority score (0-100)
        """
        if context is None:
            context = PrioritizationContext(current_time=datetime.now())
        
        score = 0.0
        
        # 1. Urgency score (0-30)
        urgency_scores = {
            UrgencyLevel.IMMEDIATE: 30,
            UrgencyLevel.URGENT: 25,
            UrgencyLevel.SOON: 15,
            UrgencyLevel.NORMAL: 5,
            UrgencyLevel.FLEXIBLE: 0
        }
        score += urgency_scores[task.urgency]
        
        # 2. Impact score (0-30)
        score += (task.impact_score / 100) * 30
        
        # 3. Effort efficiency (0-15)
        # Higher impact per hour = higher score
        if task.effort_estimate > 0:
            efficiency = task.impact_score / task.effort_estimate
            # Normalize to 0-15 range (assume max efficiency of 50)
            score += min(15, (efficiency / 50) * 15)
        
        # 4. Dependencies (0-10)
        if not task.dependencies:  # No dependencies = ready to start
            score += 10
        elif all(self.tasks.get(dep_id, Task(id="", title="", description="", status=TaskStatus.COMPLETED, priority=TaskPriority.LOW, urgency=UrgencyLevel.NORMAL, impact_score=0, effort_estimate=0)).status == TaskStatus.COMPLETED for dep_id in task.dependencies):
            score += 10  # All dependencies complete
        else:
            score += 3  # Has incomplete dependencies
        
        # 5. Context match (0-15)
        context_score = 0
        
        # Focus area match
        if context.user_focus_area and task.category == context.user_focus_area:
            context_score += 5
        
        # Preferred category match
        if task.category in context.preferred_categories:
            context_score += 3
        
        # Time availability match
        if context.available_time:
            if task.effort_estimate <= context.available_time:
                context_score += 4  # Task fits in available time
            elif task.effort_estimate <= context.available_time * 1.5:
                context_score += 2  # Close fit
        
        # Energy level match
        if context.energy_level:
            if context.energy_level == "high" and task.impact_score >= 70:
                context_score += 3  # High energy for high impact tasks
            elif context.energy_level == "low" and task.effort_estimate <= 1:
                context_score += 3  # Low energy for quick tasks
        
        score += min(15, context_score)
        
        # Store calculated score
        task.priority_score = score
        task.context_boost = min(15, context_score)
        
        return score
    
    def prioritize_tasks(
        self,
        context: Optional[PrioritizationContext] = None,
        status_filter: Optional[TaskStatus] = None,
        limit: Optional[int] = None
    ) -> List[Task]:
        """
        Get prioritized list of tasks.
        
        Args:
            context: Prioritization context
            status_filter: Filter by status (default: PENDING)
            limit: Maximum number of tasks to return
        
        Returns:
            List of tasks sorted by priority score (highest first)
        """
        if status_filter is None:
            status_filter = TaskStatus.PENDING
        
        # Filter tasks
        filtered_tasks = [
            task for task in self.tasks.values()
            if task.status == status_filter
        ]
        
        # Calculate scores
        for task in filtered_tasks:
            self.calculate_priority_score(task, context)
        
        # Sort by priority score (descending)
        sorted_tasks = sorted(
            filtered_tasks,
            key=lambda t: t.priority_score,
            reverse=True
        )
        
        # Apply limit
        if limit:
            sorted_tasks = sorted_tasks[:limit]
        
        # Log prioritization
        self._log_prioritization(sorted_tasks, context)
        
        return sorted_tasks
    
    def _log_prioritization(self, tasks: List[Task], context: Optional[PrioritizationContext]):
        """Log prioritization decision for learning"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "context": {
                "focus_area": context.user_focus_area if context else None,
                "available_time": context.available_time if context else None,
                "energy_level": context.energy_level if context else None
            },
            "prioritized_tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "priority_score": task.priority_score,
                    "category": task.category
                }
                for task in tasks[:10]  # Top 10
            ]
        }
        
        with open(self.history_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        completion_time: Optional[float] = None
    ):
        """
        Update task status and learn from completion.
        
        Args:
            task_id: Task ID
            status: New status
            completion_time: Actual time taken (for completed tasks)
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task.status = status
        task.updated_at = datetime.now()
        
        if status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now()
            
            # Learn from completion
            if completion_time:
                self._learn_from_completion(task, completion_time)
        
        self._save_task(task)
    
    def _learn_from_completion(self, task: Task, actual_time: float):
        """Learn from task completion to improve future estimates"""
        category = task.category
        
        if category not in self.completion_patterns:
            self.completion_patterns[category] = {
                "total_tasks": 0,
                "avg_estimate_accuracy": 1.0,
                "avg_completion_time": 0,
                "preferred_times": {}
            }
        
        pattern = self.completion_patterns[category]
        pattern["total_tasks"] += 1
        
        # Update estimate accuracy
        if task.effort_estimate > 0:
            accuracy = actual_time / task.effort_estimate
            current_avg = pattern["avg_estimate_accuracy"]
            pattern["avg_estimate_accuracy"] = (
                (current_avg * (pattern["total_tasks"] - 1) + accuracy) /
                pattern["total_tasks"]
            )
        
        # Update average completion time
        current_avg_time = pattern["avg_completion_time"]
        pattern["avg_completion_time"] = (
            (current_avg_time * (pattern["total_tasks"] - 1) + actual_time) /
            pattern["total_tasks"]
        )
        
        # Track preferred completion times (hour of day)
        if task.completed_at:
            hour = task.completed_at.hour
            hour_key = str(hour)
            pattern["preferred_times"][hour_key] = pattern["preferred_times"].get(hour_key, 0) + 1
        
        self._save_patterns()
    
    def get_next_task(
        self,
        context: Optional[PrioritizationContext] = None
    ) -> Optional[Task]:
        """
        Get the single highest priority task.
        
        Args:
            context: Prioritization context
        
        Returns:
            Highest priority task or None
        """
        tasks = self.prioritize_tasks(context=context, limit=1)
        return tasks[0] if tasks else None
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_tasks_by_category(self, category: str) -> List[Task]:
        """Get all tasks in a category"""
        return [task for task in self.tasks.values() if task.category == category]
    
    def get_blocked_tasks(self) -> List[Task]:
        """Get tasks that are blocked by dependencies"""
        blocked = []
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING and task.dependencies:
                if any(
                    self.tasks.get(dep_id, Task(id="", title="", description="", status=TaskStatus.COMPLETED, priority=TaskPriority.LOW, urgency=UrgencyLevel.NORMAL, impact_score=0, effort_estimate=0)).status != TaskStatus.COMPLETED
                    for dep_id in task.dependencies
                ):
                    blocked.append(task)
        return blocked
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks that are ready to start (no blocking dependencies)"""
        ready = []
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                if not task.dependencies or all(
                    self.tasks.get(dep_id, Task(id="", title="", description="", status=TaskStatus.COMPLETED, priority=TaskPriority.LOW, urgency=UrgencyLevel.NORMAL, impact_score=0, effort_estimate=0)).status == TaskStatus.COMPLETED
                    for dep_id in task.dependencies
                ):
                    ready.append(task)
        return ready
    
    def get_statistics(self) -> Dict:
        """Get prioritization statistics"""
        total_tasks = len(self.tasks)
        
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = sum(
                1 for task in self.tasks.values() if task.status == status
            )
        
        priority_counts = {}
        for priority in TaskPriority:
            priority_counts[priority.value] = sum(
                1 for task in self.tasks.values() if task.priority == priority
            )
        
        category_counts = {}
        for task in self.tasks.values():
            category_counts[task.category] = category_counts.get(task.category, 0) + 1
        
        return {
            "total_tasks": total_tasks,
            "by_status": status_counts,
            "by_priority": priority_counts,
            "by_category": category_counts,
            "blocked_tasks": len(self.get_blocked_tasks()),
            "ready_tasks": len(self.get_ready_tasks()),
            "completion_patterns": self.completion_patterns
        }
