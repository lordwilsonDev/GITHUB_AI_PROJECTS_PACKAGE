#!/usr/bin/env python3
"""
Progress Logger for Self-Evolving AI Ecosystem

Author: Vy AI
Created: December 15, 2025
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


class ProgressLogger:
    """Comprehensive progress logging system."""
    
    def __init__(self, base_path: str = "/Users/lordwilson/vy-nexus/self-evolving-ecosystem"):
        self.base_path = Path(base_path)
        self.logs_path = self.base_path / "logs"
        self.progress_log_path = self.logs_path / "progress_log.jsonl"
        self.activity_log_path = self.logs_path / "activity_log.jsonl"
        self.error_log_path = self.logs_path / "error_log.jsonl"
        self.logs_path.mkdir(parents=True, exist_ok=True)
    
    def log_progress(self, event: str, phase: str, task: str, status: str, details: str = ""):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "phase": phase,
            "task": task,
            "status": status,
            "details": details
        }
        self._append_jsonl(self.progress_log_path, entry)
    
    def log_activity(self, module: str, action: str, result: str, metadata: Optional[Dict[str, Any]] = None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "module": module,
            "action": action,
            "result": result,
            "metadata": metadata or {}
        }
        self._append_jsonl(self.activity_log_path, entry)
    
    def log_error(self, module: str, error_type: str, error_message: str, traceback: str = ""):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "module": module,
            "error_type": error_type,
            "error_message": error_message,
            "traceback": traceback
        }
        self._append_jsonl(self.error_log_path, entry)
    
    def _append_jsonl(self, file_path: Path, entry: Dict[str, Any]):
        with open(file_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')


def get_logger():
    global _logger_instance
    if '_logger_instance' not in globals():
        _logger_instance = ProgressLogger()
    return _logger_instance
