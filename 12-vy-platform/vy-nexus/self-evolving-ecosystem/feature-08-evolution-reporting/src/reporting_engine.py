"""Evolution Reporting System - Generates comprehensive reports on system evolution.

This module provides reporting capabilities for the self-evolving AI ecosystem,
including morning optimization summaries, evening learning reports, metrics
dashboards, improvement tracking, and daily summaries.

Components:
- MorningOptimizationReporter: Reports overnight improvements
- EveningLearningReporter: Summarizes daily learning
- MetricsDashboard: Real-time metrics visualization
- ImprovementTracker: Tracks improvements over time
- DailySummaryGenerator: Generates comprehensive daily reports
- EvolutionReportingEngine: Orchestrates all reporting
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict


class ReportType(Enum):
    """Types of reports that can be generated."""
    MORNING_OPTIMIZATION = "morning_optimization"
    EVENING_LEARNING = "evening_learning"
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_SUMMARY = "weekly_summary"
    METRICS_DASHBOARD = "metrics_dashboard"
    IMPROVEMENT_HISTORY = "improvement_history"


class ImprovementCategory(Enum):
    """Categories of improvements."""
    AUTOMATION = "automation"
    OPTIMIZATION = "optimization"
    LEARNING = "learning"
    FEATURE = "feature"
    BUG_FIX = "bug_fix"
    PERFORMANCE = "performance"
    SECURITY = "security"
    UX = "user_experience"


class MetricType(Enum):
    """Types of metrics tracked."""
    TASKS_AUTOMATED = "tasks_automated"
    TIME_SAVED = "time_saved"
    SUCCESS_RATE = "success_rate"
    USER_SATISFACTION = "user_satisfaction"
    SYSTEM_EFFICIENCY = "system_efficiency"
    KNOWLEDGE_ITEMS = "knowledge_items"
    ACTIVE_EXPERIMENTS = "active_experiments"
    IMPROVEMENTS_DEPLOYED = "improvements_deployed"


@dataclass
class Improvement:
    """Represents a system improvement."""
    id: str
    category: ImprovementCategory
    title: str
    description: str
    impact_score: float  # 0.0 to 1.0
    timestamp: datetime
    metrics: Dict[str, Any] = field(default_factory=dict)
    related_components: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'category': self.category.value,
            'title': self.title,
            'description': self.description,
            'impact_score': self.impact_score,
            'timestamp': self.timestamp.isoformat(),
            'metrics': self.metrics,
            'related_components': self.related_components
        }


@dataclass
class LearningEvent:
    """Represents a learning event."""
    id: str
    area: str  # technical, domain, behavioral, etc.
    topic: str
    insights: List[str]
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    source: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'area': self.area,
            'topic': self.topic,
            'insights': self.insights,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source
        }


@dataclass
class MetricSnapshot:
    """Snapshot of a metric at a point in time."""
    metric_type: MetricType
    value: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'metric_type': self.metric_type.value,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


class MorningOptimizationReporter:
    """Generates morning reports on overnight optimizations."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.overnight_improvements: List[Improvement] = []
        self.deployment_log: List[Dict[str, Any]] = []
        
    def record_improvement(self, improvement: Improvement) -> None:
        """Record an improvement made overnight."""
        self.overnight_improvements.append(improvement)
        if len(self.overnight_improvements) > self.max_history:
            self.overnight_improvements.pop(0)
    
    def record_deployment(self, component: str, version: str, 
                         changes: List[str]) -> None:
        """Record a deployment."""
        self.deployment_log.append({
            'component': component,
            'version': version,
            'changes': changes,
            'timestamp': datetime.now()
        })
        if len(self.deployment_log) > self.max_history:
            self.deployment_log.pop(0)
    
    def generate_morning_report(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate morning optimization report.
        
        Args:
            since: Only include improvements since this time (default: last 12 hours)
        
        Returns:
            Dictionary containing the morning report
        """
        if since is None:
            since = datetime.now() - timedelta(hours=12)
        
        recent_improvements = [
            imp for imp in self.overnight_improvements
            if imp.timestamp >= since
        ]
        
        recent_deployments = [
            dep for dep in self.deployment_log
            if dep['timestamp'] >= since
        ]
        
        # Categorize improvements
        by_category = defaultdict(list)
        for imp in recent_improvements:
            by_category[imp.category].append(imp)
        
        # Calculate total impact
        total_impact = sum(imp.impact_score for imp in recent_improvements)
        avg_impact = total_impact / len(recent_improvements) if recent_improvements else 0.0
        
        return {
            'report_type': ReportType.MORNING_OPTIMIZATION.value,
            'generated_at': datetime.now().isoformat(),
            'period_start': since.isoformat(),
            'period_end': datetime.now().isoformat(),
            'summary': {
                'total_improvements': len(recent_improvements),
                'total_deployments': len(recent_deployments),
                'total_impact': total_impact,
                'average_impact': avg_impact
            },
            'improvements_by_category': {
                cat.value: [imp.to_dict() for imp in imps]
                for cat, imps in by_category.items()
            },
            'deployments': recent_deployments,
            'top_improvements': [
                imp.to_dict() for imp in 
                sorted(recent_improvements, key=lambda x: x.impact_score, reverse=True)[:5]
            ]
        }


class EveningLearningReporter:
    """Generates evening reports on daily learning."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.learning_events: List[LearningEvent] = []
        self.experiments_conducted: List[Dict[str, Any]] = []
        self.patterns_discovered: List[Dict[str, Any]] = []
        
    def record_learning(self, event: LearningEvent) -> None:
        """Record a learning event."""
        self.learning_events.append(event)
        if len(self.learning_events) > self.max_history:
            self.learning_events.pop(0)
    
    def record_experiment(self, experiment_id: str, hypothesis: str,
                         results: Dict[str, Any]) -> None:
        """Record an experiment."""
        self.experiments_conducted.append({
            'id': experiment_id,
            'hypothesis': hypothesis,
            'results': results,
            'timestamp': datetime.now()
        })
        if len(self.experiments_conducted) > self.max_history:
            self.experiments_conducted.pop(0)
    
    def record_pattern(self, pattern_type: str, description: str,
                      confidence: float) -> None:
        """Record a discovered pattern."""
        self.patterns_discovered.append({
            'type': pattern_type,
            'description': description,
            'confidence': confidence,
            'timestamp': datetime.now()
        })
        if len(self.patterns_discovered) > self.max_history:
            self.patterns_discovered.pop(0)
    
    def generate_evening_report(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate evening learning report.
        
        Args:
            since: Only include learning since this time (default: last 12 hours)
        
        Returns:
            Dictionary containing the evening report
        """
        if since is None:
            since = datetime.now() - timedelta(hours=12)
        
        recent_learning = [
            event for event in self.learning_events
            if event.timestamp >= since
        ]
        
        recent_experiments = [
            exp for exp in self.experiments_conducted
            if exp['timestamp'] >= since
        ]
        
        recent_patterns = [
            pat for pat in self.patterns_discovered
            if pat['timestamp'] >= since
        ]
        
        # Group by area
        by_area = defaultdict(list)
        for event in recent_learning:
            by_area[event.area].append(event)
        
        # Calculate average confidence
        avg_confidence = (
            sum(e.confidence for e in recent_learning) / len(recent_learning)
            if recent_learning else 0.0
        )
        
        return {
            'report_type': ReportType.EVENING_LEARNING.value,
            'generated_at': datetime.now().isoformat(),
            'period_start': since.isoformat(),
            'period_end': datetime.now().isoformat(),
            'summary': {
                'total_learning_events': len(recent_learning),
                'total_experiments': len(recent_experiments),
                'total_patterns': len(recent_patterns),
                'average_confidence': avg_confidence
            },
            'learning_by_area': {
                area: [event.to_dict() for event in events]
                for area, events in by_area.items()
            },
            'experiments': recent_experiments,
            'patterns': recent_patterns,
            'top_insights': [
                event.to_dict() for event in
                sorted(recent_learning, key=lambda x: x.confidence, reverse=True)[:5]
            ]
        }


class MetricsDashboard:
    """Provides real-time metrics visualization."""
    
    def __init__(self, max_snapshots: int = 10000):
        self.max_snapshots = max_snapshots
        self.metric_snapshots: Dict[MetricType, List[MetricSnapshot]] = defaultdict(list)
        self.alerts: List[Dict[str, Any]] = []
        
    def record_metric(self, snapshot: MetricSnapshot) -> None:
        """Record a metric snapshot."""
        self.metric_snapshots[snapshot.metric_type].append(snapshot)
        if len(self.metric_snapshots[snapshot.metric_type]) > self.max_snapshots:
            self.metric_snapshots[snapshot.metric_type].pop(0)
    
    def add_alert(self, metric_type: MetricType, message: str,
                 severity: str = "info") -> None:
        """Add an alert."""
        self.alerts.append({
            'metric_type': metric_type.value,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now()
        })
        if len(self.alerts) > 100:
            self.alerts.pop(0)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current values for all metrics."""
        current = {}
        for metric_type, snapshots in self.metric_snapshots.items():
            if snapshots:
                latest = snapshots[-1]
                current[metric_type.value] = {
                    'value': latest.value,
                    'timestamp': latest.timestamp.isoformat(),
                    'metadata': latest.metadata
                }
        return current
    
    def get_metric_trend(self, metric_type: MetricType,
                        duration: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Get trend for a specific metric."""
        cutoff = datetime.now() - duration
        snapshots = [
            s for s in self.metric_snapshots.get(metric_type, [])
            if s.timestamp >= cutoff
        ]
        
        if not snapshots:
            return {'trend': 'no_data', 'change': 0.0}
        
        values = [s.value for s in snapshots]
        first_value = values[0]
        last_value = values[-1]
        change = last_value - first_value
        percent_change = (change / first_value * 100) if first_value != 0 else 0.0
        
        # Determine trend
        if abs(percent_change) < 5:
            trend = 'stable'
        elif percent_change > 0:
            trend = 'increasing'
        else:
            trend = 'decreasing'
        
        return {
            'trend': trend,
            'change': change,
            'percent_change': percent_change,
            'first_value': first_value,
            'last_value': last_value,
            'data_points': len(snapshots)
        }
    
    def generate_dashboard(self) -> Dict[str, Any]:
        """Generate complete metrics dashboard."""
        return {
            'report_type': ReportType.METRICS_DASHBOARD.value,
            'generated_at': datetime.now().isoformat(),
            'current_metrics': self.get_current_metrics(),
            'trends_24h': {
                metric_type.value: self.get_metric_trend(metric_type)
                for metric_type in MetricType
            },
            'recent_alerts': self.alerts[-10:],
            'total_data_points': sum(
                len(snapshots) for snapshots in self.metric_snapshots.values()
            )
        }


class ImprovementTracker:
    """Tracks all improvements over time."""
    
    def __init__(self, max_history: int = 5000):
        self.max_history = max_history
        self.improvements: List[Improvement] = []
        self.milestones: List[Dict[str, Any]] = []
        
    def track_improvement(self, improvement: Improvement) -> None:
        """Track an improvement."""
        self.improvements.append(improvement)
        if len(self.improvements) > self.max_history:
            self.improvements.pop(0)
        
        # Check for milestones
        self._check_milestones()
    
    def add_milestone(self, title: str, description: str,
                     achievement_date: Optional[datetime] = None) -> None:
        """Add a milestone."""
        self.milestones.append({
            'title': title,
            'description': description,
            'achievement_date': achievement_date or datetime.now(),
            'total_improvements': len(self.improvements)
        })
    
    def _check_milestones(self) -> None:
        """Check if any milestones have been reached."""
        total = len(self.improvements)
        milestone_counts = [100, 500, 1000, 2500, 5000]
        
        for count in milestone_counts:
            if total == count:
                self.add_milestone(
                    f"{count} Improvements",
                    f"Reached {count} total improvements"
                )
    
    def get_improvement_history(self, duration: timedelta = timedelta(days=30)) -> Dict[str, Any]:
        """Get improvement history for a duration."""
        cutoff = datetime.now() - duration
        recent = [
            imp for imp in self.improvements
            if imp.timestamp >= cutoff
        ]
        
        # Group by category
        by_category = defaultdict(int)
        for imp in recent:
            by_category[imp.category.value] += 1
        
        # Calculate impact
        total_impact = sum(imp.impact_score for imp in recent)
        
        return {
            'report_type': ReportType.IMPROVEMENT_HISTORY.value,
            'generated_at': datetime.now().isoformat(),
            'period_start': cutoff.isoformat(),
            'period_end': datetime.now().isoformat(),
            'total_improvements': len(recent),
            'total_impact': total_impact,
            'by_category': dict(by_category),
            'recent_milestones': [
                m for m in self.milestones
                if m['achievement_date'] >= cutoff
            ],
            'top_improvements': [
                imp.to_dict() for imp in
                sorted(recent, key=lambda x: x.impact_score, reverse=True)[:10]
            ]
        }


class DailySummaryGenerator:
    """Generates comprehensive daily summaries."""
    
    def __init__(self, morning_reporter: MorningOptimizationReporter,
                 evening_reporter: EveningLearningReporter,
                 dashboard: MetricsDashboard,
                 tracker: ImprovementTracker):
        self.morning_reporter = morning_reporter
        self.evening_reporter = evening_reporter
        self.dashboard = dashboard
        self.tracker = tracker
    
    def generate_daily_summary(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate comprehensive daily summary.
        
        Args:
            date: Date to generate summary for (default: today)
        
        Returns:
            Dictionary containing the daily summary
        """
        if date is None:
            date = datetime.now()
        
        # Define day boundaries
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        # Get reports from all components
        morning_report = self.morning_reporter.generate_morning_report(since=day_start)
        evening_report = self.evening_reporter.generate_evening_report(since=day_start)
        dashboard_data = self.dashboard.generate_dashboard()
        improvement_history = self.tracker.get_improvement_history(
            duration=timedelta(days=1)
        )
        
        # Calculate daily statistics
        total_improvements = morning_report['summary']['total_improvements']
        total_learning = evening_report['summary']['total_learning_events']
        total_experiments = evening_report['summary']['total_experiments']
        
        return {
            'report_type': ReportType.DAILY_SUMMARY.value,
            'generated_at': datetime.now().isoformat(),
            'date': date.date().isoformat(),
            'executive_summary': {
                'total_improvements': total_improvements,
                'total_learning_events': total_learning,
                'total_experiments': total_experiments,
                'total_impact': morning_report['summary']['total_impact'],
                'learning_confidence': evening_report['summary']['average_confidence']
            },
            'morning_optimization': morning_report,
            'evening_learning': evening_report,
            'metrics_dashboard': dashboard_data,
            'improvement_history': improvement_history,
            'highlights': self._generate_highlights(
                morning_report, evening_report, dashboard_data
            )
        }
    
    def _generate_highlights(self, morning_report: Dict[str, Any],
                           evening_report: Dict[str, Any],
                           dashboard_data: Dict[str, Any]) -> List[str]:
        """Generate highlights from the day's activities."""
        highlights = []
        
        # Top improvement
        if morning_report['top_improvements']:
            top_imp = morning_report['top_improvements'][0]
            highlights.append(
                f"Top improvement: {top_imp['title']} "
                f"(impact: {top_imp['impact_score']:.2f})"
            )
        
        # Top learning
        if evening_report['top_insights']:
            top_learning = evening_report['top_insights'][0]
            highlights.append(
                f"Key learning: {top_learning['topic']} in {top_learning['area']} "
                f"(confidence: {top_learning['confidence']:.2f})"
            )
        
        # Metric trends
        for metric, trend_data in dashboard_data.get('trends_24h', {}).items():
            if trend_data['trend'] in ['increasing', 'decreasing']:
                highlights.append(
                    f"{metric}: {trend_data['trend']} "
                    f"({trend_data['percent_change']:.1f}%)"
                )
        
        return highlights[:5]  # Top 5 highlights


class EvolutionReportingEngine:
    """Orchestrates all reporting activities."""
    
    def __init__(self, cycle_interval_minutes: int = 60):
        self.cycle_interval_minutes = cycle_interval_minutes
        self.morning_reporter = MorningOptimizationReporter()
        self.evening_reporter = EveningLearningReporter()
        self.dashboard = MetricsDashboard()
        self.tracker = ImprovementTracker()
        self.summary_generator = DailySummaryGenerator(
            self.morning_reporter,
            self.evening_reporter,
            self.dashboard,
            self.tracker
        )
        self.is_running = False
        self.last_cycle: Optional[datetime] = None
    
    async def start(self) -> None:
        """Start the reporting engine."""
        self.is_running = True
        while self.is_running:
            await self._run_cycle()
            await asyncio.sleep(self.cycle_interval_minutes * 60)
    
    def stop(self) -> None:
        """Stop the reporting engine."""
        self.is_running = False
    
    async def _run_cycle(self) -> None:
        """Run one reporting cycle."""
        self.last_cycle = datetime.now()
        
        # Update metrics
        await self._update_metrics()
        
        # Check if it's time for scheduled reports
        current_hour = datetime.now().hour
        
        # Morning report (6 AM)
        if current_hour == 6:
            morning_report = self.morning_reporter.generate_morning_report()
            await self._publish_report(morning_report)
        
        # Evening report (6 PM)
        if current_hour == 18:
            evening_report = self.evening_reporter.generate_evening_report()
            await self._publish_report(evening_report)
        
        # Daily summary (11 PM)
        if current_hour == 23:
            daily_summary = self.summary_generator.generate_daily_summary()
            await self._publish_report(daily_summary)
    
    async def _update_metrics(self) -> None:
        """Update current metrics."""
        # Record current metric snapshots
        metrics_to_record = [
            (MetricType.TASKS_AUTOMATED, len(self.tracker.improvements)),
            (MetricType.IMPROVEMENTS_DEPLOYED, len(self.morning_reporter.deployment_log)),
            (MetricType.KNOWLEDGE_ITEMS, len(self.evening_reporter.learning_events)),
        ]
        
        for metric_type, value in metrics_to_record:
            snapshot = MetricSnapshot(
                metric_type=metric_type,
                value=float(value),
                timestamp=datetime.now()
            )
            self.dashboard.record_metric(snapshot)
    
    async def _publish_report(self, report: Dict[str, Any]) -> None:
        """Publish a report (placeholder for actual implementation)."""
        # In a real implementation, this would:
        # - Save to file system
        # - Send notifications
        # - Update dashboards
        # - Log to database
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the reporting engine."""
        return {
            'is_running': self.is_running,
            'last_cycle': self.last_cycle.isoformat() if self.last_cycle else None,
            'cycle_interval_minutes': self.cycle_interval_minutes,
            'total_improvements': len(self.tracker.improvements),
            'total_learning_events': len(self.evening_reporter.learning_events),
            'total_metrics': sum(
                len(snapshots) for snapshots in self.dashboard.metric_snapshots.values()
            )
        }
