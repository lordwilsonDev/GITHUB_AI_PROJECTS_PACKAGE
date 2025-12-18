"""Efficiency Metrics Tracker.

Tracks and analyzes efficiency metrics for automations and workflows.
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class EfficiencyTracker:
    """Tracks efficiency metrics and improvements."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/efficiency"):
        """Initialize the efficiency tracker.
        
        Args:
            data_dir: Directory for efficiency data
        """
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Efficiency records
        self.efficiency_records: List[Dict[str, Any]] = []
        
        # Baseline metrics (before optimization)
        self.baselines: Dict[str, Dict[str, float]] = {}
        
        # Improvement tracking
        self.improvements: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Aggregate statistics
        self.stats: Dict[str, Any] = {
            'total_time_saved_hours': 0.0,
            'total_automations': 0,
            'total_executions': 0,
            'avg_efficiency_gain': 0.0
        }
        
        self._load_data()
    
    def set_baseline(
        self,
        process_id: str,
        avg_duration: float,
        avg_cpu: float = 0.0,
        avg_memory: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Set baseline metrics for a process.
        
        Args:
            process_id: Process identifier
            avg_duration: Average duration in seconds
            avg_cpu: Average CPU usage percentage
            avg_memory: Average memory usage percentage
            metadata: Optional metadata
        """
        self.baselines[process_id] = {
            'avg_duration': avg_duration,
            'avg_cpu': avg_cpu,
            'avg_memory': avg_memory,
            'set_at': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self._save_data()
    
    def record_efficiency(
        self,
        process_id: str,
        duration: float,
        cpu_usage: float = 0.0,
        memory_usage: float = 0.0,
        automation_used: bool = False,
        automation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Record efficiency metrics for a process execution.
        
        Args:
            process_id: Process identifier
            duration: Execution duration in seconds
            cpu_usage: CPU usage percentage
            memory_usage: Memory usage percentage
            automation_used: Whether automation was used
            automation_id: ID of automation if used
        
        Returns:
            Efficiency analysis
        """
        record = {
            'process_id': process_id,
            'duration': duration,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'automation_used': automation_used,
            'automation_id': automation_id,
            'timestamp': datetime.now().isoformat()
        }
        
        # Calculate efficiency gains if baseline exists
        if process_id in self.baselines:
            baseline = self.baselines[process_id]
            
            duration_improvement = (
                (baseline['avg_duration'] - duration) / baseline['avg_duration'] * 100
            )
            
            cpu_improvement = 0.0
            if baseline['avg_cpu'] > 0:
                cpu_improvement = (
                    (baseline['avg_cpu'] - cpu_usage) / baseline['avg_cpu'] * 100
                )
            
            memory_improvement = 0.0
            if baseline['avg_memory'] > 0:
                memory_improvement = (
                    (baseline['avg_memory'] - memory_usage) / baseline['avg_memory'] * 100
                )
            
            record['improvements'] = {
                'duration_improvement_pct': duration_improvement,
                'cpu_improvement_pct': cpu_improvement,
                'memory_improvement_pct': memory_improvement,
                'time_saved_seconds': baseline['avg_duration'] - duration
            }
            
            # Track improvement
            if automation_used and duration_improvement > 0:
                self.improvements[process_id].append({
                    'timestamp': record['timestamp'],
                    'automation_id': automation_id,
                    'improvement_pct': duration_improvement,
                    'time_saved': baseline['avg_duration'] - duration
                })
                
                # Update aggregate stats
                self.stats['total_time_saved_hours'] += (baseline['avg_duration'] - duration) / 3600
                self.stats['total_executions'] += 1
        
        self.efficiency_records.append(record)
        
        # Periodic save
        if len(self.efficiency_records) % 50 == 0:
            self._save_data()
        
        return record
    
    def get_efficiency_report(
        self,
        process_id: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """Generate efficiency report.
        
        Args:
            process_id: Optional process filter
            days: Number of days to include
        
        Returns:
            Efficiency report
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        # Filter records
        records = [
            r for r in self.efficiency_records
            if datetime.fromisoformat(r['timestamp']) >= cutoff
        ]
        
        if process_id:
            records = [r for r in records if r['process_id'] == process_id]
        
        if not records:
            return {'error': 'No data available'}
        
        # Calculate statistics
        total_executions = len(records)
        automated_executions = sum(1 for r in records if r.get('automation_used', False))
        
        total_time_saved = sum(
            r.get('improvements', {}).get('time_saved_seconds', 0)
            for r in records
        )
        
        avg_duration_improvement = 0.0
        improvements_count = 0
        for r in records:
            if 'improvements' in r:
                avg_duration_improvement += r['improvements']['duration_improvement_pct']
                improvements_count += 1
        
        if improvements_count > 0:
            avg_duration_improvement /= improvements_count
        
        return {
            'period_days': days,
            'total_executions': total_executions,
            'automated_executions': automated_executions,
            'automation_rate': automated_executions / total_executions if total_executions > 0 else 0,
            'total_time_saved_hours': total_time_saved / 3600,
            'avg_duration_improvement_pct': avg_duration_improvement,
            'top_improvements': self._get_top_improvements(records, limit=10)
        }
    
    def _get_top_improvements(
        self,
        records: List[Dict[str, Any]],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top improvements from records.
        
        Args:
            records: Efficiency records
            limit: Maximum number to return
        
        Returns:
            List of top improvements
        """
        improvements = []
        
        for record in records:
            if 'improvements' in record and record.get('automation_used'):
                improvements.append({
                    'process_id': record['process_id'],
                    'automation_id': record.get('automation_id'),
                    'improvement_pct': record['improvements']['duration_improvement_pct'],
                    'time_saved_seconds': record['improvements']['time_saved_seconds'],
                    'timestamp': record['timestamp']
                })
        
        # Sort by improvement percentage
        improvements.sort(key=lambda x: x['improvement_pct'], reverse=True)
        
        return improvements[:limit]
    
    def get_process_efficiency(
        self,
        process_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get efficiency metrics for a specific process.
        
        Args:
            process_id: Process identifier
            days: Number of days to analyze
        
        Returns:
            Process efficiency metrics
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        records = [
            r for r in self.efficiency_records
            if r['process_id'] == process_id
            and datetime.fromisoformat(r['timestamp']) >= cutoff
        ]
        
        if not records:
            return {'process_id': process_id, 'error': 'No data available'}
        
        # Separate automated vs manual
        automated = [r for r in records if r.get('automation_used', False)]
        manual = [r for r in records if not r.get('automation_used', False)]
        
        result = {
            'process_id': process_id,
            'total_executions': len(records),
            'automated_executions': len(automated),
            'manual_executions': len(manual),
            'automation_adoption_rate': len(automated) / len(records) if records else 0
        }
        
        # Calculate averages
        if automated:
            result['automated_avg_duration'] = sum(r['duration'] for r in automated) / len(automated)
        
        if manual:
            result['manual_avg_duration'] = sum(r['duration'] for r in manual) / len(manual)
        
        # Calculate total improvements
        if process_id in self.improvements:
            improvements = self.improvements[process_id]
            result['total_improvements'] = len(improvements)
            result['total_time_saved_hours'] = sum(i['time_saved'] for i in improvements) / 3600
            result['avg_improvement_pct'] = sum(i['improvement_pct'] for i in improvements) / len(improvements)
        
        # Get baseline comparison
        if process_id in self.baselines:
            baseline = self.baselines[process_id]
            current_avg = sum(r['duration'] for r in records) / len(records)
            
            result['baseline_duration'] = baseline['avg_duration']
            result['current_avg_duration'] = current_avg
            result['overall_improvement_pct'] = (
                (baseline['avg_duration'] - current_avg) / baseline['avg_duration'] * 100
            )
        
        return result
    
    def get_roi_analysis(self) -> Dict[str, Any]:
        """Calculate ROI for automation efforts.
        
        Returns:
            ROI analysis
        """
        total_time_saved_hours = self.stats['total_time_saved_hours']
        
        # Estimate value (assuming $50/hour average)
        hourly_rate = 50
        total_value_saved = total_time_saved_hours * hourly_rate
        
        # Estimate automation development cost (rough estimate)
        # Assume 2 hours per automation at $100/hour
        automation_count = self.stats.get('total_automations', 0)
        development_cost = automation_count * 2 * 100
        
        roi = 0.0
        if development_cost > 0:
            roi = ((total_value_saved - development_cost) / development_cost) * 100
        
        return {
            'total_time_saved_hours': total_time_saved_hours,
            'estimated_value_saved': total_value_saved,
            'estimated_development_cost': development_cost,
            'roi_percentage': roi,
            'break_even': development_cost <= total_value_saved,
            'automations_created': automation_count,
            'total_executions': self.stats['total_executions']
        }
    
    def get_trend_analysis(
        self,
        process_id: Optional[str] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Analyze efficiency trends over time.
        
        Args:
            process_id: Optional process filter
            days: Number of days to analyze
        
        Returns:
            Daily trend data
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        records = [
            r for r in self.efficiency_records
            if datetime.fromisoformat(r['timestamp']) >= cutoff
        ]
        
        if process_id:
            records = [r for r in records if r['process_id'] == process_id]
        
        # Group by day
        daily_data = defaultdict(lambda: {
            'executions': 0,
            'automated': 0,
            'total_duration': 0.0,
            'time_saved': 0.0
        })
        
        for record in records:
            date = datetime.fromisoformat(record['timestamp']).date().isoformat()
            daily_data[date]['executions'] += 1
            daily_data[date]['total_duration'] += record['duration']
            
            if record.get('automation_used'):
                daily_data[date]['automated'] += 1
            
            if 'improvements' in record:
                daily_data[date]['time_saved'] += record['improvements'].get('time_saved_seconds', 0)
        
        # Convert to list and calculate averages
        trends = []
        for date, data in sorted(daily_data.items()):
            trends.append({
                'date': date,
                'executions': data['executions'],
                'automated': data['automated'],
                'automation_rate': data['automated'] / data['executions'] if data['executions'] > 0 else 0,
                'avg_duration': data['total_duration'] / data['executions'] if data['executions'] > 0 else 0,
                'time_saved_hours': data['time_saved'] / 3600
            })
        
        return trends
    
    def get_overall_statistics(self) -> Dict[str, Any]:
        """Get overall efficiency statistics.
        
        Returns:
            Overall statistics
        """
        return {
            **self.stats,
            'total_processes_tracked': len(self.baselines),
            'total_records': len(self.efficiency_records),
            'processes_with_improvements': len(self.improvements)
        }
    
    def _save_data(self) -> None:
        """Save efficiency data."""
        data = {
            'efficiency_records': self.efficiency_records,
            'baselines': self.baselines,
            'improvements': dict(self.improvements),
            'stats': self.stats,
            'last_updated': datetime.now().isoformat()
        }
        
        filepath = self.data_dir / 'efficiency_data.json'
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_data(self) -> None:
        """Load efficiency data."""
        filepath = self.data_dir / 'efficiency_data.json'
        
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                self.efficiency_records = data.get('efficiency_records', [])
                self.baselines = data.get('baselines', {})
                
                loaded_improvements = data.get('improvements', {})
                for process_id, improvements in loaded_improvements.items():
                    self.improvements[process_id] = improvements
                
                self.stats = data.get('stats', self.stats)
            except Exception as e:
                print(f"Error loading efficiency data: {e}")
