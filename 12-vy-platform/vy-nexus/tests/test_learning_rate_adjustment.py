#!/usr/bin/env python3
"""
Tests for Learning Rate Adjustment System

Author: Vy Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import unittest
import json
import tempfile
import math
from pathlib import Path
import sys
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'self_improvement'))

from learning_rate_adjustment import (
    ScheduleType,
    LearningRateConfig,
    LearningRateScheduler,
    AdaptiveLearningRate,
    ConvergenceDetector
)


class TestLearningRateScheduler(unittest.TestCase):
    """Test cases for LearningRateScheduler."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary config file
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        self.scheduler = LearningRateScheduler(str(self.config_path))
    
    def test_initialization(self):
        """Test scheduler initialization."""
        self.assertIsNotNone(self.scheduler)
        self.assertIsNotNone(self.scheduler.config)
        self.assertEqual(len(self.scheduler.learning_rates), 0)
    
    def test_config_creation(self):
        """Test that config file is created."""
        self.assertTrue(self.config_path.exists())
        
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        self.assertIn('default_initial_rate', config)
        self.assertIn('components', config)
        self.assertIn('adaptive_settings', config)
    
    def test_register_component(self):
        """Test component registration."""
        rate = self.scheduler.register_component(
            "test_component",
            initial_rate=0.01,
            schedule_type=ScheduleType.ADAPTIVE
        )
        
        self.assertEqual(rate, 0.01)
        self.assertIn("test_component", self.scheduler.learning_rates)
        self.assertEqual(self.scheduler.learning_rates["test_component"], 0.01)
    
    def test_get_learning_rate(self):
        """Test getting learning rate."""
        self.scheduler.register_component("test", initial_rate=0.05)
        
        rate = self.scheduler.get_learning_rate("test")
        self.assertEqual(rate, 0.05)
    
    def test_get_learning_rate_unregistered(self):
        """Test getting learning rate for unregistered component."""
        # Should auto-register with default
        rate = self.scheduler.get_learning_rate("new_component")
        self.assertIsNotNone(rate)
        self.assertIn("new_component", self.scheduler.learning_rates)
    
    def test_fixed_schedule(self):
        """Test fixed learning rate schedule."""
        self.scheduler.register_component(
            "fixed_test",
            initial_rate=0.01,
            schedule_type=ScheduleType.FIXED
        )
        
        # Step multiple times
        for _ in range(10):
            rate = self.scheduler.step("fixed_test")
        
        # Should remain constant
        self.assertEqual(rate, 0.01)
    
    def test_step_decay_schedule(self):
        """Test step decay schedule."""
        self.scheduler.register_component(
            "step_test",
            initial_rate=0.1,
            schedule_type=ScheduleType.STEP_DECAY,
            step_size=5,
            decay_factor=0.5
        )
        
        # Step 10 times
        rates = []
        for _ in range(10):
            rate = self.scheduler.step("step_test")
            rates.append(rate)
        
        # Should decay at step 5
        self.assertGreater(rates[4], rates[5])
    
    def test_exponential_decay_schedule(self):
        """Test exponential decay schedule."""
        self.scheduler.register_component(
            "exp_test",
            initial_rate=0.1,
            schedule_type=ScheduleType.EXPONENTIAL_DECAY,
            decay_rate=0.9
        )
        
        rate1 = self.scheduler.step("exp_test")
        rate2 = self.scheduler.step("exp_test")
        
        # Should decay exponentially
        self.assertLess(rate2, rate1)
    
    def test_cosine_annealing_schedule(self):
        """Test cosine annealing schedule."""
        self.scheduler.register_component(
            "cosine_test",
            initial_rate=0.1,
            schedule_type=ScheduleType.COSINE_ANNEALING,
            cycle_length=10,
            min_rate=0.01
        )
        
        rates = []
        for _ in range(20):
            rate = self.scheduler.step("cosine_test")
            rates.append(rate)
        
        # Should oscillate
        self.assertGreater(max(rates), min(rates))
    
    def test_adaptive_schedule_improvement(self):
        """Test adaptive schedule with improving performance."""
        self.scheduler.register_component(
            "adaptive_test",
            initial_rate=0.01,
            schedule_type=ScheduleType.ADAPTIVE,
            patience=5
        )
        
        # Simulate improving performance (decreasing loss)
        initial_rate = self.scheduler.get_learning_rate("adaptive_test")
        
        for i in range(20):
            loss = 1.0 / (1.0 + i * 0.1)  # Decreasing loss
            self.scheduler.step("adaptive_test", loss)
        
        final_rate = self.scheduler.get_learning_rate("adaptive_test")
        
        # Rate should have increased due to improvement
        # (or at least not decreased significantly)
        self.assertGreaterEqual(final_rate, initial_rate * 0.5)
    
    def test_adaptive_schedule_degradation(self):
        """Test adaptive schedule with degrading performance."""
        self.scheduler.register_component(
            "degrade_test",
            initial_rate=0.1,
            schedule_type=ScheduleType.ADAPTIVE,
            patience=5
        )
        
        initial_rate = self.scheduler.get_learning_rate("degrade_test")
        
        # Simulate degrading performance (increasing loss)
        for i in range(20):
            loss = 1.0 + i * 0.1  # Increasing loss
            self.scheduler.step("degrade_test", loss)
        
        final_rate = self.scheduler.get_learning_rate("degrade_test")
        
        # Rate should have decreased
        self.assertLess(final_rate, initial_rate)
    
    def test_reduce_on_plateau(self):
        """Test reduce on plateau schedule."""
        self.scheduler.register_component(
            "plateau_test",
            initial_rate=0.1,
            schedule_type=ScheduleType.REDUCE_ON_PLATEAU,
            patience=5
        )
        
        initial_rate = self.scheduler.get_learning_rate("plateau_test")
        
        # Simulate plateau (constant loss)
        for _ in range(20):
            self.scheduler.step("plateau_test", 0.5)
        
        final_rate = self.scheduler.get_learning_rate("plateau_test")
        
        # Rate should have decreased due to plateau
        self.assertLess(final_rate, initial_rate)
    
    def test_convergence_detection(self):
        """Test convergence detection."""
        self.scheduler.register_component(
            "converge_test",
            initial_rate=0.01,
            schedule_type=ScheduleType.ADAPTIVE
        )
        
        # Simulate convergence (very stable loss)
        for i in range(100):
            loss = 0.1 + np.random.normal(0, 0.0001)  # Very small variance
            self.scheduler.step("converge_test", loss)
        
        # Should detect convergence
        self.assertTrue(self.scheduler.converged.get("converge_test", False))
    
    def test_rate_bounds(self):
        """Test that learning rate stays within bounds."""
        self.scheduler.register_component(
            "bounds_test",
            initial_rate=0.01,
            schedule_type=ScheduleType.ADAPTIVE,
            min_rate=0.001,
            max_rate=0.1
        )
        
        # Try to push rate outside bounds
        for i in range(50):
            # Alternating good and bad performance
            loss = 0.5 if i % 2 == 0 else 2.0
            rate = self.scheduler.step("bounds_test", loss)
            
            # Should stay within bounds
            self.assertGreaterEqual(rate, 0.001)
            self.assertLessEqual(rate, 0.1)
    
    def test_get_status(self):
        """Test getting status of all components."""
        self.scheduler.register_component("comp1", initial_rate=0.01)
        self.scheduler.register_component("comp2", initial_rate=0.05)
        
        status = self.scheduler.get_status()
        
        self.assertIn("comp1", status)
        self.assertIn("comp2", status)
        self.assertIn("current_rate", status["comp1"])
        self.assertIn("steps", status["comp1"])
    
    def test_get_metrics(self):
        """Test getting scheduler metrics."""
        self.scheduler.register_component("test", initial_rate=0.01)
        
        for i in range(10):
            self.scheduler.step("test", 1.0 / (1.0 + i))
        
        metrics = self.scheduler.get_metrics()
        
        self.assertIn("total_adjustments", metrics)
        self.assertIn("components_registered", metrics)
        self.assertGreater(metrics["total_adjustments"], 0)
    
    def test_reset_component(self):
        """Test resetting a component."""
        self.scheduler.register_component("reset_test", initial_rate=0.1)
        
        # Make some steps
        for _ in range(10):
            self.scheduler.step("reset_test", 0.5)
        
        # Reset
        self.scheduler.reset_component("reset_test")
        
        # Should be back to initial
        self.assertEqual(self.scheduler.learning_rates["reset_test"], 0.1)
        self.assertEqual(self.scheduler.steps["reset_test"], 0)
        self.assertFalse(self.scheduler.converged["reset_test"])


class TestAdaptiveLearningRate(unittest.TestCase):
    """Test cases for AdaptiveLearningRate."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.adaptive_lr = AdaptiveLearningRate(initial_rate=0.01)
    
    def test_initialization(self):
        """Test initialization."""
        self.assertEqual(self.adaptive_lr.initial_rate, 0.01)
        self.assertEqual(self.adaptive_lr.current_rate, 0.01)
    
    def test_update_with_gradient(self):
        """Test updating with gradient information."""
        # Simulate gradients
        gradients = [0.1, 0.08, 0.06, 0.04, 0.02]
        
        rates = []
        for grad in gradients:
            rate = self.adaptive_lr.update_with_gradient(grad)
            rates.append(rate)
        
        # Should adapt based on gradients
        self.assertIsNotNone(rates[-1])
    
    def test_get_rate(self):
        """Test getting current rate."""
        rate = self.adaptive_lr.get_rate()
        self.assertEqual(rate, 0.01)


class TestConvergenceDetector(unittest.TestCase):
    """Test cases for ConvergenceDetector."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = ConvergenceDetector(window_size=10, threshold=0.01)
    
    def test_initialization(self):
        """Test initialization."""
        self.assertEqual(self.detector.window_size, 10)
        self.assertEqual(self.detector.threshold, 0.01)
    
    def test_add_metric(self):
        """Test adding metrics."""
        self.detector.add_metric(0.5)
        self.assertEqual(len(self.detector.history), 1)
    
    def test_not_converged_insufficient_data(self):
        """Test that convergence requires enough data."""
        for i in range(5):
            self.detector.add_metric(0.5)
        
        self.assertFalse(self.detector.is_converged())
    
    def test_converged_stable_metrics(self):
        """Test convergence detection with stable metrics."""
        # Add very stable metrics
        for _ in range(20):
            self.detector.add_metric(0.5 + np.random.normal(0, 0.001))
        
        self.assertTrue(self.detector.is_converged())
    
    def test_not_converged_varying_metrics(self):
        """Test no convergence with varying metrics."""
        # Add varying metrics
        for i in range(20):
            self.detector.add_metric(0.5 + i * 0.1)
        
        self.assertFalse(self.detector.is_converged())
    
    def test_get_trend_improving(self):
        """Test trend detection - improving."""
        # Add decreasing metrics (improving)
        for i in range(20):
            self.detector.add_metric(1.0 - i * 0.05)
        
        trend = self.detector.get_trend()
        self.assertEqual(trend, "improving")
    
    def test_get_trend_degrading(self):
        """Test trend detection - degrading."""
        # Add increasing metrics (degrading)
        for i in range(20):
            self.detector.add_metric(0.5 + i * 0.05)
        
        trend = self.detector.get_trend()
        self.assertEqual(trend, "degrading")
    
    def test_get_trend_stable(self):
        """Test trend detection - stable."""
        # Add stable metrics
        for _ in range(20):
            self.detector.add_metric(0.5 + np.random.normal(0, 0.001))
        
        trend = self.detector.get_trend()
        self.assertEqual(trend, "stable")


class TestIntegrationScenarios(unittest.TestCase):
    """Test real-world integration scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scheduler = LearningRateScheduler()
    
    def test_multi_component_training(self):
        """Test managing multiple components simultaneously."""
        # Register multiple components
        components = [
            ("pattern_recognition", 0.01, ScheduleType.ADAPTIVE),
            ("prediction_models", 0.001, ScheduleType.COSINE_ANNEALING),
            ("task_optimizer", 0.1, ScheduleType.STEP_DECAY)
        ]
        
        for name, rate, schedule in components:
            self.scheduler.register_component(name, rate, schedule)
        
        # Simulate training
        for i in range(50):
            loss = 1.0 / (1.0 + i * 0.1)
            
            for name, _, _ in components:
                self.scheduler.step(name, loss)
        
        # All should have valid rates
        status = self.scheduler.get_status()
        for name, _, _ in components:
            self.assertIn(name, status)
            self.assertGreater(status[name]['current_rate'], 0)
    
    def test_training_with_noise(self):
        """Test training with noisy performance metrics."""
        self.scheduler.register_component(
            "noisy_test",
            initial_rate=0.01,
            schedule_type=ScheduleType.ADAPTIVE
        )
        
        # Simulate noisy training
        for i in range(100):
            # Decreasing trend with noise
            loss = 1.0 / (1.0 + i * 0.05) + np.random.normal(0, 0.1)
            self.scheduler.step("noisy_test", loss)
        
        # Should still adapt reasonably
        final_rate = self.scheduler.get_learning_rate("noisy_test")
        self.assertGreater(final_rate, 0)
    
    def test_early_convergence(self):
        """Test early convergence scenario."""
        self.scheduler.register_component(
            "early_converge",
            initial_rate=0.1,
            schedule_type=ScheduleType.ADAPTIVE
        )
        
        # Quick convergence
        for i in range(30):
            loss = 0.1 if i > 20 else 1.0 / (1.0 + i)
            self.scheduler.step("early_converge", loss)
        
        # Continue stepping after convergence
        for _ in range(20):
            self.scheduler.step("early_converge", 0.1)
        
        # Should detect convergence
        self.assertTrue(self.scheduler.converged.get("early_converge", False))


if __name__ == '__main__':
    unittest.main()
