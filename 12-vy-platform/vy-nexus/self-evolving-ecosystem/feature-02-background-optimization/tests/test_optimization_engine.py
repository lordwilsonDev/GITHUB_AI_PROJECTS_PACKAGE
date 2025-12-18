"""Tests for Background Process Optimization Engine"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from optimization_engine import (
    Task, RepetitivePattern, MicroAutomation, PerformanceMetric,
    RepetitiveTaskIdentifier, MicroAutomationCreator,
    PerformanceAnalyzer, WorkflowOptimizer, OptimizationEngine
)


class TestTask:
    """Test Task dataclass."""
    
    def test_task_creation(self):
        task = Task(
            task_id="task_001",
            task_type="file_copy",
            description="Copy file from A to B",
            parameters={"source": "/path/a", "dest": "/path/b"},
            timestamp=datetime.now(),
            duration_ms=150.5,
            success=True
        )
        assert task.task_id == "task_001"
        assert task.success is True
    
    def test_task_signature(self):
        task1 = Task(
            task_id="task_001",
            task_type="file_copy",
            description="Copy file",
            parameters={"source": "/a", "dest": "/b"},
            timestamp=datetime.now(),
            duration_ms=100,
            success=True
        )
        task2 = Task(
            task_id="task_002",
            task_type="file_copy",
            description="Copy file",
            parameters={"source": "/a", "dest": "/b"},
            timestamp=datetime.now(),
            duration_ms=120,
            success=True
        )
        # Same parameters should produce same signature
        assert task1.get_signature() == task2.get_signature()
    
    def test_different_signatures(self):
        task1 = Task(
            task_id="task_001",
            task_type="file_copy",
            description="Copy file",
            parameters={"source": "/a", "dest": "/b"},
            timestamp=datetime.now(),
            duration_ms=100,
            success=True
        )
        task2 = Task(
            task_id="task_002",
            task_type="file_copy",
            description="Copy file",
            parameters={"source": "/c", "dest": "/d"},
            timestamp=datetime.now(),
            duration_ms=100,
            success=True
        )
        # Different parameters should produce different signatures
        assert task1.get_signature() != task2.get_signature()


class TestRepetitiveTaskIdentifier:
    """Test RepetitiveTaskIdentifier."""
    
    def test_initialization(self):
        identifier = RepetitiveTaskIdentifier(min_occurrences=3, time_window_hours=24)
        assert identifier.min_occurrences == 3
        assert identifier.time_window_hours == 24
        assert len(identifier.task_history) == 0
    
    def test_add_task(self):
        identifier = RepetitiveTaskIdentifier()
        task = Task(
            task_id="task_001",
            task_type="test",
            description="Test task",
            parameters={"key": "value"},
            timestamp=datetime.now(),
            duration_ms=100,
            success=True
        )
        identifier.add_task(task)
        assert len(identifier.task_history) == 1
    
    def test_pattern_detection(self):
        identifier = RepetitiveTaskIdentifier(min_occurrences=3)
        
        # Add same task 5 times
        for i in range(5):
            task = Task(
                task_id=f"task_{i}",
                task_type="file_copy",
                description="Copy file",
                parameters={"source": "/a", "dest": "/b"},
                timestamp=datetime.now(),
                duration_ms=100 + i * 10,
                success=True
            )
            identifier.add_task(task)
        
        patterns = identifier.identify_repetitive_patterns()
        assert len(patterns) == 1
        assert patterns[0].occurrences == 5
    
    def test_multiple_patterns(self):
        identifier = RepetitiveTaskIdentifier(min_occurrences=2)
        
        # Add two different patterns
        for i in range(3):
            task1 = Task(
                task_id=f"task_a_{i}",
                task_type="file_copy",
                description="Copy",
                parameters={"source": "/a", "dest": "/b"},
                timestamp=datetime.now(),
                duration_ms=100,
                success=True
            )
            task2 = Task(
                task_id=f"task_b_{i}",
                task_type="file_move",
                description="Move",
                parameters={"source": "/c", "dest": "/d"},
                timestamp=datetime.now(),
                duration_ms=150,
                success=True
            )
            identifier.add_task(task1)
            identifier.add_task(task2)
        
        patterns = identifier.identify_repetitive_patterns()
        assert len(patterns) == 2
    
    def test_automation_potential_calculation(self):
        identifier = RepetitiveTaskIdentifier(min_occurrences=2)
        
        # Add frequent, slow task (high potential)
        for i in range(10):
            task = Task(
                task_id=f"task_{i}",
                task_type="slow_task",
                description="Slow task",
                parameters={"key": "value"},
                timestamp=datetime.now(),
                duration_ms=5000,  # 5 seconds
                success=True
            )
            identifier.add_task(task)
        
        patterns = identifier.identify_repetitive_patterns()
        assert len(patterns) == 1
        assert patterns[0].automation_potential > 0.5
    
    def test_history_size_limit(self):
        identifier = RepetitiveTaskIdentifier()
        identifier.max_history_size = 100
        
        # Add more tasks than limit
        for i in range(150):
            task = Task(
                task_id=f"task_{i}",
                task_type="test",
                description="Test",
                parameters={"id": i},
                timestamp=datetime.now(),
                duration_ms=100,
                success=True
            )
            identifier.add_task(task)
        
        assert len(identifier.task_history) == 100


class TestMicroAutomationCreator:
    """Test MicroAutomationCreator."""
    
    def test_initialization(self):
        creator = MicroAutomationCreator()
        assert len(creator.automations) == 0
        assert len(creator.templates) > 0
    
    def test_create_automation(self):
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
        assert automation.tested is False
        assert automation.deployed is False
        assert len(creator.automations) == 1
    
    def test_customize_automation(self):
        creator = MicroAutomationCreator()
        pattern = RepetitivePattern(
            pattern_id="pattern_001",
            task_signature="sig_001",
            task_type="test",
            occurrences=3,
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            avg_duration_ms=100,
            automation_potential=0.7,
            parameters_variance={}
        )
        
        automation = creator.create_automation(pattern)
        custom_script = "# Custom automation script\nprint('Hello')\n"
        
        result = creator.customize_automation(automation.automation_id, custom_script)
        assert result is True
        assert creator.automations[automation.automation_id].script == custom_script
        assert creator.automations[automation.automation_id].tested is False
    
    def test_list_automations(self):
        creator = MicroAutomationCreator()
        
        # Create multiple automations
        for i in range(3):
            pattern = RepetitivePattern(
                pattern_id=f"pattern_{i}",
                task_signature=f"sig_{i}",
                task_type="test",
                occurrences=3,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                avg_duration_ms=100,
                automation_potential=0.7,
                parameters_variance={}
            )
            automation = creator.create_automation(pattern)
            if i == 0:
                automation.deployed = True
        
        all_automations = creator.list_automations()
        assert len(all_automations) == 3
        
        deployed_only = creator.list_automations(deployed_only=True)
        assert len(deployed_only) == 1


class TestPerformanceAnalyzer:
    """Test PerformanceAnalyzer."""
    
    def test_initialization(self):
        analyzer = PerformanceAnalyzer()
        assert len(analyzer.metrics) == 0
        assert analyzer.bottleneck_threshold_ms == 1000
    
    def test_add_metric(self):
        analyzer = PerformanceAnalyzer()
        metric = PerformanceMetric(
            metric_id="metric_001",
            process_name="test_process",
            timestamp=datetime.now(),
            duration_ms=500,
            cpu_usage=50.0,
            memory_usage=60.0,
            success=True
        )
        analyzer.add_metric(metric)
        assert len(analyzer.metrics) == 1
    
    def test_bottleneck_detection(self):
        analyzer = PerformanceAnalyzer()
        metric = PerformanceMetric(
            metric_id="metric_001",
            process_name="slow_process",
            timestamp=datetime.now(),
            duration_ms=2000,  # Slow
            cpu_usage=85.0,    # High CPU
            memory_usage=90.0, # High memory
            success=True
        )
        analyzer.add_metric(metric)
        
        assert len(metric.bottlenecks) == 3
        assert len(metric.optimization_suggestions) > 0
    
    def test_process_statistics(self):
        analyzer = PerformanceAnalyzer()
        
        # Add multiple metrics for same process
        for i in range(5):
            metric = PerformanceMetric(
                metric_id=f"metric_{i}",
                process_name="test_process",
                timestamp=datetime.now(),
                duration_ms=100 + i * 10,
                cpu_usage=50.0 + i,
                memory_usage=60.0,
                success=i % 2 == 0  # 60% success rate
            )
            analyzer.add_metric(metric)
        
        stats = analyzer.get_process_statistics("test_process")
        assert stats['total_executions'] == 5
        assert 0 < stats['success_rate'] < 1
        assert stats['avg_duration_ms'] > 100
    
    def test_identify_slow_processes(self):
        analyzer = PerformanceAnalyzer()
        
        # Add fast process
        for i in range(3):
            metric = PerformanceMetric(
                metric_id=f"fast_{i}",
                process_name="fast_process",
                timestamp=datetime.now(),
                duration_ms=100,
                cpu_usage=30.0,
                memory_usage=40.0,
                success=True
            )
            analyzer.add_metric(metric)
        
        # Add slow process
        for i in range(3):
            metric = PerformanceMetric(
                metric_id=f"slow_{i}",
                process_name="slow_process",
                timestamp=datetime.now(),
                duration_ms=3000,
                cpu_usage=70.0,
                memory_usage=80.0,
                success=True
            )
            analyzer.add_metric(metric)
        
        slow_processes = analyzer.identify_slow_processes(threshold_ms=2000)
        assert "slow_process" in slow_processes
        assert "fast_process" not in slow_processes


class TestWorkflowOptimizer:
    """Test WorkflowOptimizer."""
    
    def test_initialization(self):
        analyzer = PerformanceAnalyzer()
        optimizer = WorkflowOptimizer(analyzer)
        assert optimizer.performance_analyzer == analyzer
    
    def test_analyze_workflow(self):
        analyzer = PerformanceAnalyzer()
        optimizer = WorkflowOptimizer(analyzer)
        
        # Add metrics for workflow
        for i in range(5):
            metric = PerformanceMetric(
                metric_id=f"metric_{i}",
                process_name="test_workflow",
                timestamp=datetime.now(),
                duration_ms=6000,  # Slow
                cpu_usage=75.0,    # High CPU
                memory_usage=60.0,
                success=i < 4  # 80% success rate
            )
            analyzer.add_metric(metric)
        
        analysis = optimizer.analyze_workflow("test_workflow")
        assert analysis['workflow'] == "test_workflow"
        assert 'statistics' in analysis
        assert 'optimizations' in analysis
        assert len(analysis['optimizations']) > 0
    
    def test_optimization_score(self):
        analyzer = PerformanceAnalyzer()
        optimizer = WorkflowOptimizer(analyzer)
        
        # Perfect workflow
        stats_perfect = {
            'success_rate': 1.0,
            'avg_duration_ms': 100,
            'avg_cpu_usage': 30.0
        }
        score_perfect = optimizer._calculate_optimization_score(stats_perfect)
        assert score_perfect < 0.2
        
        # Poor workflow
        stats_poor = {
            'success_rate': 0.5,
            'avg_duration_ms': 10000,
            'avg_cpu_usage': 90.0
        }
        score_poor = optimizer._calculate_optimization_score(stats_poor)
        assert score_poor > 0.5
    
    def test_suggest_improvements(self):
        analyzer = PerformanceAnalyzer()
        optimizer = WorkflowOptimizer(analyzer)
        
        # Add problematic metrics
        for i in range(3):
            metric = PerformanceMetric(
                metric_id=f"metric_{i}",
                process_name="problem_workflow",
                timestamp=datetime.now(),
                duration_ms=8000,
                cpu_usage=85.0,
                memory_usage=70.0,
                success=False
            )
            metric.bottlenecks.append("Database query timeout")
            analyzer.add_metric(metric)
        
        suggestions = optimizer.suggest_workflow_improvements("problem_workflow")
        assert len(suggestions) > 0


class TestOptimizationEngine:
    """Test OptimizationEngine."""
    
    def test_initialization(self):
        engine = OptimizationEngine()
        assert engine.task_identifier is not None
        assert engine.automation_creator is not None
        assert engine.performance_analyzer is not None
        assert engine.workflow_optimizer is not None
        assert engine.running is False
    
    @pytest.mark.asyncio
    async def test_start_stop(self):
        engine = OptimizationEngine()
        await engine.start()
        assert engine.running is True
        
        await engine.stop()
        assert engine.running is False
    
    def test_record_task(self):
        engine = OptimizationEngine()
        task = Task(
            task_id="task_001",
            task_type="test",
            description="Test task",
            parameters={"key": "value"},
            timestamp=datetime.now(),
            duration_ms=100,
            success=True
        )
        engine.record_task(task)
        assert len(engine.task_identifier.task_history) == 1
    
    def test_record_performance(self):
        engine = OptimizationEngine()
        metric = PerformanceMetric(
            metric_id="metric_001",
            process_name="test_process",
            timestamp=datetime.now(),
            duration_ms=500,
            cpu_usage=50.0,
            memory_usage=60.0,
            success=True
        )
        engine.record_performance(metric)
        assert len(engine.performance_analyzer.metrics) == 1
    
    def test_optimization_report(self):
        engine = OptimizationEngine()
        
        # Add some tasks
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
        
        # Add some metrics
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
        assert 'automations_created' in report
        assert 'performance_summary' in report


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
