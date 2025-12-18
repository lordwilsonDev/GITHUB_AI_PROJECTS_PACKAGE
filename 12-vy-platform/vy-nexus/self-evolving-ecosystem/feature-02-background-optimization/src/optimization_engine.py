"""Background Process Optimization Engine

This module identifies repetitive tasks, creates micro-automations,
and optimizes existing processes based on performance data.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import json
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Represents a task or action performed by the system."""
    task_id: str
    task_type: str
    description: str
    parameters: Dict[str, Any]
    timestamp: datetime
    duration_ms: float
    success: bool
    user_context: Dict[str, Any] = field(default_factory=dict)
    
    def get_signature(self) -> str:
        """Generate a unique signature for task pattern matching."""
        sig_data = f"{self.task_type}:{json.dumps(self.parameters, sort_keys=True)}"
        return hashlib.md5(sig_data.encode()).hexdigest()


@dataclass
class RepetitivePattern:
    """Represents a detected repetitive task pattern."""
    pattern_id: str
    task_signature: str
    task_type: str
    occurrences: int
    first_seen: datetime
    last_seen: datetime
    avg_duration_ms: float
    automation_potential: float  # 0.0 to 1.0
    parameters_variance: Dict[str, Any]
    suggested_automation: Optional[str] = None


@dataclass
class MicroAutomation:
    """Represents a micro-automation script."""
    automation_id: str
    name: str
    description: str
    pattern_id: str
    script: str
    language: str  # 'python', 'bash', 'applescript'
    created_at: datetime
    tested: bool = False
    deployed: bool = False
    success_rate: float = 0.0
    execution_count: int = 0
    avg_time_saved_ms: float = 0.0


@dataclass
class PerformanceMetric:
    """Performance data for a process or workflow."""
    metric_id: str
    process_name: str
    timestamp: datetime
    duration_ms: float
    cpu_usage: float
    memory_usage: float
    success: bool
    bottlenecks: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)


class RepetitiveTaskIdentifier:
    """Identifies repetitive tasks that can be automated."""
    
    def __init__(self, min_occurrences: int = 3, time_window_hours: int = 24):
        self.min_occurrences = min_occurrences
        self.time_window_hours = time_window_hours
        self.task_history: List[Task] = []
        self.patterns: Dict[str, RepetitivePattern] = {}
        self.max_history_size = 10000
        
    def add_task(self, task: Task) -> None:
        """Add a task to the history for pattern analysis."""
        self.task_history.append(task)
        
        # Maintain history size limit
        if len(self.task_history) > self.max_history_size:
            self.task_history = self.task_history[-self.max_history_size:]
        
        # Update pattern detection
        self._update_patterns(task)
    
    def _update_patterns(self, task: Task) -> None:
        """Update pattern detection with new task."""
        signature = task.get_signature()
        
        if signature in self.patterns:
            pattern = self.patterns[signature]
            pattern.occurrences += 1
            pattern.last_seen = task.timestamp
            pattern.avg_duration_ms = (
                (pattern.avg_duration_ms * (pattern.occurrences - 1) + task.duration_ms) 
                / pattern.occurrences
            )
        else:
            # Create new pattern
            pattern_id = f"pattern_{signature[:8]}_{int(task.timestamp.timestamp())}"
            self.patterns[signature] = RepetitivePattern(
                pattern_id=pattern_id,
                task_signature=signature,
                task_type=task.task_type,
                occurrences=1,
                first_seen=task.timestamp,
                last_seen=task.timestamp,
                avg_duration_ms=task.duration_ms,
                automation_potential=0.0,
                parameters_variance={}
            )
    
    def identify_repetitive_patterns(self) -> List[RepetitivePattern]:
        """Identify patterns that occur frequently enough to automate."""
        cutoff_time = datetime.now() - timedelta(hours=self.time_window_hours)
        repetitive = []
        
        for pattern in self.patterns.values():
            if pattern.last_seen < cutoff_time:
                continue
                
            if pattern.occurrences >= self.min_occurrences:
                # Calculate automation potential
                pattern.automation_potential = self._calculate_automation_potential(pattern)
                repetitive.append(pattern)
        
        # Sort by automation potential
        repetitive.sort(key=lambda p: p.automation_potential, reverse=True)
        return repetitive
    
    def _calculate_automation_potential(self, pattern: RepetitivePattern) -> float:
        """Calculate how suitable a pattern is for automation (0.0 to 1.0)."""
        score = 0.0
        
        # Frequency score (0-0.4)
        freq_score = min(pattern.occurrences / 10.0, 1.0) * 0.4
        score += freq_score
        
        # Time savings score (0-0.3)
        if pattern.avg_duration_ms > 1000:  # More than 1 second
            time_score = min(pattern.avg_duration_ms / 10000.0, 1.0) * 0.3
            score += time_score
        
        # Recency score (0-0.3)
        hours_since = (datetime.now() - pattern.last_seen).total_seconds() / 3600
        recency_score = max(0, 1.0 - (hours_since / self.time_window_hours)) * 0.3
        score += recency_score
        
        return min(score, 1.0)
    
    def get_pattern_details(self, pattern_id: str) -> Optional[RepetitivePattern]:
        """Get details for a specific pattern."""
        for pattern in self.patterns.values():
            if pattern.pattern_id == pattern_id:
                return pattern
        return None


class MicroAutomationCreator:
    """Creates micro-automation scripts for repetitive tasks."""
    
    def __init__(self):
        self.automations: Dict[str, MicroAutomation] = {}
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load automation script templates."""
        return {
            'file_operation': '''
# File Operation Automation
import os
import shutil
from pathlib import Path

def execute(params):
    """Execute file operation automation."""
    operation = params.get('operation')
    source = params.get('source')
    destination = params.get('destination')
    
    if operation == 'copy':
        shutil.copy2(source, destination)
    elif operation == 'move':
        shutil.move(source, destination)
    elif operation == 'delete':
        os.remove(source)
    
    return {'success': True, 'operation': operation}
''',
            'data_processing': '''
# Data Processing Automation
import json
import csv

def execute(params):
    """Execute data processing automation."""
    input_file = params.get('input_file')
    output_file = params.get('output_file')
    operation = params.get('operation')
    
    # Load data
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Process based on operation
    result = process_data(data, operation)
    
    # Save result
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    return {'success': True, 'records_processed': len(result)}

def process_data(data, operation):
    # Custom processing logic
    return data
''',
            'api_call': '''
# API Call Automation
import requests
import json

def execute(params):
    """Execute API call automation."""
    url = params.get('url')
    method = params.get('method', 'GET')
    headers = params.get('headers', {})
    data = params.get('data', {})
    
    response = requests.request(method, url, headers=headers, json=data)
    
    return {
        'success': response.ok,
        'status_code': response.status_code,
        'data': response.json() if response.ok else None
    }
''',
            'workflow_sequence': '''
# Workflow Sequence Automation
import asyncio

async def execute(params):
    """Execute workflow sequence automation."""
    steps = params.get('steps', [])
    results = []
    
    for step in steps:
        result = await execute_step(step)
        results.append(result)
        
        if not result.get('success'):
            break
    
    return {
        'success': all(r.get('success') for r in results),
        'steps_completed': len(results),
        'results': results
    }

async def execute_step(step):
    # Execute individual step
    await asyncio.sleep(0.1)  # Simulate work
    return {'success': True, 'step': step}
'''
        }
    
    def create_automation(self, pattern: RepetitivePattern, 
                         template_type: str = 'workflow_sequence') -> MicroAutomation:
        """Create a micro-automation for a repetitive pattern."""
        automation_id = f"auto_{pattern.pattern_id}_{int(datetime.now().timestamp())}"
        
        # Select appropriate template
        script = self.templates.get(template_type, self.templates['workflow_sequence'])
        
        automation = MicroAutomation(
            automation_id=automation_id,
            name=f"Automation for {pattern.task_type}",
            description=f"Automates repetitive {pattern.task_type} tasks",
            pattern_id=pattern.pattern_id,
            script=script,
            language='python',
            created_at=datetime.now()
        )
        
        self.automations[automation_id] = automation
        pattern.suggested_automation = automation_id
        
        return automation
    
    def customize_automation(self, automation_id: str, 
                           custom_script: str) -> bool:
        """Customize an automation script."""
        if automation_id in self.automations:
            self.automations[automation_id].script = custom_script
            self.automations[automation_id].tested = False  # Needs retesting
            return True
        return False
    
    def get_automation(self, automation_id: str) -> Optional[MicroAutomation]:
        """Get automation by ID."""
        return self.automations.get(automation_id)
    
    def list_automations(self, deployed_only: bool = False) -> List[MicroAutomation]:
        """List all automations."""
        automations = list(self.automations.values())
        if deployed_only:
            automations = [a for a in automations if a.deployed]
        return automations


class PerformanceAnalyzer:
    """Analyzes performance data to identify optimization opportunities."""
    
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.max_metrics = 5000
        self.bottleneck_threshold_ms = 1000  # 1 second
    
    def add_metric(self, metric: PerformanceMetric) -> None:
        """Add a performance metric."""
        self.metrics.append(metric)
        
        # Maintain size limit
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics:]
        
        # Analyze for bottlenecks
        self._analyze_bottlenecks(metric)
    
    def _analyze_bottlenecks(self, metric: PerformanceMetric) -> None:
        """Analyze metric for performance bottlenecks."""
        if metric.duration_ms > self.bottleneck_threshold_ms:
            metric.bottlenecks.append(f"High duration: {metric.duration_ms}ms")
        
        if metric.cpu_usage > 80.0:
            metric.bottlenecks.append(f"High CPU usage: {metric.cpu_usage}%")
        
        if metric.memory_usage > 80.0:
            metric.bottlenecks.append(f"High memory usage: {metric.memory_usage}%")
        
        # Generate optimization suggestions
        if metric.bottlenecks:
            self._generate_suggestions(metric)
    
    def _generate_suggestions(self, metric: PerformanceMetric) -> None:
        """Generate optimization suggestions based on bottlenecks."""
        if metric.duration_ms > self.bottleneck_threshold_ms:
            metric.optimization_suggestions.append(
                "Consider caching results or parallelizing operations"
            )
        
        if metric.cpu_usage > 80.0:
            metric.optimization_suggestions.append(
                "Optimize CPU-intensive operations or distribute load"
            )
        
        if metric.memory_usage > 80.0:
            metric.optimization_suggestions.append(
                "Reduce memory footprint or implement streaming processing"
            )
    
    def get_process_statistics(self, process_name: str, 
                              hours: int = 24) -> Dict[str, Any]:
        """Get statistics for a specific process."""
        cutoff = datetime.now() - timedelta(hours=hours)
        process_metrics = [
            m for m in self.metrics 
            if m.process_name == process_name and m.timestamp > cutoff
        ]
        
        if not process_metrics:
            return {}
        
        return {
            'process_name': process_name,
            'total_executions': len(process_metrics),
            'success_rate': sum(1 for m in process_metrics if m.success) / len(process_metrics),
            'avg_duration_ms': sum(m.duration_ms for m in process_metrics) / len(process_metrics),
            'avg_cpu_usage': sum(m.cpu_usage for m in process_metrics) / len(process_metrics),
            'avg_memory_usage': sum(m.memory_usage for m in process_metrics) / len(process_metrics),
            'bottleneck_count': sum(len(m.bottlenecks) for m in process_metrics),
            'common_bottlenecks': self._get_common_bottlenecks(process_metrics)
        }
    
    def _get_common_bottlenecks(self, metrics: List[PerformanceMetric]) -> List[Tuple[str, int]]:
        """Get most common bottlenecks."""
        all_bottlenecks = []
        for metric in metrics:
            all_bottlenecks.extend(metric.bottlenecks)
        
        counter = Counter(all_bottlenecks)
        return counter.most_common(5)
    
    def identify_slow_processes(self, threshold_ms: float = 2000) -> List[str]:
        """Identify processes that are consistently slow."""
        process_stats = defaultdict(list)
        
        for metric in self.metrics:
            process_stats[metric.process_name].append(metric.duration_ms)
        
        slow_processes = []
        for process, durations in process_stats.items():
            avg_duration = sum(durations) / len(durations)
            if avg_duration > threshold_ms:
                slow_processes.append(process)
        
        return slow_processes


class WorkflowOptimizer:
    """Optimizes workflows based on performance data and patterns."""
    
    def __init__(self, performance_analyzer: PerformanceAnalyzer):
        self.performance_analyzer = performance_analyzer
        self.optimizations: Dict[str, Dict[str, Any]] = {}
    
    def analyze_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Analyze a workflow for optimization opportunities."""
        stats = self.performance_analyzer.get_process_statistics(workflow_name)
        
        if not stats:
            return {'workflow': workflow_name, 'status': 'no_data'}
        
        optimizations = []
        
        # Check success rate
        if stats['success_rate'] < 0.95:
            optimizations.append({
                'type': 'reliability',
                'priority': 'high',
                'suggestion': 'Improve error handling and retry logic',
                'current_rate': stats['success_rate']
            })
        
        # Check performance
        if stats['avg_duration_ms'] > 5000:
            optimizations.append({
                'type': 'performance',
                'priority': 'medium',
                'suggestion': 'Optimize slow operations or add caching',
                'current_duration': stats['avg_duration_ms']
            })
        
        # Check resource usage
        if stats['avg_cpu_usage'] > 70:
            optimizations.append({
                'type': 'resource',
                'priority': 'medium',
                'suggestion': 'Reduce CPU usage through optimization',
                'current_cpu': stats['avg_cpu_usage']
            })
        
        return {
            'workflow': workflow_name,
            'statistics': stats,
            'optimizations': optimizations,
            'optimization_score': self._calculate_optimization_score(stats)
        }
    
    def _calculate_optimization_score(self, stats: Dict[str, Any]) -> float:
        """Calculate how much a workflow needs optimization (0-1, higher = more needed)."""
        score = 0.0
        
        # Success rate impact
        if stats['success_rate'] < 1.0:
            score += (1.0 - stats['success_rate']) * 0.4
        
        # Duration impact
        if stats['avg_duration_ms'] > 1000:
            score += min(stats['avg_duration_ms'] / 10000, 0.3)
        
        # Resource usage impact
        if stats['avg_cpu_usage'] > 50:
            score += (stats['avg_cpu_usage'] - 50) / 100 * 0.3
        
        return min(score, 1.0)
    
    def suggest_workflow_improvements(self, workflow_name: str) -> List[str]:
        """Suggest specific improvements for a workflow."""
        analysis = self.analyze_workflow(workflow_name)
        suggestions = []
        
        for opt in analysis.get('optimizations', []):
            suggestions.append(opt['suggestion'])
        
        # Add bottleneck-specific suggestions
        stats = analysis.get('statistics', {})
        for bottleneck, count in stats.get('common_bottlenecks', []):
            suggestions.append(f"Address bottleneck: {bottleneck} (occurs {count} times)")
        
        return suggestions


class OptimizationEngine:
    """Main orchestrator for background process optimization."""
    
    def __init__(self):
        self.task_identifier = RepetitiveTaskIdentifier()
        self.automation_creator = MicroAutomationCreator()
        self.performance_analyzer = PerformanceAnalyzer()
        self.workflow_optimizer = WorkflowOptimizer(self.performance_analyzer)
        self.running = False
        logger.info("Optimization Engine initialized")
    
    async def start(self) -> None:
        """Start the optimization engine."""
        self.running = True
        logger.info("Optimization Engine started")
        
        # Start background optimization cycle
        asyncio.create_task(self._optimization_cycle())
    
    async def stop(self) -> None:
        """Stop the optimization engine."""
        self.running = False
        logger.info("Optimization Engine stopped")
    
    async def _optimization_cycle(self) -> None:
        """Main optimization cycle running in background."""
        while self.running:
            try:
                # Identify repetitive patterns
                patterns = self.task_identifier.identify_repetitive_patterns()
                
                # Create automations for high-potential patterns
                for pattern in patterns[:5]:  # Top 5 patterns
                    if pattern.automation_potential > 0.7 and not pattern.suggested_automation:
                        automation = self.automation_creator.create_automation(pattern)
                        logger.info(f"Created automation: {automation.automation_id}")
                
                # Analyze slow processes
                slow_processes = self.performance_analyzer.identify_slow_processes()
                for process in slow_processes:
                    suggestions = self.workflow_optimizer.suggest_workflow_improvements(process)
                    logger.info(f"Optimization suggestions for {process}: {suggestions}")
                
                # Wait before next cycle
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Error in optimization cycle: {e}")
                await asyncio.sleep(60)
    
    def record_task(self, task: Task) -> None:
        """Record a task for pattern analysis."""
        self.task_identifier.add_task(task)
    
    def record_performance(self, metric: PerformanceMetric) -> None:
        """Record performance metric."""
        self.performance_analyzer.add_metric(metric)
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report."""
        patterns = self.task_identifier.identify_repetitive_patterns()
        automations = self.automation_creator.list_automations()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'repetitive_patterns': len(patterns),
            'high_potential_patterns': len([p for p in patterns if p.automation_potential > 0.7]),
            'automations_created': len(automations),
            'automations_deployed': len([a for a in automations if a.deployed]),
            'top_patterns': [
                {
                    'pattern_id': p.pattern_id,
                    'task_type': p.task_type,
                    'occurrences': p.occurrences,
                    'automation_potential': p.automation_potential
                }
                for p in patterns[:10]
            ],
            'performance_summary': {
                'total_metrics': len(self.performance_analyzer.metrics),
                'slow_processes': self.performance_analyzer.identify_slow_processes()
            }
        }
