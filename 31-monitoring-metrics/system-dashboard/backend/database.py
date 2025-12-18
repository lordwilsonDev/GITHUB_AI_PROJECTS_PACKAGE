"""Database connection and utilities for Vy System Dashboard"""
import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime
from typing import List, Dict, Any, Optional
import json


class Database:
    """SQLite database manager for monitoring data"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to database in parent directory
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'database', 'monitoring.db')
        
        self.db_path = db_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Ensure database file and directory exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Create database if it doesn't exist
        if not os.path.exists(self.db_path):
            print(f"Creating new database at {self.db_path}")
            self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with schema and seed data"""
        schema_path = os.path.join(
            os.path.dirname(self.db_path), 'schema.sql'
        )
        seed_path = os.path.join(
            os.path.dirname(self.db_path), 'seed_data.sql'
        )
        
        with self.get_connection() as conn:
            # Execute schema
            if os.path.exists(schema_path):
                with open(schema_path, 'r') as f:
                    conn.executescript(f.read())
                print("Database schema created")
            
            # Execute seed data
            if os.path.exists(seed_path):
                with open(seed_path, 'r') as f:
                    conn.executescript(f.read())
                print("Seed data inserted")
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results as list of dicts"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            columns = [description[0] for description in cursor.description]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT query and return last inserted row ID"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    # Service methods
    def get_all_services(self) -> List[Dict[str, Any]]:
        """Get all registered services"""
        return self.execute_query(
            "SELECT * FROM services ORDER BY category, name"
        )
    
    def get_service_by_id(self, service_id: int) -> Optional[Dict[str, Any]]:
        """Get service by ID"""
        results = self.execute_query(
            "SELECT * FROM services WHERE id = ?",
            (service_id,)
        )
        return results[0] if results else None
    
    def get_service_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get service by name"""
        results = self.execute_query(
            "SELECT * FROM services WHERE name = ?",
            (name,)
        )
        return results[0] if results else None
    
    # Health check methods
    def insert_health_check(self, service_id: int, status: str, 
                           response_time_ms: float = None,
                           status_code: int = None,
                           error_message: str = None) -> int:
        """Insert a health check record"""
        return self.execute_insert(
            """
            INSERT INTO health_checks 
            (service_id, status, response_time_ms, status_code, error_message)
            VALUES (?, ?, ?, ?, ?)
            """,
            (service_id, status, response_time_ms, status_code, error_message)
        )
    
    def get_latest_health_checks(self) -> List[Dict[str, Any]]:
        """Get latest health check for each service"""
        return self.execute_query(
            "SELECT * FROM latest_service_status"
        )
    
    def get_service_health_history(self, service_id: int, 
                                   hours: int = 24) -> List[Dict[str, Any]]:
        """Get health check history for a service"""
        return self.execute_query(
            """
            SELECT * FROM health_checks
            WHERE service_id = ?
            AND checked_at >= datetime('now', ? || ' hours')
            ORDER BY checked_at DESC
            """,
            (service_id, f'-{hours}')
        )
    
    def get_last_health_check(self, service_id: int) -> Optional[Dict[str, Any]]:
        """Get the most recent health check for a service"""
        results = self.execute_query(
            """
            SELECT * FROM health_checks
            WHERE service_id = ?
            ORDER BY checked_at DESC
            LIMIT 1
            """,
            (service_id,)
        )
        return results[0] if results else None
    
    # Metrics methods
    def insert_metric(self, service_id: int, metric_name: str, 
                     metric_value: float, metric_unit: str = None) -> int:
        """Insert a metric record"""
        return self.execute_insert(
            """
            INSERT INTO metrics 
            (service_id, metric_name, metric_value, metric_unit)
            VALUES (?, ?, ?, ?)
            """,
            (service_id, metric_name, metric_value, metric_unit)
        )
    
    def get_service_metrics(self, service_id: int, metric_name: str = None,
                           hours: int = 24) -> List[Dict[str, Any]]:
        """Get metrics for a service"""
        if metric_name:
            return self.execute_query(
                """
                SELECT * FROM metrics
                WHERE service_id = ? AND metric_name = ?
                AND recorded_at >= datetime('now', ? || ' hours')
                ORDER BY recorded_at DESC
                """,
                (service_id, metric_name, f'-{hours}')
            )
        else:
            return self.execute_query(
                """
                SELECT * FROM metrics
                WHERE service_id = ?
                AND recorded_at >= datetime('now', ? || ' hours')
                ORDER BY recorded_at DESC
                """,
                (service_id, f'-{hours}')
            )
    
    def calculate_uptime(self, service_id: int, hours: int = 24) -> float:
        """Calculate uptime percentage for a service"""
        results = self.execute_query(
            """
            SELECT 
                COUNT(CASE WHEN status = 'UP' THEN 1 END) * 100.0 / COUNT(*) as uptime
            FROM health_checks
            WHERE service_id = ?
            AND checked_at >= datetime('now', ? || ' hours')
            """,
            (service_id, f'-{hours}')
        )
        return results[0]['uptime'] if results and results[0]['uptime'] else 0.0
    
    def calculate_avg_response_time(self, service_id: int, hours: int = 1) -> float:
        """Calculate average response time for a service"""
        results = self.execute_query(
            """
            SELECT AVG(response_time_ms) as avg_response_time
            FROM health_checks
            WHERE service_id = ?
            AND response_time_ms IS NOT NULL
            AND checked_at >= datetime('now', ? || ' hours')
            """,
            (service_id, f'-{hours}')
        )
        return results[0]['avg_response_time'] if results and results[0]['avg_response_time'] else 0.0
    
    # Alert methods
    def insert_alert(self, service_id: int, alert_type: str, 
                    message: str, severity: str) -> int:
        """Insert an alert"""
        return self.execute_insert(
            """
            INSERT INTO alerts 
            (service_id, alert_type, message, severity)
            VALUES (?, ?, ?, ?)
            """,
            (service_id, alert_type, message, severity)
        )
    
    def resolve_alert(self, alert_id: int, resolved_by: str = 'system') -> int:
        """Resolve an alert"""
        return self.execute_update(
            """
            UPDATE alerts
            SET resolved = 1, resolved_at = CURRENT_TIMESTAMP, resolved_by = ?
            WHERE id = ?
            """,
            (resolved_by, alert_id)
        )
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active (unresolved) alerts"""
        return self.execute_query(
            "SELECT * FROM active_alerts"
        )
    
    def get_service_active_alerts(self, service_id: int) -> List[Dict[str, Any]]:
        """Get active alerts for a specific service"""
        return self.execute_query(
            """
            SELECT * FROM alerts
            WHERE service_id = ? AND resolved = 0
            ORDER BY created_at DESC
            """,
            (service_id,)
        )
    
    def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alert history"""
        return self.execute_query(
            """
            SELECT a.*, s.name as service_name
            FROM alerts a
            JOIN services s ON a.service_id = s.id
            WHERE a.created_at >= datetime('now', ? || ' hours')
            ORDER BY a.created_at DESC
            """,
            (f'-{hours}',)
        )
    
    # System event methods
    def insert_system_event(self, event_type: str, event_data: Dict[str, Any] = None):
        """Insert a system event"""
        event_data_json = json.dumps(event_data) if event_data else None
        return self.execute_insert(
            "INSERT INTO system_events (event_type, event_data) VALUES (?, ?)",
            (event_type, event_data_json)
        )
    
    def get_system_events(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent system events"""
        return self.execute_query(
            """
            SELECT * FROM system_events
            WHERE created_at >= datetime('now', ? || ' hours')
            ORDER BY created_at DESC
            """,
            (f'-{hours}',)
        )
    
    # Configuration methods
    def get_config(self, key: str) -> Optional[str]:
        """Get configuration value"""
        results = self.execute_query(
            "SELECT value FROM dashboard_config WHERE key = ?",
            (key,)
        )
        return results[0]['value'] if results else None
    
    def set_config(self, key: str, value: str):
        """Set configuration value"""
        self.execute_update(
            """
            INSERT OR REPLACE INTO dashboard_config (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            """,
            (key, value)
        )
    
    # Cleanup methods
    def cleanup_old_data(self, days: int = 30):
        """Remove old health checks and metrics"""
        # Clean old health checks
        health_deleted = self.execute_update(
            """
            DELETE FROM health_checks
            WHERE checked_at < datetime('now', ? || ' days')
            """,
            (f'-{days}',)
        )
        
        # Clean old metrics
        metrics_deleted = self.execute_update(
            """
            DELETE FROM metrics
            WHERE recorded_at < datetime('now', ? || ' days')
            """,
            (f'-{days}',)
        )
        
        # Clean old resolved alerts
        alerts_deleted = self.execute_update(
            """
            DELETE FROM alerts
            WHERE resolved = 1
            AND resolved_at < datetime('now', ? || ' days')
            """,
            (f'-{days}',)
        )
        
        # Vacuum database to reclaim space
        with self.get_connection() as conn:
            conn.execute("VACUUM")
        
        return {
            'health_checks_deleted': health_deleted,
            'metrics_deleted': metrics_deleted,
            'alerts_deleted': alerts_deleted
        }


if __name__ == '__main__':
    # Test database connection
    db = Database()
    print("Database initialized successfully")
    
    # Test queries
    services = db.get_all_services()
    print(f"\nFound {len(services)} services:")
    for service in services:
        print(f"  - {service['name']} ({service['category']}) on port {service['port']}")
    
    print("\nDatabase test complete!")
