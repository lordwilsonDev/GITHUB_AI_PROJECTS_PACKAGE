#!/usr/bin/env python3
"""
AI Agent Orchestration System - Main Orchestrator

This is the master coordinator for 620 AI agents.
It integrates Temporal, NATS, Consul, and Ray to create
a fault-tolerant, distributed agent system.
"""

import asyncio
import os
import logging
from datetime import timedelta
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Main orchestrator for the 620-agent system"""
    
    def __init__(self):
        self.temporal_host = os.getenv('TEMPORAL_HOST', 'localhost:7233')
        self.nats_url = os.getenv('NATS_URL', 'nats://localhost:4222')
        self.consul_host = os.getenv('CONSUL_HOST', 'localhost:8500')
        self.ray_address = os.getenv('RAY_ADDRESS', 'localhost:6379')
        self.agent_count = int(os.getenv('AGENT_COUNT', '620'))
        
        self.temporal_client = None
        self.nats_client = None
        self.consul_client = None
        self.ray_initialized = False
        
    async def initialize(self):
        """Initialize connections to all services"""
        logger.info("Initializing Agent Orchestrator...")
        logger.info(f"Target agent count: {self.agent_count}")
        
        # Initialize Temporal
        try:
            from temporalio.client import Client
            self.temporal_client = await Client.connect(self.temporal_host)
            logger.info(f"✓ Connected to Temporal at {self.temporal_host}")
        except Exception as e:
            logger.warning(f"Could not connect to Temporal: {e}")
        
        # Initialize NATS
        try:
            import nats
            self.nats_client = await nats.connect(self.nats_url)
            logger.info(f"✓ Connected to NATS at {self.nats_url}")
        except Exception as e:
            logger.warning(f"Could not connect to NATS: {e}")
        
        # Initialize Consul
        try:
            import consul
            self.consul_client = consul.Consul(host=self.consul_host.split(':')[0])
            logger.info(f"✓ Connected to Consul at {self.consul_host}")
        except Exception as e:
            logger.warning(f"Could not connect to Consul: {e}")
        
        # Initialize Ray
        try:
            import ray
            ray.init(address=f"ray://{self.ray_address}", ignore_reinit_error=True)
            self.ray_initialized = True
            logger.info(f"✓ Connected to Ray at {self.ray_address}")
        except Exception as e:
            logger.warning(f"Could not connect to Ray: {e}")
        
        logger.info("✓ Orchestrator initialized successfully")
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all services"""
        health = {
            'temporal': self.temporal_client is not None,
            'nats': self.nats_client is not None and not self.nats_client.is_closed,
            'consul': self.consul_client is not None,
            'ray': self.ray_initialized
        }
        return health
    
    async def register_agent(self, agent_id: str, agent_type: str):
        """Register an agent with Consul"""
        if self.consul_client:
            try:
                self.consul_client.agent.service.register(
                    name=f"ai-agent-{agent_type}",
                    service_id=agent_id,
                    tags=[agent_type, 'ai-agent'],
                    check={
                        'ttl': '30s',
                        'deregister_critical_service_after': '1m'
                    }
                )
                logger.info(f"Registered agent {agent_id} ({agent_type})")
            except Exception as e:
                logger.error(f"Failed to register agent {agent_id}: {e}")
    
    async def get_healthy_agents(self, agent_type: str = None) -> List[str]:
        """Get list of healthy agents from Consul"""
        if not self.consul_client:
            return []
        
        try:
            if agent_type:
                _, services = self.consul_client.health.service(
                    f"ai-agent-{agent_type}",
                    passing=True
                )
            else:
                _, services = self.consul_client.health.state('passing')
            
            agent_ids = [s['Service']['ID'] for s in services if 'ai-agent' in s['Service'].get('Tags', [])]
            return agent_ids
        except Exception as e:
            logger.error(f"Failed to get healthy agents: {e}")
            return []
    
    async def publish_message(self, subject: str, message: Dict[str, Any]):
        """Publish message to NATS"""
        if self.nats_client:
            try:
                import json
                await self.nats_client.publish(
                    subject,
                    json.dumps(message).encode()
                )
                logger.debug(f"Published message to {subject}")
            except Exception as e:
                logger.error(f"Failed to publish message: {e}")
    
    async def run(self):
        """Main orchestrator loop"""
        logger.info("Starting orchestrator main loop...")
        
        while True:
            try:
                # Health check
                health = await self.health_check()
                healthy_count = sum(health.values())
                logger.info(f"Health check: {healthy_count}/4 services healthy")
                
                # Get agent count
                agents = await self.get_healthy_agents()
                logger.info(f"Active agents: {len(agents)}/{self.agent_count}")
                
                # Publish heartbeat
                await self.publish_message('orchestrator.heartbeat', {
                    'status': 'running',
                    'health': health,
                    'agent_count': len(agents)
                })
                
                # Wait before next iteration
                await asyncio.sleep(10)
                
            except KeyboardInterrupt:
                logger.info("Shutting down orchestrator...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)
    
    async def shutdown(self):
        """Cleanup and shutdown"""
        logger.info("Shutting down orchestrator...")
        
        if self.nats_client and not self.nats_client.is_closed:
            await self.nats_client.close()
        
        if self.ray_initialized:
            import ray
            ray.shutdown()
        
        logger.info("✓ Orchestrator shutdown complete")


async def main():
    """Main entry point"""
    orchestrator = AgentOrchestrator()
    
    try:
        await orchestrator.initialize()
        await orchestrator.run()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
