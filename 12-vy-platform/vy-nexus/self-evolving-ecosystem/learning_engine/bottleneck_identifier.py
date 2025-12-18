#!/usr/bin/env python3
"""
Bottleneck Identifier
Identifies and analyzes performance bottlenecks in workflows and processes
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict

@dataclass
class Bottleneck:
    """Represents an identified bottleneck"""
    id: str
    name: str
    category: str  # performance, workflow, resource, communication, etc.
    description: str
    identified_date: str
    severity: str  # critical, high, medium, low
    impact_area: str
    affected_workflows: List[str]
    root_cause: Optional[str] = None
    symptoms: List[str] = None
    metrics: Dict[str, float] = None  # time_lost, frequency, cost, etc.
    proposed_solutions: List[str] = None
    status: str = "identified"  # identified, analyzing, resolving, resolved
    resolution_date: Optional[str] = None
    resolution_notes: str = ""
    recurrence_count: int = 1

@dataclass
class PerformanceMetric:
    """Performance metric for bottleneck analysis"""
    timestamp: str
    workflow_name: str
    step_name: str
    execution_time: float
    expected_time: float
    resource_usage: Dict[str, float]
    success: bool
    error_message: Optional[str] = None

class BottleneckIdentifier:
    """Identifies and tracks performance bottlenecks"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_dir = Path("/Users/lordwilson/vy-nexus/self-evolving-ecosystem/data/bottlenecks")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.bottlenecks_file = self.base_dir / "bottlenecks.jsonl"
        self.metrics_file = self.base_dir / "performance_metrics.jsonl"
        self.resolutions_file = self.base_dir / "resolutions.jsonl"
        
        self.bottlenecks: Dict[str, Bottleneck] = {}
        self.metrics: List[PerformanceMetric] = []
        self.load_bottlenecks()
        
        self._initialized = True
    
    def load_bottlenecks(self):
        """Load bottlenecks from storage"""
        if self.bottlenecks_file.exists():
            with open(self.bottlenecks_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        # Handle None values
                        for field in ['symptoms', 'proposed_solutions']:
                            if data.get(field) is None:
                                data[field] = []
                        if data.get('metrics') is None:
                            data['metrics'] = {}
                        bottleneck = Bottleneck(**data)
                        self.bottlenecks[bottleneck.id] = bottleneck
    
    def record_performance_metric(self, workflow_name: str, step_name: str,
                                 execution_time: float, expected_time: float,
                                 resource_usage: Dict[str, float],
                                 success: bool = True,
                                 error_message: str = None):
        """Record a performance metric"""
        metric = PerformanceMetric(
            timestamp=datetime.now().isoformat(),
            workflow_name=workflow_name,
            step_name=step_name,
            execution_time=execution_time,
            expected_time=expected_time,
            resource_usage=resource_usage,
            success=success,
            error_message=error_message
        )
        
        self.metrics.append(metric)
        
        # Save metric
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(asdict(metric)) + '\n')
        
        # Check if this indicates a bottleneck
        if execution_time > expected_time * 1.5:  # 50% slower than expected
            self._check_for_bottleneck(workflow_name, step_name, metric)
    
    def _check_for_bottleneck(self, workflow_name: str, step_name: str,
                             metric: PerformanceMetric):
        """Check if metrics indicate a bottleneck"""
        bottleneck_id = f"{workflow_name}_{step_name}"
        
        if bottleneck_id in self.bottlenecks:
            # Existing bottleneck - increment recurrence
            bottleneck = self.bottlenecks[bottleneck_id]
            bottleneck.recurrence_count += 1
            
            # Update metrics
            if bottleneck.metrics:
                bottleneck.metrics['avg_time_lost'] = (
                    (bottleneck.metrics.get('avg_time_lost', 0) * (bottleneck.recurrence_count - 1) +
                     (metric.execution_time - metric.expected_time)) / bottleneck.recurrence_count
                )
            
            self._save_bottleneck(bottleneck)
        else:
            # New bottleneck
            severity = self._calculate_severity(metric)
            
            bottleneck = Bottleneck(
                id=bottleneck_id,
                name=f"{workflow_name} - {step_name}",
                category="performance",
                description=f"Step '{step_name}' in workflow '{workflow_name}' is slower than expected",
                identified_date=datetime.now().isoformat(),
                severity=severity,
                impact_area=workflow_name,
                affected_workflows=[workflow_name],
                symptoms=[f"Execution time {metric.execution_time:.2f}s vs expected {metric.expected_time:.2f}s"],
                metrics={
                    'avg_time_lost': metric.execution_time - metric.expected_time,
                    'frequency': 1
                },
                proposed_solutions=[]
            )
            
            self.bottlenecks[bottleneck_id] = bottleneck
            self._save_bottleneck(bottleneck)
    
    def _calculate_severity(self, metric: PerformanceMetric) -> str:
        """Calculate bottleneck severity"""
        time_ratio = metric.execution_time / max(1, metric.expected_time)
        
        if time_ratio > 3.0:
            return "critical"
        elif time_ratio > 2.0:
            return "high"
        elif time_ratio > 1.5:
            return "medium"
        else:
            return "low"
    
    def identify_bottleneck(self, name: str, category: str, description: str,
                          severity: str, impact_area: str,
                          affected_workflows: List[str],
                          **kwargs) -> Bottleneck:
        """Manually identify a bottleneck"""
        bottleneck_id = kwargs.get('id', f"{impact_area}_{name.replace(' ', '_')}")
        
        if bottleneck_id in self.bottlenecks:
            return self.update_bottleneck(bottleneck_id, **kwargs)
        
        bottleneck = Bottleneck(
            id=bottleneck_id,
            name=name,
            category=category,
            description=description,
            identified_date=datetime.now().isoformat(),
            severity=severity,
            impact_area=impact_area,
            affected_workflows=affected_workflows,
            symptoms=kwargs.get('symptoms', []),
            metrics=kwargs.get('metrics', {}),
            proposed_solutions=kwargs.get('proposed_solutions', []),
            **{k: v for k, v in kwargs.items() if k not in ['id', 'symptoms', 'metrics', 'proposed_solutions']}
        )
        
        self.bottlenecks[bottleneck_id] = bottleneck
        self._save_bottleneck(bottleneck)
        
        return bottleneck
    
    def update_bottleneck(self, bottleneck_id: str, **updates) -> Optional[Bottleneck]:
        """Update bottleneck information"""
        if bottleneck_id not in self.bottlenecks:
            return None
        
        bottleneck = self.bottlenecks[bottleneck_id]
        for key, value in updates.items():
            if hasattr(bottleneck, key) and value is not None:
                setattr(bottleneck, key, value)
        
        self._save_bottleneck(bottleneck)
        return bottleneck
    
    def resolve_bottleneck(self, bottleneck_id: str, resolution_notes: str,
                          solution_applied: str):
        """Mark a bottleneck as resolved"""
        if bottleneck_id not in self.bottlenecks:
            return False
        
        bottleneck = self.bottlenecks[bottleneck_id]
        bottleneck.status = "resolved"
        bottleneck.resolution_date = datetime.now().isoformat()
        bottleneck.resolution_notes = resolution_notes
        
        # Record resolution
        resolution = {
            "timestamp": datetime.now().isoformat(),
            "bottleneck_id": bottleneck_id,
            "bottleneck_name": bottleneck.name,
            "solution_applied": solution_applied,
            "notes": resolution_notes
        }
        
        with open(self.resolutions_file, 'a') as f:
            f.write(json.dumps(resolution) + '\n')
        
        self._save_bottleneck(bottleneck)
        return True
    
    def get_active_bottlenecks(self, severity: str = None) -> List[Bottleneck]:
        """Get all active bottlenecks"""
        bottlenecks = [b for b in self.bottlenecks.values() 
                      if b.status in ["identified", "analyzing", "resolving"]]
        
        if severity:
            bottlenecks = [b for b in bottlenecks if b.severity == severity]
        
        return sorted(bottlenecks, 
                     key=lambda b: {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(b.severity, 0),
                     reverse=True)
    
    def get_bottlenecks_by_workflow(self, workflow_name: str) -> List[Bottleneck]:
        """Get bottlenecks affecting a specific workflow"""
        return [b for b in self.bottlenecks.values() 
                if workflow_name in b.affected_workflows]
    
    def get_recurring_bottlenecks(self, min_recurrence: int = 3) -> List[Bottleneck]:
        """Get bottlenecks that recur frequently"""
        return sorted(
            [b for b in self.bottlenecks.values() 
             if b.recurrence_count >= min_recurrence],
            key=lambda b: b.recurrence_count,
            reverse=True
        )
    
    def analyze_workflow_performance(self, workflow_name: str,
                                    time_window_hours: int = 24) -> Dict:
        """Analyze performance of a workflow"""
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        # Load recent metrics
        recent_metrics = []
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        metric_time = datetime.fromisoformat(data['timestamp'])
                        if (data['workflow_name'] == workflow_name and 
                            metric_time > cutoff_time):
                            recent_metrics.append(PerformanceMetric(**data))
        
        if not recent_metrics:
            return {"workflow": workflow_name, "metrics_found": 0}
        
        # Calculate statistics
        total_time = sum(m.execution_time for m in recent_metrics)
        avg_time = total_time / len(recent_metrics)
        success_rate = sum(1 for m in recent_metrics if m.success) / len(recent_metrics)
        
        slow_steps = defaultdict(list)
        for m in recent_metrics:
            if m.execution_time > m.expected_time * 1.5:
                slow_steps[m.step_name].append(m.execution_time - m.expected_time)
        
        return {
            "workflow": workflow_name,
            "time_window_hours": time_window_hours,
            "metrics_found": len(recent_metrics),
            "total_execution_time": round(total_time, 2),
            "average_execution_time": round(avg_time, 2),
            "success_rate": round(success_rate * 100, 2),
            "slow_steps": {step: {
                "occurrences": len(times),
                "avg_time_lost": round(sum(times) / len(times), 2)
            } for step, times in slow_steps.items()}
        }
    
    def get_bottleneck_stats(self) -> Dict:
        """Get statistics about bottlenecks"""
        total = len(self.bottlenecks)
        by_severity = defaultdict(int)
        by_status = defaultdict(int)
        by_category = defaultdict(int)
        
        total_recurrences = 0
        
        for bottleneck in self.bottlenecks.values():
            by_severity[bottleneck.severity] += 1
            by_status[bottleneck.status] += 1
            by_category[bottleneck.category] += 1
            total_recurrences += bottleneck.recurrence_count
        
        return {
            "total_bottlenecks": total,
            "by_severity": dict(by_severity),
            "by_status": dict(by_status),
            "by_category": dict(by_category),
            "total_recurrences": total_recurrences,
            "active_count": len(self.get_active_bottlenecks())
        }
    
    def _save_bottleneck(self, bottleneck: Bottleneck):
        """Save bottleneck to storage"""
        with open(self.bottlenecks_file, 'a') as f:
            f.write(json.dumps(asdict(bottleneck)) + '\n')
    
    def export_bottleneck_report(self) -> Dict:
        """Export complete bottleneck report"""
        return {
            "generated_at": datetime.now().isoformat(),
            "total_bottlenecks": len(self.bottlenecks),
            "bottlenecks": [asdict(b) for b in self.bottlenecks.values()],
            "stats": self.get_bottleneck_stats(),
            "active_critical": [asdict(b) for b in self.get_active_bottlenecks("critical")]
        }

def get_identifier() -> BottleneckIdentifier:
    """Get singleton instance of bottleneck identifier"""
    return BottleneckIdentifier()

if __name__ == "__main__":
    # Example usage
    identifier = get_identifier()
    
    # Record a performance metric
    identifier.record_performance_metric(
        workflow_name="data_processing",
        step_name="load_data",
        execution_time=45.0,
        expected_time=10.0,
        resource_usage={"cpu": 80.0, "memory": 60.0},
        success=True
    )
    
    print(f"Stats: {identifier.get_bottleneck_stats()}")
    print(f"Active bottlenecks: {len(identifier.get_active_bottlenecks())}")
