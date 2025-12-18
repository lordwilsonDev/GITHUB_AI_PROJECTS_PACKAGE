#!/usr/bin/env python3
"""
MoIE-OS Enterprise Orchestrator
Unified coordination layer for Levels 8-13
"""

import json
import time
import threading
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from enum import Enum
import hashlib
from datetime import datetime

class SystemStatus(Enum):
    INITIALIZING = 'initializing'
    HEALTHY = 'healthy'
    DEGRADED = 'degraded'
    CRITICAL = 'critical'
    OFFLINE = 'offline'

@dataclass
class LevelStatus:
    level: int
    name: str
    status: SystemStatus
    health_score: float  # 0.0-1.0
    last_check: float
    metrics: Dict[str, Any]
    errors: List[str]

class EnterpriseOrchestrator:
    """Main orchestrator coordinating all MoIE-OS levels"""
    
    def __init__(self):
        self.levels = {}
        self.system_status = SystemStatus.INITIALIZING
        self.start_time = time.time()
        self.health_check_interval = 30  # seconds
        self.monitoring_thread = None
        self.running = False
        
        # Initialize level configurations
        self.level_configs = {
            8: {'name': 'Semantic Routing', 'critical': True},
            9: {'name': 'Autonomous Healing', 'critical': True},
            10: {'name': 'Swarm Intelligence', 'critical': False},
            11: {'name': 'Predictive Intelligence', 'critical': False},
            12: {'name': 'Recursive Self-Improvement', 'critical': True},
            13: {'name': 'Cross-System Intelligence', 'critical': False}
        }
        
    def initialize(self):
        """Initialize all system levels"""
        print('\n⚙️  Initializing Enterprise Orchestrator...')
        
        for level_num, config in self.level_configs.items():
            try:
                status = self._check_level(level_num)
                self.levels[level_num] = status
                print(f'  Level {level_num} ({config["name"]}): {status.status.value}')
            except Exception as e:
                print(f'  Level {level_num}: ERROR - {e}')
                self.levels[level_num] = LevelStatus(
                    level=level_num,
                    name=config['name'],
                    status=SystemStatus.OFFLINE,
                    health_score=0.0,
                    last_check=time.time(),
                    metrics={},
                    errors=[str(e)]
                )
        
        self._update_system_status()
        print(f'\n✅ System Status: {self.system_status.value.upper()}')
        return self.system_status
    
    def _check_level(self, level_num: int) -> LevelStatus:
        """Check health of a specific level"""
        import os
        
        # Check if level files exist
        level_files = {
            8: ['semantic_router.py', 'transformer_core.py'],
            9: ['autonomous_core.py', 'decision_engine.py'],
            10: ['agent_core.py', 'swarm_coordinator.py'],
            11: ['mini_mind_core.py', 'workflow_synthesizer.py'],
            12: ['blueprint_reader.py', 'improvement_generator.py'],
            13: ['language_detector.py', 'universal_ast.py']
        }
        
        files = level_files.get(level_num, [])
        existing_files = [f for f in files if os.path.exists(os.path.expanduser(f'~/{f}'))]
        
        health_score = len(existing_files) / len(files) if files else 0.0
        
        if health_score >= 0.8:
            status = SystemStatus.HEALTHY
        elif health_score >= 0.5:
            status = SystemStatus.DEGRADED
        elif health_score > 0:
            status = SystemStatus.CRITICAL
        else:
            status = SystemStatus.OFFLINE
        
        return LevelStatus(
            level=level_num,
            name=self.level_configs[level_num]['name'],
            status=status,
            health_score=health_score,
            last_check=time.time(),
            metrics={'files_found': len(existing_files), 'files_expected': len(files)},
            errors=[]
        )
    
    def _update_system_status(self):
        """Update overall system status based on level health"""
        critical_levels = [l for l, c in self.level_configs.items() if c['critical']]
        
        # Check critical levels
        critical_offline = any(
            self.levels[l].status == SystemStatus.OFFLINE 
            for l in critical_levels if l in self.levels
        )
        critical_degraded = any(
            self.levels[l].status in [SystemStatus.DEGRADED, SystemStatus.CRITICAL]
            for l in critical_levels if l in self.levels
        )
        
        if critical_offline:
            self.system_status = SystemStatus.CRITICAL
        elif critical_degraded:
            self.system_status = SystemStatus.DEGRADED
        else:
            # Check overall health score
            avg_health = sum(l.health_score for l in self.levels.values()) / len(self.levels)
            if avg_health >= 0.9:
                self.system_status = SystemStatus.HEALTHY
            elif avg_health >= 0.7:
                self.system_status = SystemStatus.DEGRADED
            else:
                self.system_status = SystemStatus.CRITICAL
    
    def start_monitoring(self):
        """Start continuous health monitoring"""
        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        print('\n👁️  Monitoring started')
    
    def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.running:
            time.sleep(self.health_check_interval)
            for level_num in self.levels.keys():
                self.levels[level_num] = self._check_level(level_num)
            self._update_system_status()
    
    def get_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive status report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': time.time() - self.start_time,
            'system_status': self.system_status.value,
            'levels': {
                level_num: asdict(status) 
                for level_num, status in self.levels.items()
            },
            'summary': {
                'total_levels': len(self.levels),
                'healthy': sum(1 for l in self.levels.values() if l.status == SystemStatus.HEALTHY),
                'degraded': sum(1 for l in self.levels.values() if l.status == SystemStatus.DEGRADED),
                'critical': sum(1 for l in self.levels.values() if l.status == SystemStatus.CRITICAL),
                'offline': sum(1 for l in self.levels.values() if l.status == SystemStatus.OFFLINE),
                'avg_health_score': sum(l.health_score for l in self.levels.values()) / len(self.levels)
            }
        }
    
    def execute_task(self, task_type: str, **kwargs) -> Dict[str, Any]:
        """Execute a task using appropriate level"""
        # Route to appropriate level based on task type
        routing = {
            'semantic_search': 8,
            'heal_failure': 9,
            'distribute_work': 10,
            'predict_failure': 11,
            'improve_code': 12,
            'analyze_external': 13
        }
        
        level = routing.get(task_type)
        if not level:
            return {'success': False, 'error': f'Unknown task type: {task_type}'}
        
        if level not in self.levels or self.levels[level].status == SystemStatus.OFFLINE:
            return {'success': False, 'error': f'Level {level} is offline'}
        
        # Simulate task execution
        return {
            'success': True,
            'level': level,
            'task_type': task_type,
            'result': f'Task executed by Level {level}',
            'timestamp': time.time()
        }
    
    def shutdown(self):
        """Graceful shutdown"""
        print('\n🛑 Shutting down Enterprise Orchestrator...')
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        print('✅ Shutdown complete')

if __name__ == '__main__':
    # Demo
    orchestrator = EnterpriseOrchestrator()
    orchestrator.initialize()
    
    # Get status report
    report = orchestrator.get_status_report()
    print(f'\n📊 Status Report:')
    print(f'  System: {report["system_status"]}')
    print(f'  Uptime: {report["uptime_seconds"]:.1f}s')
    print(f'  Healthy: {report["summary"]["healthy"]}/{report["summary"]["total_levels"]}')
    print(f'  Avg Health: {report["summary"]["avg_health_score"]:.2%}')
    
    # Test task execution
    print(f'\n🚀 Testing Task Execution:')
    tasks = ['semantic_search', 'heal_failure', 'predict_failure']
    for task in tasks:
        result = orchestrator.execute_task(task)
        print(f'  {task}: {"SUCCESS" if result["success"] else "FAILED"}')
    
    print('\n✅ Enterprise Orchestrator Demo Complete!')
