#!/usr/bin/env python3
"""
Database Manager for Level 33 Sovereign Architecture

Provides:
- SQLite database management
- Activity logging
- Metrics storage
- Query helpers
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Centralized database management."""
    
    def __init__(self, db_path: str = "data/level33.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn: Optional[sqlite3.Connection] = None
        self._connect()
        self._create_tables()
    
    def _connect(self) -> None:
        """Connect to database."""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Activity log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                activity_type TEXT NOT NULL,
                component TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                status TEXT,
                duration_seconds REAL,
                error_message TEXT
            )
        """)
        
        # Metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                tags TEXT
            )
        """)
        
        # Automation runs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS automation_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                automation_name TEXT NOT NULL,
                status TEXT NOT NULL,
                duration_seconds REAL,
                input_params TEXT,
                output_result TEXT,
                error_message TEXT
            )
        """)
        
        # Configuration history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                config_key TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                changed_by TEXT
            )
        """)
        
        # LLM interactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS llm_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                model TEXT NOT NULL,
                prompt TEXT NOT NULL,
                response TEXT,
                tokens_used INTEGER,
                duration_seconds REAL,
                success BOOLEAN
            )
        """)
        
        self.conn.commit()
        logger.info("Database tables created/verified")
    
    def log_activity(self, activity_type: str, component: str, action: str,
                    details: Optional[Dict] = None, status: str = "success",
                    duration: Optional[float] = None, error: Optional[str] = None) -> int:
        """
        Log an activity.
        
        Args:
            activity_type: Type of activity (automation, tool, agent, etc.)
            component: Component name
            action: Action performed
            details: Additional details (will be JSON serialized)
            status: Status (success, failure, warning)
            duration: Duration in seconds
            error: Error message if any
        
        Returns:
            Activity log ID
        """
        cursor = self.conn.cursor()
        
        details_json = json.dumps(details) if details else None
        
        cursor.execute("""
            INSERT INTO activity_log 
            (activity_type, component, action, details, status, duration_seconds, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (activity_type, component, action, details_json, status, duration, error))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def log_metric(self, metric_name: str, value: float, unit: Optional[str] = None,
                  tags: Optional[Dict] = None) -> int:
        """
        Log a metric.
        
        Args:
            metric_name: Name of metric
            value: Metric value
            unit: Unit of measurement
            tags: Additional tags (will be JSON serialized)
        
        Returns:
            Metric log ID
        """
        cursor = self.conn.cursor()
        
        tags_json = json.dumps(tags) if tags else None
        
        cursor.execute("""
            INSERT INTO metrics (metric_name, metric_value, metric_unit, tags)
            VALUES (?, ?, ?, ?)
        """, (metric_name, value, unit, tags_json))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def log_automation_run(self, automation_name: str, status: str,
                          duration: Optional[float] = None,
                          input_params: Optional[Dict] = None,
                          output_result: Optional[Dict] = None,
                          error: Optional[str] = None) -> int:
        """
        Log an automation run.
        
        Args:
            automation_name: Name of automation
            status: Status (success, failure)
            duration: Duration in seconds
            input_params: Input parameters
            output_result: Output result
            error: Error message if any
        
        Returns:
            Automation run ID
        """
        cursor = self.conn.cursor()
        
        input_json = json.dumps(input_params) if input_params else None
        output_json = json.dumps(output_result) if output_result else None
        
        cursor.execute("""
            INSERT INTO automation_runs 
            (automation_name, status, duration_seconds, input_params, output_result, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (automation_name, status, duration, input_json, output_json, error))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def log_llm_interaction(self, model: str, prompt: str, response: Optional[str] = None,
                           tokens: Optional[int] = None, duration: Optional[float] = None,
                           success: bool = True) -> int:
        """
        Log an LLM interaction.
        
        Args:
            model: Model name
            prompt: Prompt sent to LLM
            response: Response from LLM
            tokens: Tokens used
            duration: Duration in seconds
            success: Whether interaction was successful
        
        Returns:
            LLM interaction ID
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO llm_interactions 
            (model, prompt, response, tokens_used, duration_seconds, success)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (model, prompt, response, tokens, duration, success))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_recent_activities(self, limit: int = 100, activity_type: Optional[str] = None) -> List[Dict]:
        """
        Get recent activities.
        
        Args:
            limit: Maximum number of activities to return
            activity_type: Filter by activity type
        
        Returns:
            List of activity dictionaries
        """
        cursor = self.conn.cursor()
        
        if activity_type:
            cursor.execute("""
                SELECT * FROM activity_log 
                WHERE activity_type = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (activity_type, limit))
        else:
            cursor.execute("""
                SELECT * FROM activity_log 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_metrics(self, metric_name: Optional[str] = None, 
                   hours: int = 24) -> List[Dict]:
        """
        Get metrics from last N hours.
        
        Args:
            metric_name: Filter by metric name
            hours: Number of hours to look back
        
        Returns:
            List of metric dictionaries
        """
        cursor = self.conn.cursor()
        
        if metric_name:
            cursor.execute("""
                SELECT * FROM metrics 
                WHERE metric_name = ? 
                AND timestamp >= datetime('now', '-' || ? || ' hours')
                ORDER BY timestamp DESC
            """, (metric_name, hours))
        else:
            cursor.execute("""
                SELECT * FROM metrics 
                WHERE timestamp >= datetime('now', '-' || ? || ' hours')
                ORDER BY timestamp DESC
            """, (hours,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_automation_stats(self, automation_name: Optional[str] = None) -> Dict:
        """
        Get automation statistics.
        
        Args:
            automation_name: Filter by automation name
        
        Returns:
            Statistics dictionary
        """
        cursor = self.conn.cursor()
        
        if automation_name:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_runs,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_runs,
                    SUM(CASE WHEN status = 'failure' THEN 1 ELSE 0 END) as failed_runs,
                    AVG(duration_seconds) as avg_duration,
                    MAX(duration_seconds) as max_duration,
                    MIN(duration_seconds) as min_duration
                FROM automation_runs
                WHERE automation_name = ?
            """, (automation_name,))
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_runs,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_runs,
                    SUM(CASE WHEN status = 'failure' THEN 1 ELSE 0 END) as failed_runs,
                    AVG(duration_seconds) as avg_duration,
                    MAX(duration_seconds) as max_duration,
                    MIN(duration_seconds) as min_duration
                FROM automation_runs
            """)
        
        row = cursor.fetchone()
        return dict(row) if row else {}
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


# Global database instance
_db_instance: Optional[DatabaseManager] = None


def get_database() -> DatabaseManager:
    """Get global database instance."""
    global _db_instance
    
    if _db_instance is None:
        _db_instance = DatabaseManager()
    
    return _db_instance


if __name__ == "__main__":
    # Test database
    db = DatabaseManager()
    
    print("\n=== Database Manager Test ===")
    
    # Log some test data
    print("\nLogging test activity...")
    db.log_activity(
        activity_type="automation",
        component="workspace_launcher",
        action="launch",
        details={"apps": ["Terminal", "Chrome"]},
        status="success",
        duration=2.5
    )
    
    print("Logging test metric...")
    db.log_metric(
        metric_name="cpu_usage",
        value=45.2,
        unit="percent",
        tags={"host": "localhost"}
    )
    
    print("Logging test automation run...")
    db.log_automation_run(
        automation_name="file_organizer",
        status="success",
        duration=1.8,
        input_params={"dry_run": False},
        output_result={"files_moved": 15}
    )
    
    # Query data
    print("\nRecent activities:")
    activities = db.get_recent_activities(limit=5)
    for activity in activities:
        print(f"  • {activity['timestamp']}: {activity['component']} - {activity['action']}")
    
    print("\nAutomation stats:")
    stats = db.get_automation_stats()
    print(f"  Total runs: {stats.get('total_runs', 0)}")
    print(f"  Successful: {stats.get('successful_runs', 0)}")
    print(f"  Failed: {stats.get('failed_runs', 0)}")
    print(f"  Avg duration: {stats.get('avg_duration', 0):.2f}s")
    
    db.close()
    print("\n=== Test Complete ===")
