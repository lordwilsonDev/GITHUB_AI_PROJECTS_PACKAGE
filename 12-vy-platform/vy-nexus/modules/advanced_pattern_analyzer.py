#!/usr/bin/env python3
"""
Advanced Pattern Analyzer
Enhanced pattern recognition with ML-inspired algorithms
Integrates with existing pattern_recognition.py

Part of Phase 2: Continuous Learning Engine
Created: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import Counter, defaultdict
import hashlib
import math


class AdvancedPatternAnalyzer:
    """
    Advanced pattern recognition and analysis.
    Complements existing pattern_recognition.py with additional algorithms.
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.path.expanduser("~/vy-nexus"))
        self.data_path = self.base_path / "data" / "patterns"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Pattern storage
        self.patterns_file = self.data_path / "advanced_patterns.json"
        self.sequences_file = self.data_path / "sequence_patterns.json"
        self.temporal_file = self.data_path / "temporal_patterns.json"
        
        # Load existing patterns
        self.patterns = self._load_json(self.patterns_file, {})
        self.sequences = self._load_json(self.sequences_file, {})
        self.temporal = self._load_json(self.temporal_file, {})
        
        print("✅ Advanced Pattern Analyzer initialized")
    
    def _load_json(self, filepath: Path, default: Any) -> Any:
        """Load JSON file or return default"""
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
        return default
    
    def _save_json(self, filepath: Path, data: Any):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")
    
    def analyze_interaction_sequences(self, interactions: List[Dict[str, Any]],
                                     min_sequence_length: int = 2,
                                     max_sequence_length: int = 5,
                                     min_support: int = 2) -> List[Dict[str, Any]]:
        """
        Analyze sequences of interactions to find common patterns.
        Uses sequential pattern mining.
        
        Args:
            interactions: List of interaction records
            min_sequence_length: Minimum length of sequences to consider
            max_sequence_length: Maximum length of sequences to consider
            min_support: Minimum number of occurrences to be considered a pattern
        
        Returns:
            List of discovered sequence patterns
        """
        if len(interactions) < min_sequence_length:
            return []
        
        # Extract interaction types in order
        interaction_types = [i.get("type", "unknown") for i in interactions]
        
        # Find all sequences of different lengths
        sequence_counts = defaultdict(int)
        
        for length in range(min_sequence_length, min(max_sequence_length + 1, len(interaction_types))):
            for i in range(len(interaction_types) - length + 1):
                sequence = tuple(interaction_types[i:i+length])
                sequence_counts[sequence] += 1
        
        # Filter by minimum support
        patterns = []
        for sequence, count in sequence_counts.items():
            if count >= min_support:
                patterns.append({
                    "sequence": list(sequence),
                    "length": len(sequence),
                    "support": count,
                    "confidence": count / len(interactions),
                    "pattern_id": self._generate_pattern_id(sequence)
                })
        
        # Sort by support (most common first)
        patterns.sort(key=lambda x: x["support"], reverse=True)
        
        return patterns
    
    def detect_temporal_patterns(self, interactions: List[Dict[str, Any]],
                                time_bucket_minutes: int = 60) -> Dict[str, Any]:
        """
        Detect temporal patterns in interactions.
        Identifies peak times, cyclical patterns, and time-based correlations.
        
        Args:
            interactions: List of interaction records
            time_bucket_minutes: Size of time buckets for analysis
        
        Returns:
            Dictionary of temporal patterns
        """
        if not interactions:
            return {}
        
        # Group by time buckets
        hourly_counts = defaultdict(int)
        daily_counts = defaultdict(int)
        weekday_counts = defaultdict(int)
        
        for interaction in interactions:
            try:
                timestamp = datetime.fromisoformat(interaction["timestamp"])
                
                # Hour of day (0-23)
                hourly_counts[timestamp.hour] += 1
                
                # Day of week (0=Monday, 6=Sunday)
                weekday_counts[timestamp.weekday()] += 1
                
                # Date
                date_key = timestamp.strftime("%Y-%m-%d")
                daily_counts[date_key] += 1
                
            except Exception as e:
                continue
        
        # Find peak times
        peak_hour = max(hourly_counts.items(), key=lambda x: x[1]) if hourly_counts else (None, 0)
        peak_weekday = max(weekday_counts.items(), key=lambda x: x[1]) if weekday_counts else (None, 0)
        
        # Calculate activity distribution
        total_interactions = len(interactions)
        hourly_distribution = {h: count/total_interactions for h, count in hourly_counts.items()}
        
        # Detect cyclical patterns (simple heuristic)
        is_cyclical = self._detect_cyclical_pattern(list(hourly_counts.values()))
        
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        return {
            "peak_hour": peak_hour[0],
            "peak_hour_count": peak_hour[1],
            "peak_weekday": weekday_names[peak_weekday[0]] if peak_weekday[0] is not None else None,
            "peak_weekday_count": peak_weekday[1],
            "hourly_distribution": dict(sorted(hourly_distribution.items())),
            "weekday_distribution": dict(weekday_counts),
            "daily_counts": dict(sorted(daily_counts.items())),
            "is_cyclical": is_cyclical,
            "total_days": len(daily_counts),
            "avg_interactions_per_day": total_interactions / len(daily_counts) if daily_counts else 0
        }
    
    def _detect_cyclical_pattern(self, values: List[int]) -> bool:
        """Simple cyclical pattern detection using variance"""
        if len(values) < 3:
            return False
        
        # Calculate variance
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        
        # If variance is low relative to mean, it's more cyclical
        coefficient_of_variation = (variance ** 0.5) / mean if mean > 0 else 0
        
        return coefficient_of_variation < 0.5  # Threshold for cyclical
    
    def identify_co_occurrence_patterns(self, interactions: List[Dict[str, Any]],
                                       time_window_minutes: int = 30) -> List[Dict[str, Any]]:
        """
        Identify patterns where certain interaction types frequently occur together.
        
        Args:
            interactions: List of interaction records
            time_window_minutes: Time window to consider interactions as co-occurring
        
        Returns:
            List of co-occurrence patterns
        """
        if len(interactions) < 2:
            return []
        
        # Group interactions by time windows
        time_windows = []
        current_window = []
        window_start = None
        
        for interaction in sorted(interactions, key=lambda x: x.get("timestamp", "")):
            try:
                timestamp = datetime.fromisoformat(interaction["timestamp"])
                
                if window_start is None:
                    window_start = timestamp
                    current_window = [interaction]
                elif (timestamp - window_start).total_seconds() <= time_window_minutes * 60:
                    current_window.append(interaction)
                else:
                    if len(current_window) > 1:
                        time_windows.append(current_window)
                    window_start = timestamp
                    current_window = [interaction]
            except:
                continue
        
        if len(current_window) > 1:
            time_windows.append(current_window)
        
        # Find co-occurrence patterns
        co_occurrences = defaultdict(int)
        
        for window in time_windows:
            types = set(i.get("type", "unknown") for i in window)
            if len(types) > 1:
                # Create sorted tuple of types for consistent key
                type_tuple = tuple(sorted(types))
                co_occurrences[type_tuple] += 1
        
        # Convert to list of patterns
        patterns = []
        for types, count in co_occurrences.items():
            if count >= 2:  # Minimum support
                patterns.append({
                    "interaction_types": list(types),
                    "co_occurrence_count": count,
                    "confidence": count / len(time_windows) if time_windows else 0,
                    "time_window_minutes": time_window_minutes
                })
        
        patterns.sort(key=lambda x: x["co_occurrence_count"], reverse=True)
        
        return patterns
    
    def detect_anomalies(self, interactions: List[Dict[str, Any]],
                        sensitivity: float = 2.0) -> List[Dict[str, Any]]:
        """
        Detect anomalous interactions using statistical methods.
        
        Args:
            interactions: List of interaction records
            sensitivity: Standard deviations from mean to consider anomalous
        
        Returns:
            List of detected anomalies
        """
        if len(interactions) < 10:  # Need sufficient data
            return []
        
        anomalies = []
        
        # Analyze interaction timing
        timestamps = []
        for i in interactions:
            try:
                timestamps.append(datetime.fromisoformat(i["timestamp"]))
            except:
                continue
        
        if len(timestamps) < 2:
            return []
        
        # Calculate time differences between consecutive interactions
        time_diffs = [(timestamps[i+1] - timestamps[i]).total_seconds() 
                     for i in range(len(timestamps)-1)]
        
        if not time_diffs:
            return []
        
        # Calculate mean and standard deviation
        mean_diff = sum(time_diffs) / len(time_diffs)
        variance = sum((x - mean_diff) ** 2 for x in time_diffs) / len(time_diffs)
        std_dev = variance ** 0.5
        
        # Detect anomalies
        for i, diff in enumerate(time_diffs):
            if abs(diff - mean_diff) > sensitivity * std_dev:
                anomalies.append({
                    "type": "timing_anomaly",
                    "interaction_index": i,
                    "time_diff_seconds": diff,
                    "expected_range": [mean_diff - sensitivity * std_dev, 
                                      mean_diff + sensitivity * std_dev],
                    "deviation_score": abs(diff - mean_diff) / std_dev if std_dev > 0 else 0,
                    "timestamp": timestamps[i].isoformat()
                })
        
        return anomalies
    
    def calculate_pattern_confidence(self, pattern: Dict[str, Any],
                                    total_interactions: int) -> float:
        """
        Calculate confidence score for a pattern.
        
        Args:
            pattern: Pattern dictionary
            total_interactions: Total number of interactions
        
        Returns:
            Confidence score (0-1)
        """
        support = pattern.get("support", 0)
        length = pattern.get("length", 1)
        
        # Base confidence from support
        base_confidence = support / total_interactions if total_interactions > 0 else 0
        
        # Bonus for longer patterns (they're more specific)
        length_bonus = min(length / 10, 0.3)  # Max 30% bonus
        
        # Final confidence
        confidence = min(base_confidence + length_bonus, 1.0)
        
        return round(confidence, 3)
    
    def _generate_pattern_id(self, sequence: Tuple) -> str:
        """Generate unique pattern ID"""
        content = ":".join(str(s) for s in sequence)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def find_workflow_patterns(self, interactions: List[Dict[str, Any]],
                              min_workflow_length: int = 3,
                              max_time_gap_minutes: int = 60) -> List[Dict[str, Any]]:
        """
        Identify complete workflow patterns (sequences that lead to completion).
        
        Args:
            interactions: List of interaction records
            min_workflow_length: Minimum steps in a workflow
            max_time_gap_minutes: Maximum time between steps
        
        Returns:
            List of workflow patterns
        """
        workflows = []
        current_workflow = []
        last_timestamp = None
        
        for interaction in interactions:
            try:
                timestamp = datetime.fromisoformat(interaction["timestamp"])
                
                # Check if this continues the current workflow
                if last_timestamp is None or \
                   (timestamp - last_timestamp).total_seconds() <= max_time_gap_minutes * 60:
                    current_workflow.append(interaction)
                    last_timestamp = timestamp
                else:
                    # Workflow ended, save if long enough
                    if len(current_workflow) >= min_workflow_length:
                        workflows.append(self._analyze_workflow(current_workflow))
                    current_workflow = [interaction]
                    last_timestamp = timestamp
            except:
                continue
        
        # Don't forget the last workflow
        if len(current_workflow) >= min_workflow_length:
            workflows.append(self._analyze_workflow(current_workflow))
        
        return workflows
    
    def _analyze_workflow(self, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a single workflow"""
        if not workflow:
            return {}
        
        # Extract workflow characteristics
        steps = [i.get("type", "unknown") for i in workflow]
        
        # Calculate duration
        try:
            start_time = datetime.fromisoformat(workflow[0]["timestamp"])
            end_time = datetime.fromisoformat(workflow[-1]["timestamp"])
            duration = (end_time - start_time).total_seconds()
        except:
            duration = 0
        
        # Check if workflow was successful (heuristic: ends with completion)
        success = any("completion" in step.lower() or "success" in step.lower() 
                     for step in steps)
        
        return {
            "workflow_id": self._generate_pattern_id(tuple(steps)),
            "steps": steps,
            "step_count": len(steps),
            "duration_seconds": duration,
            "duration_minutes": round(duration / 60, 2),
            "success": success,
            "start_time": workflow[0].get("timestamp"),
            "end_time": workflow[-1].get("timestamp")
        }
    
    def generate_pattern_report(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive pattern analysis report.
        
        Args:
            interactions: List of interaction records
        
        Returns:
            Comprehensive pattern report
        """
        print("\n🔍 Generating comprehensive pattern report...")
        
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_interactions": len(interactions),
            "analysis_results": {}
        }
        
        # Sequence patterns
        print("  Analyzing sequences...")
        sequences = self.analyze_interaction_sequences(interactions)
        report["analysis_results"]["sequence_patterns"] = {
            "count": len(sequences),
            "patterns": sequences[:10]  # Top 10
        }
        
        # Temporal patterns
        print("  Analyzing temporal patterns...")
        temporal = self.detect_temporal_patterns(interactions)
        report["analysis_results"]["temporal_patterns"] = temporal
        
        # Co-occurrence patterns
        print("  Analyzing co-occurrences...")
        co_occurrences = self.identify_co_occurrence_patterns(interactions)
        report["analysis_results"]["co_occurrence_patterns"] = {
            "count": len(co_occurrences),
            "patterns": co_occurrences[:10]  # Top 10
        }
        
        # Workflow patterns
        print("  Analyzing workflows...")
        workflows = self.find_workflow_patterns(interactions)
        report["analysis_results"]["workflow_patterns"] = {
            "count": len(workflows),
            "successful_workflows": len([w for w in workflows if w.get("success")]),
            "avg_workflow_duration": sum(w.get("duration_seconds", 0) for w in workflows) / len(workflows) if workflows else 0,
            "workflows": workflows[:5]  # Top 5
        }
        
        # Anomalies
        print("  Detecting anomalies...")
        anomalies = self.detect_anomalies(interactions)
        report["analysis_results"]["anomalies"] = {
            "count": len(anomalies),
            "anomalies": anomalies[:5]  # Top 5
        }
        
        # Save report
        report_path = self.data_path / f"pattern_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        self._save_json(report_path, report)
        
        print(f"\n✅ Pattern report saved: {report_path}")
        
        return report
    
    def get_pattern_insights(self, report: Dict[str, Any]) -> List[str]:
        """
        Generate human-readable insights from pattern report.
        
        Args:
            report: Pattern analysis report
        
        Returns:
            List of insight strings
        """
        insights = []
        results = report.get("analysis_results", {})
        
        # Sequence insights
        sequences = results.get("sequence_patterns", {}).get("patterns", [])
        if sequences:
            top_sequence = sequences[0]
            insights.append(
                f"Most common interaction sequence: {' → '.join(top_sequence['sequence'])} "
                f"(occurred {top_sequence['support']} times)"
            )
        
        # Temporal insights
        temporal = results.get("temporal_patterns", {})
        if temporal.get("peak_hour") is not None:
            insights.append(
                f"Peak activity hour: {temporal['peak_hour']}:00 "
                f"({temporal['peak_hour_count']} interactions)"
            )
        
        if temporal.get("is_cyclical"):
            insights.append("Activity shows cyclical patterns - predictable usage times")
        
        # Workflow insights
        workflows = results.get("workflow_patterns", {})
        if workflows.get("count", 0) > 0:
            success_rate = (workflows.get("successful_workflows", 0) / workflows["count"]) * 100
            insights.append(
                f"Identified {workflows['count']} workflows with {success_rate:.1f}% success rate"
            )
        
        # Anomaly insights
        anomalies = results.get("anomalies", {})
        if anomalies.get("count", 0) > 0:
            insights.append(
                f"Detected {anomalies['count']} anomalous interactions - may indicate issues or unusual usage"
            )
        
        return insights


if __name__ == "__main__":
    print("🔍 Advanced Pattern Analyzer - Test Mode")
    print("="*60)
    
    analyzer = AdvancedPatternAnalyzer()
    
    # Create test interactions
    print("\n📝 Creating test interactions...")
    test_interactions = []
    base_time = datetime.utcnow()
    
    interaction_types = ["task_request", "query", "task_completion", "feedback"]
    
    for i in range(20):
        test_interactions.append({
            "timestamp": (base_time + timedelta(minutes=i*5)).isoformat(),
            "type": interaction_types[i % len(interaction_types)],
            "data": {"test": True}
        })
    
    print(f"✅ Created {len(test_interactions)} test interactions")
    
    # Analyze sequences
    print("\n🔍 Analyzing sequences...")
    sequences = analyzer.analyze_interaction_sequences(test_interactions)
    print(f"  Found {len(sequences)} sequence patterns")
    if sequences:
        print(f"  Top pattern: {sequences[0]['sequence']} (support: {sequences[0]['support']})")
    
    # Detect temporal patterns
    print("\n🕒 Analyzing temporal patterns...")
    temporal = analyzer.detect_temporal_patterns(test_interactions)
    print(f"  Peak hour: {temporal.get('peak_hour')}")
    print(f"  Is cyclical: {temporal.get('is_cyclical')}")
    
    # Find co-occurrences
    print("\n🔗 Analyzing co-occurrences...")
    co_occurrences = analyzer.identify_co_occurrence_patterns(test_interactions)
    print(f"  Found {len(co_occurrences)} co-occurrence patterns")
    
    # Find workflows
    print("\n🔄 Analyzing workflows...")
    workflows = analyzer.find_workflow_patterns(test_interactions)
    print(f"  Found {len(workflows)} workflows")
    
    # Generate full report
    print("\n📊 Generating comprehensive report...")
    report = analyzer.generate_pattern_report(test_interactions)
    
    # Get insights
    print("\n💡 Pattern Insights:")
    insights = analyzer.get_pattern_insights(report)
    for insight in insights:
        print(f"  - {insight}")
    
    print("\n✨ Advanced pattern analyzer test complete!")
