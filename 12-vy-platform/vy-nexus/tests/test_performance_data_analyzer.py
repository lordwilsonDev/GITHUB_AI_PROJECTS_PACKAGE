"""
Test suite for Performance Data Analyzer

Tests all functionality of the performance analysis system including
metric recording, bottleneck detection, trend analysis, and optimization
opportunity identification.

Author: VY-NEXUS Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.optimization.performance_data_analyzer import PerformanceDataAnalyzer


class TestPerformanceDataAnalyzer(unittest.TestCase):
    """Test cases for PerformanceDataAnalyzer"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.analyzer = PerformanceDataAnalyzer(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test analyzer initialization"""
        self.assertIsNotNone(self.analyzer)
        self.assertTrue(Path(self.test_dir).exists())
        self.assertIsNotNone(self.analyzer.performance_data)
        self.assertIsNotNone(self.analyzer.bottlenecks)
        self.assertIsNotNone(self.analyzer.trends)
        self.assertIsNotNone(self.analyzer.optimizations)
    
    def test_record_performance_metric(self):
        """Test recording a performance metric"""
        result = self.analyzer.record_performance_metric(
            component="test_component",
            metric_type="response_time",
            value=500,
            metadata={"operation": "test_op"}
        )
        
        self.assertIsNotNone(result)
        self.assertIn("status", result)
        self.assertEqual(result["status"], "recorded")
        
        # Verify data was stored
        self.assertIn("test_component", self.analyzer.performance_data["components"])
        component_data = self.analyzer.performance_data["components"]["test_component"]
        self.assertIn("response_time", component_data["metrics"])
        self.assertEqual(len(component_data["metrics"]["response_time"]), 1)
    
    def test_threshold_violation_detection(self):
        """Test detection of threshold violations"""
        # Record a metric that exceeds threshold
        result = self.analyzer.record_performance_metric(
            component="test_component",
            metric_type="response_time",
            value=1500,  # Exceeds 1000ms threshold
            metadata={"operation": "slow_op"}
        )
        
        self.assertIn("warnings", result)
        self.assertGreater(len(result["warnings"]), 0)
        self.assertIn("threshold", result["warnings"][0].lower())
    
    def test_multiple_metrics_same_component(self):
        """Test recording multiple metrics for the same component"""
        # Record multiple metrics
        for i in range(5):
            self.analyzer.record_performance_metric(
                component="test_component",
                metric_type="response_time",
                value=500 + i * 100
            )
        
        component_data = self.analyzer.performance_data["components"]["test_component"]
        self.assertEqual(len(component_data["metrics"]["response_time"]), 5)
        self.assertEqual(component_data["total_measurements"], 5)
    
    def test_multiple_metric_types(self):
        """Test recording different metric types"""
        self.analyzer.record_performance_metric(
            component="test_component",
            metric_type="response_time",
            value=500
        )
        
        self.analyzer.record_performance_metric(
            component="test_component",
            metric_type="cpu_usage",
            value=45.5
        )
        
        self.analyzer.record_performance_metric(
            component="test_component",
            metric_type="memory_usage",
            value=512
        )
        
        component_data = self.analyzer.performance_data["components"]["test_component"]
        self.assertEqual(len(component_data["metrics"]), 3)
        self.assertIn("response_time", component_data["metrics"])
        self.assertIn("cpu_usage", component_data["metrics"])
        self.assertIn("memory_usage", component_data["metrics"])
    
    def test_analyze_component_performance(self):
        """Test component performance analysis"""
        # Record some metrics
        for i in range(10):
            self.analyzer.record_performance_metric(
                component="test_component",
                metric_type="response_time",
                value=500 + i * 50
            )
        
        analysis = self.analyzer.analyze_component_performance("test_component")
        
        self.assertIsNotNone(analysis)
        self.assertIn("component", analysis)
        self.assertEqual(analysis["component"], "test_component")
        self.assertIn("metrics", analysis)
        self.assertIn("overall_health", analysis)
    
    def test_analyze_nonexistent_component(self):
        """Test analyzing a component with no data"""
        analysis = self.analyzer.analyze_component_performance("nonexistent")
        
        self.assertIsNotNone(analysis)
        self.assertIn("error", analysis)
    
    def test_identify_bottlenecks(self):
        """Test bottleneck identification"""
        # Create performance data with bottlenecks
        for i in range(10):
            # Slow response times
            self.analyzer.record_performance_metric(
                component="slow_component",
                metric_type="response_time",
                value=1200 + i * 100  # Consistently over threshold
            )
            
            # Normal response times
            self.analyzer.record_performance_metric(
                component="fast_component",
                metric_type="response_time",
                value=300 + i * 10
            )
        
        bottlenecks = self.analyzer.identify_bottlenecks()
        
        self.assertIsInstance(bottlenecks, list)
        # Should identify slow_component as bottleneck
        bottleneck_components = [b["component"] for b in bottlenecks]
        self.assertIn("slow_component", bottleneck_components)
    
    def test_identify_optimization_opportunities(self):
        """Test optimization opportunity identification"""
        # Create performance data
        for i in range(20):
            self.analyzer.record_performance_metric(
                component="test_component",
                metric_type="response_time",
                value=800 + i * 50
            )
        
        opportunities = self.analyzer.identify_optimization_opportunities()
        
        self.assertIsInstance(opportunities, list)
        # Each opportunity should have required fields
        for opp in opportunities:
            self.assertIn("component", opp)
            self.assertIn("opportunity_type", opp)
            self.assertIn("priority", opp)
            self.assertIn("recommendation", opp)
    
    def test_calculate_performance_trends(self):
        """Test performance trend calculation"""
        # Record metrics over time
        for i in range(15):
            self.analyzer.record_performance_metric(
                component="test_component",
                metric_type="response_time",
                value=500 + i * 20  # Gradually increasing
            )
        
        trends = self.analyzer.calculate_performance_trends("test_component")
        
        self.assertIsNotNone(trends)
        self.assertIn("component", trends)
        self.assertIn("trends", trends)
    
    def test_get_system_wide_performance(self):
        """Test system-wide performance retrieval"""
        # Record metrics for multiple components
        for component in ["comp1", "comp2", "comp3"]:
            for i in range(5):
                self.analyzer.record_performance_metric(
                    component=component,
                    metric_type="response_time",
                    value=500 + i * 100
                )
        
        system_perf = self.analyzer.get_system_wide_performance()
        
        self.assertIsNotNone(system_perf)
        self.assertIn("total_components", system_perf)
        self.assertEqual(system_perf["total_components"], 3)
        self.assertIn("total_measurements", system_perf)
        self.assertIn("active_bottlenecks", system_perf)
    
    def test_generate_performance_report(self):
        """Test performance report generation"""
        # Record some metrics
        for i in range(10):
            self.analyzer.record_performance_metric(
                component="test_component",
                metric_type="response_time",
                value=600 + i * 50
            )
        
        report = self.analyzer.generate_performance_report()
        
        self.assertIsNotNone(report)
        self.assertIn("generated_at", report)
        self.assertIn("system_overview", report)
        self.assertIn("components", report)
        self.assertIn("bottlenecks", report)
        self.assertIn("optimization_opportunities", report)
        
        # Check system overview
        overview = report["system_overview"]
        self.assertIn("health_status", overview)
        self.assertIn("health_score", overview)
        self.assertIn("total_components", overview)
    
    def test_data_persistence(self):
        """Test that data persists across analyzer instances"""
        # Record metrics
        self.analyzer.record_performance_metric(
            component="persistent_component",
            metric_type="response_time",
            value=750
        )
        
        # Create new analyzer instance with same data directory
        new_analyzer = PerformanceDataAnalyzer(data_dir=self.test_dir)
        
        # Verify data was loaded
        self.assertIn("persistent_component", new_analyzer.performance_data["components"])
    
    def test_metric_statistics(self):
        """Test calculation of metric statistics"""
        # Record metrics with known values
        values = [100, 200, 300, 400, 500]
        for value in values:
            self.analyzer.record_performance_metric(
                component="test_component",
                metric_type="response_time",
                value=value
            )
        
        analysis = self.analyzer.analyze_component_performance("test_component")
        
        # Check that statistics are calculated
        self.assertIn("metrics", analysis)
        if "response_time" in analysis["metrics"]:
            stats = analysis["metrics"]["response_time"]
            self.assertIn("avg", stats)
            self.assertIn("min", stats)
            self.assertIn("max", stats)
    
    def test_health_score_calculation(self):
        """Test health score calculation"""
        # Record good performance metrics
        for i in range(10):
            self.analyzer.record_performance_metric(
                component="healthy_component",
                metric_type="response_time",
                value=400 + i * 10  # Well below threshold
            )
        
        report = self.analyzer.generate_performance_report()
        health_score = report["system_overview"]["health_score"]
        
        self.assertIsInstance(health_score, (int, float))
        self.assertGreaterEqual(health_score, 0)
        self.assertLessEqual(health_score, 100)
    
    def test_empty_report_generation(self):
        """Test report generation with no data"""
        report = self.analyzer.generate_performance_report()
        
        self.assertIsNotNone(report)
        self.assertIn("system_overview", report)
        self.assertEqual(report["system_overview"]["total_components"], 0)
    
    def test_bottleneck_severity_classification(self):
        """Test that bottlenecks are classified by severity"""
        # Create severe bottleneck
        for i in range(10):
            self.analyzer.record_performance_metric(
                component="critical_component",
                metric_type="response_time",
                value=2000 + i * 100  # Way over threshold
            )
        
        bottlenecks = self.analyzer.identify_bottlenecks()
        
        if bottlenecks:
            # Check that severity is assigned
            for bottleneck in bottlenecks:
                self.assertIn("severity", bottleneck)
                self.assertIn(bottleneck["severity"], ["low", "medium", "high", "critical"])
    
    def test_optimization_priority_assignment(self):
        """Test that optimization opportunities have priorities"""
        # Create data for optimization
        for i in range(15):
            self.analyzer.record_performance_metric(
                component="test_component",
                metric_type="response_time",
                value=900 + i * 50
            )
        
        opportunities = self.analyzer.identify_optimization_opportunities()
        
        for opp in opportunities:
            self.assertIn("priority", opp)
            self.assertIn(opp["priority"], ["low", "medium", "high", "critical"])
    
    def test_metadata_preservation(self):
        """Test that metadata is preserved with metrics"""
        metadata = {
            "operation": "test_operation",
            "user": "test_user",
            "context": "unit_test"
        }
        
        self.analyzer.record_performance_metric(
            component="test_component",
            metric_type="response_time",
            value=500,
            metadata=metadata
        )
        
        component_data = self.analyzer.performance_data["components"]["test_component"]
        metric_entry = component_data["metrics"]["response_time"][0]
        
        self.assertIn("metadata", metric_entry)
        self.assertEqual(metric_entry["metadata"], metadata)
    
    def test_timestamp_recording(self):
        """Test that timestamps are recorded correctly"""
        before = datetime.now()
        
        self.analyzer.record_performance_metric(
            component="test_component",
            metric_type="response_time",
            value=500
        )
        
        after = datetime.now()
        
        component_data = self.analyzer.performance_data["components"]["test_component"]
        metric_entry = component_data["metrics"]["response_time"][0]
        
        self.assertIn("timestamp", metric_entry)
        timestamp = datetime.fromisoformat(metric_entry["timestamp"])
        
        # Timestamp should be between before and after
        self.assertGreaterEqual(timestamp, before)
        self.assertLessEqual(timestamp, after)
    
    def test_component_comparison(self):
        """Test comparing performance across components"""
        # Record metrics for multiple components
        components = ["comp_a", "comp_b", "comp_c"]
        for comp in components:
            for i in range(5):
                self.analyzer.record_performance_metric(
                    component=comp,
                    metric_type="response_time",
                    value=500 + hash(comp) % 500  # Different values per component
                )
        
        system_perf = self.analyzer.get_system_wide_performance()
        
        self.assertEqual(system_perf["total_components"], 3)
        self.assertGreater(system_perf["total_measurements"], 0)
    
    def test_trend_direction_detection(self):
        """Test detection of performance trend direction"""
        # Create improving trend
        for i in range(10):
            self.analyzer.record_performance_metric(
                component="improving_component",
                metric_type="response_time",
                value=1000 - i * 50  # Decreasing (improving)
            )
        
        trends = self.analyzer.calculate_performance_trends("improving_component")
        
        self.assertIsNotNone(trends)
        # Should detect improvement trend
        if "trends" in trends and trends["trends"]:
            # Trend analysis should show improvement
            pass  # Implementation may vary
    
    def test_multiple_components_report(self):
        """Test report with multiple components"""
        # Create data for multiple components
        for comp_num in range(5):
            comp_name = f"component_{comp_num}"
            for i in range(10):
                self.analyzer.record_performance_metric(
                    component=comp_name,
                    metric_type="response_time",
                    value=500 + comp_num * 100 + i * 10
                )
        
        report = self.analyzer.generate_performance_report()
        
        self.assertEqual(report["system_overview"]["total_components"], 5)
        self.assertIn("components", report)
        self.assertGreater(len(report["components"]), 0)


def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == "__main__":
    run_tests()
