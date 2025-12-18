#!/usr/bin/env python3
"""
Test Workflow - Simple test to verify the orchestration system works

This script:
1. Connects to all services (Temporal, NATS, Consul, Ray)
2. Spawns test agents
3. Executes a simple workflow
4. Verifies results
"""

import asyncio
import json
import logging
import time
from typing import List, Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TestWorkflow')


class WorkflowTester:
    """Test the orchestration system"""
    
    def __init__(self):
        self.nats_url = 'nats://localhost:4222'
        self.consul_host = 'localhost'
        self.consul_port = 8500
        
        self.nats_client = None
        self.consul_client = None
        self.test_results = []
        
    async def test_nats_connection(self) -> bool:
        """Test NATS connectivity"""
        logger.info("Testing NATS connection...")
        try:
            import nats
            self.nats_client = await nats.connect(self.nats_url)
            logger.info("✓ NATS connection successful")
            return True
        except Exception as e:
            logger.error(f"✗ NATS connection failed: {e}")
            return False
    
    async def test_consul_connection(self) -> bool:
        """Test Consul connectivity"""
        logger.info("Testing Consul connection...")
        try:
            import consul
            self.consul_client = consul.Consul(
                host=self.consul_host,
                port=self.consul_port
            )
            # Try to get services
            services = self.consul_client.agent.services()
            logger.info(f"✓ Consul connection successful (Services: {len(services)})")
            return True
        except Exception as e:
            logger.error(f"✗ Consul connection failed: {e}")
            return False
    
    async def test_temporal_connection(self) -> bool:
        """Test Temporal connectivity"""
        logger.info("Testing Temporal connection...")
        try:
            from temporalio.client import Client
            client = await Client.connect('localhost:7233')
            logger.info("✓ Temporal connection successful")
            return True
        except Exception as e:
            logger.error(f"✗ Temporal connection failed: {e}")
            logger.info("  Note: Temporal may take 30-60 seconds to start")
            return False
    
    async def test_ray_connection(self) -> bool:
        """Test Ray connectivity"""
        logger.info("Testing Ray connection...")
        try:
            import ray
            ray.init(address='ray://localhost:6379', ignore_reinit_error=True)
            logger.info("✓ Ray connection successful")
            ray.shutdown()
            return True
        except Exception as e:
            logger.error(f"✗ Ray connection failed: {e}")
            return False
    
    async def test_message_publish_subscribe(self) -> bool:
        """Test NATS pub/sub"""
        logger.info("Testing NATS pub/sub...")
        
        if not self.nats_client:
            logger.error("✗ NATS client not connected")
            return False
        
        try:
            received_messages = []
            
            # Subscribe
            async def message_handler(msg):
                data = json.loads(msg.data.decode())
                received_messages.append(data)
                logger.info(f"  Received: {data}")
            
            await self.nats_client.subscribe('test.workflow', cb=message_handler)
            
            # Publish test messages
            for i in range(3):
                test_msg = {'test_id': i, 'message': f'Test message {i}'}
                await self.nats_client.publish(
                    'test.workflow',
                    json.dumps(test_msg).encode()
                )
                logger.info(f"  Published: {test_msg}")
            
            # Wait for messages
            await asyncio.sleep(1)
            
            if len(received_messages) == 3:
                logger.info(f"✓ NATS pub/sub test passed ({len(received_messages)} messages)")
                return True
            else:
                logger.error(f"✗ NATS pub/sub test failed (expected 3, got {len(received_messages)})")
                return False
                
        except Exception as e:
            logger.error(f"✗ NATS pub/sub test failed: {e}")
            return False
    
    async def test_agent_task_execution(self) -> bool:
        """Test sending task to agent and receiving response"""
        logger.info("Testing agent task execution...")
        
        if not self.nats_client:
            logger.error("✗ NATS client not connected")
            return False
        
        try:
            responses = []
            
            # Subscribe to responses
            async def response_handler(msg):
                data = json.loads(msg.data.decode())
                responses.append(data)
                logger.info(f"  Received response: {data.get('status')}")
            
            await self.nats_client.subscribe('agent.test.response', cb=response_handler)
            
            # Send test task
            task = {
                'type': 'test_task',
                'task_id': 'test-001',
                'data': 'Test data',
                'reply_to': 'agent.test.response'
            }
            
            logger.info("  Sending test task to agents...")
            await self.nats_client.publish(
                'agent.processing.request',
                json.dumps(task).encode()
            )
            
            # Wait for response
            await asyncio.sleep(2)
            
            if len(responses) > 0:
                logger.info(f"✓ Agent task execution test passed ({len(responses)} responses)")
                return True
            else:
                logger.warning("⚠ No agent responses received (agents may not be running)")
                return False
                
        except Exception as e:
            logger.error(f"✗ Agent task execution test failed: {e}")
            return False
    
    async def test_simple_workflow(self) -> bool:
        """Test a simple multi-step workflow"""
        logger.info("Testing simple workflow...")
        
        try:
            # Step 1: Research
            logger.info("  Step 1: Research phase")
            research_task = {
                'type': 'research',
                'task_id': 'workflow-research-001',
                'query': 'AI trends 2025',
                'reply_to': 'workflow.research.response'
            }
            
            research_responses = []
            
            async def research_handler(msg):
                data = json.loads(msg.data.decode())
                research_responses.append(data)
            
            await self.nats_client.subscribe('workflow.research.response', cb=research_handler)
            await self.nats_client.publish('agent.research.request', json.dumps(research_task).encode())
            await asyncio.sleep(1)
            
            # Step 2: Processing
            logger.info("  Step 2: Processing phase")
            processing_task = {
                'type': 'processing',
                'task_id': 'workflow-processing-001',
                'data': 'Process research results',
                'reply_to': 'workflow.processing.response'
            }
            
            processing_responses = []
            
            async def processing_handler(msg):
                data = json.loads(msg.data.decode())
                processing_responses.append(data)
            
            await self.nats_client.subscribe('workflow.processing.response', cb=processing_handler)
            await self.nats_client.publish('agent.processing.request', json.dumps(processing_task).encode())
            await asyncio.sleep(1)
            
            # Step 3: Analysis
            logger.info("  Step 3: Analysis phase")
            analysis_task = {
                'type': 'analysis',
                'task_id': 'workflow-analysis-001',
                'data': 'Analyze processed data',
                'reply_to': 'workflow.analysis.response'
            }
            
            analysis_responses = []
            
            async def analysis_handler(msg):
                data = json.loads(msg.data.decode())
                analysis_responses.append(data)
            
            await self.nats_client.subscribe('workflow.analysis.response', cb=analysis_handler)
            await self.nats_client.publish('agent.analysis.request', json.dumps(analysis_task).encode())
            await asyncio.sleep(1)
            
            # Check results
            total_responses = len(research_responses) + len(processing_responses) + len(analysis_responses)
            
            if total_responses > 0:
                logger.info(f"✓ Simple workflow test passed ({total_responses} total responses)")
                logger.info(f"    Research: {len(research_responses)}, Processing: {len(processing_responses)}, Analysis: {len(analysis_responses)}")
                return True
            else:
                logger.warning("⚠ Workflow completed but no agent responses (agents may not be running)")
                return False
                
        except Exception as e:
            logger.error(f"✗ Simple workflow test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        logger.info("="*60)
        logger.info("AI Agent Orchestration System - Test Suite")
        logger.info("="*60)
        logger.info("")
        
        tests = [
            ('NATS Connection', self.test_nats_connection),
            ('Consul Connection', self.test_consul_connection),
            ('Temporal Connection', self.test_temporal_connection),
            ('Ray Connection', self.test_ray_connection),
            ('NATS Pub/Sub', self.test_message_publish_subscribe),
            ('Agent Task Execution', self.test_agent_task_execution),
            ('Simple Workflow', self.test_simple_workflow),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            logger.info("")
            logger.info("-" * 60)
            try:
                result = await test_func()
                results[test_name] = result
            except Exception as e:
                logger.error(f"Test '{test_name}' crashed: {e}")
                results[test_name] = False
            
            await asyncio.sleep(0.5)
        
        # Summary
        logger.info("")
        logger.info("="*60)
        logger.info("Test Summary")
        logger.info("="*60)
        
        passed = sum(1 for r in results.values() if r)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            logger.info(f"{status:8} - {test_name}")
        
        logger.info("")
        logger.info(f"Results: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("✓ All tests passed! System is ready.")
        elif passed >= total * 0.7:
            logger.info("⚠ Most tests passed. System is partially ready.")
        else:
            logger.info("✗ Many tests failed. Check service status.")
        
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. If services failed: docker-compose up -d")
        logger.info("2. If agents failed: python simple_agent.py <type>")
        logger.info("3. Deploy full 620-agent system")
        logger.info("")
        
        # Cleanup
        if self.nats_client and not self.nats_client.is_closed:
            await self.nats_client.close()


async def main():
    """Main entry point"""
    tester = WorkflowTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
