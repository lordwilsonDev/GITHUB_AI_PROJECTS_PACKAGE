#!/usr/bin/env python3
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List

class SpecializationType(Enum):
    GENERALIST = 'generalist'
    DATA_PROCESSING = 'data_processing'
    OPTIMIZATION = 'optimization'
    MONITORING = 'monitoring'
    COORDINATION = 'coordination'

@dataclass
class Skill:
    name: str
    level: int = 1
    xp: float = 0.0
    
    def update(self, success: bool, points: float = 10.0):
        self.xp += points if success else points * 0.5
        if self.xp >= 100 * self.level:
            self.level = min(6, self.level + 1)
            self.xp = 0

class SpecializationManager:
    def __init__(self):
        self.agents: Dict[str, Dict] = {}
    
    def register(self, agent_id: str, spec_type: SpecializationType):
        self.agents[agent_id] = {'type': spec_type, 'skills': {}}
    
    def record(self, agent_id: str, skill: str, success: bool, xp: float = 10.0):
        if agent_id not in self.agents:
            return
        if skill not in self.agents[agent_id]['skills']:
            self.agents[agent_id]['skills'][skill] = Skill(skill)
        self.agents[agent_id]['skills'][skill].update(success, xp)

class DynamicRoleAssigner:
    def __init__(self, mgr: SpecializationManager):
        self.mgr = mgr
        self.roles: Dict[str, str] = {}
    
    def assign(self, agent_id: str) -> str:
        if agent_id not in self.mgr.agents:
            return 'generalist'
        role = self.mgr.agents[agent_id]['type'].value
        self.roles[agent_id] = role
        return role

if __name__ == '__main__':
    print('=== Agent Specialization Demo ===')
    mgr = SpecializationManager()
    assigner = DynamicRoleAssigner(mgr)
    
    mgr.register('agent_001', SpecializationType.DATA_PROCESSING)
    mgr.register('agent_002', SpecializationType.OPTIMIZATION)
    mgr.register('agent_003', SpecializationType.MONITORING)
    
    mgr.record('agent_001', 'data_cleaning', True, 15.0)
    mgr.record('agent_001', 'data_cleaning', True, 15.0)
    mgr.record('agent_002', 'parameter_tuning', True, 20.0)
    mgr.record('agent_003', 'health_checking', True, 18.0)
    
    print('\nRole Assignments:')
    for aid in ['agent_001', 'agent_002', 'agent_003']:
        role = assigner.assign(aid)
        skills = mgr.agents[aid]['skills']
        print(f'  {aid} -> {role} ({len(skills)} skills)')
    
    print('\n=== System Operational ===')
