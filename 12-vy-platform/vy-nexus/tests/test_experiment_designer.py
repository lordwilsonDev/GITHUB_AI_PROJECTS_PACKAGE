#!/usr/bin/env python3
"""
Tests for Experiment Designer

Author: Vy-Nexus Self-Evolving AI
Created: December 15, 2025
"""

import unittest
import os
import json
import tempfile
import shutil
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from self_improvement.experiment_designer import (
    ExperimentDesigner,
    ExperimentType,
    MetricType,
    RiskLevel,
    ExperimentMetric,
    ExperimentGroup,
    SuccessCriteria,
    ExperimentProtocol
)


class TestExperimentDesigner(unittest.TestCase):
    """Test cases for ExperimentDesigner."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.designer = ExperimentDesigner(data_dir=self.test_dir)
        
        # Sample hypothesis
        self.sample_hypothesis = {
            "hypothesis_id": "hyp_test_001",
            "title": "Test Hypothesis",
            "category": "performance",
            "reasoning": "Test reasoning",
            "proposed_change": {"test_param": True},
            "expected_outcome": "Improved performance",
            "expected_improvement": 0.2,
            "confidence": "high",
            "priority": "medium",
            "affects_critical_systems": False,
            "easily_reversible": True,
            "user_impact": "low"
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test designer initialization."""
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertIsInstance(self.designer.protocols, dict)
        self.assertIsInstance(self.designer.templates, dict)
    
    def test_default_templates_created(self):
        """Test that default templates are created."""
        self.assertIn('performance_optimization', self.designer.templates)
        self.assertIn('user_experience', self.designer.templates)
        self.assertIn('automation_effectiveness', self.designer.templates)
    
    def test_design_experiment_basic(self):
        """Test basic experiment design."""
        protocol = self.designer.design_experiment(self.sample_hypothesis)
        
        self.assertIsInstance(protocol, ExperimentProtocol)
        self.assertTrue(protocol.experiment_id.startswith('exp_'))
        self.assertEqual(protocol.hypothesis_id, 'hyp_test_001')
        self.assertGreater(len(protocol.groups), 0)
        self.assertGreater(len(protocol.metrics), 0)
    
    def test_experiment_groups_created(self):
        """Test that control and treatment groups are created."""
        protocol = self.designer.design_experiment(self.sample_hypothesis)
        
        # Should have at least control and one treatment group
        self.assertGreaterEqual(len(protocol.groups), 2)
        
        # Check for control group
        control_groups = [g for g in protocol.groups if g.is_control]
        self.assertEqual(len(control_groups), 1)
        
        # Check for treatment group
        treatment_groups = [g for g in protocol.groups if not g.is_control]
        self.assertGreater(len(treatment_groups), 0)
    
    def test_metrics_selection(self):
        """Test that appropriate metrics are selected."""
        protocol = self.designer.design_experiment(self.sample_hypothesis)
        
        self.assertGreater(len(protocol.metrics), 0)
        
        # Check metric structure
        for metric in protocol.metrics:
            self.assertIsInstance(metric, ExperimentMetric)
            self.assertTrue(hasattr(metric, 'name'))
            self.assertTrue(hasattr(metric, 'metric_type'))
    
    def test_success_criteria_defined(self):
        """Test that success criteria are defined."""
        protocol = self.designer.design_experiment(self.sample_hypothesis)
        
        self.assertGreater(len(protocol.success_criteria), 0)
        
        for criterion in protocol.success_criteria:
            self.assertIsInstance(criterion, SuccessCriteria)
            self.assertIn(criterion.operator, ['>', '<', '>=', '<=', '=='])
    
    def test_duration_calculation(self):
        """Test experiment duration calculation."""
        protocol = self.designer.design_experiment(self.sample_hypothesis)
        
        self.assertGreater(protocol.estimated_duration_days, 0)
        self.assertGreater(protocol.minimum_duration_days, 0)
        self.assertGreater(protocol.maximum_duration_days, 0)
        
        # Maximum should be greater than estimated
        self.assertGreater(protocol.maximum_duration_days, 
                          protocol.estimated_duration_days)
    
    def test_risk_assessment_low(self):
        """Test risk assessment for low-risk hypothesis."""
        protocol = self.designer.design_experiment(self.sample_hypothesis)
        
        # Low risk hypothesis should have low or medium risk
        self.assertIn(protocol.risk_level, [RiskLevel.LOW.value, RiskLevel.MEDIUM.value])
        self.assertGreater(len(protocol.risk_mitigation), 0)
    
    def test_risk_assessment_high(self):
        """Test risk assessment for high-risk hypothesis."""
        high_risk_hypothesis = self.sample_hypothesis.copy()
        high_risk_hypothesis.update({
            "affects_critical_systems": True,
            "easily_reversible": False,
            "user_impact": "high"
        })
        
        protocol = self.designer.design_experiment(high_risk_hypothesis)
        
        # Should have high or critical risk
        self.assertIn(protocol.risk_level, [RiskLevel.HIGH.value, RiskLevel.CRITICAL.value])
        
        # Should have more mitigation steps
        self.assertGreater(len(protocol.risk_mitigation), 4)
    
    def test_resource_estimation(self):
        """Test resource and cost estimation."""
        protocol = self.designer.design_experiment(self.sample_hypothesis)
        
        self.assertGreater(len(protocol.required_resources), 0)
        self.assertGreater(protocol.estimated_cost, 0)
    
    def test_execution_plan_created(self):
        """Test that execution plan is created."""
        protocol = self.designer.design_experiment(self.sample_hypothesis)
        
        self.assertGreater(len(protocol.setup_steps), 0)
        self.assertGreater(len(protocol.execution_steps), 0)
        self.assertGreater(len(protocol.teardown_steps), 0)
    
    def test_monitoring_plan_created(self):
        """Test that monitoring plan is created."""
        protocol = self.designer.design_experiment(self.sample_hypothesis)
        
        self.assertIsInstance(protocol.monitoring_plan, dict)
        self.assertIn('metrics_to_monitor', protocol.monitoring_plan)
        self.assertIn('alert_conditions', protocol.monitoring_plan)
    
    def test_protocol_persistence(self):
        """Test that protocols are saved and loaded."""
        protocol = self.designer.design_experiment(self.sample_hypothesis)
        exp_id = protocol.experiment_id
        
        # Create new designer instance
        designer2 = ExperimentDesigner(data_dir=self.test_dir)
        
        # Should load saved protocol
        loaded_protocol = designer2.get_protocol(exp_id)
        self.assertIsNotNone(loaded_protocol)
        self.assertEqual(loaded_protocol['experiment_id'], exp_id)
    
    def test_template_selection_performance(self):
        """Test template selection for performance hypothesis."""
        perf_hypothesis = self.sample_hypothesis.copy()
        perf_hypothesis['category'] = 'performance'
        
        protocol = self.designer.design_experiment(perf_hypothesis)
        
        # Should use performance template
        self.assertEqual(protocol.experiment_type, ExperimentType.AB_TEST.value)
    
    def test_template_selection_user_experience(self):
        """Test template selection for user experience hypothesis."""
        ux_hypothesis = self.sample_hypothesis.copy()
        ux_hypothesis['category'] = 'user_experience'
        
        protocol = self.designer.design_experiment(ux_hypothesis)
        
        # Should use user experience template
        self.assertEqual(protocol.experiment_type, ExperimentType.AB_TEST.value)
    
    def test_list_protocols(self):
        """Test listing protocols."""
        # Create multiple protocols
        self.designer.design_experiment(self.sample_hypothesis)
        
        hyp2 = self.sample_hypothesis.copy()
        hyp2['hypothesis_id'] = 'hyp_test_002'
        self.designer.design_experiment(hyp2)
        
        protocols = self.designer.list_protocols()
        self.assertEqual(len(protocols), 2)
    
    def test_list_protocols_filtered_by_status(self):
        """Test listing protocols filtered by status."""
        protocol1 = self.designer.design_experiment(self.sample_hypothesis)
        
        hyp2 = self.sample_hypothesis.copy()
        hyp2['hypothesis_id'] = 'hyp_test_002'
        protocol2 = self.designer.design_experiment(hyp2)
        
        # Update one protocol status
        self.designer.update_protocol_status(protocol1.experiment_id, 'running')
        
        # Filter by status
        running = self.designer.list_protocols(status='running')
        self.assertEqual(len(running), 1)
        
        draft = self.designer.list_protocols(status='draft')
        self.assertEqual(len(draft), 1)
    
    def test_update_protocol_status(self):
        """Test updating protocol status."""
        protocol = self.designer.design_experiment(self.sample_hypothesis)
        
        # Update status
        result = self.designer.update_protocol_status(
            protocol.experiment_id, 'running'
        )
        self.assertTrue(result)
        
        # Verify update
        updated = self.designer.get_protocol(protocol.experiment_id)
        self.assertEqual(updated['status'], 'running')
    
    def test_generate_experiment_report(self):
        """Test experiment report generation."""
        protocol = self.designer.design_experiment(self.sample_hypothesis)
        
        report = self.designer.generate_experiment_report(protocol.experiment_id)
        
        self.assertIn('experiment_id', report)
        self.assertIn('name', report)
        self.assertIn('status', report)
        self.assertIn('duration', report)
        self.assertIn('groups', report)
        self.assertIn('metrics', report)
    
    def test_multiple_treatment_groups(self):
        """Test experiment with multiple treatment groups."""
        multi_hypothesis = self.sample_hypothesis.copy()
        multi_hypothesis['proposed_change'] = [
            {"variant": "A"},
            {"variant": "B"},
            {"variant": "C"}
        ]
        
        protocol = self.designer.design_experiment(multi_hypothesis)
        
        # Should have 1 control + 3 treatment groups
        self.assertEqual(len(protocol.groups), 4)
        
        treatment_groups = [g for g in protocol.groups if not g.is_control]
        self.assertEqual(len(treatment_groups), 3)
    
    def test_experiment_id_uniqueness(self):
        """Test that experiment IDs are unique."""
        protocol1 = self.designer.design_experiment(self.sample_hypothesis)
        protocol2 = self.designer.design_experiment(self.sample_hypothesis)
        
        self.assertNotEqual(protocol1.experiment_id, protocol2.experiment_id)
    
    def test_tags_generation(self):
        """Test that appropriate tags are generated."""
        protocol = self.designer.design_experiment(self.sample_hypothesis)
        
        self.assertGreater(len(protocol.tags), 0)
        self.assertIn('performance', protocol.tags)
    
    def test_critical_system_tag(self):
        """Test that critical tag is added for critical systems."""
        critical_hypothesis = self.sample_hypothesis.copy()
        critical_hypothesis['affects_critical_systems'] = True
        
        protocol = self.designer.design_experiment(critical_hypothesis)
        
        self.assertIn('critical', protocol.tags)
    
    def test_experiment_description(self):
        """Test that experiment description is created."""
        protocol = self.designer.design_experiment(self.sample_hypothesis)
        
        self.assertIsInstance(protocol.description, str)
        self.assertGreater(len(protocol.description), 0)
        self.assertIn(self.sample_hypothesis['title'], protocol.description)


class TestExperimentMetric(unittest.TestCase):
    """Test cases for ExperimentMetric dataclass."""
    
    def test_metric_creation(self):
        """Test creating an experiment metric."""
        metric = ExperimentMetric(
            name="test_metric",
            metric_type=MetricType.PERFORMANCE.value,
            description="Test metric",
            measurement_method="automated"
        )
        
        self.assertEqual(metric.name, "test_metric")
        self.assertEqual(metric.metric_type, MetricType.PERFORMANCE.value)


class TestExperimentGroup(unittest.TestCase):
    """Test cases for ExperimentGroup dataclass."""
    
    def test_group_creation(self):
        """Test creating an experiment group."""
        group = ExperimentGroup(
            group_id="test_group",
            name="Test Group",
            description="Test description",
            is_control=True,
            configuration={"test": True},
            sample_size=50,
            selection_criteria=["random"]
        )
        
        self.assertEqual(group.group_id, "test_group")
        self.assertTrue(group.is_control)
        self.assertEqual(group.sample_size, 50)


class TestSuccessCriteria(unittest.TestCase):
    """Test cases for SuccessCriteria dataclass."""
    
    def test_criteria_creation(self):
        """Test creating success criteria."""
        criteria = SuccessCriteria(
            metric_name="response_time",
            operator="<",
            threshold=100.0,
            required=True,
            description="Response time must be under 100ms"
        )
        
        self.assertEqual(criteria.metric_name, "response_time")
        self.assertEqual(criteria.operator, "<")
        self.assertTrue(criteria.required)


if __name__ == '__main__':
    unittest.main()
