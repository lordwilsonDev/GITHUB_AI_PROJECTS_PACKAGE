"""
Self-Improvement Cycle Module

This module implements the self-improvement cycle that generates hypotheses,
designs experiments, implements A/B testing, builds predictive models, and
develops adaptive algorithms for continuous system evolution.

Components:
- HypothesisGenerator: Generates optimization hypotheses based on data
- ExperimentDesigner: Designs experiments to test improvement theories
- ABTestingFramework: Implements A/B testing for workflows
- PredictiveModels: Builds models to predict user needs
- AdaptiveAlgorithms: Develops algorithms that adapt to usage patterns
- SelfImprovementEngine: Orchestrates the improvement cycle
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict
import statistics


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HypothesisType(Enum):
    """Types of optimization hypotheses"""
    PERFORMANCE = "performance"
    ACCURACY = "accuracy"
    EFFICIENCY = "efficiency"
    USER_SATISFACTION = "user_satisfaction"
    RESOURCE_USAGE = "resource_usage"
    ERROR_REDUCTION = "error_reduction"


class ExperimentStatus(Enum):
    """Status of experiments"""
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelType(Enum):
    """Types of predictive models"""
    TASK_PREDICTION = "task_prediction"
    TIMING_PREDICTION = "timing_prediction"
    RESOURCE_PREDICTION = "resource_prediction"
    PREFERENCE_PREDICTION = "preference_prediction"
    WORKFLOW_PREDICTION = "workflow_prediction"


@dataclass
class Hypothesis:
    """Represents an optimization hypothesis"""
    id: str
    type: HypothesisType
    description: str
    rationale: str
    expected_improvement: float  # Expected improvement percentage
    confidence: float  # Confidence in hypothesis (0-1)
    data_sources: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    tested: bool = False
    result: Optional[Dict[str, Any]] = None


@dataclass
class Experiment:
    """Represents an experiment to test a hypothesis"""
    id: str
    hypothesis_id: str
    name: str
    description: str
    control_group: str
    treatment_group: str
    metrics: List[str]
    duration_hours: int
    status: ExperimentStatus = ExperimentStatus.PLANNED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None


@dataclass
class ABTest:
    """Represents an A/B test"""
    id: str
    name: str
    variant_a: Dict[str, Any]
    variant_b: Dict[str, Any]
    metric: str
    sample_size_per_variant: int
    results_a: List[float] = field(default_factory=list)
    results_b: List[float] = field(default_factory=list)
    winner: Optional[str] = None
    confidence_level: float = 0.95
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class PredictiveModel:
    """Represents a predictive model"""
    id: str
    type: ModelType
    name: str
    description: str
    features: List[str]
    accuracy: float = 0.0
    training_data_size: int = 0
    last_trained: Optional[datetime] = None
    predictions_made: int = 0
    correct_predictions: int = 0


@dataclass
class AdaptiveAlgorithm:
    """Represents an adaptive algorithm"""
    id: str
    name: str
    description: str
    parameters: Dict[str, float]
    performance_history: List[float] = field(default_factory=list)
    adaptation_rate: float = 0.1
    last_adapted: Optional[datetime] = None


class HypothesisGenerator:
    """Generates optimization hypotheses based on data analysis"""
    
    def __init__(self, max_hypotheses: int = 100):
        self.hypotheses: List[Hypothesis] = []
        self.max_hypotheses = max_hypotheses
        self.hypothesis_counter = 0
        
    def generate_from_performance_data(
        self,
        performance_data: Dict[str, Any]
    ) -> List[Hypothesis]:
        """Generate hypotheses from performance data"""
        new_hypotheses = []
        
        # Analyze bottlenecks
        if 'bottlenecks' in performance_data:
            for bottleneck in performance_data['bottlenecks']:
                hypothesis = Hypothesis(
                    id=f"hyp_{self.hypothesis_counter}",
                    type=HypothesisType.PERFORMANCE,
                    description=f"Optimizing {bottleneck['component']} will improve overall performance",
                    rationale=f"Component shows {bottleneck['impact']}% performance impact",
                    expected_improvement=bottleneck['impact'] * 0.5,
                    confidence=0.7,
                    data_sources=['performance_metrics']
                )
                new_hypotheses.append(hypothesis)
                self.hypothesis_counter += 1
        
        # Analyze error patterns
        if 'error_rate' in performance_data and performance_data['error_rate'] > 0.05:
            hypothesis = Hypothesis(
                id=f"hyp_{self.hypothesis_counter}",
                type=HypothesisType.ERROR_REDUCTION,
                description="Implementing additional error handling will reduce error rate",
                rationale=f"Current error rate is {performance_data['error_rate']:.2%}",
                expected_improvement=50.0,
                confidence=0.8,
                data_sources=['error_logs']
            )
            new_hypotheses.append(hypothesis)
            self.hypothesis_counter += 1
        
        # Analyze resource usage
        if 'resource_usage' in performance_data:
            usage = performance_data['resource_usage']
            if usage.get('cpu', 0) > 0.8:
                hypothesis = Hypothesis(
                    id=f"hyp_{self.hypothesis_counter}",
                    type=HypothesisType.RESOURCE_USAGE,
                    description="Optimizing CPU-intensive operations will reduce resource usage",
                    rationale=f"CPU usage at {usage['cpu']:.1%}",
                    expected_improvement=30.0,
                    confidence=0.75,
                    data_sources=['resource_monitor']
                )
                new_hypotheses.append(hypothesis)
                self.hypothesis_counter += 1
        
        self.hypotheses.extend(new_hypotheses)
        self._prune_hypotheses()
        return new_hypotheses
    
    def generate_from_user_feedback(
        self,
        feedback_data: Dict[str, Any]
    ) -> List[Hypothesis]:
        """Generate hypotheses from user feedback"""
        new_hypotheses = []
        
        if 'satisfaction_score' in feedback_data:
            score = feedback_data['satisfaction_score']
            if score < 0.7:
                hypothesis = Hypothesis(
                    id=f"hyp_{self.hypothesis_counter}",
                    type=HypothesisType.USER_SATISFACTION,
                    description="Improving response quality will increase user satisfaction",
                    rationale=f"Current satisfaction score is {score:.2f}",
                    expected_improvement=(0.9 - score) * 100,
                    confidence=0.8,
                    data_sources=['user_feedback']
                )
                new_hypotheses.append(hypothesis)
                self.hypothesis_counter += 1
        
        if 'common_complaints' in feedback_data:
            for complaint in feedback_data['common_complaints'][:3]:
                hypothesis = Hypothesis(
                    id=f"hyp_{self.hypothesis_counter}",
                    type=HypothesisType.USER_SATISFACTION,
                    description=f"Addressing '{complaint['issue']}' will improve satisfaction",
                    rationale=f"Issue mentioned {complaint['frequency']} times",
                    expected_improvement=20.0,
                    confidence=0.7,
                    data_sources=['user_feedback']
                )
                new_hypotheses.append(hypothesis)
                self.hypothesis_counter += 1
        
        self.hypotheses.extend(new_hypotheses)
        self._prune_hypotheses()
        return new_hypotheses
    
    def prioritize_hypotheses(self) -> List[Hypothesis]:
        """Prioritize hypotheses by expected impact and confidence"""
        untested = [h for h in self.hypotheses if not h.tested]
        return sorted(
            untested,
            key=lambda h: h.expected_improvement * h.confidence,
            reverse=True
        )
    
    def _prune_hypotheses(self):
        """Remove old tested hypotheses if limit exceeded"""
        if len(self.hypotheses) > self.max_hypotheses:
            # Keep untested and recent tested hypotheses
            self.hypotheses = sorted(
                self.hypotheses,
                key=lambda h: (not h.tested, h.created_at),
                reverse=True
            )[:self.max_hypotheses]


class ExperimentDesigner:
    """Designs experiments to test improvement theories"""
    
    def __init__(self):
        self.experiments: List[Experiment] = []
        self.experiment_counter = 0
        
    def design_experiment(
        self,
        hypothesis: Hypothesis,
        duration_hours: int = 24
    ) -> Experiment:
        """Design an experiment to test a hypothesis"""
        experiment = Experiment(
            id=f"exp_{self.experiment_counter}",
            hypothesis_id=hypothesis.id,
            name=f"Test: {hypothesis.description[:50]}",
            description=f"Experiment to validate: {hypothesis.description}",
            control_group="baseline",
            treatment_group="optimized",
            metrics=self._select_metrics(hypothesis.type),
            duration_hours=duration_hours
        )
        
        self.experiments.append(experiment)
        self.experiment_counter += 1
        return experiment
    
    def _select_metrics(self, hypothesis_type: HypothesisType) -> List[str]:
        """Select appropriate metrics for hypothesis type"""
        metric_map = {
            HypothesisType.PERFORMANCE: ['execution_time', 'throughput', 'latency'],
            HypothesisType.ACCURACY: ['accuracy', 'precision', 'recall'],
            HypothesisType.EFFICIENCY: ['resource_usage', 'cost', 'time_saved'],
            HypothesisType.USER_SATISFACTION: ['satisfaction_score', 'task_completion_rate'],
            HypothesisType.RESOURCE_USAGE: ['cpu_usage', 'memory_usage', 'io_operations'],
            HypothesisType.ERROR_REDUCTION: ['error_rate', 'recovery_rate', 'mean_time_to_recovery']
        }
        return metric_map.get(hypothesis_type, ['general_performance'])
    
    def start_experiment(self, experiment_id: str) -> bool:
        """Start an experiment"""
        for exp in self.experiments:
            if exp.id == experiment_id:
                exp.status = ExperimentStatus.RUNNING
                exp.started_at = datetime.now()
                logger.info(f"Started experiment: {exp.name}")
                return True
        return False
    
    def complete_experiment(
        self,
        experiment_id: str,
        results: Dict[str, Any]
    ) -> bool:
        """Complete an experiment with results"""
        for exp in self.experiments:
            if exp.id == experiment_id:
                exp.status = ExperimentStatus.COMPLETED
                exp.completed_at = datetime.now()
                exp.results = results
                logger.info(f"Completed experiment: {exp.name}")
                return True
        return False
    
    def get_active_experiments(self) -> List[Experiment]:
        """Get all active experiments"""
        return [e for e in self.experiments if e.status == ExperimentStatus.RUNNING]


class ABTestingFramework:
    """Implements A/B testing for workflows"""
    
    def __init__(self):
        self.tests: List[ABTest] = []
        self.test_counter = 0
        
    def create_test(
        self,
        name: str,
        variant_a: Dict[str, Any],
        variant_b: Dict[str, Any],
        metric: str,
        sample_size: int = 100
    ) -> ABTest:
        """Create a new A/B test"""
        test = ABTest(
            id=f"ab_{self.test_counter}",
            name=name,
            variant_a=variant_a,
            variant_b=variant_b,
            metric=metric,
            sample_size_per_variant=sample_size
        )
        
        self.tests.append(test)
        self.test_counter += 1
        logger.info(f"Created A/B test: {name}")
        return test
    
    def record_result(
        self,
        test_id: str,
        variant: str,
        value: float
    ) -> bool:
        """Record a result for a variant"""
        for test in self.tests:
            if test.id == test_id:
                if variant == 'a':
                    test.results_a.append(value)
                elif variant == 'b':
                    test.results_b.append(value)
                else:
                    return False
                
                # Check if test is complete
                if (len(test.results_a) >= test.sample_size_per_variant and
                    len(test.results_b) >= test.sample_size_per_variant):
                    self._analyze_test(test)
                
                return True
        return False
    
    def _analyze_test(self, test: ABTest):
        """Analyze A/B test results"""
        if not test.results_a or not test.results_b:
            return
        
        mean_a = statistics.mean(test.results_a)
        mean_b = statistics.mean(test.results_b)
        
        # Simple comparison (in production, use proper statistical tests)
        if mean_b > mean_a * 1.05:  # B is 5% better
            test.winner = 'b'
        elif mean_a > mean_b * 1.05:  # A is 5% better
            test.winner = 'a'
        else:
            test.winner = 'inconclusive'
        
        test.completed_at = datetime.now()
        logger.info(f"A/B test '{test.name}' completed. Winner: {test.winner}")
    
    def get_test_results(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get results of an A/B test"""
        for test in self.tests:
            if test.id == test_id:
                if not test.results_a or not test.results_b:
                    return None
                
                return {
                    'test_id': test.id,
                    'name': test.name,
                    'variant_a_mean': statistics.mean(test.results_a),
                    'variant_b_mean': statistics.mean(test.results_b),
                    'variant_a_samples': len(test.results_a),
                    'variant_b_samples': len(test.results_b),
                    'winner': test.winner,
                    'improvement': self._calculate_improvement(test)
                }
        return None
    
    def _calculate_improvement(self, test: ABTest) -> float:
        """Calculate improvement percentage"""
        if not test.results_a or not test.results_b:
            return 0.0
        
        mean_a = statistics.mean(test.results_a)
        mean_b = statistics.mean(test.results_b)
        
        if mean_a == 0:
            return 0.0
        
        return ((mean_b - mean_a) / mean_a) * 100


class PredictiveModels:
    """Builds and manages predictive models"""
    
    def __init__(self):
        self.models: List[PredictiveModel] = []
        self.model_counter = 0
        self.training_data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
    def create_model(
        self,
        model_type: ModelType,
        name: str,
        features: List[str]
    ) -> PredictiveModel:
        """Create a new predictive model"""
        model = PredictiveModel(
            id=f"model_{self.model_counter}",
            type=model_type,
            name=name,
            description=f"Predictive model for {model_type.value}",
            features=features
        )
        
        self.models.append(model)
        self.model_counter += 1
        logger.info(f"Created predictive model: {name}")
        return model
    
    def add_training_data(
        self,
        model_id: str,
        data: Dict[str, Any]
    ):
        """Add training data for a model"""
        self.training_data[model_id].append({
            **data,
            'timestamp': datetime.now()
        })
    
    def train_model(self, model_id: str) -> bool:
        """Train a predictive model"""
        for model in self.models:
            if model.id == model_id:
                training_data = self.training_data.get(model_id, [])
                
                if len(training_data) < 10:
                    logger.warning(f"Insufficient training data for {model.name}")
                    return False
                
                # Simulate training (in production, use actual ML algorithms)
                model.training_data_size = len(training_data)
                model.accuracy = min(0.95, 0.5 + (len(training_data) / 1000))
                model.last_trained = datetime.now()
                
                logger.info(f"Trained model {model.name} with {len(training_data)} samples")
                return True
        return False
    
    def predict(
        self,
        model_id: str,
        features: Dict[str, Any]
    ) -> Optional[Any]:
        """Make a prediction using a model"""
        for model in self.models:
            if model.id == model_id:
                if model.last_trained is None:
                    logger.warning(f"Model {model.name} not trained yet")
                    return None
                
                model.predictions_made += 1
                
                # Simulate prediction (in production, use actual model)
                prediction = self._simulate_prediction(model, features)
                
                return prediction
        return None
    
    def record_prediction_outcome(
        self,
        model_id: str,
        was_correct: bool
    ):
        """Record whether a prediction was correct"""
        for model in self.models:
            if model.id == model_id:
                if was_correct:
                    model.correct_predictions += 1
                
                # Update accuracy
                if model.predictions_made > 0:
                    model.accuracy = model.correct_predictions / model.predictions_made
    
    def _simulate_prediction(
        self,
        model: PredictiveModel,
        features: Dict[str, Any]
    ) -> Any:
        """Simulate a prediction (placeholder for actual ML)"""
        if model.type == ModelType.TASK_PREDICTION:
            return "predicted_task_type"
        elif model.type == ModelType.TIMING_PREDICTION:
            return datetime.now() + timedelta(hours=2)
        elif model.type == ModelType.RESOURCE_PREDICTION:
            return {"cpu": 0.5, "memory": 0.6}
        else:
            return "prediction"
    
    def get_model_performance(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get performance metrics for a model"""
        for model in self.models:
            if model.id == model_id:
                return {
                    'model_id': model.id,
                    'name': model.name,
                    'type': model.type.value,
                    'accuracy': model.accuracy,
                    'predictions_made': model.predictions_made,
                    'correct_predictions': model.correct_predictions,
                    'training_data_size': model.training_data_size,
                    'last_trained': model.last_trained
                }
        return None


class AdaptiveAlgorithms:
    """Develops algorithms that adapt to usage patterns"""
    
    def __init__(self):
        self.algorithms: List[AdaptiveAlgorithm] = []
        self.algorithm_counter = 0
        
    def create_algorithm(
        self,
        name: str,
        initial_parameters: Dict[str, float],
        adaptation_rate: float = 0.1
    ) -> AdaptiveAlgorithm:
        """Create a new adaptive algorithm"""
        algorithm = AdaptiveAlgorithm(
            id=f"algo_{self.algorithm_counter}",
            name=name,
            description=f"Adaptive algorithm: {name}",
            parameters=initial_parameters.copy(),
            adaptation_rate=adaptation_rate
        )
        
        self.algorithms.append(algorithm)
        self.algorithm_counter += 1
        logger.info(f"Created adaptive algorithm: {name}")
        return algorithm
    
    def record_performance(
        self,
        algorithm_id: str,
        performance_score: float
    ):
        """Record performance of an algorithm"""
        for algo in self.algorithms:
            if algo.id == algorithm_id:
                algo.performance_history.append(performance_score)
                
                # Keep only recent history
                if len(algo.performance_history) > 100:
                    algo.performance_history = algo.performance_history[-100:]
    
    def adapt_parameters(self, algorithm_id: str) -> bool:
        """Adapt algorithm parameters based on performance"""
        for algo in self.algorithms:
            if algo.id == algorithm_id:
                if len(algo.performance_history) < 5:
                    return False
                
                recent_performance = algo.performance_history[-5:]
                avg_performance = statistics.mean(recent_performance)
                
                # If performance is declining, adjust parameters
                if len(algo.performance_history) >= 10:
                    older_performance = statistics.mean(algo.performance_history[-10:-5])
                    
                    if avg_performance < older_performance:
                        # Adapt parameters (simple gradient descent simulation)
                        for param in algo.parameters:
                            adjustment = algo.adaptation_rate * (older_performance - avg_performance)
                            algo.parameters[param] *= (1 + adjustment)
                        
                        algo.last_adapted = datetime.now()
                        logger.info(f"Adapted parameters for {algo.name}")
                        return True
                
                return False
        return False
    
    def get_algorithm_status(self, algorithm_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an adaptive algorithm"""
        for algo in self.algorithms:
            if algo.id == algorithm_id:
                recent_perf = algo.performance_history[-10:] if algo.performance_history else []
                
                return {
                    'algorithm_id': algo.id,
                    'name': algo.name,
                    'parameters': algo.parameters,
                    'recent_performance': recent_perf,
                    'avg_recent_performance': statistics.mean(recent_perf) if recent_perf else 0.0,
                    'last_adapted': algo.last_adapted,
                    'total_adaptations': len([p for p in algo.performance_history if p > 0])
                }
        return None


class SelfImprovementEngine:
    """Orchestrates the self-improvement cycle"""
    
    def __init__(
        self,
        cycle_interval_minutes: int = 20
    ):
        self.hypothesis_generator = HypothesisGenerator()
        self.experiment_designer = ExperimentDesigner()
        self.ab_testing = ABTestingFramework()
        self.predictive_models = PredictiveModels()
        self.adaptive_algorithms = AdaptiveAlgorithms()
        
        self.cycle_interval = timedelta(minutes=cycle_interval_minutes)
        self.last_cycle = datetime.now()
        self.is_running = False
        self.improvement_history: List[Dict[str, Any]] = []
        
    async def start(self):
        """Start the self-improvement cycle"""
        self.is_running = True
        logger.info("Self-Improvement Engine started")
        
        while self.is_running:
            await self._run_improvement_cycle()
            await asyncio.sleep(self.cycle_interval.total_seconds())
    
    def stop(self):
        """Stop the self-improvement cycle"""
        self.is_running = False
        logger.info("Self-Improvement Engine stopped")
    
    async def _run_improvement_cycle(self):
        """Run one improvement cycle"""
        logger.info("Running self-improvement cycle...")
        
        cycle_results = {
            'timestamp': datetime.now(),
            'hypotheses_generated': 0,
            'experiments_started': 0,
            'experiments_completed': 0,
            'models_trained': 0,
            'algorithms_adapted': 0
        }
        
        # Generate new hypotheses
        # (In production, this would analyze real system data)
        sample_performance_data = {
            'bottlenecks': [
                {'component': 'data_processing', 'impact': 25}
            ],
            'error_rate': 0.08
        }
        
        new_hypotheses = self.hypothesis_generator.generate_from_performance_data(
            sample_performance_data
        )
        cycle_results['hypotheses_generated'] = len(new_hypotheses)
        
        # Design experiments for top hypotheses
        top_hypotheses = self.hypothesis_generator.prioritize_hypotheses()[:3]
        for hypothesis in top_hypotheses:
            if not hypothesis.tested:
                experiment = self.experiment_designer.design_experiment(hypothesis)
                self.experiment_designer.start_experiment(experiment.id)
                cycle_results['experiments_started'] += 1
        
        # Check active experiments
        active_experiments = self.experiment_designer.get_active_experiments()
        for exp in active_experiments:
            if exp.started_at and (datetime.now() - exp.started_at).total_seconds() > 3600:
                # Simulate experiment completion
                results = {'improvement': 15.0, 'confidence': 0.85}
                self.experiment_designer.complete_experiment(exp.id, results)
                cycle_results['experiments_completed'] += 1
        
        # Train models with new data
        for model in self.predictive_models.models:
            if len(self.predictive_models.training_data.get(model.id, [])) >= 10:
                self.predictive_models.train_model(model.id)
                cycle_results['models_trained'] += 1
        
        # Adapt algorithms
        for algo in self.adaptive_algorithms.algorithms:
            if self.adaptive_algorithms.adapt_parameters(algo.id):
                cycle_results['algorithms_adapted'] += 1
        
        self.improvement_history.append(cycle_results)
        self.last_cycle = datetime.now()
        
        logger.info(f"Improvement cycle complete: {cycle_results}")
    
    def generate_improvement_report(self) -> Dict[str, Any]:
        """Generate a report on self-improvement activities"""
        recent_history = self.improvement_history[-10:] if self.improvement_history else []
        
        total_hypotheses = sum(h['hypotheses_generated'] for h in recent_history)
        total_experiments = sum(h['experiments_started'] for h in recent_history)
        total_completions = sum(h['experiments_completed'] for h in recent_history)
        
        return {
            'total_hypotheses_generated': total_hypotheses,
            'total_experiments_started': total_experiments,
            'total_experiments_completed': total_completions,
            'active_hypotheses': len([h for h in self.hypothesis_generator.hypotheses if not h.tested]),
            'active_experiments': len(self.experiment_designer.get_active_experiments()),
            'active_ab_tests': len([t for t in self.ab_testing.tests if t.winner is None]),
            'total_models': len(self.predictive_models.models),
            'total_algorithms': len(self.adaptive_algorithms.algorithms),
            'last_cycle': self.last_cycle,
            'cycle_interval_minutes': self.cycle_interval.total_seconds() / 60
        }


# Example usage
if __name__ == "__main__":
    async def main():
        # Create self-improvement engine
        engine = SelfImprovementEngine(cycle_interval_minutes=20)
        
        # Create some initial models and algorithms
        task_model = engine.predictive_models.create_model(
            ModelType.TASK_PREDICTION,
            "Task Type Predictor",
            ['time_of_day', 'user_context', 'recent_tasks']
        )
        
        priority_algo = engine.adaptive_algorithms.create_algorithm(
            "Priority Calculator",
            {'urgency_weight': 0.5, 'importance_weight': 0.3, 'effort_weight': 0.2}
        )
        
        # Generate report
        report = engine.generate_improvement_report()
        print(json.dumps(report, indent=2, default=str))
        
        # Run one cycle
        await engine._run_improvement_cycle()
        
        print("\nSelf-Improvement Engine initialized successfully!")
    
    asyncio.run(main())
