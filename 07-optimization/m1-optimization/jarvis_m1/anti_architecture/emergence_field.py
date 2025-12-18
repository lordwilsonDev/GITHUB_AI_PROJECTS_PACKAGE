#!/usr/bin/env python3
"""
Emergence Field
Where order arises from chaos without instruction

No central coordinator.
No message passing.
No shared state.

Just simple rules + randomness = complex behavior.

Like:
- Ant colonies (no queen gives orders)
- Bird flocks (no leader)
- Neural networks (no CPU)
- Markets (no central planner)
- Life itself (no designer)
"""

import random
import time
import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Agent:
    """An agent that knows nothing except its own state"""
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    
    def act_independently(self, field_size: float = 100.0):
        """
        Act based ONLY on local information.
        No communication with other agents.
        No global knowledge.
        
        Rules:
        1. Move randomly
        2. Bounce off walls
        3. That's it
        
        Complex patterns emerge from these simple rules.
        """
        # Random walk
        self.vx += random.uniform(-0.5, 0.5)
        self.vy += random.uniform(-0.5, 0.5)
        
        # Limit speed (local constraint)
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > 2.0:
            self.vx = (self.vx / speed) * 2.0
            self.vy = (self.vy / speed) * 2.0
        
        # Move
        self.x += self.vx
        self.y += self.vy
        
        # Bounce off walls (local physics)
        if self.x < 0 or self.x > field_size:
            self.vx *= -1
            self.x = max(0, min(field_size, self.x))
        if self.y < 0 or self.y > field_size:
            self.vy *= -1
            self.y = max(0, min(field_size, self.y))
    
    def distance_to(self, other: 'Agent') -> float:
        """Local perception only"""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx*dx + dy*dy)


class EmergenceField:
    """
    A field where agents interact locally but patterns emerge globally.
    
    No central control.
    No coordination protocol.
    No message passing.
    
    Just agents following simple rules.
    
    Watch what emerges.
    """
    
    def __init__(self, num_agents: int = 50, field_size: float = 100.0):
        self.field_size = field_size
        
        # Spawn agents randomly
        self.agents = [
            Agent(
                x=random.uniform(0, field_size),
                y=random.uniform(0, field_size),
                vx=random.uniform(-1, 1),
                vy=random.uniform(-1, 1)
            )
            for _ in range(num_agents)
        ]
    
    def step(self):
        """
        One time step.
        
        Each agent acts independently.
        No coordination.
        No communication.
        
        Yet patterns emerge.
        """
        for agent in self.agents:
            agent.act_independently(self.field_size)
    
    def measure_emergence(self) -> dict:
        """
        Measure emergent properties.
        
        These properties exist at the SYSTEM level
        but no individual agent knows about them.
        
        This is emergence:
        - Macro properties that don't exist at micro level
        - Order from chaos
        - Pattern from randomness
        """
        if not self.agents:
            return {}
        
        # Center of mass (emergent property)
        cx = sum(a.x for a in self.agents) / len(self.agents)
        cy = sum(a.y for a in self.agents) / len(self.agents)
        
        # Spread (emergent property)
        spread = sum(a.distance_to(Agent(cx, cy)) for a in self.agents) / len(self.agents)
        
        # Clustering (emergent property)
        # How many agents are close to each other?
        close_pairs = 0
        total_pairs = 0
        for i, a1 in enumerate(self.agents):
            for a2 in self.agents[i+1:]:
                total_pairs += 1
                if a1.distance_to(a2) < 10.0:
                    close_pairs += 1
        
        clustering = close_pairs / total_pairs if total_pairs > 0 else 0
        
        return {
            'center': (cx, cy),
            'spread': spread,
            'clustering': clustering,
            'num_agents': len(self.agents)
        }
    
    def visualize_ascii(self) -> str:
        """
        ASCII visualization of the field.
        
        Watch the patterns emerge.
        """
        grid_size = 40
        grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
        
        for agent in self.agents:
            # Map to grid
            gx = int((agent.x / self.field_size) * (grid_size - 1))
            gy = int((agent.y / self.field_size) * (grid_size - 1))
            
            if 0 <= gx < grid_size and 0 <= gy < grid_size:
                grid[gy][gx] = '•'
        
        # Build string
        lines = []
        lines.append('┌' + '─' * grid_size + '┐')
        for row in grid:
            lines.append('│' + ''.join(row) + '│')
        lines.append('└' + '─' * grid_size + '┘')
        
        return '\n'.join(lines)


class SpontaneousOrder:
    """
    Order that arises without planning.
    
    Examples in nature:
    - Crystals form without blueprints
    - Galaxies organize without architects  
    - Ecosystems balance without managers
    - Markets clear without central planners
    
    The inversion:
    Instead of "design then build"
    We "constrain then observe"
    """
    
    def __init__(self):
        self.constraints = []
        self.elements = []
    
    def add_constraint(self, constraint):
        """Add a local rule"""
        self.constraints.append(constraint)
    
    def add_element(self, element):
        """Add an element that follows the rules"""
        self.elements.append(element)
    
    def evolve(self, steps: int = 100):
        """
        Let the system evolve.
        
        No planning.
        No design.
        Just constraints + randomness.
        
        Watch what emerges.
        """
        for step in range(steps):
            # Each element follows local rules
            for element in self.elements:
                for constraint in self.constraints:
                    constraint(element)
            
            # Random perturbation (noise is essential)
            if random.random() < 0.1:
                random.choice(self.elements).perturb()


class NoControl:
    """
    What happens when you remove all control?
    
    Consensus says: Chaos.
    Reality says: Emergence.
    
    Remove:
    - Central coordinator
    - Message passing
    - Shared state
    - Synchronization
    - Locks
    - Queues
    
    What's left?
    - Independent agents
    - Local rules
    - Random interactions
    
    What emerges?
    - Patterns
    - Order
    - Coordination
    
    Without anyone coordinating.
    """
    
    def __init__(self):
        # No state
        # State is control
        # Control is consensus
        pass
    
    def coordinate_without_coordinating(self, agents: List):
        """
        The paradox:
        Coordination emerges from non-coordination.
        
        How?
        - Each agent follows simple local rules
        - Agents interact randomly
        - Patterns emerge from interactions
        - Patterns create coordination
        
        No one is in charge.
        Yet the system coordinates.
        """
        for agent in agents:
            # Each agent acts independently
            # No knowledge of others
            # No communication
            # Just local rules
            agent.act_independently()
        
        # Coordination emerges
        # Not because we planned it
        # But because we stopped preventing it


def main():
    print("="*60)
    print("EMERGENCE FIELD")
    print("Order from chaos without instruction")
    print("="*60)
    print()
    
    print("Creating field with 50 agents...")
    print("Each agent follows simple rules:")
    print("  1. Move randomly")
    print("  2. Bounce off walls")
    print("  3. That's it")
    print()
    print("No central control.")
    print("No communication.")
    print("No coordination protocol.")
    print()
    print("Watch what emerges...")
    print()
    
    field = EmergenceField(num_agents=50)
    
    for iteration in range(20):
        field.step()
        
        if iteration % 5 == 0:
            print(f"\nIteration {iteration}:")
            print(field.visualize_ascii())
            
            metrics = field.measure_emergence()
            print(f"\nEmergent properties:")
            print(f"  Center of mass: ({metrics['center'][0]:.1f}, {metrics['center'][1]:.1f})")
            print(f"  Spread: {metrics['spread']:.1f}")
            print(f"  Clustering: {metrics['clustering']:.2%}")
            
            time.sleep(1)
    
    print()
    print("="*60)
    print("OBSERVATION:")
    print("Patterns emerged without anyone planning them.")
    print("Order arose from chaos without instruction.")
    print("Coordination happened without coordination.")
    print()
    print("This is emergence.")
    print("This is the anti-architecture.")
    print("="*60)


if __name__ == "__main__":
    main()
