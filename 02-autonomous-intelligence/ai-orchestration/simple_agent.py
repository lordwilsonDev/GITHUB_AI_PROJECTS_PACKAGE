#!/usr/bin/env python3
"""
Simple AI Agent - Lightweight agent for the 620-agent system

Each agent:
- Registers with Consul
- Subscribes to NATS for tasks
- Executes assigned work
- Reports results
- Uses <3MB RAM
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any, Optional
import signal

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - Agent-%(name)s - %(levelname)s - %(message)s'
)


class SimpleAgent:
    """Lightweight AI agent"""
    
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.logger = logging.getLogger(agent_id)
        
        # Service connections
        self.nats_url = os.getenv('NATS_URL', 'nats://localhost:4222')
        self.consul_host = os.getenv('CONSUL_HOST', 'localhost')
        self.consul_port = int(os.getenv('CONSUL_PORT', '8500'))
        
        self.nats_client = None
        self.consul_client = None
        self.running = False
        self.tasks_completed = 0
        
    async def initialize(self):
        """Initialize connections"""
        self.logger.info(f"Initializing {self.agent_type} agent...")
        
        # Connect to NATS
        try:
            import nats
            self.nats_client = await nats.connect(self.nats_url)
            self.logger.info(f"✓ Connected to NATS")
        except Exception as e:
            self.logger.error(f"Failed to connect to NATS: {e}")
            return False
        
        # Register with Consul
        try:
            import consul
            self.consul_client = consul.Consul(
                host=self.consul_host,
                port=self.consul_port
            )
            
            # Register service
            self.consul_client.agent.service.register(
                name=f"ai-agent-{self.agent_type}",
                service_id=self.agent_id,
                tags=[self.agent_type, 'ai-agent', 'active'],
                check={
                    'ttl': '30s',
                    'deregister_critical_service_after': '1m'
                }
            )
            self.logger.info(f"✓ Registered with Consul")
        except Exception as e:
            self.logger.warning(f"Could not register with Consul: {e}")
        
        self.running = True
        self.logger.info(f"✓ Agent {self.agent_id} ready")
        return True
    
    async def send_heartbeat(self):
        """Send heartbeat to Consul"""
        while self.running:
            try:
                if self.consul_client:
                    self.consul_client.agent.check.ttl_pass(
                        f"service:{self.agent_id}"
                    )
                await asyncio.sleep(10)
            except Exception as e:
                self.logger.error(f"Heartbeat failed: {e}")
                await asyncio.sleep(5)
    
    async def handle_task(self, msg):
        """Handle incoming task from NATS"""
        try:
            # Parse task
            task_data = json.loads(msg.data.decode())
            task_type = task_data.get('type')
            task_id = task_data.get('task_id')
            
            self.logger.info(f"Received task: {task_type} (ID: {task_id})")
            
            # Execute task based on agent type
            result = await self.execute_task(task_data)
            
            # Send result
            response_subject = task_data.get('reply_to', f'agent.{self.agent_type}.response')
            await self.nats_client.publish(
                response_subject,
                json.dumps({
                    'agent_id': self.agent_id,
                    'task_id': task_id,
                    'status': 'completed',
                    'result': result
                }).encode()
            )
            
            self.tasks_completed += 1
            self.logger.info(f"✓ Task {task_id} completed (Total: {self.tasks_completed})")
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
    
    async def execute_task(self, task_data: Dict[str, Any]) -> Any:
        """Execute task based on agent type"""
        task_type = task_data.get('type')
        
        # Simulate task execution
        await asyncio.sleep(0.1)  # Simulate work
        
        if self.agent_type == 'research':
            return self.research_task(task_data)
        elif self.agent_type == 'processing':
            return self.processing_task(task_data)
        elif self.agent_type == 'analysis':
            return self.analysis_task(task_data)
        elif self.agent_type == 'monitoring':
            return self.monitoring_task(task_data)
        elif self.agent_type == 'coordination':
            return self.coordination_task(task_data)
        else:
            return {'status': 'unknown_type'}
    
    def research_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research task"""
        query = task_data.get('query', '')
        return {
            'type': 'research',
            'query': query,
            'findings': f"Research results for: {query}",
            'sources': ['source1', 'source2', 'source3']
        }
    
    def processing_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute processing task"""
        data = task_data.get('data', '')
        return {
            'type': 'processing',
            'processed_data': f"Processed: {data}",
            'transformations_applied': ['transform1', 'transform2']
        }
    
    def analysis_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analysis task"""
        data = task_data.get('data', '')
        return {
            'type': 'analysis',
            'insights': f"Analysis of: {data}",
            'metrics': {'quality': 0.95, 'confidence': 0.88}
        }
    
    def monitoring_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute monitoring task"""
        target = task_data.get('target', '')
        return {
            'type': 'monitoring',
            'target': target,
            'status': 'healthy',
            'metrics': {'uptime': 0.99, 'response_time': 120}
        }
    
    def coordination_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute coordination task"""
        workflow = task_data.get('workflow', '')
        return {
            'type': 'coordination',
            'workflow': workflow,
            'status': 'coordinated',
            'agents_assigned': 10
        }
    
    async def subscribe_to_tasks(self):
        """Subscribe to task queue for this agent type"""
        subject = f"agent.{self.agent_type}.request"
        self.logger.info(f"Subscribing to: {subject}")
        
        await self.nats_client.subscribe(
            subject,
            cb=self.handle_task,
            queue=f"{self.agent_type}-workers"  # Load balancing
        )
    
    async def run(self):
        """Main agent loop"""
        self.logger.info("Starting agent...")
        
        # Start heartbeat
        heartbeat_task = asyncio.create_task(self.send_heartbeat())
        
        # Subscribe to tasks
        await self.subscribe_to_tasks()
        
        # Keep running
        try:
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Shutdown signal received")
        finally:
            heartbeat_task.cancel()
    
    async def shutdown(self):
        """Cleanup and shutdown"""
        self.logger.info("Shutting down agent...")
        self.running = False
        
        # Deregister from Consul
        if self.consul_client:
            try:
                self.consul_client.agent.service.deregister(self.agent_id)
                self.logger.info("✓ Deregistered from Consul")
            except Exception as e:
                self.logger.error(f"Failed to deregister: {e}")
        
        # Close NATS connection
        if self.nats_client and not self.nats_client.is_closed:
            await self.nats_client.close()
            self.logger.info("✓ Closed NATS connection")
        
        self.logger.info(f"✓ Agent shutdown complete (Tasks completed: {self.tasks_completed})")


async def main():
    """Main entry point"""
    # Get agent configuration from environment or args
    agent_id = os.getenv('AGENT_ID', f"agent-{os.getpid()}")
    agent_type = os.getenv('AGENT_TYPE', 'processing')
    
    if len(sys.argv) > 1:
        agent_type = sys.argv[1]
    if len(sys.argv) > 2:
        agent_id = sys.argv[2]
    
    # Create and run agent
    agent = SimpleAgent(agent_id, agent_type)
    
    # Handle shutdown signals
    def signal_handler(sig, frame):
        asyncio.create_task(agent.shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if await agent.initialize():
            await agent.run()
    finally:
        await agent.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
