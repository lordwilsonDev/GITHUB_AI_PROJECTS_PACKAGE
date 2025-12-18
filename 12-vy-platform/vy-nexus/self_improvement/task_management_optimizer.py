#!/usr/bin/env python3
"""
Task Management Optimizer - Vy-Nexus Self-Improvement Cycle

Intelligent task management with dynamic prioritization, resource allocation,
schedule optimization, and adaptive learning.

Features:
- Dynamic task prioritization
- Optimal resource allocation
- Schedule optimization
- Adaptive learning from task history
- Constraint handling
- Deadline management

Author: Vy-Nexus Self-Evolving AI
Created: December 15, 2025
Phase: 6.2 - Adaptive Algorithms
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import heapq
from collections import defaultdict, deque


class TaskStatus(Enum):
    """Task status."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ResourceType(Enum):
    """Types of resources."""
    HUMAN = "human"
    COMPUTE = "compute"
    MEMORY = "memory"
    NETWORK = "network"
    CUSTOM = "custom"


@dataclass
class Task:
    """A task to be managed."""
    task_id: str
    name: str
    description: str
    priority: str = TaskPriority.MEDIUM.value
    status: str = TaskStatus.PENDING.value
    estimated_duration_minutes: int = 30
    deadline: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    required_resources: Dict[str, int] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Resource:
    """A resource that can be allocated to tasks."""
    resource_id: str
    name: str
    resource_type: str
    capacity: int
    available: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def allocate(self, amount: int) -> bool:
        """Allocate resource."""
        if self.available >= amount:
            self.available -= amount
            return True
        return False
    
    def release(self, amount: int):
        """Release resource."""
        self.available = min(self.capacity, self.available + amount)
    
    def utilization(self) -> float:
        """Get utilization percentage."""
        return (self.capacity - self.available) / self.capacity if self.capacity > 0 else 0.0


@dataclass
class ScheduledTask:
    """A task with schedule information."""
    task: Task
    start_time: str
    end_time: str
    allocated_resources: Dict[str, int]
    priority_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'task': self.task.to_dict(),
            'start_time': self.start_time,
            'end_time': self.end_time,
            'allocated_resources': self.allocated_resources,
            'priority_score': self.priority_score
        }


class TaskPriorityOptimizer:
    """Optimizes task priorities dynamically."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.weights = self.config.get('priority_weights', {})
        self.task_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration."""
        return {
            'priority_weights': {
                'urgency': 0.4,
                'importance': 0.3,
                'dependencies': 0.2,
                'deadline_proximity': 0.1
            }
        }
    
    def calculate_priority_score(self, task: Task, current_time: Optional[datetime] = None) -> float:
        """
        Calculate priority score for a task.
        Higher score = higher priority.
        """
        current_time = current_time or datetime.now()
        
        # Base priority from task priority level
        priority_map = {
            TaskPriority.CRITICAL.value: 10,
            TaskPriority.HIGH.value: 7,
            TaskPriority.MEDIUM.value: 5,
            TaskPriority.LOW.value: 3
        }
        base_score = priority_map.get(task.priority, 5)
        
        # Urgency score (0-10)
        urgency_score = self._calculate_urgency(task, current_time)
        
        # Importance score (0-10)
        importance_score = base_score
        
        # Dependency score (0-10)
        dependency_score = self._calculate_dependency_score(task)
        
        # Deadline proximity score (0-10)
        deadline_score = self._calculate_deadline_score(task, current_time)
        
        # Weighted combination
        total_score = (
            self.weights.get('urgency', 0.4) * urgency_score +
            self.weights.get('importance', 0.3) * importance_score +
            self.weights.get('dependencies', 0.2) * dependency_score +
            self.weights.get('deadline_proximity', 0.1) * deadline_score
        )
        
        return total_score
    
    def _calculate_urgency(self, task: Task, current_time: datetime) -> float:
        """Calculate urgency score."""
        # If task has been waiting long, increase urgency
        created = datetime.fromisoformat(task.created_at)
        wait_time = (current_time - created).total_seconds() / 3600  # hours
        
        # Urgency increases with wait time
        urgency = min(10, wait_time / 24 * 5)  # Max urgency after ~2 days
        
        return urgency
    
    def _calculate_dependency_score(self, task: Task) -> float:
        """Calculate score based on dependencies."""
        # Tasks with no dependencies can start immediately
        if not task.dependencies:
            return 10
        
        # Tasks with many dependencies have lower score
        num_deps = len(task.dependencies)
        score = max(0, 10 - num_deps * 2)
        
        return score
    
    def _calculate_deadline_score(self, task: Task, current_time: datetime) -> float:
        """Calculate score based on deadline proximity."""
        if not task.deadline:
            return 5  # Neutral score
        
        deadline = datetime.fromisoformat(task.deadline)
        time_until_deadline = (deadline - current_time).total_seconds() / 3600  # hours
        
        if time_until_deadline < 0:
            return 10  # Overdue - highest priority
        elif time_until_deadline < 24:
            return 9  # Due within 24 hours
        elif time_until_deadline < 72:
            return 7  # Due within 3 days
        elif time_until_deadline < 168:
            return 5  # Due within a week
        else:
            return 3  # Due later
    
    def prioritize_tasks(self, tasks: List[Task]) -> List[Tuple[Task, float]]:
        """
        Prioritize a list of tasks.
        Returns list of (task, priority_score) tuples, sorted by priority.
        """
        scored_tasks = []
        for task in tasks:
            if task.status in [TaskStatus.PENDING.value, TaskStatus.SCHEDULED.value]:
                score = self.calculate_priority_score(task)
                scored_tasks.append((task, score))
        
        # Sort by score (descending)
        scored_tasks.sort(key=lambda x: x[1], reverse=True)
        
        return scored_tasks


class ResourceAllocator:
    """Allocates resources to tasks optimally."""
    
    def __init__(self, resources: List[Resource]):
        self.resources = {r.resource_id: r for r in resources}
        self.allocations: Dict[str, Dict[str, int]] = {}  # task_id -> {resource_id: amount}
    
    def can_allocate(self, task: Task) -> bool:
        """Check if resources can be allocated for task."""
        for resource_type, amount in task.required_resources.items():
            available = sum(
                r.available for r in self.resources.values()
                if r.resource_type == resource_type
            )
            if available < amount:
                return False
        return True
    
    def allocate_resources(self, task: Task) -> Dict[str, int]:
        """
        Allocate resources for a task.
        Returns dict of resource_id -> amount allocated.
        """
        allocation = {}
        
        for resource_type, amount_needed in task.required_resources.items():
            # Find resources of this type
            available_resources = [
                r for r in self.resources.values()
                if r.resource_type == resource_type and r.available > 0
            ]
            
            # Sort by utilization (prefer less utilized resources for load balancing)
            available_resources.sort(key=lambda r: r.utilization())
            
            remaining = amount_needed
            for resource in available_resources:
                if remaining <= 0:
                    break
                
                allocate_amount = min(remaining, resource.available)
                if resource.allocate(allocate_amount):
                    allocation[resource.resource_id] = allocate_amount
                    remaining -= allocate_amount
            
            if remaining > 0:
                # Couldn't allocate enough - rollback
                self.release_resources(task.task_id, allocation)
                return {}
        
        # Store allocation
        self.allocations[task.task_id] = allocation
        return allocation
    
    def release_resources(self, task_id: str, allocation: Optional[Dict[str, int]] = None):
        """Release resources allocated to a task."""
        if allocation is None:
            allocation = self.allocations.get(task_id, {})
        
        for resource_id, amount in allocation.items():
            if resource_id in self.resources:
                self.resources[resource_id].release(amount)
        
        if task_id in self.allocations:
            del self.allocations[task_id]
    
    def get_resource_utilization(self) -> Dict[str, float]:
        """Get utilization for all resources."""
        return {
            resource_id: resource.utilization()
            for resource_id, resource in self.resources.items()
        }


class ScheduleOptimizer:
    """Optimizes task scheduling."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.schedule: List[ScheduledTask] = []
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration."""
        return {
            'max_parallel_tasks': 5,
            'working_hours_start': 9,
            'working_hours_end': 17,
            'buffer_time_percentage': 0.15
        }
    
    def generate_schedule(
        self,
        tasks: List[Tuple[Task, float]],  # (task, priority_score)
        resource_allocator: ResourceAllocator,
        start_time: Optional[datetime] = None
    ) -> List[ScheduledTask]:
        """
        Generate optimal schedule for tasks.
        Uses greedy algorithm with priority ordering.
        """
        start_time = start_time or datetime.now()
        schedule = []
        current_time = start_time
        
        # Track tasks in progress
        in_progress: List[Tuple[datetime, ScheduledTask]] = []  # (end_time, scheduled_task)
        
        for task, priority_score in tasks:
            # Check dependencies
            if not self._dependencies_satisfied(task, schedule):
                continue
            
            # Wait for resources if needed
            while not resource_allocator.can_allocate(task):
                if not in_progress:
                    break  # No tasks to complete, can't proceed
                
                # Wait for next task to complete
                next_end_time, completed_task = heapq.heappop(in_progress)
                current_time = next_end_time
                resource_allocator.release_resources(completed_task.task.task_id)
            
            # Allocate resources
            allocation = resource_allocator.allocate_resources(task)
            if not allocation and task.required_resources:
                continue  # Skip if can't allocate
            
            # Calculate duration with buffer
            duration_minutes = task.estimated_duration_minutes
            buffer = duration_minutes * self.config.get('buffer_time_percentage', 0.15)
            total_duration = duration_minutes + buffer
            
            # Schedule task
            end_time = current_time + timedelta(minutes=total_duration)
            
            scheduled_task = ScheduledTask(
                task=task,
                start_time=current_time.isoformat(),
                end_time=end_time.isoformat(),
                allocated_resources=allocation,
                priority_score=priority_score
            )
            
            schedule.append(scheduled_task)
            heapq.heappush(in_progress, (end_time, scheduled_task))
            
            # Limit parallel tasks
            max_parallel = self.config.get('max_parallel_tasks', 5)
            while len(in_progress) >= max_parallel:
                next_end_time, completed_task = heapq.heappop(in_progress)
                current_time = max(current_time, next_end_time)
                resource_allocator.release_resources(completed_task.task.task_id)
        
        self.schedule = schedule
        return schedule
    
    def _dependencies_satisfied(self, task: Task, schedule: List[ScheduledTask]) -> bool:
        """Check if task dependencies are satisfied."""
        if not task.dependencies:
            return True
        
        scheduled_task_ids = {st.task.task_id for st in schedule}
        return all(dep_id in scheduled_task_ids for dep_id in task.dependencies)
    
    def get_completion_time(self) -> Optional[datetime]:
        """Get estimated completion time for all tasks."""
        if not self.schedule:
            return None
        
        latest_end = max(
            datetime.fromisoformat(st.end_time)
            for st in self.schedule
        )
        return latest_end


class AdaptiveLearner:
    """Learns from task history to improve optimization."""
    
    def __init__(self, learning_rate: float = 0.1):
        self.learning_rate = learning_rate
        self.task_history: List[Dict[str, Any]] = []
        self.duration_estimates: Dict[str, deque] = defaultdict(lambda: deque(maxlen=20))
        self.priority_adjustments: Dict[str, float] = defaultdict(float)
    
    def record_task_completion(
        self,
        task: Task,
        actual_duration_minutes: int,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record task completion for learning."""
        record = {
            'task_id': task.task_id,
            'task_name': task.name,
            'estimated_duration': task.estimated_duration_minutes,
            'actual_duration': actual_duration_minutes,
            'success': success,
            'priority': task.priority,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.task_history.append(record)
        
        # Update duration estimates
        task_type = task.metadata.get('type', task.name)
        self.duration_estimates[task_type].append(actual_duration_minutes)
    
    def get_improved_estimate(self, task: Task) -> int:
        """Get improved duration estimate based on history."""
        task_type = task.metadata.get('type', task.name)
        
        if task_type in self.duration_estimates and self.duration_estimates[task_type]:
            # Use historical average
            historical_durations = list(self.duration_estimates[task_type])
            avg_duration = sum(historical_durations) / len(historical_durations)
            
            # Blend with original estimate
            improved = (
                (1 - self.learning_rate) * task.estimated_duration_minutes +
                self.learning_rate * avg_duration
            )
            return int(improved)
        
        return task.estimated_duration_minutes
    
    def get_success_rate(self, task_type: str) -> float:
        """Get success rate for a task type."""
        relevant_tasks = [
            t for t in self.task_history
            if t.get('task_name') == task_type or t.get('metadata', {}).get('type') == task_type
        ]
        
        if not relevant_tasks:
            return 0.5  # Unknown
        
        successes = sum(1 for t in relevant_tasks if t.get('success', False))
        return successes / len(relevant_tasks)
    
    def suggest_priority_adjustment(self, task: Task) -> str:
        """Suggest priority adjustment based on history."""
        task_type = task.metadata.get('type', task.name)
        success_rate = self.get_success_rate(task_type)
        
        # If success rate is low, might need higher priority (more attention)
        if success_rate < 0.5 and task.priority != TaskPriority.CRITICAL.value:
            return "increase"
        elif success_rate > 0.9 and task.priority != TaskPriority.LOW.value:
            return "decrease"
        
        return "maintain"


class TaskManagementOptimizer:
    """Main task management optimizer."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.priority_optimizer = TaskPriorityOptimizer(self.config.get('optimizer_settings'))
        self.adaptive_learner = AdaptiveLearner(
            learning_rate=self.config.get('optimizer_settings', {}).get('learning', {}).get('learning_rate', 0.1)
        )
        
        self.tasks: Dict[str, Task] = {}
        self.resources: Dict[str, Resource] = {}
        self.current_schedule: List[ScheduledTask] = []
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration."""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default config
        return {
            'optimizer_settings': {
                'priority_weights': {
                    'urgency': 0.4,
                    'importance': 0.3,
                    'dependencies': 0.2,
                    'deadline_proximity': 0.1
                },
                'scheduling': {
                    'max_parallel_tasks': 5,
                    'buffer_time_percentage': 0.15
                },
                'learning': {
                    'learning_rate': 0.1
                }
            }
        }
    
    def add_task(self, task: Task):
        """Add a task to be managed."""
        # Improve estimate using adaptive learning
        task.estimated_duration_minutes = self.adaptive_learner.get_improved_estimate(task)
        self.tasks[task.task_id] = task
    
    def add_resource(self, resource: Resource):
        """Add a resource."""
        self.resources[resource.resource_id] = resource
    
    def optimize_and_schedule(self) -> List[ScheduledTask]:
        """Optimize priorities and generate schedule."""
        # Get pending tasks
        pending_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.PENDING.value]
        
        # Prioritize tasks
        prioritized = self.priority_optimizer.prioritize_tasks(pending_tasks)
        
        # Create resource allocator
        resource_list = list(self.resources.values())
        allocator = ResourceAllocator(resource_list)
        
        # Generate schedule
        scheduler = ScheduleOptimizer(self.config.get('optimizer_settings', {}).get('scheduling'))
        schedule = scheduler.generate_schedule(prioritized, allocator)
        
        self.current_schedule = schedule
        return schedule
    
    def record_completion(
        self,
        task_id: str,
        actual_duration_minutes: int,
        success: bool = True
    ):
        """Record task completion for learning."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.COMPLETED.value
            self.adaptive_learner.record_task_completion(task, actual_duration_minutes, success)
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get optimization report."""
        return {
            'total_tasks': len(self.tasks),
            'pending_tasks': len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING.value]),
            'scheduled_tasks': len(self.current_schedule),
            'resource_utilization': self._get_resource_utilization(),
            'estimated_completion': self._get_estimated_completion(),
            'learning_insights': self._get_learning_insights()
        }
    
    def _get_resource_utilization(self) -> Dict[str, float]:
        """Get resource utilization."""
        allocator = ResourceAllocator(list(self.resources.values()))
        return allocator.get_resource_utilization()
    
    def _get_estimated_completion(self) -> Optional[str]:
        """Get estimated completion time."""
        if self.current_schedule:
            latest = max(
                datetime.fromisoformat(st.end_time)
                for st in self.current_schedule
            )
            return latest.isoformat()
        return None
    
    def _get_learning_insights(self) -> Dict[str, Any]:
        """Get learning insights."""
        return {
            'total_completed_tasks': len(self.adaptive_learner.task_history),
            'task_types_learned': len(self.adaptive_learner.duration_estimates),
            'average_estimation_accuracy': self._calculate_estimation_accuracy()
        }
    
    def _calculate_estimation_accuracy(self) -> float:
        """Calculate estimation accuracy."""
        if not self.adaptive_learner.task_history:
            return 0.0
        
        accuracies = []
        for record in self.adaptive_learner.task_history:
            estimated = record['estimated_duration']
            actual = record['actual_duration']
            if actual > 0:
                accuracy = 1 - abs(estimated - actual) / actual
                accuracies.append(max(0, accuracy))
        
        return sum(accuracies) / len(accuracies) if accuracies else 0.0


# Example usage
if __name__ == "__main__":
    print("=== Task Management Optimizer Demo ===\n")
    
    # Initialize optimizer
    optimizer = TaskManagementOptimizer()
    
    # Add resources
    optimizer.add_resource(Resource("cpu1", "CPU 1", ResourceType.COMPUTE.value, 100, 100))
    optimizer.add_resource(Resource("mem1", "Memory 1", ResourceType.MEMORY.value, 1000, 1000))
    
    # Add tasks
    tasks = [
        Task("t1", "Critical Bug Fix", "Fix production bug", priority=TaskPriority.CRITICAL.value,
             estimated_duration_minutes=60, deadline=(datetime.now() + timedelta(hours=2)).isoformat()),
        Task("t2", "Feature Development", "New feature", priority=TaskPriority.HIGH.value,
             estimated_duration_minutes=120),
        Task("t3", "Code Review", "Review PR", priority=TaskPriority.MEDIUM.value,
             estimated_duration_minutes=30),
        Task("t4", "Documentation", "Update docs", priority=TaskPriority.LOW.value,
             estimated_duration_minutes=45),
        Task("t5", "Testing", "Run tests", priority=TaskPriority.HIGH.value,
             estimated_duration_minutes=40, dependencies=["t2"])
    ]
    
    for task in tasks:
        optimizer.add_task(task)
    
    # Optimize and schedule
    schedule = optimizer.optimize_and_schedule()
    
    print(f"Generated schedule with {len(schedule)} tasks:\n")
    for i, st in enumerate(schedule, 1):
        print(f"{i}. {st.task.name}")
        print(f"   Priority Score: {st.priority_score:.2f}")
        print(f"   Start: {st.start_time}")
        print(f"   End: {st.end_time}")
        print(f"   Duration: {st.task.estimated_duration_minutes} min\n")
    
    # Get report
    report = optimizer.get_optimization_report()
    print("Optimization Report:")
    print(json.dumps(report, indent=2))
    
    print("\n=== Demo Complete ===")
