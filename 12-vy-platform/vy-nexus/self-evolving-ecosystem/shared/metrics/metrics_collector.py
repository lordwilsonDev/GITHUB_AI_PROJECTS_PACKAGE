"""\nMetrics Collection System for Self-Evolving AI Ecosystem\nTracks performance, learning, and optimization metrics\n"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import statistics


@dataclass
class Metric:
    """Represents a single metric measurement"""
    timestamp: str
    feature: str
    metric_type: str
    metric_name: str
    value: float
    metadata: Dict[str, Any]


class MetricsCollector:
    """\n    Comprehensive metrics collection and analysis system.\n    Stores metrics in SQLite and provides analysis capabilities.\n    """
    
    def __init__(self, db_path: str = "/Users/lordwilson/vy-nexus/data/metrics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize the metrics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                feature TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_feature_timestamp 
            ON metrics(feature, timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_metric_type 
            ON metrics(metric_type)
        ''')
        
        # Create aggregated metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metric_aggregates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                feature TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                avg_value REAL,
                min_value REAL,
                max_value REAL,
                count INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, feature, metric_name)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_metric(self, feature: str, metric_type: str, 
                     metric_name: str, value: float, 
                     metadata: Optional[Dict[str, Any]] = None):
        """\n        Record a single metric.\n        \n        Args:\n            feature: Feature name (e.g., 'learning-engine')\n            metric_type: Type of metric (e.g., 'performance', 'learning', 'optimization')\n            metric_name: Specific metric name (e.g., 'response_time_ms', 'accuracy')\n            value: Metric value\n            metadata: Optional additional data\n        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        metadata_json = json.dumps(metadata or {})
        
        cursor.execute('''
            INSERT INTO metrics (timestamp, feature, metric_type, metric_name, value, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, feature, metric_type, metric_name, value, metadata_json))
        
        conn.commit()
        conn.close()
    
    def record_performance_metric(self, feature: str, metric_name: str, 
                                 value: float, metadata: Optional[Dict] = None):
        """Record a performance metric"""
        self.record_metric(feature, 'performance', metric_name, value, metadata)
    
    def record_learning_metric(self, feature: str, metric_name: str, 
                              value: float, metadata: Optional[Dict] = None):
        """Record a learning metric"""
        self.record_metric(feature, 'learning', metric_name, value, metadata)
    
    def record_optimization_metric(self, feature: str, metric_name: str, 
                                  value: float, metadata: Optional[Dict] = None):
        """Record an optimization metric"""
        self.record_metric(feature, 'optimization', metric_name, value, metadata)
    
    def get_metrics(self, feature: Optional[str] = None, 
                   metric_type: Optional[str] = None,
                   metric_name: Optional[str] = None,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   limit: int = 1000) -> List[Metric]:
        """\n        Query metrics with filters.\n        \n        Args:\n            feature: Filter by feature name\n            metric_type: Filter by metric type\n            metric_name: Filter by metric name\n            start_time: Filter by start time\n            end_time: Filter by end time\n            limit: Maximum number of results\n        \n        Returns:\n            List of Metric objects\n        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT timestamp, feature, metric_type, metric_name, value, metadata FROM metrics WHERE 1=1"
        params = []
        
        if feature:
            query += " AND feature = ?"
            params.append(feature)
        
        if metric_type:
            query += " AND metric_type = ?"
            params.append(metric_type)
        
        if metric_name:
            query += " AND metric_name = ?"
            params.append(metric_name)
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        metrics = []
        for row in rows:
            metrics.append(Metric(
                timestamp=row[0],
                feature=row[1],
                metric_type=row[2],
                metric_name=row[3],
                value=row[4],
                metadata=json.loads(row[5]) if row[5] else {}
            ))
        
        return metrics
    
    def get_metric_statistics(self, feature: str, metric_name: str,
                            hours: int = 24) -> Dict[str, float]:
        """\n        Get statistical summary of a metric over time.\n        \n        Args:\n            feature: Feature name\n            metric_name: Metric name\n            hours: Number of hours to look back\n        \n        Returns:\n            Dictionary with statistics (avg, min, max, stddev, count)\n        """
        start_time = datetime.now() - timedelta(hours=hours)
        metrics = self.get_metrics(
            feature=feature,
            metric_name=metric_name,
            start_time=start_time
        )
        
        if not metrics:
            return {
                'avg': 0.0,
                'min': 0.0,
                'max': 0.0,
                'stddev': 0.0,
                'count': 0
            }
        
        values = [m.value for m in metrics]
        
        return {
            'avg': statistics.mean(values),
            'min': min(values),
            'max': max(values),
            'stddev': statistics.stdev(values) if len(values) > 1 else 0.0,
            'count': len(values)
        }
    
    def aggregate_daily_metrics(self, date: Optional[str] = None):
        """\n        Aggregate metrics for a specific date.\n        \n        Args:\n            date: Date string (YYYY-MM-DD), defaults to today\n        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Aggregate metrics by feature and metric_name
        cursor.execute('''
            INSERT OR REPLACE INTO metric_aggregates 
            (date, feature, metric_name, avg_value, min_value, max_value, count)
            SELECT 
                DATE(timestamp) as date,
                feature,
                metric_name,
                AVG(value) as avg_value,
                MIN(value) as min_value,
                MAX(value) as max_value,
                COUNT(*) as count
            FROM metrics
            WHERE DATE(timestamp) = ?
            GROUP BY DATE(timestamp), feature, metric_name
        ''', (date,))
        
        conn.commit()
        conn.close()
    
    def get_feature_dashboard(self, feature: str, hours: int = 24) -> Dict[str, Any]:
        """\n        Get a dashboard summary for a feature.\n        \n        Args:\n            feature: Feature name\n            hours: Number of hours to look back\n        \n        Returns:\n            Dictionary with dashboard data\n        """
        start_time = datetime.now() - timedelta(hours=hours)
        metrics = self.get_metrics(feature=feature, start_time=start_time)
        
        # Group metrics by type and name
        grouped = {}
        for metric in metrics:
            key = f"{metric.metric_type}.{metric.metric_name}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(metric.value)
        
        # Calculate statistics for each metric
        dashboard = {
            'feature': feature,
            'time_range_hours': hours,
            'total_metrics': len(metrics),
            'metrics': {}
        }
        
        for key, values in grouped.items():
            dashboard['metrics'][key] = {
                'count': len(values),
                'avg': statistics.mean(values),
                'min': min(values),
                'max': max(values),
                'latest': values[0] if values else None
            }
        
        return dashboard


# Global metrics collector instance
_global_collector = None

def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    global _global_collector
    if _global_collector is None:
        _global_collector = MetricsCollector()
    return _global_collector


if __name__ == "__main__":
    # Test the metrics system
    collector = get_metrics_collector()
    
    # Record some test metrics
    collector.record_performance_metric(
        'learning-engine',
        'pattern_recognition_time_ms',
        125.5,
        {'algorithm': 'neural_pattern_v1'}
    )
    
    collector.record_learning_metric(
        'learning-engine',
        'accuracy',
        0.87,
        {'training_samples': 1000}
    )
    
    collector.record_optimization_metric(
        'process-optimization',
        'automation_success_rate',
        0.92,
        {'automations_tested': 50}
    )
    
    # Get statistics
    stats = collector.get_metric_statistics('learning-engine', 'accuracy', hours=24)
    print(f"Learning Engine Accuracy Stats: {stats}")
    
    # Get dashboard
    dashboard = collector.get_feature_dashboard('learning-engine', hours=24)
    print(f"\nLearning Engine Dashboard:")
    print(json.dumps(dashboard, indent=2))
    
    print("\n✅ Metrics system test complete!")
