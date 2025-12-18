#!/usr/bin/env python3
"""
Tests for Adaptive Algorithms

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

from self_improvement.adaptive_algorithms import (
    AdaptiveAlgorithms,
    AdaptationStrategy,
    ConvergenceStatus,
    AlgorithmState,
    BanditArm,
    AdaptationResult
)


class TestAdaptiveAlgorithms(unittest.TestCase):
    """Test cases for AdaptiveAlgorithms."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.adaptive = AdaptiveAlgorithms(data_dir=self.test_dir)
        random.seed(42)  # For reproducibility
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test adaptive algorithms initialization."""
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertIsInstance(self.adaptive.algorithms, dict)
        self.assertIsInstance(self.adaptive.bandits, dict)
    
    def test_create_algorithm(self):
        """Test creating an adaptive algorithm."""
        algo = self.adaptive.create_algorithm(
            'test_algo',
            'gradient_descent',
            {'learning_rate': 0.01}
        )
        
        self.assertIsInstance(algo, AlgorithmState)
        self.assertEqual(algo.algorithm_id, 'test_algo')
        self.assertIn('test_algo', self.adaptive.algorithms)
    
    def test_create_bandit(self):
        """Test creating a multi-armed bandit."""
        arms = self.adaptive.create_bandit('test_bandit', ['arm1', 'arm2', 'arm3'])
        
        self.assertEqual(len(arms), 3)
        self.assertIn('test_bandit', self.adaptive.bandits)
    
    def test_select_arm_epsilon_greedy(self):
        """Test epsilon-greedy arm selection."""
        self.adaptive.create_bandit('test_bandit', ['arm1', 'arm2'])
        
        # Should select an arm
        arm = self.adaptive.select_arm_epsilon_greedy('test_bandit', epsilon=0.1)
        self.assertIn(arm, ['arm1', 'arm2'])
    
    def test_select_arm_ucb(self):
        """Test UCB arm selection."""
        self.adaptive.create_bandit('test_bandit', ['arm1', 'arm2', 'arm3'])
        
        # Should select an arm
        arm = self.adaptive.select_arm_ucb('test_bandit')
        self.assertIn(arm, ['arm1', 'arm2', 'arm3'])
    
    def test_update_bandit(self):
        """Test updating bandit after pulling arm."""
        self.adaptive.create_bandit('test_bandit', ['arm1', 'arm2'])
        
        # Pull arm and update
        self.adaptive.update_bandit('test_bandit', 'arm1', 1.0)
        
        bandit = self.adaptive.bandits['test_bandit']
        self.assertEqual(bandit['arms']['arm1']['pulls'], 1)
        self.assertEqual(bandit['arms']['arm1']['total_reward'], 1.0)
        self.assertEqual(bandit['total_pulls'], 1)
    
    def test_bandit_learns_best_arm(self):
        """Test that bandit learns to select best arm."""
        self.adaptive.create_bandit('test_bandit', ['bad_arm', 'good_arm'])
        
        # Simulate many pulls with different rewards
        for i in range(100):
            arm = self.adaptive.select_arm_ucb('test_bandit')
            
            # good_arm gives higher reward
            if arm == 'good_arm':
                reward = random.gauss(0.8, 0.1)
            else:
                reward = random.gauss(0.3, 0.1)
            
            self.adaptive.update_bandit('test_bandit', arm, reward)
        
        # Best arm should be good_arm
        best_arm, best_reward = self.adaptive.get_best_arm('test_bandit')
        self.assertEqual(best_arm, 'good_arm')
        self.assertGreater(best_reward, 0.5)
    
    def test_adapt_parameters_gradient(self):
        """Test gradient-based parameter adaptation."""
        self.adaptive.create_algorithm(
            'test_algo',
            'gradient_descent',
            {'param1': 1.0}
        )
        
        # Simulate improving performance
        for i in range(10):
            performance = 0.5 + i * 0.05
            params = self.adaptive.adapt_parameters_gradient(
                'test_algo',
                performance,
                learning_rate=0.01
            )
        
        algo = self.adaptive.algorithms['test_algo']
        self.assertEqual(len(algo['performance_history']), 10)
        self.assertGreater(algo['best_performance'], 0.5)
    
    def test_adapt_parameters_simulated_annealing(self):
        """Test simulated annealing parameter adaptation."""
        self.adaptive.create_algorithm(
            'test_algo',
            'simulated_annealing',
            {'param1': 1.0}
        )
        
        # Simulate adaptation
        for i in range(10):
            performance = 0.5 + random.gauss(0, 0.1)
            params = self.adaptive.adapt_parameters_simulated_annealing(
                'test_algo',
                performance,
                temperature=1.0,
                cooling_rate=0.95
            )
        
        algo = self.adaptive.algorithms['test_algo']
        self.assertEqual(len(algo['performance_history']), 10)
        self.assertIn('temperature', algo['metadata'])
    
    def test_convergence_detection_exploring(self):
        """Test convergence detection in exploring phase."""
        # Not enough data
        history = [0.5, 0.6, 0.7]
        status = self.adaptive._check_convergence(history, window_size=10)
        self.assertEqual(status, ConvergenceStatus.EXPLORING)
    
    def test_convergence_detection_converged(self):
        """Test convergence detection when converged."""
        # Stable performance
        history = [0.9] * 15
        status = self.adaptive._check_convergence(history, window_size=10)
        self.assertEqual(status, ConvergenceStatus.CONVERGED)
    
    def test_convergence_detection_converging(self):
        """Test convergence detection when converging."""
        # Slowly improving
        history = [0.5 + i * 0.01 for i in range(15)]
        status = self.adaptive._check_convergence(history, window_size=10, threshold=0.05)
        self.assertIn(status, [ConvergenceStatus.CONVERGING, ConvergenceStatus.CONVERGED])
    
    def test_auto_tune_parameter(self):
        """Test automatic parameter tuning."""
        self.adaptive.create_algorithm(
            'test_algo',
            'auto_tune',
            {'param1': 0.5}
        )
        
        # Define performance function (peaks at 0.7)
        def perf_func(x):
            return 1.0 - abs(x - 0.7)
        
        # Auto-tune
        best_value, best_perf = self.adaptive.auto_tune_parameter(
            'test_algo',
            'param1',
            min_value=0.0,
            max_value=1.0,
            performance_function=perf_func,
            iterations=10
        )
        
        # Should find value close to 0.7
        self.assertGreater(best_value, 0.6)
        self.assertLess(best_value, 0.8)
        self.assertGreater(best_perf, 0.9)
    
    def test_select_strategy_dynamically(self):
        """Test dynamic strategy selection."""
        strategies = ['strategy_a', 'strategy_b', 'strategy_c']
        
        strategy = self.adaptive.select_strategy_dynamically(
            context={},
            available_strategies=strategies,
            bandit_id='strategy_selector'
        )
        
        self.assertIn(strategy, strategies)
        self.assertIn('strategy_selector', self.adaptive.bandits)
    
    def test_record_adaptation_result(self):
        """Test recording adaptation results."""
        self.adaptive.create_algorithm(
            'test_algo',
            'test',
            {'param1': 1.0}
        )
        
        result = self.adaptive.record_adaptation_result(
            'test_algo',
            selected_action='action1',
            performance=0.85,
            parameters_updated={'param1': 1.1}
        )
        
        self.assertIsInstance(result, AdaptationResult)
        self.assertEqual(result.algorithm_id, 'test_algo')
        self.assertEqual(len(self.adaptive.results), 1)
    
    def test_get_algorithm_state(self):
        """Test getting algorithm state."""
        self.adaptive.create_algorithm(
            'test_algo',
            'test',
            {'param1': 1.0}
        )
        
        state = self.adaptive.get_algorithm_state('test_algo')
        
        self.assertIsNotNone(state)
        self.assertEqual(state['algorithm_id'], 'test_algo')
    
    def test_get_bandit_state(self):
        """Test getting bandit state."""
        self.adaptive.create_bandit('test_bandit', ['arm1', 'arm2'])
        
        state = self.adaptive.get_bandit_state('test_bandit')
        
        self.assertIsNotNone(state)
        self.assertEqual(state['bandit_id'], 'test_bandit')
    
    def test_get_best_arm(self):
        """Test getting best arm from bandit."""
        self.adaptive.create_bandit('test_bandit', ['arm1', 'arm2'])
        
        # Update with different rewards
        self.adaptive.update_bandit('test_bandit', 'arm1', 0.5)
        self.adaptive.update_bandit('test_bandit', 'arm2', 0.9)
        
        best_arm, best_reward = self.adaptive.get_best_arm('test_bandit')
        
        self.assertEqual(best_arm, 'arm2')
        self.assertGreater(best_reward, 0.8)
    
    def test_get_performance_summary(self):
        """Test getting performance summary."""
        self.adaptive.create_algorithm(
            'test_algo',
            'test',
            {'param1': 1.0}
        )
        
        # Add some performance data
        for i in range(5):
            self.adaptive.adapt_parameters_gradient('test_algo', 0.5 + i * 0.1)
        
        summary = self.adaptive.get_performance_summary('test_algo')
        
        self.assertIn('iterations', summary)
        self.assertIn('best_performance', summary)
        self.assertIn('convergence_status', summary)
        self.assertEqual(summary['iterations'], 5)
    
    def test_reset_algorithm(self):
        """Test resetting algorithm."""
        self.adaptive.create_algorithm(
            'test_algo',
            'test',
            {'param1': 1.0}
        )
        
        # Add performance data
        self.adaptive.adapt_parameters_gradient('test_algo', 0.8)
        
        # Reset
        self.adaptive.reset_algorithm('test_algo', keep_history=False)
        
        algo = self.adaptive.algorithms['test_algo']
        self.assertEqual(algo['iteration'], 0)
        self.assertEqual(len(algo['performance_history']), 0)
    
    def test_compare_strategies(self):
        """Test comparing strategies."""
        self.adaptive.create_bandit('test_bandit', ['strategy_a', 'strategy_b'])
        
        # Add different performance
        for i in range(10):
            self.adaptive.update_bandit('test_bandit', 'strategy_a', 0.5)
            self.adaptive.update_bandit('test_bandit', 'strategy_b', 0.8)
        
        comparison = self.adaptive.compare_strategies('test_bandit')
        
        self.assertEqual(len(comparison), 2)
        # strategy_b should be first (better)
        self.assertEqual(comparison[0]['strategy'], 'strategy_b')
        self.assertGreater(comparison[0]['average_reward'], comparison[1]['average_reward'])
    
    def test_persistence(self):
        """Test that data persists across instances."""
        self.adaptive.create_algorithm(
            'test_algo',
            'test',
            {'param1': 1.0}
        )
        self.adaptive.create_bandit('test_bandit', ['arm1', 'arm2'])
        
        # Create new instance
        adaptive2 = AdaptiveAlgorithms(data_dir=self.test_dir)
        
        # Should load saved data
        self.assertIn('test_algo', adaptive2.algorithms)
        self.assertIn('test_bandit', adaptive2.bandits)
    
    def test_epsilon_greedy_exploration(self):
        """Test that epsilon-greedy explores."""
        self.adaptive.create_bandit('test_bandit', ['arm1', 'arm2'])
        
        # Make arm1 clearly better
        for i in range(20):
            self.adaptive.update_bandit('test_bandit', 'arm1', 1.0)
        
        # With epsilon=1.0, should still explore
        selections = []
        for i in range(10):
            arm = self.adaptive.select_arm_epsilon_greedy('test_bandit', epsilon=1.0)
            selections.append(arm)
        
        # Should have selected both arms
        self.assertGreater(len(set(selections)), 1)
    
    def test_ucb_exploration_bonus(self):
        """Test that UCB gives exploration bonus to less-pulled arms."""
        self.adaptive.create_bandit('test_bandit', ['arm1', 'arm2'])
        
        # Pull arm1 many times
        for i in range(20):
            self.adaptive.update_bandit('test_bandit', 'arm1', 0.5)
        
        # UCB should select arm2 (less pulled)
        arm = self.adaptive.select_arm_ucb('test_bandit')
        self.assertEqual(arm, 'arm2')


class TestBanditArm(unittest.TestCase):
    """Test cases for BanditArm dataclass."""
    
    def test_arm_creation(self):
        """Test creating a bandit arm."""
        arm = BanditArm(
            arm_id="arm_001",
            name="test_arm"
        )
        
        self.assertEqual(arm.arm_id, "arm_001")
        self.assertEqual(arm.pulls, 0)
        self.assertEqual(arm.average_reward, 0.0)
    
    def test_average_reward_calculation(self):
        """Test average reward calculation."""
        arm = BanditArm(
            arm_id="arm_001",
            name="test_arm",
            pulls=5,
            total_reward=2.5
        )
        
        self.assertEqual(arm.average_reward, 0.5)


class TestAlgorithmState(unittest.TestCase):
    """Test cases for AlgorithmState dataclass."""
    
    def test_state_creation(self):
        """Test creating algorithm state."""
        state = AlgorithmState(
            algorithm_id="algo_001",
            algorithm_type="gradient_descent",
            parameters={'learning_rate': 0.01}
        )
        
        self.assertEqual(state.algorithm_id, "algo_001")
        self.assertEqual(state.iteration, 0)
        self.assertEqual(state.convergence_status, ConvergenceStatus.NOT_STARTED.value)


if __name__ == '__main__':
    unittest.main()
