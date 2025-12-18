#!/usr/bin/env python3
"""
Success/Failure Tracking System for VY-NEXUS

This module tracks task outcomes, success rates, failure patterns, and generates
automated improvement suggestions based on historical performance data.

Features:
- Task outcome tracking (success/failure/partial)
- Success rate metrics and trending
- Failure root cause analysis
- Performance trend analysis
- User satisfaction correlation
- Automated improvement suggestions
- Integration with User Interaction Monitor and Pattern Recognition

Author: VY-NEXUS Self-Evolving AI System
Date: December 15, 2025
"""

import json
import os
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from enum import Enum
import statistics


class TaskOutcome(Enum):
    """Enumeration of possible task outcomes."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class FailureCategory(Enum):
    """Categories of failure root causes."""
    USER_ERROR = "user_error"  # User provided incorrect input
    SYSTEM_ERROR = "system_error"  # System/infrastructure failure
    RESOURCE_ERROR = "resource_error"  # Resource unavailable/exhausted
    LOGIC_ERROR = "logic_error"  # Algorithm/logic bug
    TIMEOUT_ERROR = "timeout_error"  # Operation timed out
    DEPENDENCY_ERROR = "dependency_error"  # External dependency failed
    CONFIGURATION_ERROR = "configuration_error"  # Misconfiguration
    UNKNOWN_ERROR = "unknown_error"  # Unclassified


@dataclass
class TaskExecution:
    """Represents a single task execution."""
    task_id: str
    task_type: str
    outcome: TaskOutcome
    start_time: str
    end_time: str
    duration_ms: float
    error_message: Optional[str] = None
    failure_category: Optional[FailureCategory] = None
    user_satisfaction: Optional[int] = None  # 1-5 scale
    retry_count: int = 0
    context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['outcome'] = self.outcome.value
        if self.failure_category:
            data['failure_category'] = self.failure_category.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskExecution':
        """Create from dictionary."""
        data['outcome'] = TaskOutcome(data['outcome'])
        if data.get('failure_category'):
            data['failure_category'] = FailureCategory(data['failure_category'])
        return cls(**data)


@dataclass
class SuccessMetrics:
    """Success rate metrics for a task type."""
    task_type: str
    total_executions: int
    successful: int
    failed: int
    partial: int
    success_rate: float
    avg_duration_ms: float
    avg_satisfaction: Optional[float]
    failure_categories: Dict[str, int]
    trend: str  # "improving", "declining", "stable"
    

@dataclass
class ImprovementSuggestion:
    """Automated improvement suggestion."""
    suggestion_id: str
    task_type: str
    priority: str  # "high", "medium", "low"
    category: str  # "performance", "reliability", "usability"
    description: str
    rationale: str
    expected_impact: str
    implementation_effort: str  # "low", "medium", "high"
    created_at: str
    

class SuccessFailureTracker:
    """
    Tracks task execution outcomes and generates insights.
    
    This class provides comprehensive tracking of task success/failure patterns,
    analyzes trends, identifies root causes, and generates automated improvement
    suggestions.
    """
    
    def __init__(self, data_dir: str = "~/vy_data/outcomes"):
        """
        Initialize the Success/Failure Tracker.
        
        Args:
            data_dir: Directory to store outcome data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.executions_file = os.path.join(self.data_dir, "task_executions.jsonl")
        self.metrics_file = os.path.join(self.data_dir, "success_metrics.json")
        self.suggestions_file = os.path.join(self.data_dir, "improvement_suggestions.json")
        
        self._lock = threading.Lock()
        self._buffer: List[TaskExecution] = []
        self._buffer_size = 50
        
        # Cache for metrics
        self._metrics_cache: Dict[str, SuccessMetrics] = {}
        self._cache_timestamp = None
        self._cache_ttl = 300  # 5 minutes
        
    def record_execution(self,
                        task_id: str,
                        task_type: str,
                        outcome: TaskOutcome,
                        start_time: datetime,
                        end_time: datetime,
                        error_message: Optional[str] = None,
                        failure_category: Optional[FailureCategory] = None,
                        user_satisfaction: Optional[int] = None,
                        retry_count: int = 0,
                        context: Optional[Dict[str, Any]] = None) -> None:
        """
        Record a task execution.
        
        Args:
            task_id: Unique identifier for this execution
            task_type: Type/category of task
            outcome: Task outcome
            start_time: When task started
            end_time: When task ended
            error_message: Error message if failed
            failure_category: Category of failure
            user_satisfaction: User satisfaction rating (1-5)
            retry_count: Number of retries attempted
            context: Additional context data
        """
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        execution = TaskExecution(
            task_id=task_id,
            task_type=task_type,
            outcome=outcome,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            duration_ms=duration_ms,
            error_message=error_message,
            failure_category=failure_category,
            user_satisfaction=user_satisfaction,
            retry_count=retry_count,
            context=context
        )
        
        with self._lock:
            self._buffer.append(execution)
            if len(self._buffer) >= self._buffer_size:
                self._flush_buffer()
    
    def _flush_buffer(self) -> None:
        """Flush buffered executions to disk."""
        if not self._buffer:
            return
        
        try:
            with open(self.executions_file, 'a') as f:
                for execution in self._buffer:
                    f.write(json.dumps(execution.to_dict()) + '\n')
            self._buffer.clear()
            
            # Invalidate metrics cache
            self._cache_timestamp = None
            
        except Exception as e:
            print(f"Error flushing execution buffer: {e}")
    
    def flush(self) -> None:
        """Manually flush buffer to disk."""
        with self._lock:
            self._flush_buffer()
    
    def load_executions(self,
                       task_type: Optional[str] = None,
                       since: Optional[datetime] = None,
                       limit: Optional[int] = None) -> List[TaskExecution]:
        """
        Load task executions from disk.
        
        Args:
            task_type: Filter by task type
            since: Only load executions after this time
            limit: Maximum number of executions to load
            
        Returns:
            List of task executions
        """
        executions = []
        
        if not os.path.exists(self.executions_file):
            return executions
        
        try:
            with open(self.executions_file, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    data = json.loads(line)
                    execution = TaskExecution.from_dict(data)
                    
                    # Apply filters
                    if task_type and execution.task_type != task_type:
                        continue
                    
                    if since:
                        exec_time = datetime.fromisoformat(execution.start_time)
                        if exec_time < since:
                            continue
                    
                    executions.append(execution)
                    
                    if limit and len(executions) >= limit:
                        break
            
        except Exception as e:
            print(f"Error loading executions: {e}")
        
        return executions
    
    def calculate_metrics(self, task_type: Optional[str] = None,
                         time_window_days: int = 30) -> Dict[str, SuccessMetrics]:
        """
        Calculate success metrics for task types.
        
        Args:
            task_type: Calculate for specific task type (None for all)
            time_window_days: Number of days to analyze
            
        Returns:
            Dictionary mapping task types to their metrics
        """
        # Check cache
        if (self._cache_timestamp and 
            (datetime.now() - self._cache_timestamp).seconds < self._cache_ttl and
            not task_type):  # Only use cache for all-tasks queries
            return self._metrics_cache
        
        since = datetime.now() - timedelta(days=time_window_days)
        executions = self.load_executions(task_type=task_type, since=since)
        
        # Group by task type
        by_type: Dict[str, List[TaskExecution]] = defaultdict(list)
        for execution in executions:
            by_type[execution.task_type].append(execution)
        
        metrics = {}
        for ttype, execs in by_type.items():
            metrics[ttype] = self._calculate_task_metrics(ttype, execs, time_window_days)
        
        # Update cache
        if not task_type:
            self._metrics_cache = metrics
            self._cache_timestamp = datetime.now()
        
        return metrics
    
    def _calculate_task_metrics(self, task_type: str,
                               executions: List[TaskExecution],
                               time_window_days: int) -> SuccessMetrics:
        """
        Calculate metrics for a specific task type.
        
        Args:
            task_type: Task type to analyze
            executions: List of executions for this task type
            time_window_days: Time window for trend analysis
            
        Returns:
            Success metrics for the task type
        """
        total = len(executions)
        successful = sum(1 for e in executions if e.outcome == TaskOutcome.SUCCESS)
        failed = sum(1 for e in executions if e.outcome == TaskOutcome.FAILURE)
        partial = sum(1 for e in executions if e.outcome == TaskOutcome.PARTIAL)
        
        success_rate = (successful / total * 100) if total > 0 else 0.0
        
        # Average duration
        durations = [e.duration_ms for e in executions]
        avg_duration = statistics.mean(durations) if durations else 0.0
        
        # Average satisfaction
        satisfactions = [e.user_satisfaction for e in executions 
                        if e.user_satisfaction is not None]
        avg_satisfaction = statistics.mean(satisfactions) if satisfactions else None
        
        # Failure categories
        failure_cats = Counter()
        for e in executions:
            if e.failure_category:
                failure_cats[e.failure_category.value] += 1
        
        # Calculate trend
        trend = self._calculate_trend(executions, time_window_days)
        
        return SuccessMetrics(
            task_type=task_type,
            total_executions=total,
            successful=successful,
            failed=failed,
            partial=partial,
            success_rate=success_rate,
            avg_duration_ms=avg_duration,
            avg_satisfaction=avg_satisfaction,
            failure_categories=dict(failure_cats),
            trend=trend
        )
    
    def _calculate_trend(self, executions: List[TaskExecution],
                        time_window_days: int) -> str:
        """
        Calculate success rate trend.
        
        Args:
            executions: List of executions
            time_window_days: Time window to analyze
            
        Returns:
            Trend description: "improving", "declining", or "stable"
        """
        if len(executions) < 10:
            return "stable"  # Not enough data
        
        # Split into two halves
        mid = len(executions) // 2
        first_half = executions[:mid]
        second_half = executions[mid:]
        
        # Calculate success rates
        first_success_rate = sum(1 for e in first_half 
                                if e.outcome == TaskOutcome.SUCCESS) / len(first_half)
        second_success_rate = sum(1 for e in second_half 
                                 if e.outcome == TaskOutcome.SUCCESS) / len(second_half)
        
        # Determine trend
        diff = second_success_rate - first_success_rate
        
        if diff > 0.1:  # 10% improvement
            return "improving"
        elif diff < -0.1:  # 10% decline
            return "declining"
        else:
            return "stable"
    
    def analyze_failures(self, task_type: Optional[str] = None,
                        time_window_days: int = 30) -> Dict[str, Any]:
        """
        Perform root cause analysis on failures.
        
        Args:
            task_type: Analyze specific task type (None for all)
            time_window_days: Number of days to analyze
            
        Returns:
            Failure analysis report
        """
        since = datetime.now() - timedelta(days=time_window_days)
        executions = self.load_executions(task_type=task_type, since=since)
        
        failures = [e for e in executions if e.outcome == TaskOutcome.FAILURE]
        
        if not failures:
            return {
                "total_failures": 0,
                "failure_rate": 0.0,
                "categories": {},
                "common_errors": [],
                "high_retry_tasks": []
            }
        
        # Failure categories
        categories = Counter()
        for f in failures:
            if f.failure_category:
                categories[f.failure_category.value] += 1
        
        # Common error messages
        error_messages = Counter()
        for f in failures:
            if f.error_message:
                # Normalize error message (first 100 chars)
                normalized = f.error_message[:100]
                error_messages[normalized] += 1
        
        # High retry tasks
        high_retry = [e for e in failures if e.retry_count > 2]
        high_retry_types = Counter(e.task_type for e in high_retry)
        
        failure_rate = len(failures) / len(executions) * 100 if executions else 0.0
        
        return {
            "total_failures": len(failures),
            "failure_rate": failure_rate,
            "categories": dict(categories.most_common()),
            "common_errors": [{
                "error": msg,
                "count": count
            } for msg, count in error_messages.most_common(10)],
            "high_retry_tasks": dict(high_retry_types.most_common(5))
        }
    
    def generate_improvement_suggestions(self,
                                        time_window_days: int = 30) -> List[ImprovementSuggestion]:
        """
        Generate automated improvement suggestions based on performance data.
        
        Args:
            time_window_days: Number of days to analyze
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        # Get metrics and failure analysis
        metrics = self.calculate_metrics(time_window_days=time_window_days)
        failure_analysis = self.analyze_failures(time_window_days=time_window_days)
        
        # Suggestion 1: Low success rate tasks
        for task_type, metric in metrics.items():
            if metric.success_rate < 70 and metric.total_executions >= 10:
                suggestion = ImprovementSuggestion(
                    suggestion_id=self._generate_suggestion_id(task_type, "low_success"),
                    task_type=task_type,
                    priority="high",
                    category="reliability",
                    description=f"Improve success rate for {task_type}",
                    rationale=f"Current success rate is {metric.success_rate:.1f}%, "
                             f"which is below the 70% threshold. "
                             f"{metric.failed} out of {metric.total_executions} executions failed.",
                    expected_impact="Increase success rate by 20-30%",
                    implementation_effort="medium",
                    created_at=datetime.now().isoformat()
                )
                suggestions.append(suggestion)
        
        # Suggestion 2: Declining trends
        for task_type, metric in metrics.items():
            if metric.trend == "declining" and metric.total_executions >= 20:
                suggestion = ImprovementSuggestion(
                    suggestion_id=self._generate_suggestion_id(task_type, "declining"),
                    task_type=task_type,
                    priority="high",
                    category="reliability",
                    description=f"Address declining performance for {task_type}",
                    rationale=f"Success rate is declining. Current rate: {metric.success_rate:.1f}%. "
                             f"Investigate recent changes or environmental factors.",
                    expected_impact="Stabilize and improve success rate",
                    implementation_effort="medium",
                    created_at=datetime.now().isoformat()
                )
                suggestions.append(suggestion)
        
        # Suggestion 3: Slow tasks
        for task_type, metric in metrics.items():
            if metric.avg_duration_ms > 5000 and metric.total_executions >= 10:  # > 5 seconds
                suggestion = ImprovementSuggestion(
                    suggestion_id=self._generate_suggestion_id(task_type, "slow"),
                    task_type=task_type,
                    priority="medium",
                    category="performance",
                    description=f"Optimize performance for {task_type}",
                    rationale=f"Average execution time is {metric.avg_duration_ms:.0f}ms, "
                             f"which is above the 5000ms threshold. Consider caching, "
                             f"parallelization, or algorithm optimization.",
                    expected_impact="Reduce execution time by 30-50%",
                    implementation_effort="medium",
                    created_at=datetime.now().isoformat()
                )
                suggestions.append(suggestion)
        
        # Suggestion 4: Low satisfaction
        for task_type, metric in metrics.items():
            if metric.avg_satisfaction and metric.avg_satisfaction < 3.0:
                suggestion = ImprovementSuggestion(
                    suggestion_id=self._generate_suggestion_id(task_type, "low_satisfaction"),
                    task_type=task_type,
                    priority="high",
                    category="usability",
                    description=f"Improve user experience for {task_type}",
                    rationale=f"Average user satisfaction is {metric.avg_satisfaction:.1f}/5.0, "
                             f"which indicates poor user experience. Gather user feedback "
                             f"and identify pain points.",
                    expected_impact="Increase user satisfaction by 1-2 points",
                    implementation_effort="high",
                    created_at=datetime.now().isoformat()
                )
                suggestions.append(suggestion)
        
        # Suggestion 5: Common failure categories
        if failure_analysis['categories']:
            top_category = max(failure_analysis['categories'].items(), key=lambda x: x[1])
            category_name, count = top_category
            
            if count >= 5:  # At least 5 failures in this category
                suggestion = ImprovementSuggestion(
                    suggestion_id=self._generate_suggestion_id("system", category_name),
                    task_type="all",
                    priority="high",
                    category="reliability",
                    description=f"Address {category_name} failures",
                    rationale=f"{count} failures categorized as {category_name}. "
                             f"This is the most common failure category. "
                             f"Implement targeted fixes for this issue.",
                    expected_impact="Reduce failures by 20-40%",
                    implementation_effort="medium",
                    created_at=datetime.now().isoformat()
                )
                suggestions.append(suggestion)
        
        # Save suggestions
        self._save_suggestions(suggestions)
        
        return suggestions
    
    def _generate_suggestion_id(self, task_type: str, issue_type: str) -> str:
        """Generate unique suggestion ID."""
        data = f"{task_type}:{issue_type}:{datetime.now().date()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _save_suggestions(self, suggestions: List[ImprovementSuggestion]) -> None:
        """Save improvement suggestions to disk."""
        try:
            data = [asdict(s) for s in suggestions]
            with open(self.suggestions_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving suggestions: {e}")
    
    def load_suggestions(self) -> List[ImprovementSuggestion]:
        """Load improvement suggestions from disk."""
        if not os.path.exists(self.suggestions_file):
            return []
        
        try:
            with open(self.suggestions_file, 'r') as f:
                data = json.load(f)
            return [ImprovementSuggestion(**item) for item in data]
        except Exception as e:
            print(f"Error loading suggestions: {e}")
            return []
    
    def get_performance_report(self, time_window_days: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.
        
        Args:
            time_window_days: Number of days to analyze
            
        Returns:
            Performance report dictionary
        """
        metrics = self.calculate_metrics(time_window_days=time_window_days)
        failure_analysis = self.analyze_failures(time_window_days=time_window_days)
        suggestions = self.generate_improvement_suggestions(time_window_days=time_window_days)
        
        # Overall statistics
        total_executions = sum(m.total_executions for m in metrics.values())
        total_successful = sum(m.successful for m in metrics.values())
        overall_success_rate = (total_successful / total_executions * 100 
                               if total_executions > 0 else 0.0)
        
        # Best and worst performing tasks
        sorted_metrics = sorted(metrics.values(), 
                               key=lambda m: m.success_rate, 
                               reverse=True)
        best_tasks = sorted_metrics[:5] if len(sorted_metrics) >= 5 else sorted_metrics
        worst_tasks = sorted_metrics[-5:] if len(sorted_metrics) >= 5 else []
        
        return {
            "report_date": datetime.now().isoformat(),
            "time_window_days": time_window_days,
            "overall_statistics": {
                "total_executions": total_executions,
                "success_rate": overall_success_rate,
                "total_task_types": len(metrics)
            },
            "best_performing_tasks": [
                {
                    "task_type": m.task_type,
                    "success_rate": m.success_rate,
                    "executions": m.total_executions
                } for m in best_tasks
            ],
            "worst_performing_tasks": [
                {
                    "task_type": m.task_type,
                    "success_rate": m.success_rate,
                    "executions": m.total_executions
                } for m in worst_tasks
            ],
            "failure_analysis": failure_analysis,
            "improvement_suggestions": [
                {
                    "priority": s.priority,
                    "category": s.category,
                    "description": s.description,
                    "task_type": s.task_type
                } for s in suggestions
            ],
            "metrics_by_task": {
                task_type: {
                    "success_rate": m.success_rate,
                    "total_executions": m.total_executions,
                    "avg_duration_ms": m.avg_duration_ms,
                    "trend": m.trend
                } for task_type, m in metrics.items()
            }
        }


if __name__ == "__main__":
    # Example usage
    tracker = SuccessFailureTracker()
    
    # Record some sample executions
    print("Recording sample task executions...")
    
    # Successful task
    tracker.record_execution(
        task_id="task_001",
        task_type="data_processing",
        outcome=TaskOutcome.SUCCESS,
        start_time=datetime.now() - timedelta(seconds=5),
        end_time=datetime.now(),
        user_satisfaction=4
    )
    
    # Failed task
    tracker.record_execution(
        task_id="task_002",
        task_type="data_processing",
        outcome=TaskOutcome.FAILURE,
        start_time=datetime.now() - timedelta(seconds=3),
        end_time=datetime.now(),
        error_message="Database connection timeout",
        failure_category=FailureCategory.TIMEOUT_ERROR,
        retry_count=2
    )
    
    tracker.flush()
    
    # Generate report
    print("\nGenerating performance report...")
    report = tracker.get_performance_report(time_window_days=7)
    print(json.dumps(report, indent=2))
