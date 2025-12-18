#!/usr/bin/env python3
"""
Micro-Automation Framework

This module provides a framework for creating, managing, and executing
micro-automations - small, focused automation scripts that handle
repetitive tasks with built-in redundancy and error handling.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
from collections import defaultdict
import traceback
import time
from enum import Enum


class AutomationStatus(Enum):
    """Status of an automation"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class AutomationType(Enum):
    """Type of automation"""
    SCRIPT = "script"
    WORKFLOW = "workflow"
    MACRO = "macro"
    SCHEDULED = "scheduled"
    TRIGGERED = "triggered"


class MicroAutomation:
    """
    Represents a single micro-automation with error handling and retry logic.
    """
    
    def __init__(
        self,
        automation_id: str,
        name: str,
        description: str,
        automation_type: AutomationType,
        execute_func: Callable,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: Optional[float] = None,
        rollback_func: Optional[Callable] = None,
        validation_func: Optional[Callable] = None
    ):
        self.automation_id = automation_id
        self.name = name
        self.description = description
        self.automation_type = automation_type
        self.execute_func = execute_func
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.rollback_func = rollback_func
        self.validation_func = validation_func
        
        self.status = AutomationStatus.PENDING
        self.retry_count = 0
        self.last_error = None
        self.execution_history = []
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the automation with error handling and retry logic.
        
        Args:
            **kwargs: Arguments to pass to the execute function
        
        Returns:
            Execution result dictionary
        """
        start_time = time.time()
        self.status = AutomationStatus.RUNNING
        
        result = {
            "automation_id": self.automation_id,
            "name": self.name,
            "status": "unknown",
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration_seconds": 0,
            "retry_count": 0,
            "error": None,
            "output": None
        }
        
        while self.retry_count <= self.max_retries:
            try:
                # Execute the automation function
                output = self.execute_func(**kwargs)
                
                # Validate output if validation function provided
                if self.validation_func:
                    validation_result = self.validation_func(output)
                    if not validation_result:
                        raise ValueError("Validation failed for automation output")
                
                # Success
                self.status = AutomationStatus.COMPLETED
                result["status"] = "success"
                result["output"] = output
                break
                
            except Exception as e:
                self.last_error = str(e)
                self.retry_count += 1
                
                if self.retry_count <= self.max_retries:
                    # Retry
                    self.status = AutomationStatus.RETRYING
                    result["status"] = "retrying"
                    time.sleep(self.retry_delay)
                else:
                    # Failed after all retries
                    self.status = AutomationStatus.FAILED
                    result["status"] = "failed"
                    result["error"] = {
                        "message": str(e),
                        "traceback": traceback.format_exc()
                    }
                    
                    # Attempt rollback if function provided
                    if self.rollback_func:
                        try:
                            self.rollback_func(**kwargs)
                            result["rollback"] = "success"
                        except Exception as rollback_error:
                            result["rollback"] = "failed"
                            result["rollback_error"] = str(rollback_error)
                    
                    break
        
        # Record execution time
        end_time = time.time()
        result["end_time"] = datetime.now().isoformat()
        result["duration_seconds"] = end_time - start_time
        result["retry_count"] = self.retry_count
        
        # Add to execution history
        self.execution_history.append(result)
        
        return result


class MicroAutomationFramework:
    """
    Framework for managing and executing micro-automations.
    """
    
    def __init__(self, db_path: str = "data/vy_nexus.db"):
        self.db_path = db_path
        self.automations: Dict[str, MicroAutomation] = {}
        self._init_database()
    
    def _init_database(self):
        """Initialize automation tracking tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Automation definitions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS automation_definitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                automation_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                automation_type TEXT NOT NULL,
                max_retries INTEGER DEFAULT 3,
                retry_delay REAL DEFAULT 1.0,
                timeout REAL,
                enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Automation executions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS automation_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                automation_id TEXT NOT NULL,
                status TEXT NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                duration_seconds REAL,
                retry_count INTEGER DEFAULT 0,
                error_message TEXT,
                output TEXT,
                metadata TEXT
            )
        """)
        
        # Automation schedules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS automation_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                automation_id TEXT NOT NULL,
                schedule_type TEXT NOT NULL,
                schedule_config TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                last_run TIMESTAMP,
                next_run TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Automation dependencies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS automation_dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                automation_id TEXT NOT NULL,
                depends_on_automation_id TEXT NOT NULL,
                dependency_type TEXT DEFAULT 'sequential',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (automation_id) REFERENCES automation_definitions(automation_id),
                FOREIGN KEY (depends_on_automation_id) REFERENCES automation_definitions(automation_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def register_automation(
        self,
        automation_id: str,
        name: str,
        description: str,
        automation_type: AutomationType,
        execute_func: Callable,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: Optional[float] = None,
        rollback_func: Optional[Callable] = None,
        validation_func: Optional[Callable] = None,
        metadata: Optional[Dict] = None
    ) -> MicroAutomation:
        """
        Register a new micro-automation.
        
        Args:
            automation_id: Unique identifier for the automation
            name: Human-readable name
            description: Description of what the automation does
            automation_type: Type of automation
            execute_func: Function to execute
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            timeout: Execution timeout in seconds
            rollback_func: Function to call on failure for cleanup
            validation_func: Function to validate execution output
            metadata: Additional metadata
        
        Returns:
            MicroAutomation instance
        """
        # Create automation instance
        automation = MicroAutomation(
            automation_id=automation_id,
            name=name,
            description=description,
            automation_type=automation_type,
            execute_func=execute_func,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout,
            rollback_func=rollback_func,
            validation_func=validation_func
        )
        
        # Store in memory
        self.automations[automation_id] = automation
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        try:
            cursor.execute("""
                INSERT INTO automation_definitions
                (automation_id, name, description, automation_type, max_retries, retry_delay, timeout, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (automation_id, name, description, automation_type.value, max_retries, retry_delay, timeout, metadata_json))
        except sqlite3.IntegrityError:
            # Update existing
            cursor.execute("""
                UPDATE automation_definitions
                SET name = ?, description = ?, automation_type = ?, max_retries = ?, 
                    retry_delay = ?, timeout = ?, metadata = ?
                WHERE automation_id = ?
            """, (name, description, automation_type.value, max_retries, retry_delay, timeout, metadata_json, automation_id))
        
        conn.commit()
        conn.close()
        
        return automation
    
    def execute_automation(self, automation_id: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a registered automation.
        
        Args:
            automation_id: ID of the automation to execute
            **kwargs: Arguments to pass to the automation
        
        Returns:
            Execution result
        """
        if automation_id not in self.automations:
            return {
                "status": "error",
                "error": f"Automation {automation_id} not found"
            }
        
        automation = self.automations[automation_id]
        result = automation.execute(**kwargs)
        
        # Record execution in database
        self._record_execution(result)
        
        return result
    
    def _record_execution(self, result: Dict[str, Any]):
        """Record automation execution in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        error_message = None
        if result.get("error"):
            error_message = json.dumps(result["error"])
        
        output = None
        if result.get("output"):
            output = json.dumps(result["output"]) if isinstance(result["output"], (dict, list)) else str(result["output"])
        
        cursor.execute("""
            INSERT INTO automation_executions
            (automation_id, status, start_time, end_time, duration_seconds, retry_count, error_message, output)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result["automation_id"],
            result["status"],
            result["start_time"],
            result["end_time"],
            result["duration_seconds"],
            result["retry_count"],
            error_message,
            output
        ))
        
        conn.commit()
        conn.close()
    
    def execute_workflow(self, automation_ids: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Execute multiple automations in sequence (workflow).
        
        Args:
            automation_ids: List of automation IDs to execute in order
            **kwargs: Arguments to pass to all automations
        
        Returns:
            List of execution results
        """
        results = []
        
        for automation_id in automation_ids:
            result = self.execute_automation(automation_id, **kwargs)
            results.append(result)
            
            # Stop workflow if automation failed
            if result["status"] == "failed":
                break
        
        return results
    
    def add_dependency(
        self,
        automation_id: str,
        depends_on: str,
        dependency_type: str = "sequential"
    ):
        """
        Add a dependency between automations.
        
        Args:
            automation_id: ID of the automation
            depends_on: ID of the automation it depends on
            dependency_type: Type of dependency (sequential, parallel, conditional)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO automation_dependencies
            (automation_id, depends_on_automation_id, dependency_type)
            VALUES (?, ?, ?)
        """, (automation_id, depends_on, dependency_type))
        
        conn.commit()
        conn.close()
    
    def get_execution_history(
        self,
        automation_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get execution history for automations.
        
        Args:
            automation_id: Optional filter by automation ID
            limit: Maximum number of records to return
        
        Returns:
            List of execution records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if automation_id:
            cursor.execute("""
                SELECT automation_id, status, start_time, end_time, duration_seconds, 
                       retry_count, error_message, output
                FROM automation_executions
                WHERE automation_id = ?
                ORDER BY start_time DESC
                LIMIT ?
            """, (automation_id, limit))
        else:
            cursor.execute("""
                SELECT automation_id, status, start_time, end_time, duration_seconds,
                       retry_count, error_message, output
                FROM automation_executions
                ORDER BY start_time DESC
                LIMIT ?
            """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        history = []
        for row in results:
            history.append({
                "automation_id": row[0],
                "status": row[1],
                "start_time": row[2],
                "end_time": row[3],
                "duration_seconds": row[4],
                "retry_count": row[5],
                "error_message": json.loads(row[6]) if row[6] else None,
                "output": json.loads(row[7]) if row[7] else None
            })
        
        return history
    
    def get_automation_stats(self, automation_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get statistics for an automation.
        
        Args:
            automation_id: ID of the automation
            days: Number of days to analyze
        
        Returns:
            Statistics dictionary
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT status, COUNT(*) as count, AVG(duration_seconds) as avg_duration,
                   SUM(retry_count) as total_retries
            FROM automation_executions
            WHERE automation_id = ? AND start_time > ?
            GROUP BY status
        """, (automation_id, cutoff_date))
        
        results = cursor.fetchall()
        conn.close()
        
        stats = {
            "automation_id": automation_id,
            "period_days": days,
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "avg_duration_seconds": 0,
            "total_retries": 0,
            "success_rate": 0.0,
            "by_status": {}
        }
        
        for status, count, avg_duration, total_retries in results:
            stats["total_executions"] += count
            stats["by_status"][status] = {
                "count": count,
                "avg_duration": avg_duration,
                "total_retries": total_retries or 0
            }
            
            if status == "success":
                stats["successful_executions"] = count
                stats["avg_duration_seconds"] = avg_duration or 0
            elif status == "failed":
                stats["failed_executions"] = count
            
            stats["total_retries"] += (total_retries or 0)
        
        if stats["total_executions"] > 0:
            stats["success_rate"] = stats["successful_executions"] / stats["total_executions"]
        
        return stats
    
    def disable_automation(self, automation_id: str):
        """Disable an automation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE automation_definitions
            SET enabled = 0
            WHERE automation_id = ?
        """, (automation_id,))
        
        conn.commit()
        conn.close()
    
    def enable_automation(self, automation_id: str):
        """Enable an automation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE automation_definitions
            SET enabled = 1
            WHERE automation_id = ?
        """, (automation_id,))
        
        conn.commit()
        conn.close()
    
    def get_all_automations(self) -> List[Dict[str, Any]]:
        """Get all registered automations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT automation_id, name, description, automation_type, enabled, created_at
            FROM automation_definitions
            ORDER BY created_at DESC
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        automations = []
        for row in results:
            automations.append({
                "automation_id": row[0],
                "name": row[1],
                "description": row[2],
                "automation_type": row[3],
                "enabled": bool(row[4]),
                "created_at": row[5]
            })
        
        return automations


# Example automation functions with error handling
def example_file_backup(source_path: str, dest_path: str) -> Dict[str, Any]:
    """
    Example automation: Backup a file with error handling.
    """
    import shutil
    import os
    
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source file not found: {source_path}")
    
    # Create destination directory if needed
    dest_dir = os.path.dirname(dest_path)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)
    
    # Perform backup
    shutil.copy2(source_path, dest_path)
    
    return {
        "source": source_path,
        "destination": dest_path,
        "size_bytes": os.path.getsize(dest_path)
    }


def example_file_backup_rollback(source_path: str, dest_path: str):
    """Rollback function for file backup"""
    import os
    
    if os.path.exists(dest_path):
        os.remove(dest_path)


def example_file_backup_validation(output: Dict[str, Any]) -> bool:
    """Validation function for file backup"""
    import os
    
    return os.path.exists(output["destination"]) and output["size_bytes"] > 0


if __name__ == "__main__":
    # Example usage
    framework = MicroAutomationFramework()
    
    # Register a file backup automation
    automation = framework.register_automation(
        automation_id="file_backup_001",
        name="Daily File Backup",
        description="Backs up important files with retry logic",
        automation_type=AutomationType.SCHEDULED,
        execute_func=example_file_backup,
        max_retries=3,
        retry_delay=2.0,
        rollback_func=example_file_backup_rollback,
        validation_func=example_file_backup_validation
    )
    
    print(f"Registered automation: {automation.name}")
    print(f"All automations: {framework.get_all_automations()}")
