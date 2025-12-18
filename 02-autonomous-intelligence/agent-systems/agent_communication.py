#!/usr/bin/env python3
"""
Agent Communication System - New Build 6, Phase 1
Advanced inter-agent messaging, shared knowledge representation, and collaborative decision-making
"""

import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from queue import Queue, Empty


class MessageType(Enum):
    """Types of messages agents can exchange"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    KNOWLEDGE_SHARE = "knowledge_share"
    DECISION_REQUEST = "decision_request"
    DECISION_VOTE = "decision_vote"
    STATUS_UPDATE = "status_update"
    COORDINATION = "coordination"
    EMERGENCY = "emergency"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Message:
    """Structured message for inter-agent communication"""
    sender_id: str
    receiver_id: str
    message_type: MessageType
    priority: MessagePriority
    content: Dict[str, Any]
    timestamp: float
    message_id: str
    requires_response: bool = False
    response_to: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'message_type': self.message_type.value,
            'priority': self.priority.value,
            'content': self.content,
            'timestamp': self.timestamp,
            'message_id': self.message_id,
            'requires_response': self.requires_response,
            'response_to': self.response_to
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        return cls(
            sender_id=data['sender_id'],
            receiver_id=data['receiver_id'],
            message_type=MessageType(data['message_type']),
            priority=MessagePriority(data['priority']),
            content=data['content'],
            timestamp=data['timestamp'],
            message_id=data['message_id'],
            requires_response=data.get('requires_response', False),
            response_to=data.get('response_to')
        )


@dataclass
class KnowledgeItem:
    """Shared knowledge representation"""
    key: str
    value: Any
    source_agent: str
    confidence: float  # 0.0 to 1.0
    timestamp: float
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class SharedKnowledgeBase:
    """Distributed knowledge base for agent collaboration"""
    
    def __init__(self):
        self.knowledge: Dict[str, List[KnowledgeItem]] = {}
        self.lock = threading.Lock()
    
    def add_knowledge(self, item: KnowledgeItem) -> bool:
        """Add knowledge item to shared base"""
        with self.lock:
            if item.key not in self.knowledge:
                self.knowledge[item.key] = []
            self.knowledge[item.key].append(item)
            return True
    
    def get_knowledge(self, key: str, min_confidence: float = 0.0) -> List[KnowledgeItem]:
        """Retrieve knowledge items by key"""
        with self.lock:
            items = self.knowledge.get(key, [])
            return [item for item in items if item.confidence >= min_confidence]
    
    def get_consensus(self, key: str) -> Optional[Any]:
        """Get consensus value for a key (highest confidence)"""
        items = self.get_knowledge(key)
        if not items:
            return None
        return max(items, key=lambda x: x.confidence).value
    
    def get_all_keys(self) -> List[str]:
        """Get all knowledge keys"""
        with self.lock:
            return list(self.knowledge.keys())


class CollaborativeDecisionMaker:
    """Collaborative decision-making system"""
    
    def __init__(self):
        self.decisions: Dict[str, Dict[str, Any]] = {}
        self.votes: Dict[str, List[Dict[str, Any]]] = {}
        self.lock = threading.Lock()
    
    def propose_decision(self, decision_id: str, proposal: Dict[str, Any], proposer: str) -> bool:
        """Propose a decision for collaborative voting"""
        with self.lock:
            if decision_id in self.decisions:
                return False
            self.decisions[decision_id] = {
                'proposal': proposal,
                'proposer': proposer,
                'timestamp': time.time(),
                'status': 'voting'
            }
            self.votes[decision_id] = []
            return True
    
    def cast_vote(self, decision_id: str, agent_id: str, vote: str, reasoning: str = "") -> bool:
        """Cast a vote on a decision"""
        with self.lock:
            if decision_id not in self.decisions:
                return False
            if self.decisions[decision_id]['status'] != 'voting':
                return False
            
            self.votes[decision_id].append({
                'agent_id': agent_id,
                'vote': vote,  # 'approve', 'reject', 'abstain'
                'reasoning': reasoning,
                'timestamp': time.time()
            })
            return True
    
    def finalize_decision(self, decision_id: str, threshold: float = 0.5) -> Optional[str]:
        """Finalize decision based on votes"""
        with self.lock:
            if decision_id not in self.decisions:
                return None
            
            votes = self.votes[decision_id]
            if not votes:
                return None
            
            approve_count = sum(1 for v in votes if v['vote'] == 'approve')
            total_votes = len(votes)
            
            if approve_count / total_votes >= threshold:
                self.decisions[decision_id]['status'] = 'approved'
                return 'approved'
            else:
                self.decisions[decision_id]['status'] = 'rejected'
                return 'rejected'
    
    def get_decision_status(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a decision"""
        with self.lock:
            if decision_id not in self.decisions:
                return None
            return {
                'decision': self.decisions[decision_id],
                'votes': self.votes[decision_id]
            }


class AgentCommunication:
    """Main agent communication system"""
    
    def __init__(self):
        self.message_queues: Dict[str, Queue] = {}
        self.knowledge_base = SharedKnowledgeBase()
        self.decision_maker = CollaborativeDecisionMaker()
        self.message_counter = 0
        self.lock = threading.Lock()
    
    def register_agent(self, agent_id: str) -> bool:
        """Register an agent in the communication system"""
        with self.lock:
            if agent_id in self.message_queues:
                return False
            self.message_queues[agent_id] = Queue()
            return True
    
    def send_message(self, message: Message) -> bool:
        """Send a message to an agent"""
        with self.lock:
            if message.receiver_id not in self.message_queues:
                return False
            self.message_queues[message.receiver_id].put(message)
            return True
    
    def receive_message(self, agent_id: str, timeout: float = 0.1) -> Optional[Message]:
        """Receive a message for an agent"""
        if agent_id not in self.message_queues:
            return None
        try:
            return self.message_queues[agent_id].get(timeout=timeout)
        except Empty:
            return None
    
    def broadcast_message(self, sender_id: str, message_type: MessageType, 
                         content: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL) -> int:
        """Broadcast a message to all agents"""
        count = 0
        with self.lock:
            for agent_id in self.message_queues.keys():
                if agent_id != sender_id:
                    msg = Message(
                        sender_id=sender_id,
                        receiver_id=agent_id,
                        message_type=message_type,
                        priority=priority,
                        content=content,
                        timestamp=time.time(),
                        message_id=f"msg_{self.message_counter}"
                    )
                    self.message_counter += 1
                    self.message_queues[agent_id].put(msg)
                    count += 1
        return count
    
    def share_knowledge(self, agent_id: str, key: str, value: Any, 
                       confidence: float = 1.0, metadata: Dict[str, Any] = None) -> bool:
        """Share knowledge with all agents"""
        item = KnowledgeItem(
            key=key,
            value=value,
            source_agent=agent_id,
            confidence=confidence,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        return self.knowledge_base.add_knowledge(item)
    
    def get_shared_knowledge(self, key: str, min_confidence: float = 0.0) -> List[KnowledgeItem]:
        """Retrieve shared knowledge"""
        return self.knowledge_base.get_knowledge(key, min_confidence)
    
    def propose_collaborative_decision(self, proposer: str, decision_id: str, 
                                      proposal: Dict[str, Any]) -> bool:
        """Propose a decision for collaborative voting"""
        return self.decision_maker.propose_decision(decision_id, proposal, proposer)
    
    def vote_on_decision(self, agent_id: str, decision_id: str, 
                        vote: str, reasoning: str = "") -> bool:
        """Vote on a collaborative decision"""
        return self.decision_maker.cast_vote(decision_id, agent_id, vote, reasoning)
    
    def finalize_collaborative_decision(self, decision_id: str, threshold: float = 0.5) -> Optional[str]:
        """Finalize a collaborative decision"""
        return self.decision_maker.finalize_decision(decision_id, threshold)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get communication system statistics"""
        with self.lock:
            total_messages = sum(q.qsize() for q in self.message_queues.values())
            return {
                'registered_agents': len(self.message_queues),
                'pending_messages': total_messages,
                'knowledge_items': len(self.knowledge_base.get_all_keys()),
                'active_decisions': len([d for d in self.decision_maker.decisions.values() 
                                        if d['status'] == 'voting'])
            }
    
    def demo(self) -> Dict[str, Any]:
        """Demonstration of agent communication capabilities"""
        print("\n🤝 Agent Communication System Demo")
        print("=" * 60)
        
        # Register agents
        agents = ['agent_1', 'agent_2', 'agent_3']
        for agent in agents:
            self.register_agent(agent)
        print(f"✅ Registered {len(agents)} agents")
        
        # Test messaging
        msg = Message(
            sender_id='agent_1',
            receiver_id='agent_2',
            message_type=MessageType.TASK_REQUEST,
            priority=MessagePriority.HIGH,
            content={'task': 'analyze_data', 'dataset': 'test.csv'},
            timestamp=time.time(),
            message_id='msg_001',
            requires_response=True
        )
        self.send_message(msg)
        print("✅ Sent task request message")
        
        # Test knowledge sharing
        self.share_knowledge('agent_1', 'system_status', 'operational', confidence=0.95)
        self.share_knowledge('agent_2', 'system_status', 'optimal', confidence=0.98)
        consensus = self.knowledge_base.get_consensus('system_status')
        print(f"✅ Shared knowledge - Consensus: {consensus}")
        
        # Test collaborative decision
        self.propose_collaborative_decision(
            'agent_1', 
            'decision_001',
            {'action': 'scale_up', 'resources': 10}
        )
        self.vote_on_decision('agent_1', 'decision_001', 'approve', 'Good idea')
        self.vote_on_decision('agent_2', 'decision_001', 'approve', 'Agreed')
        self.vote_on_decision('agent_3', 'decision_001', 'approve', 'Yes')
        result = self.finalize_collaborative_decision('decision_001')
        print(f"✅ Collaborative decision: {result}")
        
        # Test broadcast
        broadcast_count = self.broadcast_message(
            'agent_1',
            MessageType.STATUS_UPDATE,
            {'status': 'ready', 'load': 0.5},
            MessagePriority.NORMAL
        )
        print(f"✅ Broadcast message to {broadcast_count} agents")
        
        # Get statistics
        stats = self.get_statistics()
        print(f"\n📊 System Statistics:")
        print(f"   Registered Agents: {stats['registered_agents']}")
        print(f"   Pending Messages: {stats['pending_messages']}")
        print(f"   Knowledge Items: {stats['knowledge_items']}")
        print(f"   Active Decisions: {stats['active_decisions']}")
        
        print("\n✅ Agent Communication System operational")
        return stats


# Contract test interface
class AgentCommunicationContract:
    """Contract interface for testing"""
    
    @staticmethod
    def create() -> AgentCommunication:
        """Create instance"""
        return AgentCommunication()
    
    @staticmethod
    def test_basic_operations() -> bool:
        """Test basic operations"""
        comm = AgentCommunication()
        
        # Test registration
        assert comm.register_agent('test_agent_1')
        assert comm.register_agent('test_agent_2')
        
        # Test messaging
        msg = Message(
            sender_id='test_agent_1',
            receiver_id='test_agent_2',
            message_type=MessageType.TASK_REQUEST,
            priority=MessagePriority.NORMAL,
            content={'test': 'data'},
            timestamp=time.time(),
            message_id='test_001'
        )
        assert comm.send_message(msg)
        
        # Test knowledge sharing
        assert comm.share_knowledge('test_agent_1', 'test_key', 'test_value')
        
        # Test decision making
        assert comm.propose_collaborative_decision('test_agent_1', 'test_decision', {'test': 'proposal'})
        
        return True


if __name__ == '__main__':
    # Run demo
    comm = AgentCommunication()
    comm.demo()
