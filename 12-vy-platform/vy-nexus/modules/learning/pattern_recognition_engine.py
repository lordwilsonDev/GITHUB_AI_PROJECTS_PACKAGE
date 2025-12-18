#!/usr/bin/env python3
"""
Pattern Recognition Engine

Purpose: Identify patterns in user behavior and system performance.
Builds upon User Interaction Monitor to detect actionable patterns.

Features:
- Repetitive task detection
- Temporal pattern analysis
- Error pattern clustering
- Workflow sequence detection
- Anomaly detection
- Optimization opportunity identification

Integration Points:
- User Interaction Monitor (data source)
- NEXUS Core (pattern mining algorithms)
- Living Memory (pattern storage)
- Optimization Generator (pattern consumers)

Author: VY-NEXUS Self-Evolving AI Ecosystem
Date: December 15, 2025
Version: 1.0.0
"""

from __future__ import annotations

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict, field
from collections import defaultdict, Counter
import threading
import math

# -------------------------
# Configuration
# -------------------------
HOME = Path.home()
DATA_DIR = HOME / "vy_data" / "patterns"
LOG_DIR = HOME / "vy_logs"
RESEARCH_LOGS = HOME / "research_logs"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Pattern detection thresholds
MIN_PATTERN_FREQUENCY = 3  # Minimum occurrences to be considered a pattern
MIN_CONFIDENCE_SCORE = 0.7  # Minimum confidence (0-1)
MAX_SEQUENCE_LENGTH = 5  # Maximum command sequence length
TIME_WINDOW_HOURS = 24  # Time window for pattern detection

# Anomaly detection
ANOMALY_THRESHOLD_STDDEV = 2.0  # Standard deviations for anomaly

# -------------------------
# Data Models
# -------------------------

@dataclass
class Pattern:
    """Detected pattern"""
    pattern_id: str
    pattern_type: str  # repetitive, sequential, temporal, error, anomaly
    description: str
    frequency: int
    confidence: float
    first_seen: str
    last_seen: str
    examples: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    optimization_potential: float = 0.0  # 0-1 score
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pattern':
        return cls(**data)

@dataclass
class CommandSequence:
    """Sequence of commands"""
    commands: List[str]
    frequency: int
    avg_duration_ms: float
    success_rate: float
    
    def to_tuple(self) -> Tuple[str, ...]:
        return tuple(self.commands)
    
    def __hash__(self):
        return hash(self.to_tuple())

@dataclass
class TemporalPattern:
    """Time-based pattern"""
    hour_of_day: int
    day_of_week: int
    command: str
    frequency: int
    avg_duration_ms: float

@dataclass
class ErrorCluster:
    """Cluster of related errors"""
    error_type: str
    commands: List[str]
    frequency: int
    first_seen: str
    last_seen: str
    suggested_fix: Optional[str] = None

# -------------------------
# Pattern Recognition Engine
# -------------------------

class PatternRecognitionEngine:
    """Detect and analyze patterns in user interactions"""
    
    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Pattern storage
        self.patterns: Dict[str, Pattern] = {}
        self.command_sequences: Dict[Tuple[str, ...], CommandSequence] = {}
        self.temporal_patterns: List[TemporalPattern] = []
        self.error_clusters: Dict[str, ErrorCluster] = {}
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Statistics
        self.stats = {
            "total_patterns": 0,
            "repetitive_patterns": 0,
            "sequential_patterns": 0,
            "temporal_patterns": 0,
            "error_patterns": 0,
            "anomalies_detected": 0,
            "last_analysis": None
        }
        
        # Load existing patterns
        self._load_patterns()
    
    def analyze_interactions(self, interactions: List[Any]) -> Dict[str, Any]:
        """
        Analyze interactions and detect patterns.
        
        Args:
            interactions: List of Interaction objects from UserInteractionMonitor
        
        Returns:
            Dict with analysis results and detected patterns
        """
        if not interactions:
            return {"patterns_detected": 0, "patterns": []}
        
        with self.lock:
            # Detect different pattern types
            repetitive = self._detect_repetitive_patterns(interactions)
            sequential = self._detect_sequential_patterns(interactions)
            temporal = self._detect_temporal_patterns(interactions)
            errors = self._detect_error_patterns(interactions)
            anomalies = self._detect_anomalies(interactions)
            
            # Combine all patterns
            all_patterns = repetitive + sequential + temporal + errors + anomalies
            
            # Update pattern storage
            for pattern in all_patterns:
                self.patterns[pattern.pattern_id] = pattern
            
            # Update statistics
            self.stats["total_patterns"] = len(self.patterns)
            self.stats["repetitive_patterns"] = len(repetitive)
            self.stats["sequential_patterns"] = len(sequential)
            self.stats["temporal_patterns"] = len(temporal)
            self.stats["error_patterns"] = len(errors)
            self.stats["anomalies_detected"] = len(anomalies)
            self.stats["last_analysis"] = datetime.utcnow().isoformat()
            
            # Save patterns
            self._save_patterns()
            
            # Log analysis
            self._log(f"Pattern analysis complete: {len(all_patterns)} patterns detected")
            
            return {
                "patterns_detected": len(all_patterns),
                "patterns": [p.to_dict() for p in all_patterns],
                "statistics": self.stats.copy()
            }
    
    def get_patterns(
        self,
        pattern_type: Optional[str] = None,
        min_confidence: float = MIN_CONFIDENCE_SCORE,
        min_frequency: int = MIN_PATTERN_FREQUENCY
    ) -> List[Pattern]:
        """
        Get detected patterns with optional filtering.
        
        Args:
            pattern_type: Filter by pattern type (repetitive, sequential, etc.)
            min_confidence: Minimum confidence score
            min_frequency: Minimum frequency
        
        Returns:
            List of Pattern objects
        """
        with self.lock:
            patterns = list(self.patterns.values())
            
            # Apply filters
            if pattern_type:
                patterns = [p for p in patterns if p.pattern_type == pattern_type]
            
            patterns = [
                p for p in patterns
                if p.confidence >= min_confidence and p.frequency >= min_frequency
            ]
            
            # Sort by optimization potential
            patterns.sort(key=lambda p: p.optimization_potential, reverse=True)
            
            return patterns
    
    def get_optimization_opportunities(self, top_n: int = 10) -> List[Pattern]:
        """
        Get top optimization opportunities based on patterns.
        
        Args:
            top_n: Number of top opportunities to return
        
        Returns:
            List of Pattern objects sorted by optimization potential
        """
        patterns = self.get_patterns()
        patterns.sort(key=lambda p: p.optimization_potential, reverse=True)
        return patterns[:top_n]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get pattern recognition statistics"""
        with self.lock:
            return self.stats.copy()
    
    # -------------------------
    # Pattern Detection Methods
    # -------------------------
    
    def _detect_repetitive_patterns(self, interactions: List[Any]) -> List[Pattern]:
        """
        Detect repetitive command patterns.
        Commands that are executed frequently without variation.
        """
        patterns = []
        
        # Count command frequency
        command_counts = Counter()
        command_durations = defaultdict(list)
        command_timestamps = defaultdict(list)
        
        for interaction in interactions:
            cmd = interaction.command
            command_counts[cmd] += 1
            command_durations[cmd].append(interaction.duration_ms)
            command_timestamps[cmd].append(interaction.timestamp)
        
        # Identify repetitive patterns
        for command, count in command_counts.items():
            if count >= MIN_PATTERN_FREQUENCY:
                # Calculate confidence based on frequency and consistency
                avg_duration = sum(command_durations[command]) / len(command_durations[command])
                duration_variance = self._calculate_variance(command_durations[command])
                
                # Higher confidence if durations are consistent
                consistency = 1.0 / (1.0 + duration_variance / (avg_duration + 1))
                confidence = min(0.5 + (count / len(interactions)) + consistency * 0.3, 1.0)
                
                # Calculate optimization potential
                # High frequency + consistent duration = good automation candidate
                optimization_potential = min(
                    (count / len(interactions)) * consistency,
                    1.0
                )
                
                pattern = Pattern(
                    pattern_id=self._generate_pattern_id("repetitive", command),
                    pattern_type="repetitive",
                    description=f"Command '{command}' executed {count} times",
                    frequency=count,
                    confidence=confidence,
                    first_seen=min(command_timestamps[command]),
                    last_seen=max(command_timestamps[command]),
                    examples=[command] * min(3, count),
                    metadata={
                        "avg_duration_ms": avg_duration,
                        "duration_variance": duration_variance,
                        "consistency_score": consistency
                    },
                    optimization_potential=optimization_potential
                )
                
                patterns.append(pattern)
        
        return patterns
    
    def _detect_sequential_patterns(self, interactions: List[Any]) -> List[Pattern]:
        """
        Detect sequential command patterns.
        Sequences of commands that are frequently executed together.
        """
        patterns = []
        
        # Extract command sequences
        sequences = defaultdict(lambda: {
            "count": 0,
            "durations": [],
            "successes": 0,
            "timestamps": []
        })
        
        # Sliding window to find sequences
        for i in range(len(interactions) - 1):
            for length in range(2, min(MAX_SEQUENCE_LENGTH + 1, len(interactions) - i + 1)):
                seq = tuple(interactions[j].command for j in range(i, i + length))
                
                # Calculate total duration
                total_duration = sum(
                    interactions[j].duration_ms for j in range(i, i + length)
                )
                
                # Check if all succeeded
                all_success = all(
                    interactions[j].status == "success" for j in range(i, i + length)
                )
                
                sequences[seq]["count"] += 1
                sequences[seq]["durations"].append(total_duration)
                sequences[seq]["successes"] += 1 if all_success else 0
                sequences[seq]["timestamps"].append(interactions[i].timestamp)
        
        # Identify significant sequences
        for seq, data in sequences.items():
            if data["count"] >= MIN_PATTERN_FREQUENCY:
                avg_duration = sum(data["durations"]) / len(data["durations"])
                success_rate = data["successes"] / data["count"]
                
                # Confidence based on frequency and success rate
                confidence = min(
                    0.5 + (data["count"] / len(interactions)) + success_rate * 0.3,
                    1.0
                )
                
                # Optimization potential: frequent + successful sequences
                optimization_potential = min(
                    (data["count"] / len(interactions)) * success_rate * len(seq) / MAX_SEQUENCE_LENGTH,
                    1.0
                )
                
                pattern = Pattern(
                    pattern_id=self._generate_pattern_id("sequential", " -> ".join(seq)),
                    pattern_type="sequential",
                    description=f"Command sequence: {' -> '.join(seq)}",
                    frequency=data["count"],
                    confidence=confidence,
                    first_seen=min(data["timestamps"]),
                    last_seen=max(data["timestamps"]),
                    examples=[" -> ".join(seq)],
                    metadata={
                        "sequence_length": len(seq),
                        "avg_duration_ms": avg_duration,
                        "success_rate": success_rate
                    },
                    optimization_potential=optimization_potential
                )
                
                patterns.append(pattern)
        
        return patterns
    
    def _detect_temporal_patterns(self, interactions: List[Any]) -> List[Pattern]:
        """
        Detect temporal patterns.
        Commands that are frequently executed at specific times.
        """
        patterns = []
        
        # Group by hour of day
        hourly_commands = defaultdict(lambda: defaultdict(int))
        hourly_durations = defaultdict(lambda: defaultdict(list))
        hourly_timestamps = defaultdict(lambda: defaultdict(list))
        
        for interaction in interactions:
            timestamp = datetime.fromisoformat(interaction.timestamp)
            hour = timestamp.hour
            cmd = interaction.command
            
            hourly_commands[hour][cmd] += 1
            hourly_durations[hour][cmd].append(interaction.duration_ms)
            hourly_timestamps[hour][cmd].append(interaction.timestamp)
        
        # Identify temporal patterns
        for hour, commands in hourly_commands.items():
            for cmd, count in commands.items():
                if count >= MIN_PATTERN_FREQUENCY:
                    # Calculate what percentage of this command happens in this hour
                    total_cmd_count = sum(
                        hourly_commands[h].get(cmd, 0) for h in range(24)
                    )
                    
                    if total_cmd_count > 0:
                        concentration = count / total_cmd_count
                        
                        # Only create pattern if significantly concentrated in this hour
                        if concentration > 0.3:  # >30% of occurrences in this hour
                            avg_duration = sum(hourly_durations[hour][cmd]) / len(hourly_durations[hour][cmd])
                            
                            confidence = min(0.5 + concentration * 0.5, 1.0)
                            
                            # Optimization potential: predictable timing
                            optimization_potential = concentration * 0.8
                            
                            pattern = Pattern(
                                pattern_id=self._generate_pattern_id("temporal", f"{hour}_{cmd}"),
                                pattern_type="temporal",
                                description=f"Command '{cmd}' frequently executed at hour {hour}:00",
                                frequency=count,
                                confidence=confidence,
                                first_seen=min(hourly_timestamps[hour][cmd]),
                                last_seen=max(hourly_timestamps[hour][cmd]),
                                examples=[f"{hour}:00 - {cmd}"],
                                metadata={
                                    "hour_of_day": hour,
                                    "concentration": concentration,
                                    "avg_duration_ms": avg_duration
                                },
                                optimization_potential=optimization_potential
                            )
                            
                            patterns.append(pattern)
        
        return patterns
    
    def _detect_error_patterns(self, interactions: List[Any]) -> List[Pattern]:
        """
        Detect error patterns.
        Commands that frequently fail or produce errors.
        """
        patterns = []
        
        # Group errors by command
        error_commands = defaultdict(lambda: {
            "count": 0,
            "total": 0,
            "errors": [],
            "timestamps": []
        })
        
        for interaction in interactions:
            cmd = interaction.command
            error_commands[cmd]["total"] += 1
            
            if interaction.status in ["failure", "error", "timeout"]:
                error_commands[cmd]["count"] += 1
                if interaction.error_message:
                    error_commands[cmd]["errors"].append(interaction.error_message)
                error_commands[cmd]["timestamps"].append(interaction.timestamp)
        
        # Identify error patterns
        for cmd, data in error_commands.items():
            if data["count"] >= MIN_PATTERN_FREQUENCY and data["total"] > 0:
                error_rate = data["count"] / data["total"]
                
                # Only flag if error rate is significant
                if error_rate > 0.2:  # >20% error rate
                    # Find most common error
                    if data["errors"]:
                        error_counter = Counter(data["errors"])
                        most_common_error = error_counter.most_common(1)[0][0]
                    else:
                        most_common_error = "Unknown error"
                    
                    confidence = min(0.5 + error_rate * 0.5, 1.0)
                    
                    # High error rate = high priority for fixing
                    optimization_potential = error_rate * 0.9
                    
                    pattern = Pattern(
                        pattern_id=self._generate_pattern_id("error", cmd),
                        pattern_type="error",
                        description=f"Command '{cmd}' has {error_rate:.1%} error rate",
                        frequency=data["count"],
                        confidence=confidence,
                        first_seen=min(data["timestamps"]) if data["timestamps"] else "",
                        last_seen=max(data["timestamps"]) if data["timestamps"] else "",
                        examples=[most_common_error],
                        metadata={
                            "error_rate": error_rate,
                            "total_executions": data["total"],
                            "most_common_error": most_common_error
                        },
                        optimization_potential=optimization_potential
                    )
                    
                    patterns.append(pattern)
        
        return patterns
    
    def _detect_anomalies(self, interactions: List[Any]) -> List[Pattern]:
        """
        Detect anomalous patterns.
        Unusual behavior that deviates from normal patterns.
        """
        patterns = []
        
        if len(interactions) < 10:
            return patterns  # Need sufficient data
        
        # Analyze duration anomalies
        command_durations = defaultdict(list)
        for interaction in interactions:
            command_durations[interaction.command].append(interaction.duration_ms)
        
        for cmd, durations in command_durations.items():
            if len(durations) >= 5:
                mean = sum(durations) / len(durations)
                variance = self._calculate_variance(durations)
                stddev = math.sqrt(variance) if variance > 0 else 0
                
                if stddev > 0:
                    # Find outliers
                    anomalies = [
                        d for d in durations
                        if abs(d - mean) > ANOMALY_THRESHOLD_STDDEV * stddev
                    ]
                    
                    if anomalies:
                        anomaly_rate = len(anomalies) / len(durations)
                        
                        if anomaly_rate > 0.1:  # >10% anomalies
                            confidence = min(0.5 + anomaly_rate * 0.3, 1.0)
                            
                            # Anomalies indicate potential issues
                            optimization_potential = anomaly_rate * 0.7
                            
                            pattern = Pattern(
                                pattern_id=self._generate_pattern_id("anomaly", cmd),
                                pattern_type="anomaly",
                                description=f"Command '{cmd}' shows {anomaly_rate:.1%} anomalous execution times",
                                frequency=len(anomalies),
                                confidence=confidence,
                                first_seen=interactions[0].timestamp,
                                last_seen=interactions[-1].timestamp,
                                examples=[f"Anomalous duration: {a:.1f}ms" for a in anomalies[:3]],
                                metadata={
                                    "mean_duration_ms": mean,
                                    "stddev_ms": stddev,
                                    "anomaly_rate": anomaly_rate,
                                    "threshold_stddev": ANOMALY_THRESHOLD_STDDEV
                                },
                                optimization_potential=optimization_potential
                            )
                            
                            patterns.append(pattern)
        
        return patterns
    
    # -------------------------
    # Helper Methods
    # -------------------------
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values"""
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)
    
    def _generate_pattern_id(self, pattern_type: str, identifier: str) -> str:
        """Generate unique pattern ID"""
        hash_input = f"{pattern_type}_{identifier}"
        return f"{pattern_type}_{hashlib.md5(hash_input.encode()).hexdigest()[:8]}"
    
    def _save_patterns(self):
        """Save patterns to disk"""
        filepath = self.data_dir / "detected_patterns.json"
        
        try:
            data = {
                pattern_id: pattern.to_dict()
                for pattern_id, pattern in self.patterns.items()
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            self._log(f"Saved {len(self.patterns)} patterns to {filepath}")
        
        except Exception as e:
            self._log(f"Error saving patterns: {e}", level="ERROR")
    
    def _load_patterns(self):
        """Load patterns from disk"""
        filepath = self.data_dir / "detected_patterns.json"
        
        if not filepath.exists():
            return
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            for pattern_id, pattern_data in data.items():
                self.patterns[pattern_id] = Pattern.from_dict(pattern_data)
            
            self.stats["total_patterns"] = len(self.patterns)
            self._log(f"Loaded {len(self.patterns)} patterns from {filepath}")
        
        except Exception as e:
            self._log(f"Error loading patterns: {e}", level="ERROR")
    
    def _log(self, message: str, level: str = "INFO"):
        """Log message"""
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"[{timestamp}] [{level}] [PatternRecognitionEngine] {message}\n"
        
        # Log to file
        log_file = LOG_DIR / "pattern_recognition.log"
        try:
            with open(log_file, 'a') as f:
                f.write(log_entry)
        except Exception:
            pass
        
        # Also log to system journal
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

_engine_instance: Optional[PatternRecognitionEngine] = None

def get_engine() -> PatternRecognitionEngine:
    """Get singleton engine instance"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = PatternRecognitionEngine()
    return _engine_instance

# -------------------------
# CLI for Testing
# -------------------------

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from learning.user_interaction_monitor import get_monitor, Interaction
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("Testing Pattern Recognition Engine...")
        
        # Get monitor and create test interactions
        monitor = get_monitor()
        
        # Load recent interactions
        interactions = monitor._load_recent_interactions(
            datetime.utcnow() - timedelta(hours=24)
        )
        
        if not interactions:
            print("No interactions found. Creating test data...")
            # Create test interactions
            from learning.user_interaction_monitor import InteractionType, InteractionStatus
            
            test_commands = ["status", "query", "experts", "status", "query", "status"]
            for i, cmd in enumerate(test_commands):
                monitor.record_interaction(
                    interaction_type=InteractionType.CLI_COMMAND,
                    command=cmd,
                    status=InteractionStatus.SUCCESS if i % 3 != 0 else InteractionStatus.FAILURE,
                    duration_ms=100.0 + i * 10
                )
            
            interactions = list(monitor.interaction_buffer)
        
        # Analyze patterns
        engine = get_engine()
        results = engine.analyze_interactions(interactions)
        
        print(f"\nAnalysis Results:")
        print(f"Patterns detected: {results['patterns_detected']}")
        print(f"\nStatistics: {json.dumps(results['statistics'], indent=2)}")
        
        # Show top patterns
        print(f"\nTop Patterns:")
        for pattern in results['patterns'][:5]:
            print(f"  - {pattern['pattern_type']}: {pattern['description']}")
            print(f"    Confidence: {pattern['confidence']:.2f}, Frequency: {pattern['frequency']}")
            print(f"    Optimization Potential: {pattern['optimization_potential']:.2f}")
        
        print("\nTest complete!")
    
    elif len(sys.argv) > 1 and sys.argv[1] == "analyze":
        # Analyze recent interactions
        from learning.user_interaction_monitor import get_monitor
        
        monitor = get_monitor()
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        
        interactions = monitor._load_recent_interactions(
            datetime.utcnow() - timedelta(hours=hours)
        )
        
        engine = get_engine()
        results = engine.analyze_interactions(interactions)
        
        print(json.dumps(results, indent=2))
    
    elif len(sys.argv) > 1 and sys.argv[1] == "opportunities":
        # Show optimization opportunities
        engine = get_engine()
        opportunities = engine.get_optimization_opportunities(top_n=10)
        
        print("Top Optimization Opportunities:")
        for i, pattern in enumerate(opportunities, 1):
            print(f"\n{i}. {pattern.description}")
            print(f"   Type: {pattern.pattern_type}")
            print(f"   Frequency: {pattern.frequency}")
            print(f"   Confidence: {pattern.confidence:.2f}")
            print(f"   Optimization Potential: {pattern.optimization_potential:.2f}")
    
    else:
        print("Pattern Recognition Engine")
        print("Usage:")
        print("  python pattern_recognition_engine.py test          - Run test")
        print("  python pattern_recognition_engine.py analyze [hours] - Analyze recent interactions")
        print("  python pattern_recognition_engine.py opportunities - Show optimization opportunities")
