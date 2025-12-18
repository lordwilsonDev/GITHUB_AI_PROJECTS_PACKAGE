#!/usr/bin/env python3
"""
User Interaction Monitor

Purpose: Track and learn from all user interactions with the vy-nexus system.
This module collects interaction data while respecting privacy and security.

Features:
- Command pattern tracking
- Task success/failure monitoring
- Timing pattern analysis
- Error pattern detection
- Privacy-preserving data collection

Integration Points:
- CLI Interface hooks
- API Gateway hooks
- Living Memory storage
- Journalist Service logging

Author: VY-NEXUS Self-Evolving AI Ecosystem
Date: December 15, 2025
Version: 1.0.0
"""

from __future__ import annotations

import json
import hashlib
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
from collections import defaultdict, deque

# -------------------------
# Configuration
# -------------------------
HOME = Path.home()
DATA_DIR = HOME / "vy_data" / "interactions"
LOG_DIR = HOME / "vy_logs"
RESEARCH_LOGS = HOME / "research_logs"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Data retention (days)
RETENTION_DAYS = 90

# Privacy settings
ANONYMIZE_DATA = True
COLLECT_PII = False

# Performance settings
BATCH_SIZE = 100
FLUSH_INTERVAL_SECONDS = 60

# -------------------------
# Data Models
# -------------------------

class InteractionType(Enum):
    """Types of user interactions"""
    CLI_COMMAND = "cli_command"
    API_REQUEST = "api_request"
    TASK_SUBMISSION = "task_submission"
    EXPERT_QUERY = "expert_query"
    CONFIGURATION = "configuration"
    SYSTEM_QUERY = "system_query"

class InteractionStatus(Enum):
    """Status of interaction"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    ERROR = "error"

@dataclass
class Interaction:
    """Single user interaction record"""
    timestamp: str
    interaction_type: str
    command: str  # Anonymized if needed
    status: str
    duration_ms: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    user_hash: Optional[str] = None  # Anonymized user identifier
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Interaction':
        """Create from dictionary"""
        return cls(**data)

@dataclass
class InteractionPattern:
    """Detected pattern in user interactions"""
    pattern_id: str
    pattern_type: str
    frequency: int
    first_seen: str
    last_seen: str
    confidence: float
    description: str
    examples: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

@dataclass
class UserProfile:
    """Aggregated user behavior profile"""
    user_hash: str
    total_interactions: int
    success_rate: float
    avg_session_duration_minutes: float
    peak_usage_hours: List[int]
    common_commands: List[str]
    common_errors: List[str]
    preferred_experts: List[str]
    last_updated: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

# -------------------------
# User Interaction Monitor
# -------------------------

class UserInteractionMonitor:
    """Monitor and track user interactions"""
    
    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory buffers
        self.interaction_buffer: deque = deque(maxlen=1000)
        self.pattern_cache: Dict[str, InteractionPattern] = {}
        self.user_profiles: Dict[str, UserProfile] = {}
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Background flush thread
        self.flush_thread = None
        self.running = False
        
        # Statistics
        self.stats = {
            "total_interactions": 0,
            "successful_interactions": 0,
            "failed_interactions": 0,
            "patterns_detected": 0,
            "last_flush": None
        }
        
        # Load existing data
        self._load_user_profiles()
        self._load_patterns()
        
    def start(self):
        """Start background monitoring"""
        if self.running:
            return
        
        self.running = True
        self.flush_thread = threading.Thread(target=self._background_flush, daemon=True)
        self.flush_thread.start()
        
        self._log("User Interaction Monitor started")
    
    def stop(self):
        """Stop monitoring and flush data"""
        self.running = False
        if self.flush_thread:
            self.flush_thread.join(timeout=5)
        
        self._flush_to_disk()
        self._log("User Interaction Monitor stopped")
    
    def record_interaction(
        self,
        interaction_type: InteractionType,
        command: str,
        status: InteractionStatus,
        duration_ms: float,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> str:
        """Record a user interaction"""
        
        # Anonymize user ID if needed
        user_hash = self._anonymize_user_id(user_id) if user_id else None
        
        # Anonymize command if needed
        anonymized_command = self._anonymize_command(command) if ANONYMIZE_DATA else command
        
        # Create interaction record
        interaction = Interaction(
            timestamp=datetime.utcnow().isoformat(),
            interaction_type=interaction_type.value,
            command=anonymized_command,
            status=status.value,
            duration_ms=duration_ms,
            error_message=error_message,
            metadata=metadata or {},
            session_id=self._get_session_id(),
            user_hash=user_hash
        )
        
        # Add to buffer
        with self.lock:
            self.interaction_buffer.append(interaction)
            
            # Update statistics
            self.stats["total_interactions"] += 1
            if status == InteractionStatus.SUCCESS:
                self.stats["successful_interactions"] += 1
            else:
                self.stats["failed_interactions"] += 1
        
        # Flush if buffer is full
        if len(self.interaction_buffer) >= BATCH_SIZE:
            self._flush_to_disk()
        
        return interaction.timestamp
    
    def get_patterns(self, min_frequency: int = 3) -> List[InteractionPattern]:
        """Get detected patterns"""
        with self.lock:
            return [
                pattern for pattern in self.pattern_cache.values()
                if pattern.frequency >= min_frequency
            ]
    
    def get_user_profile(self, user_id: Optional[str] = None) -> Optional[UserProfile]:
        """Get user behavior profile"""
        if not user_id:
            return None
        
        user_hash = self._anonymize_user_id(user_id)
        with self.lock:
            return self.user_profiles.get(user_hash)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        with self.lock:
            return self.stats.copy()
    
    def analyze_recent_interactions(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze recent interactions"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Load recent interactions from disk
        recent_interactions = self._load_recent_interactions(cutoff_time)
        
        # Add buffered interactions
        with self.lock:
            recent_interactions.extend(list(self.interaction_buffer))
        
        # Analyze
        analysis = {
            "total_count": len(recent_interactions),
            "success_rate": 0.0,
            "avg_duration_ms": 0.0,
            "command_frequency": defaultdict(int),
            "error_frequency": defaultdict(int),
            "hourly_distribution": defaultdict(int),
            "interaction_types": defaultdict(int)
        }
        
        if not recent_interactions:
            return analysis
        
        successful = 0
        total_duration = 0.0
        
        for interaction in recent_interactions:
            # Success rate
            if interaction.status == InteractionStatus.SUCCESS.value:
                successful += 1
            
            # Duration
            total_duration += interaction.duration_ms
            
            # Command frequency
            analysis["command_frequency"][interaction.command] += 1
            
            # Error frequency
            if interaction.error_message:
                analysis["error_frequency"][interaction.error_message] += 1
            
            # Hourly distribution
            hour = datetime.fromisoformat(interaction.timestamp).hour
            analysis["hourly_distribution"][hour] += 1
            
            # Interaction types
            analysis["interaction_types"][interaction.interaction_type] += 1
        
        analysis["success_rate"] = successful / len(recent_interactions)
        analysis["avg_duration_ms"] = total_duration / len(recent_interactions)
        
        # Convert defaultdicts to regular dicts
        analysis["command_frequency"] = dict(analysis["command_frequency"])
        analysis["error_frequency"] = dict(analysis["error_frequency"])
        analysis["hourly_distribution"] = dict(analysis["hourly_distribution"])
        analysis["interaction_types"] = dict(analysis["interaction_types"])
        
        return analysis
    
    # -------------------------
    # Private Methods
    # -------------------------
    
    def _background_flush(self):
        """Background thread to flush data periodically"""
        while self.running:
            time.sleep(FLUSH_INTERVAL_SECONDS)
            self._flush_to_disk()
    
    def _flush_to_disk(self):
        """Flush buffered interactions to disk"""
        with self.lock:
            if not self.interaction_buffer:
                return
            
            # Get current date for filename
            today = datetime.utcnow().date().isoformat()
            filepath = self.data_dir / f"interactions_{today}.jsonl"
            
            # Write to file
            try:
                with open(filepath, 'a') as f:
                    for interaction in self.interaction_buffer:
                        f.write(json.dumps(interaction.to_dict()) + '\n')
                
                # Clear buffer
                count = len(self.interaction_buffer)
                self.interaction_buffer.clear()
                
                # Update stats
                self.stats["last_flush"] = datetime.utcnow().isoformat()
                
                self._log(f"Flushed {count} interactions to {filepath}")
                
            except Exception as e:
                self._log(f"Error flushing interactions: {e}", level="ERROR")
    
    def _load_recent_interactions(self, cutoff_time: datetime) -> List[Interaction]:
        """Load recent interactions from disk"""
        interactions = []
        
        # Get files from last N days
        days_to_check = 7
        for i in range(days_to_check):
            date = (datetime.utcnow().date() - timedelta(days=i)).isoformat()
            filepath = self.data_dir / f"interactions_{date}.jsonl"
            
            if not filepath.exists():
                continue
            
            try:
                with open(filepath, 'r') as f:
                    for line in f:
                        data = json.loads(line.strip())
                        interaction = Interaction.from_dict(data)
                        
                        # Check if within time range
                        timestamp = datetime.fromisoformat(interaction.timestamp)
                        if timestamp >= cutoff_time:
                            interactions.append(interaction)
            
            except Exception as e:
                self._log(f"Error loading interactions from {filepath}: {e}", level="ERROR")
        
        return interactions
    
    def _load_user_profiles(self):
        """Load user profiles from disk"""
        filepath = self.data_dir / "user_profiles.json"
        
        if not filepath.exists():
            return
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                for user_hash, profile_data in data.items():
                    self.user_profiles[user_hash] = UserProfile(**profile_data)
            
            self._log(f"Loaded {len(self.user_profiles)} user profiles")
        
        except Exception as e:
            self._log(f"Error loading user profiles: {e}", level="ERROR")
    
    def _load_patterns(self):
        """Load detected patterns from disk"""
        filepath = self.data_dir / "patterns.json"
        
        if not filepath.exists():
            return
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                for pattern_id, pattern_data in data.items():
                    self.pattern_cache[pattern_id] = InteractionPattern(**pattern_data)
            
            self.stats["patterns_detected"] = len(self.pattern_cache)
            self._log(f"Loaded {len(self.pattern_cache)} patterns")
        
        except Exception as e:
            self._log(f"Error loading patterns: {e}", level="ERROR")
    
    def _anonymize_user_id(self, user_id: str) -> str:
        """Anonymize user ID using hash"""
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
    
    def _anonymize_command(self, command: str) -> str:
        """Anonymize command by removing potential PII"""
        # For now, just return the command type/category
        # In production, implement more sophisticated anonymization
        parts = command.split()
        if parts:
            return parts[0]  # Return just the command name
        return "unknown"
    
    def _get_session_id(self) -> str:
        """Get or create session ID"""
        # Simple session ID based on time
        # In production, use more sophisticated session tracking
        return datetime.utcnow().strftime("%Y%m%d%H")
    
    def _log(self, message: str, level: str = "INFO"):
        """Log message to system journal"""
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"[{timestamp}] [{level}] [UserInteractionMonitor] {message}\n"
        
        # Log to file
        log_file = LOG_DIR / "interaction_monitor.log"
        try:
            with open(log_file, 'a') as f:
                f.write(log_entry)
        except Exception:
            pass  # Fail silently for logging errors
        
        # Also log to system journal if it exists
        journal_file = RESEARCH_LOGS / "system_journal.md"
        if journal_file.exists():
            try:
                with open(journal_file, 'a') as f:
                    f.write(f"\n## {timestamp}\n{message}\n")
            except Exception:
                pass

# -------------------------
# Singleton Instance
# -------------------------

_monitor_instance: Optional[UserInteractionMonitor] = None

def get_monitor() -> UserInteractionMonitor:
    """Get singleton monitor instance"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = UserInteractionMonitor()
        _monitor_instance.start()
    return _monitor_instance

def stop_monitor():
    """Stop singleton monitor instance"""
    global _monitor_instance
    if _monitor_instance is not None:
        _monitor_instance.stop()
        _monitor_instance = None

# -------------------------
# CLI for Testing
# -------------------------

if __name__ == "__main__":
    import sys
    
    monitor = get_monitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("Testing User Interaction Monitor...")
        
        # Record some test interactions
        for i in range(5):
            monitor.record_interaction(
                interaction_type=InteractionType.CLI_COMMAND,
                command=f"test_command_{i}",
                status=InteractionStatus.SUCCESS if i % 2 == 0 else InteractionStatus.FAILURE,
                duration_ms=100.0 + i * 10,
                user_id="test_user"
            )
        
        # Get statistics
        stats = monitor.get_statistics()
        print(f"\nStatistics: {json.dumps(stats, indent=2)}")
        
        # Analyze recent interactions
        analysis = monitor.analyze_recent_interactions(hours=24)
        print(f"\nRecent Analysis: {json.dumps(analysis, indent=2)}")
        
        # Stop monitor
        stop_monitor()
        print("\nTest complete!")
    
    elif len(sys.argv) > 1 and sys.argv[1] == "stats":
        stats = monitor.get_statistics()
        print(json.dumps(stats, indent=2))
    
    elif len(sys.argv) > 1 and sys.argv[1] == "analyze":
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        analysis = monitor.analyze_recent_interactions(hours=hours)
        print(json.dumps(analysis, indent=2))
    
    else:
        print("User Interaction Monitor")
        print("Usage:")
        print("  python user_interaction_monitor.py test     - Run test")
        print("  python user_interaction_monitor.py stats    - Show statistics")
        print("  python user_interaction_monitor.py analyze [hours] - Analyze recent interactions")
