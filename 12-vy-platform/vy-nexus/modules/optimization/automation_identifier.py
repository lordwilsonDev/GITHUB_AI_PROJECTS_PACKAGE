#!/usr/bin/env python3
"""
Background Process Optimization - Automation Identifier
Identifies repetitive tasks that can be automated
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Set
from pathlib import Path
from collections import defaultdict
import hashlib

class AutomationIdentifier:
    """Identifies repetitive tasks suitable for automation"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.expanduser("~/vy-nexus/data/automation")
        self.tasks_file = os.path.join(self.data_dir, "tasks.jsonl")
        self.automations_file = os.path.join(self.data_dir, "automations.jsonl")
        self.candidates_file = os.path.join(self.data_dir, "automation_candidates.jsonl")
        
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        
        self.task_sequences = defaultdict(list)
        self.automation_candidates = []
    
    def record_task(self, task: Dict[str, Any]):
        """
        Record a task execution for analysis
        
        Args:
            task: Task details including type, steps, parameters, etc.
        """
        task_record = {
            'id': self._generate_task_id(task),
            'timestamp': datetime.now().isoformat(),
            'type': task.get('type', 'unknown'),
            'steps': task.get('steps', []),
            'parameters': task.get('parameters', {}),
            'duration': task.get('duration', 0),
            'frequency_key': self._generate_frequency_key(task)
        }
        
        # Save task record
        with open(self.tasks_file, 'a') as f:
            f.write(json.dumps(task_record) + '\n')
        
        # Add to sequence tracking
        self.task_sequences[task_record['frequency_key']].append(task_record)
        
        # Analyze for automation opportunities
        self._analyze_for_automation()
    
    def _generate_task_id(self, task: Dict[str, Any]) -> str:
        """Generate unique task ID"""
        content = f"{task.get('type')}:{json.dumps(task.get('steps', []), sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _generate_frequency_key(self, task: Dict[str, Any]) -> str:
        """
        Generate a key for tracking task frequency
        Normalizes task to identify similar executions
        """
        # Create normalized representation
        key_parts = [
            task.get('type', 'unknown'),
            str(sorted(task.get('steps', []))),
            str(sorted(task.get('parameters', {}).keys()))
        ]
        
        key_string = '|'.join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()[:16]
    
    def _analyze_for_automation(self):
        """Analyze recorded tasks for automation opportunities"""
        # Load recent tasks
        recent_tasks = self._load_recent_tasks(days=30)
        
        # Group by frequency key
        task_groups = defaultdict(list)
        for task in recent_tasks:
            task_groups[task['frequency_key']].append(task)
        
        # Identify candidates
        candidates = []
        
        for freq_key, tasks in task_groups.items():
            if len(tasks) >= 3:  # Occurred at least 3 times
                # Calculate metrics
                avg_duration = sum(t['duration'] for t in tasks) / len(tasks)
                total_time_spent = sum(t['duration'] for t in tasks)
                
                # Check if worth automating (significant time savings)
                if total_time_spent > 300:  # More than 5 minutes total
                    candidate = {
                        'id': freq_key,
                        'task_type': tasks[0]['type'],
                        'occurrence_count': len(tasks),
                        'avg_duration': avg_duration,
                        'total_time_spent': total_time_spent,
                        'potential_savings': total_time_spent * 0.8,  # 80% time savings
                        'steps': tasks[0]['steps'],
                        'parameters': tasks[0]['parameters'],
                        'first_seen': tasks[0]['timestamp'],
                        'last_seen': tasks[-1]['timestamp'],
                        'priority': self._calculate_priority(len(tasks), total_time_spent),
                        'automation_complexity': self._estimate_complexity(tasks[0])
                    }
                    
                    candidates.append(candidate)
        
        # Save new candidates
        for candidate in candidates:
            if not self._candidate_exists(candidate['id']):
                with open(self.candidates_file, 'a') as f:
                    f.write(json.dumps(candidate) + '\n')
                
                self.automation_candidates.append(candidate)
    
    def _load_recent_tasks(self, days: int = 30) -> List[Dict[str, Any]]:
        """Load tasks from the last N days"""
        if not os.path.exists(self.tasks_file):
            return []
        
        cutoff = datetime.now() - timedelta(days=days)
        tasks = []
        
        with open(self.tasks_file, 'r') as f:
            for line in f:
                if line.strip():
                    task = json.loads(line)
                    if datetime.fromisoformat(task['timestamp']) > cutoff:
                        tasks.append(task)
        
        return tasks
    
    def _candidate_exists(self, candidate_id: str) -> bool:
        """Check if automation candidate already exists"""
        if not os.path.exists(self.candidates_file):
            return False
        
        with open(self.candidates_file, 'r') as f:
            for line in f:
                if line.strip():
                    candidate = json.loads(line)
                    if candidate['id'] == candidate_id:
                        return True
        
        return False
    
    def _calculate_priority(self, occurrence_count: int, total_time: float) -> str:
        """Calculate automation priority"""
        score = occurrence_count * total_time
        
        if score > 5000:
            return 'critical'
        elif score > 2000:
            return 'high'
        elif score > 500:
            return 'medium'
        else:
            return 'low'
    
    def _estimate_complexity(self, task: Dict[str, Any]) -> str:
        """Estimate automation complexity"""
        steps = task.get('steps', [])
        params = task.get('parameters', {})
        
        complexity_score = len(steps) + len(params) * 2
        
        if complexity_score > 20:
            return 'high'
        elif complexity_score > 10:
            return 'medium'
        else:
            return 'low'
    
    def get_automation_candidates(self, priority: str = None, 
                                 max_complexity: str = None) -> List[Dict[str, Any]]:
        """
        Get automation candidates
        
        Args:
            priority: Filter by priority (critical, high, medium, low)
            max_complexity: Maximum complexity (low, medium, high)
            
        Returns:
            List of automation candidates
        """
        if not os.path.exists(self.candidates_file):
            return []
        
        candidates = []
        complexity_order = {'low': 1, 'medium': 2, 'high': 3}
        
        with open(self.candidates_file, 'r') as f:
            for line in f:
                if line.strip():
                    candidate = json.loads(line)
                    
                    # Apply filters
                    if priority and candidate['priority'] != priority:
                        continue
                    
                    if max_complexity:
                        if complexity_order.get(candidate['automation_complexity'], 3) > \
                           complexity_order.get(max_complexity, 3):
                            continue
                    
                    candidates.append(candidate)
        
        # Sort by priority and potential savings
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        candidates.sort(key=lambda x: (priority_order.get(x['priority'], 4), 
                                      -x['potential_savings']))
        
        return candidates
    
    def create_automation(self, candidate_id: str, automation_script: str, 
                         metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create an automation from a candidate
        
        Args:
            candidate_id: ID of the automation candidate
            automation_script: Path or content of automation script
            metadata: Additional metadata
            
        Returns:
            Automation record
        """
        # Find candidate
        candidate = None
        candidates = self.get_automation_candidates()
        for c in candidates:
            if c['id'] == candidate_id:
                candidate = c
                break
        
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")
        
        automation = {
            'id': f"auto_{candidate_id}",
            'candidate_id': candidate_id,
            'created': datetime.now().isoformat(),
            'task_type': candidate['task_type'],
            'script': automation_script,
            'status': 'active',
            'execution_count': 0,
            'total_time_saved': 0.0,
            'metadata': metadata or {}
        }
        
        # Save automation
        with open(self.automations_file, 'a') as f:
            f.write(json.dumps(automation) + '\n')
        
        return automation
    
    def record_automation_execution(self, automation_id: str, 
                                   duration: float, success: bool):
        """Record an automation execution"""
        execution = {
            'automation_id': automation_id,
            'timestamp': datetime.now().isoformat(),
            'duration': duration,
            'success': success
        }
        
        # Save execution record
        execution_file = os.path.join(self.data_dir, "automation_executions.jsonl")
        with open(execution_file, 'a') as f:
            f.write(json.dumps(execution) + '\n')
    
    def get_automation_statistics(self) -> Dict[str, Any]:
        """Get statistics about automations"""
        candidates = self.get_automation_candidates()
        
        total_potential_savings = sum(c['potential_savings'] for c in candidates)
        
        by_priority = defaultdict(int)
        for c in candidates:
            by_priority[c['priority']] += 1
        
        return {
            'total_candidates': len(candidates),
            'by_priority': dict(by_priority),
            'total_potential_time_savings': total_potential_savings,
            'high_priority_count': by_priority.get('critical', 0) + by_priority.get('high', 0)
        }


if __name__ == "__main__":
    # Test the automation identifier
    identifier = AutomationIdentifier()
    
    # Simulate repetitive tasks
    for i in range(5):
        task = {
            'type': 'data_processing',
            'steps': ['load_data', 'transform', 'save'],
            'parameters': {'format': 'json', 'output': 'processed'},
            'duration': 120 + i * 10
        }
        identifier.record_task(task)
    
    # Get candidates
    candidates = identifier.get_automation_candidates()
    print(f"Found {len(candidates)} automation candidates")
    
    for candidate in candidates:
        print(f"\nCandidate: {candidate['task_type']}")
        print(f"  Priority: {candidate['priority']}")
        print(f"  Occurrences: {candidate['occurrence_count']}")
        print(f"  Potential savings: {candidate['potential_savings']:.1f}s")
    
    # Get statistics
    stats = identifier.get_automation_statistics()
    print("\nAutomation Statistics:")
    print(json.dumps(stats, indent=2))
