"""Tests for Evolution Reporting System.

This module contains comprehensive tests for all reporting components.
"""

import pytest
from datetime import datetime, timedelta
from reporting_engine import (
    MorningOptimizationReporter,
    EveningLearningReporter,
    MetricsDashboard,
    ImprovementTracker,
    DailySummaryGenerator,
    EvolutionReportingEngine,
    Improvement,
    LearningEvent,
    MetricSnapshot,
    ImprovementCategory,
    MetricType,
    ReportType
)


class TestMorningOptimizationReporter:
    """Tests for MorningOptimizationReporter."""
    
    def test_record_improvement(self):
        """Test recording improvements."""
        reporter = MorningOptimizationReporter()
        
        improvement = Improvement(
            id="imp_001",
            category=ImprovementCategory.AUTOMATION,
            title="New automation",
            description="Automated task X",
            impact_score=0.8,
            timestamp=datetime.now()
        )
        
        reporter.record_improvement(improvement)
        assert len(reporter.overnight_improvements) == 1
        assert reporter.overnight_improvements[0].id == "imp_001"
    
    def test_record_deployment(self):
        """Test recording deployments."""
        reporter = MorningOptimizationReporter()
        
        reporter.record_deployment(
            component="learning_engine",
            version="1.2.0",
            changes=["Added feature X", "Fixed bug Y"]
        )
        
        assert len(reporter.deployment_log) == 1
        assert reporter.deployment_log[0]['component'] == "learning_engine"
    
    def test_generate_morning_report(self):
        """Test generating morning report."""
        reporter = MorningOptimizationReporter()
        
        # Add some improvements
        for i in range(3):
            improvement = Improvement(
                id=f"imp_{i:03d}",
                category=ImprovementCategory.AUTOMATION,
                title=f"Improvement {i}",
                description=f"Description {i}",
                impact_score=0.5 + i * 0.1,
                timestamp=datetime.now()
            )
            reporter.record_improvement(improvement)
        
        report = reporter.generate_morning_report()
        
        assert report['report_type'] == ReportType.MORNING_OPTIMIZATION.value
        assert report['summary']['total_improvements'] == 3
        assert len(report['top_improvements']) <= 5


class TestEveningLearningReporter:
    """Tests for EveningLearningReporter."""
    
    def test_record_learning(self):
        """Test recording learning events."""
        reporter = EveningLearningReporter()
        
        event = LearningEvent(
            id="learn_001",
            area="technical",
            topic="Python async",
            insights=["Insight 1", "Insight 2"],
            confidence=0.8,
            timestamp=datetime.now(),
            source="documentation"
        )
        
        reporter.record_learning(event)
        assert len(reporter.learning_events) == 1
        assert reporter.learning_events[0].topic == "Python async"
    
    def test_record_experiment(self):
        """Test recording experiments."""
        reporter = EveningLearningReporter()
        
        reporter.record_experiment(
            experiment_id="exp_001",
            hypothesis="Hypothesis X",
            results={'success': True, 'improvement': 0.15}
        )
        
        assert len(reporter.experiments_conducted) == 1
        assert reporter.experiments_conducted[0]['hypothesis'] == "Hypothesis X"
    
    def test_record_pattern(self):
        """Test recording patterns."""
        reporter = EveningLearningReporter()
        
        reporter.record_pattern(
            pattern_type="temporal",
            description="Users prefer morning tasks",
            confidence=0.75
        )
        
        assert len(reporter.patterns_discovered) == 1
        assert reporter.patterns_discovered[0]['type'] == "temporal"
    
    def test_generate_evening_report(self):
        """Test generating evening report."""
        reporter = EveningLearningReporter()
        
        # Add learning events
        for i in range(3):
            event = LearningEvent(
                id=f"learn_{i:03d}",
                area="technical",
                topic=f"Topic {i}",
                insights=[f"Insight {i}"],
                confidence=0.6 + i * 0.1,
                timestamp=datetime.now(),
                source="research"
            )
            reporter.record_learning(event)
        
        report = reporter.generate_evening_report()
        
        assert report['report_type'] == ReportType.EVENING_LEARNING.value
        assert report['summary']['total_learning_events'] == 3
        assert len(report['top_insights']) <= 5


class TestMetricsDashboard:
    """Tests for MetricsDashboard."""
    
    def test_record_metric(self):
        """Test recording metrics."""
        dashboard = MetricsDashboard()
        
        snapshot = MetricSnapshot(
            metric_type=MetricType.TASKS_AUTOMATED,
            value=42.0,
            timestamp=datetime.now()
        )
        
        dashboard.record_metric(snapshot)
        assert len(dashboard.metric_snapshots[MetricType.TASKS_AUTOMATED]) == 1
    
    def test_add_alert(self):
        """Test adding alerts."""
        dashboard = MetricsDashboard()
        
        dashboard.add_alert(
            metric_type=MetricType.SUCCESS_RATE,
            message="Success rate dropped below 90%",
            severity="warning"
        )
        
        assert len(dashboard.alerts) == 1
        assert dashboard.alerts[0]['severity'] == "warning"
    
    def test_get_current_metrics(self):
        """Test getting current metrics."""
        dashboard = MetricsDashboard()
        
        # Record some metrics
        for metric_type in [MetricType.TASKS_AUTOMATED, MetricType.TIME_SAVED]:
            snapshot = MetricSnapshot(
                metric_type=metric_type,
                value=100.0,
                timestamp=datetime.now()
            )
            dashboard.record_metric(snapshot)
        
        current = dashboard.get_current_metrics()
        assert len(current) == 2
        assert MetricType.TASKS_AUTOMATED.value in current
    
    def test_get_metric_trend(self):
        """Test getting metric trends."""
        dashboard = MetricsDashboard()
        
        # Record increasing trend
        base_time = datetime.now() - timedelta(hours=2)
        for i in range(10):
            snapshot = MetricSnapshot(
                metric_type=MetricType.TASKS_AUTOMATED,
                value=float(10 + i * 2),
                timestamp=base_time + timedelta(minutes=i * 10)
            )
            dashboard.record_metric(snapshot)
        
        trend = dashboard.get_metric_trend(MetricType.TASKS_AUTOMATED)
        assert trend['trend'] == 'increasing'
        assert trend['change'] > 0
    
    def test_generate_dashboard(self):
        """Test generating dashboard."""
        dashboard = MetricsDashboard()
        
        # Add some data
        snapshot = MetricSnapshot(
            metric_type=MetricType.SYSTEM_EFFICIENCY,
            value=0.95,
            timestamp=datetime.now()
        )
        dashboard.record_metric(snapshot)
        
        dashboard_data = dashboard.generate_dashboard()
        
        assert dashboard_data['report_type'] == ReportType.METRICS_DASHBOARD.value
        assert 'current_metrics' in dashboard_data
        assert 'trends_24h' in dashboard_data


class TestImprovementTracker:
    """Tests for ImprovementTracker."""
    
    def test_track_improvement(self):
        """Test tracking improvements."""
        tracker = ImprovementTracker()
        
        improvement = Improvement(
            id="imp_001",
            category=ImprovementCategory.PERFORMANCE,
            title="Performance boost",
            description="Optimized algorithm",
            impact_score=0.9,
            timestamp=datetime.now()
        )
        
        tracker.track_improvement(improvement)
        assert len(tracker.improvements) == 1
    
    def test_add_milestone(self):
        """Test adding milestones."""
        tracker = ImprovementTracker()
        
        tracker.add_milestone(
            title="First 100 improvements",
            description="Reached 100 improvements"
        )
        
        assert len(tracker.milestones) == 1
        assert tracker.milestones[0]['title'] == "First 100 improvements"
    
    def test_milestone_auto_detection(self):
        """Test automatic milestone detection."""
        tracker = ImprovementTracker()
        
        # Add 100 improvements
        for i in range(100):
            improvement = Improvement(
                id=f"imp_{i:03d}",
                category=ImprovementCategory.OPTIMIZATION,
                title=f"Improvement {i}",
                description=f"Description {i}",
                impact_score=0.5,
                timestamp=datetime.now()
            )
            tracker.track_improvement(improvement)
        
        # Should have auto-created milestone
        assert any(m['title'] == "100 Improvements" for m in tracker.milestones)
    
    def test_get_improvement_history(self):
        """Test getting improvement history."""
        tracker = ImprovementTracker()
        
        # Add improvements
        for i in range(5):
            improvement = Improvement(
                id=f"imp_{i:03d}",
                category=ImprovementCategory.FEATURE,
                title=f"Feature {i}",
                description=f"Description {i}",
                impact_score=0.6 + i * 0.05,
                timestamp=datetime.now()
            )
            tracker.track_improvement(improvement)
        
        history = tracker.get_improvement_history(duration=timedelta(days=1))
        
        assert history['report_type'] == ReportType.IMPROVEMENT_HISTORY.value
        assert history['total_improvements'] == 5
        assert len(history['top_improvements']) <= 10


class TestDailySummaryGenerator:
    """Tests for DailySummaryGenerator."""
    
    def test_generate_daily_summary(self):
        """Test generating daily summary."""
        morning_reporter = MorningOptimizationReporter()
        evening_reporter = EveningLearningReporter()
        dashboard = MetricsDashboard()
        tracker = ImprovementTracker()
        
        generator = DailySummaryGenerator(
            morning_reporter,
            evening_reporter,
            dashboard,
            tracker
        )
        
        # Add some data
        improvement = Improvement(
            id="imp_001",
            category=ImprovementCategory.AUTOMATION,
            title="Test improvement",
            description="Test",
            impact_score=0.7,
            timestamp=datetime.now()
        )
        morning_reporter.record_improvement(improvement)
        
        event = LearningEvent(
            id="learn_001",
            area="technical",
            topic="Test topic",
            insights=["Test insight"],
            confidence=0.8,
            timestamp=datetime.now(),
            source="test"
        )
        evening_reporter.record_learning(event)
        
        summary = generator.generate_daily_summary()
        
        assert summary['report_type'] == ReportType.DAILY_SUMMARY.value
        assert 'executive_summary' in summary
        assert 'morning_optimization' in summary
        assert 'evening_learning' in summary
        assert 'highlights' in summary


class TestEvolutionReportingEngine:
    """Tests for EvolutionReportingEngine."""
    
    def test_initialization(self):
        """Test engine initialization."""
        engine = EvolutionReportingEngine(cycle_interval_minutes=30)
        
        assert engine.cycle_interval_minutes == 30
        assert not engine.is_running
        assert engine.last_cycle is None
    
    def test_get_status(self):
        """Test getting engine status."""
        engine = EvolutionReportingEngine()
        
        status = engine.get_status()
        
        assert 'is_running' in status
        assert 'cycle_interval_minutes' in status
        assert 'total_improvements' in status
        assert 'total_learning_events' in status
    
    @pytest.mark.asyncio
    async def test_update_metrics(self):
        """Test metrics update."""
        engine = EvolutionReportingEngine()
        
        # Add some data
        improvement = Improvement(
            id="imp_001",
            category=ImprovementCategory.OPTIMIZATION,
            title="Test",
            description="Test",
            impact_score=0.5,
            timestamp=datetime.now()
        )
        engine.tracker.track_improvement(improvement)
        
        await engine._update_metrics()
        
        # Check that metrics were recorded
        assert len(engine.dashboard.metric_snapshots) > 0


def test_improvement_to_dict():
    """Test Improvement serialization."""
    improvement = Improvement(
        id="imp_001",
        category=ImprovementCategory.SECURITY,
        title="Security update",
        description="Enhanced security",
        impact_score=0.95,
        timestamp=datetime.now(),
        metrics={'vulnerabilities_fixed': 3},
        related_components=['auth', 'api']
    )
    
    data = improvement.to_dict()
    
    assert data['id'] == "imp_001"
    assert data['category'] == ImprovementCategory.SECURITY.value
    assert data['metrics']['vulnerabilities_fixed'] == 3
    assert 'auth' in data['related_components']


def test_learning_event_to_dict():
    """Test LearningEvent serialization."""
    event = LearningEvent(
        id="learn_001",
        area="domain",
        topic="User behavior",
        insights=["Insight 1", "Insight 2"],
        confidence=0.85,
        timestamp=datetime.now(),
        source="observation"
    )
    
    data = event.to_dict()
    
    assert data['id'] == "learn_001"
    assert data['area'] == "domain"
    assert len(data['insights']) == 2


def test_metric_snapshot_to_dict():
    """Test MetricSnapshot serialization."""
    snapshot = MetricSnapshot(
        metric_type=MetricType.USER_SATISFACTION,
        value=4.5,
        timestamp=datetime.now(),
        metadata={'survey_responses': 100}
    )
    
    data = snapshot.to_dict()
    
    assert data['metric_type'] == MetricType.USER_SATISFACTION.value
    assert data['value'] == 4.5
    assert data['metadata']['survey_responses'] == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
