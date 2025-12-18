#!/usr/bin/env python3
"""
Learning Rate Adjustment System

Adaptive learning rate adjustment that dynamically optimizes learning rates
across all learning components based on performance feedback.

Author: Vy Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from collections import deque
import numpy as np


class ScheduleType(Enum):
    """Types of learning rate schedules."""
    FIXED = "fixed"
    STEP_DECAY = "step_decay"
    EXPONENTIAL_DECAY = "exponential_decay"
    POLYNOMIAL_DECAY = "polynomial_decay"
    COSINE_ANNEALING = "cosine_annealing"
    ADAPTIVE = "adaptive"
    CYCLICAL = "cyclical"
    WARM_RESTART = "warm_restart"
    REDUCE_ON_PLATEAU = "reduce_on_plateau"


@dataclass
class LearningRateConfig:
    """Configuration for learning rate adjustment."""
    initial_rate: float
    min_rate: float = 1e-6
    max_rate: float = 1.0
    schedule_type: ScheduleType = ScheduleType.ADAPTIVE
    
    # Step decay parameters
    step_size: int = 100
    decay_factor: float = 0.5
    
    # Exponential decay parameters
    decay_rate: float = 0.95
    
    # Adaptive parameters
    patience: int = 10
    improvement_threshold: float = 0.01
    increase_factor: float = 1.1
    decrease_factor: float = 0.5
    
    # Cyclical parameters
    cycle_length: int = 100
    cycle_mult: float = 2.0
    
    # Convergence detection
    convergence_window: int = 20
    convergence_threshold: float = 0.001


class LearningRateScheduler:
    """
    Main learning rate scheduling system.
    
    Manages learning rates across multiple components with various
    scheduling strategies and adaptive adjustment.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the learning rate scheduler.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or str(Path.home() / "Lords Love" / "learning_rate_config.json")
        self.config = self._load_config()
        
        # Component learning rates
        self.learning_rates: Dict[str, float] = {}
        self.rate_configs: Dict[str, LearningRateConfig] = {}
        
        # Performance history
        self.performance_history: Dict[str, deque] = {}
        
        # Step counters
        self.steps: Dict[str, int] = {}
        
        # Convergence tracking
        self.converged: Dict[str, bool] = {}
        
        # Metrics
        self.metrics = {
            'total_adjustments': 0,
            'improvements': 0,
            'degradations': 0,
            'plateaus_detected': 0,
            'convergences': 0
        }
        
        self.logger.info("Learning Rate Scheduler initialized")
    
    def _load_config(self) -> Dict:
        """Load configuration from file or create default."""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load config: {e}")
        
        # Default configuration
        default_config = {
            'default_initial_rate': 0.01,
            'default_schedule': 'adaptive',
            'global_min_rate': 1e-6,
            'global_max_rate': 1.0,
            'components': {
                'pattern_recognition': {
                    'initial_rate': 0.01,
                    'schedule': 'adaptive',
                    'patience': 10
                },
                'prediction_models': {
                    'initial_rate': 0.001,
                    'schedule': 'cosine_annealing',
                    'cycle_length': 100
                },
                'task_optimizer': {
                    'initial_rate': 0.1,
                    'schedule': 'step_decay',
                    'step_size': 50
                },
                'adaptive_algorithms': {
                    'initial_rate': 0.05,
                    'schedule': 'adaptive',
                    'patience': 15
                }
            },
            'adaptive_settings': {
                'patience': 10,
                'improvement_threshold': 0.01,
                'increase_factor': 1.1,
                'decrease_factor': 0.5
            },
            'convergence_settings': {
                'window_size': 20,
                'threshold': 0.001,
                'min_steps': 50
            }
        }
        
        # Save default config
        try:
            Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not save default config: {e}")
        
        return default_config
    
    def register_component(self, 
                          component_name: str,
                          initial_rate: Optional[float] = None,
                          schedule_type: Optional[ScheduleType] = None,
                          **kwargs) -> float:
        """
        Register a component for learning rate management.
        
        Args:
            component_name: Name of the component
            initial_rate: Initial learning rate (uses config if None)
            schedule_type: Schedule type (uses config if None)
            **kwargs: Additional schedule parameters
        
        Returns:
            Initial learning rate for the component
        """
        # Get component config
        component_config = self.config.get('components', {}).get(component_name, {})
        
        # Determine initial rate
        if initial_rate is None:
            initial_rate = component_config.get('initial_rate', 
                                               self.config.get('default_initial_rate', 0.01))
        
        # Determine schedule type
        if schedule_type is None:
            schedule_name = component_config.get('schedule', 
                                                self.config.get('default_schedule', 'adaptive'))
            schedule_type = ScheduleType(schedule_name)
        
        # Create config
        config_params = {
            'initial_rate': initial_rate,
            'min_rate': self.config.get('global_min_rate', 1e-6),
            'max_rate': self.config.get('global_max_rate', 1.0),
            'schedule_type': schedule_type
        }
        
        # Add schedule-specific parameters
        config_params.update(kwargs)
        config_params.update(component_config)
        
        # Create config object
        self.rate_configs[component_name] = LearningRateConfig(**config_params)
        
        # Initialize
        self.learning_rates[component_name] = initial_rate
        self.performance_history[component_name] = deque(maxlen=100)
        self.steps[component_name] = 0
        self.converged[component_name] = False
        
        self.logger.info(f"Registered {component_name} with initial rate {initial_rate} ({schedule_type.value})")
        
        return initial_rate
    
    def get_learning_rate(self, component_name: str) -> float:
        """
        Get current learning rate for a component.
        
        Args:
            component_name: Name of the component
        
        Returns:
            Current learning rate
        """
        if component_name not in self.learning_rates:
            self.logger.warning(f"Component {component_name} not registered, using default")
            return self.register_component(component_name)
        
        return self.learning_rates[component_name]
    
    def step(self, 
            component_name: str,
            performance_metric: Optional[float] = None) -> float:
        """
        Update learning rate for a component.
        
        Args:
            component_name: Name of the component
            performance_metric: Current performance (lower is better, e.g., loss)
        
        Returns:
            New learning rate
        """
        if component_name not in self.learning_rates:
            return self.register_component(component_name)
        
        config = self.rate_configs[component_name]
        self.steps[component_name] += 1
        step = self.steps[component_name]
        
        # Record performance
        if performance_metric is not None:
            self.performance_history[component_name].append(performance_metric)
        
        # Check convergence
        if self._check_convergence(component_name):
            self.converged[component_name] = True
            self.metrics['convergences'] += 1
            self.logger.info(f"{component_name} has converged")
            return self.learning_rates[component_name]
        
        # Apply schedule
        old_rate = self.learning_rates[component_name]
        
        if config.schedule_type == ScheduleType.FIXED:
            new_rate = config.initial_rate
        
        elif config.schedule_type == ScheduleType.STEP_DECAY:
            new_rate = self._step_decay(config, step)
        
        elif config.schedule_type == ScheduleType.EXPONENTIAL_DECAY:
            new_rate = self._exponential_decay(config, step)
        
        elif config.schedule_type == ScheduleType.COSINE_ANNEALING:
            new_rate = self._cosine_annealing(config, step)
        
        elif config.schedule_type == ScheduleType.ADAPTIVE:
            new_rate = self._adaptive_adjustment(component_name, config)
        
        elif config.schedule_type == ScheduleType.REDUCE_ON_PLATEAU:
            new_rate = self._reduce_on_plateau(component_name, config)
        
        else:
            new_rate = old_rate
        
        # Clamp to bounds
        new_rate = max(config.min_rate, min(config.max_rate, new_rate))
        
        # Update
        self.learning_rates[component_name] = new_rate
        self.metrics['total_adjustments'] += 1
        
        if new_rate != old_rate:
            self.logger.debug(f"{component_name}: {old_rate:.6f} -> {new_rate:.6f}")
        
        return new_rate
    
    def _step_decay(self, config: LearningRateConfig, step: int) -> float:
        """Calculate step decay learning rate."""
        decay_steps = step // config.step_size
        return config.initial_rate * (config.decay_factor ** decay_steps)
    
    def _exponential_decay(self, config: LearningRateConfig, step: int) -> float:
        """Calculate exponential decay learning rate."""
        return config.initial_rate * (config.decay_rate ** step)
    
    def _cosine_annealing(self, config: LearningRateConfig, step: int) -> float:
        """Calculate cosine annealing learning rate."""
        cycle = step % config.cycle_length
        return config.min_rate + (config.initial_rate - config.min_rate) * \
               (1 + math.cos(math.pi * cycle / config.cycle_length)) / 2
    
    def _adaptive_adjustment(self, component_name: str, config: LearningRateConfig) -> float:
        """Adaptively adjust learning rate based on performance."""
        history = self.performance_history[component_name]
        current_rate = self.learning_rates[component_name]
        
        if len(history) < config.patience + 1:
            return current_rate
        
        # Check recent performance
        recent = list(history)[-config.patience:]
        previous = list(history)[-(config.patience + 1):-1]
        
        recent_avg = np.mean(recent)
        previous_avg = np.mean(previous)
        
        improvement = (previous_avg - recent_avg) / (previous_avg + 1e-10)
        
        if improvement > config.improvement_threshold:
            # Performance improving - can increase rate
            new_rate = current_rate * config.increase_factor
            self.metrics['improvements'] += 1
        elif improvement < -config.improvement_threshold:
            # Performance degrading - decrease rate
            new_rate = current_rate * config.decrease_factor
            self.metrics['degradations'] += 1
        else:
            # Plateau - slightly decrease
            new_rate = current_rate * 0.95
            self.metrics['plateaus_detected'] += 1
        
        return new_rate
    
    def _reduce_on_plateau(self, component_name: str, config: LearningRateConfig) -> float:
        """Reduce learning rate when performance plateaus."""
        history = self.performance_history[component_name]
        current_rate = self.learning_rates[component_name]
        
        if len(history) < config.patience:
            return current_rate
        
        recent = list(history)[-config.patience:]
        
        # Check if plateaued (small variance)
        if len(recent) > 1:
            variance = np.var(recent)
            if variance < config.improvement_threshold:
                # Plateau detected
                self.metrics['plateaus_detected'] += 1
                return current_rate * config.decrease_factor
        
        return current_rate
    
    def _check_convergence(self, component_name: str) -> bool:
        """Check if component has converged."""
        if self.converged.get(component_name, False):
            return True
        
        config = self.rate_configs[component_name]
        history = self.performance_history[component_name]
        
        # Need minimum steps
        convergence_config = self.config.get('convergence_settings', {})
        min_steps = convergence_config.get('min_steps', 50)
        
        if self.steps[component_name] < min_steps:
            return False
        
        # Need enough history
        window_size = convergence_config.get('window_size', 20)
        if len(history) < window_size:
            return False
        
        # Check variance in recent window
        recent = list(history)[-window_size:]
        variance = np.var(recent)
        threshold = convergence_config.get('threshold', 0.001)
        
        return variance < threshold
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all components."""
        status = {}
        
        for component_name in self.learning_rates.keys():
            config = self.rate_configs[component_name]
            history = self.performance_history[component_name]
            
            status[component_name] = {
                'current_rate': self.learning_rates[component_name],
                'initial_rate': config.initial_rate,
                'schedule': config.schedule_type.value,
                'steps': self.steps[component_name],
                'converged': self.converged[component_name],
                'history_length': len(history),
                'recent_performance': list(history)[-5:] if history else []
            }
        
        return status
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get scheduler metrics."""
        return {
            'total_adjustments': self.metrics['total_adjustments'],
            'improvements': self.metrics['improvements'],
            'degradations': self.metrics['degradations'],
            'plateaus_detected': self.metrics['plateaus_detected'],
            'convergences': self.metrics['convergences'],
            'components_registered': len(self.learning_rates),
            'components_converged': sum(self.converged.values())
        }
    
    def reset_component(self, component_name: str):
        """Reset a component's learning rate to initial value."""
        if component_name in self.rate_configs:
            config = self.rate_configs[component_name]
            self.learning_rates[component_name] = config.initial_rate
            self.steps[component_name] = 0
            self.converged[component_name] = False
            self.performance_history[component_name].clear()
            self.logger.info(f"Reset {component_name} to initial rate {config.initial_rate}")


class AdaptiveLearningRate:
    """
    Advanced adaptive learning rate adjustment.
    
    Uses gradient information and second-order statistics for
    more sophisticated learning rate adaptation.
    """
    
    def __init__(self, initial_rate: float = 0.01):
        """
        Initialize adaptive learning rate.
        
        Args:
            initial_rate: Initial learning rate
        """
        self.initial_rate = initial_rate
        self.current_rate = initial_rate
        
        # Momentum terms
        self.momentum = 0.9
        self.velocity = 0.0
        
        # RMSprop terms
        self.decay_rate = 0.99
        self.squared_gradient = 0.0
        
        # Adam terms
        self.beta1 = 0.9
        self.beta2 = 0.999
        self.m = 0.0  # First moment
        self.v = 0.0  # Second moment
        self.t = 0    # Time step
        
        self.epsilon = 1e-8
    
    def update_with_gradient(self, gradient: float) -> float:
        """
        Update learning rate using gradient information.
        
        Args:
            gradient: Current gradient
        
        Returns:
            Adjusted learning rate
        """
        self.t += 1
        
        # Update biased first moment estimate
        self.m = self.beta1 * self.m + (1 - self.beta1) * gradient
        
        # Update biased second raw moment estimate
        self.v = self.beta2 * self.v + (1 - self.beta2) * (gradient ** 2)
        
        # Compute bias-corrected moments
        m_hat = self.m / (1 - self.beta1 ** self.t)
        v_hat = self.v / (1 - self.beta2 ** self.t)
        
        # Adjust learning rate based on second moment
        self.current_rate = self.initial_rate / (np.sqrt(v_hat) + self.epsilon)
        
        return self.current_rate
    
    def get_rate(self) -> float:
        """Get current learning rate."""
        return self.current_rate


class ConvergenceDetector:
    """
    Detects convergence in learning processes.
    """
    
    def __init__(self, window_size: int = 20, threshold: float = 0.001):
        """
        Initialize convergence detector.
        
        Args:
            window_size: Size of window for variance calculation
            threshold: Variance threshold for convergence
        """
        self.window_size = window_size
        self.threshold = threshold
        self.history = deque(maxlen=window_size)
    
    def add_metric(self, metric: float):
        """Add a performance metric."""
        self.history.append(metric)
    
    def is_converged(self) -> bool:
        """Check if process has converged."""
        if len(self.history) < self.window_size:
            return False
        
        variance = np.var(list(self.history))
        return variance < self.threshold
    
    def get_trend(self) -> str:
        """Get trend direction (improving, degrading, stable)."""
        if len(self.history) < 2:
            return "unknown"
        
        recent = list(self.history)[-10:]
        if len(recent) < 2:
            return "unknown"
        
        # Linear regression to find trend
        x = np.arange(len(recent))
        y = np.array(recent)
        
        slope = np.polyfit(x, y, 1)[0]
        
        if slope < -0.01:
            return "improving"
        elif slope > 0.01:
            return "degrading"
        else:
            return "stable"


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create scheduler
    scheduler = LearningRateScheduler()
    
    # Register components
    scheduler.register_component("pattern_recognition", initial_rate=0.01)
    scheduler.register_component("prediction_models", initial_rate=0.001, 
                                schedule_type=ScheduleType.COSINE_ANNEALING)
    
    # Simulate training
    print("\nSimulating training...")
    for i in range(100):
        # Simulate decreasing loss
        loss = 1.0 / (1.0 + i * 0.1) + np.random.normal(0, 0.01)
        
        # Update learning rates
        lr1 = scheduler.step("pattern_recognition", loss)
        lr2 = scheduler.step("prediction_models", loss)
        
        if i % 20 == 0:
            print(f"Step {i}: pattern_recognition={lr1:.6f}, prediction_models={lr2:.6f}, loss={loss:.4f}")
    
    # Get status
    status = scheduler.get_status()
    print("\nFinal Status:")
    for component, info in status.items():
        print(f"  {component}:")
        print(f"    Current rate: {info['current_rate']:.6f}")
        print(f"    Converged: {info['converged']}")
    
    # Get metrics
    metrics = scheduler.get_metrics()
    print(f"\nMetrics:")
    print(f"  Total adjustments: {metrics['total_adjustments']}")
    print(f"  Improvements: {metrics['improvements']}")
    print(f"  Plateaus detected: {metrics['plateaus_detected']}")
