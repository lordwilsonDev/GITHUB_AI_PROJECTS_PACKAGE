#!/usr/bin/env python3
"""
Performance Analyzer Module
Analyzes system and workflow performance to identify optimization opportunities.
Part of the Self-Evolving AI Ecosystem for vy-nexus.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics

@dataclass
class PerformanceMetric:
    """Represents a performance metric measurement."""
    metric_id: str
    timestamp: str
    category: str  # system, workflow, module, network, storage
    metric_name: str
    value: float
    unit: str
    context: Dict[str, Any]
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    
    def is_warning(self) -> bool:
        """Check if metric exceeds warning threshold."""
        if self.threshold_warning is None:
            return False
        return self.value >= self.threshold_warning
    
    def is_critical(self) -> bool:
        """Check if metric exceeds critical threshold."""
        if self.threshold_critical is None:
            return False
        return self.value >= self.threshold_critical

@dataclass
class PerformanceAnalysis:
    """Results of performance analysis."""
    analysis_id: str
    timestamp: str
    category: str
    time_period: str  # e.g., "last_hour", "last_day", "last_week"
    metrics_analyzed: int
    
    # Statistical analysis
    avg_value: float
    min_value: float
    max_value: float
    std_dev: float
    median_value: float
    
    # Trend analysis
    trend: str  # improving, degrading, stable
    trend_percentage: float
    
    # Issues identified
    warnings: List[Dict[str, Any]]
    critical_issues: List[Dict[str, Any]]
    
    # Recommendations
    recommendations: List[Dict[str, Any]]
    priority_score: float

@dataclass
class OptimizationOpportunity:
    """Represents an identified optimization opportunity."""
    opportunity_id: str
    timestamp: str
    category: str
    title: str
    description: str
    
    # Impact assessment
    current_performance: float
    potential_performance: float
    improvement_percentage: float
    
    # Implementation details
    difficulty: str  # easy, medium, hard
    estimated_effort_hours: float
    required_resources: List[str]
    
    # Priority
    priority_score: float
    roi_score: float
    
    # Status
    status: str  # identified, planned, in_progress, completed, rejected
    implementation_notes: str

class PerformanceAnalyzer:
    """Analyzes performance metrics and identifies optimization opportunities."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_dir = Path("/Users/lordwilson/vy-nexus/self-evolving-ecosystem")
        self.data_dir = self.base_dir / "data" / "process_enhancement" / "performance"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Data files
        self.metrics_file = self.data_dir / "metrics.jsonl"
        self.analyses_file = self.data_dir / "analyses.jsonl"
        self.opportunities_file = self.data_dir / "opportunities.jsonl"
        
        # In-memory caches
        self.metrics: List[PerformanceMetric] = []
        self.analyses: List[PerformanceAnalysis] = []
        self.opportunities: List[OptimizationOpportunity] = []
        
        # Performance thresholds (configurable)
        self.thresholds = {
            'cpu_usage': {'warning': 70.0, 'critical': 90.0},
            'memory_usage': {'warning': 75.0, 'critical': 90.0},
            'disk_usage': {'warning': 80.0, 'critical': 95.0},
            'response_time_ms': {'warning': 1000.0, 'critical': 3000.0},
            'error_rate': {'warning': 1.0, 'critical': 5.0},
            'task_duration_seconds': {'warning': 300.0, 'critical': 600.0},
        }
        
        self._load_data()
        self._initialized = True
    
    def _load_data(self):
        """Load existing data from files."""
        # Load metrics
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    self.metrics.append(PerformanceMetric(**data))
        
        # Load analyses
        if self.analyses_file.exists():
            with open(self.analyses_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    self.analyses.append(PerformanceAnalysis(**data))
        
        # Load opportunities
        if self.opportunities_file.exists():
            with open(self.opportunities_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    self.opportunities.append(OptimizationOpportunity(**data))
    
    def record_metric(
        self,
        category: str,
        metric_name: str,
        value: float,
        unit: str,
        context: Optional[Dict[str, Any]] = None
    ) -> PerformanceMetric:
        """Record a performance metric."""
        metric_id = f"metric_{len(self.metrics) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Get thresholds if available
        threshold_warning = None
        threshold_critical = None
        if metric_name in self.thresholds:
            threshold_warning = self.thresholds[metric_name]['warning']
            threshold_critical = self.thresholds[metric_name]['critical']
        
        metric = PerformanceMetric(
            metric_id=metric_id,
            timestamp=datetime.now().isoformat(),
            category=category,
            metric_name=metric_name,
            value=value,
            unit=unit,
            context=context or {},
            threshold_warning=threshold_warning,
            threshold_critical=threshold_critical
        )
        
        self.metrics.append(metric)
        
        # Save to file
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(asdict(metric)) + '\n')
        
        return metric
    
    def analyze_performance(
        self,
        category: str,
        metric_name: str,
        time_period: str = "last_day"
    ) -> PerformanceAnalysis:
        """Analyze performance for a specific metric over a time period."""
        # Get time range
        now = datetime.now()
        if time_period == "last_hour":
            start_time = now - timedelta(hours=1)
        elif time_period == "last_day":
            start_time = now - timedelta(days=1)
        elif time_period == "last_week":
            start_time = now - timedelta(weeks=1)
        elif time_period == "last_month":
            start_time = now - timedelta(days=30)
        else:
            start_time = now - timedelta(days=1)
        
        # Filter metrics
        relevant_metrics = [
            m for m in self.metrics
            if m.category == category
            and m.metric_name == metric_name
            and datetime.fromisoformat(m.timestamp) >= start_time
        ]
        
        if not relevant_metrics:
            # Return empty analysis
            return PerformanceAnalysis(
                analysis_id=f"analysis_{len(self.analyses) + 1}",
                timestamp=now.isoformat(),
                category=category,
                time_period=time_period,
                metrics_analyzed=0,
                avg_value=0.0,
                min_value=0.0,
                max_value=0.0,
                std_dev=0.0,
                median_value=0.0,
                trend="stable",
                trend_percentage=0.0,
                warnings=[],
                critical_issues=[],
                recommendations=[],
                priority_score=0.0
            )
        
        # Calculate statistics
        values = [m.value for m in relevant_metrics]
        avg_value = statistics.mean(values)
        min_value = min(values)
        max_value = max(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0.0
        median_value = statistics.median(values)
        
        # Trend analysis (compare first half vs second half)
        trend, trend_percentage = self._calculate_trend(values)
        
        # Identify issues
        warnings = []
        critical_issues = []
        
        for metric in relevant_metrics:
            if metric.is_critical():
                critical_issues.append({
                    'metric_id': metric.metric_id,
                    'timestamp': metric.timestamp,
                    'value': metric.value,
                    'threshold': metric.threshold_critical,
                    'context': metric.context
                })
            elif metric.is_warning():
                warnings.append({
                    'metric_id': metric.metric_id,
                    'timestamp': metric.timestamp,
                    'value': metric.value,
                    'threshold': metric.threshold_warning,
                    'context': metric.context
                })
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            category, metric_name, avg_value, trend, warnings, critical_issues
        )
        
        # Calculate priority score
        priority_score = self._calculate_priority_score(
            trend, len(warnings), len(critical_issues), avg_value, relevant_metrics[0]
        )
        
        analysis = PerformanceAnalysis(
            analysis_id=f"analysis_{len(self.analyses) + 1}_{now.strftime('%Y%m%d_%H%M%S')}",
            timestamp=now.isoformat(),
            category=category,
            time_period=time_period,
            metrics_analyzed=len(relevant_metrics),
            avg_value=avg_value,
            min_value=min_value,
            max_value=max_value,
            std_dev=std_dev,
            median_value=median_value,
            trend=trend,
            trend_percentage=trend_percentage,
            warnings=warnings,
            critical_issues=critical_issues,
            recommendations=recommendations,
            priority_score=priority_score
        )
        
        self.analyses.append(analysis)
        
        # Save to file
        with open(self.analyses_file, 'a') as f:
            f.write(json.dumps(asdict(analysis)) + '\n')
        
        return analysis
    
    def _calculate_trend(self, values: List[float]) -> Tuple[str, float]:
        """Calculate trend from values (improving, degrading, stable)."""
        if len(values) < 2:
            return "stable", 0.0
        
        # Split into two halves
        mid = len(values) // 2
        first_half = values[:mid]
        second_half = values[mid:]
        
        avg_first = statistics.mean(first_half)
        avg_second = statistics.mean(second_half)
        
        if avg_first == 0:
            return "stable", 0.0
        
        change_percentage = ((avg_second - avg_first) / avg_first) * 100
        
        # Determine trend (note: for some metrics, higher is worse)
        if abs(change_percentage) < 5:
            return "stable", change_percentage
        elif change_percentage > 0:
            return "degrading", change_percentage  # Assuming higher values are worse
        else:
            return "improving", change_percentage
    
    def _generate_recommendations(
        self,
        category: str,
        metric_name: str,
        avg_value: float,
        trend: str,
        warnings: List[Dict],
        critical_issues: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Critical issues
        if critical_issues:
            recommendations.append({
                'priority': 'critical',
                'title': f'Critical {metric_name} issues detected',
                'description': f'Found {len(critical_issues)} critical threshold breaches',
                'action': f'Immediate investigation required for {category}/{metric_name}',
                'impact': 'high'
            })
        
        # Warnings
        if warnings:
            recommendations.append({
                'priority': 'high',
                'title': f'{metric_name} approaching limits',
                'description': f'Found {len(warnings)} warning threshold breaches',
                'action': f'Monitor and optimize {category}/{metric_name}',
                'impact': 'medium'
            })
        
        # Degrading trend
        if trend == "degrading":
            recommendations.append({
                'priority': 'medium',
                'title': f'{metric_name} performance degrading',
                'description': f'Performance trend shows degradation over time',
                'action': f'Investigate root cause of {metric_name} degradation',
                'impact': 'medium'
            })
        
        # Specific metric recommendations
        if metric_name == "response_time_ms" and avg_value > 500:
            recommendations.append({
                'priority': 'medium',
                'title': 'Response time optimization needed',
                'description': f'Average response time is {avg_value:.0f}ms',
                'action': 'Consider caching, query optimization, or parallel processing',
                'impact': 'medium'
            })
        
        if metric_name == "error_rate" and avg_value > 0.5:
            recommendations.append({
                'priority': 'high',
                'title': 'Error rate too high',
                'description': f'Average error rate is {avg_value:.2f}%',
                'action': 'Review error logs and implement better error handling',
                'impact': 'high'
            })
        
        return recommendations
    
    def _calculate_priority_score(
        self,
        trend: str,
        warning_count: int,
        critical_count: int,
        avg_value: float,
        sample_metric: PerformanceMetric
    ) -> float:
        """Calculate priority score for analysis (0-100)."""
        score = 0.0
        
        # Critical issues have highest impact
        score += critical_count * 30
        
        # Warnings have medium impact
        score += warning_count * 15
        
        # Degrading trend adds to priority
        if trend == "degrading":
            score += 20
        elif trend == "stable":
            score += 5
        
        # Check if average exceeds thresholds
        if sample_metric.threshold_critical and avg_value >= sample_metric.threshold_critical:
            score += 25
        elif sample_metric.threshold_warning and avg_value >= sample_metric.threshold_warning:
            score += 10
        
        return min(score, 100.0)
    
    def identify_optimization_opportunity(
        self,
        category: str,
        title: str,
        description: str,
        current_performance: float,
        potential_performance: float,
        difficulty: str = "medium",
        estimated_effort_hours: float = 4.0,
        required_resources: Optional[List[str]] = None
    ) -> OptimizationOpportunity:
        """Identify and record an optimization opportunity."""
        opportunity_id = f"opt_{len(self.opportunities) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Calculate improvement
        if current_performance > 0:
            improvement_percentage = ((potential_performance - current_performance) / current_performance) * 100
        else:
            improvement_percentage = 0.0
        
        # Calculate ROI score (improvement / effort)
        roi_score = abs(improvement_percentage) / max(estimated_effort_hours, 0.5)
        
        # Calculate priority score
        priority_score = self._calculate_opportunity_priority(
            improvement_percentage, difficulty, estimated_effort_hours, roi_score
        )
        
        opportunity = OptimizationOpportunity(
            opportunity_id=opportunity_id,
            timestamp=datetime.now().isoformat(),
            category=category,
            title=title,
            description=description,
            current_performance=current_performance,
            potential_performance=potential_performance,
            improvement_percentage=improvement_percentage,
            difficulty=difficulty,
            estimated_effort_hours=estimated_effort_hours,
            required_resources=required_resources or [],
            priority_score=priority_score,
            roi_score=roi_score,
            status="identified",
            implementation_notes=""
        )
        
        self.opportunities.append(opportunity)
        
        # Save to file
        with open(self.opportunities_file, 'a') as f:
            f.write(json.dumps(asdict(opportunity)) + '\n')
        
        return opportunity
    
    def _calculate_opportunity_priority(
        self,
        improvement_percentage: float,
        difficulty: str,
        estimated_effort_hours: float,
        roi_score: float
    ) -> float:
        """Calculate priority score for optimization opportunity (0-100)."""
        score = 0.0
        
        # Impact (improvement percentage)
        score += min(abs(improvement_percentage), 50)
        
        # ROI score
        score += min(roi_score * 2, 30)
        
        # Difficulty (easier = higher priority)
        if difficulty == "easy":
            score += 15
        elif difficulty == "medium":
            score += 10
        else:  # hard
            score += 5
        
        # Effort (less effort = higher priority)
        if estimated_effort_hours <= 2:
            score += 5
        elif estimated_effort_hours <= 8:
            score += 3
        
        return min(score, 100.0)
    
    def get_performance_summary(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get summary of performance metrics."""
        metrics = self.metrics if category is None else [m for m in self.metrics if m.category == category]
        
        if not metrics:
            return {
                'total_metrics': 0,
                'categories': [],
                'recent_warnings': 0,
                'recent_critical': 0
            }
        
        # Get recent metrics (last 24 hours)
        now = datetime.now()
        recent_cutoff = now - timedelta(days=1)
        recent_metrics = [m for m in metrics if datetime.fromisoformat(m.timestamp) >= recent_cutoff]
        
        # Count warnings and critical
        recent_warnings = sum(1 for m in recent_metrics if m.is_warning() and not m.is_critical())
        recent_critical = sum(1 for m in recent_metrics if m.is_critical())
        
        # Get categories
        categories = list(set(m.category for m in metrics))
        
        # Get metric names by category
        metrics_by_category = defaultdict(set)
        for m in metrics:
            metrics_by_category[m.category].add(m.metric_name)
        
        return {
            'total_metrics': len(metrics),
            'recent_metrics_24h': len(recent_metrics),
            'categories': categories,
            'metrics_by_category': {k: list(v) for k, v in metrics_by_category.items()},
            'recent_warnings': recent_warnings,
            'recent_critical': recent_critical,
            'total_analyses': len(self.analyses),
            'total_opportunities': len(self.opportunities)
        }
    
    def get_top_opportunities(self, limit: int = 10) -> List[OptimizationOpportunity]:
        """Get top optimization opportunities by priority score."""
        # Filter to identified or planned opportunities
        active_opportunities = [
            o for o in self.opportunities
            if o.status in ['identified', 'planned']
        ]
        
        # Sort by priority score
        sorted_opportunities = sorted(
            active_opportunities,
            key=lambda o: o.priority_score,
            reverse=True
        )
        
        return sorted_opportunities[:limit]
    
    def update_opportunity_status(
        self,
        opportunity_id: str,
        status: str,
        implementation_notes: str = ""
    ) -> bool:
        """Update the status of an optimization opportunity."""
        for opportunity in self.opportunities:
            if opportunity.opportunity_id == opportunity_id:
                opportunity.status = status
                if implementation_notes:
                    opportunity.implementation_notes = implementation_notes
                
                # Rewrite opportunities file
                with open(self.opportunities_file, 'w') as f:
                    for opp in self.opportunities:
                        f.write(json.dumps(asdict(opp)) + '\n')
                
                return True
        
        return False
    
    def export_analysis_report(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Export comprehensive performance analysis report."""
        if output_file is None:
            output_file = self.data_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': self.get_performance_summary(),
            'recent_analyses': [asdict(a) for a in self.analyses[-20:]],
            'top_opportunities': [asdict(o) for o in self.get_top_opportunities(10)],
            'critical_issues': [
                asdict(a) for a in self.analyses
                if a.critical_issues and datetime.fromisoformat(a.timestamp) >= datetime.now() - timedelta(days=7)
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report

def get_analyzer() -> PerformanceAnalyzer:
    """Get the singleton PerformanceAnalyzer instance."""
    return PerformanceAnalyzer()

if __name__ == "__main__":
    # Test the performance analyzer
    analyzer = get_analyzer()
    
    print("🔍 Performance Analyzer Test")
    print("=" * 60)
    
    # Record some test metrics
    print("\n1. Recording test metrics...")
    analyzer.record_metric("system", "cpu_usage", 65.5, "percent", {"host": "localhost"})
    analyzer.record_metric("system", "cpu_usage", 72.3, "percent", {"host": "localhost"})
    analyzer.record_metric("system", "cpu_usage", 68.1, "percent", {"host": "localhost"})
    analyzer.record_metric("workflow", "response_time_ms", 450.0, "ms", {"workflow": "data_processing"})
    analyzer.record_metric("workflow", "response_time_ms", 1200.0, "ms", {"workflow": "data_processing"})
    
    # Analyze performance
    print("\n2. Analyzing CPU usage...")
    analysis = analyzer.analyze_performance("system", "cpu_usage", "last_day")
    print(f"   Average: {analysis.avg_value:.2f}%")
    print(f"   Trend: {analysis.trend} ({analysis.trend_percentage:+.2f}%)")
    print(f"   Warnings: {len(analysis.warnings)}")
    print(f"   Priority Score: {analysis.priority_score:.1f}")
    
    # Identify optimization opportunity
    print("\n3. Identifying optimization opportunity...")
    opportunity = analyzer.identify_optimization_opportunity(
        category="workflow",
        title="Optimize data processing pipeline",
        description="Add caching layer to reduce redundant computations",
        current_performance=1200.0,
        potential_performance=450.0,
        difficulty="medium",
        estimated_effort_hours=6.0,
        required_resources=["Redis", "Developer time"]
    )
    print(f"   Opportunity ID: {opportunity.opportunity_id}")
    print(f"   Improvement: {opportunity.improvement_percentage:.1f}%")
    print(f"   ROI Score: {opportunity.roi_score:.2f}")
    print(f"   Priority: {opportunity.priority_score:.1f}")
    
    # Get summary
    print("\n4. Performance Summary:")
    summary = analyzer.get_performance_summary()
    print(f"   Total Metrics: {summary['total_metrics']}")
    print(f"   Categories: {', '.join(summary['categories'])}")
    print(f"   Recent Warnings: {summary['recent_warnings']}")
    print(f"   Recent Critical: {summary['recent_critical']}")
    print(f"   Total Opportunities: {summary['total_opportunities']}")
    
    # Get top opportunities
    print("\n5. Top Optimization Opportunities:")
    top_opps = analyzer.get_top_opportunities(5)
    for i, opp in enumerate(top_opps, 1):
        print(f"   {i}. {opp.title} (Priority: {opp.priority_score:.1f}, ROI: {opp.roi_score:.2f})")
    
    print("\n✅ Performance Analyzer test complete!")
    print(f"📁 Data stored in: {analyzer.data_dir}")
