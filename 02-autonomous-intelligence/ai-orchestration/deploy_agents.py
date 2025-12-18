#!/usr/bin/env python3
"""
Deploy Multiple Worker Agents - Scale the orchestration system

This script deploys and manages multiple worker agents:
- Creates configurable number of worker agents
- Distributes agents across capabilities
- Monitors agent health
- Provides scaling controls
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

# Import our components
from agent_framework import WorkerAgent, CoordinatorAgent, SpecializedAgent, AgentCapability
from message_bus import create_message_bus, Message, MessageType
from task_queue import TaskQueue, TaskScheduler, Task, TaskPriority

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AgentDeployment')


class AgentDeploymentManager:
    """
    Manages deployment and scaling of worker agents.
    
    Features:
    - Deploy agents with different capability profiles
    - Scale up/down dynamically
    - Monitor agent health
    - Load balancing
    """
    
    def __init__(self, task_queue: TaskQueue, message_bus=None):
        self.task_queue = task_queue
        self.message_bus = message_bus
        self.scheduler = TaskScheduler(task_queue)
        
        # Agent pools by capability
        self.agent_pools = {
            'research': [],
            'writing': [],
            'analysis': [],
            'automation': [],
            'monitoring': [],
            'general': []
        }
        
        self.all_agents = []
        self.deployment_stats = {
            'total_deployed': 0,
            'active_agents': 0,
            'failed_deployments': 0
        }
        
        logger.info("AgentDeploymentManager initialized")
    
    async def deploy_agent_pool(self, pool_config: Dict) -> List[WorkerAgent]:
        """
        Deploy a pool of agents with specific configuration.
        
        Args:
            pool_config: {
                'pool_name': str,
                'num_agents': int,
                'capabilities': List[str],
                'max_concurrent': int
            }
        """
        pool_name = pool_config['pool_name']
        num_agents = pool_config['num_agents']
        capabilities = pool_config['capabilities']
        max_concurrent = pool_config.get('max_concurrent', 3)
        
        logger.info(f"Deploying {num_agents} agents for pool '{pool_name}'...")
        
        deployed_agents = []
        
        for i in range(num_agents):
            try:
                # Create agent
                agent_id = f"{pool_name}_agent_{i}"
                
                # Convert capability strings to enums
                capability_enums = []
                for cap in capabilities:
                    try:
                        capability_enums.append(AgentCapability[cap.upper()])
                    except KeyError:
                        logger.warning(f"Unknown capability: {cap}")
                
                agent = WorkerAgent(agent_id, capability_enums)
                
                # Initialize agent
                success = await agent.initialize()
                if not success:
                    logger.error(f"Failed to initialize agent {agent_id}")
                    self.deployment_stats['failed_deployments'] += 1
                    continue
                
                # Register with scheduler
                self.scheduler.register_agent(
                    agent_id,
                    capabilities,
                    max_concurrent=max_concurrent
                )
                
                # Register with message bus
                if self.message_bus:
                    await self.message_bus.register_agent(
                        agent_id,
                        capabilities,
                        {'pool': pool_name, 'index': i}
                    )
                
                # Add to pools
                deployed_agents.append(agent)
                self.all_agents.append(agent)
                
                for cap in capabilities:
                    if cap in self.agent_pools:
                        self.agent_pools[cap].append(agent)
                
                self.deployment_stats['total_deployed'] += 1
                self.deployment_stats['active_agents'] += 1
                
                logger.info(f"✅ Deployed: {agent_id}")
                
            except Exception as e:
                logger.error(f"Error deploying agent {i} in pool {pool_name}: {e}")
                self.deployment_stats['failed_deployments'] += 1
        
        logger.info(f"✅ Pool '{pool_name}' deployed: {len(deployed_agents)}/{num_agents} agents")
        return deployed_agents
    
    async def deploy_standard_configuration(self, total_agents: int = 100):
        """
        Deploy a standard configuration of agents across different capabilities.
        
        Distribution:
        - 30% Research agents
        - 30% Writing agents
        - 20% Analysis agents
        - 10% Automation agents
        - 10% General purpose agents
        """
        logger.info(f"Deploying standard configuration: {total_agents} total agents")
        
        pools = [
            {
                'pool_name': 'research',
                'num_agents': int(total_agents * 0.3),
                'capabilities': ['research', 'analysis'],
                'max_concurrent': 5
            },
            {
                'pool_name': 'writing',
                'num_agents': int(total_agents * 0.3),
                'capabilities': ['writing'],
                'max_concurrent': 3
            },
            {
                'pool_name': 'analysis',
                'num_agents': int(total_agents * 0.2),
                'capabilities': ['analysis'],
                'max_concurrent': 4
            },
            {
                'pool_name': 'automation',
                'num_agents': int(total_agents * 0.1),
                'capabilities': ['automation'],
                'max_concurrent': 2
            },
            {
                'pool_name': 'general',
                'num_agents': int(total_agents * 0.1),
                'capabilities': ['research', 'writing', 'analysis'],
                'max_concurrent': 3
            }
        ]
        
        for pool_config in pools:
            await self.deploy_agent_pool(pool_config)
        
        logger.info(f"✅ Standard configuration deployed: {len(self.all_agents)} agents")
    
    async def deploy_620_agent_system(self):
        """
        Deploy the full 620-agent system as described in the workflow.
        
        Distribution optimized for various workflows:
        - Content Creation: 200 agents
        - Data Analysis: 150 agents
        - Research: 120 agents
        - Automation: 100 agents
        - Monitoring: 50 agents
        """
        logger.info("🚀 Deploying 620-agent system...")
        
        pools = [
            # Content Creation Pool (200 agents)
            {
                'pool_name': 'content_research',
                'num_agents': 50,
                'capabilities': ['research'],
                'max_concurrent': 5
            },
            {
                'pool_name': 'content_writing',
                'num_agents': 100,
                'capabilities': ['writing'],
                'max_concurrent': 3
            },
            {
                'pool_name': 'content_editing',
                'num_agents': 30,
                'capabilities': ['writing', 'analysis'],
                'max_concurrent': 4
            },
            {
                'pool_name': 'content_factcheck',
                'num_agents': 20,
                'capabilities': ['research', 'analysis'],
                'max_concurrent': 5
            },
            
            # Data Analysis Pool (150 agents)
            {
                'pool_name': 'data_analysis',
                'num_agents': 100,
                'capabilities': ['analysis'],
                'max_concurrent': 4
            },
            {
                'pool_name': 'data_aggregation',
                'num_agents': 30,
                'capabilities': ['analysis'],
                'max_concurrent': 6
            },
            {
                'pool_name': 'data_visualization',
                'num_agents': 20,
                'capabilities': ['analysis', 'writing'],
                'max_concurrent': 3
            },
            
            # Research Pool (120 agents)
            {
                'pool_name': 'research_primary',
                'num_agents': 80,
                'capabilities': ['research'],
                'max_concurrent': 5
            },
            {
                'pool_name': 'research_synthesis',
                'num_agents': 40,
                'capabilities': ['research', 'analysis', 'writing'],
                'max_concurrent': 4
            },
            
            # Automation Pool (100 agents)
            {
                'pool_name': 'automation_workers',
                'num_agents': 80,
                'capabilities': ['automation'],
                'max_concurrent': 2
            },
            {
                'pool_name': 'automation_coordinators',
                'num_agents': 20,
                'capabilities': ['automation', 'coordination'],
                'max_concurrent': 5
            },
            
            # Monitoring Pool (50 agents)
            {
                'pool_name': 'monitoring',
                'num_agents': 50,
                'capabilities': ['monitoring'],
                'max_concurrent': 10
            }
        ]
        
        for pool_config in pools:
            await self.deploy_agent_pool(pool_config)
        
        logger.info(f"✅ 620-agent system deployed: {len(self.all_agents)} agents active")
    
    async def scale_pool(self, pool_name: str, target_size: int):
        """Scale a specific pool up or down."""
        current_pool = self.agent_pools.get(pool_name, [])
        current_size = len(current_pool)
        
        if target_size > current_size:
            # Scale up
            num_to_add = target_size - current_size
            logger.info(f"Scaling up pool '{pool_name}': {current_size} -> {target_size}")
            
            await self.deploy_agent_pool({
                'pool_name': pool_name,
                'num_agents': num_to_add,
                'capabilities': [pool_name],
                'max_concurrent': 3
            })
        
        elif target_size < current_size:
            # Scale down
            num_to_remove = current_size - target_size
            logger.info(f"Scaling down pool '{pool_name}': {current_size} -> {target_size}")
            
            # Shutdown excess agents
            for i in range(num_to_remove):
                agent = current_pool.pop()
                await agent.shutdown()
                self.all_agents.remove(agent)
                self.deployment_stats['active_agents'] -= 1
    
    def get_deployment_stats(self) -> Dict:
        """Get deployment statistics."""
        pool_stats = {}
        for pool_name, agents in self.agent_pools.items():
            pool_stats[pool_name] = len(agents)
        
        return {
            'total_deployed': self.deployment_stats['total_deployed'],
            'active_agents': self.deployment_stats['active_agents'],
            'failed_deployments': self.deployment_stats['failed_deployments'],
            'pool_distribution': pool_stats,
            'timestamp': datetime.now().isoformat()
        }
    
    async def start_scheduler(self):
        """Start the task scheduler."""
        await self.scheduler.start()
        logger.info("✅ Task scheduler started")
    
    async def stop_scheduler(self):
        """Stop the task scheduler."""
        await self.scheduler.stop()
        logger.info("✅ Task scheduler stopped")
    
    async def shutdown_all_agents(self):
        """Shutdown all deployed agents."""
        logger.info(f"Shutting down {len(self.all_agents)} agents...")
        
        for agent in self.all_agents:
            await agent.shutdown()
        
        self.all_agents.clear()
        for pool in self.agent_pools.values():
            pool.clear()
        
        self.deployment_stats['active_agents'] = 0
        logger.info("✅ All agents shutdown")


async def main():
    """Main deployment script."""
    print("\n" + "="*60)
    print("AI Agent Deployment System")
    print("="*60)
    
    # Create task queue
    print("\n[1/5] Creating task queue...")
    task_queue = TaskQueue(max_concurrent_tasks=1000)
    
    # Create message bus
    print("\n[2/5] Creating message bus...")
    message_bus = await create_message_bus()
    
    # Create deployment manager
    print("\n[3/5] Creating deployment manager...")
    manager = AgentDeploymentManager(task_queue, message_bus)
    
    # Deploy agents
    print("\n[4/5] Deploying agents...")
    print("\nChoose deployment configuration:")
    print("  1. Small (10 agents) - Testing")
    print("  2. Medium (100 agents) - Standard")
    print("  3. Large (620 agents) - Full system")
    print("  4. Custom")
    
    # For automated deployment, use medium configuration
    print("\nDeploying medium configuration (100 agents)...")
    await manager.deploy_standard_configuration(total_agents=100)
    
    # Start scheduler
    print("\n[5/5] Starting task scheduler...")
    await manager.start_scheduler()
    
    # Show deployment stats
    print("\n" + "="*60)
    print("Deployment Complete")
    print("="*60)
    stats = manager.get_deployment_stats()
    print(json.dumps(stats, indent=2))
    
    # Submit test workflow
    print("\n" + "="*60)
    print("Testing with sample workflow")
    print("="*60)
    
    # Create test tasks
    test_tasks = []
    for i in range(50):
        task = Task(
            task_id=f"test_task_{i}",
            task_type="analysis",
            payload={'data': f'test data {i}'},
            priority=TaskPriority.NORMAL
        )
        test_tasks.append(task)
    
    task_ids = await task_queue.submit_batch(test_tasks)
    print(f"\nSubmitted {len(task_ids)} test tasks")
    
    # Process tasks
    print("\nProcessing tasks...")
    await asyncio.sleep(2)
    
    # Simulate task completion
    for i in range(min(30, len(test_tasks))):
        task = task_queue.get_next_task(f"analysis_agent_{i % 20}", ['analysis'])
        if task:
            await task_queue.mark_task_running(task.task_id)
            await task_queue.complete_task(task.task_id, {'result': 'success'})
    
    # Show final stats
    print("\n" + "="*60)
    print("Final Statistics")
    print("="*60)
    queue_stats = task_queue.get_queue_stats()
    print(json.dumps(queue_stats, indent=2))
    
    # Keep running
    print("\n" + "="*60)
    print("System running. Press Ctrl+C to stop.")
    print("="*60)
    
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        await manager.stop_scheduler()
        await manager.shutdown_all_agents()
        if message_bus:
            await message_bus.disconnect()
        print("\n✅ Shutdown complete")


if __name__ == '__main__':
    asyncio.run(main())
