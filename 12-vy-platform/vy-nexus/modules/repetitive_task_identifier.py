#!/usr/bin/env python3
"""
Repetitive Task Identifier
Identifies repetitive tasks suitable for automation
Enhances existing task_identifier.py with advanced detection

Part of Phase 3: Background Process Optimization
Created: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, Counter
import hashlib
import statistics


class RepetitiveTaskIdentifier:
    """
    Identifies repetitive tasks that are candidates for automation.
    Uses multiple detection strategies and scoring algorithms.
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.path.expanduser("~/vy-nexus"))
        self.data_path = self.base_path / "data" / "repetitive_tasks"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Storage files
        self.candidates_file = self.data_path / "automation_candidates.json"
        self.task_signatures_file = self.data_path / "task_signatures.json"
        self.repetition_patterns_file = self.data_path / "repetition_patterns.json"
        
        # Load existing data
        self.candidates = self._load_json(self.candidates_file, [])
        self.task_signatures = self._load_json(self.task_signatures_file, {})
        self.repetition_patterns = self._load_json(self.repetition_patterns_file, [])
        
        # Detection thresholds
        self.min_repetitions = 3  # Minimum occurrences to consider
        self.time_window_days = 30  # Analysis window
        self.similarity_threshold = 0.8  # Task similarity threshold
        
        print("✅ Repetitive Task Identifier initialized")
    
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
    
    def generate_task_signature(self, task_data: Dict[str, Any]) -> str:
        """
        Generate a signature for a task based on its characteristics.
        Similar tasks will have similar signatures.
        
        Args:
            task_data: Task data including type, parameters, context
        
        Returns:
            Task signature hash
        """
        # Extract key characteristics
        task_type = task_data.get("task_type", "unknown")
        
        # Normalize parameters for signature
        params = task_data.get("parameters", {})
        normalized_params = self._normalize_parameters(params)
        
        # Create signature string
        signature_parts = [
            task_type,
            json.dumps(normalized_params, sort_keys=True)
        ]
        
        signature_string = ":".join(signature_parts)
        signature_hash = hashlib.sha256(signature_string.encode()).hexdigest()[:16]
        
        return signature_hash
    
    def _normalize_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize parameters to identify similar tasks.
        Removes specific values that vary but keeps structure.
        """
        normalized = {}
        
        for key, value in params.items():
            # Keep parameter keys, generalize values
            if isinstance(value, (int, float)):
                # Categorize numeric values
                if value == 0:
                    normalized[key] = "zero"
                elif value < 10:
                    normalized[key] = "small"
                elif value < 100:
                    normalized[key] = "medium"
                else:
                    normalized[key] = "large"
            elif isinstance(value, str):
                # Keep string structure, not content
                if len(value) == 0:
                    normalized[key] = "empty_string"
                elif len(value) < 20:
                    normalized[key] = "short_string"
                else:
                    normalized[key] = "long_string"
            elif isinstance(value, bool):
                normalized[key] = str(value)
            elif isinstance(value, (list, tuple)):
                normalized[key] = f"list_{len(value)}"
            elif isinstance(value, dict):
                normalized[key] = f"dict_{len(value)}"
            else:
                normalized[key] = type(value).__name__
        
        return normalized
    
    def analyze_task_history(self, interactions_file: Path = None,
                            days: int = None) -> List[Dict[str, Any]]:
        """
        Analyze task history to identify repetitive patterns.
        
        Args:
            interactions_file: Path to interactions file
            days: Number of days to analyze
        
        Returns:
            List of repetitive task candidates
        """
        if interactions_file is None:
            interactions_file = self.base_path / "data" / "interactions" / "interactions.jsonl"
        
        if not interactions_file.exists():
            print("⚠️ No interactions file found")
            return []
        
        days = days or self.time_window_days
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Collect tasks
        tasks = []
        with open(interactions_file, 'r') as f:
            for line in f:
                try:
                    interaction = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(interaction["timestamp"])
                    
                    if timestamp < cutoff_date:
                        continue
                    
                    # Look for task-related interactions
                    if interaction.get("type") in ["task_request", "task_completion"]:
                        tasks.append(interaction)
                except:
                    continue
        
        # Group by signature
        signature_groups = defaultdict(list)
        
        for task in tasks:
            task_data = task.get("data", {})
            signature = self.generate_task_signature(task_data)
            signature_groups[signature].append(task)
        
        # Identify repetitive tasks
        candidates = []
        
        for signature, task_group in signature_groups.items():
            if len(task_group) >= self.min_repetitions:
                candidate = self._create_candidate(signature, task_group)
                candidates.append(candidate)
        
        # Sort by automation potential
        candidates.sort(key=lambda x: x["automation_score"], reverse=True)
        
        # Save candidates
        self.candidates = candidates
        self._save_json(self.candidates_file, candidates)
        
        return candidates
    
    def _create_candidate(self, signature: str, task_group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create an automation candidate from a group of similar tasks.
        """
        # Extract common characteristics
        first_task = task_group[0]
        task_data = first_task.get("data", {})
        task_type = task_data.get("task_type", "unknown")
        
        # Calculate statistics
        repetition_count = len(task_group)
        
        # Calculate time savings potential
        durations = []
        for task in task_group:
            if "duration" in task.get("data", {}):
                durations.append(task["data"]["duration"])
        
        avg_duration = statistics.mean(durations) if durations else 0
        total_time_spent = sum(durations) if durations else 0
        
        # Calculate frequency
        timestamps = [datetime.fromisoformat(t["timestamp"]) for t in task_group]
        time_span = (max(timestamps) - min(timestamps)).total_seconds() / 86400  # days
        frequency_per_day = repetition_count / time_span if time_span > 0 else 0
        
        # Calculate automation score
        automation_score = self._calculate_automation_score(
            repetition_count,
            avg_duration,
            frequency_per_day
        )
        
        # Estimate effort to automate
        automation_effort = self._estimate_automation_effort(task_type, task_data)
        
        # Calculate ROI
        roi = self._calculate_roi(
            total_time_spent,
            frequency_per_day,
            automation_effort
        )
        
        candidate = {
            "candidate_id": signature,
            "task_type": task_type,
            "task_signature": signature,
            "repetition_count": repetition_count,
            "avg_duration_seconds": round(avg_duration, 2),
            "total_time_spent_seconds": round(total_time_spent, 2),
            "frequency_per_day": round(frequency_per_day, 2),
            "automation_score": round(automation_score, 2),
            "automation_effort": automation_effort,
            "estimated_roi": round(roi, 2),
            "priority": self._determine_priority(automation_score, roi),
            "sample_task": task_data,
            "first_seen": min(timestamps).isoformat(),
            "last_seen": max(timestamps).isoformat(),
            "identified_at": datetime.utcnow().isoformat(),
            "status": "identified"
        }
        
        return candidate
    
    def _calculate_automation_score(self, repetitions: int, avg_duration: float,
                                   frequency: float) -> float:
        """
        Calculate automation potential score (0-100).
        
        Factors:
        - Repetition count (more = higher score)
        - Average duration (longer = higher score)
        - Frequency (more frequent = higher score)
        """
        # Repetition score (0-40 points)
        repetition_score = min(repetitions / 10 * 40, 40)
        
        # Duration score (0-30 points)
        duration_score = min(avg_duration / 60 * 30, 30)  # Max at 60 seconds
        
        # Frequency score (0-30 points)
        frequency_score = min(frequency / 5 * 30, 30)  # Max at 5 per day
        
        total_score = repetition_score + duration_score + frequency_score
        
        return total_score
    
    def _estimate_automation_effort(self, task_type: str, task_data: Dict[str, Any]) -> str:
        """
        Estimate effort required to automate this task.
        
        Returns:
            Effort level: low, medium, high
        """
        # Simple heuristic based on task complexity
        params = task_data.get("parameters", {})
        param_count = len(params)
        
        # Check for complex parameters
        has_complex_params = any(
            isinstance(v, (dict, list)) for v in params.values()
        )
        
        if param_count <= 2 and not has_complex_params:
            return "low"
        elif param_count <= 5 or has_complex_params:
            return "medium"
        else:
            return "high"
    
    def _calculate_roi(self, total_time_spent: float, frequency_per_day: float,
                      automation_effort: str) -> float:
        """
        Calculate return on investment for automation.
        
        Returns:
            ROI score (higher = better)
        """
        # Estimate time saved per month
        time_saved_per_month = frequency_per_day * 30 * (total_time_spent / max(frequency_per_day * 30, 1))
        
        # Estimate automation cost in hours
        effort_hours = {
            "low": 2,
            "medium": 8,
            "high": 20
        }
        
        automation_cost = effort_hours.get(automation_effort, 8) * 3600  # Convert to seconds
        
        # ROI = (time saved per month) / automation cost
        roi = time_saved_per_month / automation_cost if automation_cost > 0 else 0
        
        return roi
    
    def _determine_priority(self, automation_score: float, roi: float) -> str:
        """
        Determine priority level for automation.
        
        Returns:
            Priority: critical, high, medium, low
        """
        if automation_score >= 80 and roi >= 2.0:
            return "critical"
        elif automation_score >= 60 and roi >= 1.0:
            return "high"
        elif automation_score >= 40 or roi >= 0.5:
            return "medium"
        else:
            return "low"
    
    def detect_temporal_patterns(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """
        Detect temporal patterns for a specific candidate.
        
        Args:
            candidate_id: Candidate identifier
        
        Returns:
            Temporal pattern information
        """
        candidate = next((c for c in self.candidates if c["candidate_id"] == candidate_id), None)
        
        if not candidate:
            return None
        
        # Load interactions for this candidate
        interactions_file = self.base_path / "data" / "interactions" / "interactions.jsonl"
        
        if not interactions_file.exists():
            return None
        
        matching_tasks = []
        with open(interactions_file, 'r') as f:
            for line in f:
                try:
                    interaction = json.loads(line.strip())
                    task_data = interaction.get("data", {})
                    signature = self.generate_task_signature(task_data)
                    
                    if signature == candidate_id:
                        matching_tasks.append(interaction)
                except:
                    continue
        
        if not matching_tasks:
            return None
        
        # Analyze temporal patterns
        timestamps = [datetime.fromisoformat(t["timestamp"]) for t in matching_tasks]
        
        # Hour of day distribution
        hour_counts = Counter(t.hour for t in timestamps)
        peak_hour = hour_counts.most_common(1)[0] if hour_counts else (None, 0)
        
        # Day of week distribution
        weekday_counts = Counter(t.weekday() for t in timestamps)
        peak_weekday = weekday_counts.most_common(1)[0] if weekday_counts else (None, 0)
        
        # Calculate intervals between occurrences
        if len(timestamps) > 1:
            sorted_timestamps = sorted(timestamps)
            intervals = [(sorted_timestamps[i+1] - sorted_timestamps[i]).total_seconds() / 3600 
                        for i in range(len(sorted_timestamps)-1)]
            avg_interval = statistics.mean(intervals)
            interval_std = statistics.stdev(intervals) if len(intervals) > 1 else 0
        else:
            avg_interval = 0
            interval_std = 0
        
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        pattern = {
            "candidate_id": candidate_id,
            "peak_hour": peak_hour[0],
            "peak_hour_count": peak_hour[1],
            "peak_weekday": weekday_names[peak_weekday[0]] if peak_weekday[0] is not None else None,
            "peak_weekday_count": peak_weekday[1],
            "avg_interval_hours": round(avg_interval, 2),
            "interval_std_hours": round(interval_std, 2),
            "is_regular": interval_std < avg_interval * 0.3 if avg_interval > 0 else False,
            "hourly_distribution": dict(hour_counts),
            "weekday_distribution": dict(weekday_counts)
        }
        
        return pattern
    
    def get_top_candidates(self, limit: int = 10, min_priority: str = None) -> List[Dict[str, Any]]:
        """
        Get top automation candidates.
        
        Args:
            limit: Maximum number of candidates to return
            min_priority: Minimum priority level
        
        Returns:
            List of top candidates
        """
        candidates = self.candidates.copy()
        
        # Filter by priority if specified
        if min_priority:
            priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            min_level = priority_order.get(min_priority, 0)
            candidates = [c for c in candidates 
                         if priority_order.get(c["priority"], 0) >= min_level]
        
        # Sort by automation score
        candidates.sort(key=lambda x: x["automation_score"], reverse=True)
        
        return candidates[:limit]
    
    def generate_identification_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive identification report.
        
        Returns:
            Identification report
        """
        print("\n🔍 Generating repetitive task identification report...")
        
        # Analyze current candidates
        total_candidates = len(self.candidates)
        
        # Group by priority
        priority_counts = Counter(c["priority"] for c in self.candidates)
        
        # Calculate potential time savings
        total_time_savings = sum(c["total_time_spent_seconds"] for c in self.candidates)
        
        # Get top candidates
        top_candidates = self.get_top_candidates(5)
        
        # Calculate average metrics
        if self.candidates:
            avg_repetitions = statistics.mean(c["repetition_count"] for c in self.candidates)
            avg_automation_score = statistics.mean(c["automation_score"] for c in self.candidates)
            avg_roi = statistics.mean(c["estimated_roi"] for c in self.candidates)
        else:
            avg_repetitions = 0
            avg_automation_score = 0
            avg_roi = 0
        
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "analysis_window_days": self.time_window_days,
            "total_candidates": total_candidates,
            "priority_distribution": dict(priority_counts),
            "total_time_savings_hours": round(total_time_savings / 3600, 2),
            "average_metrics": {
                "avg_repetitions": round(avg_repetitions, 2),
                "avg_automation_score": round(avg_automation_score, 2),
                "avg_roi": round(avg_roi, 2)
            },
            "top_candidates": [
                {
                    "task_type": c["task_type"],
                    "repetitions": c["repetition_count"],
                    "automation_score": c["automation_score"],
                    "priority": c["priority"],
                    "roi": c["estimated_roi"]
                }
                for c in top_candidates
            ]
        }
        
        # Save report
        report_path = self.data_path / f"identification_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        self._save_json(report_path, report)
        
        print(f"✅ Report saved: {report_path}")
        
        return report


if __name__ == "__main__":
    print("🔍 Repetitive Task Identifier - Test Mode")
    print("="*60)
    
    identifier = RepetitiveTaskIdentifier()
    
    # Test signature generation
    print("\n🔑 Testing signature generation...")
    
    task1 = {
        "task_type": "file_backup",
        "parameters": {"source": "/data", "destination": "/backup", "size": 1024}
    }
    
    task2 = {
        "task_type": "file_backup",
        "parameters": {"source": "/documents", "destination": "/backup", "size": 2048}
    }
    
    sig1 = identifier.generate_task_signature(task1)
    sig2 = identifier.generate_task_signature(task2)
    
    print(f"  Task 1 signature: {sig1}")
    print(f"  Task 2 signature: {sig2}")
    print(f"  Signatures match: {sig1 == sig2}")
    
    # Analyze task history
    print("\n📊 Analyzing task history...")
    candidates = identifier.analyze_task_history()
    print(f"  Candidates identified: {len(candidates)}")
    
    # Get top candidates
    print("\n🎯 Getting top candidates...")
    top = identifier.get_top_candidates(5)
    print(f"  Top candidates: {len(top)}")
    
    for i, candidate in enumerate(top, 1):
        print(f"\n  {i}. {candidate['task_type']}")
        print(f"     Repetitions: {candidate['repetition_count']}")
        print(f"     Score: {candidate['automation_score']:.1f}")
        print(f"     Priority: {candidate['priority']}")
        print(f"     ROI: {candidate['estimated_roi']:.2f}")
    
    # Generate report
    print("\n📄 Generating identification report...")
    report = identifier.generate_identification_report()
    print(f"  Total candidates: {report['total_candidates']}")
    print(f"  Potential time savings: {report['total_time_savings_hours']:.1f} hours")
    print(f"  Priority distribution: {report['priority_distribution']}")
    
    print("\n✨ Repetitive task identifier test complete!")
