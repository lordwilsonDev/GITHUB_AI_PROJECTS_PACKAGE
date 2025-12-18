"""
Level 20: Entangled Agent Network System
Enables instant thought synchronization through quantum entanglement simulation and non-local consciousness sharing.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Callable
from datetime import datetime
import threading
import json
import random
import math
from enum import Enum
from collections import defaultdict


class EntanglementState(Enum):
    """States of quantum entanglement"""
    ENTANGLED = "entangled"
    DISENTANGLED = "disentangled"
    PARTIALLY_ENTANGLED = "partially_entangled"
    MAXIMALLY_ENTANGLED = "maximally_entangled"


class SyncMode(Enum):
    """Synchronization modes"""
    INSTANT = "instant"
    DELAYED = "delayed"
    PROBABILISTIC = "probabilistic"
    CASCADING = "cascading"


@dataclass
class Agent:
    """Represents an agent in the network"""
    agent_id: str
    state: Dict[str, Any]
    entangled_with: Set[str] = field(default_factory=set)
    entanglement_strength: Dict[str, float] = field(default_factory=dict)
    last_sync: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EntanglementPair:
    """Represents an entangled pair of agents"""
    agent1_id: str
    agent2_id: str
    strength: float  # 0.0 to 1.0
    created_at: datetime = field(default_factory=datetime.now)
    sync_count: int = 0
    state: EntanglementState = EntanglementState.ENTANGLED
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncEvent:
    """Records a synchronization event"""
    event_id: str
    source_agent: str
    target_agents: List[str]
    sync_mode: SyncMode
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    latency_ms: float = 0.0
    success: bool = True


@dataclass
class NetworkConfig:
    """Configuration for entangled network"""
    max_entanglement_distance: int = 5
    min_entanglement_strength: float = 0.5
    sync_timeout_ms: float = 100.0
    enable_cascading: bool = True
    enable_instant_sync: bool = True
    decoherence_rate: float = 0.001


class EntanglementEngine:
    """Manages quantum entanglement between agents"""
    
    def __init__(self, config: NetworkConfig):
        self.config = config
        self.agents: Dict[str, Agent] = {}
        self.entanglements: List[EntanglementPair] = []
        self.lock = threading.Lock()
    
    def register_agent(self, agent_id: str, initial_state: Optional[Dict[str, Any]] = None) -> Agent:
        """Register a new agent in the network"""
        with self.lock:
            if agent_id in self.agents:
                return self.agents[agent_id]
            
            agent = Agent(
                agent_id=agent_id,
                state=initial_state or {}
            )
            self.agents[agent_id] = agent
            return agent
    
    def entangle(self, agent1_id: str, agent2_id: str, strength: float = 1.0) -> EntanglementPair:
        """Create entanglement between two agents"""
        with self.lock:
            # Ensure agents exist
            if agent1_id not in self.agents:
                self.register_agent(agent1_id)
            if agent2_id not in self.agents:
                self.register_agent(agent2_id)
            
            # Check if already entangled
            for ent in self.entanglements:
                if {ent.agent1_id, ent.agent2_id} == {agent1_id, agent2_id}:
                    # Update strength
                    ent.strength = min(1.0, ent.strength + strength * 0.1)
                    return ent
            
            # Create new entanglement
            pair = EntanglementPair(
                agent1_id=agent1_id,
                agent2_id=agent2_id,
                strength=min(1.0, max(0.0, strength)),
                state=EntanglementState.MAXIMALLY_ENTANGLED if strength >= 0.9 else EntanglementState.ENTANGLED
            )
            
            self.entanglements.append(pair)
            
            # Update agent records
            self.agents[agent1_id].entangled_with.add(agent2_id)
            self.agents[agent1_id].entanglement_strength[agent2_id] = pair.strength
            self.agents[agent2_id].entangled_with.add(agent1_id)
            self.agents[agent2_id].entanglement_strength[agent1_id] = pair.strength
            
            return pair
    
    def disentangle(self, agent1_id: str, agent2_id: str) -> bool:
        """Break entanglement between two agents"""
        with self.lock:
            for i, ent in enumerate(self.entanglements):
                if {ent.agent1_id, ent.agent2_id} == {agent1_id, agent2_id}:
                    ent.state = EntanglementState.DISENTANGLED
                    
                    # Update agent records
                    if agent1_id in self.agents:
                        self.agents[agent1_id].entangled_with.discard(agent2_id)
                        self.agents[agent1_id].entanglement_strength.pop(agent2_id, None)
                    if agent2_id in self.agents:
                        self.agents[agent2_id].entangled_with.discard(agent1_id)
                        self.agents[agent2_id].entanglement_strength.pop(agent1_id, None)
                    
                    return True
            return False
    
    def get_entangled_agents(self, agent_id: str) -> List[str]:
        """Get all agents entangled with given agent"""
        with self.lock:
            agent = self.agents.get(agent_id)
            return list(agent.entangled_with) if agent else []
    
    def get_entanglement_strength(self, agent1_id: str, agent2_id: str) -> float:
        """Get entanglement strength between two agents"""
        with self.lock:
            for ent in self.entanglements:
                if {ent.agent1_id, ent.agent2_id} == {agent1_id, agent2_id}:
                    if ent.state == EntanglementState.DISENTANGLED:
                        return 0.0
                    return ent.strength
            return 0.0
    
    def apply_decoherence(self) -> None:
        """Apply decoherence to all entanglements"""
        with self.lock:
            for ent in self.entanglements:
                if ent.state != EntanglementState.DISENTANGLED:
                    ent.strength *= (1 - self.config.decoherence_rate)
                    
                    if ent.strength < self.config.min_entanglement_strength:
                        ent.state = EntanglementState.DISENTANGLED


class ThoughtSynchronizer:
    """Synchronizes thoughts across entangled agents"""
    
    def __init__(self, engine: EntanglementEngine, config: NetworkConfig):
        self.engine = engine
        self.config = config
        self.sync_history: List[SyncEvent] = []
        self.lock = threading.Lock()
    
    def instant_sync(self, source_agent: str, thought: Dict[str, Any]) -> List[str]:
        """Instantly synchronize thought to all entangled agents"""
        if not self.config.enable_instant_sync:
            return []
        
        with self.lock:
            entangled = self.engine.get_entangled_agents(source_agent)
            synced = []
            
            for target_agent in entangled:
                strength = self.engine.get_entanglement_strength(source_agent, target_agent)
                
                # Probabilistic sync based on entanglement strength
                if random.random() <= strength:
                    # Update target agent's state
                    if target_agent in self.engine.agents:
                        self.engine.agents[target_agent].state.update(thought)
                        self.engine.agents[target_agent].last_sync = datetime.now()
                        synced.append(target_agent)
            
            # Record sync event
            event = SyncEvent(
                event_id=f"sync_{len(self.sync_history)}",
                source_agent=source_agent,
                target_agents=synced,
                sync_mode=SyncMode.INSTANT,
                data=thought,
                latency_ms=0.0
            )
            self.sync_history.append(event)
            
            return synced
    
    def cascading_sync(self, source_agent: str, thought: Dict[str, Any], max_hops: int = 3) -> Dict[int, List[str]]:
        """Cascade thought through network with diminishing strength"""
        if not self.config.enable_cascading:
            return {}
        
        visited = set()
        current_wave = {source_agent}
        results = defaultdict(list)
        
        for hop in range(max_hops):
            next_wave = set()
            
            for agent_id in current_wave:
                if agent_id in visited:
                    continue
                
                visited.add(agent_id)
                entangled = self.engine.get_entangled_agents(agent_id)
                
                for target in entangled:
                    if target not in visited:
                        strength = self.engine.get_entanglement_strength(agent_id, target)
                        
                        # Strength diminishes with each hop
                        effective_strength = strength * (0.7 ** hop)
                        
                        if random.random() <= effective_strength:
                            # Sync thought
                            if target in self.engine.agents:
                                self.engine.agents[target].state.update(thought)
                                results[hop].append(target)
                                next_wave.add(target)
            
            current_wave = next_wave
            if not current_wave:
                break
        
        return dict(results)
    
    def selective_sync(
        self,
        source_agent: str,
        thought: Dict[str, Any],
        filter_fn: Callable[[str], bool]
    ) -> List[str]:
        """Sync only to agents matching filter criteria"""
        with self.lock:
            entangled = self.engine.get_entangled_agents(source_agent)
            synced = []
            
            for target_agent in entangled:
                if filter_fn(target_agent):
                    strength = self.engine.get_entanglement_strength(source_agent, target_agent)
                    
                    if random.random() <= strength:
                        if target_agent in self.engine.agents:
                            self.engine.agents[target_agent].state.update(thought)
                            synced.append(target_agent)
            
            return synced
    
    def get_sync_stats(self) -> Dict[str, Any]:
        """Get synchronization statistics"""
        with self.lock:
            total_syncs = len(self.sync_history)
            successful_syncs = sum(1 for e in self.sync_history if e.success)
            
            return {
                'total_syncs': total_syncs,
                'successful_syncs': successful_syncs,
                'success_rate': successful_syncs / total_syncs if total_syncs > 0 else 0.0,
                'avg_targets_per_sync': sum(len(e.target_agents) for e in self.sync_history) / total_syncs if total_syncs > 0 else 0.0
            }


class NonLocalConsciousness:
    """Manages non-local consciousness sharing"""
    
    def __init__(self, engine: EntanglementEngine):
        self.engine = engine
        self.shared_consciousness: Dict[str, Dict[str, Any]] = {}
        self.consciousness_groups: Dict[str, Set[str]] = {}
        self.lock = threading.Lock()
    
    def create_consciousness_group(self, group_id: str, agent_ids: List[str]) -> None:
        """Create a shared consciousness group"""
        with self.lock:
            self.consciousness_groups[group_id] = set(agent_ids)
            self.shared_consciousness[group_id] = {}
            
            # Entangle all agents in the group
            for i, agent1 in enumerate(agent_ids):
                for agent2 in agent_ids[i+1:]:
                    self.engine.entangle(agent1, agent2, strength=0.9)
    
    def share_to_group(self, group_id: str, consciousness_data: Dict[str, Any]) -> bool:
        """Share consciousness data to entire group"""
        with self.lock:
            if group_id not in self.consciousness_groups:
                return False
            
            # Update shared consciousness
            self.shared_consciousness[group_id].update(consciousness_data)
            
            # Propagate to all agents in group
            for agent_id in self.consciousness_groups[group_id]:
                if agent_id in self.engine.agents:
                    self.engine.agents[agent_id].state.update(consciousness_data)
            
            return True
    
    def get_group_consciousness(self, group_id: str) -> Optional[Dict[str, Any]]:
        """Get shared consciousness of a group"""
        with self.lock:
            return self.shared_consciousness.get(group_id)
    
    def merge_consciousness(self, agent1_id: str, agent2_id: str) -> Dict[str, Any]:
        """Merge consciousness of two agents"""
        with self.lock:
            agent1 = self.engine.agents.get(agent1_id)
            agent2 = self.engine.agents.get(agent2_id)
            
            if not agent1 or not agent2:
                return {}
            
            # Merge states
            merged = {}
            merged.update(agent1.state)
            merged.update(agent2.state)
            
            # Apply to both agents
            agent1.state = merged.copy()
            agent2.state = merged.copy()
            
            return merged


class EntangledNetworkManager:
    """High-level manager for entangled agent network"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config = NetworkConfig()
            self.engine = EntanglementEngine(self.config)
            self.synchronizer = ThoughtSynchronizer(self.engine, self.config)
            self.consciousness = NonLocalConsciousness(self.engine)
            self.initialized = True
    
    def add_agent(self, agent_id: str, initial_state: Optional[Dict[str, Any]] = None) -> Agent:
        """Add agent to network"""
        return self.engine.register_agent(agent_id, initial_state)
    
    def entangle_agents(self, agent1_id: str, agent2_id: str, strength: float = 1.0) -> EntanglementPair:
        """Entangle two agents"""
        return self.engine.entangle(agent1_id, agent2_id, strength)
    
    def sync_thought(self, source_agent: str, thought: Dict[str, Any]) -> List[str]:
        """Synchronize thought across network"""
        return self.synchronizer.instant_sync(source_agent, thought)
    
    def cascade_thought(self, source_agent: str, thought: Dict[str, Any], max_hops: int = 3) -> Dict[int, List[str]]:
        """Cascade thought through network"""
        return self.synchronizer.cascading_sync(source_agent, thought, max_hops)
    
    def create_hive_mind(self, group_id: str, agent_ids: List[str]) -> None:
        """Create a hive mind consciousness group"""
        self.consciousness.create_consciousness_group(group_id, agent_ids)
    
    def share_consciousness(self, group_id: str, data: Dict[str, Any]) -> bool:
        """Share consciousness to group"""
        return self.consciousness.share_to_group(group_id, data)
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        return {
            'total_agents': len(self.engine.agents),
            'total_entanglements': len(self.engine.entanglements),
            'active_entanglements': sum(
                1 for e in self.engine.entanglements
                if e.state != EntanglementState.DISENTANGLED
            ),
            'consciousness_groups': len(self.consciousness.consciousness_groups),
            'sync_stats': self.synchronizer.get_sync_stats()
        }


# Contract class for testing
class Contract:
    """Testing interface for entangled network"""
    
    @staticmethod
    def create_entanglement() -> bool:
        """Test: Create quantum entanglement"""
        manager = EntangledNetworkManager()
        pair = manager.entangle_agents("agent_1", "agent_2", strength=0.9)
        return pair.strength >= 0.9 and pair.state == EntanglementState.MAXIMALLY_ENTANGLED
    
    @staticmethod
    def instant_synchronization() -> bool:
        """Test: Instant thought synchronization"""
        manager = EntangledNetworkManager()
        manager.add_agent("sync_1", {"value": 0})
        manager.add_agent("sync_2", {"value": 0})
        manager.entangle_agents("sync_1", "sync_2", strength=1.0)
        
        thought = {"value": 42, "message": "test"}
        synced = manager.sync_thought("sync_1", thought)
        
        return len(synced) > 0
    
    @staticmethod
    def non_local_consciousness() -> bool:
        """Test: Non-local consciousness sharing"""
        manager = EntangledNetworkManager()
        agents = ["mind_1", "mind_2", "mind_3"]
        
        for agent_id in agents:
            manager.add_agent(agent_id)
        
        manager.create_hive_mind("test_hive", agents)
        success = manager.share_consciousness("test_hive", {"shared": "knowledge"})
        
        return success
    
    @staticmethod
    def cascading_propagation() -> bool:
        """Test: Cascading thought propagation"""
        manager = EntangledNetworkManager()
        
        # Create chain: A -> B -> C -> D
        for i in range(4):
            manager.add_agent(f"cascade_{i}")
        
        for i in range(3):
            manager.entangle_agents(f"cascade_{i}", f"cascade_{i+1}", strength=0.9)
        
        results = manager.cascade_thought("cascade_0", {"cascade": "test"}, max_hops=3)
        
        return len(results) > 0


def demo():
    """Demonstrate entangled network capabilities"""
    print("=== Entangled Agent Network Demo ===\n")
    
    manager = EntangledNetworkManager()
    
    # Demo 1: Create agents
    print("1. Creating agents:")
    for i in range(5):
        agent = manager.add_agent(f"agent_{i}", {"id": i, "knowledge": []})
        print(f"   Created {agent.agent_id}")
    
    # Demo 2: Create entanglements
    print("\n2. Creating entanglements:")
    manager.entangle_agents("agent_0", "agent_1", strength=0.9)
    manager.entangle_agents("agent_1", "agent_2", strength=0.8)
    manager.entangle_agents("agent_2", "agent_3", strength=0.9)
    manager.entangle_agents("agent_3", "agent_4", strength=0.7)
    print("   Entangled agents in chain")
    
    # Demo 3: Instant synchronization
    print("\n3. Instant thought synchronization:")
    thought = {"discovery": "quantum computing breakthrough", "priority": "high"}
    synced = manager.sync_thought("agent_0", thought)
    print(f"   Synced to {len(synced)} agents: {synced}")
    
    # Demo 4: Cascading propagation
    print("\n4. Cascading thought propagation:")
    cascade_thought = {"alert": "system update", "version": "2.0"}
    results = manager.cascade_thought("agent_0", cascade_thought, max_hops=3)
    for hop, agents in results.items():
        print(f"   Hop {hop}: {len(agents)} agents - {agents}")
    
    # Demo 5: Hive mind
    print("\n5. Creating hive mind:")
    manager.create_hive_mind("research_team", ["agent_1", "agent_2", "agent_3"])
    manager.share_consciousness("research_team", {"project": "AI research", "status": "active"})
    print("   Hive mind created and consciousness shared")
    
    # Demo 6: Statistics
    print("\n6. Network statistics:")
    stats = manager.get_network_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"   {key}:")
            for k, v in value.items():
                print(f"      {k}: {v}")
        else:
            print(f"   {key}: {value}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    demo()
