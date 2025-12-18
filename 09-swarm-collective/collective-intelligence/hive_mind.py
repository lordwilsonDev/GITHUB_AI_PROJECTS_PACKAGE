#!/usr/bin/env python3
"""
Hive Mind Coordinator - Level 16

Enables multi-agent thought coordination through:
- Multi-agent thought coordination
- Consensus mechanisms
- Collective intelligence emergence

Part of New Build 8: Collective Consciousness & Universal Integration
"""

import time
import threading
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import json


@dataclass
class AgentNode:
    """Represents an agent in the hive mind."""
    agent_id: str
    role: str  # 'worker', 'coordinator', 'specialist', 'observer'
    capabilities: Set[str] = field(default_factory=set)
    active: bool = True
    last_heartbeat: float = field(default_factory=time.time)
    contribution_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThoughtCoordination:
    """Represents a coordinated thought across multiple agents."""
    coordination_id: str
    topic: str
    participating_agents: Set[str] = field(default_factory=set)
    thoughts: List[Dict[str, Any]] = field(default_factory=list)
    consensus_reached: bool = False
    consensus_result: Optional[Any] = None
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None


@dataclass
class ConsensusProposal:
    """Represents a proposal for consensus."""
    proposal_id: str
    proposer: str
    content: Any
    options: List[str]
    votes: Dict[str, str] = field(default_factory=dict)  # agent_id -> option
    weights: Dict[str, float] = field(default_factory=dict)  # agent_id -> weight
    status: str = "open"  # open, closed, consensus, no_consensus
    result: Optional[str] = None
    created_at: float = field(default_factory=time.time)


class ConsensusEngine:
    """Engine for building consensus among agents."""
    
    def __init__(self, threshold: float = 0.6):
        self.threshold = threshold  # Minimum agreement percentage
        self.proposals: Dict[str, ConsensusProposal] = {}
        self.lock = threading.Lock()
    
    def create_proposal(self, proposal_id: str, proposer: str, content: Any, 
                       options: List[str]) -> bool:
        """Create a new consensus proposal."""
        with self.lock:
            if proposal_id in self.proposals:
                return False
            
            self.proposals[proposal_id] = ConsensusProposal(
                proposal_id=proposal_id,
                proposer=proposer,
                content=content,
                options=options
            )
            return True
    
    def vote(self, proposal_id: str, agent_id: str, option: str, 
             weight: float = 1.0) -> bool:
        """Cast a vote on a proposal."""
        with self.lock:
            if proposal_id not in self.proposals:
                return False
            
            proposal = self.proposals[proposal_id]
            if proposal.status != "open":
                return False
            
            if option not in proposal.options:
                return False
            
            proposal.votes[agent_id] = option
            proposal.weights[agent_id] = weight
            return True
    
    def check_consensus(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """Check if consensus has been reached."""
        with self.lock:
            if proposal_id not in self.proposals:
                return None
            
            proposal = self.proposals[proposal_id]
            if not proposal.votes:
                return None
            
            # Calculate weighted vote counts
            vote_counts: Dict[str, float] = defaultdict(float)
            total_weight = 0.0
            
            for agent_id, option in proposal.votes.items():
                weight = proposal.weights.get(agent_id, 1.0)
                vote_counts[option] += weight
                total_weight += weight
            
            # Find option with highest weighted votes
            max_option = max(vote_counts.items(), key=lambda x: x[1])
            max_votes = max_option[1]
            max_percentage = max_votes / total_weight if total_weight > 0 else 0
            
            # Check if threshold met
            if max_percentage >= self.threshold:
                proposal.status = "consensus"
                proposal.result = max_option[0]
            
            return {
                "proposal_id": proposal_id,
                "status": proposal.status,
                "result": proposal.result,
                "vote_counts": dict(vote_counts),
                "total_weight": total_weight,
                "consensus_percentage": max_percentage
            }
    
    def close_proposal(self, proposal_id: str) -> bool:
        """Close a proposal and finalize result."""
        with self.lock:
            if proposal_id not in self.proposals:
                return False
            
            proposal = self.proposals[proposal_id]
            if proposal.status == "open":
                # Check consensus one last time
                self.check_consensus(proposal_id)
                if proposal.status == "open":
                    proposal.status = "no_consensus"
            
            return True


class CollectiveIntelligence:
    """Manages emergent collective intelligence."""
    
    def __init__(self):
        self.insights: List[Dict[str, Any]] = []
        self.patterns: List[Dict[str, Any]] = []
        self.emergent_behaviors: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
    
    def record_insight(self, source_agents: List[str], insight: Any, 
                      confidence: float = 0.5) -> str:
        """Record an emergent insight from collective processing."""
        with self.lock:
            insight_id = f"insight_{len(self.insights)}"
            self.insights.append({
                "insight_id": insight_id,
                "source_agents": source_agents,
                "insight": insight,
                "confidence": confidence,
                "timestamp": time.time()
            })
            return insight_id
    
    def detect_pattern(self, pattern_type: str, data: Any, 
                      detected_by: List[str]) -> str:
        """Record a detected pattern from collective observation."""
        with self.lock:
            pattern_id = f"pattern_{len(self.patterns)}"
            self.patterns.append({
                "pattern_id": pattern_id,
                "pattern_type": pattern_type,
                "data": data,
                "detected_by": detected_by,
                "timestamp": time.time()
            })
            return pattern_id
    
    def record_emergent_behavior(self, behavior_type: str, description: str,
                                 participants: List[str]) -> str:
        """Record emergent behavior from agent interactions."""
        with self.lock:
            behavior_id = f"behavior_{len(self.emergent_behaviors)}"
            self.emergent_behaviors.append({
                "behavior_id": behavior_id,
                "behavior_type": behavior_type,
                "description": description,
                "participants": participants,
                "timestamp": time.time()
            })
            return behavior_id
    
    def get_insights(self, min_confidence: float = 0.0) -> List[Dict[str, Any]]:
        """Get insights above minimum confidence."""
        with self.lock:
            return [i for i in self.insights if i["confidence"] >= min_confidence]
    
    def get_patterns(self, pattern_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get detected patterns, optionally filtered by type."""
        with self.lock:
            if pattern_type:
                return [p for p in self.patterns if p["pattern_type"] == pattern_type]
            return self.patterns.copy()


class HiveMind:
    """Main hive mind coordinator for multi-agent systems."""
    
    def __init__(self, hive_id: str = "default"):
        self.hive_id = hive_id
        self.agents: Dict[str, AgentNode] = {}
        self.coordinations: Dict[str, ThoughtCoordination] = {}
        self.consensus_engine = ConsensusEngine()
        self.collective_intelligence = CollectiveIntelligence()
        self.lock = threading.Lock()
        self.active = True
    
    def register_agent(self, agent_id: str, role: str = "worker",
                      capabilities: Optional[Set[str]] = None) -> bool:
        """Register an agent in the hive mind."""
        with self.lock:
            if agent_id in self.agents:
                return False
            
            self.agents[agent_id] = AgentNode(
                agent_id=agent_id,
                role=role,
                capabilities=capabilities or set()
            )
            return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the hive mind."""
        with self.lock:
            if agent_id not in self.agents:
                return False
            
            self.agents[agent_id].active = False
            del self.agents[agent_id]
            return True
    
    def heartbeat(self, agent_id: str) -> bool:
        """Update agent heartbeat."""
        with self.lock:
            if agent_id not in self.agents:
                return False
            
            self.agents[agent_id].last_heartbeat = time.time()
            return True
    
    def start_coordination(self, coordination_id: str, topic: str,
                          agents: List[str]) -> bool:
        """Start a thought coordination session."""
        with self.lock:
            if coordination_id in self.coordinations:
                return False
            
            # Verify all agents exist
            for agent_id in agents:
                if agent_id not in self.agents:
                    return False
            
            self.coordinations[coordination_id] = ThoughtCoordination(
                coordination_id=coordination_id,
                topic=topic,
                participating_agents=set(agents)
            )
            return True
    
    def contribute_thought(self, coordination_id: str, agent_id: str,
                          thought: Any) -> bool:
        """Contribute a thought to a coordination session."""
        with self.lock:
            if coordination_id not in self.coordinations:
                return False
            
            coordination = self.coordinations[coordination_id]
            if agent_id not in coordination.participating_agents:
                return False
            
            coordination.thoughts.append({
                "agent_id": agent_id,
                "thought": thought,
                "timestamp": time.time()
            })
            
            # Update contribution score
            if agent_id in self.agents:
                self.agents[agent_id].contribution_score += 1.0
            
            return True
    
    def finalize_coordination(self, coordination_id: str) -> Optional[Dict[str, Any]]:
        """Finalize a coordination session and extract collective result."""
        with self.lock:
            if coordination_id not in self.coordinations:
                return None
            
            coordination = self.coordinations[coordination_id]
            coordination.consensus_reached = True
            coordination.completed_at = time.time()
            
            # Synthesize collective result
            result = {
                "coordination_id": coordination_id,
                "topic": coordination.topic,
                "participants": list(coordination.participating_agents),
                "thought_count": len(coordination.thoughts),
                "thoughts": coordination.thoughts,
                "duration": coordination.completed_at - coordination.created_at
            }
            
            coordination.consensus_result = result
            return result
    
    def propose_consensus(self, proposal_id: str, proposer: str, content: Any,
                         options: List[str]) -> bool:
        """Create a consensus proposal."""
        return self.consensus_engine.create_proposal(proposal_id, proposer, content, options)
    
    def vote_consensus(self, proposal_id: str, agent_id: str, option: str) -> bool:
        """Vote on a consensus proposal."""
        # Calculate weight based on contribution score
        weight = 1.0
        if agent_id in self.agents:
            weight = 1.0 + (self.agents[agent_id].contribution_score * 0.1)
        
        return self.consensus_engine.vote(proposal_id, agent_id, option, weight)
    
    def check_consensus(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """Check consensus status."""
        return self.consensus_engine.check_consensus(proposal_id)
    
    def record_insight(self, source_agents: List[str], insight: Any,
                      confidence: float = 0.5) -> str:
        """Record emergent collective insight."""
        return self.collective_intelligence.record_insight(source_agents, insight, confidence)
    
    def detect_pattern(self, pattern_type: str, data: Any,
                      detected_by: List[str]) -> str:
        """Record detected pattern."""
        return self.collective_intelligence.detect_pattern(pattern_type, data, detected_by)
    
    def get_hive_state(self) -> Dict[str, Any]:
        """Get current hive mind state."""
        with self.lock:
            active_agents = [a for a in self.agents.values() if a.active]
            
            return {
                "hive_id": self.hive_id,
                "active": self.active,
                "agent_count": len(active_agents),
                "agents": [a.agent_id for a in active_agents],
                "coordination_count": len(self.coordinations),
                "active_coordinations": len([c for c in self.coordinations.values() 
                                            if not c.consensus_reached]),
                "insights": len(self.collective_intelligence.insights),
                "patterns": len(self.collective_intelligence.patterns),
                "emergent_behaviors": len(self.collective_intelligence.emergent_behaviors)
            }
    
    def shutdown(self):
        """Shutdown the hive mind."""
        with self.lock:
            self.active = False
            self.agents.clear()
            self.coordinations.clear()


# Singleton pattern for global hive mind access
_hive_minds: Dict[str, HiveMind] = {}
_hive_lock = threading.Lock()


def get_hive_mind(hive_id: str = "default") -> HiveMind:
    """Get or create a hive mind instance."""
    with _hive_lock:
        if hive_id not in _hive_minds:
            _hive_minds[hive_id] = HiveMind(hive_id)
        return _hive_minds[hive_id]


class HiveMindContract:
    """Contract interface for testing."""
    
    @staticmethod
    def coordinate_agents(agent_ids: List[str], topic: str) -> Dict[str, Any]:
        """Coordinate multiple agents on a topic."""
        hive = get_hive_mind("test")
        
        # Register agents
        for agent_id in agent_ids:
            hive.register_agent(agent_id)
        
        # Start coordination
        coord_id = f"coord_{topic}"
        hive.start_coordination(coord_id, topic, agent_ids)
        
        # Simulate contributions
        for agent_id in agent_ids:
            hive.contribute_thought(coord_id, agent_id, f"Thought from {agent_id}")
        
        # Finalize
        result = hive.finalize_coordination(coord_id)
        
        hive.shutdown()
        return result
    
    @staticmethod
    def reach_consensus(agents: List[str], proposal: str, options: List[str]) -> Dict[str, Any]:
        """Reach consensus among agents."""
        hive = get_hive_mind("test")
        
        # Register agents
        for agent_id in agents:
            hive.register_agent(agent_id)
        
        # Create proposal
        hive.propose_consensus("test_proposal", agents[0], proposal, options)
        
        # Vote (majority votes for first option)
        for i, agent_id in enumerate(agents):
            option = options[0] if i < len(agents) // 2 + 1 else options[1]
            hive.vote_consensus("test_proposal", agent_id, option)
        
        # Check consensus
        result = hive.check_consensus("test_proposal")
        
        hive.shutdown()
        return result
    
    @staticmethod
    def emerge_intelligence(agent_ids: List[str]) -> Dict[str, Any]:
        """Demonstrate emergent collective intelligence."""
        hive = get_hive_mind("test")
        
        # Register agents
        for agent_id in agent_ids:
            hive.register_agent(agent_id)
        
        # Record insights
        insight_id = hive.record_insight(
            agent_ids[:2],
            "Collective pattern recognition",
            confidence=0.85
        )
        
        # Detect pattern
        pattern_id = hive.detect_pattern(
            "temporal",
            {"sequence": [1, 2, 3, 5, 8]},
            agent_ids
        )
        
        # Get state
        state = hive.get_hive_state()
        
        hive.shutdown()
        return {
            "insight_id": insight_id,
            "pattern_id": pattern_id,
            "state": state
        }


def demo():
    """Demonstrate hive mind capabilities."""
    print("=== Hive Mind Coordinator Demo ===\n")
    
    hive = get_hive_mind("demo")
    
    # Register agents
    print("1. Registering agents...")
    agents = ["alpha", "beta", "gamma", "delta"]
    for agent in agents:
        hive.register_agent(agent, role="worker", capabilities={"analyze", "decide"})
    print(f"   Registered {len(agents)} agents\n")
    
    # Start coordination
    print("2. Starting thought coordination...")
    hive.start_coordination("coord_001", "Problem Analysis", agents)
    for agent in agents:
        hive.contribute_thought("coord_001", agent, f"Analysis from {agent}")
    result = hive.finalize_coordination("coord_001")
    print(f"   Coordination complete: {result['thought_count']} thoughts\n")
    
    # Consensus
    print("3. Building consensus...")
    hive.propose_consensus("prop_001", "alpha", "Should we proceed?", ["yes", "no", "defer"])
    hive.vote_consensus("prop_001", "alpha", "yes")
    hive.vote_consensus("prop_001", "beta", "yes")
    hive.vote_consensus("prop_001", "gamma", "no")
    hive.vote_consensus("prop_001", "delta", "yes")
    consensus = hive.check_consensus("prop_001")
    print(f"   Consensus: {consensus['result']} ({consensus['consensus_percentage']:.1%})\n")
    
    # Collective intelligence
    print("4. Emergent collective intelligence...")
    insight_id = hive.record_insight(["alpha", "beta"], "Pattern detected", 0.9)
    pattern_id = hive.detect_pattern("sequence", [1, 1, 2, 3, 5], ["gamma", "delta"])
    print(f"   Insight: {insight_id}")
    print(f"   Pattern: {pattern_id}\n")
    
    # State
    print("5. Hive state:")
    state = hive.get_hive_state()
    for key, value in state.items():
        print(f"   {key}: {value}")
    
    hive.shutdown()
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    demo()
