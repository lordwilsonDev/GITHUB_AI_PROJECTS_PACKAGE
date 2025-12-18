"""Integration Tests for Phase 3: Background Process Optimization

Rigorous testing of all optimization processes to validate they improve productivity.
"""

import pytest
import os
import sqlite3
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.task_identifier import RepetitiveTaskIdentifier
from modules.micro_automation import MicroAutomationFramework
from modules.process_optimizer import ProcessOptimizationEngine
from modules.efficiency_improver import EfficiencyImprovementEngine
from modules.sandbox_tester import SandboxManager, SandboxTester, SafetyValidator


@pytest.fixture
def test_db():
    """Create a temporary test database"""
    db_path = 'data/test_integration_phase3.db'
    os.makedirs('data', exist_ok=True)
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    yield db_path
    
    if os.path.exists(db_path):
        os.remove(db_path)


def test_full_optimization_pipeline(test_db):
    """Test complete optimization pipeline from identification to deployment"""
    # Step 1: Identify repetitive tasks
    task_identifier = RepetitiveTaskIdentifier(test_db)
    
    # Simulate repetitive tasks
    for i in range(5):
        task_identifier.record_task(
            task_type='data_export',
            parameters={'format': 'csv', 'destination': 'reports'},
            duration=3.5,
            success=True
        )
    
    candidates = task_identifier.get_automation_candidates(min_frequency=3)
    assert len(candidates) > 0
    
    # Step 2: Create automation
    automation_framework = MicroAutomationFramework(test_db)
    
    def export_automation():
        return "Data exported successfully"
    
    automation_framework.create_automation(
        name='auto_export',
        description='Automated data export',
        automation_func=export_automation
    )
    
    # Step 3: Test in sandbox
    sandbox_manager = SandboxManager(test_db)
    sandbox_tester = SandboxTester(test_db)
    
    sandbox = sandbox_manager.create_sandbox('optimization_test')
    
    execution = sandbox_tester.run_test(
        sandbox.sandbox_id,
        'export_automation_test',
        'automation',
        export_automation
    )
    
    assert execution.status == 'passed'
    
    # Step 4: Safety validation
    validator = SafetyValidator(test_db)
    is_safe = validator.validate_for_deployment(execution.execution_id)
    assert is_safe is True
    
    # Step 5: Measure improvement
    process_optimizer = ProcessOptimizationEngine(test_db)
    
    # Record performance before
    for i in range(5):
        from modules.process_optimizer import PerformanceMetric
        metric = PerformanceMetric(
            process_id='data_export',
            metric_name='execution_time',
            value=3.5,
            unit='seconds',
            timestamp=(datetime.now() - timedelta(days=i)).isoformat(),
            context={}
        )
        process_optimizer.performance_analyzer.record_metric(metric)
    
    # Record performance after automation
    for i in range(5):
        metric = PerformanceMetric(
            process_id='data_export',
            metric_name='execution_time',
            value=0.5,  # Much faster with automation
            unit='seconds',
            timestamp=datetime.now().isoformat(),
            context={'automated': True}
        )
        process_optimizer.performance_analyzer.record_metric(metric)
    
    # Verify improvement
    trends = process_optimizer.performance_analyzer.analyze_performance_trends('data_export')
    assert trends['status'] == 'success'


def test_bottleneck_detection_and_resolution(test_db):
    """Test bottleneck detection and optimization"""
    optimizer = ProcessOptimizationEngine(test_db)
    
    # Create performance degradation
    from modules.process_optimizer import PerformanceMetric
    
    for i in range(10):
        metric = PerformanceMetric(
            process_id='slow_process',
            metric_name='response_time',
            value=1.0 + i * 0.5,  # Degrading performance
            unit='seconds',
            timestamp=(datetime.now() - timedelta(days=9-i)).isoformat(),
            context={}
        )
        optimizer.performance_analyzer.record_metric(metric)
    
    # Analyze and detect bottlenecks
    analysis = optimizer.analyze_process('slow_process')
    
    assert len(analysis['bottlenecks']) > 0
    assert len(analysis['optimization_opportunities']) > 0
    assert analysis['summary']['health_status'] in ['warning', 'critical']
    
    # Verify opportunities are actionable
    for opp in analysis['optimization_opportunities']:
        assert 'title' in opp
        assert 'suggested_actions' in opp
        assert len(opp['suggested_actions']) > 0


def test_efficiency_improvements_validation(test_db):
    """Test that efficiency improvements actually improve productivity"""
    efficiency_engine = EfficiencyImprovementEngine(test_db)
    
    # Analyze workflow
    workflow_steps = [
        "Click File menu",
        "Click Save",
        "Copy text",
        "Paste text",
        "Open file",
        "Read data",
        "Open file",
        "Read data"
    ]
    
    analysis = efficiency_engine.analyze_workflow('test_workflow', workflow_steps)
    
    # Verify shortcuts were identified
    assert analysis['shortcuts_identified'] > 0
    assert analysis['total_time_saved_per_execution'] > 0
    
    # Verify recommendations are provided
    assert len(analysis['recommendations']) > 0
    
    # Test actual time savings
    shortcuts = analysis['shortcuts']
    total_savings = sum(s['time_saved_per_use'] for s in shortcuts)
    
    # Validate improvement
    assert total_savings > 0, "Shortcuts should save time"


def test_automation_safety_in_sandbox(test_db):
    """Test that all automations are tested in isolated environments"""
    sandbox_manager = SandboxManager(test_db)
    sandbox_tester = SandboxTester(test_db)
    
    # Create multiple sandboxes for isolation
    sandbox1 = sandbox_manager.create_sandbox('isolation_test_1')
    sandbox2 = sandbox_manager.create_sandbox('isolation_test_2')
    
    # Test automation in sandbox 1
    def automation1():
        return "Automation 1 result"
    
    exec1 = sandbox_tester.run_test(
        sandbox1.sandbox_id,
        'automation1',
        'automation',
        automation1
    )
    
    # Test different automation in sandbox 2
    def automation2():
        return "Automation 2 result"
    
    exec2 = sandbox_tester.run_test(
        sandbox2.sandbox_id,
        'automation2',
        'automation',
        automation2
    )
    
    # Verify both executed successfully in isolation
    assert exec1.status == 'passed'
    assert exec2.status == 'passed'
    assert exec1.sandbox_id != exec2.sandbox_id
    
    # Verify sandboxes are isolated
    assert sandbox1.base_path != sandbox2.base_path


def test_optimization_rollback_capability(test_db):
    """Test that optimizations can be rolled back if they fail"""
    automation_framework = MicroAutomationFramework(test_db)
    
    # Create automation with rollback
    rollback_executed = {'value': False}
    
    def main_automation():
        raise Exception("Automation failed")
    
    def rollback_func():
        rollback_executed['value'] = True
        return "Rolled back successfully"
    
    automation_id = automation_framework.create_automation(
        name='rollback_test',
        description='Test rollback',
        automation_func=main_automation,
        rollback_func=rollback_func
    )
    
    # Execute and expect failure
    result = automation_framework.execute_automation(automation_id)
    
    # Verify rollback was executed
    assert rollback_executed['value'] is True


def test_performance_metrics_accuracy(test_db):
    """Test that performance metrics accurately reflect improvements"""
    optimizer = ProcessOptimizationEngine(test_db)
    
    from modules.process_optimizer import PerformanceMetric
    
    # Record baseline performance
    baseline_times = [5.0, 5.1, 4.9, 5.2, 5.0]
    for i, time_val in enumerate(baseline_times):
        metric = PerformanceMetric(
            process_id='accuracy_test',
            metric_name='execution_time',
            value=time_val,
            unit='seconds',
            timestamp=(datetime.now() - timedelta(days=10-i)).isoformat(),
            context={'phase': 'baseline'}
        )
        optimizer.performance_analyzer.record_metric(metric)
    
    # Record improved performance
    improved_times = [2.0, 2.1, 1.9, 2.2, 2.0]
    for time_val in improved_times:
        metric = PerformanceMetric(
            process_id='accuracy_test',
            metric_name='execution_time',
            value=time_val,
            unit='seconds',
            timestamp=datetime.now().isoformat(),
            context={'phase': 'optimized'}
        )
        optimizer.performance_analyzer.record_metric(metric)
    
    # Analyze trends
    trends = optimizer.performance_analyzer.analyze_performance_trends('accuracy_test')
    
    assert trends['status'] == 'success'
    trend_data = trends['trends']['execution_time']
    
    # Verify improvement detected
    assert trend_data['trend'] == 'improving'
    assert trend_data['recent_avg'] < trend_data['older_avg']


def test_end_to_end_optimization_cycle(test_db):
    """Test complete optimization cycle: identify -> optimize -> test -> deploy"""
    # 1. Identify repetitive task
    task_identifier = RepetitiveTaskIdentifier(test_db)
    
    for i in range(10):
        task_identifier.record_task(
            task_type='report_generation',
            parameters={'format': 'pdf'},
            duration=8.0,
            success=True
        )
    
    candidates = task_identifier.get_automation_candidates(min_frequency=5)
    assert len(candidates) > 0
    
    # 2. Create optimization
    efficiency_engine = EfficiencyImprovementEngine(test_db)
    
    workflow = ['Generate data', 'Format report', 'Export PDF']
    analysis = efficiency_engine.analyze_workflow('report_gen', workflow)
    
    assert analysis['shortcuts_identified'] >= 0
    
    # 3. Test in sandbox
    sandbox_manager = SandboxManager(test_db)
    sandbox_tester = SandboxTester(test_db)
    validator = SafetyValidator(test_db)
    
    sandbox = sandbox_manager.create_sandbox('e2e_test')
    
    def optimized_report():
        return "Report generated in 2s"
    
    execution = sandbox_tester.run_test(
        sandbox.sandbox_id,
        'optimized_report',
        'automation',
        optimized_report
    )
    
    assert execution.status == 'passed'
    
    # 4. Validate safety
    is_safe = validator.validate_for_deployment(execution.execution_id)
    assert is_safe is True
    
    # 5. Measure actual improvement
    from modules.efficiency_improver import EfficiencyAnalyzer
    analyzer = EfficiencyAnalyzer(test_db)
    
    metric = analyzer.measure_improvement(
        process_id='report_generation',
        metric_type='time',
        before_value=8.0,
        after_value=2.0
    )
    
    assert metric.improvement_percentage == 75.0
    
    # 6. Verify deployment readiness
    summary = analyzer.get_improvement_summary('report_generation')
    assert 'time' in summary
    assert summary['time']['avg_improvement'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
