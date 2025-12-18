"""
Test Suite for Self-Improvement Cycle Module

Tests all components of the self-improvement system including:
- HypothesisGenerator
- ExperimentDesigner
- ABTestingFramework
- PredictiveModels
- AdaptiveAlgorithms
- SelfImprovementEngine
"""

import unittest
import asyncio
from datetime import datetime, timedelta
from self_improvement import (
    HypothesisGenerator, ExperimentDesigner, ABTestingFramework,
    PredictiveModels, AdaptiveAlgorithms, SelfImprovementEngine,
    HypothesisType, ExperimentStatus, ModelType
)


class TestHypothesisGenerator(unittest.TestCase):
    """Test HypothesisGenerator component"""
    
    def setUp(self):
        self.generator = HypothesisGenerator()
    
    def test_generate_from_performance_data(self):
        """Test hypothesis generation from performance data"""
        performance_data = {
            'bottlenecks': [
                {'component': 'database', 'impact': 30}
            ],
            'error_rate': 0.1,
            'resource_usage': {'cpu': 0.85, 'memory': 0.6}
        }
        
        hypotheses = self.generator.generate_from_performance_data(performance_data)
        
        self.assertGreater(len(hypotheses), 0)
        self.assertTrue(any(h.type == HypothesisType.PERFORMANCE for h in hypotheses))
        self.assertTrue(any(h.type == HypothesisType.ERROR_REDUCTION for h in hypotheses))
        self.assertTrue(any(h.type == HypothesisType.RESOURCE_USAGE for h in hypotheses))
    
    def test_generate_from_user_feedback(self):
        """Test hypothesis generation from user feedback"""
        feedback_data = {
            'satisfaction_score': 0.6,
            'common_complaints': [
                {'issue': 'slow response', 'frequency': 10},
                {'issue': 'unclear output', 'frequency': 5}
            ]
        }
        
        hypotheses = self.generator.generate_from_user_feedback(feedback_data)
        
        self.assertGreater(len(hypotheses), 0)
        self.assertTrue(all(h.type == HypothesisType.USER_SATISFACTION for h in hypotheses))
    
    def test_prioritize_hypotheses(self):
        """Test hypothesis prioritization"""
        # Generate some hypotheses
        self.generator.generate_from_performance_data({
            'bottlenecks': [{'component': 'test', 'impact': 20}],
            'error_rate': 0.05
        })
        
        prioritized = self.generator.prioritize_hypotheses()
        
        # Check that they're sorted by expected_improvement * confidence
        for i in range(len(prioritized) - 1):
            score_i = prioritized[i].expected_improvement * prioritized[i].confidence
            score_next = prioritized[i + 1].expected_improvement * prioritized[i + 1].confidence
            self.assertGreaterEqual(score_i, score_next)
    
    def test_hypothesis_pruning(self):
        """Test that old hypotheses are pruned"""
        generator = HypothesisGenerator(max_hypotheses=5)
        
        # Generate more than max
        for i in range(10):
            generator.generate_from_performance_data({
                'bottlenecks': [{'component': f'test_{i}', 'impact': 10}]
            })
        
        self.assertLessEqual(len(generator.hypotheses), 5)


class TestExperimentDesigner(unittest.TestCase):
    """Test ExperimentDesigner component"""
    
    def setUp(self):
        self.designer = ExperimentDesigner()
        self.generator = HypothesisGenerator()
    
    def test_design_experiment(self):
        """Test experiment design"""
        hypotheses = self.generator.generate_from_performance_data({
            'bottlenecks': [{'component': 'test', 'impact': 25}]
        })
        
        experiment = self.designer.design_experiment(hypotheses[0])
        
        self.assertIsNotNone(experiment)
        self.assertEqual(experiment.hypothesis_id, hypotheses[0].id)
        self.assertEqual(experiment.status, ExperimentStatus.PLANNED)
        self.assertGreater(len(experiment.metrics), 0)
    
    def test_start_experiment(self):
        """Test starting an experiment"""
        hypotheses = self.generator.generate_from_performance_data({
            'error_rate': 0.1
        })
        
        experiment = self.designer.design_experiment(hypotheses[0])
        success = self.designer.start_experiment(experiment.id)
        
        self.assertTrue(success)
        self.assertEqual(experiment.status, ExperimentStatus.RUNNING)
        self.assertIsNotNone(experiment.started_at)
    
    def test_complete_experiment(self):
        """Test completing an experiment"""
        hypotheses = self.generator.generate_from_performance_data({
            'error_rate': 0.1
        })
        
        experiment = self.designer.design_experiment(hypotheses[0])
        self.designer.start_experiment(experiment.id)
        
        results = {'improvement': 20.0, 'confidence': 0.9}
        success = self.designer.complete_experiment(experiment.id, results)
        
        self.assertTrue(success)
        self.assertEqual(experiment.status, ExperimentStatus.COMPLETED)
        self.assertEqual(experiment.results, results)
    
    def test_get_active_experiments(self):
        """Test getting active experiments"""
        hypotheses = self.generator.generate_from_performance_data({
            'bottlenecks': [{'component': 'test', 'impact': 20}],
            'error_rate': 0.1
        })
        
        exp1 = self.designer.design_experiment(hypotheses[0])
        exp2 = self.designer.design_experiment(hypotheses[1])
        
        self.designer.start_experiment(exp1.id)
        
        active = self.designer.get_active_experiments()
        
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].id, exp1.id)


class TestABTestingFramework(unittest.TestCase):
    """Test ABTestingFramework component"""
    
    def setUp(self):
        self.framework = ABTestingFramework()
    
    def test_create_test(self):
        """Test creating an A/B test"""
        test = self.framework.create_test(
            name="Response Time Test",
            variant_a={'method': 'old'},
            variant_b={'method': 'new'},
            metric='response_time',
            sample_size=50
        )
        
        self.assertIsNotNone(test)
        self.assertEqual(test.name, "Response Time Test")
        self.assertEqual(test.sample_size_per_variant, 50)
    
    def test_record_result(self):
        """Test recording A/B test results"""
        test = self.framework.create_test(
            name="Test",
            variant_a={'v': 'a'},
            variant_b={'v': 'b'},
            metric='score',
            sample_size=10
        )
        
        success = self.framework.record_result(test.id, 'a', 0.8)
        self.assertTrue(success)
        self.assertEqual(len(test.results_a), 1)
    
    def test_ab_test_completion(self):
        """Test A/B test automatic completion"""
        test = self.framework.create_test(
            name="Test",
            variant_a={'v': 'a'},
            variant_b={'v': 'b'},
            metric='score',
            sample_size=5
        )
        
        # Record results for variant A (lower scores)
        for i in range(5):
            self.framework.record_result(test.id, 'a', 0.5)
        
        # Record results for variant B (higher scores)
        for i in range(5):
            self.framework.record_result(test.id, 'b', 0.9)
        
        # Test should be completed and B should win
        self.assertIsNotNone(test.winner)
        self.assertEqual(test.winner, 'b')
    
    def test_get_test_results(self):
        """Test getting A/B test results"""
        test = self.framework.create_test(
            name="Test",
            variant_a={'v': 'a'},
            variant_b={'v': 'b'},
            metric='score',
            sample_size=3
        )
        
        for i in range(3):
            self.framework.record_result(test.id, 'a', 0.6)
            self.framework.record_result(test.id, 'b', 0.8)
        
        results = self.framework.get_test_results(test.id)
        
        self.assertIsNotNone(results)
        self.assertIn('variant_a_mean', results)
        self.assertIn('variant_b_mean', results)
        self.assertIn('winner', results)


class TestPredictiveModels(unittest.TestCase):
    """Test PredictiveModels component"""
    
    def setUp(self):
        self.models = PredictiveModels()
    
    def test_create_model(self):
        """Test creating a predictive model"""
        model = self.models.create_model(
            ModelType.TASK_PREDICTION,
            "Task Predictor",
            ['time', 'context', 'history']
        )
        
        self.assertIsNotNone(model)
        self.assertEqual(model.type, ModelType.TASK_PREDICTION)
        self.assertEqual(len(model.features), 3)
    
    def test_add_training_data(self):
        """Test adding training data"""
        model = self.models.create_model(
            ModelType.TASK_PREDICTION,
            "Test Model",
            ['feature1']
        )
        
        self.models.add_training_data(model.id, {'feature1': 0.5, 'label': 'task_a'})
        
        self.assertEqual(len(self.models.training_data[model.id]), 1)
    
    def test_train_model(self):
        """Test training a model"""
        model = self.models.create_model(
            ModelType.TASK_PREDICTION,
            "Test Model",
            ['feature1']
        )
        
        # Add sufficient training data
        for i in range(20):
            self.models.add_training_data(model.id, {'feature1': i * 0.1, 'label': 'task'})
        
        success = self.models.train_model(model.id)
        
        self.assertTrue(success)
        self.assertGreater(model.accuracy, 0)
        self.assertIsNotNone(model.last_trained)
    
    def test_predict(self):
        """Test making predictions"""
        model = self.models.create_model(
            ModelType.TASK_PREDICTION,
            "Test Model",
            ['feature1']
        )
        
        # Train model
        for i in range(20):
            self.models.add_training_data(model.id, {'feature1': i, 'label': 'task'})
        self.models.train_model(model.id)
        
        # Make prediction
        prediction = self.models.predict(model.id, {'feature1': 5})
        
        self.assertIsNotNone(prediction)
        self.assertEqual(model.predictions_made, 1)
    
    def test_record_prediction_outcome(self):
        """Test recording prediction outcomes"""
        model = self.models.create_model(
            ModelType.TASK_PREDICTION,
            "Test Model",
            ['feature1']
        )
        
        # Train and predict
        for i in range(20):
            self.models.add_training_data(model.id, {'feature1': i, 'label': 'task'})
        self.models.train_model(model.id)
        self.models.predict(model.id, {'feature1': 5})
        
        # Record outcome
        self.models.record_prediction_outcome(model.id, True)
        
        self.assertEqual(model.correct_predictions, 1)
    
    def test_get_model_performance(self):
        """Test getting model performance metrics"""
        model = self.models.create_model(
            ModelType.TASK_PREDICTION,
            "Test Model",
            ['feature1']
        )
        
        performance = self.models.get_model_performance(model.id)
        
        self.assertIsNotNone(performance)
        self.assertIn('accuracy', performance)
        self.assertIn('predictions_made', performance)


class TestAdaptiveAlgorithms(unittest.TestCase):
    """Test AdaptiveAlgorithms component"""
    
    def setUp(self):
        self.algorithms = AdaptiveAlgorithms()
    
    def test_create_algorithm(self):
        """Test creating an adaptive algorithm"""
        algo = self.algorithms.create_algorithm(
            "Priority Calculator",
            {'weight_a': 0.5, 'weight_b': 0.3},
            adaptation_rate=0.1
        )
        
        self.assertIsNotNone(algo)
        self.assertEqual(algo.name, "Priority Calculator")
        self.assertEqual(len(algo.parameters), 2)
    
    def test_record_performance(self):
        """Test recording algorithm performance"""
        algo = self.algorithms.create_algorithm(
            "Test Algo",
            {'param': 0.5}
        )
        
        self.algorithms.record_performance(algo.id, 0.8)
        
        self.assertEqual(len(algo.performance_history), 1)
        self.assertEqual(algo.performance_history[0], 0.8)
    
    def test_adapt_parameters(self):
        """Test parameter adaptation"""
        algo = self.algorithms.create_algorithm(
            "Test Algo",
            {'param': 1.0},
            adaptation_rate=0.1
        )
        
        # Record declining performance
        for i in range(10):
            score = 0.9 - (i * 0.05)  # Declining from 0.9 to 0.4
            self.algorithms.record_performance(algo.id, score)
        
        initial_param = algo.parameters['param']
        adapted = self.algorithms.adapt_parameters(algo.id)
        
        self.assertTrue(adapted)
        self.assertNotEqual(algo.parameters['param'], initial_param)
    
    def test_get_algorithm_status(self):
        """Test getting algorithm status"""
        algo = self.algorithms.create_algorithm(
            "Test Algo",
            {'param': 0.5}
        )
        
        self.algorithms.record_performance(algo.id, 0.8)
        
        status = self.algorithms.get_algorithm_status(algo.id)
        
        self.assertIsNotNone(status)
        self.assertIn('parameters', status)
        self.assertIn('recent_performance', status)


class TestSelfImprovementEngine(unittest.TestCase):
    """Test SelfImprovementEngine orchestrator"""
    
    def setUp(self):
        self.engine = SelfImprovementEngine(cycle_interval_minutes=1)
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        self.assertIsNotNone(self.engine.hypothesis_generator)
        self.assertIsNotNone(self.engine.experiment_designer)
        self.assertIsNotNone(self.engine.ab_testing)
        self.assertIsNotNone(self.engine.predictive_models)
        self.assertIsNotNone(self.engine.adaptive_algorithms)
    
    def test_improvement_cycle(self):
        """Test running an improvement cycle"""
        async def run_test():
            await self.engine._run_improvement_cycle()
            
            self.assertGreater(len(self.engine.improvement_history), 0)
            
            last_cycle = self.engine.improvement_history[-1]
            self.assertIn('hypotheses_generated', last_cycle)
            self.assertIn('experiments_started', last_cycle)
        
        asyncio.run(run_test())
    
    def test_generate_improvement_report(self):
        """Test generating improvement report"""
        async def run_test():
            await self.engine._run_improvement_cycle()
            
            report = self.engine.generate_improvement_report()
            
            self.assertIn('total_hypotheses_generated', report)
            self.assertIn('total_experiments_started', report)
            self.assertIn('active_hypotheses', report)
            self.assertIn('total_models', report)
        
        asyncio.run(run_test())
    
    def test_engine_components_integration(self):
        """Test that all components work together"""
        # Create a model
        model = self.engine.predictive_models.create_model(
            ModelType.TASK_PREDICTION,
            "Integration Test Model",
            ['feature1']
        )
        
        # Create an algorithm
        algo = self.engine.adaptive_algorithms.create_algorithm(
            "Integration Test Algo",
            {'param': 0.5}
        )
        
        # Create an A/B test
        test = self.engine.ab_testing.create_test(
            "Integration Test",
            {'v': 'a'},
            {'v': 'b'},
            'metric',
            sample_size=5
        )
        
        report = self.engine.generate_improvement_report()
        
        self.assertEqual(report['total_models'], 1)
        self.assertEqual(report['total_algorithms'], 1)
        self.assertEqual(report['active_ab_tests'], 1)


if __name__ == '__main__':
    unittest.main()
