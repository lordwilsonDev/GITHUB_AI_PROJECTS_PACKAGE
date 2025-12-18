"""
Tests for Evolution Tracker Module
"""

import pytest
from datetime import datetime, timedelta
from evolution_tracker import (
    VersionHistorySystem, PerformanceMetricsTracker,
    OptimizationStrategyCatalog, ExperimentLogger,
    BestPracticesDatabase, EvolutionTrackerEngine,
    ChangeType, ExperimentStatus, StrategyCategory
)


class TestVersionHistorySystem:
    """Test version history tracking"""
    
    def test_create_version(self):
        system = VersionHistorySystem()
        version = system.create_version(
            version_number="1.0.0",
            changes=[{'type': ChangeType.FEATURE_ADDED.value, 'desc': 'Initial'}],
            author="test",
            description="First version"
        )
        
        assert version.version_number == "1.0.0"
        assert system.current_version == "1.0.0"
        assert len(system.versions) == 1
    
    def test_get_version(self):
        system = VersionHistorySystem()
        system.create_version("1.0.0", [], "test", "Test")
        
        version = system.get_version("1.0.0")
        assert version is not None
        assert version.version_number == "1.0.0"
    
    def test_version_history_filtering(self):
        system = VersionHistorySystem()
        
        # Create versions with different change types
        system.create_version(
            "1.0.0",
            [{'type': ChangeType.FEATURE_ADDED.value}],
            "test", "V1"
        )
        system.create_version(
            "1.1.0",
            [{'type': ChangeType.BUG_FIX.value}],
            "test", "V2"
        )
        
        # Filter by change type
        features = system.get_version_history(change_type=ChangeType.FEATURE_ADDED)
        assert len(features) == 1
        assert features[0].version_number == "1.0.0"
    
    def test_compare_versions(self):
        system = VersionHistorySystem()
        system.create_version("1.0.0", [], "test", "V1")
        system.create_version("2.0.0", [], "test", "V2")
        
        comparison = system.compare_versions("1.0.0", "2.0.0")
        assert comparison['version1'] == "1.0.0"
        assert comparison['version2'] == "2.0.0"
        assert 'time_difference' in comparison


class TestPerformanceMetricsTracker:
    """Test performance metrics tracking"""
    
    def test_set_baseline(self):
        tracker = PerformanceMetricsTracker()
        tracker.set_baseline({'metric1': 100.0, 'metric2': 50.0})
        
        assert tracker.baseline_metrics['metric1'] == 100.0
        assert tracker.baseline_metrics['metric2'] == 50.0
    
    def test_record_snapshot(self):
        tracker = PerformanceMetricsTracker()
        tracker.set_baseline({'response_time': 1.0})
        
        snapshot = tracker.record_snapshot(
            version="1.0.0",
            metrics={'response_time': 0.8}
        )
        
        assert snapshot.version == "1.0.0"
        assert snapshot.metrics['response_time'] == 0.8
        # 20% improvement
        assert snapshot.baseline_comparison['response_time'] == -20.0
    
    def test_performance_trend(self):
        tracker = PerformanceMetricsTracker()
        tracker.set_baseline({'metric': 100.0})
        
        tracker.record_snapshot("1.0", {'metric': 90.0})
        tracker.record_snapshot("1.1", {'metric': 80.0})
        
        trend = tracker.get_performance_trend('metric')
        assert len(trend) == 2
        assert trend[0]['value'] == 90.0
        assert trend[1]['value'] == 80.0
    
    def test_improvement_summary(self):
        tracker = PerformanceMetricsTracker()
        tracker.set_baseline({'metric1': 100.0, 'metric2': 50.0})
        tracker.record_snapshot("1.0", {'metric1': 80.0, 'metric2': 40.0})
        
        summary = tracker.get_improvement_summary()
        assert summary['current_version'] == "1.0"
        assert 'overall_improvement' in summary
        assert summary['overall_improvement'] == -20.0  # Both improved by 20%
    
    def test_identify_regressions(self):
        tracker = PerformanceMetricsTracker()
        tracker.set_baseline({'metric': 100.0})
        tracker.record_snapshot("1.0", {'metric': 120.0})  # 20% worse
        
        regressions = tracker.identify_regressions(threshold=-5.0)
        assert len(regressions) == 0  # 20% is above threshold
        
        regressions = tracker.identify_regressions(threshold=15.0)
        assert len(regressions) == 1
        assert regressions[0]['metric'] == 'metric'


class TestOptimizationStrategyCatalog:
    """Test optimization strategy catalog"""
    
    def test_add_strategy(self):
        catalog = OptimizationStrategyCatalog()
        strategy = catalog.add_strategy(
            strategy_id="s1",
            name="Test Strategy",
            category=StrategyCategory.PERFORMANCE,
            description="Test"
        )
        
        assert strategy.strategy_id == "s1"
        assert strategy.name == "Test Strategy"
        assert strategy.use_count == 0
    
    def test_record_strategy_use(self):
        catalog = OptimizationStrategyCatalog()
        catalog.add_strategy(
            "s1", "Test", StrategyCategory.PERFORMANCE, "Test"
        )
        
        catalog.record_strategy_use("s1", success=True, improvement=10.0)
        catalog.record_strategy_use("s1", success=True, improvement=20.0)
        catalog.record_strategy_use("s1", success=False, improvement=0.0)
        
        strategy = catalog.strategies["s1"]
        assert strategy.use_count == 3
        assert strategy.success_rate == 2/3
        assert strategy.avg_improvement == 10.0  # (10+20+0)/3
    
    def test_get_top_strategies(self):
        catalog = OptimizationStrategyCatalog()
        
        # Add strategies with different performance
        catalog.add_strategy("s1", "Good", StrategyCategory.PERFORMANCE, "Test")
        catalog.add_strategy("s2", "Better", StrategyCategory.PERFORMANCE, "Test")
        
        # Record uses
        for _ in range(5):
            catalog.record_strategy_use("s1", True, 10.0)
        for _ in range(5):
            catalog.record_strategy_use("s2", True, 20.0)
        
        top = catalog.get_top_strategies(min_uses=3, limit=2)
        assert len(top) == 2
        assert top[0].strategy_id == "s2"  # Better performance
    
    def test_strategy_recommendations(self):
        catalog = OptimizationStrategyCatalog()
        
        catalog.add_strategy(
            "s1", "Test", StrategyCategory.PERFORMANCE, "Test",
            prerequisites=["feature_x"]
        )
        
        # Record successful uses
        for _ in range(5):
            catalog.record_strategy_use("s1", True, 15.0)
        
        # Without prerequisite
        recs = catalog.get_strategy_recommendations({'capabilities': []})
        assert len(recs) == 0
        
        # With prerequisite
        recs = catalog.get_strategy_recommendations({'capabilities': ['feature_x']})
        assert len(recs) == 1


class TestExperimentLogger:
    """Test experiment logging"""
    
    def test_create_experiment(self):
        logger = ExperimentLogger()
        exp = logger.create_experiment(
            "exp1", "Test", "Hypothesis", "Method"
        )
        
        assert exp.experiment_id == "exp1"
        assert exp.status == ExperimentStatus.PLANNED
    
    def test_experiment_lifecycle(self):
        logger = ExperimentLogger()
        logger.create_experiment("exp1", "Test", "H", "M")
        
        logger.start_experiment("exp1")
        assert logger.experiments["exp1"].status == ExperimentStatus.IN_PROGRESS
        
        logger.complete_experiment(
            "exp1",
            results={'metric': 100},
            conclusions=['Works well'],
            success=True
        )
        
        exp = logger.experiments["exp1"]
        assert exp.status == ExperimentStatus.COMPLETED
        assert exp.success is True
        assert len(exp.conclusions) == 1
    
    def test_fail_experiment(self):
        logger = ExperimentLogger()
        logger.create_experiment("exp1", "Test", "H", "M")
        logger.fail_experiment("exp1", "Technical issues")
        
        exp = logger.experiments["exp1"]
        assert exp.status == ExperimentStatus.FAILED
        assert exp.success is False
    
    def test_get_success_rate(self):
        logger = ExperimentLogger()
        
        logger.create_experiment("exp1", "T1", "H", "M")
        logger.complete_experiment("exp1", {}, [], True)
        
        logger.create_experiment("exp2", "T2", "H", "M")
        logger.complete_experiment("exp2", {}, [], True)
        
        logger.create_experiment("exp3", "T3", "H", "M")
        logger.complete_experiment("exp3", {}, [], False)
        
        assert logger.get_success_rate() == 2/3
    
    def test_get_learnings(self):
        logger = ExperimentLogger()
        
        logger.create_experiment("exp1", "T", "H", "M")
        logger.complete_experiment(
            "exp1", {}, ['Learning 1', 'Learning 2'], True
        )
        
        learnings = logger.get_learnings()
        assert len(learnings) == 2
        assert 'Learning 1' in learnings


class TestBestPracticesDatabase:
    """Test best practices database"""
    
    def test_add_practice(self):
        db = BestPracticesDatabase()
        practice = db.add_practice(
            "bp1", "Test Practice", "Description", "security"
        )
        
        assert practice.practice_id == "bp1"
        assert practice.category == "security"
        assert "security" in db.categories
    
    def test_validate_practice(self):
        db = BestPracticesDatabase()
        db.add_practice("bp1", "Test", "Desc", "cat", initial_confidence=0.5)
        
        # Successful validation increases confidence
        db.validate_practice("bp1", success=True)
        assert db.practices["bp1"].confidence == 0.55
        
        # Failed validation decreases confidence
        db.validate_practice("bp1", success=False)
        assert db.practices["bp1"].confidence == 0.45
    
    def test_get_practices_by_category(self):
        db = BestPracticesDatabase()
        db.add_practice("bp1", "T1", "D", "security", 0.8)
        db.add_practice("bp2", "T2", "D", "performance", 0.9)
        db.add_practice("bp3", "T3", "D", "security", 0.5)
        
        security_practices = db.get_practices_by_category("security", min_confidence=0.6)
        assert len(security_practices) == 1
        assert security_practices[0].practice_id == "bp1"
    
    def test_get_top_practices(self):
        db = BestPracticesDatabase()
        
        db.add_practice("bp1", "T1", "D", "cat", 0.9)
        db.add_practice("bp2", "T2", "D", "cat", 0.8)
        db.add_practice("bp3", "T3", "D", "cat", 0.6)
        
        # Validate to increase evidence count
        for _ in range(5):
            db.validate_practice("bp1", True)
        
        top = db.get_top_practices(limit=2, min_confidence=0.7)
        assert len(top) == 2
        assert top[0].practice_id == "bp1"  # Highest confidence * evidence
    
    def test_search_practices(self):
        db = BestPracticesDatabase()
        db.add_practice("bp1", "Input Validation", "Validate inputs", "security", 0.8)
        db.add_practice("bp2", "Cache Strategy", "Use caching", "performance", 0.9)
        
        results = db.search_practices("validation")
        assert len(results) == 1
        assert results[0].practice_id == "bp1"
    
    def test_prune_low_confidence(self):
        db = BestPracticesDatabase()
        db.add_practice("bp1", "T1", "D", "cat", 0.8)
        db.add_practice("bp2", "T2", "D", "cat", 0.2)
        
        db.prune_low_confidence(threshold=0.3)
        assert "bp1" in db.practices
        assert "bp2" not in db.practices


class TestEvolutionTrackerEngine:
    """Test evolution tracker engine integration"""
    
    def test_engine_initialization(self):
        engine = EvolutionTrackerEngine(cycle_interval=60)
        
        assert engine.version_history is not None
        assert engine.performance_tracker is not None
        assert engine.strategy_catalog is not None
        assert engine.experiment_logger is not None
        assert engine.best_practices is not None
        assert engine.cycle_interval == 60
    
    def test_generate_evolution_report(self):
        engine = EvolutionTrackerEngine()
        
        # Add some data
        engine.version_history.create_version("1.0.0", [], "test", "Test")
        engine.performance_tracker.set_baseline({'metric': 100})
        engine.performance_tracker.record_snapshot("1.0.0", {'metric': 90})
        
        report = engine.generate_evolution_report()
        
        assert 'timestamp' in report
        assert report['current_version'] == "1.0.0"
        assert report['total_versions'] == 1
        assert 'performance_summary' in report
        assert 'top_strategies' in report
        assert 'experiment_success_rate' in report


if __name__ == "__main__":
    # Run tests
    print("Running Evolution Tracker Tests...\n")
    
    # Version History Tests
    print("Testing VersionHistorySystem...")
    test = TestVersionHistorySystem()
    test.test_create_version()
    test.test_get_version()
    test.test_version_history_filtering()
    test.test_compare_versions()
    print("✅ VersionHistorySystem tests passed\n")
    
    # Performance Tracker Tests
    print("Testing PerformanceMetricsTracker...")
    test = TestPerformanceMetricsTracker()
    test.test_set_baseline()
    test.test_record_snapshot()
    test.test_performance_trend()
    test.test_improvement_summary()
    test.test_identify_regressions()
    print("✅ PerformanceMetricsTracker tests passed\n")
    
    # Strategy Catalog Tests
    print("Testing OptimizationStrategyCatalog...")
    test = TestOptimizationStrategyCatalog()
    test.test_add_strategy()
    test.test_record_strategy_use()
    test.test_get_top_strategies()
    test.test_strategy_recommendations()
    print("✅ OptimizationStrategyCatalog tests passed\n")
    
    # Experiment Logger Tests
    print("Testing ExperimentLogger...")
    test = TestExperimentLogger()
    test.test_create_experiment()
    test.test_experiment_lifecycle()
    test.test_fail_experiment()
    test.test_get_success_rate()
    test.test_get_learnings()
    print("✅ ExperimentLogger tests passed\n")
    
    # Best Practices Tests
    print("Testing BestPracticesDatabase...")
    test = TestBestPracticesDatabase()
    test.test_add_practice()
    test.test_validate_practice()
    test.test_get_practices_by_category()
    test.test_get_top_practices()
    test.test_search_practices()
    test.test_prune_low_confidence()
    print("✅ BestPracticesDatabase tests passed\n")
    
    # Engine Tests
    print("Testing EvolutionTrackerEngine...")
    test = TestEvolutionTrackerEngine()
    test.test_engine_initialization()
    test.test_generate_evolution_report()
    print("✅ EvolutionTrackerEngine tests passed\n")
    
    print("=" * 70)
    print("✅ ALL EVOLUTION TRACKER TESTS PASSED")
    print("=" * 70)
