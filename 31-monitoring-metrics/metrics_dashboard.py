#!/usr/bin/env python3
"""
Monitoring and Observability for MoIE-OS Enterprise
Provides metrics collection, health checks, and dashboard
"""

import time
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import deque
import threading

@dataclass
class Metric:
    """Represents a single metric data point"""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str]

class MetricsCollector:
    """Collects and stores system metrics"""
    
    def __init__(self, retention_seconds: int = 3600):
        self.retention_seconds = retention_seconds
        self.metrics: Dict[str, deque] = {}
        self.lock = threading.Lock()
        
    def record(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a metric"""
        metric = Metric(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags or {}
        )
        
        with self.lock:
            if name not in self.metrics:
                self.metrics[name] = deque(maxlen=10000)
            
            self.metrics[name].append(metric)
            self._cleanup_old_metrics(name)
    
    def _cleanup_old_metrics(self, name: str):
        """Remove metrics older than retention period"""
        cutoff = time.time() - self.retention_seconds
        
        while self.metrics[name] and self.metrics[name][0].timestamp < cutoff:
            self.metrics[name].popleft()
    
    def get_latest(self, name: str) -> Optional[Metric]:
        """Get the latest value for a metric"""
        with self.lock:
            if name in self.metrics and self.metrics[name]:
                return self.metrics[name][-1]
        return None
    
    def get_average(self, name: str, seconds: int = 60) -> Optional[float]:
        """Get average value over the last N seconds"""
        cutoff = time.time() - seconds
        
        with self.lock:
            if name not in self.metrics:
                return None
            
            recent = [m.value for m in self.metrics[name] if m.timestamp >= cutoff]
            
            if not recent:
                return None
            
            return sum(recent) / len(recent)
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        with self.lock:
            summary = {}
            
            for name, metrics in self.metrics.items():
                if not metrics:
                    continue
                
                values = [m.value for m in metrics]
                summary[name] = {
                    'latest': values[-1] if values else None,
                    'count': len(values),
                    'avg': sum(values) / len(values) if values else 0,
                    'min': min(values) if values else 0,
                    'max': max(values) if values else 0
                }
            
            return summary

class HealthChecker:
    """Performs health checks on system components"""
    
    def __init__(self):
        self.checks: Dict[str, callable] = {}
        self.last_results: Dict[str, Dict[str, Any]] = {}
    
    def register_check(self, name: str, check_func: callable):
        """Register a health check function"""
        self.checks[name] = check_func
    
    def run_check(self, name: str) -> Dict[str, Any]:
        """Run a specific health check"""
        if name not in self.checks:
            return {'status': 'unknown', 'error': 'Check not found'}
        
        try:
            start = time.time()
            result = self.checks[name]()
            duration = time.time() - start
            
            check_result = {
                'status': 'healthy' if result else 'unhealthy',
                'timestamp': time.time(),
                'duration': duration,
                'details': result if isinstance(result, dict) else {}
            }
            
            self.last_results[name] = check_result
            return check_result
            
        except Exception as e:
            check_result = {
                'status': 'error',
                'timestamp': time.time(),
                'error': str(e)
            }
            self.last_results[name] = check_result
            return check_result
    
    def run_all_checks(self) -> Dict[str, Dict[str, Any]]:
        """Run all registered health checks"""
        results = {}
        for name in self.checks:
            results[name] = self.run_check(name)
        return results
    
    def get_overall_health(self) -> str:
        """Get overall system health status"""
        if not self.last_results:
            return 'unknown'
        
        statuses = [r['status'] for r in self.last_results.values()]
        
        if any(s == 'error' for s in statuses):
            return 'critical'
        elif any(s == 'unhealthy' for s in statuses):
            return 'degraded'
        elif all(s == 'healthy' for s in statuses):
            return 'healthy'
        else:
            return 'unknown'

class ObservabilityDashboard:
    """Main dashboard for monitoring and observability"""
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self.health = HealthChecker()
        self.start_time = time.time()
        
        # Register default health checks
        self._register_default_checks()
    
    def _register_default_checks(self):
        """Register default health checks"""
        self.health.register_check('uptime', lambda: {'uptime': time.time() - self.start_time})
        self.health.register_check('memory', lambda: True)  # Placeholder
    
    def record_task_execution(self, level: int, duration: float, success: bool):
        """Record task execution metrics"""
        self.metrics.record(f'task_duration_level_{level}', duration, {'level': str(level)})
        self.metrics.record(f'task_success_level_{level}', 1.0 if success else 0.0, {'level': str(level)})
        self.metrics.record('total_tasks', 1.0)
    
    def record_error(self, level: int, error_type: str):
        """Record error occurrence"""
        self.metrics.record(f'errors_level_{level}', 1.0, {'level': str(level), 'type': error_type})
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data"""
        return {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': time.time() - self.start_time,
            'health': {
                'overall': self.health.get_overall_health(),
                'checks': self.health.last_results
            },
            'metrics': self.metrics.get_all_metrics()
        }
    
    def print_dashboard(self):
        """Print dashboard to console"""
        data = self.get_dashboard_data()
        
        print("\n" + "="*60)
        print("📊 MoIE-OS Enterprise Observability Dashboard")
        print("="*60)
        
        print(f"\n⏱️  Uptime: {data['uptime_seconds']:.1f}s")
        print(f"🏥 Overall Health: {data['health']['overall'].upper()}")
        
        print("\n📈 Metrics Summary:")
        for name, stats in data['metrics'].items():
            print(f"  {name}:")
            print(f"    Latest: {stats['latest']:.2f}")
            print(f"    Avg: {stats['avg']:.2f}")
            print(f"    Min/Max: {stats['min']:.2f}/{stats['max']:.2f}")
        
        print("\n✅ Health Checks:")
        for name, result in data['health']['checks'].items():
            status_icon = "✅" if result['status'] == 'healthy' else "❌"
            print(f"  {status_icon} {name}: {result['status']}")
        
        print("\n" + "="*60)


if __name__ == '__main__':
    print("MoIE-OS Observability Demo")
    print("="*60)
    
    # Create dashboard
    dashboard = ObservabilityDashboard()
    
    # Simulate some task executions
    print("\n🚀 Simulating task executions...")
    for level in [8, 9, 10]:
        for i in range(5):
            duration = 0.1 + (i * 0.05)
            success = i < 4  # Last one fails
            dashboard.record_task_execution(level, duration, success)
            time.sleep(0.01)
    
    # Run health checks
    print("\n🏥 Running health checks...")
    dashboard.health.run_all_checks()
    
    # Display dashboard
    dashboard.print_dashboard()
    
    # Export to JSON
    print("\n💾 Exporting dashboard data...")
    data = dashboard.get_dashboard_data()
    print(json.dumps(data, indent=2))
    
    print("\n✅ Demo Complete!")
