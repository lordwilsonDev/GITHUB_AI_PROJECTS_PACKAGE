"""
Tests for Meta-Learning Analysis System
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from meta_learning import (
    LearningMethod, KnowledgeArea,
    LearningMethodAnalyzer, KnowledgeGapIdentifier,
    AutomationSuccessTracker, SatisfactionAnalyzer,
    ImprovementPlanner, MetaLearningEngine
)


class TestLearningMethodAnalyzer:
    """Test learning method analysis"""
    
    def test_initialization(self):
        analyzer = LearningMethodAnalyzer()
        assert len(analyzer.method_metrics) == len(LearningMethod)
        assert len(analyzer.learning_events) == 0
    
    def test_record_learning_event(self):
        analyzer = LearningMethodAnalyzer()
        analyzer.record_learning_event(
            method=LearningMethod.PATTERN_ANALYSIS,
            success=True,
            time_taken=5.0,
            confidence_gain=0.8,
            impact_score=0.9
        )
        
        metrics = analyzer.method_metrics[LearningMethod.PATTERN_ANALYSIS]
        assert metrics.total_applications == 1
        assert metrics.successful_applications == 1
        assert metrics.avg_time_to_learn == 5.0
        assert metrics.avg_confidence_gain == 0.8
        assert metrics.avg_impact_score == 0.9
        assert metrics.effectiveness_score > 0
    
    def test_effectiveness_calculation(self):
        analyzer = LearningMethodAnalyzer()
        
        # Record multiple events
        for i in range(10):
            analyzer.record_learning_event(
                method=LearningMethod.PATTERN_ANALYSIS,
                success=i < 8,  # 80% success rate
                time_taken=5.0,
                confidence_gain=0.7,
                impact_score=0.8
            )
        
        metrics = analyzer.method_metrics[LearningMethod.PATTERN_ANALYSIS]
        # Effectiveness = 0.8 * 0.4 + 0.7 * 0.3 + 0.8 * 0.3 = 0.77
        assert 0.75 < metrics.effectiveness_score < 0.79
    
    def test_get_most_effective_methods(self):
        analyzer = LearningMethodAnalyzer()
        
        # Create different effectiveness scores
        analyzer.record_learning_event(
            LearningMethod.PATTERN_ANALYSIS, True, 5.0, 0.9, 0.9
        )
        analyzer.record_learning_event(
            LearningMethod.SUCCESS_FAILURE_ANALYSIS, True, 5.0, 0.5, 0.5
        )
        
        top_methods = analyzer.get_most_effective_methods(2)
        assert len(top_methods) <= 2
        assert top_methods[0].effectiveness_score >= top_methods[1].effectiveness_score
    
    def test_method_trends(self):
        analyzer = LearningMethodAnalyzer()
        
        # Record recent successful events
        for _ in range(8):
            analyzer.record_learning_event(
                LearningMethod.PATTERN_ANALYSIS, True, 5.0, 0.8, 0.9
            )
        
        trends = analyzer.get_method_trends(LearningMethod.PATTERN_ANALYSIS, days=7)
        assert trends['trend'] == 'improving'
        assert trends['success_rate'] > 0.7


class TestKnowledgeGapIdentifier:
    """Test knowledge gap identification"""
    
    def test_initialization(self):
        identifier = KnowledgeGapIdentifier()
        assert len(identifier.knowledge_gaps) == 0
    
    def test_report_knowledge_gap(self):
        identifier = KnowledgeGapIdentifier()
        identifier.report_knowledge_gap(
            area=KnowledgeArea.TECHNICAL,
            topic="Python async programming",
            severity=0.8,
            context="Failed to implement async task"
        )
        
        assert len(identifier.knowledge_gaps) == 1
        gap_key = "technical:Python async programming"
        assert gap_key in identifier.knowledge_gaps
        gap = identifier.knowledge_gaps[gap_key]
        assert gap.severity == 0.8
        assert gap.frequency_encountered == 1
    
    def test_gap_frequency_tracking(self):
        identifier = KnowledgeGapIdentifier()
        
        # Report same gap multiple times
        for i in range(5):
            identifier.report_knowledge_gap(
                area=KnowledgeArea.TECHNICAL,
                topic="Python async programming",
                severity=0.7 + (i * 0.01)
            )
        
        gap_key = "technical:Python async programming"
        gap = identifier.knowledge_gaps[gap_key]
        assert gap.frequency_encountered == 5
        assert gap.research_priority > 0.5
    
    def test_priority_calculation(self):
        identifier = KnowledgeGapIdentifier()
        
        # High severity, high frequency
        identifier.report_knowledge_gap(
            KnowledgeArea.TECHNICAL, "Critical topic", 0.9
        )
        for _ in range(10):
            identifier.report_knowledge_gap(
                KnowledgeArea.TECHNICAL, "Critical topic", 0.9
            )
        
        # Low severity, low frequency
        identifier.report_knowledge_gap(
            KnowledgeArea.DOMAIN_SPECIFIC, "Minor topic", 0.2
        )
        
        top_gaps = identifier.get_top_priority_gaps(2)
        assert top_gaps[0].topic == "Critical topic"
        assert top_gaps[0].research_priority > top_gaps[1].research_priority
    
    def test_gap_resolution(self):
        identifier = KnowledgeGapIdentifier()
        identifier.report_knowledge_gap(
            KnowledgeArea.TECHNICAL, "Test topic", 0.7
        )
        identifier.record_gap_resolution(
            KnowledgeArea.TECHNICAL, "Test topic", "Read documentation"
        )
        
        gap_key = "technical:Test topic"
        gap = identifier.knowledge_gaps[gap_key]
        assert len(gap.attempted_solutions) == 1
        assert gap.attempted_solutions[0] == "Read documentation"
    
    def test_get_gaps_by_area(self):
        identifier = KnowledgeGapIdentifier()
        identifier.report_knowledge_gap(KnowledgeArea.TECHNICAL, "Topic 1", 0.7)
        identifier.report_knowledge_gap(KnowledgeArea.TECHNICAL, "Topic 2", 0.6)
        identifier.report_knowledge_gap(KnowledgeArea.DOMAIN_SPECIFIC, "Topic 3", 0.8)
        
        technical_gaps = identifier.get_gaps_by_area(KnowledgeArea.TECHNICAL)
        assert len(technical_gaps) == 2


class TestAutomationSuccessTracker:
    """Test automation success tracking"""
    
    def test_initialization(self):
        tracker = AutomationSuccessTracker()
        assert len(tracker.automations) == 0
    
    def test_register_automation(self):
        tracker = AutomationSuccessTracker()
        tracker.register_automation("auto_001", "Email automation")
        
        assert "auto_001" in tracker.automations
        assert tracker.automations["auto_001"].name == "Email automation"
    
    def test_record_execution(self):
        tracker = AutomationSuccessTracker()
        tracker.register_automation("auto_001", "Test automation")
        tracker.record_execution(
            automation_id="auto_001",
            success=True,
            execution_time=2.5,
            time_saved=60.0,
            user_satisfaction=0.9
        )
        
        metrics = tracker.automations["auto_001"]
        assert metrics.total_executions == 1
        assert metrics.successful_executions == 1
        assert metrics.time_saved == 60.0
        assert metrics.user_satisfaction == 0.9
    
    def test_roi_calculation(self):
        tracker = AutomationSuccessTracker()
        tracker.register_automation("auto_001", "High ROI automation")
        
        # Record multiple successful executions with high time savings
        for _ in range(10):
            tracker.record_execution(
                "auto_001", True, 1.0, 300.0, 0.9
            )
        
        metrics = tracker.automations["auto_001"]
        assert metrics.roi_score > 0.7  # Should be high
    
    def test_get_top_performing(self):
        tracker = AutomationSuccessTracker()
        
        # Create automations with different performance
        tracker.register_automation("auto_001", "Good automation")
        for _ in range(10):
            tracker.record_execution("auto_001", True, 1.0, 100.0, 0.9)
        
        tracker.register_automation("auto_002", "Poor automation")
        for _ in range(10):
            tracker.record_execution("auto_002", False, 5.0, 10.0, 0.3)
        
        top = tracker.get_top_performing_automations(1)
        assert top[0].automation_id == "auto_001"
    
    def test_underperforming_detection(self):
        tracker = AutomationSuccessTracker()
        tracker.register_automation("auto_001", "Bad automation")
        
        # Record mostly failures
        for i in range(10):
            tracker.record_execution("auto_001", i < 3, 1.0, 10.0, 0.2)
        
        underperforming = tracker.get_underperforming_automations(0.5)
        assert len(underperforming) > 0
        assert underperforming[0].automation_id == "auto_001"


class TestSatisfactionAnalyzer:
    """Test satisfaction analysis"""
    
    def test_initialization(self):
        analyzer = SatisfactionAnalyzer()
        assert len(analyzer.satisfaction_data) == 0
    
    def test_record_satisfaction(self):
        analyzer = SatisfactionAnalyzer()
        analyzer.record_satisfaction(
            task_type="email_processing",
            completion_time=30.0,
            user_rating=0.8,
            productivity_gain=0.5,
            errors_encountered=0
        )
        
        assert len(analyzer.satisfaction_data) == 1
        assert "email_processing" in analyzer.task_type_stats
    
    def test_task_type_statistics(self):
        analyzer = SatisfactionAnalyzer()
        
        # Record multiple tasks of same type
        for i in range(5):
            analyzer.record_satisfaction(
                task_type="email_processing",
                completion_time=30.0,
                user_rating=0.8,
                productivity_gain=0.4
            )
        
        stats = analyzer.task_type_stats["email_processing"]
        assert stats['count'] == 5
        assert stats['avg_rating'] == 0.8
        assert stats['avg_productivity_gain'] == 0.4
    
    def test_overall_satisfaction(self):
        analyzer = SatisfactionAnalyzer()
        
        # Record recent tasks
        for i in range(10):
            analyzer.record_satisfaction(
                task_type="test_task",
                completion_time=20.0,
                user_rating=0.7,
                productivity_gain=0.3,
                errors_encountered=i % 3  # Some errors
            )
        
        overall = analyzer.get_overall_satisfaction(days=7)
        assert overall['total_tasks'] == 10
        assert overall['avg_rating'] == 0.7
        assert overall['total_errors'] > 0
    
    def test_identify_improvement_areas(self):
        analyzer = SatisfactionAnalyzer()
        
        # Create a task type with low satisfaction
        for _ in range(10):
            analyzer.record_satisfaction(
                task_type="problematic_task",
                completion_time=60.0,
                user_rating=0.4,  # Low rating
                productivity_gain=0.05  # Low gain
            )
        
        improvements = analyzer.identify_improvement_areas()
        assert len(improvements) > 0
        assert improvements[0]['task_type'] == "problematic_task"
        assert 'low_satisfaction' in improvements[0]['issues']


class TestImprovementPlanner:
    """Test improvement planning"""
    
    def test_initialization(self):
        planner = ImprovementPlanner()
        assert len(planner.improvement_plans) == 0
    
    def test_create_improvement_plan(self):
        planner = ImprovementPlanner()
        plan_id = planner.create_improvement_plan(
            category="automation",
            description="Improve email automation",
            expected_impact=0.8,
            estimated_effort=2.0,
            target_days=7
        )
        
        assert len(planner.improvement_plans) == 1
        assert planner.improvement_plans[0].category == "automation"
    
    def test_prioritization(self):
        planner = ImprovementPlanner()
        
        # High impact, low effort (should be priority 1)
        planner.create_improvement_plan(
            "quick_win", "Quick improvement", 0.9, 0.5
        )
        
        # Low impact, high effort (should be lower priority)
        planner.create_improvement_plan(
            "big_project", "Large improvement", 0.3, 5.0
        )
        
        plans = planner.get_next_improvements(2)
        assert plans[0].category == "quick_win"
    
    def test_plan_lifecycle(self):
        planner = ImprovementPlanner()
        planner.create_improvement_plan(
            "test", "Test improvement", 0.7, 1.0
        )
        
        # Start the plan
        planner.start_improvement(0)
        assert planner.improvement_plans[0].status == 'in_progress'
        
        # Complete the plan
        planner.complete_improvement(0)
        assert planner.improvement_plans[0].status == 'completed'
        assert len(planner.completed_improvements) == 1
    
    def test_get_improvements_by_category(self):
        planner = ImprovementPlanner()
        planner.create_improvement_plan("automation", "Auto 1", 0.7, 1.0)
        planner.create_improvement_plan("automation", "Auto 2", 0.6, 1.5)
        planner.create_improvement_plan("knowledge", "Know 1", 0.8, 2.0)
        
        automation_plans = planner.get_improvements_by_category("automation")
        assert len(automation_plans) == 2


class TestMetaLearningEngine:
    """Test meta-learning engine orchestration"""
    
    def test_initialization(self):
        engine = MetaLearningEngine()
        assert engine.learning_analyzer is not None
        assert engine.gap_identifier is not None
        assert engine.automation_tracker is not None
        assert engine.satisfaction_analyzer is not None
        assert engine.improvement_planner is not None
    
    def test_custom_config(self):
        config = {
            'max_learning_history': 5000,
            'max_knowledge_gaps': 500,
            'cycle_interval_minutes': 10
        }
        engine = MetaLearningEngine(config)
        assert engine.learning_analyzer.max_history == 5000
        assert engine.gap_identifier.max_gaps == 500
        assert engine.cycle_interval == 600  # 10 minutes in seconds
    
    def test_meta_learning_report(self):
        engine = MetaLearningEngine()
        
        # Add some data
        engine.learning_analyzer.record_learning_event(
            LearningMethod.PATTERN_ANALYSIS, True, 5.0, 0.8, 0.9
        )
        engine.gap_identifier.report_knowledge_gap(
            KnowledgeArea.TECHNICAL, "Test topic", 0.7
        )
        engine.automation_tracker.register_automation("auto_001", "Test")
        engine.automation_tracker.record_execution("auto_001", True, 1.0, 60.0, 0.8)
        
        report = engine.get_meta_learning_report()
        
        assert 'timestamp' in report
        assert 'learning_methods' in report
        assert 'knowledge_gaps' in report
        assert 'automation_performance' in report
        assert 'user_satisfaction' in report
        assert 'improvement_plans' in report
    
    @pytest.mark.asyncio
    async def test_start_stop(self):
        engine = MetaLearningEngine({'cycle_interval_minutes': 0.01})
        
        # Start engine
        task = asyncio.create_task(engine.start())
        assert engine.is_running
        
        # Let it run briefly
        await asyncio.sleep(0.1)
        
        # Stop engine
        await engine.stop()
        assert not engine.is_running
        
        # Cancel the task
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
