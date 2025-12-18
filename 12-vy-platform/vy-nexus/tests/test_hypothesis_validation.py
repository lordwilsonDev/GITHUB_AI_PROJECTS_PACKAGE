#!/usr/bin/env python3
"""
Hypothesis Generation Validation Tests

Validates the quality and effectiveness of:
- Hypothesis Generator
- Experiment Designer
- A/B Testing Framework

Tests hypothesis quality, diversity, experiment design completeness,
and A/B testing statistical rigor.
"""

import unittest
import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from self_improvement.hypothesis_generator import (
    HypothesisGenerator, OptimizationHypothesis, HypothesisType
)
from self_improvement.experiment_designer import (
    ExperimentDesigner, Experiment, ExperimentStatus
)
from self_improvement.ab_testing import (
    ABTestingFramework, Variant, TestResult
)


class HypothesisQualityMetrics:
    """Track hypothesis generation quality metrics"""
    
    def __init__(self):
        self.metrics = {
            'total_hypotheses': 0,
            'unique_hypotheses': 0,
            'hypothesis_types': {},
            'avg_confidence': 0.0,
            'high_confidence_count': 0,
            'diversity_score': 0.0,
            'actionable_count': 0,
            'experiments_designed': 0,
            'complete_experiments': 0,
            'ab_tests_run': 0,
            'statistically_significant': 0
        }
        self.hypotheses = []
    
    def record_hypothesis(self, hypothesis: OptimizationHypothesis):
        """Record a generated hypothesis"""
        self.hypotheses.append(hypothesis)
        self.metrics['total_hypotheses'] += 1
        
        # Track hypothesis type
        h_type = hypothesis.type.value
        self.metrics['hypothesis_types'][h_type] = \
            self.metrics['hypothesis_types'].get(h_type, 0) + 1
        
        # Track confidence
        if hypothesis.confidence > 0.7:
            self.metrics['high_confidence_count'] += 1
        
        # Check if actionable
        if hypothesis.expected_impact and hypothesis.implementation_steps:
            self.metrics['actionable_count'] += 1
    
    def calculate_diversity(self):
        """Calculate hypothesis diversity score"""
        if not self.hypotheses:
            return 0.0
        
        # Unique descriptions
        unique_descriptions = len(set(h.description for h in self.hypotheses))
        self.metrics['unique_hypotheses'] = unique_descriptions
        
        # Type diversity (entropy)
        total = len(self.hypotheses)
        type_counts = self.metrics['hypothesis_types']
        
        if len(type_counts) == 0:
            diversity = 0.0
        else:
            # Calculate entropy
            import math
            entropy = 0.0
            for count in type_counts.values():
                p = count / total
                if p > 0:
                    entropy -= p * math.log2(p)
            
            # Normalize to 0-1 scale
            max_entropy = math.log2(len(HypothesisType))
            diversity = entropy / max_entropy if max_entropy > 0 else 0.0
        
        self.metrics['diversity_score'] = diversity
        return diversity
    
    def calculate_avg_confidence(self):
        """Calculate average confidence"""
        if not self.hypotheses:
            return 0.0
        
        avg = sum(h.confidence for h in self.hypotheses) / len(self.hypotheses)
        self.metrics['avg_confidence'] = avg
        return avg
    
    def record_experiment(self, complete: bool = False):
        """Record experiment design"""
        self.metrics['experiments_designed'] += 1
        if complete:
            self.metrics['complete_experiments'] += 1
    
    def record_ab_test(self, significant: bool = False):
        """Record A/B test"""
        self.metrics['ab_tests_run'] += 1
        if significant:
            self.metrics['statistically_significant'] += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of metrics"""
        self.calculate_diversity()
        self.calculate_avg_confidence()
        return self.metrics.copy()
    
    def meets_quality_standards(self) -> tuple[bool, List[str]]:
        """Check if hypothesis generation meets quality standards"""
        summary = self.get_summary()
        issues = []
        
        # At least 10 hypotheses generated
        if summary['total_hypotheses'] < 10:
            issues.append(f"Only {summary['total_hypotheses']} hypotheses (need 10+)")
        
        # At least 80% unique
        uniqueness = summary['unique_hypotheses'] / max(summary['total_hypotheses'], 1)
        if uniqueness < 0.8:
            issues.append(f"Uniqueness {uniqueness:.1%} < 80%")
        
        # Average confidence > 0.5
        if summary['avg_confidence'] < 0.5:
            issues.append(f"Avg confidence {summary['avg_confidence']:.2f} < 0.5")
        
        # Diversity score > 0.6
        if summary['diversity_score'] < 0.6:
            issues.append(f"Diversity {summary['diversity_score']:.2f} < 0.6")
        
        # At least 70% actionable
        actionable_pct = summary['actionable_count'] / max(summary['total_hypotheses'], 1)
        if actionable_pct < 0.7:
            issues.append(f"Actionable {actionable_pct:.1%} < 70%")
        
        # At least 5 experiments designed
        if summary['experiments_designed'] < 5:
            issues.append(f"Only {summary['experiments_designed']} experiments (need 5+)")
        
        # At least 80% complete experiments
        if summary['experiments_designed'] > 0:
            completeness = summary['complete_experiments'] / summary['experiments_designed']
            if completeness < 0.8:
                issues.append(f"Experiment completeness {completeness:.1%} < 80%")
        
        return len(issues) == 0, issues


class TestHypothesisGeneration(unittest.TestCase):
    """Test hypothesis generation quality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.quality_metrics = HypothesisQualityMetrics()
    
    def setUp(self):
        """Set up for each test"""
        self.generator = HypothesisGenerator()
        self.designer = ExperimentDesigner()
        self.ab_framework = ABTestingFramework()
    
    def test_01_hypothesis_generation_basic(self):
        """Test basic hypothesis generation"""
        print("\n[TEST 1] Testing Basic Hypothesis Generation...")
        
        context = {
            'current_performance': 0.75,
            'bottlenecks': ['slow_processing', 'high_memory'],
            'recent_changes': ['updated_algorithm'],
            'user_feedback': ['needs_faster_response']
        }
        
        hypotheses = self.generator.generate_hypotheses(context, count=5)
        
        self.assertGreaterEqual(len(hypotheses), 3)
        
        for h in hypotheses:
            self.assertIsInstance(h, OptimizationHypothesis)
            self.assertIsNotNone(h.description)
            self.assertGreater(h.confidence, 0)
            self.assertLessEqual(h.confidence, 1)
            self.quality_metrics.record_hypothesis(h)
        
        print(f"✓ Generated {len(hypotheses)} hypotheses")
    
    def test_02_hypothesis_diversity(self):
        """Test hypothesis diversity"""
        print("\n[TEST 2] Testing Hypothesis Diversity...")
        
        # Generate hypotheses for different contexts
        contexts = [
            {'focus': 'performance', 'metric': 'speed'},
            {'focus': 'resource', 'metric': 'memory'},
            {'focus': 'accuracy', 'metric': 'precision'},
            {'focus': 'user_experience', 'metric': 'satisfaction'},
            {'focus': 'scalability', 'metric': 'throughput'}
        ]
        
        all_hypotheses = []
        for context in contexts:
            hypotheses = self.generator.generate_hypotheses(context, count=3)
            all_hypotheses.extend(hypotheses)
            for h in hypotheses:
                self.quality_metrics.record_hypothesis(h)
        
        # Check diversity
        unique_descriptions = len(set(h.description for h in all_hypotheses))
        diversity_ratio = unique_descriptions / len(all_hypotheses)
        
        self.assertGreater(diversity_ratio, 0.7)
        print(f"✓ Diversity ratio: {diversity_ratio:.1%}")
    
    def test_03_hypothesis_types_coverage(self):
        """Test coverage of different hypothesis types"""
        print("\n[TEST 3] Testing Hypothesis Type Coverage...")
        
        # Generate many hypotheses to cover different types
        for i in range(10):
            context = {
                'iteration': i,
                'focus': ['performance', 'resource', 'accuracy', 'ux'][i % 4]
            }
            hypotheses = self.generator.generate_hypotheses(context, count=2)
            for h in hypotheses:
                self.quality_metrics.record_hypothesis(h)
        
        # Check type coverage
        types_covered = len(self.quality_metrics.metrics['hypothesis_types'])
        total_types = len(HypothesisType)
        
        coverage = types_covered / total_types
        print(f"✓ Type coverage: {types_covered}/{total_types} ({coverage:.1%})")
        self.assertGreaterEqual(types_covered, 3)
    
    def test_04_hypothesis_confidence_scoring(self):
        """Test hypothesis confidence scoring"""
        print("\n[TEST 4] Testing Confidence Scoring...")
        
        # High-quality context should produce high-confidence hypotheses
        high_quality_context = {
            'current_performance': 0.85,
            'historical_data': [0.7, 0.75, 0.8, 0.85],
            'bottlenecks': ['identified_issue'],
            'evidence': ['strong_correlation'],
            'sample_size': 1000
        }
        
        hypotheses = self.generator.generate_hypotheses(high_quality_context, count=5)
        
        high_confidence_count = sum(1 for h in hypotheses if h.confidence > 0.6)
        
        for h in hypotheses:
            self.quality_metrics.record_hypothesis(h)
        
        self.assertGreater(high_confidence_count, 0)
        print(f"✓ High-confidence hypotheses: {high_confidence_count}/{len(hypotheses)}")
    
    def test_05_hypothesis_actionability(self):
        """Test that hypotheses are actionable"""
        print("\n[TEST 5] Testing Hypothesis Actionability...")
        
        context = {
            'problem': 'slow_response_time',
            'current_value': 500,
            'target_value': 200
        }
        
        hypotheses = self.generator.generate_hypotheses(context, count=5)
        
        actionable_count = 0
        for h in hypotheses:
            self.quality_metrics.record_hypothesis(h)
            
            # Check if hypothesis has implementation steps
            if h.implementation_steps and len(h.implementation_steps) > 0:
                actionable_count += 1
            
            # Check if hypothesis has expected impact
            if h.expected_impact:
                self.assertIsInstance(h.expected_impact, dict)
        
        actionable_ratio = actionable_count / len(hypotheses)
        print(f"✓ Actionable hypotheses: {actionable_count}/{len(hypotheses)} ({actionable_ratio:.1%})")
        self.assertGreater(actionable_ratio, 0.5)
    
    def test_06_experiment_design_completeness(self):
        """Test experiment design completeness"""
        print("\n[TEST 6] Testing Experiment Design...")
        
        # Create a hypothesis
        hypothesis = OptimizationHypothesis(
            type=HypothesisType.PERFORMANCE,
            description="Caching will reduce response time by 30%",
            confidence=0.8,
            expected_impact={'response_time': -0.3},
            implementation_steps=['add_cache', 'configure_ttl', 'monitor']
        )
        
        # Design experiment
        experiment = self.designer.design_experiment(hypothesis)
        
        self.assertIsNotNone(experiment)
        self.assertIsNotNone(experiment.control_group)
        self.assertIsNotNone(experiment.treatment_group)
        self.assertIsNotNone(experiment.success_criteria)
        self.assertIsNotNone(experiment.duration)
        
        # Check completeness
        is_complete = (
            experiment.control_group is not None and
            experiment.treatment_group is not None and
            experiment.success_criteria is not None and
            len(experiment.success_criteria) > 0
        )
        
        self.quality_metrics.record_experiment(complete=is_complete)
        print(f"✓ Experiment design complete: {is_complete}")
    
    def test_07_multiple_experiment_designs(self):
        """Test designing multiple experiments"""
        print("\n[TEST 7] Testing Multiple Experiment Designs...")
        
        hypotheses = [
            OptimizationHypothesis(
                type=HypothesisType.PERFORMANCE,
                description=f"Optimization {i} will improve performance",
                confidence=0.7,
                expected_impact={'metric': 0.1 * i}
            )
            for i in range(1, 6)
        ]
        
        experiments = []
        for h in hypotheses:
            exp = self.designer.design_experiment(h)
            experiments.append(exp)
            
            is_complete = (
                exp.control_group is not None and
                exp.treatment_group is not None and
                exp.success_criteria is not None
            )
            self.quality_metrics.record_experiment(complete=is_complete)
        
        self.assertEqual(len(experiments), 5)
        print(f"✓ Designed {len(experiments)} experiments")
    
    def test_08_ab_testing_setup(self):
        """Test A/B testing framework setup"""
        print("\n[TEST 8] Testing A/B Testing Setup...")
        
        # Create variants
        control = Variant(
            id='control',
            name='Current System',
            description='Baseline performance',
            traffic_allocation=0.5
        )
        
        treatment = Variant(
            id='treatment',
            name='Optimized System',
            description='With optimization applied',
            traffic_allocation=0.5
        )
        
        # Set up test
        test_id = self.ab_framework.create_test(
            name='Performance Optimization Test',
            variants=[control, treatment],
            metric='response_time'
        )
        
        self.assertIsNotNone(test_id)
        print(f"✓ A/B test created: {test_id}")
    
    def test_09_ab_testing_statistical_analysis(self):
        """Test A/B testing statistical analysis"""
        print("\n[TEST 9] Testing Statistical Analysis...")
        
        # Simulate test data
        control_data = [100, 105, 98, 102, 101, 99, 103, 100, 102, 101] * 10
        treatment_data = [85, 88, 82, 86, 84, 87, 83, 85, 86, 84] * 10
        
        # Analyze results
        result = self.ab_framework.analyze_results(
            control_data=control_data,
            treatment_data=treatment_data,
            metric_name='response_time',
            higher_is_better=False
        )
        
        self.assertIsNotNone(result)
        self.assertIn('p_value', result)
        self.assertIn('confidence_interval', result)
        self.assertIn('effect_size', result)
        
        is_significant = result.get('p_value', 1.0) < 0.05
        self.quality_metrics.record_ab_test(significant=is_significant)
        
        print(f"✓ Statistical analysis complete")
        print(f"  - p-value: {result.get('p_value', 'N/A')}")
        print(f"  - Significant: {is_significant}")
    
    def test_10_ab_testing_winner_selection(self):
        """Test A/B testing winner selection"""
        print("\n[TEST 10] Testing Winner Selection...")
        
        # Clear winner scenario
        control_data = [100] * 100
        treatment_data = [80] * 100  # 20% improvement
        
        result = self.ab_framework.analyze_results(
            control_data=control_data,
            treatment_data=treatment_data,
            metric_name='response_time',
            higher_is_better=False
        )
        
        winner = self.ab_framework.select_winner(result)
        
        self.assertIsNotNone(winner)
        self.assertEqual(winner, 'treatment')
        
        is_significant = result.get('p_value', 1.0) < 0.05
        self.quality_metrics.record_ab_test(significant=is_significant)
        
        print(f"✓ Winner selected: {winner}")
    
    def test_11_end_to_end_hypothesis_to_test(self):
        """Test complete flow from hypothesis to A/B test"""
        print("\n[TEST 11] Testing End-to-End Flow...")
        
        # 1. Generate hypothesis
        context = {'problem': 'high_latency', 'current_value': 200}
        hypotheses = self.generator.generate_hypotheses(context, count=3)
        self.assertGreater(len(hypotheses), 0)
        
        best_hypothesis = max(hypotheses, key=lambda h: h.confidence)
        self.quality_metrics.record_hypothesis(best_hypothesis)
        
        # 2. Design experiment
        experiment = self.designer.design_experiment(best_hypothesis)
        self.assertIsNotNone(experiment)
        
        is_complete = (
            experiment.control_group is not None and
            experiment.treatment_group is not None
        )
        self.quality_metrics.record_experiment(complete=is_complete)
        
        # 3. Run A/B test (simulated)
        control_data = [200] * 50
        treatment_data = [140] * 50  # 30% improvement as hypothesized
        
        result = self.ab_framework.analyze_results(
            control_data=control_data,
            treatment_data=treatment_data,
            metric_name='latency',
            higher_is_better=False
        )
        
        is_significant = result.get('p_value', 1.0) < 0.05
        self.quality_metrics.record_ab_test(significant=is_significant)
        
        # 4. Select winner
        winner = self.ab_framework.select_winner(result)
        
        print(f"✓ End-to-end flow complete")
        print(f"  - Hypothesis confidence: {best_hypothesis.confidence:.2f}")
        print(f"  - Experiment complete: {is_complete}")
        print(f"  - Test significant: {is_significant}")
        print(f"  - Winner: {winner}")
    
    @classmethod
    def tearDownClass(cls):
        """Generate final quality report"""
        print("\n" + "="*70)
        print("HYPOTHESIS GENERATION QUALITY REPORT")
        print("="*70)
        
        summary = cls.quality_metrics.get_summary()
        
        print(f"\n📊 Generation Metrics:")
        print(f"  • Total Hypotheses: {summary['total_hypotheses']}")
        print(f"  • Unique Hypotheses: {summary['unique_hypotheses']}")
        print(f"  • Average Confidence: {summary['avg_confidence']:.2f}")
        print(f"  • High Confidence Count: {summary['high_confidence_count']}")
        print(f"  • Diversity Score: {summary['diversity_score']:.2f}")
        print(f"  • Actionable Count: {summary['actionable_count']}")
        
        print(f"\n🧪 Experiment Metrics:")
        print(f"  • Experiments Designed: {summary['experiments_designed']}")
        print(f"  • Complete Experiments: {summary['complete_experiments']}")
        print(f"  • A/B Tests Run: {summary['ab_tests_run']}")
        print(f"  • Statistically Significant: {summary['statistically_significant']}")
        
        print(f"\n📈 Hypothesis Types:")
        for h_type, count in summary['hypothesis_types'].items():
            print(f"  • {h_type}: {count}")
        
        # Check quality standards
        meets_standards, issues = cls.quality_metrics.meets_quality_standards()
        
        print(f"\n✅ Quality Standards:")
        if meets_standards:
            print("  ✓ ALL STANDARDS MET!")
        else:
            print("  ✗ Some standards not met:")
            for issue in issues:
                print(f"    - {issue}")
        
        # Save report
        report_path = os.path.expanduser("~/Lords Love/HYPOTHESIS_VALIDATION_REPORT.md")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w') as f:
            f.write("# 🧪 Hypothesis Generation Validation Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Summary\n\n")
            f.write(f"- **Total Hypotheses Generated:** {summary['total_hypotheses']}\n")
            f.write(f"- **Quality Standards Met:** {'✅ YES' if meets_standards else '❌ NO'}\n\n")
            
            f.write("## Generation Quality\n\n")
            f.write(f"| Metric | Value | Target | Status |\n")
            f.write(f"|--------|-------|--------|--------|\n")
            
            uniqueness = summary['unique_hypotheses'] / max(summary['total_hypotheses'], 1)
            f.write(f"| Uniqueness | {uniqueness:.1%} | >80% | {'✅' if uniqueness >= 0.8 else '❌'} |\n")
            f.write(f"| Avg Confidence | {summary['avg_confidence']:.2f} | >0.5 | {'✅' if summary['avg_confidence'] >= 0.5 else '❌'} |\n")
            f.write(f"| Diversity Score | {summary['diversity_score']:.2f} | >0.6 | {'✅' if summary['diversity_score'] >= 0.6 else '❌'} |\n")
            
            actionable_pct = summary['actionable_count'] / max(summary['total_hypotheses'], 1)
            f.write(f"| Actionable | {actionable_pct:.1%} | >70% | {'✅' if actionable_pct >= 0.7 else '❌'} |\n\n")
            
            f.write("## Experiment Design\n\n")
            f.write(f"- Experiments Designed: {summary['experiments_designed']}\n")
            f.write(f"- Complete Experiments: {summary['complete_experiments']}\n")
            
            if summary['experiments_designed'] > 0:
                completeness = summary['complete_experiments'] / summary['experiments_designed']
                f.write(f"- Completeness Rate: {completeness:.1%}\n\n")
            
            f.write("## A/B Testing\n\n")
            f.write(f"- Tests Run: {summary['ab_tests_run']}\n")
            f.write(f"- Statistically Significant: {summary['statistically_significant']}\n")
            
            if summary['ab_tests_run'] > 0:
                sig_rate = summary['statistically_significant'] / summary['ab_tests_run']
                f.write(f"- Significance Rate: {sig_rate:.1%}\n\n")
            
            f.write("## Hypothesis Type Distribution\n\n")
            for h_type, count in summary['hypothesis_types'].items():
                pct = count / max(summary['total_hypotheses'], 1) * 100
                f.write(f"- {h_type}: {count} ({pct:.1f}%)\n")
            
            f.write("\n## Conclusion\n\n")
            if meets_standards:
                f.write("The hypothesis generation system meets all quality standards. ")
                f.write("Hypotheses are diverse, actionable, and well-designed. ")
                f.write("Experiment design is complete and A/B testing is statistically rigorous.\n")
            else:
                f.write("Some quality standards were not met. Issues:\n\n")
                for issue in issues:
                    f.write(f"- {issue}\n")
        
        print(f"\n📄 Full report saved to: {report_path}")
        print("="*70 + "\n")


if __name__ == '__main__':
    unittest.main(verbosity=2)
