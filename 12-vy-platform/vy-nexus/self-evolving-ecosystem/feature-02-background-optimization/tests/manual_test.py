#!/usr/bin/env python3
"""Manual test runner for optimization engine (no pytest required)"""

import sys
from pathlib import Path
import asyncio
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from optimization_engine import (
    Task, RepetitivePattern, MicroAutomation, PerformanceMetric,
    RepetitiveTaskIdentifier, MicroAutomationCreator,
    PerformanceAnalyzer, WorkflowOptimizer, OptimizationEngine
)

from automation_sandbox import (
    SandboxManager, AutomationTester
)

def test_task_creation():
    """Test Task creation and signature."""
    print("Testing Task creation...")
    task = Task(
        task_id="task_001",
        task_type="file_copy",
        description="Copy file",
        parameters={"source": "/a", "dest": "/b"},
        timestamp=datetime.now(),
        duration_ms=100,
        success=True
    )
    assert task.task_id == "task_001"
    assert task.success is True
    signature = task.get_signature()
    assert len(signature) > 0
    print("✅ Task creation test passed")

def test_repetitive_task_identifier():
    """Test RepetitiveTaskIdentifier."""
    print("\nTesting RepetitiveTaskIdentifier...")
    identifier = RepetitiveTaskIdentifier(min_occurrences=3)
    
    # Add same task 5 times
    for i in range(5):
        task = Task(
            task_id=f"task_{i}",
            task_type="file_copy",
            description="Copy file",
            parameters={"source": "/a", "dest": "/b"},
            timestamp=datetime.now(),
            duration_ms=100,
            success=True
        )
        identifier.add_task(task)
    
    patterns = identifier.identify_repetitive_patterns()
    assert len(patterns) == 1
    assert patterns[0].occurrences == 5
    print(f"✅ Identified {len(patterns)} pattern(s) with {patterns[0].occurrences} occurrences")

def test_micro_automation_creator():
    """Test MicroAutomationCreator."""
    print("\nTesting MicroAutomationCreator...")
    creator = MicroAutomationCreator()
    
    pattern = RepetitivePattern(
        pattern_id="pattern_001",
        task_signature="sig_001",
        task_type="file_copy",
        occurrences=5,
        first_seen=datetime.now(),
        last_seen=datetime.now(),
        avg_duration_ms=150,
        automation_potential=0.8,
        parameters_variance={}
    )
    
    automation = creator.create_automation(pattern)
    assert automation.pattern_id == "pattern_001"
    assert len(creator.automations) == 1
    print(f"✅ Created automation: {automation.automation_id}")

def test_performance_analyzer():
    """Test PerformanceAnalyzer."""
    print("\nTesting PerformanceAnalyzer...")
    analyzer = PerformanceAnalyzer()
    
    # Add metrics
    for i in range(5):
        metric = PerformanceMetric(
            metric_id=f"metric_{i}",
            process_name="test_process",
            timestamp=datetime.now(),
            duration_ms=100 + i * 10,
            cpu_usage=50.0,
            memory_usage=60.0,
            success=True
        )
        analyzer.add_metric(metric)
    
    stats = analyzer.get_process_statistics("test_process")
    assert stats['total_executions'] == 5
    print(f"✅ Analyzed {stats['total_executions']} metrics, avg duration: {stats['avg_duration_ms']:.2f}ms")

def test_workflow_optimizer():
    """Test WorkflowOptimizer."""
    print("\nTesting WorkflowOptimizer...")
    analyzer = PerformanceAnalyzer()
    optimizer = WorkflowOptimizer(analyzer)
    
    # Add metrics
    for i in range(3):
        metric = PerformanceMetric(
            metric_id=f"metric_{i}",
            process_name="test_workflow",
            timestamp=datetime.now(),
            duration_ms=6000,
            cpu_usage=75.0,
            memory_usage=60.0,
            success=True
        )
        analyzer.add_metric(metric)
    
    analysis = optimizer.analyze_workflow("test_workflow")
    assert 'optimizations' in analysis
    print(f"✅ Found {len(analysis['optimizations'])} optimization opportunities")

def test_optimization_engine():
    """Test OptimizationEngine."""
    print("\nTesting OptimizationEngine...")
    engine = OptimizationEngine()
    
    # Add tasks
    for i in range(5):
        task = Task(
            task_id=f"task_{i}",
            task_type="file_copy",
            description="Copy file",
            parameters={"source": "/a", "dest": "/b"},
            timestamp=datetime.now(),
            duration_ms=100,
            success=True
        )
        engine.record_task(task)
    
    # Add metrics
    for i in range(3):
        metric = PerformanceMetric(
            metric_id=f"metric_{i}",
            process_name="test_process",
            timestamp=datetime.now(),
            duration_ms=500,
            cpu_usage=50.0,
            memory_usage=60.0,
            success=True
        )
        engine.record_performance(metric)
    
    report = engine.get_optimization_report()
    assert 'timestamp' in report
    assert 'repetitive_patterns' in report
    print(f"✅ Generated optimization report with {report['repetitive_patterns']} patterns")

def test_sandbox_manager():
    """Test SandboxManager."""
    print("\nTesting SandboxManager...")
    manager = SandboxManager()
    
    env = manager.create_environment()
    assert env.temp_dir.exists()
    print(f"✅ Created sandbox environment: {env.env_id}")
    
    result = manager.cleanup_environment(env.env_id)
    assert result is True
    assert not env.temp_dir.exists()
    print("✅ Cleaned up sandbox environment")

async def test_sandbox_execution():
    """Test sandbox script execution."""
    print("\nTesting sandbox script execution...")
    manager = SandboxManager(timeout_seconds=10)
    
    script = '''
def execute(params):
    return {'success': True, 'result': params.get('value', 0) * 2}
'''
    
    test = await manager.run_test(
        automation_id='test_auto_001',
        script=script,
        language='python',
        test_params={'value': 5}
    )
    
    assert test.completed_at is not None
    print(f"✅ Executed sandbox test in {test.duration_ms:.2f}ms")

def test_automation_tester():
    """Test AutomationTester."""
    print("\nTesting AutomationTester...")
    manager = SandboxManager()
    tester = AutomationTester(manager)
    
    test_cases = [
        {'name': 'test1', 'params': {'value': 1}},
        {'name': 'test2', 'params': {'value': 2}}
    ]
    
    tester.create_test_suite('auto_001', test_cases)
    assert 'auto_001' in tester.test_suites
    print(f"✅ Created test suite with {len(test_cases)} test cases")
    
    # Test default test generation
    default_tests = tester.generate_default_tests('file_operation')
    assert len(default_tests) > 0
    print(f"✅ Generated {len(default_tests)} default tests")

def main():
    """Run all tests."""
    print("=" * 70)
    print("Background Process Optimization - Manual Test Suite")
    print("=" * 70)
    
    tests = [
        test_task_creation,
        test_repetitive_task_identifier,
        test_micro_automation_creator,
        test_performance_analyzer,
        test_workflow_optimizer,
        test_optimization_engine,
        test_sandbox_manager,
        test_automation_tester,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            failed += 1
    
    # Run async test
    try:
        asyncio.run(test_sandbox_execution())
        passed += 1
    except Exception as e:
        print(f"❌ test_sandbox_execution FAILED: {e}")
        failed += 1
    
    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("✅ ALL TESTS PASSED")
        return 0
    else:
        print(f"❌ {failed} TEST(S) FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())
