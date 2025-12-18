#!/usr/bin/env python3
"""
Message Bus - Inter-agent communication system

Provides:
- NATS-based pub/sub messaging
- Request-reply patterns
- Message persistence and replay
- Agent discovery and registration
- Event streaming
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Standard message types for inter-agent communication."""
    TASK_REQUEST = "task.request"
    TASK_RESPONSE = "task.response"
    TASK_STATUS = "task.status"
    AGENT_REGISTER = "agent.register"
    AGENT_HEARTBEAT = "agent.heartbeat"
    AGENT_SHUTDOWN = "agent.shutdown"
    EVENT_NOTIFICATION = "event.notification"
    DATA_SYNC = "data.sync"
    ERROR_REPORT = "error.report"


@dataclass
class Message:
    """Standard message format for inter-agent communication."""
    message_type: str
    sender_id: str
    recipient_id: Optional[str] = None  # None for broadcast
    payload: Dict[str, Any] = None
    timestamp: str = None
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.payload is None:
            self.payload = {}
    
    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Create message from JSON string."""
        data = json.loads(json_str)
        return cls(**data)


class MessageBus:
    """
    Message bus for inter-agent communication.
    
    Features:
    - Pub/sub messaging
    - Request-reply patterns
    - Message persistence (NATS JetStream)
    - Agent discovery
    - Event streaming
    """
    
    def __init__(self, nats_url: str = "nats://localhost:4222"):
        self.nats_url = nats_url
        self.nc = None  # NATS connection
        self.js = None  # JetStream context
        self.subscriptions = {}
        self.registered_agents = {}
        self.message_handlers = {}
        self.connected = False
        
        logger.info(f"MessageBus initialized (NATS URL: {nats_url})")
    
    async def connect(self) -> bool:
        """Connect to NATS server."""
        try:
            import nats
            from nats.errors import TimeoutError
            
            logger.info(f"Connecting to NATS at {self.nats_url}...")
            
            self.nc = await nats.connect(
                self.nats_url,
                connect_timeout=5,
                max_reconnect_attempts=3
            )
            
            # Enable JetStream for persistence
            try:
                self.js = self.nc.jetstream()
                logger.info("✅ JetStream enabled (message persistence active)")
            except Exception as e:
                logger.warning(f"⚠️ JetStream not available: {e}")
                self.js = None
            
            self.connected = True
            logger.info("✅ Connected to NATS message bus")
            return True
            
        except ImportError:
            logger.warning("⚠️ NATS library not installed - using fallback mode")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"❌ Failed to connect to NATS: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from NATS server."""
        if self.nc and self.connected:
            await self.nc.close()
            self.connected = False
            logger.info("✅ Disconnected from NATS")
    
    async def publish(self, subject: str, message: Message) -> bool:
        """Publish a message to a subject."""
        if not self.connected:
            logger.warning(f"Not connected to NATS - message not sent: {subject}")
            return False
        
        try:
            await self.nc.publish(subject, message.to_json().encode())
            logger.debug(f"📤 Published to {subject}: {message.message_type}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to publish to {subject}: {e}")
            return False
    
    async def subscribe(self, subject: str, handler: Callable) -> bool:
        """Subscribe to a subject with a message handler."""
        if not self.connected:
            logger.warning(f"Not connected to NATS - cannot subscribe to {subject}")
            return False
        
        try:
            async def message_callback(msg):
                try:
                    message = Message.from_json(msg.data.decode())
                    await handler(message)
                except Exception as e:
                    logger.error(f"Error in message handler for {subject}: {e}")
            
            sub = await self.nc.subscribe(subject, cb=message_callback)
            self.subscriptions[subject] = sub
            logger.info(f"✅ Subscribed to {subject}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to subscribe to {subject}: {e}")
            return False
    
    async def request(self, subject: str, message: Message, timeout: float = 5.0) -> Optional[Message]:
        """Send a request and wait for a reply."""
        if not self.connected:
            logger.warning(f"Not connected to NATS - cannot send request to {subject}")
            return None
        
        try:
            response = await self.nc.request(
                subject,
                message.to_json().encode(),
                timeout=timeout
            )
            
            reply_message = Message.from_json(response.data.decode())
            logger.debug(f"📥 Received reply from {subject}")
            return reply_message
            
        except Exception as e:
            logger.error(f"❌ Request to {subject} failed: {e}")
            return None
    
    async def reply(self, original_message: Message, reply_message: Message):
        """Reply to a message."""
        if not self.connected or not original_message.reply_to:
            return False
        
        try:
            await self.nc.publish(
                original_message.reply_to,
                reply_message.to_json().encode()
            )
            logger.debug(f"📤 Sent reply to {original_message.reply_to}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send reply: {e}")
            return False
    
    async def register_agent(self, agent_id: str, capabilities: List[str], metadata: Dict = None):
        """Register an agent with the message bus."""
        registration = {
            'agent_id': agent_id,
            'capabilities': capabilities,
            'metadata': metadata or {},
            'registered_at': datetime.now().isoformat()
        }
        
        self.registered_agents[agent_id] = registration
        
        # Publish registration event
        message = Message(
            message_type=MessageType.AGENT_REGISTER.value,
            sender_id=agent_id,
            payload=registration
        )
        
        await self.publish("agents.register", message)
        logger.info(f"✅ Agent registered: {agent_id}")
    
    async def send_heartbeat(self, agent_id: str, status: Dict = None):
        """Send agent heartbeat."""
        message = Message(
            message_type=MessageType.AGENT_HEARTBEAT.value,
            sender_id=agent_id,
            payload={
                'status': status or {},
                'timestamp': datetime.now().isoformat()
            }
        )
        
        await self.publish(f"agents.heartbeat.{agent_id}", message)
    
    async def broadcast_event(self, event_type: str, sender_id: str, event_data: Dict):
        """Broadcast an event to all agents."""
        message = Message(
            message_type=MessageType.EVENT_NOTIFICATION.value,
            sender_id=sender_id,
            payload={
                'event_type': event_type,
                'event_data': event_data
            }
        )
        
        await self.publish("events.broadcast", message)
        logger.info(f"📢 Broadcast event: {event_type} from {sender_id}")
    
    def get_registered_agents(self) -> Dict[str, Dict]:
        """Get all registered agents."""
        return self.registered_agents.copy()
    
    async def create_stream(self, stream_name: str, subjects: List[str]) -> bool:
        """Create a JetStream stream for message persistence."""
        if not self.js:
            logger.warning("JetStream not available - cannot create stream")
            return False
        
        try:
            await self.js.add_stream(
                name=stream_name,
                subjects=subjects
            )
            logger.info(f"✅ Created stream: {stream_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create stream {stream_name}: {e}")
            return False


class FallbackMessageBus:
    """
    Fallback message bus for when NATS is not available.
    Uses in-memory pub/sub for local testing.
    """
    
    def __init__(self):
        self.subscribers = {}
        self.registered_agents = {}
        self.connected = True
        logger.info("Using fallback in-memory message bus")
    
    async def connect(self) -> bool:
        self.connected = True
        return True
    
    async def disconnect(self):
        self.connected = False
    
    async def publish(self, subject: str, message: Message) -> bool:
        """Publish message to in-memory subscribers."""
        if subject in self.subscribers:
            for handler in self.subscribers[subject]:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"Error in fallback handler: {e}")
        return True
    
    async def subscribe(self, subject: str, handler: Callable) -> bool:
        """Subscribe to subject."""
        if subject not in self.subscribers:
            self.subscribers[subject] = []
        self.subscribers[subject].append(handler)
        logger.info(f"✅ Subscribed to {subject} (fallback mode)")
        return True
    
    async def request(self, subject: str, message: Message, timeout: float = 5.0) -> Optional[Message]:
        """Send request (not implemented in fallback)."""
        logger.warning("Request-reply not available in fallback mode")
        return None
    
    async def register_agent(self, agent_id: str, capabilities: List[str], metadata: Dict = None):
        """Register agent."""
        self.registered_agents[agent_id] = {
            'agent_id': agent_id,
            'capabilities': capabilities,
            'metadata': metadata or {}
        }
        logger.info(f"✅ Agent registered (fallback): {agent_id}")
    
    async def send_heartbeat(self, agent_id: str, status: Dict = None):
        """Send heartbeat (no-op in fallback)."""
        pass
    
    async def broadcast_event(self, event_type: str, sender_id: str, event_data: Dict):
        """Broadcast event."""
        message = Message(
            message_type=MessageType.EVENT_NOTIFICATION.value,
            sender_id=sender_id,
            payload={'event_type': event_type, 'event_data': event_data}
        )
        await self.publish("events.broadcast", message)
    
    def get_registered_agents(self) -> Dict[str, Dict]:
        return self.registered_agents.copy()


async def create_message_bus(nats_url: str = "nats://localhost:4222") -> MessageBus:
    """
    Factory function to create and connect message bus.
    Falls back to in-memory bus if NATS is not available.
    """
    bus = MessageBus(nats_url)
    connected = await bus.connect()
    
    if not connected:
        logger.warning("Using fallback message bus")
        return FallbackMessageBus()
    
    return bus


# Example usage and testing
async def test_message_bus():
    """Test the message bus."""
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("Testing Message Bus")
    print("="*60)
    
    # Create message bus
    print("\n[Test 1] Creating message bus...")
    bus = await create_message_bus()
    
    # Register agents
    print("\n[Test 2] Registering agents...")
    await bus.register_agent(
        "agent_1",
        ["analysis", "writing"],
        {"version": "1.0", "location": "local"}
    )
    await bus.register_agent(
        "agent_2",
        ["research", "monitoring"],
        {"version": "1.0", "location": "local"}
    )
    
    print(f"Registered agents: {list(bus.get_registered_agents().keys())}")
    
    # Test pub/sub
    print("\n[Test 3] Testing pub/sub...")
    
    received_messages = []
    
    async def message_handler(message: Message):
        received_messages.append(message)
        print(f"  Received: {message.message_type} from {message.sender_id}")
    
    await bus.subscribe("test.messages", message_handler)
    
    # Publish some messages
    for i in range(3):
        message = Message(
            message_type=MessageType.TASK_REQUEST.value,
            sender_id="agent_1",
            recipient_id="agent_2",
            payload={"task_id": f"task_{i}", "data": f"test data {i}"}
        )
        await bus.publish("test.messages", message)
    
    # Wait for messages to be processed
    await asyncio.sleep(0.5)
    print(f"\n  Total messages received: {len(received_messages)}")
    
    # Test broadcast
    print("\n[Test 4] Testing broadcast...")
    await bus.broadcast_event(
        "system.startup",
        "orchestrator",
        {"status": "ready", "agents": 2}
    )
    
    # Test heartbeat
    print("\n[Test 5] Testing heartbeat...")
    await bus.send_heartbeat(
        "agent_1",
        {"status": "active", "tasks_completed": 10}
    )
    
    # Cleanup
    print("\n[Cleanup] Disconnecting...")
    await bus.disconnect()
    
    print("\n" + "="*60)
    print("Message Bus Tests Complete")
    print("="*60)


if __name__ == '__main__':
    asyncio.run(test_message_bus())
