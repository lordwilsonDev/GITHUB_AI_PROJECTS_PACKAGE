#!/usr/bin/env python3
"""
Productivity Metrics Analyzer

This module analyzes productivity metrics and identifies bottlenecks.
It tracks task completion rates, time efficiency, and performance trends.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import statistics


class ProductivityMetricsAnalyzer:
    """
    Analyzes productivity metrics to identify patterns and bottlenecks.
    """
    
    def __init__(self, db_path: str = "data/vy_nexus.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize productivity metrics tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Productivity metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productivity_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                period_start TIMESTAMP,
                period_end TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Bottlenecks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bottlenecks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bottleneck_type TEXT NOT NULL,
                description TEXT,
                severity TEXT DEFAULT 'medium',
                impact_score REAL DEFAULT 0.5,
                identified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                status TEXT DEFAULT 'active',
                metadata TEXT
            )
        """)
        
        # Performance snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_date DATE NOT NULL,
                tasks_completed INTEGER DEFAULT 0,
                tasks_failed INTEGER DEFAULT 0,
                avg_task_duration REAL,
                total_active_time REAL,
                efficiency_score REAL,
                metadata TEXT,
                UNIQUE(snapshot_date)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def record_metric(
        self,
        metric_type: str,
        metric_name: str,
        metric_value: float,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Record a productivity metric.
        
        Args:
            metric_type: Type of metric (completion_rate, efficiency, etc.)
            metric_name: Specific metric name
            metric_value: The metric value
            period_start: Start of measurement period
            period_end: End of measurement period
            metadata: Additional metadata
        
        Returns:
            Metric ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        period_start_str = period_start.isoformat() if period_start else None
        period_end_str = period_end.isoformat() if period_end else None
        
        cursor.execute("""
            INSERT INTO productivity_metrics
            (metric_type, metric_name, metric_value, period_start, period_end, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (metric_type, metric_name, metric_value, period_start_str, period_end_str, metadata_json))
        
        metric_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return metric_id
    
    def record_bottleneck(
        self,
        bottleneck_type: str,
        description: str,
        severity: str = "medium",
        impact_score: float = 0.5,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Record a productivity bottleneck.
        
        Args:
            bottleneck_type: Type of bottleneck (time, resource, process, etc.)
            description: Description of the bottleneck
            severity: Severity level (low, medium, high, critical)
            impact_score: Impact score (0-1)
            metadata: Additional metadata
        
        Returns:
            Bottleneck ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT INTO bottlenecks
            (bottleneck_type, description, severity, impact_score, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (bottleneck_type, description, severity, impact_score, metadata_json))
        
        bottleneck_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return bottleneck_id
    
    def analyze_task_completion_rate(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyze task completion rates over a period.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dictionary with completion rate analysis
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Check if tasks table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='tasks'
        """)
        
        if not cursor.fetchone():
            conn.close()
            return {"status": "no_data", "message": "No task data available"}
        
        # Get task statistics
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM tasks
            WHERE created_at > ?
            GROUP BY status
        """, (cutoff_date,))
        
        status_counts = dict(cursor.fetchall())
        conn.close()
        
        if not status_counts:
            return {"status": "no_data", "message": "No tasks in the specified period"}
        
        total_tasks = sum(status_counts.values())
        completed_tasks = status_counts.get('completed', 0)
        failed_tasks = status_counts.get('failed', 0)
        pending_tasks = status_counts.get('pending', 0)
        
        completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
        failure_rate = failed_tasks / total_tasks if total_tasks > 0 else 0
        
        # Record this metric
        period_start = datetime.now() - timedelta(days=days)
        period_end = datetime.now()
        
        self.record_metric(
            "completion_rate",
            f"{days}_day_completion_rate",
            completion_rate,
            period_start,
            period_end,
            {"total_tasks": total_tasks}
        )
        
        # Identify bottleneck if completion rate is low
        if completion_rate < 0.7 and total_tasks >= 5:
            self.record_bottleneck(
                "low_completion_rate",
                f"Task completion rate is {completion_rate:.1%} over the last {days} days",
                severity="high" if completion_rate < 0.5 else "medium",
                impact_score=1.0 - completion_rate
            )
        
        return {
            "status": "success",
            "period_days": days,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": completion_rate,
            "failure_rate": failure_rate,
            "status_distribution": status_counts
        }
    
    def analyze_time_efficiency(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyze time efficiency based on task durations.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dictionary with time efficiency analysis
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT task_type, duration_seconds, status
            FROM tasks
            WHERE created_at > ? AND duration_seconds IS NOT NULL
        """, (cutoff_date,))
        
        tasks = cursor.fetchall()
        conn.close()
        
        if not tasks:
            return {"status": "no_data", "message": "No task duration data available"}
        
        # Analyze by task type
        by_type = defaultdict(list)
        for task_type, duration, status in tasks:
            if status == 'completed':
                by_type[task_type].append(duration)
        
        efficiency_by_type = {}
        for task_type, durations in by_type.items():
            if durations:
                efficiency_by_type[task_type] = {
                    "avg_duration_seconds": statistics.mean(durations),
                    "median_duration_seconds": statistics.median(durations),
                    "min_duration_seconds": min(durations),
                    "max_duration_seconds": max(durations),
                    "task_count": len(durations)
                }
        
        # Calculate overall efficiency
        all_durations = [d for durations in by_type.values() for d in durations]
        overall_avg = statistics.mean(all_durations) if all_durations else 0
        
        # Record metric
        self.record_metric(
            "time_efficiency",
            "avg_task_duration",
            overall_avg,
            datetime.now() - timedelta(days=days),
            datetime.now(),
            {"task_count": len(all_durations)}
        )
        
        return {
            "status": "success",
            "period_days": days,
            "overall_avg_duration_seconds": overall_avg,
            "efficiency_by_type": efficiency_by_type,
            "total_tasks_analyzed": len(all_durations)
        }
    
    def identify_bottlenecks(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Identify productivity bottlenecks.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            List of identified bottlenecks
        """
        bottlenecks = []
        
        # Analyze completion rate
        completion_analysis = self.analyze_task_completion_rate(days)
        if completion_analysis.get("status") == "success":
            if completion_analysis["completion_rate"] < 0.7:
                bottlenecks.append({
                    "type": "low_completion_rate",
                    "severity": "high" if completion_analysis["completion_rate"] < 0.5 else "medium",
                    "description": f"Task completion rate is {completion_analysis['completion_rate']:.1%}",
                    "impact_score": 1.0 - completion_analysis["completion_rate"],
                    "recommendation": "Review failed tasks and identify common failure patterns"
                })
        
        # Analyze time efficiency
        time_analysis = self.analyze_time_efficiency(days)
        if time_analysis.get("status") == "success":
            # Check for task types with unusually long durations
            for task_type, metrics in time_analysis.get("efficiency_by_type", {}).items():
                avg_duration = metrics["avg_duration_seconds"]
                if avg_duration > 600:  # More than 10 minutes
                    bottlenecks.append({
                        "type": "long_task_duration",
                        "severity": "medium",
                        "description": f"{task_type} tasks take an average of {avg_duration/60:.1f} minutes",
                        "impact_score": min(1.0, avg_duration / 1800),  # Normalize to 30 min
                        "recommendation": f"Consider optimizing or automating {task_type} tasks"
                    })
        
        # Get active bottlenecks from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT bottleneck_type, description, severity, impact_score, identified_at
            FROM bottlenecks
            WHERE status = 'active'
            ORDER BY impact_score DESC, identified_at DESC
        """)
        
        for row in cursor.fetchall():
            bottlenecks.append({
                "type": row[0],
                "description": row[1],
                "severity": row[2],
                "impact_score": row[3],
                "identified_at": row[4]
            })
        
        conn.close()
        
        # Sort by impact score
        bottlenecks.sort(key=lambda x: x["impact_score"], reverse=True)
        
        return bottlenecks
    
    def create_daily_snapshot(self, date: Optional[datetime] = None) -> int:
        """
        Create a daily performance snapshot.
        
        Args:
            date: Date for the snapshot (defaults to today)
        
        Returns:
            Snapshot ID
        """
        if date is None:
            date = datetime.now()
        
        snapshot_date = date.date().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get tasks for the day
        cursor.execute("""
            SELECT status, duration_seconds
            FROM tasks
            WHERE DATE(created_at) = ?
        """, (snapshot_date,))
        
        tasks = cursor.fetchall()
        
        tasks_completed = sum(1 for status, _ in tasks if status == 'completed')
        tasks_failed = sum(1 for status, _ in tasks if status == 'failed')
        
        durations = [d for _, d in tasks if d is not None]
        avg_duration = statistics.mean(durations) if durations else None
        
        # Calculate efficiency score (0-1)
        total_tasks = len(tasks)
        if total_tasks > 0:
            completion_rate = tasks_completed / total_tasks
            failure_rate = tasks_failed / total_tasks
            efficiency_score = completion_rate * (1 - failure_rate)
        else:
            efficiency_score = 0.0
        
        # Insert or update snapshot
        try:
            cursor.execute("""
                INSERT INTO performance_snapshots
                (snapshot_date, tasks_completed, tasks_failed, avg_task_duration, efficiency_score)
                VALUES (?, ?, ?, ?, ?)
            """, (snapshot_date, tasks_completed, tasks_failed, avg_duration, efficiency_score))
            snapshot_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            # Update existing snapshot
            cursor.execute("""
                UPDATE performance_snapshots
                SET tasks_completed = ?, tasks_failed = ?, avg_task_duration = ?, efficiency_score = ?
                WHERE snapshot_date = ?
            """, (tasks_completed, tasks_failed, avg_duration, efficiency_score, snapshot_date))
            
            cursor.execute("""
                SELECT id FROM performance_snapshots WHERE snapshot_date = ?
            """, (snapshot_date,))
            snapshot_id = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        return snapshot_id
    
    def get_performance_trend(self, days: int = 30) -> Dict[str, Any]:
        """
        Get performance trend over time.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dictionary with trend data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        
        cursor.execute("""
            SELECT snapshot_date, tasks_completed, tasks_failed, efficiency_score
            FROM performance_snapshots
            WHERE snapshot_date >= ?
            ORDER BY snapshot_date ASC
        """, (cutoff_date,))
        
        snapshots = cursor.fetchall()
        conn.close()
        
        if not snapshots:
            return {"status": "no_data", "message": "No performance snapshots available"}
        
        # Calculate trends
        efficiency_scores = [s[3] for s in snapshots if s[3] is not None]
        
        trend_data = {
            "status": "success",
            "period_days": days,
            "snapshots": [
                {
                    "date": s[0],
                    "tasks_completed": s[1],
                    "tasks_failed": s[2],
                    "efficiency_score": s[3]
                }
                for s in snapshots
            ],
            "avg_efficiency": statistics.mean(efficiency_scores) if efficiency_scores else 0,
            "trend": "improving" if len(efficiency_scores) >= 2 and efficiency_scores[-1] > efficiency_scores[0] else "declining"
        }
        
        return trend_data
    
    def generate_productivity_report(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate a comprehensive productivity report.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dictionary with comprehensive report
        """
        report = {
            "report_date": datetime.now().isoformat(),
            "period_days": days,
            "completion_analysis": self.analyze_task_completion_rate(days),
            "time_efficiency": self.analyze_time_efficiency(days),
            "bottlenecks": self.identify_bottlenecks(days),
            "performance_trend": self.get_performance_trend(days)
        }
        
        # Add summary
        completion_rate = report["completion_analysis"].get("completion_rate", 0)
        bottleneck_count = len(report["bottlenecks"])
        
        if completion_rate >= 0.8 and bottleneck_count <= 2:
            overall_status = "excellent"
        elif completion_rate >= 0.6 and bottleneck_count <= 5:
            overall_status = "good"
        elif completion_rate >= 0.4:
            overall_status = "needs_improvement"
        else:
            overall_status = "critical"
        
        report["summary"] = {
            "overall_status": overall_status,
            "completion_rate": completion_rate,
            "bottleneck_count": bottleneck_count,
            "key_recommendations": [
                b["recommendation"] for b in report["bottlenecks"][:3] if "recommendation" in b
            ]
        }
        
        return report


if __name__ == "__main__":
    # Example usage
    analyzer = ProductivityMetricsAnalyzer()
    
    # Generate report
    report = analyzer.generate_productivity_report(days=7)
    print("Productivity Report:")
    print(json.dumps(report, indent=2))
