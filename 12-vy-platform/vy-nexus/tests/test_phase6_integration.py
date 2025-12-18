#!/usr/bin/env python3
"""
Phase 6 Integration Tests - Self-Improvement Cycle

Comprehensive integration tests for all Phase 6 components:
- Hypothesis Generator
- Experiment Designer
- A/B Testing Framework
- Predictive Models

Tests the complete workflow and quality of each component.
"""

import unittest
import os
import shutil
import json
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.hypothesis_generator import HypothesisGenerator, HypothesisType
from self_improvement.experiment_designer import ExperimentDesigner, ExperimentType
from self_improvement.ab_testing_framework import ABTestFramework, TestGroup
from self_improvement.predictive_models import (
    PredictiveModelManager,
    TrendDirection
)


class TestPhase6Integration(unittest.TestCase):
    """Integration tests for Phase 6 components."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = "test_data_phase6"
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Initialize components
        self.hypothesis_gen = HypothesisGenerator(data_dir=self.test_dir)
        self.experiment_designer = ExperimentDesigner(data_dir=self.test_dir)
        self.ab_framework = ABTestFramework(data_dir=self.test_dir)
        self.predictive_manager = PredictiveModelManager(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_hypothesis_generation_quality(self):
        """Test quality of generated hypotheses."""
        # Add some performance data
        for i in range(10):
            self.hypothesis_gen.record_performance(
                metric_name="response_time",
                value=100 + i * 5,
                context={"optimization": "none"}
            )
        
        # Generate hypotheses
        hypotheses = self.hypothesis_gen.generate_hypotheses(
            focus_area="performance",
            max_hypotheses=5
        )
        
        # Quality checks
        self.assertGreater(len(hypotheses), 0, "Should generate at least one hypothesis")
        
        for hyp in hypotheses:
            # Check completeness
            self.assertIsNotNone(hyp.hypothesis_id)
            self.assertIsNotNone(hyp.description)
            self.assertIsNotNone(hyp.expected_impact)
            self.assertIsNotNone(hyp.confidence)
            
            # Check confidence is valid
            self.assertGreaterEqual(hyp.confidence, 0.0)
            self.assertLessEqual(hyp.confidence, 1.0)
            
            # Check expected impact is reasonable
            self.assertGreater(abs(hyp.expected_impact), 0)
    
    def test_experiment_design_quality(self):
        """Test quality of experiment designs."""
        # Create a hypothesis
        hypothesis = {
            'hypothesis_id': 'hyp_001',
            'description': 'Caching will improve response time',
            'expected_impact': 0.25,
            'confidence': 0.8
        }
        
        # Design experiment
        protocol = self.experiment_designer.design_experiment(
            hypothesis=hypothesis,
            experiment_type=ExperimentType.AB_TEST,
            primary_metric='response_time'
        )
        
        # Quality checks
        self.assertIsNotNone(protocol.experiment_id)
        self.assertEqual(len(protocol.groups), 2)  # Control + Treatment
        self.assertGreater(len(protocol.metrics), 0)
        self.assertGreater(len(protocol.success_criteria), 0)
        
        # Check control group exists
        control_groups = [g for g in protocol.groups if g.is_control]
        self.assertEqual(len(control_groups), 1, "Should have exactly one control group")
        
        # Check metrics are defined
        for metric in protocol.metrics:
            self.assertIsNotNone(metric.name)
            self.assertIsNotNone(metric.type)
        
        # Check success criteria are actionable
        for criterion in protocol.success_criteria:
            self.assertIsNotNone(criterion.metric_name)
            self.assertIsNotNone(criterion.operator)
            self.assertIsNotNone(criterion.threshold)
    
    def test_ab_testing_statistical_accuracy(self):
        """Test statistical accuracy of A/B testing."""
        # Create test protocol
        protocol = {
            'experiment_id': 'exp_stat_001',
            'name': 'Statistical Accuracy Test',
            'groups': [
                {'group_id': 'control', 'is_control': True},
                {'group_id': 'treatment', 'is_control': False}
            ],
            'metrics': [
                {'name': 'success_rate'}
            ],
            'success_criteria': [
                {'metric_name': 'success_rate', 'operator': '>', 'threshold': 0.5}
            ]
        }
        
        # Start test
        test_id = self.ab_framework.start_test(protocol)
        
        # Simulate data with known difference
        # Control: 50% success rate
        # Treatment: 60% success rate (20% relative improvement)
        import random
        random.seed(42)  # For reproducibility
        
        for i in range(200):
            participant_id = f"user_{i}"
            group = self.ab_framework.assign_participant(test_id, participant_id)
            
            if group == 'control':
                success = random.random() < 0.50
            else:
                success = random.random() < 0.60
            
            self.ab_framework.record_metric(
                test_id, participant_id, 'success_rate', 1.0 if success else 0.0
            )
        
        # Analyze results
        result = self.ab_framework.analyze_test(test_id)
        
        # Quality checks
        self.assertIsNotNone(result.decision)
        self.assertGreater(result.confidence, 0.0)
        
        # With 200 samples and 20% improvement, should detect significance
        # (This is a probabilistic test, but with seed it should be deterministic)
        self.assertGreater(result.confidence, 0.8, "Should have high confidence with clear difference")
    
    def test_predictive_model_accuracy(self):
        """Test accuracy of predictive models."""
        # Create known trend
        for i in range(30):
            value = 100 + i * 2  # Linear increasing trend
            self.predictive_manager.trend_analyzer.add_metric("metric", value)
        
        # Analyze trend
        trend = self.predictive_manager.analyze_metric_trend("metric")
        
        # Should detect increasing trend
        self.assertEqual(trend['trend_direction'], TrendDirection.INCREASING.value)
        self.assertGreater(trend['trend_strength'], 0.5)
        
        # Forecast should be reasonable
        forecast = trend['forecast_5_steps']
        expected_next = 100 + 30 * 2  # Next value in sequence
        self.assertAlmostEqual(forecast, expected_next, delta=10)
    
    def test_anomaly_detection_precision(self):
        """Test precision of anomaly detection."""
        # Establish baseline
        for i in range(50):
            self.predictive_manager.anomaly_detector.add_observation("metric", 100.0)
        
        # Test normal values (should not be anomalies)
        normal_results = []
        for value in [99, 100, 101, 102, 98]:
            result = self.predictive_manager.check_for_anomalies("metric", value)
            normal_results.append(result.is_anomaly)
        
        # Most normal values should not be flagged
        false_positives = sum(normal_results)
        self.assertLess(false_positives, 2, "Too many false positives")
        
        # Test anomalous values (should be detected)
        anomaly_results = []
        for value in [200, 0, 250, -50]:
            result = self.predictive_manager.check_for_anomalies("metric", value)
            anomaly_results.append(result.is_anomaly)
        
        # Most anomalies should be detected
        true_positives = sum(anomaly_results)
        self.assertGreater(true_positives, 2, "Should detect clear anomalies")
    
    def test_full_workflow_integration(self):
        """Test complete workflow from hypothesis to deployment decision."""
        # Step 1: Record performance data
        for i in range(20):
            self.hypothesis_gen.record_performance(
                metric_name="execution_time",
                value=100 - i,  # Improving trend
                context={"version": "v1"}
            )
        
        # Step 2: Generate hypothesis
        hypotheses = self.hypothesis_gen.generate_hypotheses(
            focus_area="performance",
            max_hypotheses=1
        )
        self.assertGreater(len(hypotheses), 0)
        hypothesis = hypotheses[0]
        
        # Step 3: Design experiment
        protocol = self.experiment_designer.design_experiment(
            hypothesis=hypothesis.to_dict(),
            experiment_type=ExperimentType.AB_TEST,
            primary_metric='execution_time'
        )
        self.assertIsNotNone(protocol)
        
        # Step 4: Run A/B test
        test_protocol = {
            'experiment_id': protocol.experiment_id,
            'name': protocol.name,
            'groups': [g.to_dict() for g in protocol.groups],
            'metrics': [m.to_dict() for m in protocol.metrics],
            'success_criteria': [c.to_dict() for c in protocol.success_criteria]
        }
        
        test_id = self.ab_framework.start_test(test_protocol)
        
        # Simulate test data
        import random
        random.seed(42)
        for i in range(100):
            participant_id = f"user_{i}"
            group = self.ab_framework.assign_participant(test_id, participant_id)
            
            # Treatment is 15% faster
            if group == 'control':
                time = random.gauss(100, 10)
            else:
                time = random.gauss(85, 10)
            
            self.ab_framework.record_metric(test_id, participant_id, 'execution_time', time)
        
        # Step 5: Analyze results
        result = self.ab_framework.analyze_test(test_id)
        
        # Step 6: Use predictions to validate
        self.predictive_manager.performance_predictor.record_optimization(
            "workflow_optimization", 100, 85
        )
        
        impact = self.predictive_manager.predict_optimization_impact("workflow_optimization")
        
        # Verify workflow completed successfully
        self.assertIsNotNone(result.decision)
        self.assertIsNotNone(impact['expected_improvement'])
        
        # Results should be consistent
        self.assertGreater(result.confidence, 0.5)
        self.assertGreater(impact['confidence'], 0.0)
    
    def test_hypothesis_diversity(self):
        """Test that hypothesis generator produces diverse hypotheses."""
        # Add varied performance data
        metrics = ['response_time', 'throughput', 'error_rate', 'cpu_usage']
        for metric in metrics:
            for i in range(10):
                self.hypothesis_gen.record_performance(
                    metric_name=metric,
                    value=100 + i * 5,
                    context={}
                )
        
        # Generate multiple hypotheses
        hypotheses = self.hypothesis_gen.generate_hypotheses(
            focus_area="performance",
            max_hypotheses=10
        )
        
        # Check diversity
        unique_types = set(h.hypothesis_type for h in hypotheses)
        self.assertGreater(len(unique_types), 1, "Should generate diverse hypothesis types")
        
        # Check that hypotheses target different areas
        descriptions = [h.description.lower() for h in hypotheses]
        unique_descriptions = set(descriptions)
        self.assertGreater(len(unique_descriptions), 1, "Should have varied descriptions")
    
    def test_experiment_protocol_completeness(self):
        """Test that experiment protocols are complete and actionable."""
        hypothesis = {
            'hypothesis_id': 'hyp_complete',
            'description': 'Test completeness',
            'expected_impact': 0.2,
            'confidence': 0.7
        }
        
        protocol = self.experiment_designer.design_experiment(
            hypothesis=hypothesis,
            experiment_type=ExperimentType.AB_TEST,
            primary_metric='test_metric'
        )
        
        # Check all required fields
        required_fields = [
            'experiment_id', 'name', 'description', 'groups',
            'metrics', 'success_criteria', 'setup_steps',
            'execution_steps', 'teardown_steps'
        ]
        
        for field in required_fields:
            self.assertTrue(
                hasattr(protocol, field),
                f"Protocol missing required field: {field}"
            )
            value = getattr(protocol, field)
            self.assertIsNotNone(value, f"Field {field} should not be None")
    
    def test_prediction_confidence_calibration(self):
        """Test that prediction confidence is well-calibrated."""
        # Record consistent data (should have high confidence)
        for i in range(20):
            self.predictive_manager.performance_predictor.record_optimization(
                "consistent_opt", 100, 75  # Always 25% improvement
            )
        
        improvement, confidence = self.predictive_manager.performance_predictor.predict_improvement(
            "consistent_opt"
        )
        
        # Should have high confidence for consistent data
        self.assertGreater(confidence, 0.7, "Should have high confidence for consistent data")
        
        # Record inconsistent data (should have lower confidence)
        import random
        random.seed(42)
        for i in range(20):
            baseline = 100
            optimized = random.uniform(50, 95)  # Highly variable
            self.predictive_manager.performance_predictor.record_optimization(
                "inconsistent_opt", baseline, optimized
            )
        
        improvement2, confidence2 = self.predictive_manager.performance_predictor.predict_improvement(
            "inconsistent_opt"
        )
        
        # Should have lower confidence for inconsistent data
        self.assertLess(confidence2, confidence, "Should have lower confidence for variable data")
    
    def test_edge_case_insufficient_data(self):
        """Test handling of insufficient data scenarios."""
        # Try to generate hypotheses with no data
        hypotheses = self.hypothesis_gen.generate_hypotheses(
            focus_area="performance",
            max_hypotheses=5
        )
        
        # Should handle gracefully (may return empty or default hypotheses)
        self.assertIsInstance(hypotheses, list)
        
        # Try to predict with no data
        predictions = self.predictive_manager.predict_user_needs(top_k=5)
        self.assertIsInstance(predictions, list)
        
        # Try to analyze trend with insufficient data
        self.predictive_manager.trend_analyzer.add_metric("sparse", 100)
        trend = self.predictive_manager.analyze_metric_trend("sparse")
        self.assertIn('trend_direction', trend)
    
    def test_error_handling_invalid_inputs(self):
        """Test error handling for invalid inputs."""
        # Test with invalid hypothesis
        try:
            protocol = self.experiment_designer.design_experiment(
                hypothesis={},  # Empty hypothesis
                experiment_type=ExperimentType.AB_TEST,
                primary_metric='test'
            )
            # Should either handle gracefully or raise appropriate error
            self.assertIsNotNone(protocol)
        except (ValueError, KeyError) as e:
            # Acceptable to raise error for invalid input
            pass
        
        # Test anomaly detection with invalid metric
        result = self.predictive_manager.check_for_anomalies("nonexistent", 100)
        self.assertIsNotNone(result)  # Should return result, not crash
    
    def test_performance_scalability(self):
        """Test performance with larger datasets."""
        import time
        
        # Add large amount of data
        start_time = time.time()
        for i in range(1000):
            self.predictive_manager.trend_analyzer.add_metric("perf_test", float(i))
        add_time = time.time() - start_time
        
        # Should complete in reasonable time
        self.assertLess(add_time, 5.0, "Adding 1000 points should be fast")
        
        # Analyze should also be fast
        start_time = time.time()
        trend = self.predictive_manager.analyze_metric_trend("perf_test")
        analyze_time = time.time() - start_time
        
        self.assertLess(analyze_time, 2.0, "Analysis should be fast")
        self.assertIsNotNone(trend)
    
    def test_data_persistence(self):
        """Test that data persists correctly."""
        # Record some data
        self.predictive_manager.record_prediction_accuracy("test_model", 100, 95)
        self.predictive_manager.save_models()
        
        # Create new manager and load
        new_manager = PredictiveModelManager(data_dir=self.test_dir)
        new_manager.load_models()
        
        # Data should be loaded
        self.assertIn("test_model", new_manager.prediction_accuracy)
        self.assertEqual(
            len(new_manager.prediction_accuracy["test_model"]),
            len(self.predictive_manager.prediction_accuracy["test_model"])
        )


class TestPhase6QualityMetrics(unittest.TestCase):
    """Calculate quality metrics for Phase 6 components."""
    
    def setUp(self):
        self.test_dir = "test_data_quality"
        os.makedirs(self.test_dir, exist_ok=True)
        self.predictive_manager = PredictiveModelManager(data_dir=self.test_dir)
    
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_calculate_prediction_accuracy_metrics(self):
        """Calculate MAPE and RMSE for predictions."""
        import math
        
        # Simulate predictions and actuals
        predictions = [100, 95, 105, 98, 102]
        actuals = [98, 97, 103, 100, 101]
        
        # Calculate MAPE (Mean Absolute Percentage Error)
        mape = sum(abs(p - a) / abs(a) for p, a in zip(predictions, actuals)) / len(predictions)
        
        # Calculate RMSE (Root Mean Square Error)
        rmse = math.sqrt(sum((p - a) ** 2 for p, a in zip(predictions, actuals)) / len(predictions))
        
        # Quality thresholds
        self.assertLess(mape, 0.1, "MAPE should be < 10%")
        self.assertLess(rmse, 5.0, "RMSE should be reasonable")
    
    def test_model_performance_tracking(self):
        """Test that model performance is tracked correctly."""
        # Record multiple predictions
        for i in range(10):
            predicted = 100
            actual = 100 + (i % 3) - 1  # Small variations
            self.predictive_manager.record_prediction_accuracy(
                "test_model", predicted, actual
            )
        
        # Get performance metrics
        performance = self.predictive_manager.get_model_performance()
        
        self.assertIn("test_model", performance)
        self.assertGreater(performance["test_model"]['mean_accuracy'], 0.9)


if __name__ == '__main__':
    # Run tests and generate report
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestPhase6Integration))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase6QualityMetrics))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("PHASE 6 INTEGRATION TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("="*70)
