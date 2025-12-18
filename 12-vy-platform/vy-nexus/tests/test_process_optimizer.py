"""Tests for Process Optimization Engine"""

import pytest
import os
import sqlite3
from datetime import datetime, timedelta
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.process_optimizer import (
    PerformanceAnalyzer, BottleneckDetector, ProcessOptimizationEngine,
    PerformanceMetric, Bottleneck, OptimizationOpportunity
)


@pytest.fixture
def test_db():
    """Create a temporary test database"""
    db_path = 'data/test_optimizer.db'
    os.makedirs('data', exist_ok=True)
    
    # Clean up if exists
    if os.path.exists(db_path):
        os.remove(db_path)
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


def test_performance_analyzer_init(test_db):
    """Test PerformanceAnalyzer initialization"""
    analyzer = PerformanceAnalyzer(test_db)
    assert os.path.exists(test_db)
    
    # Verify tables created
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='performance_metrics'")
    assert cursor.fetchone() is not None
    conn.close()


def test_record_and_get_metrics(test_db):
    """Test recording and retrieving metrics"""
    analyzer = PerformanceAnalyzer(test_db)
    
    # Record some metrics
    for i in range(5):
        metric = PerformanceMetric(
            process_id='test_process',
            metric_name='execution_time',
            value=1.5 + i * 0.1,
            unit='seconds',
            timestamp=(datetime.now() - timedelta(days=i)).isoformat(),
            context={'iteration': i}
        )
        analyzer.record_metric(metric)
    
    # Retrieve metrics
    metrics = analyzer.get_metrics('test_process', 'execution_time')
    assert len(metrics) == 5
    assert metrics[0].process_id == 'test_process'
    assert metrics[0].metric_name == 'execution_time'


def test_performance_trends(test_db):
    """Test performance trend analysis"""
    analyzer = PerformanceAnalyzer(test_db)
    
    # Record degrading performance
    for i in range(10):
        metric = PerformanceMetric(
            process_id='degrading_process',
            metric_name='response_time',
            value=1.0 + i * 0.2,  # Increasing over time
            unit='seconds',
            timestamp=(datetime.now() - timedelta(days=9-i)).isoformat(),
            context={}
        )
        analyzer.record_metric(metric)
    
    trends = analyzer.analyze_performance_trends('degrading_process')
    assert trends['status'] == 'success'
    assert 'response_time' in trends['trends']
    assert trends['trends']['response_time']['trend'] == 'degrading'


def test_bottleneck_detector_init(test_db):
    """Test BottleneckDetector initialization"""
    detector = BottleneckDetector(test_db)
    assert os.path.exists(test_db)
    
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bottlenecks'")
    assert cursor.fetchone() is not None
    conn.close()


def test_detect_bottlenecks(test_db):
    """Test bottleneck detection"""
    analyzer = PerformanceAnalyzer(test_db)
    detector = BottleneckDetector(test_db)
    
    # Create degrading performance pattern
    for i in range(10):
        metric = PerformanceMetric(
            process_id='slow_process',
            metric_name='processing_time',
            value=1.0 + i * 0.5,  # Significant degradation
            unit='seconds',
            timestamp=(datetime.now() - timedelta(days=9-i)).isoformat(),
            context={}
        )
        analyzer.record_metric(metric)
    
    bottlenecks = detector.detect_bottlenecks('slow_process', analyzer)
    assert len(bottlenecks) > 0
    assert bottlenecks[0].process_id == 'slow_process'
    assert bottlenecks[0].severity in ['low', 'medium', 'high', 'critical']


def test_optimization_engine_init(test_db):
    """Test ProcessOptimizationEngine initialization"""
    engine = ProcessOptimizationEngine(test_db)
    assert os.path.exists(test_db)
    
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='optimization_opportunities'")
    assert cursor.fetchone() is not None
    conn.close()


def test_analyze_process(test_db):
    """Test comprehensive process analysis"""
    engine = ProcessOptimizationEngine(test_db)
    
    # Create test data with performance issues
    for i in range(15):
        metric = PerformanceMetric(
            process_id='complex_process',
            metric_name='total_time',
            value=2.0 + i * 0.3,
            unit='seconds',
            timestamp=(datetime.now() - timedelta(days=14-i)).isoformat(),
            context={}
        )
        engine.performance_analyzer.record_metric(metric)
    
    analysis = engine.analyze_process('complex_process')
    
    assert analysis['process_id'] == 'complex_process'
    assert 'performance_trends' in analysis
    assert 'bottlenecks' in analysis
    assert 'optimization_opportunities' in analysis
    assert 'summary' in analysis


def test_generate_opportunities(test_db):
    """Test opportunity generation"""
    engine = ProcessOptimizationEngine(test_db)
    
    # Create performance data
    for i in range(10):
        metric = PerformanceMetric(
            process_id='opt_process',
            metric_name='api_call_time',
            value=1.5 + i * 0.4,
            unit='seconds',
            timestamp=(datetime.now() - timedelta(days=9-i)).isoformat(),
            context={}
        )
        engine.performance_analyzer.record_metric(metric)
    
    analysis = engine.analyze_process('opt_process')
    opportunities = analysis['optimization_opportunities']
    
    assert len(opportunities) > 0
    assert all('opportunity_id' in opp for opp in opportunities)
    assert all('priority_score' in opp for opp in opportunities)


def test_get_top_opportunities(test_db):
    """Test retrieving top opportunities"""
    engine = ProcessOptimizationEngine(test_db)
    
    # Create multiple processes with issues
    for proc_num in range(3):
        for i in range(10):
            metric = PerformanceMetric(
                process_id=f'process_{proc_num}',
                metric_name='execution_time',
                value=1.0 + i * 0.5,
                unit='seconds',
                timestamp=(datetime.now() - timedelta(days=9-i)).isoformat(),
                context={}
            )
            engine.performance_analyzer.record_metric(metric)
        
        engine.analyze_process(f'process_{proc_num}')
    
    top_opps = engine.get_top_opportunities(limit=5)
    assert len(top_opps) <= 5
    
    # Verify sorted by priority
    if len(top_opps) > 1:
        for i in range(len(top_opps) - 1):
            assert top_opps[i].priority_score >= top_opps[i+1].priority_score


def test_severity_calculation(test_db):
    """Test severity calculation logic"""
    detector = BottleneckDetector(test_db)
    
    # Test different degradation levels
    test_cases = [
        ({'recent_avg': 2.0, 'older_avg': 1.0}, 'critical'),  # 100% degradation
        ({'recent_avg': 1.4, 'older_avg': 1.0}, 'high'),      # 40% degradation
        ({'recent_avg': 1.2, 'older_avg': 1.0}, 'medium'),    # 20% degradation
        ({'recent_avg': 1.1, 'older_avg': 1.0}, 'low'),       # 10% degradation
    ]
    
    for trend_data, expected_severity in test_cases:
        severity = detector._calculate_severity(trend_data)
        assert severity == expected_severity


def test_impact_calculation(test_db):
    """Test impact score calculation"""
    detector = BottleneckDetector(test_db)
    
    trend_data = {'recent_avg': 1.5, 'older_avg': 1.0}
    impact = detector._calculate_impact(trend_data)
    
    assert 0 <= impact <= 100
    assert impact == 50.0  # 50% degradation


def test_high_variance_detection(test_db):
    """Test detection of high variance (inconsistent performance)"""
    analyzer = PerformanceAnalyzer(test_db)
    detector = BottleneckDetector(test_db)
    
    # Create highly variable performance
    import random
    random.seed(42)
    for i in range(20):
        metric = PerformanceMetric(
            process_id='variable_process',
            metric_name='query_time',
            value=random.uniform(0.5, 3.0),  # High variance
            unit='seconds',
            timestamp=(datetime.now() - timedelta(days=19-i)).isoformat(),
            context={}
        )
        analyzer.record_metric(metric)
    
    bottlenecks = detector.detect_bottlenecks('variable_process', analyzer)
    
    # Should detect variance issue
    variance_bottlenecks = [b for b in bottlenecks if 'variance' in b.description.lower()]
    assert len(variance_bottlenecks) > 0


def test_summary_generation(test_db):
    """Test analysis summary generation"""
    engine = ProcessOptimizationEngine(test_db)
    
    # Create critical performance issue
    for i in range(10):
        metric = PerformanceMetric(
            process_id='critical_process',
            metric_name='load_time',
            value=1.0 + i * 1.0,  # Severe degradation
            unit='seconds',
            timestamp=(datetime.now() - timedelta(days=9-i)).isoformat(),
            context={}
        )
        engine.performance_analyzer.record_metric(metric)
    
    analysis = engine.analyze_process('critical_process')
    summary = analysis['summary']
    
    assert 'total_bottlenecks' in summary
    assert 'total_opportunities' in summary
    assert 'health_status' in summary
    assert summary['health_status'] in ['healthy', 'warning', 'critical']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
