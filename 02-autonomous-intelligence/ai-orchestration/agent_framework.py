#!/usr/bin/env python3
"""
Agent Framework - Base classes for all AI agents in the orchestration system

Provides:
- BaseAgent: Abstract base class for all agents
- WorkerAgent: Stateful worker for task processing
- CoordinatorAgent: Manages groups of workers
- SpecializedAgent: Domain-specific agent wrapper
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from enum import Enum

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent lifecycle states."""
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class AgentCapability(Enum):
    """Standard agent capabilities."""
    RESEARCH = "research"
    WRITING = "writing"
    ANALYSIS = "analysis"
    AUTOMATION = "automation"
    MONITORING = "monitoring"
    COORDINATION = "coordination"
    PHYSICAL_CONTROL = "physical_control"
    MEMORY = "memory"
    LEARNING = "learning"


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    
    All agents must implement:
    - initialize(): Setup agent resources
    - process_task(): Handle incoming tasks
    - shutdown(): Cleanup resources
    """
    
    def __init__(self, agent_id: str, capabilities: List[AgentCapability]):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.status = AgentStatus.INITIALIZING
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.created_at = datetime.now()
        self.metadata = {}
        
        logger.info(f"Agent {agent_id} created with capabilities: {[c.value for c in capabilities]}")
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize agent resources. Return True if successful."""
        pass
    
    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task and return result."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """Cleanup resources. Return True if successful."""
        pass
    
    def can_handle(self, task: Dict[str, Any]) -> bool:
        """Check if agent can handle a task based on capabilities."""
        required_capability = task.get('required_capability')
        if not required_capability:
            return True
        
        return any(c.value == required_capability for c in self.capabilities)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        uptime = (datetime.now() - self.created_at).total_seconds()
        
        return {
            'agent_id': self.agent_id,
            'status': self.status.value,
            'capabilities': [c.value for c in self.capabilities],
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'success_rate': self.tasks_completed / max(1, self.tasks_completed + self.tasks_failed),
            'uptime_seconds': uptime,
            'metadata': self.metadata
        }


class WorkerAgent(BaseAgent):
    """
    General-purpose worker agent for task processing.
    
    Features:
    - Stateful execution
    - Task queue management
    - Error handling and retry logic
    - Performance tracking
    """
    
    def __init__(self, agent_id: str, capabilities: List[AgentCapability] = None):
        if capabilities is None:
            capabilities = [AgentCapability.ANALYSIS, AgentCapability.WRITING]
        
        super().__init__(agent_id, capabilities)
        self.task_queue = asyncio.Queue()
        self.current_task = None
        self.processing = False
    
    async def initialize(self) -> bool:
        """Initialize worker agent."""
        try:
            self.status = AgentStatus.READY
            logger.info(f"Worker {self.agent_id} initialized and ready")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize worker {self.agent_id}: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single task."""
        self.status = AgentStatus.BUSY
        self.current_task = task
        
        try:
            task_type = task.get('type', 'unknown')
            task_id = task.get('id', 'unknown')
            
            logger.info(f"Worker {self.agent_id} processing task {task_id} (type: {task_type})")
            
            # Simulate task processing
            await asyncio.sleep(0.1)  # Replace with actual work
            
            result = {
                'task_id': task_id,
                'agent_id': self.agent_id,
                'status': 'success',
                'result': f"Task {task_id} completed by {self.agent_id}",
                'timestamp': datetime.now().isoformat()
            }
            
            self.tasks_completed += 1
            self.status = AgentStatus.READY
            self.current_task = None
            
            return result
            
        except Exception as e:
            logger.error(f"Worker {self.agent_id} failed to process task: {e}")
            self.tasks_failed += 1
            self.status = AgentStatus.ERROR
            
            return {
                'task_id': task.get('id', 'unknown'),
                'agent_id': self.agent_id,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def shutdown(self) -> bool:
        """Shutdown worker agent."""
        try:
            self.status = AgentStatus.SHUTDOWN
            logger.info(f"Worker {self.agent_id} shutdown complete")
            return True
        except Exception as e:
            logger.error(f"Error shutting down worker {self.agent_id}: {e}")
            return False


class CoordinatorAgent(BaseAgent):
    """
    Coordinator agent that manages groups of worker agents.
    
    Features:
    - Worker pool management
    - Task distribution
    - Load balancing
    - Result aggregation
    """
    
    def __init__(self, agent_id: str, num_workers: int = 10):
        super().__init__(agent_id, [AgentCapability.COORDINATION])
        self.num_workers = num_workers
        self.workers: List[WorkerAgent] = []
        self.task_results = []
    
    async def initialize(self) -> bool:
        """Initialize coordinator and worker pool."""
        try:
            logger.info(f"Coordinator {self.agent_id} creating {self.num_workers} workers...")
            
            # Create worker pool
            for i in range(self.num_workers):
                worker = WorkerAgent(f"{self.agent_id}_worker_{i}")
                await worker.initialize()
                self.workers.append(worker)
            
            self.status = AgentStatus.READY
            logger.info(f"Coordinator {self.agent_id} initialized with {len(self.workers)} workers")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize coordinator {self.agent_id}: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Distribute tasks to workers and aggregate results."""
        self.status = AgentStatus.BUSY
        
        try:
            # If task contains subtasks, distribute them
            subtasks = task.get('subtasks', [task])
            
            logger.info(f"Coordinator {self.agent_id} distributing {len(subtasks)} tasks to {len(self.workers)} workers")
            
            # Distribute tasks to workers
            futures = []
            for i, subtask in enumerate(subtasks):
                worker = self.workers[i % len(self.workers)]
                future = worker.process_task(subtask)
                futures.append(future)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*futures)
            
            self.tasks_completed += 1
            self.status = AgentStatus.READY
            
            return {
                'task_id': task.get('id', 'unknown'),
                'coordinator_id': self.agent_id,
                'status': 'success',
                'subtasks_completed': len(results),
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Coordinator {self.agent_id} failed: {e}")
            self.tasks_failed += 1
            self.status = AgentStatus.ERROR
            
            return {
                'task_id': task.get('id', 'unknown'),
                'coordinator_id': self.agent_id,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def shutdown(self) -> bool:
        """Shutdown coordinator and all workers."""
        try:
            logger.info(f"Coordinator {self.agent_id} shutting down {len(self.workers)} workers...")
            
            # Shutdown all workers
            for worker in self.workers:
                await worker.shutdown()
            
            self.status = AgentStatus.SHUTDOWN
            logger.info(f"Coordinator {self.agent_id} shutdown complete")
            return True
            
        except Exception as e:
            logger.error(f"Error shutting down coordinator {self.agent_id}: {e}")
            return False
    
    def get_worker_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all workers."""
        return [worker.get_stats() for worker in self.workers]


class SpecializedAgent(BaseAgent):
    """
    Wrapper for specialized agents (JARVIS, Level33, NanoApex, MoIE).
    
    Provides:
    - Unified interface for existing agents
    - Integration with orchestration system
    - Capability mapping
    """
    
    def __init__(self, agent_id: str, agent_type: str, agent_path: str, capabilities: List[AgentCapability]):
        super().__init__(agent_id, capabilities)
        self.agent_type = agent_type
        self.agent_path = agent_path
        self.native_agent = None
    
    async def initialize(self) -> bool:
        """Initialize specialized agent."""
        try:
            logger.info(f"Initializing specialized agent {self.agent_id} (type: {self.agent_type})")
            
            # Agent-specific initialization would go here
            # For now, just mark as ready
            self.status = AgentStatus.READY
            self.metadata['agent_type'] = self.agent_type
            self.metadata['agent_path'] = self.agent_path
            
            logger.info(f"Specialized agent {self.agent_id} initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize specialized agent {self.agent_id}: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process task using specialized agent."""
        self.status = AgentStatus.BUSY
        
        try:
            task_id = task.get('id', 'unknown')
            logger.info(f"Specialized agent {self.agent_id} processing task {task_id}")
            
            # Route to appropriate specialized agent
            if self.agent_type == 'jarvis':
                result = await self._process_jarvis_task(task)
            elif self.agent_type == 'level33':
                result = await self._process_level33_task(task)
            elif self.agent_type == 'nanoapex':
                result = await self._process_nanoapex_task(task)
            elif self.agent_type == 'moie':
                result = await self._process_moie_task(task)
            else:
                result = {'status': 'error', 'error': f'Unknown agent type: {self.agent_type}'}
            
            self.tasks_completed += 1
            self.status = AgentStatus.READY
            
            return result
            
        except Exception as e:
            logger.error(f"Specialized agent {self.agent_id} failed: {e}")
            self.tasks_failed += 1
            self.status = AgentStatus.ERROR
            
            return {
                'task_id': task.get('id', 'unknown'),
                'agent_id': self.agent_id,
                'status': 'failed',
                'error': str(e)
            }
    
    async def _process_jarvis_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process task using JARVIS Level 7."""
        # Integration with JARVIS would go here
        return {
            'task_id': task.get('id'),
            'agent_id': self.agent_id,
            'agent_type': 'jarvis',
            'status': 'success',
            'result': 'JARVIS task completed (integration pending)'
        }
    
    async def _process_level33_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process task using Level 33 Sovereign."""
        # Integration with Level 33 would go here
        return {
            'task_id': task.get('id'),
            'agent_id': self.agent_id,
            'agent_type': 'level33',
            'status': 'success',
            'result': 'Level 33 task completed (integration pending)'
        }
    
    async def _process_nanoapex_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process task using NanoApex."""
        # Integration with NanoApex would go here
        return {
            'task_id': task.get('id'),
            'agent_id': self.agent_id,
            'agent_type': 'nanoapex',
            'status': 'success',
            'result': 'NanoApex task completed (integration pending)'
        }
    
    async def _process_moie_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process task using MoIE OS."""
        # Integration with MoIE would go here
        return {
            'task_id': task.get('id'),
            'agent_id': self.agent_id,
            'agent_type': 'moie',
            'status': 'success',
            'result': 'MoIE task completed (integration pending)'
        }
    
    async def shutdown(self) -> bool:
        """Shutdown specialized agent."""
        try:
            self.status = AgentStatus.SHUTDOWN
            logger.info(f"Specialized agent {self.agent_id} shutdown complete")
            return True
        except Exception as e:
            logger.error(f"Error shutting down specialized agent {self.agent_id}: {e}")
            return False


# Example usage and testing
async def test_agent_framework():
    """Test the agent framework."""
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("Testing Agent Framework")
    print("="*60)
    
    # Test 1: Worker Agent
    print("\n[Test 1] Creating and testing worker agent...")
    worker = WorkerAgent("test_worker_1")
    await worker.initialize()
    
    task = {'id': 'task_1', 'type': 'analysis', 'data': 'test data'}
    result = await worker.process_task(task)
    print(f"Result: {json.dumps(result, indent=2)}")
    print(f"Stats: {json.dumps(worker.get_stats(), indent=2)}")
    
    # Test 2: Coordinator Agent
    print("\n[Test 2] Creating and testing coordinator agent...")
    coordinator = CoordinatorAgent("test_coordinator_1", num_workers=5)
    await coordinator.initialize()
    
    batch_task = {
        'id': 'batch_1',
        'subtasks': [
            {'id': f'subtask_{i}', 'type': 'analysis', 'data': f'data_{i}'}
            for i in range(10)
        ]
    }
    
    result = await coordinator.process_task(batch_task)
    print(f"Result: {json.dumps(result, indent=2)}")
    print(f"\nWorker Stats:")
    for stats in coordinator.get_worker_stats():
        print(f"  {stats['agent_id']}: {stats['tasks_completed']} tasks completed")
    
    # Test 3: Specialized Agent
    print("\n[Test 3] Creating and testing specialized agent...")
    specialized = SpecializedAgent(
        "jarvis_1",
        "jarvis",
        "/Users/lordwilson/jarvis_m1",
        [AgentCapability.MEMORY, AgentCapability.ANALYSIS]
    )
    await specialized.initialize()
    
    task = {'id': 'jarvis_task_1', 'type': 'memory_query', 'query': 'test'}
    result = await specialized.process_task(task)
    print(f"Result: {json.dumps(result, indent=2)}")
    
    # Cleanup
    print("\n[Cleanup] Shutting down agents...")
    await worker.shutdown()
    await coordinator.shutdown()
    await specialized.shutdown()
    
    print("\n" + "="*60)
    print("Agent Framework Tests Complete")
    print("="*60)


if __name__ == '__main__':
    asyncio.run(test_agent_framework())
