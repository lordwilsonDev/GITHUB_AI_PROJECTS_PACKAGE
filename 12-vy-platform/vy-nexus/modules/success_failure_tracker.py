#!/usr/bin/env python3
"""
Success/Failure Tracking Mechanism
Tracks task outcomes, learns from successes and failures
Integrates with existing success_failure_learning.py

Part of Phase 2: Continuous Learning Engine
Created: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import hashlib


class SuccessFailureTracker:
    """
    Tracks and analyzes task successes and failures.
    Learns from outcomes to improve future performance.
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.path.expanduser("~/vy-nexus"))
        self.data_path = self.base_path / "data" / "outcomes"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Outcome storage
        self.outcomes_file = self.data_path / "task_outcomes.jsonl"
        self.success_patterns_file = self.data_path / "success_patterns.json"
        self.failure_patterns_file = self.data_path / "failure_patterns.json"
        self.learnings_file = self.data_path / "learnings.json"
        
        # Load existing data
        self.success_patterns = self._load_json(self.success_patterns_file, [])
        self.failure_patterns = self._load_json(self.failure_patterns_file, [])
        self.learnings = self._load_json(self.learnings_file, [])
        
        # In-memory tracking
        self.recent_outcomes = []
        
        print("✅ Success/Failure Tracker initialized")
    
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
    
    def track_task_outcome(self, task_id: str, task_type: str,
                          success: bool, duration: float,
                          context: Dict[str, Any] = None,
                          error_details: Dict[str, Any] = None,
                          result_quality: float = None) -> Dict[str, Any]:
        """
        Track the outcome of a task.
        
        Args:
            task_id: Unique task identifier
            task_type: Type of task
            success: Whether task succeeded
            duration: Task duration in seconds
            context: Task context (parameters, environment, etc.)
            error_details: Error information if failed
            result_quality: Quality score of result (0-1)
        
        Returns:
            Outcome record
        """
        timestamp = datetime.utcnow()
        
        outcome = {
            "outcome_id": self._generate_outcome_id(task_id, timestamp),
            "task_id": task_id,
            "task_type": task_type,
            "timestamp": timestamp.isoformat(),
            "success": success,
            "duration_seconds": duration,
            "context": context or {},
            "error_details": error_details,
            "result_quality": result_quality,
            "metadata": {
                "tracked_at": timestamp.isoformat()
            }
        }
        
        # Add to recent outcomes
        self.recent_outcomes.append(outcome)
        if len(self.recent_outcomes) > 100:  # Keep last 100
            self.recent_outcomes.pop(0)
        
        # Persist to disk
        self._persist_outcome(outcome)
        
        # Analyze and learn from outcome
        if success:
            self._learn_from_success(outcome)
        else:
            self._learn_from_failure(outcome)
        
        return outcome
    
    def _generate_outcome_id(self, task_id: str, timestamp: datetime) -> str:
        """Generate unique outcome ID"""
        content = f"{task_id}:{timestamp.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _persist_outcome(self, outcome: Dict[str, Any]):
        """Persist outcome to disk"""
        try:
            with open(self.outcomes_file, 'a') as f:
                f.write(json.dumps(outcome) + "\n")
        except Exception as e:
            print(f"⚠️ Error persisting outcome: {e}")
    
    def _learn_from_success(self, outcome: Dict[str, Any]):
        """
        Learn from successful task execution.
        Identify what contributed to success.
        """
        task_type = outcome["task_type"]
        context = outcome.get("context", {})
        duration = outcome["duration_seconds"]
        quality = outcome.get("result_quality")
        
        # Find or create success pattern for this task type
        pattern = next((p for p in self.success_patterns if p["task_type"] == task_type), None)
        
        if pattern is None:
            pattern = {
                "task_type": task_type,
                "success_count": 0,
                "total_duration": 0,
                "avg_duration": 0,
                "quality_scores": [],
                "common_context_factors": {},
                "best_practices": [],
                "created_at": datetime.utcnow().isoformat()
            }
            self.success_patterns.append(pattern)
        
        # Update pattern
        pattern["success_count"] += 1
        pattern["total_duration"] += duration
        pattern["avg_duration"] = pattern["total_duration"] / pattern["success_count"]
        
        if quality is not None:
            pattern["quality_scores"].append(quality)
            pattern["avg_quality"] = sum(pattern["quality_scores"]) / len(pattern["quality_scores"])
        
        # Track context factors
        for key, value in context.items():
            if key not in pattern["common_context_factors"]:
                pattern["common_context_factors"][key] = []
            pattern["common_context_factors"][key].append(str(value))
        
        pattern["last_updated"] = datetime.utcnow().isoformat()
        
        # Save patterns
        self._save_json(self.success_patterns_file, self.success_patterns)
    
    def _learn_from_failure(self, outcome: Dict[str, Any]):
        """
        Learn from failed task execution.
        Identify root causes and prevention strategies.
        """
        task_type = outcome["task_type"]
        error_details = outcome.get("error_details", {})
        context = outcome.get("context", {})
        
        # Extract error information
        error_type = error_details.get("error_type", "unknown")
        error_message = error_details.get("error_message", "")
        
        # Find or create failure pattern
        pattern_key = f"{task_type}:{error_type}"
        pattern = next((p for p in self.failure_patterns if p["pattern_key"] == pattern_key), None)
        
        if pattern is None:
            pattern = {
                "pattern_key": pattern_key,
                "task_type": task_type,
                "error_type": error_type,
                "occurrence_count": 0,
                "error_messages": [],
                "contexts": [],
                "potential_causes": [],
                "prevention_strategies": [],
                "created_at": datetime.utcnow().isoformat()
            }
            self.failure_patterns.append(pattern)
        
        # Update pattern
        pattern["occurrence_count"] += 1
        
        if error_message and error_message not in pattern["error_messages"]:
            pattern["error_messages"].append(error_message)
        
        pattern["contexts"].append(context)
        pattern["last_occurred"] = datetime.utcnow().isoformat()
        
        # Analyze for potential causes
        if pattern["occurrence_count"] >= 3:
            causes = self._identify_potential_causes(pattern)
            pattern["potential_causes"] = causes
        
        # Save patterns
        self._save_json(self.failure_patterns_file, self.failure_patterns)
    
    def _identify_potential_causes(self, failure_pattern: Dict[str, Any]) -> List[str]:
        """
        Identify potential causes of failures based on pattern analysis.
        """
        causes = []
        contexts = failure_pattern.get("contexts", [])
        
        if not contexts:
            return causes
        
        # Look for common factors across failures
        common_factors = defaultdict(int)
        
        for context in contexts:
            for key, value in context.items():
                factor_key = f"{key}={value}"
                common_factors[factor_key] += 1
        
        # Factors appearing in >50% of failures are potential causes
        threshold = len(contexts) * 0.5
        for factor, count in common_factors.items():
            if count >= threshold:
                causes.append(f"Common factor: {factor} (in {count}/{len(contexts)} failures)")
        
        return causes
    
    def record_learning(self, learning_type: str, description: str,
                       source_task_type: str = None,
                       confidence: float = 0.8,
                       applicable_to: List[str] = None) -> Dict[str, Any]:
        """
        Record a learning derived from success/failure analysis.
        
        Args:
            learning_type: Type of learning (best_practice, pitfall, optimization, etc.)
            description: Description of the learning
            source_task_type: Task type this learning came from
            confidence: Confidence in this learning (0-1)
            applicable_to: List of task types this applies to
        
        Returns:
            Learning record
        """
        learning = {
            "learning_id": hashlib.sha256(
                f"{learning_type}:{description}:{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:16],
            "learning_type": learning_type,
            "description": description,
            "source_task_type": source_task_type,
            "confidence": confidence,
            "applicable_to": applicable_to or [],
            "created_at": datetime.utcnow().isoformat(),
            "applied_count": 0,
            "validation_score": None
        }
        
        self.learnings.append(learning)
        self._save_json(self.learnings_file, self.learnings)
        
        return learning
    
    def get_success_rate(self, task_type: str = None,
                        time_window_days: int = 7) -> Dict[str, Any]:
        """
        Calculate success rate for tasks.
        
        Args:
            task_type: Specific task type (None for all)
            time_window_days: Time window to analyze
        
        Returns:
            Success rate statistics
        """
        if not self.outcomes_file.exists():
            return {"success_rate": 0, "total_tasks": 0}
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
        
        total = 0
        successful = 0
        
        with open(self.outcomes_file, 'r') as f:
            for line in f:
                try:
                    outcome = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(outcome["timestamp"])
                    
                    if timestamp < cutoff_date:
                        continue
                    
                    if task_type and outcome.get("task_type") != task_type:
                        continue
                    
                    total += 1
                    if outcome.get("success"):
                        successful += 1
                except:
                    continue
        
        success_rate = (successful / total * 100) if total > 0 else 0
        
        return {
            "success_rate": round(success_rate, 2),
            "total_tasks": total,
            "successful_tasks": successful,
            "failed_tasks": total - successful,
            "time_window_days": time_window_days,
            "task_type": task_type or "all"
        }
    
    def get_failure_analysis(self, task_type: str = None) -> Dict[str, Any]:
        """
        Get comprehensive failure analysis.
        
        Args:
            task_type: Specific task type (None for all)
        
        Returns:
            Failure analysis report
        """
        relevant_patterns = self.failure_patterns
        
        if task_type:
            relevant_patterns = [p for p in self.failure_patterns 
                               if p["task_type"] == task_type]
        
        if not relevant_patterns:
            return {"total_failure_patterns": 0}
        
        # Sort by occurrence count
        sorted_patterns = sorted(relevant_patterns, 
                               key=lambda x: x["occurrence_count"], 
                               reverse=True)
        
        # Calculate statistics
        total_failures = sum(p["occurrence_count"] for p in relevant_patterns)
        patterns_with_causes = len([p for p in relevant_patterns 
                                   if p.get("potential_causes")])
        
        return {
            "total_failure_patterns": len(relevant_patterns),
            "total_failures": total_failures,
            "patterns_with_identified_causes": patterns_with_causes,
            "most_common_failures": [
                {
                    "task_type": p["task_type"],
                    "error_type": p["error_type"],
                    "occurrence_count": p["occurrence_count"],
                    "potential_causes": p.get("potential_causes", [])
                }
                for p in sorted_patterns[:5]
            ]
        }
    
    def get_recommendations(self, task_type: str) -> List[Dict[str, Any]]:
        """
        Get recommendations for improving task success rate.
        
        Args:
            task_type: Task type to get recommendations for
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check success patterns
        success_pattern = next((p for p in self.success_patterns 
                              if p["task_type"] == task_type), None)
        
        if success_pattern:
            # Recommend best practices
            if success_pattern.get("avg_quality", 0) > 0.8:
                recommendations.append({
                    "type": "best_practice",
                    "priority": "high",
                    "recommendation": f"Continue current approach - achieving {success_pattern['avg_quality']:.1%} quality",
                    "confidence": 0.9
                })
            
            # Recommend based on duration
            if success_pattern.get("avg_duration", 0) > 0:
                recommendations.append({
                    "type": "performance",
                    "priority": "medium",
                    "recommendation": f"Average duration is {success_pattern['avg_duration']:.1f}s - consider optimization if >10s",
                    "confidence": 0.7
                })
        
        # Check failure patterns
        failure_patterns = [p for p in self.failure_patterns 
                          if p["task_type"] == task_type]
        
        for pattern in failure_patterns:
            if pattern["occurrence_count"] >= 3:
                recommendations.append({
                    "type": "error_prevention",
                    "priority": "high",
                    "recommendation": f"Address recurring {pattern['error_type']} errors ({pattern['occurrence_count']} occurrences)",
                    "potential_causes": pattern.get("potential_causes", []),
                    "confidence": 0.85
                })
        
        # Check learnings
        applicable_learnings = [l for l in self.learnings 
                               if task_type in l.get("applicable_to", [])]
        
        for learning in applicable_learnings:
            recommendations.append({
                "type": learning["learning_type"],
                "priority": "medium",
                "recommendation": learning["description"],
                "confidence": learning["confidence"]
            })
        
        # Sort by priority and confidence
        priority_order = {"high": 3, "medium": 2, "low": 1}
        recommendations.sort(
            key=lambda x: (priority_order.get(x["priority"], 0), x["confidence"]),
            reverse=True
        )
        
        return recommendations
    
    def generate_outcome_report(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate comprehensive outcome report.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Outcome report
        """
        print(f"\n📊 Generating outcome report for last {days} days...")
        
        # Overall success rate
        overall_stats = self.get_success_rate(time_window_days=days)
        
        # Per-task-type statistics
        task_types = set()
        if self.outcomes_file.exists():
            with open(self.outcomes_file, 'r') as f:
                for line in f:
                    try:
                        outcome = json.loads(line.strip())
                        task_types.add(outcome.get("task_type", "unknown"))
                    except:
                        continue
        
        task_type_stats = {}
        for task_type in task_types:
            task_type_stats[task_type] = self.get_success_rate(task_type, days)
        
        # Failure analysis
        failure_analysis = self.get_failure_analysis()
        
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "time_window_days": days,
            "overall_statistics": overall_stats,
            "task_type_statistics": task_type_stats,
            "failure_analysis": failure_analysis,
            "success_patterns_count": len(self.success_patterns),
            "failure_patterns_count": len(self.failure_patterns),
            "learnings_count": len(self.learnings),
            "top_performing_tasks": self._get_top_performing_tasks(task_type_stats),
            "needs_improvement_tasks": self._get_needs_improvement_tasks(task_type_stats)
        }
        
        # Save report
        report_path = self.data_path / f"outcome_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        self._save_json(report_path, report)
        
        print(f"✅ Report saved: {report_path}")
        
        return report
    
    def _get_top_performing_tasks(self, task_stats: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Get top performing task types"""
        performing = []
        for task_type, stats in task_stats.items():
            if stats["total_tasks"] >= 3 and stats["success_rate"] >= 90:
                performing.append({
                    "task_type": task_type,
                    "success_rate": stats["success_rate"],
                    "total_tasks": stats["total_tasks"]
                })
        
        return sorted(performing, key=lambda x: x["success_rate"], reverse=True)[:5]
    
    def _get_needs_improvement_tasks(self, task_stats: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Get task types that need improvement"""
        needs_improvement = []
        for task_type, stats in task_stats.items():
            if stats["total_tasks"] >= 3 and stats["success_rate"] < 70:
                needs_improvement.append({
                    "task_type": task_type,
                    "success_rate": stats["success_rate"],
                    "failed_tasks": stats["failed_tasks"]
                })
        
        return sorted(needs_improvement, key=lambda x: x["success_rate"])[:5]


if __name__ == "__main__":
    print("📊 Success/Failure Tracker - Test Mode")
    print("="*60)
    
    tracker = SuccessFailureTracker()
    
    # Simulate task outcomes
    print("\n📝 Simulating task outcomes...")
    
    # Successful tasks
    for i in range(8):
        tracker.track_task_outcome(
            f"task-{i}",
            "code_generation",
            success=True,
            duration=2.5 + i * 0.3,
            context={"language": "python", "complexity": "medium"},
            result_quality=0.85 + i * 0.01
        )
    
    # Failed tasks
    for i in range(3):
        tracker.track_task_outcome(
            f"task-fail-{i}",
            "code_generation",
            success=False,
            duration=1.5,
            context={"language": "python", "complexity": "high"},
            error_details={
                "error_type": "syntax_error",
                "error_message": "Invalid syntax in generated code"
            }
        )
    
    print("✅ Outcomes tracked")
    
    # Get success rate
    print("\n📊 Success Rate:")
    stats = tracker.get_success_rate("code_generation", 7)
    print(f"  Task type: {stats['task_type']}")
    print(f"  Success rate: {stats['success_rate']}%")
    print(f"  Total tasks: {stats['total_tasks']}")
    
    # Get failure analysis
    print("\n🔍 Failure Analysis:")
    analysis = tracker.get_failure_analysis("code_generation")
    print(f"  Total failure patterns: {analysis['total_failure_patterns']}")
    print(f"  Total failures: {analysis['total_failures']}")
    
    # Get recommendations
    print("\n💡 Recommendations:")
    recommendations = tracker.get_recommendations("code_generation")
    for rec in recommendations[:3]:
        print(f"  [{rec['priority']}] {rec['recommendation']}")
    
    # Record a learning
    print("\n📚 Recording learning...")
    learning = tracker.record_learning(
        "best_practice",
        "Always validate generated code syntax before returning",
        source_task_type="code_generation",
        confidence=0.9,
        applicable_to=["code_generation", "code_review"]
    )
    print(f"  Learning recorded: {learning['learning_id']}")
    
    # Generate report
    print("\n📄 Generating outcome report...")
    report = tracker.generate_outcome_report(7)
    print(f"  Overall success rate: {report['overall_statistics']['success_rate']}%")
    print(f"  Success patterns: {report['success_patterns_count']}")
    print(f"  Learnings: {report['learnings_count']}")
    
    print("\n✨ Success/Failure tracker test complete!")
