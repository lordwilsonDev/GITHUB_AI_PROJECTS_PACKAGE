"""
System Evolution Tracking Module

Tracks system evolution through version history, performance metrics,
optimization strategies, experiment logs, and best practices database.

Components:
- VersionHistorySystem: Tracks all system versions and changes
- PerformanceMetricsTracker: Monitors performance across iterations
- OptimizationStrategyCatalog: Catalogs successful optimization strategies
- ExperimentLogger: Logs all experiments and their outcomes
- BestPracticesDatabase: Maintains database of best practices
- EvolutionTrackerEngine: Orchestrates all tracking components
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict


class ChangeType(Enum):
    """Types of system changes"""
    FEATURE_ADDED = "feature_added"
    FEATURE_MODIFIED = "feature_modified"
    FEATURE_REMOVED = "feature_removed"
    BUG_FIX = "bug_fix"
    PERFORMANCE_IMPROVEMENT = "performance_improvement"
    SECURITY_UPDATE = "security_update"
    CONFIGURATION_CHANGE = "configuration_change"
    DEPENDENCY_UPDATE = "dependency_update"


class ExperimentStatus(Enum):
    """Status of experiments"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StrategyCategory(Enum):
    """Categories of optimization strategies"""
    PERFORMANCE = "performance"
    EFFICIENCY = "efficiency"
    ACCURACY = "accuracy"
    USER_EXPERIENCE = "user_experience"
    RELIABILITY = "reliability"
    SCALABILITY = "scalability"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"


@dataclass
class Version:
    """Represents a system version"""
    version_number: str
    timestamp: datetime
    changes: List[Dict[str, Any]]
    author: str
    description: str
    rollback_available: bool = True
    tags: List[str] = field(default_factory=list)


@dataclass
class PerformanceSnapshot:
    """Snapshot of system performance"""
    timestamp: datetime
    version: str
    metrics: Dict[str, float]
    baseline_comparison: Dict[str, float] = field(default_factory=dict)


@dataclass
class OptimizationStrategy:
    """Represents an optimization strategy"""
    strategy_id: str
    name: str
    category: StrategyCategory
    description: str
    success_rate: float
    avg_improvement: float
    use_count: int
    first_used: datetime
    last_used: datetime
    prerequisites: List[str] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)


@dataclass
class Experiment:
    """Represents an experiment"""
    experiment_id: str
    name: str
    hypothesis: str
    methodology: str
    status: ExperimentStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)
    conclusions: List[str] = field(default_factory=list)
    success: Optional[bool] = None


@dataclass
class BestPractice:
    """Represents a best practice"""
    practice_id: str
    title: str
    description: str
    category: str
    confidence: float
    evidence_count: int
    created: datetime
    last_validated: datetime
    related_strategies: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)


class VersionHistorySystem:
    """Tracks all system versions and changes"""
    
    def __init__(self, max_versions: int = 1000):
        self.versions: List[Version] = []
        self.max_versions = max_versions
        self.current_version = "1.0.0"
        
    def create_version(
        self,
        version_number: str,
        changes: List[Dict[str, Any]],
        author: str,
        description: str,
        tags: Optional[List[str]] = None
    ) -> Version:
        """Create a new version"""
        version = Version(
            version_number=version_number,
            timestamp=datetime.now(),
            changes=changes,
            author=author,
            description=description,
            tags=tags or []
        )
        
        self.versions.append(version)
        self.current_version = version_number
        
        # Maintain max versions
        if len(self.versions) > self.max_versions:
            self.versions = self.versions[-self.max_versions:]
            
        return version
    
    def get_version(self, version_number: str) -> Optional[Version]:
        """Get a specific version"""
        for version in self.versions:
            if version.version_number == version_number:
                return version
        return None
    
    def get_version_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        change_type: Optional[ChangeType] = None
    ) -> List[Version]:
        """Get version history with optional filters"""
        filtered = self.versions
        
        if start_date:
            filtered = [v for v in filtered if v.timestamp >= start_date]
        if end_date:
            filtered = [v for v in filtered if v.timestamp <= end_date]
        if change_type:
            filtered = [
                v for v in filtered
                if any(c.get('type') == change_type.value for c in v.changes)
            ]
            
        return sorted(filtered, key=lambda v: v.timestamp, reverse=True)
    
    def get_changes_by_type(self, change_type: ChangeType) -> List[Dict[str, Any]]:
        """Get all changes of a specific type"""
        changes = []
        for version in self.versions:
            for change in version.changes:
                if change.get('type') == change_type.value:
                    changes.append({
                        **change,
                        'version': version.version_number,
                        'timestamp': version.timestamp
                    })
        return changes
    
    def compare_versions(
        self,
        version1: str,
        version2: str
    ) -> Dict[str, Any]:
        """Compare two versions"""
        v1 = self.get_version(version1)
        v2 = self.get_version(version2)
        
        if not v1 or not v2:
            return {}
        
        return {
            'version1': version1,
            'version2': version2,
            'time_difference': (v2.timestamp - v1.timestamp).total_seconds(),
            'changes_between': len(v2.changes),
            'v1_changes': v1.changes,
            'v2_changes': v2.changes
        }


class PerformanceMetricsTracker:
    """Monitors performance across iterations"""
    
    def __init__(self, max_snapshots: int = 10000):
        self.snapshots: List[PerformanceSnapshot] = []
        self.max_snapshots = max_snapshots
        self.baseline_metrics: Dict[str, float] = {}
        
    def set_baseline(self, metrics: Dict[str, float]):
        """Set baseline metrics for comparison"""
        self.baseline_metrics = metrics.copy()
    
    def record_snapshot(
        self,
        version: str,
        metrics: Dict[str, float]
    ) -> PerformanceSnapshot:
        """Record a performance snapshot"""
        # Calculate baseline comparison
        comparison = {}
        for metric, value in metrics.items():
            if metric in self.baseline_metrics:
                baseline = self.baseline_metrics[metric]
                if baseline != 0:
                    comparison[metric] = ((value - baseline) / baseline) * 100
                else:
                    comparison[metric] = 0.0
        
        snapshot = PerformanceSnapshot(
            timestamp=datetime.now(),
            version=version,
            metrics=metrics,
            baseline_comparison=comparison
        )
        
        self.snapshots.append(snapshot)
        
        # Maintain max snapshots
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots = self.snapshots[-self.max_snapshots:]
            
        return snapshot
    
    def get_performance_trend(
        self,
        metric_name: str,
        time_window: Optional[timedelta] = None
    ) -> List[Dict[str, Any]]:
        """Get performance trend for a metric"""
        snapshots = self.snapshots
        
        if time_window:
            cutoff = datetime.now() - time_window
            snapshots = [s for s in snapshots if s.timestamp >= cutoff]
        
        trend = []
        for snapshot in snapshots:
            if metric_name in snapshot.metrics:
                trend.append({
                    'timestamp': snapshot.timestamp,
                    'version': snapshot.version,
                    'value': snapshot.metrics[metric_name],
                    'vs_baseline': snapshot.baseline_comparison.get(metric_name, 0.0)
                })
        
        return trend
    
    def get_improvement_summary(self) -> Dict[str, Any]:
        """Get summary of improvements"""
        if not self.snapshots or not self.baseline_metrics:
            return {}
        
        latest = self.snapshots[-1]
        summary = {
            'current_version': latest.version,
            'metrics': {},
            'overall_improvement': 0.0
        }
        
        improvements = []
        for metric, value in latest.metrics.items():
            if metric in self.baseline_metrics:
                baseline = self.baseline_metrics[metric]
                if baseline != 0:
                    improvement = ((value - baseline) / baseline) * 100
                    improvements.append(improvement)
                    summary['metrics'][metric] = {
                        'current': value,
                        'baseline': baseline,
                        'improvement_pct': improvement
                    }
        
        if improvements:
            summary['overall_improvement'] = sum(improvements) / len(improvements)
        
        return summary
    
    def identify_regressions(
        self,
        threshold: float = -5.0
    ) -> List[Dict[str, Any]]:
        """Identify performance regressions"""
        if not self.snapshots:
            return []
        
        latest = self.snapshots[-1]
        regressions = []
        
        for metric, improvement in latest.baseline_comparison.items():
            if improvement < threshold:
                regressions.append({
                    'metric': metric,
                    'current_value': latest.metrics[metric],
                    'baseline_value': self.baseline_metrics.get(metric, 0),
                    'regression_pct': improvement,
                    'version': latest.version
                })
        
        return regressions


class OptimizationStrategyCatalog:
    """Catalogs successful optimization strategies"""
    
    def __init__(self, max_strategies: int = 1000):
        self.strategies: Dict[str, OptimizationStrategy] = {}
        self.max_strategies = max_strategies
        
    def add_strategy(
        self,
        strategy_id: str,
        name: str,
        category: StrategyCategory,
        description: str,
        prerequisites: Optional[List[str]] = None,
        best_practices: Optional[List[str]] = None
    ) -> OptimizationStrategy:
        """Add a new optimization strategy"""
        strategy = OptimizationStrategy(
            strategy_id=strategy_id,
            name=name,
            category=category,
            description=description,
            success_rate=0.0,
            avg_improvement=0.0,
            use_count=0,
            first_used=datetime.now(),
            last_used=datetime.now(),
            prerequisites=prerequisites or [],
            best_practices=best_practices or []
        )
        
        self.strategies[strategy_id] = strategy
        
        # Maintain max strategies (remove least used)
        if len(self.strategies) > self.max_strategies:
            sorted_strategies = sorted(
                self.strategies.items(),
                key=lambda x: x[1].use_count
            )
            del self.strategies[sorted_strategies[0][0]]
        
        return strategy
    
    def record_strategy_use(
        self,
        strategy_id: str,
        success: bool,
        improvement: float
    ):
        """Record use of a strategy"""
        if strategy_id not in self.strategies:
            return
        
        strategy = self.strategies[strategy_id]
        
        # Update success rate
        total_uses = strategy.use_count
        current_successes = strategy.success_rate * total_uses
        new_successes = current_successes + (1 if success else 0)
        strategy.use_count += 1
        strategy.success_rate = new_successes / strategy.use_count
        
        # Update average improvement
        current_total = strategy.avg_improvement * total_uses
        strategy.avg_improvement = (current_total + improvement) / strategy.use_count
        
        strategy.last_used = datetime.now()
    
    def get_top_strategies(
        self,
        category: Optional[StrategyCategory] = None,
        min_uses: int = 3,
        limit: int = 10
    ) -> List[OptimizationStrategy]:
        """Get top performing strategies"""
        strategies = list(self.strategies.values())
        
        # Filter by category and min uses
        if category:
            strategies = [s for s in strategies if s.category == category]
        strategies = [s for s in strategies if s.use_count >= min_uses]
        
        # Sort by success rate and improvement
        strategies.sort(
            key=lambda s: (s.success_rate * s.avg_improvement),
            reverse=True
        )
        
        return strategies[:limit]
    
    def get_strategy_recommendations(
        self,
        context: Dict[str, Any]
    ) -> List[OptimizationStrategy]:
        """Get strategy recommendations based on context"""
        recommendations = []
        
        for strategy in self.strategies.values():
            # Check if prerequisites are met
            if strategy.prerequisites:
                if not all(p in context.get('capabilities', []) for p in strategy.prerequisites):
                    continue
            
            # Only recommend strategies with good track record
            if strategy.use_count >= 3 and strategy.success_rate >= 0.7:
                recommendations.append(strategy)
        
        # Sort by effectiveness
        recommendations.sort(
            key=lambda s: (s.success_rate * s.avg_improvement),
            reverse=True
        )
        
        return recommendations[:5]


class ExperimentLogger:
    """Logs all experiments and their outcomes"""
    
    def __init__(self, max_experiments: int = 5000):
        self.experiments: Dict[str, Experiment] = {}
        self.max_experiments = max_experiments
        
    def create_experiment(
        self,
        experiment_id: str,
        name: str,
        hypothesis: str,
        methodology: str
    ) -> Experiment:
        """Create a new experiment"""
        experiment = Experiment(
            experiment_id=experiment_id,
            name=name,
            hypothesis=hypothesis,
            methodology=methodology,
            status=ExperimentStatus.PLANNED,
            start_time=datetime.now()
        )
        
        self.experiments[experiment_id] = experiment
        
        # Maintain max experiments
        if len(self.experiments) > self.max_experiments:
            # Remove oldest completed/failed experiments
            sorted_exps = sorted(
                [(k, v) for k, v in self.experiments.items()
                 if v.status in [ExperimentStatus.COMPLETED, ExperimentStatus.FAILED]],
                key=lambda x: x[1].start_time
            )
            if sorted_exps:
                del self.experiments[sorted_exps[0][0]]
        
        return experiment
    
    def start_experiment(self, experiment_id: str):
        """Start an experiment"""
        if experiment_id in self.experiments:
            self.experiments[experiment_id].status = ExperimentStatus.IN_PROGRESS
    
    def complete_experiment(
        self,
        experiment_id: str,
        results: Dict[str, Any],
        conclusions: List[str],
        success: bool
    ):
        """Complete an experiment"""
        if experiment_id not in self.experiments:
            return
        
        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.COMPLETED
        experiment.end_time = datetime.now()
        experiment.results = results
        experiment.conclusions = conclusions
        experiment.success = success
    
    def fail_experiment(
        self,
        experiment_id: str,
        reason: str
    ):
        """Mark experiment as failed"""
        if experiment_id not in self.experiments:
            return
        
        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.FAILED
        experiment.end_time = datetime.now()
        experiment.results = {'failure_reason': reason}
        experiment.success = False
    
    def get_experiment_results(
        self,
        status: Optional[ExperimentStatus] = None,
        success_only: bool = False
    ) -> List[Experiment]:
        """Get experiment results"""
        experiments = list(self.experiments.values())
        
        if status:
            experiments = [e for e in experiments if e.status == status]
        if success_only:
            experiments = [e for e in experiments if e.success is True]
        
        return sorted(experiments, key=lambda e: e.start_time, reverse=True)
    
    def get_success_rate(self) -> float:
        """Get overall experiment success rate"""
        completed = [
            e for e in self.experiments.values()
            if e.status == ExperimentStatus.COMPLETED
        ]
        
        if not completed:
            return 0.0
        
        successful = sum(1 for e in completed if e.success)
        return successful / len(completed)
    
    def get_learnings(self) -> List[str]:
        """Extract learnings from all experiments"""
        learnings = []
        
        for experiment in self.experiments.values():
            if experiment.status == ExperimentStatus.COMPLETED:
                learnings.extend(experiment.conclusions)
        
        return learnings


class BestPracticesDatabase:
    """Maintains database of best practices"""
    
    def __init__(self, max_practices: int = 2000):
        self.practices: Dict[str, BestPractice] = {}
        self.max_practices = max_practices
        self.categories: Set[str] = set()
        
    def add_practice(
        self,
        practice_id: str,
        title: str,
        description: str,
        category: str,
        initial_confidence: float = 0.5,
        related_strategies: Optional[List[str]] = None,
        examples: Optional[List[str]] = None
    ) -> BestPractice:
        """Add a new best practice"""
        practice = BestPractice(
            practice_id=practice_id,
            title=title,
            description=description,
            category=category,
            confidence=initial_confidence,
            evidence_count=1,
            created=datetime.now(),
            last_validated=datetime.now(),
            related_strategies=related_strategies or [],
            examples=examples or []
        )
        
        self.practices[practice_id] = practice
        self.categories.add(category)
        
        # Maintain max practices (remove lowest confidence)
        if len(self.practices) > self.max_practices:
            sorted_practices = sorted(
                self.practices.items(),
                key=lambda x: x[1].confidence
            )
            removed = sorted_practices[0]
            del self.practices[removed[0]]
            
        return practice
    
    def validate_practice(
        self,
        practice_id: str,
        success: bool
    ):
        """Validate a best practice"""
        if practice_id not in self.practices:
            return
        
        practice = self.practices[practice_id]
        
        # Update confidence based on validation
        if success:
            practice.confidence = min(1.0, practice.confidence + 0.05)
        else:
            practice.confidence = max(0.0, practice.confidence - 0.1)
        
        practice.evidence_count += 1
        practice.last_validated = datetime.now()
    
    def get_practices_by_category(
        self,
        category: str,
        min_confidence: float = 0.6
    ) -> List[BestPractice]:
        """Get practices by category"""
        practices = [
            p for p in self.practices.values()
            if p.category == category and p.confidence >= min_confidence
        ]
        
        return sorted(practices, key=lambda p: p.confidence, reverse=True)
    
    def get_top_practices(
        self,
        limit: int = 20,
        min_confidence: float = 0.7
    ) -> List[BestPractice]:
        """Get top best practices"""
        practices = [
            p for p in self.practices.values()
            if p.confidence >= min_confidence
        ]
        
        practices.sort(
            key=lambda p: (p.confidence * p.evidence_count),
            reverse=True
        )
        
        return practices[:limit]
    
    def search_practices(
        self,
        query: str,
        min_confidence: float = 0.5
    ) -> List[BestPractice]:
        """Search for practices"""
        query_lower = query.lower()
        results = []
        
        for practice in self.practices.values():
            if practice.confidence < min_confidence:
                continue
            
            if (query_lower in practice.title.lower() or
                query_lower in practice.description.lower() or
                query_lower in practice.category.lower()):
                results.append(practice)
        
        return sorted(results, key=lambda p: p.confidence, reverse=True)
    
    def prune_low_confidence(self, threshold: float = 0.3):
        """Remove low confidence practices"""
        to_remove = [
            pid for pid, practice in self.practices.items()
            if practice.confidence < threshold
        ]
        
        for pid in to_remove:
            del self.practices[pid]


class EvolutionTrackerEngine:
    """Orchestrates all evolution tracking components"""
    
    def __init__(
        self,
        cycle_interval: int = 3600  # 60 minutes
    ):
        self.version_history = VersionHistorySystem()
        self.performance_tracker = PerformanceMetricsTracker()
        self.strategy_catalog = OptimizationStrategyCatalog()
        self.experiment_logger = ExperimentLogger()
        self.best_practices = BestPracticesDatabase()
        
        self.cycle_interval = cycle_interval
        self.is_running = False
        
    async def start(self):
        """Start the evolution tracking engine"""
        self.is_running = True
        
        while self.is_running:
            await self.run_tracking_cycle()
            await asyncio.sleep(self.cycle_interval)
    
    async def run_tracking_cycle(self):
        """Run a single tracking cycle"""
        # Generate evolution report
        report = self.generate_evolution_report()
        
        # Prune low confidence practices
        self.best_practices.prune_low_confidence()
        
        return report
    
    def generate_evolution_report(self) -> Dict[str, Any]:
        """Generate comprehensive evolution report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'current_version': self.version_history.current_version,
            'total_versions': len(self.version_history.versions),
            'performance_summary': self.performance_tracker.get_improvement_summary(),
            'top_strategies': [
                {
                    'name': s.name,
                    'category': s.category.value,
                    'success_rate': s.success_rate,
                    'avg_improvement': s.avg_improvement,
                    'use_count': s.use_count
                }
                for s in self.strategy_catalog.get_top_strategies(limit=5)
            ],
            'experiment_success_rate': self.experiment_logger.get_success_rate(),
            'total_experiments': len(self.experiment_logger.experiments),
            'best_practices_count': len(self.best_practices.practices),
            'practice_categories': list(self.best_practices.categories)
        }
    
    def stop(self):
        """Stop the evolution tracking engine"""
        self.is_running = False


# Example usage
if __name__ == "__main__":
    # Create engine
    engine = EvolutionTrackerEngine(cycle_interval=3600)
    
    # Create a version
    engine.version_history.create_version(
        version_number="1.1.0",
        changes=[
            {
                'type': ChangeType.FEATURE_ADDED.value,
                'description': 'Added evolution tracking',
                'impact': 'high'
            }
        ],
        author="system",
        description="Added comprehensive evolution tracking system"
    )
    
    # Record performance
    engine.performance_tracker.set_baseline({
        'response_time': 1.0,
        'accuracy': 0.85,
        'throughput': 100
    })
    
    engine.performance_tracker.record_snapshot(
        version="1.1.0",
        metrics={
            'response_time': 0.8,
            'accuracy': 0.90,
            'throughput': 120
        }
    )
    
    # Add strategy
    engine.strategy_catalog.add_strategy(
        strategy_id="cache_optimization",
        name="Cache Optimization",
        category=StrategyCategory.PERFORMANCE,
        description="Optimize caching strategy for better performance"
    )
    
    # Create experiment
    engine.experiment_logger.create_experiment(
        experiment_id="exp_001",
        name="Test new caching",
        hypothesis="Caching will improve response time by 20%",
        methodology="A/B test with 50/50 split"
    )
    
    # Add best practice
    engine.best_practices.add_practice(
        practice_id="bp_001",
        title="Always validate inputs",
        description="Validate all user inputs before processing",
        category="security",
        initial_confidence=0.9
    )
    
    # Generate report
    report = engine.generate_evolution_report()
    print("Evolution Report:")
    print(f"Current Version: {report['current_version']}")
    print(f"Total Versions: {report['total_versions']}")
    print(f"Experiment Success Rate: {report['experiment_success_rate']:.2%}")
    print(f"Best Practices: {report['best_practices_count']}")
