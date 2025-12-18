#!/usr/bin/env python3
"""
Tests for A/B Testing Framework

Author: Vy-Nexus Self-Evolving AI
Created: December 15, 2025
"""

import unittest
import os
import json
import tempfile
import shutil
import random
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from self_improvement.ab_testing_framework import (
    ABTestingFramework,
    TestStatus,
    DecisionType,
    Participant,
    MetricValue,
    StatisticalResult,
    TestResult
)


class TestABTestingFramework(unittest.TestCase):
    """Test cases for ABTestingFramework."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.framework = ABTestingFramework(data_dir=self.test_dir)
        
        # Sample protocol
        self.sample_protocol = {
            'experiment_id': 'exp_test_001',
            'name': 'Test Experiment',
            'groups': [
                {'group_id': 'control', 'is_control': True},
                {'group_id': 'treatment', 'is_control': False}
            ],
            'metrics': [
                {'name': 'response_time'},
                {'name': 'success_rate'}
            ],
            'success_criteria': [
                {'metric_name': 'response_time', 'operator': '<', 'threshold': 100},
                {'metric_name': 'success_rate', 'operator': '>', 'threshold': 0.95}
            ]
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test framework initialization."""
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertIsInstance(self.framework.tests, dict)
        self.assertIsInstance(self.framework.participants, dict)
        self.assertIsInstance(self.framework.metrics, dict)
    
    def test_start_test(self):
        """Test starting a new test."""
        test_id = self.framework.start_test(self.sample_protocol)
        
        self.assertEqual(test_id, 'exp_test_001')
        self.assertIn(test_id, self.framework.tests)
        self.assertEqual(self.framework.tests[test_id]['status'], TestStatus.RUNNING.value)
    
    def test_assign_participant(self):
        """Test assigning participants to groups."""
        test_id = self.framework.start_test(self.sample_protocol)
        
        group = self.framework.assign_participant(test_id, 'user_001')
        
        self.assertIn(group, ['control', 'treatment'])
        self.assertEqual(len(self.framework.participants[test_id]), 1)
    
    def test_participant_distribution(self):
        """Test that participants are distributed across groups."""
        test_id = self.framework.start_test(self.sample_protocol)
        
        # Assign many participants
        for i in range(100):
            self.framework.assign_participant(test_id, f'user_{i}')
        
        # Count groups
        groups = {}
        for p in self.framework.participants[test_id]:
            group = p['group_id']
            groups[group] = groups.get(group, 0) + 1
        
        # Should have both groups
        self.assertGreater(len(groups), 1)
        
        # Should be roughly balanced (within 30%)
        for count in groups.values():
            self.assertGreater(count, 20)
            self.assertLess(count, 80)
    
    def test_record_metric(self):
        """Test recording metrics."""
        test_id = self.framework.start_test(self.sample_protocol)
        group = self.framework.assign_participant(test_id, 'user_001')
        
        self.framework.record_metric(test_id, 'user_001', 'response_time', 95.5)
        
        self.assertEqual(len(self.framework.metrics[test_id]), 1)
        self.assertEqual(self.framework.metrics[test_id][0]['value'], 95.5)
    
    def test_get_group_metrics(self):
        """Test retrieving metrics by group."""
        test_id = self.framework.start_test(self.sample_protocol)
        
        # Add participants and metrics
        for i in range(10):
            participant_id = f'user_{i}'
            group = self.framework.assign_participant(test_id, participant_id)
            self.framework.record_metric(test_id, participant_id, 'response_time', 100 + i)
        
        group_metrics = self.framework.get_group_metrics(test_id, 'response_time')
        
        self.assertGreater(len(group_metrics), 0)
        for group_id, values in group_metrics.items():
            self.assertGreater(len(values), 0)
    
    def test_calculate_statistics(self):
        """Test statistical calculations."""
        values = [10, 20, 30, 40, 50]
        stats = self.framework.calculate_statistics(values)
        
        self.assertEqual(stats['mean'], 30)
        self.assertEqual(stats['n'], 5)
        self.assertGreater(stats['std'], 0)
    
    def test_t_test(self):
        """Test t-test calculation."""
        control = [100, 105, 110, 95, 102]
        treatment = [80, 85, 90, 75, 82]
        
        t_stat, p_value = self.framework.t_test(control, treatment)
        
        # Treatment is significantly different (lower)
        self.assertLess(p_value, 0.05)
    
    def test_t_test_no_difference(self):
        """Test t-test with no significant difference."""
        control = [100, 105, 110, 95, 102]
        treatment = [98, 103, 108, 97, 104]
        
        t_stat, p_value = self.framework.t_test(control, treatment)
        
        # Should not be significant
        self.assertGreater(p_value, 0.05)
    
    def test_confidence_interval(self):
        """Test confidence interval calculation."""
        values = [100, 105, 110, 95, 102]
        ci_lower, ci_upper = self.framework.calculate_confidence_interval(values)
        
        mean = sum(values) / len(values)
        
        self.assertLess(ci_lower, mean)
        self.assertGreater(ci_upper, mean)
    
    def test_effect_size(self):
        """Test effect size calculation."""
        control = [100, 105, 110, 95, 102]
        treatment = [80, 85, 90, 75, 82]
        
        effect_size = self.framework.calculate_effect_size(control, treatment)
        
        # Should be negative (treatment lower) and large
        self.assertLess(effect_size, -1.0)
    
    def test_analyze_test_with_improvement(self):
        """Test analyzing a test with significant improvement."""
        test_id = self.framework.start_test(self.sample_protocol)
        
        # Add participants with treatment performing better
        for i in range(50):
            participant_id = f'user_{i}'
            group = self.framework.assign_participant(test_id, participant_id)
            
            if group == 'control':
                response_time = random.gauss(120, 10)
                success_rate = random.gauss(0.93, 0.02)
            else:
                response_time = random.gauss(85, 10)  # Much better
                success_rate = random.gauss(0.97, 0.02)
            
            self.framework.record_metric(test_id, participant_id, 'response_time', response_time)
            self.framework.record_metric(test_id, participant_id, 'success_rate', success_rate)
        
        result = self.framework.analyze_test(test_id)
        
        self.assertIsInstance(result, TestResult)
        self.assertEqual(result.status, TestStatus.COMPLETED.value)
        self.assertGreater(len(result.statistical_results), 0)
    
    def test_analyze_test_decision_deploy(self):
        """Test that analysis recommends deployment for clear winner."""
        test_id = self.framework.start_test(self.sample_protocol)
        
        # Strong improvement in treatment
        for i in range(100):
            participant_id = f'user_{i}'
            group = self.framework.assign_participant(test_id, participant_id)
            
            if group == 'control':
                response_time = random.gauss(150, 10)
                success_rate = random.gauss(0.90, 0.02)
            else:
                response_time = random.gauss(80, 10)
                success_rate = random.gauss(0.98, 0.01)
            
            self.framework.record_metric(test_id, participant_id, 'response_time', response_time)
            self.framework.record_metric(test_id, participant_id, 'success_rate', success_rate)
        
        result = self.framework.analyze_test(test_id)
        
        # Should recommend deployment
        self.assertEqual(result.decision, DecisionType.DEPLOY_TREATMENT.value)
        self.assertGreater(result.confidence, 0.5)
    
    def test_analyze_test_decision_keep_control(self):
        """Test that analysis keeps control when treatment is worse."""
        test_id = self.framework.start_test(self.sample_protocol)
        
        # Treatment performs worse
        for i in range(100):
            participant_id = f'user_{i}'
            group = self.framework.assign_participant(test_id, participant_id)
            
            if group == 'control':
                response_time = random.gauss(90, 10)
                success_rate = random.gauss(0.97, 0.01)
            else:
                response_time = random.gauss(150, 10)  # Worse
                success_rate = random.gauss(0.85, 0.02)
            
            self.framework.record_metric(test_id, participant_id, 'response_time', response_time)
            self.framework.record_metric(test_id, participant_id, 'success_rate', success_rate)
        
        result = self.framework.analyze_test(test_id)
        
        # Should keep control
        self.assertEqual(result.decision, DecisionType.KEEP_CONTROL.value)
    
    def test_check_early_stopping_not_enough_data(self):
        """Test early stopping check with insufficient data."""
        test_id = self.framework.start_test(self.sample_protocol)
        
        # Add only a few participants
        for i in range(10):
            self.framework.assign_participant(test_id, f'user_{i}')
        
        should_stop, reason = self.framework.check_early_stopping(test_id)
        
        self.assertFalse(should_stop)
        self.assertIn('Not enough', reason)
    
    def test_stop_test(self):
        """Test stopping a test."""
        test_id = self.framework.start_test(self.sample_protocol)
        
        self.framework.stop_test(test_id, "Manual stop for testing")
        
        self.assertEqual(self.framework.tests[test_id]['status'], TestStatus.STOPPED.value)
        self.assertIn('stop_reason', self.framework.tests[test_id])
    
    def test_get_test_status(self):
        """Test getting test status."""
        test_id = self.framework.start_test(self.sample_protocol)
        
        status = self.framework.get_test_status(test_id)
        
        self.assertEqual(status['test_id'], test_id)
        self.assertEqual(status['status'], TestStatus.RUNNING.value)
        self.assertIn('participants', status)
        self.assertIn('metrics_collected', status)
    
    def test_generate_report(self):
        """Test generating test report."""
        test_id = self.framework.start_test(self.sample_protocol)
        
        # Add some data
        for i in range(50):
            participant_id = f'user_{i}'
            group = self.framework.assign_participant(test_id, participant_id)
            self.framework.record_metric(test_id, participant_id, 'response_time', 100)
        
        # Analyze
        self.framework.analyze_test(test_id)
        
        # Generate report
        report = self.framework.generate_report(test_id)
        
        self.assertIn('test_id', report)
        self.assertIn('decision', report)
        self.assertIn('summary', report)
        self.assertIn('recommendations', report)
    
    def test_persistence(self):
        """Test that data persists across instances."""
        test_id = self.framework.start_test(self.sample_protocol)
        self.framework.assign_participant(test_id, 'user_001')
        
        # Create new instance
        framework2 = ABTestingFramework(data_dir=self.test_dir)
        
        # Should load saved data
        self.assertIn(test_id, framework2.tests)
        self.assertIn(test_id, framework2.participants)
    
    def test_multiple_metrics(self):
        """Test handling multiple metrics."""
        test_id = self.framework.start_test(self.sample_protocol)
        
        participant_id = 'user_001'
        group = self.framework.assign_participant(test_id, participant_id)
        
        # Record multiple metrics
        self.framework.record_metric(test_id, participant_id, 'response_time', 95.5)
        self.framework.record_metric(test_id, participant_id, 'success_rate', 0.98)
        self.framework.record_metric(test_id, participant_id, 'error_rate', 0.02)
        
        self.assertEqual(len(self.framework.metrics[test_id]), 3)
    
    def test_statistical_significance(self):
        """Test statistical significance detection."""
        test_id = self.framework.start_test(self.sample_protocol)
        
        # Create clear difference
        for i in range(100):
            participant_id = f'user_{i}'
            group = self.framework.assign_participant(test_id, participant_id)
            
            if group == 'control':
                value = random.gauss(100, 5)
            else:
                value = random.gauss(80, 5)  # 20% improvement
            
            self.framework.record_metric(test_id, participant_id, 'response_time', value)
        
        result = self.framework.analyze_test(test_id)
        
        # Should detect significance
        for stat in result.statistical_results:
            if stat.metric_name == 'response_time':
                self.assertTrue(stat.is_significant)
                self.assertLess(stat.p_value, 0.05)


class TestParticipant(unittest.TestCase):
    """Test cases for Participant dataclass."""
    
    def test_participant_creation(self):
        """Test creating a participant."""
        participant = Participant(
            participant_id="user_001",
            group_id="control",
            assigned_at=datetime.now().isoformat()
        )
        
        self.assertEqual(participant.participant_id, "user_001")
        self.assertEqual(participant.group_id, "control")


class TestMetricValue(unittest.TestCase):
    """Test cases for MetricValue dataclass."""
    
    def test_metric_value_creation(self):
        """Test creating a metric value."""
        metric = MetricValue(
            metric_name="response_time",
            value=95.5,
            participant_id="user_001",
            group_id="control",
            timestamp=datetime.now().isoformat()
        )
        
        self.assertEqual(metric.metric_name, "response_time")
        self.assertEqual(metric.value, 95.5)


if __name__ == '__main__':
    unittest.main()
