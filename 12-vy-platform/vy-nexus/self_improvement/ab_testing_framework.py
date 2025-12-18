#!/usr/bin/env python3
"""
A/B Testing Framework - Vy-Nexus Self-Improvement Cycle

Executes A/B tests, manages groups, collects metrics, and analyzes results.
Provides statistical analysis and automated decision making.

Author: Vy-Nexus Self-Evolving AI
Created: December 15, 2025
"""

import json
import os
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib
from collections import defaultdict


class TestStatus(Enum):
    """Status of an A/B test."""
    DRAFT = "draft"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    STOPPED = "stopped"
    FAILED = "failed"


class DecisionType(Enum):
    """Types of decisions for test results."""
    DEPLOY_TREATMENT = "deploy_treatment"
    KEEP_CONTROL = "keep_control"
    INCONCLUSIVE = "inconclusive"
    NEEDS_MORE_DATA = "needs_more_data"


@dataclass
class Participant:
    """Represents a participant in an A/B test."""
    participant_id: str
    group_id: str
    assigned_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricValue:
    """Represents a metric measurement."""
    metric_name: str
    value: float
    participant_id: str
    group_id: str
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StatisticalResult:
    """Results of statistical analysis."""
    metric_name: str
    control_mean: float
    treatment_mean: float
    control_std: float
    treatment_std: float
    control_n: int
    treatment_n: int
    difference: float
    percent_change: float
    p_value: float
    confidence_interval_95: Tuple[float, float]
    is_significant: bool
    effect_size: float


@dataclass
class TestResult:
    """Complete test results."""
    test_id: str
    status: str
    decision: str
    confidence: float
    statistical_results: List[StatisticalResult]
    summary: str
    recommendations: List[str]
    analyzed_at: str


class ABTestingFramework:
    """Framework for executing and analyzing A/B tests."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/ab_tests"):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.tests_file = os.path.join(self.data_dir, "active_tests.json")
        self.participants_file = os.path.join(self.data_dir, "participants.json")
        self.metrics_file = os.path.join(self.data_dir, "metrics.json")
        self.results_file = os.path.join(self.data_dir, "results.json")
        
        self.tests = self._load_tests()
        self.participants = self._load_participants()
        self.metrics = self._load_metrics()
        self.results = self._load_results()
    
    def _load_tests(self) -> Dict[str, Dict]:
        """Load active tests."""
        if os.path.exists(self.tests_file):
            with open(self.tests_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_tests(self):
        """Save active tests."""
        with open(self.tests_file, 'w') as f:
            json.dump(self.tests, f, indent=2)
    
    def _load_participants(self) -> Dict[str, List[Dict]]:
        """Load participants by test ID."""
        if os.path.exists(self.participants_file):
            with open(self.participants_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_participants(self):
        """Save participants."""
        with open(self.participants_file, 'w') as f:
            json.dump(self.participants, f, indent=2)
    
    def _load_metrics(self) -> Dict[str, List[Dict]]:
        """Load metrics by test ID."""
        if os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_metrics(self):
        """Save metrics."""
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def _load_results(self) -> Dict[str, Dict]:
        """Load test results."""
        if os.path.exists(self.results_file):
            with open(self.results_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_results(self):
        """Save test results."""
        with open(self.results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
    
    def start_test(self, experiment_protocol: Dict[str, Any]) -> str:
        """Start an A/B test from an experiment protocol."""
        test_id = experiment_protocol.get('experiment_id')
        
        # Create test record
        test = {
            'test_id': test_id,
            'protocol': experiment_protocol,
            'status': TestStatus.RUNNING.value,
            'started_at': datetime.now().isoformat(),
            'participants_count': 0,
            'metrics_collected': 0
        }
        
        self.tests[test_id] = test
        self.participants[test_id] = []
        self.metrics[test_id] = []
        
        self._save_tests()
        self._save_participants()
        self._save_metrics()
        
        return test_id
    
    def assign_participant(self, test_id: str, participant_id: str,
                          metadata: Optional[Dict] = None) -> str:
        """Assign a participant to a test group."""
        if test_id not in self.tests:
            raise ValueError(f"Test {test_id} not found")
        
        test = self.tests[test_id]
        protocol = test['protocol']
        groups = protocol.get('groups', [])
        
        if not groups:
            raise ValueError("No groups defined in protocol")
        
        # Random assignment with equal probability
        group = random.choice(groups)
        group_id = group.get('group_id')
        
        # Create participant record
        participant = Participant(
            participant_id=participant_id,
            group_id=group_id,
            assigned_at=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        # Save participant
        if test_id not in self.participants:
            self.participants[test_id] = []
        
        self.participants[test_id].append(asdict(participant))
        test['participants_count'] += 1
        
        self._save_participants()
        self._save_tests()
        
        return group_id
    
    def record_metric(self, test_id: str, participant_id: str,
                     metric_name: str, value: float,
                     metadata: Optional[Dict] = None):
        """Record a metric value for a participant."""
        if test_id not in self.tests:
            raise ValueError(f"Test {test_id} not found")
        
        # Find participant's group
        group_id = None
        for p in self.participants.get(test_id, []):
            if p['participant_id'] == participant_id:
                group_id = p['group_id']
                break
        
        if not group_id:
            raise ValueError(f"Participant {participant_id} not found in test")
        
        # Create metric record
        metric = MetricValue(
            metric_name=metric_name,
            value=value,
            participant_id=participant_id,
            group_id=group_id,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        # Save metric
        if test_id not in self.metrics:
            self.metrics[test_id] = []
        
        self.metrics[test_id].append(asdict(metric))
        self.tests[test_id]['metrics_collected'] += 1
        
        self._save_metrics()
        self._save_tests()
    
    def get_group_metrics(self, test_id: str, metric_name: str) -> Dict[str, List[float]]:
        """Get metric values grouped by test group."""
        if test_id not in self.metrics:
            return {}
        
        grouped = defaultdict(list)
        
        for metric in self.metrics[test_id]:
            if metric['metric_name'] == metric_name:
                grouped[metric['group_id']].append(metric['value'])
        
        return dict(grouped)
    
    def calculate_statistics(self, values: List[float]) -> Dict[str, float]:
        """Calculate basic statistics for a list of values."""
        if not values:
            return {'mean': 0, 'std': 0, 'n': 0}
        
        n = len(values)
        mean = sum(values) / n
        
        if n > 1:
            variance = sum((x - mean) ** 2 for x in values) / (n - 1)
            std = math.sqrt(variance)
        else:
            std = 0
        
        return {'mean': mean, 'std': std, 'n': n}
    
    def t_test(self, control_values: List[float], 
               treatment_values: List[float]) -> Tuple[float, float]:
        """Perform independent samples t-test."""
        control_stats = self.calculate_statistics(control_values)
        treatment_stats = self.calculate_statistics(treatment_values)
        
        if control_stats['n'] < 2 or treatment_stats['n'] < 2:
            return 0.0, 1.0  # Not enough data
        
        # Calculate t-statistic
        mean_diff = treatment_stats['mean'] - control_stats['mean']
        
        # Pooled standard error
        se = math.sqrt(
            (control_stats['std'] ** 2 / control_stats['n']) +
            (treatment_stats['std'] ** 2 / treatment_stats['n'])
        )
        
        if se == 0:
            return 0.0, 1.0
        
        t_stat = mean_diff / se
        
        # Degrees of freedom (Welch's approximation)
        df = control_stats['n'] + treatment_stats['n'] - 2
        
        # Approximate p-value (two-tailed)
        # Using normal approximation for simplicity
        p_value = 2 * (1 - self._normal_cdf(abs(t_stat)))
        
        return t_stat, p_value
    
    def _normal_cdf(self, x: float) -> float:
        """Cumulative distribution function for standard normal distribution."""
        # Approximation using error function
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    def calculate_confidence_interval(self, values: List[float], 
                                     confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for mean."""
        stats = self.calculate_statistics(values)
        
        if stats['n'] < 2:
            return (stats['mean'], stats['mean'])
        
        # Z-score for 95% confidence (approximately 1.96)
        z = 1.96 if confidence == 0.95 else 2.576  # 99% confidence
        
        margin = z * (stats['std'] / math.sqrt(stats['n']))
        
        return (stats['mean'] - margin, stats['mean'] + margin)
    
    def calculate_effect_size(self, control_values: List[float],
                            treatment_values: List[float]) -> float:
        """Calculate Cohen's d effect size."""
        control_stats = self.calculate_statistics(control_values)
        treatment_stats = self.calculate_statistics(treatment_values)
        
        if control_stats['n'] < 2 or treatment_stats['n'] < 2:
            return 0.0
        
        # Pooled standard deviation
        pooled_std = math.sqrt(
            ((control_stats['n'] - 1) * control_stats['std'] ** 2 +
             (treatment_stats['n'] - 1) * treatment_stats['std'] ** 2) /
            (control_stats['n'] + treatment_stats['n'] - 2)
        )
        
        if pooled_std == 0:
            return 0.0
        
        return (treatment_stats['mean'] - control_stats['mean']) / pooled_std
    
    def analyze_test(self, test_id: str, 
                    significance_level: float = 0.05) -> TestResult:
        """Analyze test results and make a decision."""
        if test_id not in self.tests:
            raise ValueError(f"Test {test_id} not found")
        
        test = self.tests[test_id]
        protocol = test['protocol']
        metrics_to_analyze = [m['name'] for m in protocol.get('metrics', [])]
        
        statistical_results = []
        
        # Analyze each metric
        for metric_name in metrics_to_analyze:
            group_metrics = self.get_group_metrics(test_id, metric_name)
            
            # Find control and treatment groups
            control_values = None
            treatment_values = None
            
            for group in protocol.get('groups', []):
                group_id = group['group_id']
                if group_id in group_metrics:
                    if group.get('is_control'):
                        control_values = group_metrics[group_id]
                    else:
                        treatment_values = group_metrics[group_id]
            
            if not control_values or not treatment_values:
                continue
            
            # Calculate statistics
            control_stats = self.calculate_statistics(control_values)
            treatment_stats = self.calculate_statistics(treatment_values)
            
            # Perform t-test
            t_stat, p_value = self.t_test(control_values, treatment_values)
            
            # Calculate confidence interval for difference
            diff = treatment_stats['mean'] - control_stats['mean']
            percent_change = (diff / control_stats['mean'] * 100) if control_stats['mean'] != 0 else 0
            
            # Effect size
            effect_size = self.calculate_effect_size(control_values, treatment_values)
            
            # Confidence interval (simplified)
            ci_lower = diff - 1.96 * math.sqrt(
                control_stats['std']**2/control_stats['n'] + 
                treatment_stats['std']**2/treatment_stats['n']
            )
            ci_upper = diff + 1.96 * math.sqrt(
                control_stats['std']**2/control_stats['n'] + 
                treatment_stats['std']**2/treatment_stats['n']
            )
            
            result = StatisticalResult(
                metric_name=metric_name,
                control_mean=control_stats['mean'],
                treatment_mean=treatment_stats['mean'],
                control_std=control_stats['std'],
                treatment_std=treatment_stats['std'],
                control_n=control_stats['n'],
                treatment_n=treatment_stats['n'],
                difference=diff,
                percent_change=percent_change,
                p_value=p_value,
                confidence_interval_95=(ci_lower, ci_upper),
                is_significant=p_value < significance_level,
                effect_size=effect_size
            )
            
            statistical_results.append(result)
        
        # Make decision
        decision, confidence, summary, recommendations = self._make_decision(
            statistical_results, protocol, significance_level
        )
        
        # Create test result
        test_result = TestResult(
            test_id=test_id,
            status=TestStatus.COMPLETED.value,
            decision=decision.value,
            confidence=confidence,
            statistical_results=statistical_results,
            summary=summary,
            recommendations=recommendations,
            analyzed_at=datetime.now().isoformat()
        )
        
        # Save result
        self.results[test_id] = asdict(test_result)
        self._save_results()
        
        # Update test status
        self.tests[test_id]['status'] = TestStatus.COMPLETED.value
        self._save_tests()
        
        return test_result
    
    def _make_decision(self, statistical_results: List[StatisticalResult],
                      protocol: Dict, significance_level: float) -> Tuple[DecisionType, float, str, List[str]]:
        """Make a decision based on statistical results."""
        
        if not statistical_results:
            return (
                DecisionType.NEEDS_MORE_DATA,
                0.0,
                "Insufficient data to make a decision",
                ["Collect more data", "Ensure metrics are being recorded"]
            )
        
        # Check success criteria
        success_criteria = protocol.get('success_criteria', [])
        criteria_met = 0
        criteria_total = len(success_criteria)
        
        significant_improvements = 0
        significant_degradations = 0
        
        for result in statistical_results:
            # Check if significant
            if result.is_significant:
                if result.difference > 0:
                    significant_improvements += 1
                else:
                    significant_degradations += 1
            
            # Check against success criteria
            for criterion in success_criteria:
                if criterion['metric_name'] == result.metric_name:
                    if self._check_criterion(result, criterion):
                        criteria_met += 1
        
        # Calculate confidence
        if criteria_total > 0:
            confidence = criteria_met / criteria_total
        else:
            confidence = 0.5
        
        # Make decision
        if significant_degradations > 0:
            decision = DecisionType.KEEP_CONTROL
            summary = f"Treatment shows {significant_degradations} significant degradation(s). Keep control."
            recommendations = [
                "Do not deploy treatment",
                "Investigate why treatment performed worse",
                "Consider alternative approaches"
            ]
        elif significant_improvements > 0 and criteria_met >= criteria_total * 0.7:
            decision = DecisionType.DEPLOY_TREATMENT
            summary = f"Treatment shows {significant_improvements} significant improvement(s). Deploy recommended."
            recommendations = [
                "Deploy treatment to all users",
                "Monitor metrics closely after deployment",
                "Prepare rollback plan"
            ]
        elif criteria_met < criteria_total * 0.3:
            decision = DecisionType.KEEP_CONTROL
            summary = "Treatment does not meet success criteria. Keep control."
            recommendations = [
                "Do not deploy treatment",
                "Analyze why criteria were not met",
                "Redesign treatment approach"
            ]
        else:
            decision = DecisionType.INCONCLUSIVE
            summary = "Results are inconclusive. More data or analysis needed."
            recommendations = [
                "Extend test duration",
                "Increase sample size",
                "Review test design"
            ]
        
        return decision, confidence, summary, recommendations
    
    def _check_criterion(self, result: StatisticalResult, 
                        criterion: Dict) -> bool:
        """Check if a result meets a success criterion."""
        operator = criterion.get('operator')
        threshold = criterion.get('threshold')
        value = result.treatment_mean
        
        if operator == '>':
            return value > threshold
        elif operator == '<':
            return value < threshold
        elif operator == '>=':
            return value >= threshold
        elif operator == '<=':
            return value <= threshold
        elif operator == '==':
            return abs(value - threshold) < 0.01  # Approximate equality
        
        return False
    
    def check_early_stopping(self, test_id: str, 
                           min_participants: int = 100) -> Tuple[bool, str]:
        """Check if test should be stopped early."""
        if test_id not in self.tests:
            return False, "Test not found"
        
        test = self.tests[test_id]
        
        # Check minimum participants
        if test['participants_count'] < min_participants:
            return False, "Not enough participants yet"
        
        # Perform interim analysis
        try:
            result = self.analyze_test(test_id, significance_level=0.01)  # Stricter for early stopping
            
            # Stop early if very strong signal
            strong_signals = sum(
                1 for r in result.statistical_results 
                if r.is_significant and abs(r.effect_size) > 0.8
            )
            
            if strong_signals > 0:
                return True, f"Strong signal detected ({strong_signals} metrics with large effect size)"
            
            # Stop early if clear degradation
            degradations = sum(
                1 for r in result.statistical_results
                if r.is_significant and r.difference < 0
            )
            
            if degradations > 0:
                return True, f"Significant degradation detected ({degradations} metrics worse)"
            
        except Exception as e:
            return False, f"Error in interim analysis: {str(e)}"
        
        return False, "Continue test"
    
    def stop_test(self, test_id: str, reason: str = "Manual stop"):
        """Stop a running test."""
        if test_id in self.tests:
            self.tests[test_id]['status'] = TestStatus.STOPPED.value
            self.tests[test_id]['stopped_at'] = datetime.now().isoformat()
            self.tests[test_id]['stop_reason'] = reason
            self._save_tests()
    
    def get_test_status(self, test_id: str) -> Dict[str, Any]:
        """Get current status of a test."""
        if test_id not in self.tests:
            return {'error': 'Test not found'}
        
        test = self.tests[test_id]
        
        # Calculate duration
        started = datetime.fromisoformat(test['started_at'])
        duration = (datetime.now() - started).days
        
        return {
            'test_id': test_id,
            'status': test['status'],
            'duration_days': duration,
            'participants': test['participants_count'],
            'metrics_collected': test['metrics_collected'],
            'started_at': test['started_at']
        }
    
    def generate_report(self, test_id: str) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        if test_id not in self.results:
            return {'error': 'No results available for this test'}
        
        result = self.results[test_id]
        test = self.tests.get(test_id, {})
        
        report = {
            'test_id': test_id,
            'test_name': test.get('protocol', {}).get('name', 'Unknown'),
            'status': result['status'],
            'decision': result['decision'],
            'confidence': result['confidence'],
            'summary': result['summary'],
            'recommendations': result['recommendations'],
            'analyzed_at': result['analyzed_at'],
            'metrics_analyzed': len(result['statistical_results']),
            'statistical_results': result['statistical_results']
        }
        
        return report


if __name__ == "__main__":
    # Example usage
    framework = ABTestingFramework()
    
    # Example protocol
    protocol = {
        'experiment_id': 'exp_test_001',
        'name': 'Test Caching Performance',
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
    
    # Start test
    test_id = framework.start_test(protocol)
    print(f"Started test: {test_id}")
    
    # Simulate participants and metrics
    for i in range(100):
        participant_id = f"user_{i}"
        group = framework.assign_participant(test_id, participant_id)
        
        # Simulate metrics (treatment is faster)
        if group == 'control':
            response_time = random.gauss(120, 20)
            success_rate = random.gauss(0.93, 0.05)
        else:
            response_time = random.gauss(90, 15)  # 25% improvement
            success_rate = random.gauss(0.96, 0.03)
        
        framework.record_metric(test_id, participant_id, 'response_time', response_time)
        framework.record_metric(test_id, participant_id, 'success_rate', success_rate)
    
    # Analyze results
    result = framework.analyze_test(test_id)
    
    print(f"\nTest Result:")
    print(f"Decision: {result.decision}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Summary: {result.summary}")
    print(f"\nStatistical Results:")
    for stat in result.statistical_results:
        print(f"\n{stat.metric_name}:")
        print(f"  Control: {stat.control_mean:.2f} ± {stat.control_std:.2f}")
        print(f"  Treatment: {stat.treatment_mean:.2f} ± {stat.treatment_std:.2f}")
        print(f"  Change: {stat.percent_change:.2f}%")
        print(f"  P-value: {stat.p_value:.4f}")
        print(f"  Significant: {stat.is_significant}")
