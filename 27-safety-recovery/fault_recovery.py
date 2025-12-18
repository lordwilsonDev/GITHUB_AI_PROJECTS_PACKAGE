#!/usr/bin/env python3
import time
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class AgentState(Enum):
    ACTIVE = 'active'
    FAILED = 'failed'
    RECOVERING = 'recovering'
    TERMINATED = 'terminated'

@dataclass
class AgentHealth:
    agent_id: str
    state: AgentState = AgentState.ACTIVE
    last_heartbeat: float = 0.0
    failure_count: int = 0
    recovery_attempts: int = 0
    
    def is_healthy(self, timeout: float = 30.0) -> bool:
        return (time.time() - self.last_heartbeat) < timeout

class FaultRecoverySystem:
    def __init__(self, max_recovery_attempts: int = 3):
        self.agents: Dict[str, AgentHealth] = {}
        self.max_attempts = max_recovery_attempts
        self.lock = threading.Lock()
    
    def register_agent(self, agent_id: str):
        with self.lock:
            self.agents[agent_id] = AgentHealth(agent_id)
            self.agents[agent_id].last_heartbeat = time.time()
    
    def heartbeat(self, agent_id: str):
        with self.lock:
            if agent_id in self.agents:
                self.agents[agent_id].last_heartbeat = time.time()
                if self.agents[agent_id].state == AgentState.RECOVERING:
                    self.agents[agent_id].state = AgentState.ACTIVE
                    self.agents[agent_id].recovery_attempts = 0
    
    def check_health(self) -> List[str]:
        failed = []
        with self.lock:
            for agent_id, health in self.agents.items():
                if not health.is_healthy() and health.state == AgentState.ACTIVE:
                    health.state = AgentState.FAILED
                    health.failure_count += 1
                    failed.append(agent_id)
        return failed
    
    def attempt_recovery(self, agent_id: str) -> bool:
        with self.lock:
            if agent_id not in self.agents:
                return False
            
            health = self.agents[agent_id]
            if health.recovery_attempts >= self.max_attempts:
                health.state = AgentState.TERMINATED
                return False
            
            health.state = AgentState.RECOVERING
            health.recovery_attempts += 1
            return True
    
    def get_status(self) -> Dict:
        with self.lock:
            return {
                'total': len(self.agents),
                'active': sum(1 for h in self.agents.values() if h.state == AgentState.ACTIVE),
                'failed': sum(1 for h in self.agents.values() if h.state == AgentState.FAILED),
                'recovering': sum(1 for h in self.agents.values() if h.state == AgentState.RECOVERING),
                'terminated': sum(1 for h in self.agents.values() if h.state == AgentState.TERMINATED)
            }

if __name__ == '__main__':
    print('=== Fault Recovery System Demo ===')
    recovery = FaultRecoverySystem(max_recovery_attempts=3)
    
    # Register agents
    for i in range(1, 4):
        recovery.register_agent(f'agent_{i:03d}')
    
    # Simulate heartbeats
    recovery.heartbeat('agent_001')
    recovery.heartbeat('agent_002')
    # agent_003 misses heartbeat
    
    time.sleep(0.1)
    
    # Check health
    print('\nChecking health...')
    status = recovery.get_status()
    print(f"  Active: {status['active']}, Failed: {status['failed']}")
    
    # Attempt recovery
    print('\nAttempting recovery for agent_003...')
    if recovery.attempt_recovery('agent_003'):
        print('  Recovery initiated')
        recovery.heartbeat('agent_003')  # Simulate successful recovery
    
    status = recovery.get_status()
    print(f"\nFinal status: Active: {status['active']}, Recovering: {status['recovering']}")
    print('\n=== System Operational ===')
