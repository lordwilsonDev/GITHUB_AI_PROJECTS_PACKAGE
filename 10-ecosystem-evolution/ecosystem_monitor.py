#!/usr/bin/env python3
"""
Ecosystem Health Monitor - New Build 6, Phase 3
System-wide observability, health metrics aggregation, and anomaly detection
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import statistics


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"          # Monotonically increasing
    GAUGE = "gauge"              # Point-in-time value
    HISTOGRAM = "histogram"      # Distribution of values
    SUMMARY = "summary"          # Statistical summary


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class HealthMetric:
    """Represents a health metric"""
    metric_id: str
    metric_type: MetricType
    value: float
    unit: str
    component: str  # Which component this metric is from
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'metric_id': self.metric_id,
            'metric_type': self.metric_type.value,
            'value': self.value,
            'unit': self.unit,
            'component': self.component,
            'timestamp': self.timestamp,
            'labels': self.labels
        }


@dataclass
class HealthCheck:
    """Represents a health check result"""
    component: str
    status: HealthStatus
    message: str
    timestamp: float = field(default_factory=time.time)
    metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'component': self.component,
            'status': self.status.value,
            'message': self.message,
            'timestamp': self.timestamp,
            'metrics': self.metrics
        }


@dataclass
class Alert:
    """Represents a system alert"""
    alert_id: str
    severity: AlertSeverity
    component: str
    message: str
    metric_id: Optional[str] = None
    threshold_value: Optional[float] = None
    actual_value: Optional[float] = None
    timestamp: float = field(default_factory=time.time)
    acknowledged: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'alert_id': self.alert_id,
            'severity': self.severity.value,
            'component': self.component,
            'message': self.message,
            'metric_id': self.metric_id,
            'threshold_value': self.threshold_value,
            'actual_value': self.actual_value,
            'timestamp': self.timestamp,
            'acknowledged': self.acknowledged
        }


class MetricsCollector:
    """Collects and stores metrics"""
    
    def __init__(self, retention_size: int = 1000):
        self.retention_size = retention_size
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=retention_size))
        self.lock = threading.Lock()
        
    def record(self, metric: HealthMetric) -> bool:
        """Record a metric"""
        with self.lock:
            self.metrics[metric.metric_id].append(metric)
            return True
    
    def get_latest(self, metric_id: str) -> Optional[HealthMetric]:
        """Get latest value for a metric"""
        with self.lock:
            if metric_id in self.metrics and self.metrics[metric_id]:
                return self.metrics[metric_id][-1]
            return None
    
    def get_history(self, metric_id: str, limit: Optional[int] = None) -> List[HealthMetric]:
        """Get historical values for a metric"""
        with self.lock:
            if metric_id not in self.metrics:
                return []
            
            history = list(self.metrics[metric_id])
            if limit:
                return history[-limit:]
            return history
    
    def get_statistics(self, metric_id: str) -> Dict[str, float]:
        """Get statistical summary of a metric"""
        history = self.get_history(metric_id)
        
        if not history:
            return {}
        
        values = [m.value for m in history]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0.0
        }
    
    def get_all_metrics(self) -> List[str]:
        """Get list of all metric IDs"""
        with self.lock:
            return list(self.metrics.keys())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collector statistics"""
        with self.lock:
            total_datapoints = sum(len(deq) for deq in self.metrics.values())
            
            return {
                'total_metrics': len(self.metrics),
                'total_datapoints': total_datapoints,
                'retention_size': self.retention_size
            }


class AnomalyDetector:
    """Detects anomalies in metrics"""
    
    def __init__(self, sensitivity: float = 2.0):
        self.sensitivity = sensitivity  # Standard deviations for anomaly threshold
        self.detection_history: List[Dict[str, Any]] = []
        
    def detect(self, metric_id: str, current_value: float, historical_values: List[float]) -> Tuple[bool, Optional[str]]:
        """Detect if current value is anomalous"""
        if len(historical_values) < 3:
            return False, None
        
        mean = statistics.mean(historical_values)
        stdev = statistics.stdev(historical_values) if len(historical_values) > 1 else 0.0
        
        if stdev == 0:
            # No variation in historical data
            if current_value != mean:
                return True, f"Value {current_value} differs from constant baseline {mean}"
            return False, None
        
        # Calculate z-score
        z_score = abs((current_value - mean) / stdev)
        
        if z_score > self.sensitivity:
            self.detection_history.append({
                'metric_id': metric_id,
                'value': current_value,
                'mean': mean,
                'stdev': stdev,
                'z_score': z_score,
                'timestamp': time.time()
            })
            
            return True, f"Anomaly detected: value {current_value:.2f} is {z_score:.2f} std devs from mean {mean:.2f}"
        
        return False, None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get detector statistics"""
        return {
            'sensitivity': self.sensitivity,
            'total_anomalies': len(self.detection_history)
        }


class AlertManager:
    """Manages system alerts"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.lock = threading.Lock()
        self.alert_counter = 0
        
    def create_alert(self, severity: AlertSeverity, component: str, message: str, 
                    metric_id: Optional[str] = None, threshold: Optional[float] = None, 
                    actual: Optional[float] = None) -> Alert:
        """Create a new alert"""
        with self.lock:
            self.alert_counter += 1
            alert_id = f"alert_{self.alert_counter}"
            
            alert = Alert(
                alert_id=alert_id,
                severity=severity,
                component=component,
                message=message,
                metric_id=metric_id,
                threshold_value=threshold,
                actual_value=actual
            )
            
            self.alerts[alert_id] = alert
            self.alert_history.append(alert)
            
            return alert
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        with self.lock:
            if alert_id in self.alerts:
                self.alerts[alert_id].acknowledged = True
                return True
            return False
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get active (unacknowledged) alerts"""
        with self.lock:
            alerts = [a for a in self.alerts.values() if not a.acknowledged]
            
            if severity:
                alerts = [a for a in alerts if a.severity == severity]
            
            return alerts
    
    def get_stats(self) -> Dict[str, Any]:
        """Get alert statistics"""
        with self.lock:
            active_count = sum(1 for a in self.alerts.values() if not a.acknowledged)
            
            severity_counts = defaultdict(int)
            for alert in self.alerts.values():
                if not alert.acknowledged:
                    severity_counts[alert.severity.value] += 1
            
            return {
                'total_alerts': len(self.alert_history),
                'active_alerts': active_count,
                'acknowledged_alerts': len(self.alerts) - active_count,
                'severity_counts': dict(severity_counts)
            }


class HealthDashboard:
    """Aggregates and displays health information"""
    
    def __init__(self):
        self.components: Dict[str, HealthCheck] = {}
        self.lock = threading.Lock()
        
    def update_component(self, health_check: HealthCheck) -> bool:
        """Update component health status"""
        with self.lock:
            self.components[health_check.component] = health_check
            return True
    
    def get_component_health(self, component: str) -> Optional[HealthCheck]:
        """Get health status of a component"""
        with self.lock:
            return self.components.get(component)
    
    def get_overall_health(self) -> HealthStatus:
        """Get overall system health"""
        with self.lock:
            if not self.components:
                return HealthStatus.UNKNOWN
            
            statuses = [c.status for c in self.components.values()]
            
            # Overall health is worst component health
            if HealthStatus.CRITICAL in statuses:
                return HealthStatus.CRITICAL
            elif HealthStatus.UNHEALTHY in statuses:
                return HealthStatus.UNHEALTHY
            elif HealthStatus.DEGRADED in statuses:
                return HealthStatus.DEGRADED
            elif HealthStatus.HEALTHY in statuses:
                return HealthStatus.HEALTHY
            else:
                return HealthStatus.UNKNOWN
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get complete dashboard view"""
        with self.lock:
            return {
                'overall_health': self.get_overall_health().value,
                'total_components': len(self.components),
                'components': {
                    name: check.to_dict()
                    for name, check in self.components.items()
                }
            }


class EcosystemMonitor:
    """Main ecosystem health monitoring system"""
    
    def __init__(self, retention_size: int = 1000, anomaly_sensitivity: float = 2.0):
        self.metrics_collector = MetricsCollector(retention_size)
        self.anomaly_detector = AnomalyDetector(anomaly_sensitivity)
        self.alert_manager = AlertManager()
        self.dashboard = HealthDashboard()
        self.monitoring_active = False
        self.lock = threading.Lock()
        
    def record_metric(self, metric: HealthMetric) -> bool:
        """Record a health metric"""
        # Store metric
        self.metrics_collector.record(metric)
        
        # Check for anomalies
        history = self.metrics_collector.get_history(metric.metric_id, limit=100)
        historical_values = [m.value for m in history[:-1]]  # Exclude current value
        
        if historical_values:
            is_anomaly, message = self.anomaly_detector.detect(
                metric.metric_id, metric.value, historical_values
            )
            
            if is_anomaly:
                # Create alert for anomaly
                self.alert_manager.create_alert(
                    severity=AlertSeverity.WARNING,
                    component=metric.component,
                    message=message or "Anomaly detected",
                    metric_id=metric.metric_id,
                    actual=metric.value
                )
        
        return True
    
    def update_health(self, health_check: HealthCheck) -> bool:
        """Update component health status"""
        self.dashboard.update_component(health_check)
        
        # Create alerts for unhealthy components
        if health_check.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
            severity = AlertSeverity.CRITICAL if health_check.status == HealthStatus.CRITICAL else AlertSeverity.ERROR
            self.alert_manager.create_alert(
                severity=severity,
                component=health_check.component,
                message=health_check.message
            )
        
        return True
    
    def get_component_metrics(self, component: str) -> List[HealthMetric]:
        """Get all metrics for a component"""
        all_metrics = []
        for metric_id in self.metrics_collector.get_all_metrics():
            latest = self.metrics_collector.get_latest(metric_id)
            if latest and latest.component == component:
                all_metrics.append(latest)
        return all_metrics
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive monitoring statistics"""
        return {
            'overall_health': self.dashboard.get_overall_health().value,
            'metrics_collector': self.metrics_collector.get_stats(),
            'anomaly_detector': self.anomaly_detector.get_stats(),
            'alert_manager': self.alert_manager.get_stats(),
            'dashboard': self.dashboard.get_dashboard()
        }
    
    def demo(self) -> Dict[str, Any]:
        """Demonstrate ecosystem monitoring capabilities"""
        print("\n=== Ecosystem Health Monitor Demo ===")
        
        # 1. Record normal metrics
        print("\n1. Recording normal metrics...")
        for i in range(10):
            metric = HealthMetric(
                metric_id="cpu_usage",
                metric_type=MetricType.GAUGE,
                value=50.0 + (i * 2),  # Gradually increasing
                unit="percent",
                component="compute_node_1"
            )
            self.record_metric(metric)
        print(f"   Recorded 10 CPU usage metrics")
        
        # 2. Record anomalous metric
        print("\n2. Recording anomalous metric...")
        anomaly_metric = HealthMetric(
            metric_id="cpu_usage",
            metric_type=MetricType.GAUGE,
            value=95.0,  # Sudden spike
            unit="percent",
            component="compute_node_1"
        )
        self.record_metric(anomaly_metric)
        print(f"   Recorded anomalous CPU spike")
        
        # 3. Update component health
        print("\n3. Updating component health statuses...")
        self.update_health(HealthCheck(
            component="compute_node_1",
            status=HealthStatus.HEALTHY,
            message="All systems operational",
            metrics={'cpu': 60.0, 'memory': 45.0}
        ))
        
        self.update_health(HealthCheck(
            component="storage_node_1",
            status=HealthStatus.DEGRADED,
            message="Disk usage at 85%",
            metrics={'disk': 85.0}
        ))
        
        self.update_health(HealthCheck(
            component="network_node_1",
            status=HealthStatus.UNHEALTHY,
            message="High packet loss detected",
            metrics={'packet_loss': 15.0}
        ))
        print(f"   Updated 3 component health statuses")
        
        # 4. Check alerts
        print("\n4. Active alerts:")
        active_alerts = self.alert_manager.get_active_alerts()
        for alert in active_alerts:
            print(f"   [{alert.severity.value.upper()}] {alert.component}: {alert.message}")
        
        # 5. Get metric statistics
        print("\n5. CPU usage statistics:")
        stats = self.metrics_collector.get_statistics("cpu_usage")
        for key, value in stats.items():
            print(f"   {key}: {value:.2f}")
        
        # 6. Get dashboard
        print("\n6. Health dashboard:")
        dashboard = self.dashboard.get_dashboard()
        print(f"   Overall health: {dashboard['overall_health']}")
        print(f"   Total components: {dashboard['total_components']}")
        for component, health in dashboard['components'].items():
            print(f"   {component}: {health['status']}")
        
        # 7. Get comprehensive statistics
        print("\n7. System statistics:")
        system_stats = self.get_stats()
        print(f"   Total metrics: {system_stats['metrics_collector']['total_metrics']}")
        print(f"   Total datapoints: {system_stats['metrics_collector']['total_datapoints']}")
        print(f"   Anomalies detected: {system_stats['anomaly_detector']['total_anomalies']}")
        print(f"   Active alerts: {system_stats['alert_manager']['active_alerts']}")
        
        print("\n=== Demo Complete ===")
        return system_stats


class EcosystemMonitorContract:
    """Contract interface for testing"""
    
    @staticmethod
    def create() -> EcosystemMonitor:
        """Create an ecosystem monitor instance"""
        return EcosystemMonitor()
    
    @staticmethod
    def verify() -> bool:
        """Verify ecosystem monitor functionality"""
        em = EcosystemMonitor()
        
        # Test metric recording
        metric = HealthMetric(
            metric_id="test_metric",
            metric_type=MetricType.GAUGE,
            value=50.0,
            unit="percent",
            component="test_component"
        )
        if not em.record_metric(metric):
            return False
        
        # Test health update
        health_check = HealthCheck(
            component="test_component",
            status=HealthStatus.HEALTHY,
            message="Test OK"
        )
        if not em.update_health(health_check):
            return False
        
        # Test dashboard
        dashboard = em.dashboard.get_dashboard()
        if dashboard['total_components'] != 1:
            return False
        
        # Test statistics
        stats = em.get_stats()
        if stats['metrics_collector']['total_metrics'] != 1:
            return False
        
        return True


if __name__ == "__main__":
    # Run demo
    em = EcosystemMonitor()
    em.demo()
