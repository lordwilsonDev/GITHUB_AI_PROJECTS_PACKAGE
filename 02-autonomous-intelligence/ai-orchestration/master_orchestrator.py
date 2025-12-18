#!/usr/bin/env python3
"""
Master Orchestrator - Central coordinator for 620-agent AI system

Integrates:
- JARVIS Level 7 (personal AI assistant)
- Level 33 Sovereign (self-healing agent)
- NanoApex (computer automation)
- MoIE OS (mixture of experts)

Architecture:
- Temporal: Workflow orchestration
- Ray: Distributed execution
- NATS: Inter-agent messaging
- Consul: Service discovery
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path.home() / 'ai-orchestration' / 'logs' / 'orchestrator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('MasterOrchestrator')


class MasterOrchestrator:
    """
    Central coordinator for all AI agents and workflows.
    
    Responsibilities:
    1. Initialize and manage agent lifecycle
    2. Route tasks to appropriate agents
    3. Coordinate multi-agent workflows
    4. Monitor health and performance
    5. Handle failures and recovery
    """
    
    def __init__(self):
        self.agents = {}
        self.workflows = {}
        self.message_bus = None
        self.ray_cluster = None
        self.temporal_client = None
        self.consul_client = None
        
        logger.info("Master Orchestrator initializing...")
    
    async def initialize(self):
        """Initialize all orchestration components."""
        logger.info("Starting initialization sequence...")
        
        # Step 1: Check dependencies
        await self._check_dependencies()
        
        # Step 2: Initialize Ray cluster
        await self._init_ray()
        
        # Step 3: Connect to NATS message bus
        await self._init_nats()
        
        # Step 4: Register with Consul
        await self._init_consul()
        
        # Step 5: Connect to Temporal
        await self._init_temporal()
        
        # Step 6: Discover and register agents
        await self._discover_agents()
        
        logger.info("✅ Master Orchestrator initialized successfully")
    
    async def _check_dependencies(self):
        """Check if required services are available."""
        logger.info("Checking dependencies...")
        
        dependencies = {
            'ray': self._check_ray,
            'nats': self._check_nats,
            'consul': self._check_consul,
            'temporal': self._check_temporal
        }
        
        results = {}
        for name, check_func in dependencies.items():
            try:
                available = await check_func()
                results[name] = available
                status = "✅" if available else "⚠️"
                logger.info(f"{status} {name}: {'Available' if available else 'Not available (optional)'}")
            except Exception as e:
                results[name] = False
                logger.warning(f"⚠️ {name}: Error checking - {e}")
        
        # Ray is required, others are optional
        if not results.get('ray', False):
            logger.warning("Ray not available - will use local execution mode")
        
        return results
    
    async def _check_ray(self) -> bool:
        """Check if Ray is available."""
        try:
            import ray
            return True
        except ImportError:
            return False
    
    async def _check_nats(self) -> bool:
        """Check if NATS is available."""
        try:
            import nats
            # Try to connect
            nc = await nats.connect("nats://localhost:4222", connect_timeout=2)
            await nc.close()
            return True
        except Exception:
            return False
    
    async def _check_consul(self) -> bool:
        """Check if Consul is available."""
        try:
            import consul
            c = consul.Consul()
            c.agent.self()
            return True
        except Exception:
            return False
    
    async def _check_temporal(self) -> bool:
        """Check if Temporal is available."""
        try:
            from temporalio.client import Client
            # Try to connect
            client = await Client.connect("localhost:7233", timeout=2)
            await client.close()
            return True
        except Exception:
            return False
    
    async def _init_ray(self):
        """Initialize Ray cluster for distributed execution."""
        try:
            import ray
            
            if not ray.is_initialized():
                # Initialize Ray with resource limits
                ray.init(
                    num_cpus=8,  # Adjust based on your Mac
                    object_store_memory=1 * 1024 * 1024 * 1024,  # 1GB
                    ignore_reinit_error=True,
                    logging_level=logging.INFO
                )
                logger.info("✅ Ray cluster initialized")
                self.ray_cluster = ray
            else:
                logger.info("✅ Ray already initialized")
                self.ray_cluster = ray
        except ImportError:
            logger.warning("⚠️ Ray not installed - using local execution")
            self.ray_cluster = None
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ray: {e}")
            self.ray_cluster = None
    
    async def _init_nats(self):
        """Connect to NATS message bus."""
        try:
            import nats
            
            self.message_bus = await nats.connect("nats://localhost:4222")
            logger.info("✅ Connected to NATS message bus")
        except ImportError:
            logger.warning("⚠️ NATS not installed - messaging disabled")
            self.message_bus = None
        except Exception as e:
            logger.warning(f"⚠️ Could not connect to NATS: {e}")
            self.message_bus = None
    
    async def _init_consul(self):
        """Register with Consul for service discovery."""
        try:
            import consul
            
            self.consul_client = consul.Consul()
            
            # Register orchestrator service
            self.consul_client.agent.service.register(
                name='master-orchestrator',
                service_id='master-orchestrator-1',
                port=8000,
                tags=['orchestrator', 'coordinator'],
                check=consul.Check.tcp('localhost', 8000, interval='10s')
            )
            logger.info("✅ Registered with Consul")
        except ImportError:
            logger.warning("⚠️ Consul not installed - service discovery disabled")
            self.consul_client = None
        except Exception as e:
            logger.warning(f"⚠️ Could not register with Consul: {e}")
            self.consul_client = None
    
    async def _init_temporal(self):
        """Connect to Temporal workflow engine."""
        try:
            from temporalio.client import Client
            
            self.temporal_client = await Client.connect("localhost:7233")
            logger.info("✅ Connected to Temporal")
        except ImportError:
            logger.warning("⚠️ Temporal not installed - workflow orchestration disabled")
            self.temporal_client = None
        except Exception as e:
            logger.warning(f"⚠️ Could not connect to Temporal: {e}")
            self.temporal_client = None
    
    async def _discover_agents(self):
        """Discover and register available agents."""
        logger.info("Discovering agents...")
        
        # Define agent locations
        agent_configs = [
            {
                'name': 'JARVIS_Level7',
                'path': Path.home() / 'jarvis_m1',
                'type': 'personal_assistant',
                'capabilities': ['memory', 'analytics', 'monitoring']
            },
            {
                'name': 'Level33_Sovereign',
                'path': Path.home() / 'level33_sovereign',
                'type': 'autonomous_agent',
                'capabilities': ['self_healing', 'physical_control', 'reflexion']
            },
            {
                'name': 'NanoApex',
                'path': Path.home() / 'nanoapex',
                'type': 'automation',
                'capabilities': ['computer_control', 'automation', 'scripting']
            },
            {
                'name': 'MoIE_OS',
                'path': Path.home() / 'moie_os_core',
                'type': 'mixture_of_experts',
                'capabilities': ['expert_routing', 'specialized_tasks']
            }
        ]
        
        for config in agent_configs:
            if config['path'].exists():
                self.agents[config['name']] = {
                    'config': config,
                    'status': 'discovered',
                    'last_seen': datetime.now().isoformat()
                }
                logger.info(f"✅ Discovered: {config['name']} at {config['path']}")
            else:
                logger.warning(f"⚠️ Agent not found: {config['name']} at {config['path']}")
        
        logger.info(f"Discovered {len(self.agents)} agents")
    
    async def create_agent_pool(self, num_agents: int = 10):
        """Create a pool of worker agents using Ray."""
        if not self.ray_cluster:
            logger.warning("Ray not available - cannot create agent pool")
            return []
        
        logger.info(f"Creating pool of {num_agents} worker agents...")
        
        @self.ray_cluster.remote
        class WorkerAgent:
            def __init__(self, agent_id: int):
                self.agent_id = agent_id
                self.tasks_completed = 0
            
            def process_task(self, task: Dict) -> Dict:
                """Process a task and return result."""
                self.tasks_completed += 1
                return {
                    'agent_id': self.agent_id,
                    'task': task,
                    'status': 'completed',
                    'result': f"Task {task.get('id')} processed by agent {self.agent_id}"
                }
            
            def get_stats(self) -> Dict:
                return {
                    'agent_id': self.agent_id,
                    'tasks_completed': self.tasks_completed
                }
        
        # Create agent pool
        agents = [WorkerAgent.remote(i) for i in range(num_agents)]
        logger.info(f"✅ Created {num_agents} worker agents")
        
        return agents
    
    async def execute_workflow(self, workflow_name: str, tasks: List[Dict]):
        """Execute a multi-agent workflow."""
        logger.info(f"Executing workflow: {workflow_name} with {len(tasks)} tasks")
        
        if not self.ray_cluster:
            logger.warning("Ray not available - executing tasks sequentially")
            results = []
            for task in tasks:
                result = {'task': task, 'status': 'completed', 'mode': 'sequential'}
                results.append(result)
            return results
        
        # Create agent pool
        agents = await self.create_agent_pool(min(len(tasks), 10))
        
        # Distribute tasks to agents
        futures = []
        for i, task in enumerate(tasks):
            agent = agents[i % len(agents)]
            future = agent.process_task.remote(task)
            futures.append(future)
        
        # Wait for all tasks to complete
        results = self.ray_cluster.get(futures)
        
        logger.info(f"✅ Workflow {workflow_name} completed: {len(results)} tasks processed")
        return results
    
    async def publish_message(self, subject: str, message: Dict):
        """Publish message to NATS for inter-agent communication."""
        if not self.message_bus:
            logger.warning("NATS not available - message not sent")
            return
        
        try:
            await self.message_bus.publish(
                subject,
                json.dumps(message).encode()
            )
            logger.info(f"📤 Published message to {subject}")
        except Exception as e:
            logger.error(f"❌ Failed to publish message: {e}")
    
    async def get_system_status(self) -> Dict:
        """Get current system status."""
        return {
            'orchestrator': 'running',
            'timestamp': datetime.now().isoformat(),
            'agents': len(self.agents),
            'components': {
                'ray': self.ray_cluster is not None,
                'nats': self.message_bus is not None,
                'consul': self.consul_client is not None,
                'temporal': self.temporal_client is not None
            },
            'discovered_agents': list(self.agents.keys())
        }
    
    async def shutdown(self):
        """Gracefully shutdown orchestrator."""
        logger.info("Shutting down Master Orchestrator...")
        
        # Close NATS connection
        if self.message_bus:
            await self.message_bus.close()
            logger.info("✅ NATS connection closed")
        
        # Deregister from Consul
        if self.consul_client:
            try:
                self.consul_client.agent.service.deregister('master-orchestrator-1')
                logger.info("✅ Deregistered from Consul")
            except Exception as e:
                logger.warning(f"⚠️ Could not deregister from Consul: {e}")
        
        # Shutdown Ray
        if self.ray_cluster and self.ray_cluster.is_initialized():
            self.ray_cluster.shutdown()
            logger.info("✅ Ray cluster shutdown")
        
        logger.info("✅ Master Orchestrator shutdown complete")


async def main():
    """Main entry point for orchestrator."""
    orchestrator = MasterOrchestrator()
    
    try:
        # Initialize
        await orchestrator.initialize()
        
        # Get system status
        status = await orchestrator.get_system_status()
        logger.info(f"System Status: {json.dumps(status, indent=2)}")
        
        # Example: Execute a simple workflow
        logger.info("\n" + "="*60)
        logger.info("DEMO: Executing sample workflow")
        logger.info("="*60)
        
        tasks = [
            {'id': i, 'type': 'demo', 'data': f'Task {i}'}
            for i in range(20)
        ]
        
        results = await orchestrator.execute_workflow('demo_workflow', tasks)
        logger.info(f"\n✅ Demo workflow completed: {len(results)} tasks processed")
        
        # Keep running
        logger.info("\nOrchestrator running. Press Ctrl+C to stop.")
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logger.info("\nReceived shutdown signal")
    finally:
        await orchestrator.shutdown()


# Integration with agent framework, message bus, and task queue
from agent_framework import WorkerAgent, CoordinatorAgent, SpecializedAgent, AgentCapability
from message_bus import create_message_bus, Message, MessageType
from task_queue import TaskQueue, TaskScheduler, Task, TaskPriority


class EnhancedMasterOrchestrator(MasterOrchestrator):
    """
    Enhanced orchestrator with full integration of all components.
    
    Integrates:
    - Agent Framework (WorkerAgent, CoordinatorAgent, SpecializedAgent)
    - Message Bus (NATS-based inter-agent communication)
    - Task Queue (Priority-based task scheduling)
    - Ray (Distributed execution)
    - Temporal (Workflow orchestration)
    """
    
    def __init__(self):
        super().__init__()
        self.task_queue = None
        self.task_scheduler = None
        self.worker_agents = []
        self.coordinator_agents = []
        self.specialized_agents = []
    
    async def initialize(self):
        """Initialize enhanced orchestrator with all components."""
        logger.info("Enhanced Master Orchestrator initializing...")
        
        # Initialize base components
        await super().initialize()
        
        # Initialize task queue
        await self._init_task_queue()
        
        # Initialize agent pools
        await self._init_agent_pools()
        
        # Start task scheduler
        await self._start_scheduler()
        
        logger.info("✅ Enhanced Master Orchestrator initialized successfully")
    
    async def _init_task_queue(self):
        """Initialize task queue and scheduler."""
        logger.info("Initializing task queue...")
        
        self.task_queue = TaskQueue(max_concurrent_tasks=620)
        self.task_scheduler = TaskScheduler(self.task_queue)
        
        # Set up task callbacks
        self.task_queue.on_task_complete = self._on_task_complete
        self.task_queue.on_task_failed = self._on_task_failed
        
        logger.info("✅ Task queue initialized")
    
    async def _init_agent_pools(self):
        """Initialize worker and specialized agent pools."""
        logger.info("Initializing agent pools...")
        
        # Create worker agents
        num_workers = 10
        logger.info(f"Creating {num_workers} worker agents...")
        for i in range(num_workers):
            worker = WorkerAgent(
                f"worker_{i}",
                [AgentCapability.ANALYSIS, AgentCapability.WRITING]
            )
            await worker.initialize()
            self.worker_agents.append(worker)
            
            # Register with scheduler
            self.task_scheduler.register_agent(
                worker.agent_id,
                [c.value for c in worker.capabilities],
                max_concurrent=3
            )
            
            # Register with message bus
            if self.message_bus:
                await self.message_bus.register_agent(
                    worker.agent_id,
                    [c.value for c in worker.capabilities]
                )
        
        # Create coordinator agents
        num_coordinators = 2
        logger.info(f"Creating {num_coordinators} coordinator agents...")
        for i in range(num_coordinators):
            coordinator = CoordinatorAgent(
                f"coordinator_{i}",
                num_workers=5
            )
            await coordinator.initialize()
            self.coordinator_agents.append(coordinator)
            
            # Register with scheduler
            self.task_scheduler.register_agent(
                coordinator.agent_id,
                [AgentCapability.COORDINATION.value],
                max_concurrent=10
            )
        
        # Create specialized agents for existing systems
        logger.info("Creating specialized agents...")
        
        specialized_configs = [
            {
                'id': 'jarvis_level7',
                'type': 'jarvis',
                'path': str(Path.home() / 'jarvis_m1'),
                'capabilities': [AgentCapability.MEMORY, AgentCapability.ANALYSIS, AgentCapability.MONITORING]
            },
            {
                'id': 'level33_sovereign',
                'type': 'level33',
                'path': str(Path.home() / 'level33_sovereign'),
                'capabilities': [AgentCapability.AUTOMATION, AgentCapability.PHYSICAL_CONTROL, AgentCapability.LEARNING]
            },
            {
                'id': 'nanoapex',
                'type': 'nanoapex',
                'path': str(Path.home() / 'nanoapex'),
                'capabilities': [AgentCapability.AUTOMATION, AgentCapability.PHYSICAL_CONTROL]
            },
            {
                'id': 'moie_os',
                'type': 'moie',
                'path': str(Path.home() / 'moie_os_core'),
                'capabilities': [AgentCapability.COORDINATION, AgentCapability.RESEARCH]
            }
        ]
        
        for config in specialized_configs:
            if Path(config['path']).exists():
                agent = SpecializedAgent(
                    config['id'],
                    config['type'],
                    config['path'],
                    config['capabilities']
                )
                await agent.initialize()
                self.specialized_agents.append(agent)
                
                # Register with scheduler
                self.task_scheduler.register_agent(
                    agent.agent_id,
                    [c.value for c in agent.capabilities],
                    max_concurrent=5
                )
                
                logger.info(f"✅ Specialized agent initialized: {config['id']}")
        
        total_agents = len(self.worker_agents) + len(self.coordinator_agents) + len(self.specialized_agents)
        logger.info(f"✅ Agent pools initialized: {total_agents} total agents")
    
    async def _start_scheduler(self):
        """Start the task scheduler."""
        if self.task_scheduler:
            await self.task_scheduler.start()
            logger.info("✅ Task scheduler started")
    
    async def _on_task_complete(self, task):
        """Callback when a task completes."""
        logger.info(f"✅ Task completed: {task.task_id}")
        
        # Publish completion event
        if self.message_bus:
            await self.message_bus.broadcast_event(
                "task.completed",
                "orchestrator",
                {'task_id': task.task_id, 'result': task.result}
            )
    
    async def _on_task_failed(self, task):
        """Callback when a task fails."""
        logger.error(f"❌ Task failed: {task.task_id} - {task.error}")
        
        # Publish failure event
        if self.message_bus:
            await self.message_bus.broadcast_event(
                "task.failed",
                "orchestrator",
                {'task_id': task.task_id, 'error': task.error}
            )
    
    async def submit_workflow(self, workflow_name: str, tasks: List[Dict]) -> List[str]:
        """Submit a workflow with multiple tasks."""
        logger.info(f"Submitting workflow: {workflow_name} with {len(tasks)} tasks")
        
        # Convert to Task objects
        task_objects = []
        for i, task_data in enumerate(tasks):
            task = Task(
                task_id=f"{workflow_name}_task_{i}",
                task_type=task_data.get('type', 'generic'),
                payload=task_data.get('payload', {}),
                priority=TaskPriority[task_data.get('priority', 'NORMAL')],
                required_capability=task_data.get('required_capability')
            )
            task_objects.append(task)
        
        # Submit to queue
        task_ids = await self.task_queue.submit_batch(task_objects)
        
        logger.info(f"✅ Workflow submitted: {workflow_name} ({len(task_ids)} tasks)")
        return task_ids
    
    async def get_system_status(self) -> Dict:
        """Get comprehensive system status."""
        base_status = await super().get_system_status()
        
        # Add enhanced status
        base_status.update({
            'task_queue': self.task_queue.get_queue_stats() if self.task_queue else {},
            'worker_agents': len(self.worker_agents),
            'coordinator_agents': len(self.coordinator_agents),
            'specialized_agents': len(self.specialized_agents),
            'total_agents': len(self.worker_agents) + len(self.coordinator_agents) + len(self.specialized_agents),
            'scheduler_running': self.task_scheduler.running if self.task_scheduler else False
        })
        
        return base_status
    
    async def shutdown(self):
        """Gracefully shutdown enhanced orchestrator."""
        logger.info("Shutting down Enhanced Master Orchestrator...")
        
        # Stop scheduler
        if self.task_scheduler:
            await self.task_scheduler.stop()
        
        # Shutdown all agents
        for agent in self.worker_agents + self.coordinator_agents + self.specialized_agents:
            await agent.shutdown()
        
        # Shutdown base components
        await super().shutdown()
        
        logger.info("✅ Enhanced Master Orchestrator shutdown complete")


async def main_enhanced():
    """Main entry point for enhanced orchestrator."""
    orchestrator = EnhancedMasterOrchestrator()
    
    try:
        # Initialize
        await orchestrator.initialize()
        
        # Get system status
        status = await orchestrator.get_system_status()
        logger.info(f"\nSystem Status:\n{json.dumps(status, indent=2)}")
        
        # Example: Submit a content creation workflow
        logger.info("\n" + "="*60)
        logger.info("DEMO: Content Creation Workflow")
        logger.info("="*60)
        
        content_tasks = [
            {'type': 'research', 'priority': 'HIGH', 'payload': {'topic': 'AI trends'}},
            {'type': 'writing', 'priority': 'NORMAL', 'payload': {'content_type': 'blog_post'}},
            {'type': 'editing', 'priority': 'NORMAL', 'payload': {'style': 'professional'}},
            {'type': 'analysis', 'priority': 'LOW', 'payload': {'metrics': ['readability', 'seo']}}
        ]
        
        task_ids = await orchestrator.submit_workflow('content_creation', content_tasks)
        logger.info(f"\n✅ Workflow submitted: {len(task_ids)} tasks")
        
        # Wait for tasks to be processed
        logger.info("\nProcessing tasks...")
        await asyncio.sleep(3)
        
        # Get final status
        final_status = await orchestrator.get_system_status()
        logger.info(f"\nFinal Status:\n{json.dumps(final_status, indent=2)}")
        
        # Keep running
        logger.info("\n" + "="*60)
        logger.info("Enhanced Orchestrator running. Press Ctrl+C to stop.")
        logger.info("="*60)
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logger.info("\nReceived shutdown signal")
    finally:
        await orchestrator.shutdown()


if __name__ == '__main__':
    # Run enhanced orchestrator
    asyncio.run(main_enhanced())
