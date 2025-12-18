#!/usr/bin/env python3
"""
Activity Monitoring System for Vy-Nexus
Tracks all system activities, file changes, and operations
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading
import time

class ActivityMonitor:
    """
    Monitors and logs all activities in the vy-nexus ecosystem.
    Tracks file changes, system operations, and user interactions.
    """
    
    def __init__(self, base_path: str = None, log_path: str = None):
        """
        Initialize the activity monitor.
        
        Args:
            base_path: Root path to monitor (defaults to vy-nexus)
            log_path: Path to store activity logs (defaults to Lords Love)
        """
        self.base_path = Path(base_path) if base_path else Path.home() / "vy-nexus"
        self.log_path = Path(log_path) if log_path else Path.home() / "Lords Love"
        self.activity_log_file = self.log_path / "ACTIVITY_LOG.json"
        self.daily_summary_file = self.log_path / f"DAILY_SUMMARY_{datetime.now().strftime('%Y%m%d')}.md"
        
        # Activity tracking
        self.activities: List[Dict[str, Any]] = []
        self.file_snapshots: Dict[str, str] = {}  # path -> hash
        self.monitoring = False
        self.monitor_thread = None
        
        # Statistics
        self.stats = {
            'files_created': 0,
            'files_modified': 0,
            'files_deleted': 0,
            'operations_logged': 0,
            'errors_detected': 0,
            'start_time': None,
            'last_activity': None
        }
        
        # Load existing activities if available
        self._load_activities()
    
    def _load_activities(self):
        """Load existing activity log."""
        if self.activity_log_file.exists():
            try:
                with open(self.activity_log_file, 'r') as f:
                    data = json.load(f)
                    self.activities = data.get('activities', [])
                    self.stats = data.get('stats', self.stats)
            except Exception as e:
                print(f"Warning: Could not load activity log: {e}")
    
    def _save_activities(self):
        """Save activity log to disk."""
        try:
            data = {
                'activities': self.activities[-1000:],  # Keep last 1000 activities
                'stats': self.stats,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.activity_log_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving activity log: {e}")
    
    def log_activity(self, activity_type: str, description: str, 
                    details: Optional[Dict[str, Any]] = None,
                    severity: str = 'info'):
        """
        Log an activity.
        
        Args:
            activity_type: Type of activity (file_change, operation, error, etc.)
            description: Human-readable description
            details: Additional details as dictionary
            severity: info, warning, error, critical
        """
        activity = {
            'timestamp': datetime.now().isoformat(),
            'type': activity_type,
            'description': description,
            'severity': severity,
            'details': details or {}
        }
        
        self.activities.append(activity)
        self.stats['operations_logged'] += 1
        self.stats['last_activity'] = activity['timestamp']
        
        if severity in ['error', 'critical']:
            self.stats['errors_detected'] += 1
        
        # Save periodically
        if len(self.activities) % 10 == 0:
            self._save_activities()
        
        return activity
    
    def log_file_change(self, filepath: str, change_type: str, 
                       old_hash: Optional[str] = None, 
                       new_hash: Optional[str] = None):
        """
        Log a file change.
        
        Args:
            filepath: Path to the file
            change_type: created, modified, deleted
            old_hash: Previous file hash (for modifications)
            new_hash: New file hash
        """
        details = {
            'filepath': filepath,
            'change_type': change_type,
            'old_hash': old_hash,
            'new_hash': new_hash
        }
        
        # Update stats
        if change_type == 'created':
            self.stats['files_created'] += 1
        elif change_type == 'modified':
            self.stats['files_modified'] += 1
        elif change_type == 'deleted':
            self.stats['files_deleted'] += 1
        
        return self.log_activity(
            'file_change',
            f"File {change_type}: {filepath}",
            details
        )
    
    def log_operation(self, operation: str, status: str, 
                     details: Optional[Dict[str, Any]] = None):
        """
        Log a system operation.
        
        Args:
            operation: Name of the operation
            status: success, failed, in_progress
            details: Additional operation details
        """
        severity = 'info' if status == 'success' else 'warning' if status == 'in_progress' else 'error'
        
        return self.log_activity(
            'operation',
            f"Operation '{operation}': {status}",
            details or {},
            severity
        )
    
    def log_error(self, error_type: str, error_message: str, 
                 details: Optional[Dict[str, Any]] = None):
        """
        Log an error.
        
        Args:
            error_type: Type of error
            error_message: Error message
            details: Additional error details
        """
        return self.log_activity(
            'error',
            f"{error_type}: {error_message}",
            details or {},
            'error'
        )
    
    def get_recent_activities(self, count: int = 50, 
                            activity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get recent activities.
        
        Args:
            count: Number of activities to return
            activity_type: Filter by activity type (optional)
        """
        activities = self.activities
        
        if activity_type:
            activities = [a for a in activities if a['type'] == activity_type]
        
        return activities[-count:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get activity statistics."""
        stats = self.stats.copy()
        stats['total_activities'] = len(self.activities)
        
        if stats['start_time']:
            start = datetime.fromisoformat(stats['start_time'])
            duration = datetime.now() - start
            stats['uptime_hours'] = duration.total_seconds() / 3600
        
        return stats
    
    def generate_daily_summary(self) -> str:
        """
        Generate a daily summary report.
        
        Returns:
            Markdown formatted summary
        """
        today = datetime.now().strftime('%Y-%m-%d')
        today_activities = [
            a for a in self.activities 
            if a['timestamp'].startswith(today)
        ]
        
        summary = []
        summary.append(f"# Daily Activity Summary - {today}")
        summary.append("")
        summary.append("## Statistics")
        summary.append(f"- Total Activities: {len(today_activities)}")
        summary.append(f"- Files Created: {self.stats['files_created']}")
        summary.append(f"- Files Modified: {self.stats['files_modified']}")
        summary.append(f"- Files Deleted: {self.stats['files_deleted']}")
        summary.append(f"- Errors Detected: {self.stats['errors_detected']}")
        summary.append("")
        
        # Group by activity type
        by_type = {}
        for activity in today_activities:
            atype = activity['type']
            by_type[atype] = by_type.get(atype, 0) + 1
        
        summary.append("## Activities by Type")
        for atype, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            summary.append(f"- {atype}: {count}")
        summary.append("")
        
        # Recent errors
        errors = [a for a in today_activities if a['severity'] in ['error', 'critical']]
        if errors:
            summary.append("## Errors")
            for error in errors[-10:]:  # Last 10 errors
                summary.append(f"- [{error['timestamp']}] {error['description']}")
            summary.append("")
        
        # Recent operations
        operations = [a for a in today_activities if a['type'] == 'operation'][-20:]
        if operations:
            summary.append("## Recent Operations")
            for op in operations:
                summary.append(f"- [{op['timestamp']}] {op['description']}")
            summary.append("")
        
        return "\n".join(summary)
    
    def save_daily_summary(self):
        """Save daily summary to file."""
        summary = self.generate_daily_summary()
        with open(self.daily_summary_file, 'w') as f:
            f.write(summary)
        return self.daily_summary_file
    
    def start_monitoring(self):
        """Start continuous monitoring (background thread)."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.stats['start_time'] = datetime.now().isoformat()
        
        self.log_operation('monitoring', 'in_progress', {
            'message': 'Activity monitoring started'
        })
        
        # Note: Full file system monitoring would require watchdog library
        # For now, we provide the logging infrastructure
        print("Activity monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        if not self.monitoring:
            return
        
        self.monitoring = False
        self._save_activities()
        self.save_daily_summary()
        
        self.log_operation('monitoring', 'success', {
            'message': 'Activity monitoring stopped'
        })
        
        print("Activity monitoring stopped")
    
    def __enter__(self):
        """Context manager entry."""
        self.start_monitoring()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_monitoring()


def main():
    """Test the activity monitor."""
    monitor = ActivityMonitor()
    
    # Test logging
    monitor.start_monitoring()
    
    monitor.log_operation('test_operation', 'success', {
        'test': True,
        'message': 'Testing activity monitor'
    })
    
    monitor.log_file_change(
        'test_file.py',
        'created',
        new_hash='abc123'
    )
    
    # Generate summary
    summary = monitor.generate_daily_summary()
    print(summary)
    
    # Get statistics
    stats = monitor.get_statistics()
    print("\nStatistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    monitor.stop_monitoring()

if __name__ == "__main__":
    main()
