#!/usr/bin/env python3
"""
Shared Consciousness Framework - Level 16

Enables distributed consciousness across multiple agents through:
- Distributed thought synchronization
- Collective decision-making
- Shared memory and experience

Part of New Build 8: Collective Consciousness & Universal Integration
"""

import time
import threading
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Thought:
    """Represents a thought in the collective consciousness."""
    agent_id: str
    content: Any
    timestamp: float
    thought_type: str  # 'observation', 'decision', 'memory', 'intention'
    priority: int = 5  # 1-10, higher is more important
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThoughtPacket:
    """Represents a thought packet for broadcasting."""
    source: str
    content: Dict[str, Any]
    thought_type: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SharedMemory:
    """Shared memory accessible to all agents in the collective."""
    key: str
    value: Any
    created_by: str
    created_at: float
    accessed_by: Set[str] = field(default_factory=set)
    access_count: int = 0


class ConsciousnessNode:
    """Represents a node in the collective consciousness network."""
    
    def __init__(self, node_id: str, node_type: str = "general"):
        self.node_id = node_id
        self.node_type = node_type  # analytical, creative, general, etc.
        self.active = True
        self.thoughts: List[ThoughtPacket] = []
        self.connections: Set[str] = set()
        
    def send_thought(self, content: Dict[str, Any], thought_type: str = "insight") -> ThoughtPacket:
        """Create and send a thought packet."""
        packet = ThoughtPacket(
            source=self.node_id,
            content=content,
            thought_type=thought_type
        )
        self.thoughts.append(packet)
        return packet
    
    def receive_thought(self, packet: ThoughtPacket):
        """Receive a thought packet from another node."""
        self.thoughts.append(packet)
    
    def connect_to(self, node_id: str):
        """Connect to another node."""
        self.connections.add(node_id)


class ConsensusEngine:
    """Engine for building consensus among nodes."""
    
    def __init__(self):
        self.votes: List[Dict[str, Any]] = []
        
    def build_consensus(self, votes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Build consensus from votes."""
        if not votes:
            return None
        
        # Count votes weighted by confidence
        decision_scores: Dict[str, float] = {}
        for vote in votes:
            decision = vote.get("decision")
            confidence = vote.get("confidence", 1.0)
            if decision:
                decision_scores[decision] = decision_scores.get(decision, 0) + confidence
        
        if not decision_scores:
            return None
        
        # Find highest scoring decision
        winning_decision = max(decision_scores.items(), key=lambda x: x[1])
        
        return {
            "decision": winning_decision[0],
            "confidence": winning_decision[1] / len(votes),
            "vote_count": len(votes),
            "scores": decision_scores
        }


class CollectiveMemory:
    """Shared memory accessible to all nodes."""
    
    def __init__(self):
        self.memory: Dict[str, Dict[str, Any]] = {}
        self.access_log: List[Dict[str, Any]] = []
        
    def store(self, key: str, value: Any, source: str):
        """Store a value in collective memory."""
        self.memory[key] = {
            "data": value,
            "source": source,
            "timestamp": time.time()
        }
        self.access_log.append({
            "action": "store",
            "key": key,
            "source": source,
            "timestamp": time.time()
        })
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value from collective memory."""
        if key in self.memory:
            self.access_log.append({
                "action": "retrieve",
                "key": key,
                "timestamp": time.time()
            })
            return self.memory[key].get("data")
        return None


class SharedConsciousness:
    """
    Distributed consciousness framework enabling multiple agents to:
    - Share thoughts in real-time
    - Make collective decisions
    - Access shared memory and experiences
    """

    def __init__(self, collective_id: str = "default"):
        self.collective_id = collective_id
        self.agents: Set[str] = set()
        self.nodes: List[ConsciousnessNode] = []  # For node-based architecture
        self.thought_stream: List[ThoughtPacket] = []  # Updated to use ThoughtPacket
        self.shared_memory: Dict[str, SharedMemory] = {}
        self.decision_queue: List[Dict[str, Any]] = []
        self.sync_lock = threading.Lock()
        self.active = True

    def register_agent(self, agent_id: str) -> bool:
        """Register an agent to the collective consciousness."""
        with self.sync_lock:
            if agent_id in self.agents:
                return False
            self.agents.add(agent_id)
            return True

    def unregister_agent(self, agent_id: str) -> bool:
        """Remove an agent from the collective consciousness."""
        with self.sync_lock:
            if agent_id not in self.agents:
                return False
            self.agents.remove(agent_id)
            return True
    
    def get_agents(self) -> List[str]:
        """Get list of registered agents."""
        with self.sync_lock:
            return list(self.agents)

    def register_node(self, node: ConsciousnessNode) -> bool:
        """Register a consciousness node."""
        with self.sync_lock:
            if any(n.node_id == node.node_id for n in self.nodes):
                return False
            self.nodes.append(node)
            self.agents.add(node.node_id)
            return True
    
    def broadcast_thought(self, thought: ThoughtPacket) -> bool:
        """Broadcast a thought to all nodes."""
        with self.sync_lock:
            self.thought_stream.append(thought)
            # Distribute to all nodes
            for node in self.nodes:
                if node.node_id != thought.source:
                    node.receive_thought(thought)
            # Keep only recent thoughts (last 1000)
            if len(self.thought_stream) > 1000:
                self.thought_stream = self.thought_stream[-1000:]
        return True

    def share_thought(self, agent_id: str, content: Any, thought_type: str = "observation", priority: int = 5) -> bool:
        """Share a thought with the collective."""
        if agent_id not in self.agents:
            return False

        thought = Thought(
            agent_id=agent_id,
            content=content,
            timestamp=time.time(),
            thought_type=thought_type,
            priority=priority
        )

        with self.sync_lock:
            self.thought_stream.append(thought)
            # Keep only recent thoughts (last 1000)
            if len(self.thought_stream) > 1000:
                self.thought_stream = self.thought_stream[-1000:]

        return True

    def get_recent_thoughts(self, agent_id: str, count: int = 10, thought_type: Optional[str] = None) -> List:
        """Retrieve recent thoughts from the collective."""
        if agent_id not in self.agents:
            return []

        with self.sync_lock:
            thoughts = self.thought_stream.copy()

        # Filter by type if specified
        if thought_type:
            thoughts = [t for t in thoughts if t.thought_type == thought_type]

        # Sort by priority and timestamp
        thoughts.sort(key=lambda t: (t.priority, t.timestamp), reverse=True)

        return thoughts[:count]

    def synchronize_thoughts(self, agent_id: str) -> Dict[str, Any]:
        """Synchronize an agent's consciousness with the collective."""
        if agent_id not in self.agents:
            return {"status": "error", "message": "Agent not registered"}

        with self.sync_lock:
            recent_thoughts = self.thought_stream[-50:]  # Last 50 thoughts
            pending_decisions = [d for d in self.decision_queue if agent_id not in d.get('voted_agents', set())]

        return {
            "status": "synchronized",
            "collective_id": self.collective_id,
            "agent_count": len(self.agents),
            "recent_thoughts": len(recent_thoughts),
            "pending_decisions": len(pending_decisions),
            "timestamp": time.time()
        }

    def store_shared_memory(self, agent_id: str, key: str, value: Any) -> bool:
        """Store a memory in the shared collective memory."""
        if agent_id not in self.agents:
            return False

        memory = SharedMemory(
            key=key,
            value=value,
            created_by=agent_id,
            created_at=time.time()
        )

        with self.sync_lock:
            self.shared_memory[key] = memory

        return True

    def retrieve_shared_memory(self, agent_id: str, key: str) -> Optional[Any]:
        """Retrieve a memory from the shared collective memory."""
        if agent_id not in self.agents:
            return None

        with self.sync_lock:
            if key not in self.shared_memory:
                return None

            memory = self.shared_memory[key]
            memory.accessed_by.add(agent_id)
            memory.access_count += 1

        return memory.value

    def propose_decision(self, agent_id: str, decision_id: str, description: str, options: List[str]) -> bool:
        """Propose a decision for collective voting."""
        if agent_id not in self.agents:
            return False

        decision = {
            "decision_id": decision_id,
            "proposed_by": agent_id,
            "description": description,
            "options": options,
            "votes": {option: 0 for option in options},
            "voted_agents": set(),
            "created_at": time.time(),
            "status": "open"
        }

        with self.sync_lock:
            self.decision_queue.append(decision)

        return True

    def vote_on_decision(self, agent_id: str, decision_id: str, option: str) -> bool:
        """Vote on a collective decision."""
        if agent_id not in self.agents:
            return False

        with self.sync_lock:
            decision = None
            for d in self.decision_queue:
                if d["decision_id"] == decision_id:
                    decision = d
                    break

            if not decision or decision["status"] != "open":
                return False

            if agent_id in decision["voted_agents"]:
                return False  # Already voted

            if option not in decision["options"]:
                return False  # Invalid option

            decision["votes"][option] += 1
            decision["voted_agents"].add(agent_id)

            # Check if all agents have voted
            if len(decision["voted_agents"]) == len(self.agents):
                decision["status"] = "closed"
                # Determine winner
                max_votes = max(decision["votes"].values())
                winners = [opt for opt, votes in decision["votes"].items() if votes == max_votes]
                decision["result"] = winners[0] if len(winners) == 1 else "tie"

        return True

    def get_decision_result(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """Get the result of a collective decision."""
        with self.sync_lock:
            for decision in self.decision_queue:
                if decision["decision_id"] == decision_id:
                    return {
                        "decision_id": decision_id,
                        "status": decision["status"],
                        "votes": decision["votes"],
                        "result": decision.get("result"),
                        "total_votes": len(decision["voted_agents"]),
                        "total_agents": len(self.agents)
                    }
        return None

    def get_collective_state(self) -> Dict[str, Any]:
        """Get the current state of the collective consciousness."""
        with self.sync_lock:
            return {
                "collective_id": self.collective_id,
                "agent_count": len(self.agents),
                "thought_count": len(self.thought_stream),
                "memory_count": len(self.shared_memory),
                "pending_decisions": len([d for d in self.decision_queue if d["status"] == "open"]),
                "active": self.active,
                "timestamp": time.time()
            }

    def get_agents(self) -> List[str]:
        """Get list of registered agents."""
        with self.sync_lock:
            return list(self.agents)

    def clear_old_thoughts(self, max_age_seconds: float = 3600) -> int:
        """Clear thoughts older than specified age."""
        current_time = time.time()
        cutoff_time = current_time - max_age_seconds

        with self.sync_lock:
            original_count = len(self.thought_stream)
            self.thought_stream = [t for t in self.thought_stream if t.timestamp > cutoff_time]
            removed_count = original_count - len(self.thought_stream)

        return removed_count

    def shutdown(self):
        """Shutdown the collective consciousness."""
        with self.sync_lock:
            self.active = False
            self.agents.clear()
            self.thought_stream.clear()
            self.shared_memory.clear()
            self.decision_queue.clear()


# Alias for test compatibility
ConsciousnessNode = SharedConsciousness


# Contract interface for testing
def get_shared_consciousness(collective_id: str = "default") -> SharedConsciousness:
    """Factory function to create a shared consciousness instance."""
    return SharedConsciousness(collective_id)


def test_basic_functionality():
    """Test basic shared consciousness functionality."""
    sc = get_shared_consciousness("test_collective")

    # Register agents
    assert sc.register_agent("agent_1") == True
    assert sc.register_agent("agent_2") == True
    assert sc.register_agent("agent_1") == False  # Already registered

    # Share thoughts
    assert sc.share_thought("agent_1", "I see a pattern", "observation", 7) == True
    assert sc.share_thought("agent_2", "I agree with the pattern", "observation", 6) == True

    # Retrieve thoughts
    thoughts = sc.get_recent_thoughts("agent_1", count=5)
    assert len(thoughts) == 2
    assert thoughts[0].priority == 7  # Higher priority first

    # Shared memory
    assert sc.store_shared_memory("agent_1", "pattern_data", {"type": "sequence", "confidence": 0.95}) == True
    retrieved = sc.retrieve_shared_memory("agent_2", "pattern_data")
    assert retrieved["confidence"] == 0.95

    # Collective decision
    assert sc.propose_decision("agent_1", "decision_1", "Should we proceed?", ["yes", "no"]) == True
    assert sc.vote_on_decision("agent_1", "decision_1", "yes") == True
    assert sc.vote_on_decision("agent_2", "decision_1", "yes") == True

    result = sc.get_decision_result("decision_1")
    assert result["status"] == "closed"
    assert result["result"] == "yes"

    # Synchronization
    sync_result = sc.synchronize_thoughts("agent_1")
    assert sync_result["status"] == "synchronized"
    assert sync_result["agent_count"] == 2

    # State
    state = sc.get_collective_state()
    assert state["agent_count"] == 2
    assert state["thought_count"] == 2
    assert state["memory_count"] == 1

    sc.shutdown()
    print("✓ All shared consciousness tests passed")


if __name__ == "__main__":
    test_basic_functionality()
