"""Performance Monitor.

Monitors automation execution and tracks performance metrics.
"""

import json
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any


class PerformanceMonitor:
    """Monitors automation performance."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/performance"):
        """Initialize the performance monitor.
        
        Args:
            data_dir: Directory for performance data
        """
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Execution records
        self.executions: deque = deque(maxlen=10000)
        
        # Performance metrics by automation
        self.metrics_by_automation: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'execution_count': 0,
            'success_count': 0,
            'failure_count': 0,
            'total_duration': 0.0,
            'avg_duration': 0.0,
            'min_duration': float('inf'),
            'max_duration': 0.0,
            'time_saved': 0.0
        })
        
        self._load_data()
    
    def record_execution(
        self,
        automation_id: str,
        success: bool,
        duration: float,
        time_saved: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record an automation execution.
        
        Args:
            automation_id: ID of the automation
            success: Whether execution was successful
            duration: Execution duration in seconds
            time_saved: Estimated time saved vs manual execution
            metadata: Additional metadata
        """
        execution = {
            'automation_id': automation_id,
            'success': success,
            'duration': duration,
            'time_saved': time_saved or 0.0,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.executions.append(execution)
        
        # Update metrics
        metrics = self.metrics_by_automation[automation_id]
        metrics['execution_count'] += 1
        
        if success:
            metrics['success_count'] += 1
        else:
            metrics['failure_count'] += 1
        
        metrics['total_duration'] += duration
        metrics['avg_duration'] = metrics['total_duration'] / metrics['execution_count']
        metrics['min_duration'] = min(metrics['min_duration'], duration)
        metrics['max_duration'] = max(metrics['max_duration'], duration)
        
        if time_saved:
            metrics['time_saved'] += time_saved
        
        # Periodic save
        if len(self.executions) % 50 == 0:
            self._save_data()
    
    def get_automation_metrics(self, automation_id: str) -> Dict[str, Any]:
        """Get metrics for a specific automation.
        
        Args:
            automation_id: Automation ID
        
        Returns:
            Metrics dictionary
        """
        if automation_id not in self.metrics_by_automation:
            return {}
        
        metrics = dict(self.metrics_by_automation[automation_id])
        
        # Calculate success rate
        if metrics['execution_count'] > 0:
            metrics['success_rate'] = metrics['success_count'] / metrics['execution_count']
        else:
            metrics['success_rate'] = 0.0
        
        # Get recent executions
        recent = [e for e in self.executions if e['automation_id'] == automation_id]
        metrics['recent_executions'] = recent[-10:]  # Last 10
        
        return metrics
    
    def get_overall_metrics(self) -> Dict[str, Any]:
        """Get overall performance metrics.
        
        Returns:
            Overall metrics
        """
        total_executions = sum(m['execution_count'] for m in self.metrics_by_automation.values())
        total_successes = sum(m['success_count'] for m in self.metrics_by_automation.values())
        total_time_saved = sum(m['time_saved'] for m in self.metrics_by_automation.values())
        
        return {
            'total_automations': len(self.metrics_by_automation),
            'total_executions': total_executions,
            'total_successes': total_successes,
            'total_failures': total_executions - total_successes,
            'overall_success_rate': total_successes / total_executions if total_executions > 0 else 0,
            'total_time_saved_hours': total_time_saved / 3600,
            'automations_by_performance': self._rank_automations()
        }
    
    def _rank_automations(self) -> List[Dict[str, Any]]:
        """Rank automations by performance.
        
        Returns:
            Ranked list of automations
        """
        ranked = []
        
        for automation_id, metrics in self.metrics_by_automation.items():
            if metrics['execution_count'] > 0:
                score = (
                    (metrics['success_count'] / metrics['execution_count']) * 50 +  # Success rate
                    min(metrics['time_saved'] / 3600, 50)  # Time saved (capped at 50)
                )
                
                ranked.append({
                    'automation_id': automation_id,
                    'score': score,
                    'success_rate': metrics['success_count'] / metrics['execution_count'],
                    'time_saved_hours': metrics['time_saved'] / 3600,
                    'execution_count': metrics['execution_count']
                })
        
        ranked.sort(key=lambda x: x['score'], reverse=True)
        return ranked
    
    def get_time_series(
        self,
        automation_id: Optional[str] = None,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get time series data.
        
        Args:
            automation_id: Optional automation filter
            days: Number of days to include
        
        Returns:
            Time series data
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        executions = [
            e for e in self.executions
            if datetime.fromisoformat(e['timestamp']) >= cutoff
        ]
        
        if automation_id:
            executions = [e for e in executions if e['automation_id'] == automation_id]
        
        return executions
    
    def detect_anomalies(self, automation_id: str) -> List[Dict[str, Any]]:
        """Detect performance anomalies.
        
        Args:
            automation_id: Automation ID
        
        Returns:
            List of detected anomalies
        """
        metrics = self.metrics_by_automation.get(automation_id)
        if not metrics or metrics['execution_count'] < 10:
            return []
        
        anomalies = []
        recent_executions = [
            e for e in self.executions
            if e['automation_id'] == automation_id
        ][-20:]  # Last 20 executions
        
        avg_duration = metrics['avg_duration']
        
        for execution in recent_executions:
            # Check for duration anomalies
            if execution['duration'] > avg_duration * 2:
                anomalies.append({
                    'type': 'slow_execution',
                    'execution': execution,
                    'expected_duration': avg_duration,
                    'actual_duration': execution['duration']
                })
            
            # Check for failures
            if not execution['success']:
                anomalies.append({
                    'type': 'execution_failure',
                    'execution': execution
                })
        
        return anomalies
    
    def _save_data(self) -> None:
        """Save performance data."""
        data = {
            'executions': list(self.executions),
            'metrics_by_automation': dict(self.metrics_by_automation),
            'last_updated': datetime.now().isoformat()
        }
        
        filepath = self.data_dir / 'performance_data.json'
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_data(self) -> None:
        """Load performance data."""
        filepath = self.data_dir / 'performance_data.json'
        
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                self.executions = deque(data.get('executions', []), maxlen=10000)
                
                loaded_metrics = data.get('metrics_by_automation', {})
                for automation_id, metrics in loaded_metrics.items():
                    self.metrics_by_automation[automation_id] = metrics
            except Exception as e:
                print(f"Error loading performance data: {e}")
