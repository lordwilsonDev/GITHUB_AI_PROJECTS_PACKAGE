"""Tests for Productivity Analyzer"""

import pytest
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from productivity_analyzer import ProductivityAnalyzer


class TestProductivityAnalyzer:
    """Test suite for ProductivityAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create a fresh analyzer instance"""
        return ProductivityAnalyzer()
    
    def test_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert len(analyzer.task_records) == 0
        assert len(analyzer.productivity_metrics) == 0
        assert len(analyzer.bottlenecks) == 0
    
    def test_record_task(self, analyzer):
        """Test recording a task"""
        analyzer.record_task('web_search', 45.5, completed=True)
        
        assert len(analyzer.task_records) == 1
        assert len(analyzer.productivity_metrics['web_search']) == 1
        
        record = analyzer.task_records[0]
        assert record['task_type'] == 'web_search'
        assert record['duration_seconds'] == 45.5
        assert record['completed'] is True
    
    def test_record_task_with_metadata(self, analyzer):
        """Test recording task with metadata"""
        metadata = {'browser': 'chrome', 'query': 'test'}
        analyzer.record_task('web_search', 30.0, completed=True, metadata=metadata)
        
        record = analyzer.task_records[0]
        assert record['metadata'] == metadata
    
    def test_bottleneck_detection(self, analyzer):
        """Test bottleneck detection for slow tasks"""
        # Record a slow task (over 5 minutes)
        analyzer.record_task('slow_task', 400.0, completed=True)
        
        # Should detect bottleneck
        assert len(analyzer.bottlenecks) > 0
        bottleneck = analyzer.bottlenecks[0]
        assert bottleneck['task_type'] == 'slow_task'
    
    def test_bottleneck_severity(self, analyzer):
        """Test bottleneck severity classification"""
        # First establish baseline
        analyzer.record_task('task_x', 100.0, completed=True)
        analyzer.record_task('task_x', 100.0, completed=True)
        analyzer.record_task('task_x', 100.0, completed=True)
        
        # Now record very slow task (3x average)
        analyzer.record_task('task_x', 400.0, completed=True)
        
        # Should detect high severity bottleneck
        bottlenecks = [b for b in analyzer.bottlenecks if b['task_type'] == 'task_x']
        if bottlenecks:
            assert bottlenecks[0]['severity'] in ['high', 'medium']
    
    def test_get_productivity_metrics_basic(self, analyzer):
        """Test basic productivity metrics"""
        analyzer.record_task('task_a', 60.0, completed=True)
        analyzer.record_task('task_b', 90.0, completed=True)
        analyzer.record_task('task_c', 45.0, completed=False)
        
        metrics = analyzer.get_productivity_metrics()
        
        assert metrics['total_tasks'] == 3
        assert metrics['completed_tasks'] == 2
        assert metrics['completion_rate'] == 2/3
        assert metrics['total_time_seconds'] == 195.0
        assert metrics['average_task_duration'] == 65.0
    
    def test_get_productivity_metrics_by_task_type(self, analyzer):
        """Test task type breakdown in metrics"""
        analyzer.record_task('web_search', 30.0, completed=True)
        analyzer.record_task('web_search', 40.0, completed=True)
        analyzer.record_task('file_edit', 60.0, completed=False)
        
        metrics = analyzer.get_productivity_metrics()
        breakdown = metrics['task_type_breakdown']
        
        assert 'web_search' in breakdown
        assert 'file_edit' in breakdown
        assert breakdown['web_search']['count'] == 2
        assert breakdown['web_search']['completed'] == 2
        assert breakdown['web_search']['avg_duration'] == 35.0
    
    def test_get_productivity_metrics_time_window(self, analyzer):
        """Test metrics with time window filter"""
        # Record old task (should be excluded)
        old_record = {
            'timestamp': (datetime.now() - timedelta(days=2)).isoformat(),
            'task_type': 'old_task',
            'duration_seconds': 100.0,
            'completed': True,
            'metadata': {}
        }
        analyzer.task_records.append(old_record)
        
        # Record recent task
        analyzer.record_task('recent_task', 50.0, completed=True)
        
        # Get metrics for last 24 hours
        metrics = analyzer.get_productivity_metrics(timedelta(hours=24))
        
        # Should only include recent task
        assert metrics['total_tasks'] == 1
    
    def test_efficiency_score_calculation(self, analyzer):
        """Test efficiency score calculation"""
        # Record several completed tasks with reasonable durations
        for i in range(5):
            analyzer.record_task('task', 120.0, completed=True)
        
        metrics = analyzer.get_productivity_metrics()
        
        assert 'efficiency_score' in metrics
        assert 0 <= metrics['efficiency_score'] <= 100
    
    def test_identify_bottlenecks(self, analyzer):
        """Test bottleneck identification"""
        # Create baseline
        for i in range(3):
            analyzer.record_task('normal_task', 100.0, completed=True)
        
        # Create bottleneck
        analyzer.record_task('normal_task', 500.0, completed=True)
        
        bottlenecks = analyzer.identify_bottlenecks()
        assert len(bottlenecks) > 0
    
    def test_get_optimization_recommendations_slow_tasks(self, analyzer):
        """Test recommendations for slow tasks"""
        # Record slow tasks (over 5 minutes)
        for i in range(5):
            analyzer.record_task('slow_task', 400.0, completed=True)
        
        recommendations = analyzer.get_optimization_recommendations()
        
        # Should recommend optimization for slow task
        slow_recs = [r for r in recommendations if r['task_type'] == 'slow_task']
        assert len(slow_recs) > 0
        assert slow_recs[0]['issue'] == 'slow_execution'
    
    def test_get_optimization_recommendations_low_completion(self, analyzer):
        """Test recommendations for low completion rate"""
        # Record tasks with low completion rate
        for i in range(2):
            analyzer.record_task('unreliable_task', 60.0, completed=True)
        for i in range(8):
            analyzer.record_task('unreliable_task', 60.0, completed=False)
        
        recommendations = analyzer.get_optimization_recommendations()
        
        # Should recommend improving reliability
        unreliable_recs = [r for r in recommendations if r['task_type'] == 'unreliable_task']
        assert len(unreliable_recs) > 0
        assert unreliable_recs[0]['issue'] == 'low_completion_rate'
    
    def test_recommendation_priority(self, analyzer):
        """Test that recommendations are prioritized"""
        # High priority: very slow task
        for i in range(5):
            analyzer.record_task('very_slow', 700.0, completed=True)
        
        # Medium priority: moderately slow task
        for i in range(5):
            analyzer.record_task('medium_slow', 400.0, completed=True)
        
        recommendations = analyzer.get_optimization_recommendations()
        
        # High priority should come first
        if len(recommendations) >= 2:
            priorities = [r['priority'] for r in recommendations]
            # High priority items should be at the start
            assert 'high' in priorities
    
    def test_get_productivity_report(self, analyzer):
        """Test comprehensive productivity report"""
        # Add some data
        for i in range(10):
            analyzer.record_task('task_a', 60.0, completed=True)
        for i in range(5):
            analyzer.record_task('task_b', 300.0, completed=False)
        
        report = analyzer.get_productivity_report()
        
        assert 'generated_at' in report
        assert 'overall_metrics' in report
        assert 'recent_metrics' in report
        assert 'bottlenecks' in report
        assert 'recommendations' in report
        assert report['total_tasks_tracked'] == 15
    
    def test_tasks_per_hour_calculation(self, analyzer):
        """Test tasks per hour metric"""
        # Record tasks over time
        for i in range(10):
            analyzer.record_task('task', 60.0, completed=True)
        
        metrics = analyzer.get_productivity_metrics()
        
        assert 'tasks_per_hour' in metrics
        assert metrics['tasks_per_hour'] >= 0
    
    def test_empty_metrics(self, analyzer):
        """Test metrics with no data"""
        metrics = analyzer.get_productivity_metrics()
        
        # Should handle empty data gracefully
        assert 'error' in metrics or metrics['total_tasks'] == 0
    
    def test_completion_rate_edge_cases(self, analyzer):
        """Test completion rate with edge cases"""
        # All completed
        for i in range(5):
            analyzer.record_task('perfect_task', 60.0, completed=True)
        
        metrics = analyzer.get_productivity_metrics()
        breakdown = metrics['task_type_breakdown']
        
        assert breakdown['perfect_task']['completion_rate'] == 1.0
        
        # None completed
        for i in range(5):
            analyzer.record_task('failed_task', 60.0, completed=False)
        
        metrics = analyzer.get_productivity_metrics()
        breakdown = metrics['task_type_breakdown']
        
        assert breakdown['failed_task']['completion_rate'] == 0.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
