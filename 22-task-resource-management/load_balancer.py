#!/usr/bin/env python3
import time
import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import deque

@dataclass
class AgentLoad:
    agent_id: str
    current_tasks: int = 0
    total_completed: int = 0
    capacity: int = 10
    avg_completion_time: float = 1.0
    
    def utilization(self) -> float:
        return self.current_tasks / self.capacity if self.capacity > 0 else 1.0
    
    def can_accept(self) -> bool:
        return self.current_tasks < self.capacity

class LoadBalancer:
    def __init__(self, strategy: str = 'round_robin'):
        self.agents: Dict[str, AgentLoad] = {}
        self.strategy = strategy
        self.round_robin_index = 0
        self.task_queue = deque()
    
    def register_agent(self, agent_id: str, capacity: int = 10):
        self.agents[agent_id] = AgentLoad(agent_id, capacity=capacity)
    
    def assign_task(self, task_id: str) -> Optional[str]:
        if not self.agents:
            return None
        
        if self.strategy == 'round_robin':
            return self._round_robin_assign(task_id)
        elif self.strategy == 'least_loaded':
            return self._least_loaded_assign(task_id)
        elif self.strategy == 'fastest':
            return self._fastest_assign(task_id)
        return None
    
    def _round_robin_assign(self, task_id: str) -> Optional[str]:
        agent_ids = list(self.agents.keys())
        attempts = 0
        while attempts < len(agent_ids):
            agent_id = agent_ids[self.round_robin_index % len(agent_ids)]
            self.round_robin_index += 1
            if self.agents[agent_id].can_accept():
                self.agents[agent_id].current_tasks += 1
                return agent_id
            attempts += 1
        return None
    
    def _least_loaded_assign(self, task_id: str) -> Optional[str]:
        available = [(aid, agent.utilization()) 
                    for aid, agent in self.agents.items() 
                    if agent.can_accept()]
        if not available:
            return None
        agent_id = min(available, key=lambda x: x[1])[0]
        self.agents[agent_id].current_tasks += 1
        return agent_id
    
    def _fastest_assign(self, task_id: str) -> Optional[str]:
        available = [(aid, agent.avg_completion_time) 
                    for aid, agent in self.agents.items() 
                    if agent.can_accept()]
        if not available:
            return None
        agent_id = min(available, key=lambda x: x[1])[0]
        self.agents[agent_id].current_tasks += 1
        return agent_id
    
    def complete_task(self, agent_id: str, completion_time: float = 1.0):
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.current_tasks = max(0, agent.current_tasks - 1)
            agent.total_completed += 1
            # Update moving average
            alpha = 0.3
            agent.avg_completion_time = (alpha * completion_time + 
                                        (1 - alpha) * agent.avg_completion_time)
    
    def get_stats(self) -> Dict:
        total_tasks = sum(a.current_tasks for a in self.agents.values())
        total_completed = sum(a.total_completed for a in self.agents.values())
        loads = [a.utilization() for a in self.agents.values()]
        avg_load = sum(loads) / len(loads) if loads else 0
        
        # Gini coefficient for load balance fairness
        if loads:
            loads_sorted = sorted(loads)
            n = len(loads_sorted)
            gini = sum((2 * i - n - 1) * x for i, x in enumerate(loads_sorted, 1))
            gini = gini / (n * sum(loads_sorted)) if sum(loads_sorted) > 0 else 0
        else:
            gini = 0
        
        return {
            'total_agents': len(self.agents),
            'active_tasks': total_tasks,
            'completed_tasks': total_completed,
            'avg_utilization': avg_load,
            'gini_coefficient': gini,
            'balance_quality': 'excellent' if gini < 0.2 else 'good' if gini < 0.4 else 'poor'
        }

if __name__ == '__main__':
    print('=== Load Balancer Demo ===')
    
    # Test different strategies
    for strategy in ['round_robin', 'least_loaded', 'fastest']:
        print(f'\nTesting {strategy} strategy:')
        lb = LoadBalancer(strategy=strategy)
        
        # Register agents with different capacities
        lb.register_agent('agent_001', capacity=10)
        lb.register_agent('agent_002', capacity=15)
        lb.register_agent('agent_003', capacity=8)
        
        # Assign tasks
        assignments = {}
        for i in range(20):
            agent = lb.assign_task(f'task_{i:03d}')
            if agent:
                assignments[agent] = assignments.get(agent, 0) + 1
        
        print(f'  Task distribution: {assignments}')
        
        # Simulate some completions
        for agent_id in assignments:
            for _ in range(assignments[agent_id] // 2):
                lb.complete_task(agent_id, random.uniform(0.5, 2.0))
        
        stats = lb.get_stats()
        print(f"  Utilization: {stats['avg_utilization']:.2%}")
        print(f"  Balance: {stats['balance_quality']} (Gini: {stats['gini_coefficient']:.3f})")
    
    print('\n=== System Operational ===')
