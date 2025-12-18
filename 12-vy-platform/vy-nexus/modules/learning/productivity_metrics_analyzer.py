#!/usr/bin/env python3
"""
Productivity Metrics Analyzer for VY-NEXUS

This module analyzes productivity metrics, identifies bottlenecks, and generates
actionable insights to improve user productivity and system efficiency.

Features:
- Time tracking and analysis
- Task completion rate monitoring
- Workflow efficiency measurement
- Bottleneck identification
- Productivity trend analysis
- Context-aware metrics
- Personalized productivity insights
- Actionable recommendations

Author: VY-NEXUS Self-Evolving AI System
Date: December 15, 2025
"""

import json
import os
import threading
from datetime import datetime, timedelta, time as dt_time
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict, field
from enum import Enum
import statistics


class ProductivityPeriod(Enum):
    """Time periods for productivity analysis."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TaskCategory(Enum):
    """Categories of tasks for analysis."""
    DEVELOPMENT = "development"
    COMMUNICATION = "communication"
    PLANNING = "planning"
    LEARNING = "learning"
    MAINTENANCE = "maintenance"
    CREATIVE = "creative"
    ADMINISTRATIVE = "administrative"
    OTHER = "other"


@dataclass
class TimeEntry:
    """Represents a time tracking entry."""
    entry_id: str
    task_name: str
    task_category: TaskCategory
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    completed: bool = False
    interruptions: int = 0
    context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['task_category'] = self.task_category.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeEntry':
        """Create from dictionary."""
        data['task_category'] = TaskCategory(data['task_category'])
        return cls(**data)


@dataclass
class ProductivityMetrics:
    """Aggregated productivity metrics."""
    period: str
    total_time_seconds: float
    productive_time_seconds: float
    tasks_completed: int
    tasks_started: int
    completion_rate: float
    avg_task_duration_seconds: float
    interruption_count: int
    peak_productivity_hour: Optional[int]
    productivity_score: float  # 0-100
    category_breakdown: Dict[str, float]
    

@dataclass
class ProductivityInsight:
    """Productivity insight or recommendation."""
    insight_id: str
    category: str  # "bottleneck", "opportunity", "trend", "recommendation"
    priority: str  # "high", "medium", "low"
    title: str
    description: str
    data_points: Dict[str, Any]
    actionable_steps: List[str]
    expected_impact: str
    created_at: str


class ProductivityMetricsAnalyzer:
    """
    Analyzes productivity metrics and generates insights.
    
    This class tracks time spent on tasks, analyzes productivity patterns,
    identifies bottlenecks, and generates actionable recommendations.
    """
    
    def __init__(self, data_dir: str = "~/vy_data/productivity"):
        """
        Initialize the Productivity Metrics Analyzer.
        
        Args:
            data_dir: Directory to store productivity data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.entries_file = os.path.join(self.data_dir, "time_entries.jsonl")
        self.metrics_file = os.path.join(self.data_dir, "metrics.json")
        self.insights_file = os.path.join(self.data_dir, "insights.json")
        
        self._lock = threading.Lock()
        self._active_entries: Dict[str, TimeEntry] = {}
        self._entry_buffer: List[TimeEntry] = []
        self._buffer_size = 50
        
        # Configuration
        self.work_hours_start = 9  # 9 AM
        self.work_hours_end = 17  # 5 PM
        self.min_task_duration = 60  # 1 minute minimum
        self.max_task_duration = 14400  # 4 hours maximum
        
    def start_task(self,
                   task_name: str,
                   task_category: TaskCategory,
                   context: Optional[Dict[str, Any]] = None) -> str:
        """
        Start tracking a new task.
        
        Args:
            task_name: Name of the task
            task_category: Category of the task
            context: Additional context
            
        Returns:
            Entry ID
        """
        with self._lock:
            entry_id = self._generate_entry_id(task_name)
            
            entry = TimeEntry(
                entry_id=entry_id,
                task_name=task_name,
                task_category=task_category,
                start_time=datetime.now().isoformat(),
                context=context
            )
            
            self._active_entries[entry_id] = entry
            
            return entry_id
    
    def end_task(self,
                entry_id: str,
                completed: bool = True,
                interruptions: int = 0) -> bool:
        """
        End tracking a task.
        
        Args:
            entry_id: Entry ID to end
            completed: Whether task was completed
            interruptions: Number of interruptions
            
        Returns:
            True if successful
        """
        with self._lock:
            if entry_id not in self._active_entries:
                return False
            
            entry = self._active_entries[entry_id]
            entry.end_time = datetime.now().isoformat()
            entry.completed = completed
            entry.interruptions = interruptions
            
            # Calculate duration
            start = datetime.fromisoformat(entry.start_time)
            end = datetime.fromisoformat(entry.end_time)
            entry.duration_seconds = (end - start).total_seconds()
            
            # Move to buffer
            self._entry_buffer.append(entry)
            del self._active_entries[entry_id]
            
            # Auto-flush if buffer is full
            if len(self._entry_buffer) >= self._buffer_size:
                self._flush_buffer()
            
            return True
    
    def record_interruption(self, entry_id: str) -> bool:
        """
        Record an interruption for an active task.
        
        Args:
            entry_id: Entry ID
            
        Returns:
            True if successful
        """
        with self._lock:
            if entry_id in self._active_entries:
                self._active_entries[entry_id].interruptions += 1
                return True
            return False
    
    def _generate_entry_id(self, task_name: str) -> str:
        """Generate unique entry ID."""
        import hashlib
        data = f"{task_name}:{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _flush_buffer(self) -> None:
        """Flush entry buffer to disk."""
        if not self._entry_buffer:
            return
        
        try:
            with open(self.entries_file, 'a') as f:
                for entry in self._entry_buffer:
                    f.write(json.dumps(entry.to_dict()) + '\n')
            self._entry_buffer.clear()
        except Exception as e:
            print(f"Error flushing entry buffer: {e}")
    
    def flush(self) -> None:
        """Manually flush buffer to disk."""
        with self._lock:
            self._flush_buffer()
    
    def load_entries(self,
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None,
                    category: Optional[TaskCategory] = None) -> List[TimeEntry]:
        """
        Load time entries from disk.
        
        Args:
            start_date: Filter entries after this date
            end_date: Filter entries before this date
            category: Filter by category
            
        Returns:
            List of time entries
        """
        entries = []
        
        if not os.path.exists(self.entries_file):
            return entries
        
        try:
            with open(self.entries_file, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    data = json.loads(line)
                    entry = TimeEntry.from_dict(data)
                    
                    # Apply filters
                    if start_date:
                        entry_time = datetime.fromisoformat(entry.start_time)
                        if entry_time < start_date:
                            continue
                    
                    if end_date:
                        entry_time = datetime.fromisoformat(entry.start_time)
                        if entry_time > end_date:
                            continue
                    
                    if category and entry.task_category != category:
                        continue
                    
                    entries.append(entry)
        
        except Exception as e:
            print(f"Error loading entries: {e}")
        
        return entries
    
    def calculate_metrics(self,
                         period: ProductivityPeriod = ProductivityPeriod.DAILY,
                         date: Optional[datetime] = None) -> ProductivityMetrics:
        """
        Calculate productivity metrics for a period.
        
        Args:
            period: Time period to analyze
            date: Specific date (defaults to today)
            
        Returns:
            Productivity metrics
        """
        if date is None:
            date = datetime.now()
        
        # Determine date range
        if period == ProductivityPeriod.HOURLY:
            start_date = date.replace(minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(hours=1)
        elif period == ProductivityPeriod.DAILY:
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif period == ProductivityPeriod.WEEKLY:
            start_date = date - timedelta(days=date.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=7)
        else:  # MONTHLY
            start_date = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if date.month == 12:
                end_date = start_date.replace(year=date.year + 1, month=1)
            else:
                end_date = start_date.replace(month=date.month + 1)
        
        # Load entries for period
        entries = self.load_entries(start_date=start_date, end_date=end_date)
        
        if not entries:
            return ProductivityMetrics(
                period=period.value,
                total_time_seconds=0,
                productive_time_seconds=0,
                tasks_completed=0,
                tasks_started=0,
                completion_rate=0.0,
                avg_task_duration_seconds=0.0,
                interruption_count=0,
                peak_productivity_hour=None,
                productivity_score=0.0,
                category_breakdown={}
            )
        
        # Calculate metrics
        total_time = sum(e.duration_seconds or 0 for e in entries)
        productive_time = sum(
            e.duration_seconds or 0 for e in entries
            if e.completed and e.interruptions < 3
        )
        
        tasks_completed = sum(1 for e in entries if e.completed)
        tasks_started = len(entries)
        completion_rate = (tasks_completed / tasks_started * 100) if tasks_started > 0 else 0.0
        
        durations = [e.duration_seconds for e in entries if e.duration_seconds]
        avg_duration = statistics.mean(durations) if durations else 0.0
        
        interruption_count = sum(e.interruptions for e in entries)
        
        # Find peak productivity hour
        hourly_productivity = defaultdict(float)
        for entry in entries:
            if entry.completed and entry.duration_seconds:
                hour = datetime.fromisoformat(entry.start_time).hour
                hourly_productivity[hour] += entry.duration_seconds
        
        peak_hour = max(hourly_productivity.items(), key=lambda x: x[1])[0] if hourly_productivity else None
        
        # Calculate productivity score (0-100)
        score = 0.0
        score += min(40, completion_rate * 0.4)  # Up to 40 points for completion rate
        score += min(30, (productive_time / total_time * 100) * 0.3) if total_time > 0 else 0  # Up to 30 points
        score += min(20, max(0, 20 - (interruption_count / tasks_started * 20))) if tasks_started > 0 else 0  # Up to 20 points
        score += 10 if tasks_completed > 0 else 0  # 10 points for any completion
        
        # Category breakdown
        category_time = defaultdict(float)
        for entry in entries:
            if entry.duration_seconds:
                category_time[entry.task_category.value] += entry.duration_seconds
        
        return ProductivityMetrics(
            period=period.value,
            total_time_seconds=total_time,
            productive_time_seconds=productive_time,
            tasks_completed=tasks_completed,
            tasks_started=tasks_started,
            completion_rate=completion_rate,
            avg_task_duration_seconds=avg_duration,
            interruption_count=interruption_count,
            peak_productivity_hour=peak_hour,
            productivity_score=score,
            category_breakdown=dict(category_time)
        )
    
    def analyze_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze productivity trends over time.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Trend analysis
        """
        daily_scores = []
        daily_completion_rates = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            metrics = self.calculate_metrics(ProductivityPeriod.DAILY, date)
            daily_scores.append(metrics.productivity_score)
            daily_completion_rates.append(metrics.completion_rate)
        
        # Reverse to chronological order
        daily_scores.reverse()
        daily_completion_rates.reverse()
        
        # Calculate trends
        if len(daily_scores) >= 7:
            recent_avg = statistics.mean(daily_scores[-7:])
            older_avg = statistics.mean(daily_scores[:7])
            trend = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "days_analyzed": days,
            "avg_productivity_score": statistics.mean(daily_scores) if daily_scores else 0,
            "avg_completion_rate": statistics.mean(daily_completion_rates) if daily_completion_rates else 0,
            "trend": trend,
            "best_day_score": max(daily_scores) if daily_scores else 0,
            "worst_day_score": min(daily_scores) if daily_scores else 0,
            "consistency_score": 100 - (statistics.stdev(daily_scores) if len(daily_scores) > 1 else 0)
        }
    
    def identify_bottlenecks(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Identify productivity bottlenecks.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of identified bottlenecks
        """
        bottlenecks = []
        
        start_date = datetime.now() - timedelta(days=days)
        entries = self.load_entries(start_date=start_date)
        
        if not entries:
            return bottlenecks
        
        # Bottleneck 1: High interruption tasks
        high_interruption_tasks = defaultdict(list)
        for entry in entries:
            if entry.interruptions > 2:
                high_interruption_tasks[entry.task_name].append(entry.interruptions)
        
        for task_name, interruptions in high_interruption_tasks.items():
            if len(interruptions) >= 3:  # At least 3 occurrences
                bottlenecks.append({
                    "type": "high_interruptions",
                    "task": task_name,
                    "avg_interruptions": statistics.mean(interruptions),
                    "occurrences": len(interruptions),
                    "severity": "high"
                })
        
        # Bottleneck 2: Low completion rate tasks
        task_completion = defaultdict(lambda: {"started": 0, "completed": 0})
        for entry in entries:
            task_completion[entry.task_name]["started"] += 1
            if entry.completed:
                task_completion[entry.task_name]["completed"] += 1
        
        for task_name, stats in task_completion.items():
            if stats["started"] >= 3:  # At least 3 attempts
                completion_rate = stats["completed"] / stats["started"] * 100
                if completion_rate < 50:
                    bottlenecks.append({
                        "type": "low_completion_rate",
                        "task": task_name,
                        "completion_rate": completion_rate,
                        "attempts": stats["started"],
                        "severity": "high" if completion_rate < 30 else "medium"
                    })
        
        # Bottleneck 3: Unusually long tasks
        task_durations = defaultdict(list)
        for entry in entries:
            if entry.duration_seconds:
                task_durations[entry.task_name].append(entry.duration_seconds)
        
        for task_name, durations in task_durations.items():
            if len(durations) >= 3:
                avg_duration = statistics.mean(durations)
                if avg_duration > 7200:  # More than 2 hours
                    bottlenecks.append({
                        "type": "long_duration",
                        "task": task_name,
                        "avg_duration_hours": avg_duration / 3600,
                        "occurrences": len(durations),
                        "severity": "medium"
                    })
        
        return bottlenecks
    
    def generate_insights(self, days: int = 7) -> List[ProductivityInsight]:
        """
        Generate productivity insights and recommendations.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of insights
        """
        insights = []
        
        # Get metrics and trends
        current_metrics = self.calculate_metrics(ProductivityPeriod.DAILY)
        trends = self.analyze_trends(days=days)
        bottlenecks = self.identify_bottlenecks(days=days)
        
        # Insight 1: Low productivity score
        if current_metrics.productivity_score < 50:
            insights.append(ProductivityInsight(
                insight_id=self._generate_entry_id("low_productivity"),
                category="opportunity",
                priority="high",
                title="Low Productivity Score Detected",
                description=f"Your productivity score is {current_metrics.productivity_score:.1f}/100, "
                           f"which is below the recommended threshold of 50.",
                data_points={
                    "current_score": current_metrics.productivity_score,
                    "completion_rate": current_metrics.completion_rate,
                    "interruptions": current_metrics.interruption_count
                },
                actionable_steps=[
                    "Focus on completing started tasks before beginning new ones",
                    "Minimize interruptions during work sessions",
                    "Break large tasks into smaller, manageable chunks"
                ],
                expected_impact="20-30% improvement in productivity score",
                created_at=datetime.now().isoformat()
            ))
        
        # Insight 2: Declining trend
        if trends["trend"] == "declining":
            insights.append(ProductivityInsight(
                insight_id=self._generate_entry_id("declining_trend"),
                category="trend",
                priority="high",
                title="Declining Productivity Trend",
                description=f"Your productivity has been declining over the past {days} days.",
                data_points={
                    "trend": trends["trend"],
                    "avg_score": trends["avg_productivity_score"]
                },
                actionable_steps=[
                    "Review recent changes in workflow or environment",
                    "Consider taking breaks to prevent burnout",
                    "Identify and eliminate time-wasting activities"
                ],
                expected_impact="Reverse declining trend within 1-2 weeks",
                created_at=datetime.now().isoformat()
            ))
        
        # Insight 3: Bottlenecks
        for bottleneck in bottlenecks[:3]:  # Top 3 bottlenecks
            if bottleneck["type"] == "high_interruptions":
                insights.append(ProductivityInsight(
                    insight_id=self._generate_entry_id(f"bottleneck_{bottleneck['task']}"),
                    category="bottleneck",
                    priority="high",
                    title=f"High Interruptions: {bottleneck['task']}",
                    description=f"Task '{bottleneck['task']}' experiences an average of "
                               f"{bottleneck['avg_interruptions']:.1f} interruptions per session.",
                    data_points=bottleneck,
                    actionable_steps=[
                        "Schedule dedicated time blocks for this task",
                        "Use 'Do Not Disturb' mode during work sessions",
                        "Communicate availability to team members"
                    ],
                    expected_impact="50% reduction in interruptions",
                    created_at=datetime.now().isoformat()
                ))
        
        # Insight 4: Peak productivity time
        if current_metrics.peak_productivity_hour is not None:
            insights.append(ProductivityInsight(
                insight_id=self._generate_entry_id("peak_time"),
                category="recommendation",
                priority="medium",
                title="Optimize Task Scheduling",
                description=f"Your peak productivity hour is {current_metrics.peak_productivity_hour}:00. "
                           f"Schedule important tasks during this time.",
                data_points={
                    "peak_hour": current_metrics.peak_productivity_hour
                },
                actionable_steps=[
                    f"Schedule high-priority tasks around {current_metrics.peak_productivity_hour}:00",
                    "Reserve low-priority tasks for off-peak hours",
                    "Protect peak hours from meetings and interruptions"
                ],
                expected_impact="15-25% improvement in task completion",
                created_at=datetime.now().isoformat()
            ))
        
        return insights
    
    def get_productivity_report(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate comprehensive productivity report.
        
        Args:
            days: Number of days to include
            
        Returns:
            Productivity report
        """
        current_metrics = self.calculate_metrics(ProductivityPeriod.DAILY)
        weekly_metrics = self.calculate_metrics(ProductivityPeriod.WEEKLY)
        trends = self.analyze_trends(days=days)
        bottlenecks = self.identify_bottlenecks(days=days)
        insights = self.generate_insights(days=days)
        
        return {
            "report_date": datetime.now().isoformat(),
            "period_days": days,
            "current_day_metrics": asdict(current_metrics),
            "weekly_metrics": asdict(weekly_metrics),
            "trends": trends,
            "bottlenecks": bottlenecks,
            "insights": [asdict(i) for i in insights],
            "summary": {
                "productivity_score": current_metrics.productivity_score,
                "completion_rate": current_metrics.completion_rate,
                "trend": trends["trend"],
                "bottleneck_count": len(bottlenecks),
                "recommendation_count": len(insights)
            }
        }


if __name__ == "__main__":
    # Example usage
    analyzer = ProductivityMetricsAnalyzer()
    
    print("Starting task tracking...")
    
    # Start a task
    entry_id = analyzer.start_task(
        task_name="Code Review",
        task_category=TaskCategory.DEVELOPMENT,
        context={"project": "vy-nexus"}
    )
    
    print(f"Task started: {entry_id}")
    
    # Simulate some work time
    import time
    time.sleep(2)
    
    # End the task
    analyzer.end_task(entry_id, completed=True, interruptions=0)
    analyzer.flush()
    
    print("\nGenerating productivity report...")
    report = analyzer.get_productivity_report(days=7)
    print(json.dumps(report, indent=2))
