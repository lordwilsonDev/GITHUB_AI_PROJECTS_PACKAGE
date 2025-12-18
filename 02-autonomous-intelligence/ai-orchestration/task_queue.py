#!/usr/bin/env python3
"""
Task Queue System - Distributed task management and execution

Provides:
- Priority-based task queuing
- Task scheduling and distribution
- Load balancing across agents
- Task retry and failure handling
- Progress tracking and monitoring
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict
import heapq

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class TaskStatus(Enum):
    """Task lifecycle states."""
    PENDING = "pending"
    QUEUED = "queued"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


@dataclass
class Task:
    """Task definition with metadata and execution parameters."""
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    
    # Execution parameters
    max_retries: int = 3
    retry_count: int = 0
    timeout_seconds: int = 300
    required_capability: Optional[str] = None
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    assigned_to: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    # Results
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)
    
    def __lt__(self, other):
        """Compare tasks by priority for heap queue."""
        return self.priority.value < other.priority.value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        data = asdict(self)
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary."""
        data['priority'] = TaskPriority(data['priority'])
        data['status'] = TaskStatus(data['status'])
        return cls(**data)


class TaskQueue:
    """
    Distributed task queue with priority scheduling.
    
    Features:
    - Priority-based scheduling
    - Task dependencies
    - Automatic retry on failure
    - Load balancing
    - Progress tracking
    """
    
    def __init__(self, max_concurrent_tasks: int = 100):
        self.max_concurrent_tasks = max_concurrent_tasks
        
        # Task storage
        self.tasks: Dict[str, Task] = {}
        self.pending_queue = []  # Priority heap
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.failed_tasks: Dict[str, Task] = {}
        
        # Agent management
        self.available_agents: List[str] = []
        self.agent_tasks: Dict[str, List[str]] = defaultdict(list)
        
        # Statistics
        self.stats = {
            'total_tasks': 0,
            'completed': 0,
            'failed': 0,
            'retried': 0,
            'cancelled': 0
        }
        
        # Task callbacks
        self.on_task_complete: Optional[Callable] = None
        self.on_task_failed: Optional[Callable] = None
        
        logger.info(f"TaskQueue initialized (max concurrent: {max_concurrent_tasks})")
    
    async def submit_task(self, task: Task) -> str:
        """Submit a task to the queue."""
        task.status = TaskStatus.QUEUED
        self.tasks[task.task_id] = task
        heapq.heappush(self.pending_queue, task)
        self.stats['total_tasks'] += 1
        
        logger.info(f"Task submitted: {task.task_id} (priority: {task.priority.name})")
        return task.task_id
    
    async def submit_batch(self, tasks: List[Task]) -> List[str]:
        """Submit multiple tasks at once."""
        task_ids = []
        for task in tasks:
            task_id = await self.submit_task(task)
            task_ids.append(task_id)
        
        logger.info(f"Batch submitted: {len(tasks)} tasks")
        return task_ids
    
    def get_next_task(self, agent_id: str, agent_capabilities: List[str] = None) -> Optional[Task]:
        """Get the next task for an agent based on priority and capabilities."""
        if not self.pending_queue:
            return None
        
        # Find a task that matches agent capabilities
        for i, task in enumerate(self.pending_queue):
            # Check if task dependencies are met
            if not self._dependencies_met(task):
                continue
            
            # Check if agent has required capability
            if task.required_capability:
                if not agent_capabilities or task.required_capability not in agent_capabilities:
                    continue
            
            # Assign task to agent
            self.pending_queue.pop(i)
            heapq.heapify(self.pending_queue)
            
            task.status = TaskStatus.ASSIGNED
            task.assigned_to = agent_id
            task.started_at = datetime.now().isoformat()
            
            self.running_tasks[task.task_id] = task
            self.agent_tasks[agent_id].append(task.task_id)
            
            logger.info(f"Task assigned: {task.task_id} -> {agent_id}")
            return task
        
        return None
    
    def _dependencies_met(self, task: Task) -> bool:
        """Check if all task dependencies are completed."""
        if not task.depends_on:
            return True
        
        for dep_id in task.depends_on:
            if dep_id not in self.completed_tasks:
                return False
        
        return True
    
    async def mark_task_running(self, task_id: str):
        """Mark a task as running."""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.status = TaskStatus.RUNNING
            logger.debug(f"Task running: {task_id}")
    
    async def complete_task(self, task_id: str, result: Dict[str, Any]):
        """Mark a task as completed with result."""
        if task_id not in self.running_tasks:
            logger.warning(f"Task {task_id} not found in running tasks")
            return
        
        task = self.running_tasks.pop(task_id)
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now().isoformat()
        task.result = result
        
        self.completed_tasks[task_id] = task
        self.stats['completed'] += 1
        
        # Remove from agent's task list
        if task.assigned_to:
            self.agent_tasks[task.assigned_to].remove(task_id)
        
        logger.info(f"✅ Task completed: {task_id}")
        
        # Call completion callback
        if self.on_task_complete:
            await self.on_task_complete(task)
    
    async def fail_task(self, task_id: str, error: str, retry: bool = True):
        """Mark a task as failed and optionally retry."""
        if task_id not in self.running_tasks:
            logger.warning(f"Task {task_id} not found in running tasks")
            return
        
        task = self.running_tasks.pop(task_id)
        task.error = error
        
        # Remove from agent's task list
        if task.assigned_to:
            self.agent_tasks[task.assigned_to].remove(task_id)
        
        # Retry logic
        if retry and task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskStatus.RETRYING
            task.assigned_to = None
            task.started_at = None
            
            # Re-queue the task
            heapq.heappush(self.pending_queue, task)
            self.stats['retried'] += 1
            
            logger.warning(f"⚠️ Task failed, retrying ({task.retry_count}/{task.max_retries}): {task_id}")
        else:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now().isoformat()
            self.failed_tasks[task_id] = task
            self.stats['failed'] += 1
            
            logger.error(f"❌ Task failed permanently: {task_id} - {error}")
            
            # Call failure callback
            if self.on_task_failed:
                await self.on_task_failed(task)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task."""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        # Remove from pending queue
        if task in self.pending_queue:
            self.pending_queue.remove(task)
            heapq.heapify(self.pending_queue)
        
        # Remove from running tasks
        if task_id in self.running_tasks:
            self.running_tasks.pop(task_id)
            if task.assigned_to:
                self.agent_tasks[task.assigned_to].remove(task_id)
        
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now().isoformat()
        self.stats['cancelled'] += 1
        
        logger.info(f"Task cancelled: {task_id}")
        return True
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a task."""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        return task.to_dict()
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            'pending': len(self.pending_queue),
            'running': len(self.running_tasks),
            'completed': len(self.completed_tasks),
            'failed': len(self.failed_tasks),
            'total_submitted': self.stats['total_tasks'],
            'total_completed': self.stats['completed'],
            'total_failed': self.stats['failed'],
            'total_retried': self.stats['retried'],
            'total_cancelled': self.stats['cancelled'],
            'success_rate': self.stats['completed'] / max(1, self.stats['total_tasks']),
            'active_agents': len([a for a in self.agent_tasks if self.agent_tasks[a]])
        }
    
    def get_agent_load(self, agent_id: str) -> int:
        """Get number of tasks assigned to an agent."""
        return len(self.agent_tasks.get(agent_id, []))
    
    async def wait_for_completion(self, task_ids: List[str], timeout: float = None) -> Dict[str, Task]:
        """Wait for specific tasks to complete."""
        start_time = datetime.now()
        results = {}
        
        while len(results) < len(task_ids):
            for task_id in task_ids:
                if task_id in results:
                    continue
                
                if task_id in self.completed_tasks:
                    results[task_id] = self.completed_tasks[task_id]
                elif task_id in self.failed_tasks:
                    results[task_id] = self.failed_tasks[task_id]
            
            # Check timeout
            if timeout:
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > timeout:
                    logger.warning(f"Timeout waiting for tasks: {len(results)}/{len(task_ids)} completed")
                    break
            
            await asyncio.sleep(0.1)
        
        return results


class TaskScheduler:
    """
    Task scheduler that manages task queue and agent pool.
    
    Features:
    - Automatic task distribution
    - Load balancing
    - Agent health monitoring
    - Workflow orchestration
    """
    
    def __init__(self, task_queue: TaskQueue):
        self.task_queue = task_queue
        self.agents = {}
        self.running = False
        self.scheduler_task = None
        
        logger.info("TaskScheduler initialized")
    
    def register_agent(self, agent_id: str, capabilities: List[str], max_concurrent: int = 5):
        """Register an agent with the scheduler."""
        self.agents[agent_id] = {
            'capabilities': capabilities,
            'max_concurrent': max_concurrent,
            'status': 'active',
            'last_heartbeat': datetime.now()
        }
        logger.info(f"Agent registered: {agent_id} (capabilities: {capabilities})")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Agent unregistered: {agent_id}")
    
    async def start(self):
        """Start the scheduler."""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        self.scheduler_task = asyncio.create_task(self._schedule_loop())
        logger.info("✅ TaskScheduler started")
    
    async def stop(self):
        """Stop the scheduler."""
        self.running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("✅ TaskScheduler stopped")
    
    async def _schedule_loop(self):
        """Main scheduling loop."""
        logger.info("Scheduler loop started")
        
        while self.running:
            try:
                # Assign tasks to available agents
                for agent_id, agent_info in self.agents.items():
                    if agent_info['status'] != 'active':
                        continue
                    
                    # Check agent load
                    current_load = self.task_queue.get_agent_load(agent_id)
                    if current_load >= agent_info['max_concurrent']:
                        continue
                    
                    # Get next task for agent
                    task = self.task_queue.get_next_task(
                        agent_id,
                        agent_info['capabilities']
                    )
                    
                    if task:
                        logger.debug(f"Scheduled task {task.task_id} to agent {agent_id}")
                
                # Sleep before next iteration
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(1)
        
        logger.info("Scheduler loop stopped")


# Example usage and testing
async def test_task_queue():
    """Test the task queue system."""
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("Testing Task Queue System")
    print("="*60)
    
    # Create task queue
    print("\n[Test 1] Creating task queue...")
    queue = TaskQueue(max_concurrent_tasks=50)
    
    # Submit tasks
    print("\n[Test 2] Submitting tasks...")
    tasks = []
    for i in range(10):
        task = Task(
            task_id=f"task_{i}",
            task_type="analysis",
            payload={"data": f"test data {i}"},
            priority=TaskPriority.NORMAL if i % 2 == 0 else TaskPriority.HIGH
        )
        tasks.append(task)
    
    task_ids = await queue.submit_batch(tasks)
    print(f"Submitted {len(task_ids)} tasks")
    
    # Create scheduler
    print("\n[Test 3] Creating scheduler...")
    scheduler = TaskScheduler(queue)
    
    # Register agents
    print("\n[Test 4] Registering agents...")
    for i in range(3):
        scheduler.register_agent(
            f"agent_{i}",
            ["analysis", "writing"],
            max_concurrent=3
        )
    
    # Start scheduler
    print("\n[Test 5] Starting scheduler...")
    await scheduler.start()
    
    # Simulate task processing
    print("\n[Test 6] Processing tasks...")
    await asyncio.sleep(1)
    
    # Get some tasks and complete them
    for agent_id in ["agent_0", "agent_1", "agent_2"]:
        for _ in range(3):
            task = queue.get_next_task(agent_id, ["analysis"])
            if task:
                await queue.mark_task_running(task.task_id)
                await queue.complete_task(task.task_id, {"result": "success"})
    
    # Check stats
    print("\n[Test 7] Queue statistics:")
    stats = queue.get_queue_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Stop scheduler
    print("\n[Cleanup] Stopping scheduler...")
    await scheduler.stop()
    
    print("\n" + "="*60)
    print("Task Queue Tests Complete")
    print("="*60)


if __name__ == '__main__':
    asyncio.run(test_task_queue())
