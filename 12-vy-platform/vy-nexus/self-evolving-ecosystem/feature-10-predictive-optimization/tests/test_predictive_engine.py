"""Tests for Predictive Optimization Engine"""

import unittest
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from predictive_engine import (
    NeedsAnticipationSystem, ProactiveSuggestionEngine, TimingOptimizer,
    ResourceForecaster, ImpactModeler, PredictiveOptimizationEngine,
    NeedType, SuggestionType, ActivityType, ResourceType, ImpactCategory
)


class TestNeedsAnticipationSystem(unittest.TestCase):
    def setUp(self):
        self.system = NeedsAnticipationSystem(max_needs=100)
        
    def test_anticipate_need(self):
        need = self.system.anticipate_need(
            need_type=NeedType.TASK_COMPLETION,
            description="Complete weekly report",
            confidence=0.85,
            predicted_time=datetime.now() + timedelta(hours=2),
            context={"task": "report"},
            pattern="weekly_pattern"
        )
        self.assertIsNotNone(need)
        self.assertEqual(need.need_type, NeedType.TASK_COMPLETION)
        self.assertEqual(need.confidence, 0.85)
        self.assertTrue(len(need.preparation_actions) > 0)
        
    def test_get_upcoming_needs(self):
        # Add needs at different times
        self.system.anticipate_need(
            NeedType.TASK_COMPLETION, "Task 1", 0.8,
            datetime.now() + timedelta(hours=1), {}, "pattern1"
        )
        self.system.anticipate_need(
            NeedType.TASK_COMPLETION, "Task 2", 0.8,
            datetime.now() + timedelta(hours=30), {}, "pattern2"
        )
        
        upcoming = self.system.get_upcoming_needs(hours_ahead=24)
        self.assertEqual(len(upcoming), 1)
        
    def test_accuracy_tracking(self):
        need = self.system.anticipate_need(
            NeedType.TASK_COMPLETION, "Task", 0.8,
            datetime.now() + timedelta(hours=1), {}, "pattern"
        )
        
        self.system.record_need_accuracy(need.need_id, True)
        self.assertEqual(self.system.get_accuracy_rate(), 1.0)
        
        self.system.record_need_accuracy(need.need_id + "_2", False)
        self.assertEqual(self.system.get_accuracy_rate(), 0.5)
        
    def test_pruning(self):
        system = NeedsAnticipationSystem(max_needs=5)
        for i in range(10):
            system.anticipate_need(
                NeedType.TASK_COMPLETION, f"Task {i}", 0.8,
                datetime.now() + timedelta(hours=i), {}, f"pattern{i}"
            )
        self.assertEqual(len(system.anticipated_needs), 5)


class TestProactiveSuggestionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ProactiveSuggestionEngine(max_suggestions=100)
        
    def test_generate_suggestion(self):
        suggestion = self.engine.generate_suggestion(
            suggestion_type=SuggestionType.AUTOMATION_OPPORTUNITY,
            title="Automate task",
            description="This task can be automated",
            expected_benefit="HIGH",
            effort="MEDIUM",
            confidence=0.8,
            context={"task": "automation"}
        )
        self.assertIsNotNone(suggestion)
        self.assertEqual(suggestion.suggestion_type, SuggestionType.AUTOMATION_OPPORTUNITY)
        self.assertTrue(0 <= suggestion.priority <= 1.0)
        
    def test_priority_calculation(self):
        high_priority = self.engine.generate_suggestion(
            SuggestionType.EFFICIENCY_GAIN, "High", "High priority",
            "HIGH", "LOW", 0.9, {}
        )
        low_priority = self.engine.generate_suggestion(
            SuggestionType.EFFICIENCY_GAIN, "Low", "Low priority",
            "LOW", "HIGH", 0.3, {}
        )
        self.assertGreater(high_priority.priority, low_priority.priority)
        
    def test_get_top_suggestions(self):
        for i in range(10):
            self.engine.generate_suggestion(
                SuggestionType.OPTIMIZATION, f"Suggestion {i}", "Description",
                "MEDIUM", "MEDIUM", 0.5 + i * 0.05, {}
            )
        top = self.engine.get_top_suggestions(limit=3)
        self.assertEqual(len(top), 3)
        self.assertGreaterEqual(top[0].priority, top[1].priority)
        
    def test_outcome_tracking(self):
        suggestion = self.engine.generate_suggestion(
            SuggestionType.OPTIMIZATION, "Test", "Test",
            "HIGH", "LOW", 0.8, {}
        )
        
        self.engine.record_suggestion_outcome(
            suggestion.suggestion_id, implemented=True,
            actual_benefit="HIGH", actual_effort="LOW"
        )
        self.assertEqual(self.engine.get_implementation_rate(), 1.0)


class TestTimingOptimizer(unittest.TestCase):
    def setUp(self):
        self.optimizer = TimingOptimizer()
        
    def test_record_activity(self):
        self.optimizer.record_activity(
            activity_type=ActivityType.FOCUSED_WORK,
            start_time=datetime.now().replace(hour=9),
            duration_minutes=120,
            success_score=0.9,
            context={"task": "coding"}
        )
        self.assertEqual(len(self.optimizer.activity_history[ActivityType.FOCUSED_WORK]), 1)
        
    def test_calculate_optimal_timing(self):
        # Record multiple activities at hour 9
        for i in range(10):
            self.optimizer.record_activity(
                ActivityType.FOCUSED_WORK,
                datetime.now().replace(hour=9),
                120, 0.9, {}
            )
        # Record fewer activities at hour 14
        for i in range(3):
            self.optimizer.record_activity(
                ActivityType.FOCUSED_WORK,
                datetime.now().replace(hour=14),
                120, 0.5, {}
            )
            
        optimal = self.optimizer.calculate_optimal_timing(ActivityType.FOCUSED_WORK)
        self.assertIsNotNone(optimal)
        self.assertEqual(optimal.optimal_hour, 9)
        self.assertGreater(optimal.confidence, 0)
        
    def test_insufficient_data(self):
        # Only 2 activities
        for i in range(2):
            self.optimizer.record_activity(
                ActivityType.MEETINGS,
                datetime.now(), 60, 0.8, {}
            )
        optimal = self.optimizer.calculate_optimal_timing(ActivityType.MEETINGS)
        self.assertIsNone(optimal)
        
    def test_suggest_scheduling(self):
        for i in range(10):
            self.optimizer.record_activity(
                ActivityType.CREATIVE,
                datetime.now().replace(hour=10),
                90, 0.95, {}
            )
        self.optimizer.calculate_optimal_timing(ActivityType.CREATIVE)
        
        suggestion = self.optimizer.suggest_scheduling(
            ActivityType.CREATIVE,
            datetime.now().replace(hour=10)
        )
        self.assertEqual(suggestion["suggestion"], "NOW")


class TestResourceForecaster(unittest.TestCase):
    def setUp(self):
        self.forecaster = ResourceForecaster(max_forecasts=100)
        
    def test_record_usage(self):
        self.forecaster.record_usage(
            resource_type=ResourceType.COMPUTE,
            usage=75.0,
            capacity=100.0
        )
        self.assertEqual(len(self.forecaster.usage_history[ResourceType.COMPUTE]), 1)
        
    def test_forecast_usage(self):
        # Record some usage history
        for i in range(10):
            self.forecaster.record_usage(
                ResourceType.MEMORY,
                usage=50.0 + i,
                capacity=100.0
            )
            
        forecast = self.forecaster.forecast_usage(
            resource_type=ResourceType.MEMORY,
            period="next_hour",
            current_capacity=100.0
        )
        self.assertIsNotNone(forecast)
        self.assertGreater(forecast.predicted_usage, 0)
        self.assertEqual(forecast.resource_type, ResourceType.MEMORY)
        
    def test_bottleneck_detection(self):
        # High utilization
        self.forecaster.record_usage(ResourceType.STORAGE, 95.0, 100.0)
        forecast = self.forecaster.forecast_usage(
            ResourceType.STORAGE, "next_hour", 100.0
        )
        self.assertEqual(forecast.bottleneck_risk, "HIGH")
        self.assertTrue(len(forecast.recommendations) > 0)
        
    def test_identify_bottlenecks(self):
        # Create high risk forecast
        self.forecaster.record_usage(ResourceType.NETWORK, 92.0, 100.0)
        self.forecaster.forecast_usage(ResourceType.NETWORK, "next_hour", 100.0)
        
        # Create low risk forecast
        self.forecaster.record_usage(ResourceType.TIME, 30.0, 100.0)
        self.forecaster.forecast_usage(ResourceType.TIME, "next_hour", 100.0)
        
        bottlenecks = self.forecaster.identify_bottlenecks()
        self.assertGreater(len(bottlenecks), 0)


class TestImpactModeler(unittest.TestCase):
    def setUp(self):
        self.modeler = ImpactModeler(max_models=100)
        
    def test_model_impact(self):
        model = self.modeler.model_impact(
            change_description="Implement automation",
            expected_impacts={
                ImpactCategory.PRODUCTIVITY: 0.7,
                ImpactCategory.EFFICIENCY: 0.6,
                ImpactCategory.COST: -0.2
            },
            confidence=0.8,
            context={"project": "automation"}
        )
        self.assertIsNotNone(model)
        self.assertTrue(len(model.benefits) > 0)
        self.assertTrue(len(model.risks) > 0)
        self.assertIn(model.recommendation, ["IMPLEMENT", "TEST", "DEFER", "REJECT"])
        
    def test_recommendation_logic(self):
        # High positive impact, high confidence -> IMPLEMENT
        model1 = self.modeler.model_impact(
            "Change 1",
            {ImpactCategory.PRODUCTIVITY: 0.8, ImpactCategory.QUALITY: 0.7},
            0.9, {}
        )
        self.assertEqual(model1.recommendation, "IMPLEMENT")
        
        # Negative impact -> REJECT
        model2 = self.modeler.model_impact(
            "Change 2",
            {ImpactCategory.PRODUCTIVITY: -0.5, ImpactCategory.QUALITY: -0.3},
            0.8, {}
        )
        self.assertEqual(model2.recommendation, "REJECT")
        
    def test_accuracy_tracking(self):
        model = self.modeler.model_impact(
            "Test change",
            {ImpactCategory.PRODUCTIVITY: 0.6, ImpactCategory.EFFICIENCY: 0.5},
            0.8, {}
        )
        
        # Record actual impact (close to prediction)
        self.modeler.record_actual_impact(
            model.change_id,
            {ImpactCategory.PRODUCTIVITY: 0.65, ImpactCategory.EFFICIENCY: 0.55}
        )
        
        accuracy = self.modeler.get_prediction_accuracy()
        self.assertGreater(accuracy, 0.8)  # Should be high accuracy


class TestPredictiveOptimizationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = PredictiveOptimizationEngine(cycle_interval_minutes=30)
        
    def test_initialization(self):
        self.assertIsNotNone(self.engine.needs_system)
        self.assertIsNotNone(self.engine.suggestion_engine)
        self.assertIsNotNone(self.engine.timing_optimizer)
        self.assertIsNotNone(self.engine.resource_forecaster)
        self.assertIsNotNone(self.engine.impact_modeler)
        
    def test_generate_report(self):
        # Add some data
        self.engine.needs_system.anticipate_need(
            NeedType.TASK_COMPLETION, "Task", 0.8,
            datetime.now() + timedelta(hours=1), {}, "pattern"
        )
        self.engine.suggestion_engine.generate_suggestion(
            SuggestionType.OPTIMIZATION, "Optimize", "Description",
            "HIGH", "LOW", 0.8, {}
        )
        
        report = self.engine.generate_optimization_report()
        self.assertIn("needs_anticipation", report)
        self.assertIn("proactive_suggestions", report)
        self.assertIn("timing_optimization", report)
        self.assertIn("resource_forecasting", report)
        self.assertIn("impact_modeling", report)
        
    def test_component_integration(self):
        # Test that all components work together
        self.engine.needs_system.anticipate_need(
            NeedType.WORKFLOW_EXECUTION, "Workflow", 0.85,
            datetime.now() + timedelta(hours=2), {}, "pattern"
        )
        
        self.engine.timing_optimizer.record_activity(
            ActivityType.PLANNING,
            datetime.now().replace(hour=8),
            60, 0.9, {}
        )
        
        self.engine.resource_forecaster.record_usage(
            ResourceType.COMPUTE, 70.0, 100.0
        )
        
        report = self.engine.generate_optimization_report()
        self.assertGreater(report["needs_anticipation"]["total_anticipated"], 0)


if __name__ == "__main__":
    unittest.main()
