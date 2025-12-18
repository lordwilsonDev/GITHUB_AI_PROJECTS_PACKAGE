"""Workflow Analyzer.

Analyzes workflows to identify optimization opportunities.
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class WorkflowAnalyzer:
    """Analyzes workflows for optimization opportunities."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/workflows"):
        """Initialize the workflow analyzer.
        
        Args:
            data_dir: Directory for workflow data
        """
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Workflow definitions
        self.workflows: Dict[str, Dict[str, Any]] = {}
        
        # Analysis results
        self.bottlenecks: Dict[str, List[Dict[str, Any]]] = {}
        self.optimization_opportunities: List[Dict[str, Any]] = []
        
        self._load_data()
    
    def register_workflow(
        self,
        workflow_id: str,
        name: str,
        steps: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a workflow for analysis.
        
        Args:
            workflow_id: Unique workflow identifier
            name: Workflow name
            steps: List of workflow steps
            metadata: Optional metadata
        """
        self.workflows[workflow_id] = {
            'id': workflow_id,
            'name': name,
            'steps': steps,
            'metadata': metadata or {},
            'registered_at': datetime.now().isoformat(),
            'execution_count': 0,
            'total_duration': 0.0
        }
        
        self._save_data()
    
    def record_execution(
        self,
        workflow_id: str,
        step_durations: List[float],
        total_duration: float
    ) -> None:
        """Record a workflow execution.
        
        Args:
            workflow_id: Workflow ID
            step_durations: Duration of each step
            total_duration: Total workflow duration
        """
        if workflow_id not in self.workflows:
            return
        
        workflow = self.workflows[workflow_id]
        workflow['execution_count'] += 1
        workflow['total_duration'] += total_duration
        
        # Store step durations
        if 'step_durations' not in workflow:
            workflow['step_durations'] = [[] for _ in workflow['steps']]
        
        for i, duration in enumerate(step_durations):
            if i < len(workflow['step_durations']):
                workflow['step_durations'][i].append(duration)
        
        self._save_data()
    
    def analyze_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Analyze a specific workflow.
        
        Args:
            workflow_id: Workflow ID
        
        Returns:
            Analysis results
        """
        if workflow_id not in self.workflows:
            return {}
        
        workflow = self.workflows[workflow_id]
        
        # Calculate step statistics
        step_stats = []
        for i, step in enumerate(workflow['steps']):
            durations = workflow.get('step_durations', [[]])[i] if i < len(workflow.get('step_durations', [])) else []
            
            if durations:
                step_stats.append({
                    'step_index': i,
                    'step_name': step.get('name', f'Step {i}'),
                    'avg_duration': sum(durations) / len(durations),
                    'min_duration': min(durations),
                    'max_duration': max(durations),
                    'executions': len(durations)
                })
        
        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(step_stats)
        self.bottlenecks[workflow_id] = bottlenecks
        
        # Calculate efficiency
        avg_duration = workflow['total_duration'] / workflow['execution_count'] if workflow['execution_count'] > 0 else 0
        
        return {
            'workflow_id': workflow_id,
            'workflow_name': workflow['name'],
            'execution_count': workflow['execution_count'],
            'avg_duration': avg_duration,
            'step_stats': step_stats,
            'bottlenecks': bottlenecks,
            'optimization_score': self._calculate_optimization_score(step_stats, bottlenecks)
        }
    
    def _identify_bottlenecks(self, step_stats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify bottlenecks in workflow.
        
        Args:
            step_stats: Step statistics
        
        Returns:
            List of bottlenecks
        """
        if not step_stats:
            return []
        
        bottlenecks = []
        total_avg_duration = sum(s['avg_duration'] for s in step_stats)
        
        for step in step_stats:
            # Step is a bottleneck if it takes >30% of total time
            if step['avg_duration'] > total_avg_duration * 0.3:
                bottlenecks.append({
                    'step_index': step['step_index'],
                    'step_name': step['step_name'],
                    'avg_duration': step['avg_duration'],
                    'percentage_of_total': (step['avg_duration'] / total_avg_duration) * 100,
                    'severity': 'high' if step['avg_duration'] > total_avg_duration * 0.5 else 'medium'
                })
        
        return bottlenecks
    
    def _calculate_optimization_score(self, step_stats: List[Dict[str, Any]], bottlenecks: List[Dict[str, Any]]) -> float:
        """Calculate optimization potential score.
        
        Args:
            step_stats: Step statistics
            bottlenecks: Identified bottlenecks
        
        Returns:
            Optimization score (0-100)
        """
        if not step_stats:
            return 0.0
        
        # Base score from number of steps (more steps = more optimization potential)
        base_score = min(len(step_stats) * 5, 30)
        
        # Bottleneck score
        bottleneck_score = len(bottlenecks) * 20
        
        # Variance score (high variance = optimization potential)
        durations = [s['avg_duration'] for s in step_stats]
        if len(durations) > 1:
            avg = sum(durations) / len(durations)
            variance = sum((d - avg) ** 2 for d in durations) / len(durations)
            variance_score = min(variance * 10, 30)
        else:
            variance_score = 0
        
        return min(base_score + bottleneck_score + variance_score, 100)
    
    def suggest_optimizations(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Suggest optimizations for a workflow.
        
        Args:
            workflow_id: Workflow ID
        
        Returns:
            List of optimization suggestions
        """
        analysis = self.analyze_workflow(workflow_id)
        if not analysis:
            return []
        
        suggestions = []
        
        # Suggest parallelization for independent steps
        steps = self.workflows[workflow_id]['steps']
        parallel_candidates = self._find_parallel_candidates(steps)
        
        if parallel_candidates:
            suggestions.append({
                'type': 'parallelization',
                'description': 'Execute independent steps in parallel',
                'steps': parallel_candidates,
                'estimated_improvement': '20-40%',
                'priority': 'high'
            })
        
        # Suggest caching for repeated operations
        for step_stat in analysis['step_stats']:
            if step_stat['executions'] > 5 and step_stat['avg_duration'] > 1.0:
                suggestions.append({
                    'type': 'caching',
                    'description': f"Cache results for {step_stat['step_name']}",
                    'step_index': step_stat['step_index'],
                    'estimated_improvement': '30-50%',
                    'priority': 'medium'
                })
        
        # Suggest optimization for bottlenecks
        for bottleneck in analysis['bottlenecks']:
            suggestions.append({
                'type': 'bottleneck_optimization',
                'description': f"Optimize {bottleneck['step_name']} (takes {bottleneck['percentage_of_total']:.1f}% of time)",
                'step_index': bottleneck['step_index'],
                'estimated_improvement': '40-60%',
                'priority': bottleneck['severity']
            })
        
        return suggestions
    
    def _find_parallel_candidates(self, steps: List[Dict[str, Any]]) -> List[Tuple[int, int]]:
        """Find steps that can be executed in parallel.
        
        Args:
            steps: Workflow steps
        
        Returns:
            List of step index pairs that can run in parallel
        """
        candidates = []
        
        # Simple heuristic: steps with no dependencies can run in parallel
        for i in range(len(steps)):
            for j in range(i + 1, len(steps)):
                step_i = steps[i]
                step_j = steps[j]
                
                # Check if steps have no data dependencies
                # (simplified - in real implementation, would analyze inputs/outputs)
                if not self._have_dependencies(step_i, step_j):
                    candidates.append((i, j))
        
        return candidates
    
    def _have_dependencies(self, step1: Dict[str, Any], step2: Dict[str, Any]) -> bool:
        """Check if two steps have dependencies.
        
        Args:
            step1: First step
            step2: Second step
        
        Returns:
            True if steps have dependencies
        """
        # Simplified dependency check
        # In real implementation, would analyze data flow
        outputs1 = set(step1.get('outputs', []))
        inputs2 = set(step2.get('inputs', []))
        
        return bool(outputs1 & inputs2)
    
    def get_all_workflows(self) -> List[Dict[str, Any]]:
        """Get all registered workflows.
        
        Returns:
            List of workflows
        """
        return list(self.workflows.values())
    
    def _save_data(self) -> None:
        """Save workflow data."""
        data = {
            'workflows': self.workflows,
            'bottlenecks': self.bottlenecks,
            'optimization_opportunities': self.optimization_opportunities,
            'last_updated': datetime.now().isoformat()
        }
        
        filepath = self.data_dir / 'workflow_analysis.json'
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_data(self) -> None:
        """Load workflow data."""
        filepath = self.data_dir / 'workflow_analysis.json'
        
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                self.workflows = data.get('workflows', {})
                self.bottlenecks = data.get('bottlenecks', {})
                self.optimization_opportunities = data.get('optimization_opportunities', [])
            except Exception as e:
                print(f"Error loading workflow data: {e}")
