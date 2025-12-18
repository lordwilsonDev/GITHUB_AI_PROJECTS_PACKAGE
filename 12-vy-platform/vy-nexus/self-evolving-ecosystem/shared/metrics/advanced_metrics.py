"""\nAdvanced Metrics Tracking Database for Self-Evolving AI Ecosystem\nDetailed metrics on system performance and user satisfaction\n"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import statistics
from collections import defaultdict


class AdvancedMetricsTracker:
    """\n    Advanced metrics tracking system with detailed performance and satisfaction metrics.\n    Extends the basic metrics collector with comprehensive tracking capabilities.\n    """
    
    def __init__(self, db_path: str = "/Users/lordwilson/vy-nexus/data/advanced_metrics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize advanced metrics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # System performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                feature TEXT NOT NULL,
                metric_category TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                context TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User satisfaction metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_satisfaction (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                feature TEXT NOT NULL,
                satisfaction_type TEXT NOT NULL,
                score REAL NOT NULL,
                feedback TEXT,
                interaction_id TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Feature usage metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feature_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                feature TEXT NOT NULL,
                action TEXT NOT NULL,
                duration_ms REAL,
                success BOOLEAN,
                error_type TEXT,
                user_context TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Learning effectiveness metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_effectiveness (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                feature TEXT NOT NULL,
                learning_type TEXT NOT NULL,
                accuracy REAL,
                confidence REAL,
                sample_size INTEGER,
                improvement_rate REAL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Optimization impact metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_impact (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                feature TEXT NOT NULL,
                optimization_id TEXT NOT NULL,
                impact_category TEXT NOT NULL,
                before_value REAL NOT NULL,
                after_value REAL NOT NULL,
                improvement_percent REAL,
                user_impact_score REAL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Resource utilization metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resource_utilization (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_name TEXT NOT NULL,
                utilization_percent REAL,
                allocated REAL,
                used REAL,
                unit TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Error and failure metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                feature TEXT NOT NULL,
                error_type TEXT NOT NULL,
                error_severity TEXT NOT NULL,
                error_message TEXT,
                recovery_attempted BOOLEAN,
                recovery_successful BOOLEAN,
                impact_level TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Aggregated daily metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_aggregates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                feature TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                avg_value REAL,
                min_value REAL,
                max_value REAL,
                stddev REAL,
                count INTEGER,
                percentile_50 REAL,
                percentile_95 REAL,
                percentile_99 REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, feature, metric_type, metric_name)
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sys_perf_feature_time ON system_performance(feature, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_sat_feature_time ON user_satisfaction(feature, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feature_usage_feature_time ON feature_usage(feature, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_learning_eff_feature_time ON learning_effectiveness(feature, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_opt_impact_feature_time ON optimization_impact(feature, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_resource_util_type_time ON resource_utilization(resource_type, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_error_feature_time ON error_metrics(feature, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_agg_date_feature ON daily_aggregates(date, feature)')
        
        conn.commit()
        conn.close()
    
    # ==================== System Performance Metrics ====================
    
    def record_performance_metric(self, feature: str, metric_category: str,
                                 metric_name: str, value: float,
                                 unit: Optional[str] = None,
                                 context: Optional[str] = None,
                                 metadata: Optional[Dict] = None):
        """\n        Record system performance metric.\n        \n        Args:\n            feature: Feature name\n            metric_category: Category (response_time, throughput, latency, etc.)\n            metric_name: Specific metric name\n            value: Metric value\n            unit: Unit of measurement\n            context: Context information\n            metadata: Additional metadata\n        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_performance 
            (timestamp, feature, metric_category, metric_name, value, unit, context, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            feature,
            metric_category,
            metric_name,
            value,
            unit,
            context,
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
    
    def get_performance_metrics(self, feature: Optional[str] = None,
                               metric_category: Optional[str] = None,
                               hours: int = 24,
                               limit: int = 1000) -> List[Dict[str, Any]]:
        """Get system performance metrics with filters"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        query = "SELECT * FROM system_performance WHERE timestamp >= ?"
        params = [start_time]
        
        if feature:
            query += " AND feature = ?"
            params.append(feature)
        
        if metric_category:
            query += " AND metric_category = ?"
            params.append(metric_category)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        metrics = []
        for row in rows:
            metrics.append({
                'timestamp': row['timestamp'],
                'feature': row['feature'],
                'metric_category': row['metric_category'],
                'metric_name': row['metric_name'],
                'value': row['value'],
                'unit': row['unit'],
                'context': row['context'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else {}
            })
        
        conn.close()
        return metrics
    
    # ==================== User Satisfaction Metrics ====================
    
    def record_satisfaction(self, feature: str, satisfaction_type: str,
                          score: float, feedback: Optional[str] = None,
                          interaction_id: Optional[str] = None,
                          metadata: Optional[Dict] = None):
        """\n        Record user satisfaction metric.\n        \n        Args:\n            feature: Feature name\n            satisfaction_type: Type (task_completion, ease_of_use, accuracy, etc.)\n            score: Satisfaction score (0.0 to 1.0 or 1-5 scale)\n            feedback: Optional user feedback\n            interaction_id: Related interaction ID\n            metadata: Additional metadata\n        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_satisfaction 
            (timestamp, feature, satisfaction_type, score, feedback, interaction_id, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            feature,
            satisfaction_type,
            score,
            feedback,
            interaction_id,
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
    
    def get_satisfaction_metrics(self, feature: Optional[str] = None,
                                satisfaction_type: Optional[str] = None,
                                hours: int = 24) -> Dict[str, Any]:
        """Get user satisfaction statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        query = "SELECT score FROM user_satisfaction WHERE timestamp >= ?"
        params = [start_time]
        
        if feature:
            query += " AND feature = ?"
            params.append(feature)
        
        if satisfaction_type:
            query += " AND satisfaction_type = ?"
            params.append(satisfaction_type)
        
        cursor.execute(query, params)
        scores = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        if not scores:
            return {
                'avg_score': 0.0,
                'min_score': 0.0,
                'max_score': 0.0,
                'count': 0,
                'satisfaction_rate': 0.0
            }
        
        return {
            'avg_score': statistics.mean(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'count': len(scores),
            'satisfaction_rate': sum(1 for s in scores if s >= 0.7) / len(scores) if scores else 0.0
        }
    
    # ==================== Feature Usage Metrics ====================
    
    def record_feature_usage(self, feature: str, action: str,
                           duration_ms: Optional[float] = None,
                           success: bool = True,
                           error_type: Optional[str] = None,
                           user_context: Optional[str] = None,
                           metadata: Optional[Dict] = None):
        """Record feature usage event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feature_usage 
            (timestamp, feature, action, duration_ms, success, error_type, user_context, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            feature,
            action,
            duration_ms,
            success,
            error_type,
            user_context,
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
    
    def get_feature_usage_stats(self, feature: str, hours: int = 24) -> Dict[str, Any]:
        """Get feature usage statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        # Total usage count
        cursor.execute('''
            SELECT COUNT(*) FROM feature_usage 
            WHERE feature = ? AND timestamp >= ?
        ''', (feature, start_time))
        total_count = cursor.fetchone()[0]
        
        # Success rate
        cursor.execute('''
            SELECT COUNT(*) FROM feature_usage 
            WHERE feature = ? AND timestamp >= ? AND success = 1
        ''', (feature, start_time))
        success_count = cursor.fetchone()[0]
        
        # Average duration
        cursor.execute('''
            SELECT AVG(duration_ms) FROM feature_usage 
            WHERE feature = ? AND timestamp >= ? AND duration_ms IS NOT NULL
        ''', (feature, start_time))
        avg_duration = cursor.fetchone()[0] or 0.0
        
        # Most common actions
        cursor.execute('''
            SELECT action, COUNT(*) as count FROM feature_usage 
            WHERE feature = ? AND timestamp >= ?
            GROUP BY action
            ORDER BY count DESC
            LIMIT 10
        ''', (feature, start_time))
        top_actions = [{'action': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'total_usage': total_count,
            'success_count': success_count,
            'success_rate': success_count / total_count if total_count > 0 else 0.0,
            'avg_duration_ms': avg_duration,
            'top_actions': top_actions
        }
    
    # ==================== Learning Effectiveness Metrics ====================
    
    def record_learning_effectiveness(self, feature: str, learning_type: str,
                                    accuracy: float, confidence: float,
                                    sample_size: int,
                                    improvement_rate: Optional[float] = None,
                                    metadata: Optional[Dict] = None):
        """Record learning effectiveness metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO learning_effectiveness 
            (timestamp, feature, learning_type, accuracy, confidence, sample_size, improvement_rate, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            feature,
            learning_type,
            accuracy,
            confidence,
            sample_size,
            improvement_rate,
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
    
    # ==================== Optimization Impact Metrics ====================
    
    def record_optimization_impact(self, feature: str, optimization_id: str,
                                  impact_category: str, before_value: float,
                                  after_value: float, user_impact_score: Optional[float] = None,
                                  metadata: Optional[Dict] = None):
        """Record optimization impact metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        improvement = ((after_value - before_value) / before_value * 100) if before_value > 0 else 0
        
        cursor.execute('''
            INSERT INTO optimization_impact 
            (timestamp, feature, optimization_id, impact_category, before_value, after_value, 
             improvement_percent, user_impact_score, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            feature,
            optimization_id,
            impact_category,
            before_value,
            after_value,
            improvement,
            user_impact_score,
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
    
    # ==================== Resource Utilization Metrics ====================
    
    def record_resource_utilization(self, resource_type: str, resource_name: str,
                                   utilization_percent: float,
                                   allocated: Optional[float] = None,
                                   used: Optional[float] = None,
                                   unit: Optional[str] = None,
                                   metadata: Optional[Dict] = None):
        """Record resource utilization metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO resource_utilization 
            (timestamp, resource_type, resource_name, utilization_percent, allocated, used, unit, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            resource_type,
            resource_name,
            utilization_percent,
            allocated,
            used,
            unit,
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
    
    # ==================== Error Metrics ====================
    
    def record_error(self, feature: str, error_type: str, error_severity: str,
                    error_message: Optional[str] = None,
                    recovery_attempted: bool = False,
                    recovery_successful: bool = False,
                    impact_level: Optional[str] = None,
                    metadata: Optional[Dict] = None):
        """Record error metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO error_metrics 
            (timestamp, feature, error_type, error_severity, error_message, 
             recovery_attempted, recovery_successful, impact_level, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            feature,
            error_type,
            error_severity,
            error_message,
            recovery_attempted,
            recovery_successful,
            impact_level,
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
    
    def get_error_stats(self, feature: Optional[str] = None, hours: int = 24) -> Dict[str, Any]:
        """Get error statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        query = "SELECT * FROM error_metrics WHERE timestamp >= ?"
        params = [start_time]
        
        if feature:
            query += " AND feature = ?"
            params.append(feature)
        
        cursor.execute(query, params)
        errors = cursor.fetchall()
        
        total_errors = len(errors)
        recovery_attempted = sum(1 for e in errors if e[6])  # recovery_attempted column
        recovery_successful = sum(1 for e in errors if e[7])  # recovery_successful column
        
        # Errors by severity
        cursor.execute(f'''
            SELECT error_severity, COUNT(*) FROM error_metrics 
            WHERE timestamp >= ? {"AND feature = ?" if feature else ""}
            GROUP BY error_severity
        ''', params)
        by_severity = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_errors': total_errors,
            'recovery_attempted': recovery_attempted,
            'recovery_successful': recovery_successful,
            'recovery_rate': recovery_successful / recovery_attempted if recovery_attempted > 0 else 0.0,
            'by_severity': by_severity
        }
    
    # ==================== Daily Aggregation ====================
    
    def aggregate_daily_metrics(self, date: Optional[str] = None):
        """Aggregate metrics for a specific date"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Aggregate system performance metrics
        cursor.execute('''
            INSERT OR REPLACE INTO daily_aggregates 
            (date, feature, metric_type, metric_name, avg_value, min_value, max_value, count)
            SELECT 
                DATE(timestamp) as date,
                feature,
                'performance' as metric_type,
                metric_name,
                AVG(value) as avg_value,
                MIN(value) as min_value,
                MAX(value) as max_value,
                COUNT(*) as count
            FROM system_performance
            WHERE DATE(timestamp) = ?
            GROUP BY DATE(timestamp), feature, metric_name
        ''', (date,))
        
        conn.commit()
        conn.close()
    
    # ==================== Comprehensive Dashboard ====================
    
    def get_comprehensive_dashboard(self, feature: Optional[str] = None,
                                   hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive metrics dashboard"""
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'time_range_hours': hours,
            'feature': feature or 'all'
        }
        
        # Performance metrics
        perf_metrics = self.get_performance_metrics(feature=feature, hours=hours)
        dashboard['performance'] = {
            'total_measurements': len(perf_metrics),
            'categories': {}
        }
        
        # Group by category
        by_category = defaultdict(list)
        for m in perf_metrics:
            by_category[m['metric_category']].append(m['value'])
        
        for category, values in by_category.items():
            dashboard['performance']['categories'][category] = {
                'avg': statistics.mean(values),
                'min': min(values),
                'max': max(values),
                'count': len(values)
            }
        
        # User satisfaction
        dashboard['satisfaction'] = self.get_satisfaction_metrics(feature=feature, hours=hours)
        
        # Feature usage
        if feature:
            dashboard['usage'] = self.get_feature_usage_stats(feature=feature, hours=hours)
        
        # Error metrics
        dashboard['errors'] = self.get_error_stats(feature=feature, hours=hours)
        
        return dashboard


# Global advanced metrics tracker instance
_global_advanced_metrics = None

def get_advanced_metrics() -> AdvancedMetricsTracker:
    """Get the global advanced metrics tracker instance"""
    global _global_advanced_metrics
    if _global_advanced_metrics is None:
        _global_advanced_metrics = AdvancedMetricsTracker()
    return _global_advanced_metrics


if __name__ == "__main__":
    # Test the advanced metrics tracker
    metrics = get_advanced_metrics()
    
    # Record various metrics
    metrics.record_performance_metric(
        feature="learning-engine",
        metric_category="response_time",
        metric_name="pattern_recognition_ms",
        value=125.5,
        unit="milliseconds"
    )
    
    metrics.record_satisfaction(
        feature="learning-engine",
        satisfaction_type="accuracy",
        score=0.92,
        feedback="Pattern recognition is very accurate"
    )
    
    metrics.record_feature_usage(
        feature="learning-engine",
        action="recognize_pattern",
        duration_ms=125.5,
        success=True
    )
    
    # Get dashboard
    dashboard = metrics.get_comprehensive_dashboard(feature="learning-engine", hours=24)
    print("\nComprehensive Dashboard:")
    print(json.dumps(dashboard, indent=2))
    
    print("\n✅ Advanced metrics tracker test complete!")
