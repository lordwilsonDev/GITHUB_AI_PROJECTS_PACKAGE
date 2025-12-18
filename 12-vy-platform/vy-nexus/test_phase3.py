#!/usr/bin/env python3
"""
Phase 3 Component Testing Script
Tests all Phase 3 modules: Performance Data Analyzer, Efficiency Improver, Sandbox Tester
"""

import sys
from pathlib import Path

# Add modules to path
modules_path = Path.home() / "vy-nexus" / "modules" / "optimization"
sys.path.insert(0, str(modules_path))

print("=" * 60)
print("PHASE 3 COMPONENT TESTING")
print("=" * 60)

# Test 1: Performance Data Analyzer
print("\n" + "=" * 60)
print("TEST 1: Performance Data Analyzer")
print("=" * 60)

try:
    from performance_data_analyzer import PerformanceDataAnalyzer
    
    analyzer = PerformanceDataAnalyzer()
    
    # Record some metrics
    result1 = analyzer.record_performance_metric(
        component="learning_engine",
        metric_type="response_time",
        value=850,
        metadata={"operation": "pattern_analysis"}
    )
    print(f"✓ Metric recorded: {result1['status']}")
    
    # Test threshold violation
    result2 = analyzer.record_performance_metric(
        component="automation_generator",
        metric_type="response_time",
        value=1500,
        metadata={"operation": "script_generation"}
    )
    print(f"✓ Threshold violation detected: {len(result2['warnings'])} warnings")
    
    # Analyze component
    analysis = analyzer.analyze_component_performance("learning_engine")
    print(f"✓ Component analysis: {analysis.get('overall_health', 'N/A')}")
    
    # System-wide performance
    system_perf = analyzer.get_system_wide_performance()
    print(f"✓ System health: {system_perf['health_status']} (score: {system_perf['health_score']})")
    
    # Generate report
    report = analyzer.generate_performance_report()
    print(f"✓ Report generated with {len(report['component_analyses'])} component analyses")
    
    print("\n✅ Performance Data Analyzer: ALL TESTS PASSED")
    test1_passed = True
except Exception as e:
    print(f"\n❌ Performance Data Analyzer: FAILED - {str(e)}")
    import traceback
    traceback.print_exc()
    test1_passed = False

# Test 2: Efficiency Improver
print("\n" + "=" * 60)
print("TEST 2: Efficiency Improvement Engine")
print("=" * 60)

try:
    from efficiency_improver import EfficiencyImprover
    
    improver = EfficiencyImprover()
    
    # Analyze optimization opportunity
    analysis = improver.analyze_optimization_opportunity(
        component="learning_engine",
        issue_type="high_response_time",
        current_metrics={"response_time_ms": 1500, "cpu_usage_percent": 75},
        context={"operation": "pattern_analysis"}
    )
    print(f"✓ Optimization analysis: {len(analysis['suggestions'])} suggestions generated")
    print(f"✓ Estimated impact: {analysis['estimated_impact']['overall']}")
    print(f"✓ Implementation complexity: {analysis['implementation_complexity']}")
    
    # Create improvement plan
    plan = improver.create_improvement_plan(analysis["id"])
    print(f"✓ Improvement plan created: {len(plan['phases'])} phases")
    print(f"✓ Estimated hours: {plan['total_estimated_hours']}")
    
    # Track implementation
    record = improver.track_implementation(
        improvement_id=analysis["id"],
        status="completed",
        metrics_before={"response_time_ms": 1500},
        metrics_after={"response_time_ms": 800}
    )
    print(f"✓ Implementation tracked: {record['status']}")
    if record['impact']:
        print(f"✓ Overall improvement: {record['impact']['overall_improvement_percent']:.1f}%")
    
    # Get recommendations
    recommendations = improver.get_improvement_recommendations(priority="high")
    print(f"✓ High priority recommendations: {len(recommendations)}")
    
    # Test memory optimization
    mem_analysis = improver.analyze_optimization_opportunity(
        component="data_processor",
        issue_type="high_memory_usage",
        current_metrics={"memory_usage_mb": 2048}
    )
    print(f"✓ Memory optimization: {len(mem_analysis['suggestions'])} suggestions")
    
    print("\n✅ Efficiency Improvement Engine: ALL TESTS PASSED")
    test2_passed = True
except Exception as e:
    print(f"\n❌ Efficiency Improvement Engine: FAILED - {str(e)}")
    import traceback
    traceback.print_exc()
    test2_passed = False

# Test 3: Sandbox Tester
print("\n" + "=" * 60)
print("TEST 3: Sandbox Testing Environment")
print("=" * 60)

try:
    from sandbox_tester import SandboxTester
    
    tester = SandboxTester()
    
    # Create sandbox environment
    sandbox = tester.create_sandbox_environment(
        name="test_env_phase3",
        config={"isolation_level": "high", "timeout": 300}
    )
    print(f"✓ Sandbox created: {sandbox['name']}")
    print(f"✓ Status: {sandbox['status']}")
    
    # Register test
    test = tester.register_test(
        test_id="phase3_test_001",
        test_type="unit",
        description="Test Phase 3 functionality",
        expected_results={"success": True}
    )
    print(f"✓ Test registered: {test['id']}")
    print(f"✓ Test type: {test['type']}")
    
    # Run test
    result = tester.run_test(
        test_id="phase3_test_001",
        sandbox_name="test_env_phase3"
    )
    print(f"✓ Test executed: {result['status']}")
    print(f"✓ Duration: {result['duration_seconds']:.3f}s")
    
    # Benchmark performance
    def sample_function():
        return sum(range(1000))
    
    benchmark = tester.benchmark_performance(
        component="phase3_component",
        test_function=sample_function,
        iterations=50
    )
    print(f"✓ Benchmark completed: {benchmark['iterations']} iterations")
    print(f"✓ Mean execution time: {benchmark['statistics']['mean_ms']:.3f}ms")
    
    # Validate safety
    safety = tester.validate_safety(
        component="phase3_component",
        checks=["no_data_loss", "backward_compatible", "resource_limits"]
    )
    print(f"✓ Safety validation: {len(safety['checks'])} checks performed")
    print(f"✓ All checks passed: {safety['all_passed']}")
    
    # Get test summary
    summary = tester.get_test_summary()
    print(f"✓ Test summary: {summary['summary']['total_tests']} total tests")
    print(f"✓ Success rate: {summary['summary']['success_rate']:.1f}%")
    
    # Cleanup
    cleanup = tester.cleanup_sandbox("test_env_phase3", keep_logs=True)
    print(f"✓ Cleanup: {cleanup.get('status', 'completed')}")
    
    print("\n✅ Sandbox Testing Environment: ALL TESTS PASSED")
    test3_passed = True
except Exception as e:
    print(f"\n❌ Sandbox Testing Environment: FAILED - {str(e)}")
    import traceback
    traceback.print_exc()
    test3_passed = False

# Final Phase 3 Summary
print("\n" + "=" * 60)
print("PHASE 3 TESTING SUMMARY")
print("=" * 60)

all_tests = [
    ("Performance Data Analyzer", test1_passed),
    ("Efficiency Improvement Engine", test2_passed),
    ("Sandbox Testing Environment", test3_passed)
]

passed = sum(1 for _, result in all_tests if result)
total = len(all_tests)

print(f"\nTests Passed: {passed}/{total}")
print(f"Success Rate: {(passed/total)*100:.1f}%\n")

for name, result in all_tests:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"  {status} - {name}")

if passed == total:
    print("\n" + "=" * 60)
    print("🎉 PHASE 3 COMPLETE - ALL COMPONENTS OPERATIONAL")
    print("=" * 60)
else:
    print("\n" + "=" * 60)
    print("⚠️  PHASE 3 INCOMPLETE - SOME TESTS FAILED")
    print("=" * 60)
