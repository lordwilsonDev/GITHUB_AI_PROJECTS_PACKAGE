#!/usr/bin/env python3
"""
Performance Metrics Database Structure
Centralized database for tracking all system performance metrics

Part of the Self-Evolving AI Ecosystem
Created: December 15, 2025
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import hashlib


class PerformanceMetricsDB:
    """Centralized database for performance metrics tracking"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.path.expanduser("~/vy-nexus"))
        self.data_path = self.base_path / "data" / "metrics"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.data_path / "performance_metrics.db"
        self.conn = None
        self.cursor = None
        
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with all required tables"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        
        # Enable foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create tables
        self._create_tables()
        self.conn.commit()
        
        print(f"✅ Performance Metrics Database initialized: {self.db_path}")
    
    def _create_tables(self):
        """Create all database tables"""
        
        # 1. System Metrics Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                category TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Task Performance Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                task_type TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                duration_seconds REAL,
                status TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                expert_used TEXT,
                confidence_score REAL,
                resource_usage TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. Learning Metrics Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                patterns_identified INTEGER DEFAULT 0,
                preferences_learned INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                failure_rate REAL DEFAULT 0.0,
                avg_task_duration REAL DEFAULT 0.0,
                total_tasks INTEGER DEFAULT 0,
                knowledge_updates INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 4. Optimization Metrics Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS optimization_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                optimization_id TEXT UNIQUE NOT NULL,
                optimization_type TEXT NOT NULL,
                target_process TEXT NOT NULL,
                baseline_value REAL,
                optimized_value REAL,
                improvement_percent REAL,
                time_saved_seconds REAL DEFAULT 0.0,
                status TEXT NOT NULL,
                implemented_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 5. Automation Metrics Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS automation_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                automation_id TEXT UNIQUE NOT NULL,
                automation_name TEXT NOT NULL,
                task_type TEXT NOT NULL,
                execution_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                total_time_saved REAL DEFAULT 0.0,
                avg_execution_time REAL DEFAULT 0.0,
                status TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_executed TEXT
            )
        """)
        
        # 6. Adaptation Metrics Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS adaptation_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                adaptation_type TEXT NOT NULL,
                component TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                reason TEXT,
                impact_score REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 7. Error Patterns Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_hash TEXT UNIQUE NOT NULL,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                occurrence_count INTEGER DEFAULT 1,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                resolution_strategy TEXT,
                resolved BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 8. Resource Usage Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS resource_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_percent REAL,
                memory_mb REAL,
                disk_usage_mb REAL,
                network_io_mb REAL,
                active_tasks INTEGER,
                queue_depth INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 9. Evolution Cycles Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS evolution_cycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_id TEXT UNIQUE NOT NULL,
                cycle_type TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                duration_seconds REAL,
                activities_completed INTEGER DEFAULT 0,
                improvements_implemented INTEGER DEFAULT 0,
                status TEXT NOT NULL,
                results TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 10. Daily Summaries Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL,
                total_tasks INTEGER DEFAULT 0,
                successful_tasks INTEGER DEFAULT 0,
                failed_tasks INTEGER DEFAULT 0,
                patterns_identified INTEGER DEFAULT 0,
                optimizations_implemented INTEGER DEFAULT 0,
                automations_created INTEGER DEFAULT 0,
                time_saved_hours REAL DEFAULT 0.0,
                avg_success_rate REAL DEFAULT 0.0,
                evolution_cycles INTEGER DEFAULT 0,
                report_path TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better query performance
        self._create_indexes()
    
    def _create_indexes(self):
        """Create indexes for frequently queried columns"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_system_metrics_name ON system_metrics(metric_name)",
            "CREATE INDEX IF NOT EXISTS idx_task_performance_type ON task_performance(task_type)",
            "CREATE INDEX IF NOT EXISTS idx_task_performance_status ON task_performance(status)",
            "CREATE INDEX IF NOT EXISTS idx_task_performance_started ON task_performance(started_at)",
            "CREATE INDEX IF NOT EXISTS idx_optimization_type ON optimization_metrics(optimization_type)",
            "CREATE INDEX IF NOT EXISTS idx_automation_type ON automation_metrics(task_type)",
            "CREATE INDEX IF NOT EXISTS idx_error_patterns_type ON error_patterns(error_type)",
            "CREATE INDEX IF NOT EXISTS idx_evolution_cycles_type ON evolution_cycles(cycle_type)",
            "CREATE INDEX IF NOT EXISTS idx_daily_summaries_date ON daily_summaries(date)"
        ]
        
        for index_sql in indexes:
            self.cursor.execute(index_sql)
    
    # ==================== INSERT METHODS ====================
    
    def record_system_metric(self, metric_name: str, value: float, 
                            unit: str = None, category: str = None,
                            metadata: Dict = None) -> int:
        """Record a system metric"""
        timestamp = datetime.utcnow().isoformat()
        metadata_json = json.dumps(metadata) if metadata else None
        
        self.cursor.execute("""
            INSERT INTO system_metrics (timestamp, metric_name, metric_value, metric_unit, category, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (timestamp, metric_name, value, unit, category, metadata_json))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def record_task_performance(self, task_id: str, task_type: str, 
                               started_at: str, completed_at: str = None,
                               duration: float = None, status: str = "completed",
                               success: bool = True, error_message: str = None,
                               expert_used: str = None, confidence_score: float = None,
                               resource_usage: Dict = None) -> int:
        """Record task performance metrics"""
        resource_json = json.dumps(resource_usage) if resource_usage else None
        
        self.cursor.execute("""
            INSERT OR REPLACE INTO task_performance 
            (task_id, task_type, started_at, completed_at, duration_seconds, status, 
             success, error_message, expert_used, confidence_score, resource_usage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (task_id, task_type, started_at, completed_at, duration, status,
              success, error_message, expert_used, confidence_score, resource_json))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def record_learning_snapshot(self, patterns: int = 0, preferences: int = 0,
                                success_rate: float = 0.0, failure_rate: float = 0.0,
                                avg_duration: float = 0.0, total_tasks: int = 0,
                                knowledge_updates: int = 0) -> int:
        """Record learning metrics snapshot"""
        timestamp = datetime.utcnow().isoformat()
        
        self.cursor.execute("""
            INSERT INTO learning_metrics 
            (timestamp, patterns_identified, preferences_learned, success_rate, 
             failure_rate, avg_task_duration, total_tasks, knowledge_updates)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, patterns, preferences, success_rate, failure_rate,
              avg_duration, total_tasks, knowledge_updates))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def record_optimization(self, optimization_id: str, opt_type: str,
                          target_process: str, baseline: float = None,
                          optimized: float = None, improvement: float = None,
                          time_saved: float = 0.0, status: str = "proposed",
                          implemented_at: str = None) -> int:
        """Record optimization metrics"""
        timestamp = datetime.utcnow().isoformat()
        
        self.cursor.execute("""
            INSERT OR REPLACE INTO optimization_metrics
            (timestamp, optimization_id, optimization_type, target_process,
             baseline_value, optimized_value, improvement_percent, time_saved_seconds,
             status, implemented_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, optimization_id, opt_type, target_process, baseline,
              optimized, improvement, time_saved, status, implemented_at))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def record_automation(self, automation_id: str, name: str, task_type: str,
                         execution_count: int = 0, success_count: int = 0,
                         failure_count: int = 0, time_saved: float = 0.0,
                         avg_exec_time: float = 0.0, status: str = "active",
                         last_executed: str = None) -> int:
        """Record automation metrics"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO automation_metrics
            (automation_id, automation_name, task_type, execution_count,
             success_count, failure_count, total_time_saved, avg_execution_time,
             status, last_executed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (automation_id, name, task_type, execution_count, success_count,
              failure_count, time_saved, avg_exec_time, status, last_executed))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def record_adaptation(self, adaptation_type: str, component: str,
                         old_value: str = None, new_value: str = None,
                         reason: str = None, impact_score: float = None) -> int:
        """Record system adaptation"""
        timestamp = datetime.utcnow().isoformat()
        
        self.cursor.execute("""
            INSERT INTO adaptation_metrics
            (timestamp, adaptation_type, component, old_value, new_value, reason, impact_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, adaptation_type, component, old_value, new_value, reason, impact_score))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def record_error_pattern(self, error_type: str, error_message: str,
                           resolution_strategy: str = None) -> int:
        """Record error pattern"""
        error_hash = hashlib.sha256(f"{error_type}:{error_message}".encode()).hexdigest()[:16]
        timestamp = datetime.utcnow().isoformat()
        
        # Check if error already exists
        self.cursor.execute("""
            SELECT id, occurrence_count FROM error_patterns WHERE error_hash = ?
        """, (error_hash,))
        
        result = self.cursor.fetchone()
        
        if result:
            # Update existing error
            error_id, count = result
            self.cursor.execute("""
                UPDATE error_patterns 
                SET occurrence_count = ?, last_seen = ?, resolution_strategy = ?
                WHERE id = ?
            """, (count + 1, timestamp, resolution_strategy, error_id))
        else:
            # Insert new error
            self.cursor.execute("""
                INSERT INTO error_patterns
                (error_hash, error_type, error_message, first_seen, last_seen, resolution_strategy)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (error_hash, error_type, error_message, timestamp, timestamp, resolution_strategy))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def record_resource_usage(self, cpu: float = None, memory: float = None,
                            disk: float = None, network: float = None,
                            active_tasks: int = 0, queue_depth: int = 0) -> int:
        """Record resource usage snapshot"""
        timestamp = datetime.utcnow().isoformat()
        
        self.cursor.execute("""
            INSERT INTO resource_usage
            (timestamp, cpu_percent, memory_mb, disk_usage_mb, network_io_mb,
             active_tasks, queue_depth)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, cpu, memory, disk, network, active_tasks, queue_depth))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def record_evolution_cycle(self, cycle_id: str, cycle_type: str,
                             started_at: str, completed_at: str = None,
                             duration: float = None, activities: int = 0,
                             improvements: int = 0, status: str = "running",
                             results: Dict = None) -> int:
        """Record evolution cycle"""
        results_json = json.dumps(results) if results else None
        
        self.cursor.execute("""
            INSERT OR REPLACE INTO evolution_cycles
            (cycle_id, cycle_type, started_at, completed_at, duration_seconds,
             activities_completed, improvements_implemented, status, results)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (cycle_id, cycle_type, started_at, completed_at, duration,
              activities, improvements, status, results_json))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def record_daily_summary(self, date: str, total_tasks: int = 0,
                           successful: int = 0, failed: int = 0,
                           patterns: int = 0, optimizations: int = 0,
                           automations: int = 0, time_saved: float = 0.0,
                           success_rate: float = 0.0, cycles: int = 0,
                           report_path: str = None) -> int:
        """Record daily summary"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO daily_summaries
            (date, total_tasks, successful_tasks, failed_tasks, patterns_identified,
             optimizations_implemented, automations_created, time_saved_hours,
             avg_success_rate, evolution_cycles, report_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (date, total_tasks, successful, failed, patterns, optimizations,
              automations, time_saved, success_rate, cycles, report_path))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    # ==================== QUERY METHODS ====================
    
    def get_recent_metrics(self, metric_name: str, limit: int = 100) -> List[Tuple]:
        """Get recent values for a specific metric"""
        self.cursor.execute("""
            SELECT timestamp, metric_value, metric_unit
            FROM system_metrics
            WHERE metric_name = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (metric_name, limit))
        
        return self.cursor.fetchall()
    
    def get_task_performance_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get task performance summary for last N days"""
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total_tasks,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed,
                AVG(duration_seconds) as avg_duration,
                AVG(confidence_score) as avg_confidence
            FROM task_performance
            WHERE started_at >= datetime('now', '-' || ? || ' days')
        """, (days,))
        
        result = self.cursor.fetchone()
        
        return {
            "total_tasks": result[0] or 0,
            "successful": result[1] or 0,
            "failed": result[2] or 0,
            "avg_duration": round(result[3] or 0, 2),
            "avg_confidence": round(result[4] or 0, 2),
            "success_rate": round((result[1] or 0) / (result[0] or 1) * 100, 2)
        }
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get optimization summary"""
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'implemented' THEN 1 ELSE 0 END) as implemented,
                SUM(time_saved_seconds) as total_time_saved,
                AVG(improvement_percent) as avg_improvement
            FROM optimization_metrics
        """)
        
        result = self.cursor.fetchone()
        
        return {
            "total_optimizations": result[0] or 0,
            "implemented": result[1] or 0,
            "total_time_saved_hours": round((result[2] or 0) / 3600, 2),
            "avg_improvement_percent": round(result[3] or 0, 2)
        }
    
    def get_automation_summary(self) -> Dict[str, Any]:
        """Get automation summary"""
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                SUM(execution_count) as total_executions,
                SUM(total_time_saved) as time_saved
            FROM automation_metrics
        """)
        
        result = self.cursor.fetchone()
        
        return {
            "total_automations": result[0] or 0,
            "active_automations": result[1] or 0,
            "total_executions": result[2] or 0,
            "total_time_saved_hours": round((result[3] or 0) / 3600, 2)
        }
    
    def get_error_patterns_summary(self) -> List[Dict[str, Any]]:
        """Get most common error patterns"""
        self.cursor.execute("""
            SELECT error_type, error_message, occurrence_count, resolved
            FROM error_patterns
            ORDER BY occurrence_count DESC
            LIMIT 10
        """)
        
        results = self.cursor.fetchall()
        
        return [
            {
                "error_type": r[0],
                "error_message": r[1],
                "occurrence_count": r[2],
                "resolved": bool(r[3])
            }
            for r in results
        ]
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✅ Database connection closed")


if __name__ == "__main__":
    # Test the database
    print("📊 Performance Metrics Database - Test Mode")
    print("="*60)
    
    db = PerformanceMetricsDB()
    
    # Record some test data
    print("\n📝 Recording test metrics...")
    
    db.record_system_metric("cpu_usage", 45.5, "percent", "system")
    db.record_system_metric("memory_usage", 2048.0, "MB", "system")
    
    db.record_task_performance(
        "task-001", "code_generation", 
        datetime.utcnow().isoformat(),
        datetime.utcnow().isoformat(),
        2.5, "completed", True, None, "code-expert", 0.95
    )
    
    db.record_learning_snapshot(
        patterns=5, preferences=3, success_rate=92.5,
        failure_rate=7.5, avg_duration=3.2, total_tasks=20,
        knowledge_updates=8
    )
    
    print("✅ Test data recorded")
    
    # Query summaries
    print("\n📊 Querying summaries...")
    
    task_summary = db.get_task_performance_summary(7)
    print(f"\nTask Performance (7 days):")
    print(f"  Total tasks: {task_summary['total_tasks']}")
    print(f"  Success rate: {task_summary['success_rate']}%")
    print(f"  Avg duration: {task_summary['avg_duration']}s")
    
    opt_summary = db.get_optimization_summary()
    print(f"\nOptimizations:")
    print(f"  Total: {opt_summary['total_optimizations']}")
    print(f"  Implemented: {opt_summary['implemented']}")
    
    auto_summary = db.get_automation_summary()
    print(f"\nAutomations:")
    print(f"  Total: {auto_summary['total_automations']}")
    print(f"  Active: {auto_summary['active_automations']}")
    
    db.close()
    
    print("\n✨ Database test complete!")
