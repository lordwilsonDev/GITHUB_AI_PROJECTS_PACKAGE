"""NATS JetStream Messaging for AI Agent Coordination

Demonstrates:
- At-least-once delivery with JetStream
- Message replay for agent recovery
- Request-reply patterns for synchronous coordination
- Consumer groups for load distribution
"""

import asyncio
import json
from nats.aio.client import Client as NATS
from nats.js import JetStreamContext


class AgentMessaging:
    """Handles inter-agent communication via NATS JetStream"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.nc = None
        self.js = None

    async def connect(self, nats_url: str = "nats://localhost:4222"):
        """Connect to NATS server and set up JetStream"""
        self.nc = NATS()
        await self.nc.connect(nats_url)
        self.js = self.nc.jetstream()

        # Create stream for agent coordination
        try:
            await self.js.add_stream(
                name="AGENT_COORDINATION",
                subjects=["agent.tasks.*", "agent.results.*", "agent.control.*"],
                retention="limits",  # Keep messages based on limits
                max_msgs=10000,
                max_age=86400,  # 24 hours
            )
        except Exception as e:
            print(f"Stream already exists or error: {e}")

    async def publish_task(self, task_data: dict):
        """Publish task to agent task queue with persistence"""
        subject = f"agent.tasks.{task_data.get('priority', 'normal')}"
        message = json.dumps(task_data).encode()
        
        # Publish with acknowledgment
        ack = await self.js.publish(subject, message)
        print(f"Published task, sequence: {ack.seq}")
        return ack.seq

    async def subscribe_to_tasks(self, callback):
        """Subscribe to tasks with durable consumer (survives restarts)"""
        # Create durable consumer
        consumer_config = {
            "durable_name": f"agent-{self.agent_id}",
            "ack_policy": "explicit",  # Manual acknowledgment
            "max_deliver": 3,  # Retry up to 3 times
        }

        psub = await self.js.pull_subscribe(
            "agent.tasks.*",
            durable=consumer_config["durable_name"],
            config=consumer_config
        )

        print(f"Agent {self.agent_id} subscribed to tasks")

        while True:
            try:
                # Fetch messages in batches
                msgs = await psub.fetch(batch=10, timeout=1)
                
                for msg in msgs:
                    try:
                        task_data = json.loads(msg.data.decode())
                        print(f"Received task: {task_data}")
                        
                        # Process task
                        await callback(task_data)
                        
                        # Acknowledge successful processing
                        await msg.ack()
                    except Exception as e:
                        print(f"Error processing task: {e}")
                        # Negative ack - will be redelivered
                        await msg.nak()
            except TimeoutError:
                # No messages available, continue polling
                await asyncio.sleep(0.1)

    async def request_help(self, request_data: dict, timeout: float = 5.0) -> dict:
        """Synchronous request-reply pattern for agent coordination"""
        subject = "agent.help.request"
        message = json.dumps(request_data).encode()
        
        try:
            # Native request-reply in NATS
            response = await self.nc.request(
                subject, 
                message, 
                timeout=timeout
            )
            return json.loads(response.data.decode())
        except asyncio.TimeoutError:
            return {"error": "No response from other agents"}

    async def respond_to_help_requests(self, handler):
        """Listen for help requests from other agents"""
        async def message_handler(msg):
            request_data = json.loads(msg.data.decode())
            print(f"Received help request: {request_data}")
            
            # Process request
            response = await handler(request_data)
            
            # Send reply
            await msg.respond(json.dumps(response).encode())

        await self.nc.subscribe("agent.help.request", cb=message_handler)
        print(f"Agent {self.agent_id} listening for help requests")

    async def replay_from_sequence(self, start_seq: int):
        """Replay messages from specific sequence (for recovery)"""
        # Create ephemeral consumer starting from sequence
        psub = await self.js.pull_subscribe(
            "agent.tasks.*",
            config={
                "deliver_policy": "by_start_sequence",
                "opt_start_seq": start_seq,
            }
        )

        print(f"Replaying messages from sequence {start_seq}")
        
        msgs = await psub.fetch(batch=100, timeout=2)
        for msg in msgs:
            task_data = json.loads(msg.data.decode())
            print(f"Replayed: {task_data}")
            await msg.ack()

    async def close(self):
        """Close NATS connection"""
        await self.nc.close()


async def example_agent():
    """Example agent using NATS messaging"""
    agent = AgentMessaging("agent-001")
    await agent.connect()

    # Publish a task
    await agent.publish_task({
        "task_id": "task-123",
        "type": "data_processing",
        "priority": "high"
    })

    # Request help from other agents
    response = await agent.request_help({
        "agent_id": "agent-001",
        "help_type": "resource_allocation"
    })
    print(f"Help response: {response}")

    await agent.close()


if __name__ == "__main__":
    asyncio.run(example_agent())
