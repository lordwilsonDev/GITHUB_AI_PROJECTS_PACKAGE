#!/usr/bin/env python3
"""
Evolution Logger - Comprehensive logging and tracking system
Tracks all system evolution activities, learning, and optimizations
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
from enum import Enum

class LogLevel(Enum):
    """Log levels for evolution tracking"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EVOLUTION = "evolution"  # Special level for evolution events
    LEARNING = "learning"    # Special level for learning events
    OPTIMIZATION = "optimization"  # Special level for optimization events

class EvolutionLogger:
    """Comprehensive logging system for self-evolving AI ecosystem"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.path.expanduser("~/vy-nexus/logs")
        self.evolution_log = os.path.join(self.base_dir, "evolution.jsonl")
        self.learning_log = os.path.join(self.base_dir, "learning.jsonl")
        self.optimization_log = os.path.join(self.base_dir, "optimization.jsonl")
        self.system_log = os.path.join(self.base_dir, "system.jsonl")
        self.daily_log_dir = os.path.join(self.base_dir, "daily")
        
        # Create directories
        Path(self.base_dir).mkdir(parents=True, exist_ok=True)
        Path(self.daily_log_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize Python logging
        self._setup_python_logging()
        
        # Session tracking
        self.session_id = self._generate_session_id()
        self.session_start = datetime.now()
        
        # Log session start
        self.log_system_event("session_start", {
            "session_id": self.session_id,
            "start_time": self.session_start.isoformat()
        })
    
    def _setup_python_logging(self):
        """Setup Python logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.base_dir, "python.log")),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("vy-nexus")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def log_evolution_event(self, event_type: str, data: Dict[str, Any], 
                           metadata: Dict[str, Any] = None):
        """
        Log an evolution event
        
        Args:
            event_type: Type of evolution event
            data: Event data
            metadata: Additional metadata
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "level": LogLevel.EVOLUTION.value,
            "event_type": event_type,
            "data": data,
            "metadata": metadata or {}
        }
        
        self._write_log(self.evolution_log, event)
        self._write_daily_log(event)
        
        self.logger.info(f"Evolution Event: {event_type}")
    
    def log_learning_event(self, learning_type: str, data: Dict[str, Any],
                          insights: List[str] = None):
        """
        Log a learning event
        
        Args:
            learning_type: Type of learning
            data: Learning data
            insights: Insights gained
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "level": LogLevel.LEARNING.value,
            "learning_type": learning_type,
            "data": data,
            "insights": insights or []
        }
        
        self._write_log(self.learning_log, event)
        self._write_daily_log(event)
        
        self.logger.info(f"Learning Event: {learning_type}")
    
    def log_optimization_event(self, optimization_type: str, data: Dict[str, Any],
                              impact: Dict[str, Any] = None):
        """
        Log an optimization event
        
        Args:
            optimization_type: Type of optimization
            data: Optimization data
            impact: Impact metrics
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "level": LogLevel.OPTIMIZATION.value,
            "optimization_type": optimization_type,
            "data": data,
            "impact": impact or {}
        }
        
        self._write_log(self.optimization_log, event)
        self._write_daily_log(event)
        
        self.logger.info(f"Optimization Event: {optimization_type}")
    
    def log_system_event(self, event_type: str, data: Dict[str, Any],
                        level: LogLevel = LogLevel.INFO):
        """
        Log a system event
        
        Args:
            event_type: Type of system event
            data: Event data
            level: Log level
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "level": level.value,
            "event_type": event_type,
            "data": data
        }
        
        self._write_log(self.system_log, event)
        
        # Also log to Python logger
        log_method = getattr(self.logger, level.value if level.value in ['debug', 'info', 'warning', 'error', 'critical'] else 'info')
        log_method(f"System Event: {event_type}")
    
    def _write_log(self, log_file: str, event: Dict[str, Any]):
        """Write event to log file"""
        with open(log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    def _write_daily_log(self, event: Dict[str, Any]):
        """Write event to daily log file"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        daily_file = os.path.join(self.daily_log_dir, f"{date_str}.jsonl")
        
        with open(daily_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        duration = (datetime.now() - self.session_start).total_seconds()
        
        # Count events by type
        event_counts = {
            "evolution": self._count_events(self.evolution_log, self.session_id),
            "learning": self._count_events(self.learning_log, self.session_id),
            "optimization": self._count_events(self.optimization_log, self.session_id),
            "system": self._count_events(self.system_log, self.session_id)
        }
        
        return {
            "session_id": self.session_id,
            "start_time": self.session_start.isoformat(),
            "duration_seconds": duration,
            "event_counts": event_counts,
            "total_events": sum(event_counts.values())
        }
    
    def _count_events(self, log_file: str, session_id: str) -> int:
        """Count events in log file for session"""
        if not os.path.exists(log_file):
            return 0
        
        count = 0
        with open(log_file, 'r') as f:
            for line in f:
                if line.strip():
                    event = json.loads(line)
                    if event.get('session_id') == session_id:
                        count += 1
        
        return count
    
    def close_session(self):
        """Close current session and log summary"""
        summary = self.get_session_summary()
        
        self.log_system_event("session_end", summary)
        
        self.logger.info(f"Session {self.session_id} ended. Duration: {summary['duration_seconds']:.1f}s")
        
        return summary


if __name__ == "__main__":
    # Test the evolution logger
    logger = EvolutionLogger()
    
    # Log various events
    logger.log_evolution_event("module_created", {
        "module": "interaction_monitor",
        "version": "1.0.0"
    })
    
    logger.log_learning_event("pattern_identified", {
        "pattern": "repetitive_task",
        "confidence": 0.85
    }, insights=["User frequently performs data processing tasks"])
    
    logger.log_optimization_event("automation_created", {
        "automation": "data_processor",
        "task_type": "data_processing"
    }, impact={"time_saved": 120, "efficiency_gain": 0.8})
    
    # Get session summary
    summary = logger.get_session_summary()
    print("Session Summary:")
    print(json.dumps(summary, indent=2))
    
    # Close session
    logger.close_session()
