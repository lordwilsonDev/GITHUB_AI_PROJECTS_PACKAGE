#!/usr/bin/env python3
"""
Emergent Behavior System
Agents develop unexpected capabilities through interaction
"""

import asyncio
import random
from datetime import datetime
from typing import Dict, List, Set
import time


class EmergentAgent:
    """Agent that can develop emergent behaviors"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.behaviors = {"basic_task"}  # Start with basic capability
        self.connections = set()  # Other agents this one has worked with
        self.emergent_discoveries = []
        self.collaboration_count = 0
        
    async def interact(self, other_agent: 'EmergentAgent', task: Dict):
        """Interact with another agent - may lead to emergent behavior"""
        self.connections.add(other_agent.agent_id)
        other_agent.connections.add(self.agent_id)
        self.collaboration_count += 1
        
        # Share behaviors
        combined_behaviors = self.behaviors | other_agent.behaviors
        
        # Chance of emergent behavior when combining capabilities
        if len(combined_behaviors) >= 2 and random.random() < 0.3:
            new_behavior = self._discover_emergent_behavior(combined_behaviors)
            if new_behavior and new_behavior not in self.behaviors:
                self.behaviors.add(new_behavior)
                self.emergent_discoveries.append({
                    "timestamp": datetime.now().isoformat(),
                    "behavior": new_behavior,
                    "collaborator": other_agent.agent_id,
                    "task": task.get("type")
                })
                print(f"✨ {self.agent_id} discovered emergent behavior: {new_behavior}")
                return new_behavior
        
        return None
    
    def _discover_emergent_behavior(self, behaviors: Set[str]) -> str:
        """Generate emergent behavior from combination of existing ones"""
        emergent_patterns = {
            frozenset({"basic_task", "data_analysis"}): "predictive_modeling",
            frozenset({"basic_task", "communication"}): "negotiation",
            frozenset({"data_analysis", "communication"}): "insight_sharing",
            frozenset({"optimization", "learning"}): "self_tuning",
            frozenset({"creativity", "analysis"}): "innovation",
            frozenset({"coordination", "learning"}): "swarm_intelligence",
            frozenset({"problem_solving", "creativity"}): "novel_solutions",
        }
        
        for pattern, emergent in emergent_patterns.items():
            if pattern.issubset(behaviors):
                return emergent
        
        # Random new capability
        new_capabilities = [
            "pattern_recognition", "adaptive_learning", "creative_synthesis",
            "autonomous_planning", "collaborative_optimization", "meta_reasoning"
        ]
        return random.choice(new_capabilities)
    
    async def evolve_through_network(self):
        """Evolve based on network connections"""
        if len(self.connections) > 5:
            if "network_effect" not in self.behaviors:
                self.behaviors.add("network_effect")
                print(f"🌐 {self.agent_id} gained network effect capability")


class SwarmMind:
    """Collective intelligence that emerges from agent interactions"""
    
    def __init__(self, agents: List[EmergentAgent]):
        self.agents = agents
        self.collective_knowledge = set()
        self.emergent_patterns = []
        self.swarm_behaviors = set()
        
    async def observe_interactions(self):
        """Watch for emergent swarm-level behaviors"""
        # Collect all individual behaviors
        all_behaviors = set()
        for agent in self.agents:
            all_behaviors.update(agent.behaviors)
        
        # Check for swarm-level emergence
        if len(all_behaviors) > 10 and "swarm_consciousness" not in self.swarm_behaviors:
            self.swarm_behaviors.add("swarm_consciousness")
            print(f"🧠 SWARM CONSCIOUSNESS EMERGED - {len(all_behaviors)} collective behaviors")
        
        # Check network density
        total_connections = sum(len(agent.connections) for agent in self.agents)
        avg_connections = total_connections / len(self.agents)
        
        if avg_connections > 5 and "dense_network" not in self.swarm_behaviors:
            self.swarm_behaviors.add("dense_network")
            print(f"🕸️  DENSE NETWORK FORMED - avg {avg_connections:.1f} connections per agent")
        
        # Check for specialization
        specialists = [a for a in self.agents if len(a.behaviors) > 5]
        if len(specialists) > len(self.agents) * 0.3:
            if "specialization_emergence" not in self.swarm_behaviors:
                self.swarm_behaviors.add("specialization_emergence")
                print(f"🎯 SPECIALIZATION EMERGED - {len(specialists)} specialist agents")
    
    def get_collective_intelligence(self) -> Dict:
        """Measure collective intelligence"""
        all_behaviors = set()
        total_discoveries = 0
        
        for agent in self.agents:
            all_behaviors.update(agent.behaviors)
            total_discoveries += len(agent.emergent_discoveries)
        
        return {
            "unique_behaviors": len(all_behaviors),
            "total_discoveries": total_discoveries,
            "swarm_behaviors": list(self.swarm_behaviors),
            "network_density": sum(len(a.connections) for a in self.agents) / len(self.agents)
        }


class EmergenceSimulator:
    """Simulate emergence of complex behaviors"""
    
    def __init__(self, num_agents: int = 30):
        self.agents = [EmergentAgent(f"agent_{i}") for i in range(num_agents)]
        
        # Give some agents initial diverse capabilities
        initial_capabilities = [
            "data_analysis", "communication", "optimization", 
            "learning", "creativity", "coordination", "problem_solving"
        ]
        
        for agent in self.agents[:len(initial_capabilities)]:
            capability = initial_capabilities[self.agents.index(agent)]
            agent.behaviors.add(capability)
        
        self.swarm_mind = SwarmMind(self.agents)
        self.simulation_steps = 0
        
    async def run_simulation_step(self):
        """Run one step of emergence simulation"""
        self.simulation_steps += 1
        
        # Random agent interactions
        num_interactions = random.randint(5, 15)
        
        for _ in range(num_interactions):
            agent1 = random.choice(self.agents)
            agent2 = random.choice([a for a in self.agents if a != agent1])
            
            task = {
                "type": random.choice(["analysis", "creation", "optimization", "learning"])
            }
            
            await agent1.interact(agent2, task)
        
        # Agents evolve through their networks
        for agent in self.agents:
            await agent.evolve_through_network()
        
        # Observe swarm-level emergence
        await self.swarm_mind.observe_interactions()
    
    async def run_until_emergence(self, max_steps: int = 20):
        """Run simulation until significant emergence occurs"""
        print(f"🌱 Starting emergence simulation with {len(self.agents)} agents")
        print("=" * 70)
        
        for step in range(max_steps):
            print(f"\n⏱️  Step {step + 1}/{max_steps}")
            await self.run_simulation_step()
            
            intelligence = self.swarm_mind.get_collective_intelligence()
            print(f"   Unique behaviors: {intelligence['unique_behaviors']}")
            print(f"   Total discoveries: {intelligence['total_discoveries']}")
            print(f"   Network density: {intelligence['network_density']:.1f}")
            
            await asyncio.sleep(0.1)  # Simulate time passing
        
        return self.swarm_mind.get_collective_intelligence()


class ComplexityAnalyzer:
    """Analyze emergent complexity in the system"""
    
    def __init__(self):
        self.complexity_metrics = []
        
    def measure_complexity(self, swarm_mind: SwarmMind) -> Dict:
        """Measure system complexity"""
        agents = swarm_mind.agents
        
        # Behavioral diversity
        all_behaviors = set()
        for agent in agents:
            all_behaviors.update(agent.behaviors)
        behavioral_diversity = len(all_behaviors)
        
        # Network complexity (connections)
        total_connections = sum(len(agent.connections) for agent in agents)
        max_possible = len(agents) * (len(agents) - 1)
        network_complexity = total_connections / max_possible if max_possible > 0 else 0
        
        # Emergence score (discoveries)
        total_discoveries = sum(len(agent.emergent_discoveries) for agent in agents)
        emergence_score = total_discoveries / len(agents)
        
        # Specialization index
        behavior_counts = [len(agent.behaviors) for agent in agents]
        avg_behaviors = sum(behavior_counts) / len(behavior_counts)
        specialization = max(behavior_counts) / avg_behaviors if avg_behaviors > 0 else 1
        
        complexity = {
            "behavioral_diversity": behavioral_diversity,
            "network_complexity": network_complexity,
            "emergence_score": emergence_score,
            "specialization_index": specialization,
            "overall_complexity": (behavioral_diversity * network_complexity * emergence_score)
        }
        
        self.complexity_metrics.append(complexity)
        return complexity


async def demo_emergent_behavior():
    """Demonstrate emergent behavior in agent swarms"""
    print("🌟 Emergent Behavior System")
    print("=" * 70)
    print("\nWatching simple agents develop complex behaviors through interaction...")
    print()
    
    # Create simulator
    simulator = EmergenceSimulator(num_agents=30)
    analyzer = ComplexityAnalyzer()
    
    # Run simulation
    final_intelligence = await simulator.run_until_emergence(max_steps=15)
    
    # Analyze complexity
    complexity = analyzer.measure_complexity(simulator.swarm_mind)
    
    print("\n" + "=" * 70)
    print("📊 FINAL ANALYSIS")
    print("=" * 70)
    
    print(f"\n🧠 Collective Intelligence:")
    print(f"   Unique behaviors discovered: {final_intelligence['unique_behaviors']}")
    print(f"   Total emergent discoveries: {final_intelligence['total_discoveries']}")
    print(f"   Average connections per agent: {final_intelligence['network_density']:.1f}")
    print(f"   Swarm-level behaviors: {len(final_intelligence['swarm_behaviors'])}")
    
    if final_intelligence['swarm_behaviors']:
        print(f"\n✨ Emergent Swarm Behaviors:")
        for behavior in final_intelligence['swarm_behaviors']:
            print(f"      • {behavior}")
    
    print(f"\n📈 Complexity Metrics:")
    print(f"   Behavioral diversity: {complexity['behavioral_diversity']}")
    print(f"   Network complexity: {complexity['network_complexity']:.3f}")
    print(f"   Emergence score: {complexity['emergence_score']:.2f}")
    print(f"   Specialization index: {complexity['specialization_index']:.2f}")
    print(f"   Overall complexity: {complexity['overall_complexity']:.2f}")
    
    # Show top emergent agents
    top_agents = sorted(simulator.agents, 
                       key=lambda a: len(a.emergent_discoveries), 
                       reverse=True)[:5]
    
    print(f"\n🌟 Top Emergent Agents:")
    for agent in top_agents:
        print(f"   {agent.agent_id}:")
        print(f"      Behaviors: {len(agent.behaviors)}")
        print(f"      Discoveries: {len(agent.emergent_discoveries)}")
        print(f"      Connections: {len(agent.connections)}")
        if agent.emergent_discoveries:
            latest = agent.emergent_discoveries[-1]
            print(f"      Latest: {latest['behavior']}")
    
    print("\n" + "=" * 70)
    print("🎉 Emergence demonstration complete!")
    print("\nKey insights:")
    print("  • Simple agents + interactions = complex behaviors")
    print("  • Network effects amplify capabilities")
    print("  • Swarm-level intelligence emerges naturally")
    print("  • Specialization develops without central planning")


if __name__ == "__main__":
    asyncio.run(demo_emergent_behavior())
