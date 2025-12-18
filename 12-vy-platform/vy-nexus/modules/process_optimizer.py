"""Process Optimization Engine

This module analyzes existing processes and workflows to identify optimization
opportunities based on performance data, bottlenecks, and efficiency metrics.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import statistics
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance metric for a process"""
    process_id: str
    metric_name: str
    value: float
    unit: str
    timestamp: str
    context: Dict[str, Any]


@dataclass
class Bottleneck:
    """Identified bottleneck in a process"""
    bottleneck_id: str
    process_id: str
    step_name: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    impact_score: float  # 0-100
    description: str
    metrics: Dict[str, float]
    identified_at: str


@dataclass
class OptimizationOpportunity:
    """Optimization opportunity for a process"""
    opportunity_id: str
    process_id: str
    opportunity_type: str
    title: str
    description: str
    estimated_improvement: float  # percentage
    estimated_time_savings: float  # seconds
    implementation_effort: str  # 'low', 'medium', 'high'
    priority_score: float  # 0-100
    suggested_actions: List[str]
    created_at: str


class PerformanceAnalyzer:
    """Analyzes performance metrics to identify issues"""
    
    def __init__(self, db_path: str = 'data/vy_nexus.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                process_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                timestamp TEXT NOT NULL,
                context TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_perf_process 
            ON performance_metrics(process_id, timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def record_metric(self, metric: PerformanceMetric):
        """Record a performance metric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance_metrics 
            (process_id, metric_name, value, unit, timestamp, context)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            metric.process_id,
            metric.metric_name,
            metric.value,
            metric.unit,
            metric.timestamp,
            json.dumps(metric.context)
        ))
        
        conn.commit()
        conn.close()
    
    def get_metrics(self, process_id: str, metric_name: Optional[str] = None,
                   days: int = 30) -> List[PerformanceMetric]:
        """Get performance metrics for a process"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        if metric_name:
            cursor.execute('''
                SELECT process_id, metric_name, value, unit, timestamp, context
                FROM performance_metrics
                WHERE process_id = ? AND metric_name = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            ''', (process_id, metric_name, cutoff))
        else:
            cursor.execute('''
                SELECT process_id, metric_name, value, unit, timestamp, context
                FROM performance_metrics
                WHERE process_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            ''', (process_id, cutoff))
        
        metrics = []
        for row in cursor.fetchall():
            metrics.append(PerformanceMetric(
                process_id=row[0],
                metric_name=row[1],
                value=row[2],
                unit=row[3],
                timestamp=row[4],
                context=json.loads(row[5]) if row[5] else {}
            ))
        
        conn.close()
        return metrics
    
    def analyze_performance_trends(self, process_id: str) -> Dict[str, Any]:
        """Analyze performance trends for a process"""
        metrics = self.get_metrics(process_id)
        
        if not metrics:
            return {'status': 'no_data', 'trends': {}}
        
        # Group by metric name
        metric_groups = {}
        for metric in metrics:
            if metric.metric_name not in metric_groups:
                metric_groups[metric.metric_name] = []
            metric_groups[metric.metric_name].append(metric.value)
        
        trends = {}
        for metric_name, values in metric_groups.items():
            if len(values) < 2:
                continue
            
            avg = statistics.mean(values)
            median = statistics.median(values)
            stdev = statistics.stdev(values) if len(values) > 1 else 0
            
            # Calculate trend (improving or degrading)
            recent = values[:len(values)//3] if len(values) >= 3 else values
            older = values[len(values)//3:] if len(values) >= 3 else values
            
            recent_avg = statistics.mean(recent)
            older_avg = statistics.mean(older)
            
            trend_direction = 'stable'
            if recent_avg < older_avg * 0.9:  # 10% improvement
                trend_direction = 'improving'
            elif recent_avg > older_avg * 1.1:  # 10% degradation
                trend_direction = 'degrading'
            
            trends[metric_name] = {
                'average': avg,
                'median': median,
                'std_dev': stdev,
                'trend': trend_direction,
                'recent_avg': recent_avg,
                'older_avg': older_avg,
                'sample_count': len(values)
            }
        
        return {'status': 'success', 'trends': trends}


class BottleneckDetector:
    """Detects bottlenecks in processes"""
    
    def __init__(self, db_path: str = 'data/vy_nexus.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bottlenecks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bottleneck_id TEXT UNIQUE NOT NULL,
                process_id TEXT NOT NULL,
                step_name TEXT NOT NULL,
                severity TEXT NOT NULL,
                impact_score REAL NOT NULL,
                description TEXT,
                metrics TEXT,
                identified_at TEXT NOT NULL,
                resolved BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def detect_bottlenecks(self, process_id: str, 
                          performance_analyzer: PerformanceAnalyzer) -> List[Bottleneck]:
        """Detect bottlenecks in a process"""
        trends = performance_analyzer.analyze_performance_trends(process_id)
        
        if trends['status'] != 'success':
            return []
        
        bottlenecks = []
        
        for metric_name, trend_data in trends['trends'].items():
            # Check for degrading performance
            if trend_data['trend'] == 'degrading':
                severity = self._calculate_severity(trend_data)
                impact_score = self._calculate_impact(trend_data)
                
                if impact_score > 30:  # Only report significant bottlenecks
                    bottleneck = Bottleneck(
                        bottleneck_id=f"btn_{process_id}_{metric_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        process_id=process_id,
                        step_name=metric_name,
                        severity=severity,
                        impact_score=impact_score,
                        description=f"Performance degradation detected in {metric_name}",
                        metrics={
                            'recent_avg': trend_data['recent_avg'],
                            'older_avg': trend_data['older_avg'],
                            'degradation_pct': ((trend_data['recent_avg'] - trend_data['older_avg']) / trend_data['older_avg']) * 100
                        },
                        identified_at=datetime.now().isoformat()
                    )
                    bottlenecks.append(bottleneck)
                    self._save_bottleneck(bottleneck)
            
            # Check for high variance (inconsistent performance)
            if trend_data['std_dev'] > trend_data['average'] * 0.5:
                severity = 'medium'
                impact_score = min(60, (trend_data['std_dev'] / trend_data['average']) * 100)
                
                bottleneck = Bottleneck(
                    bottleneck_id=f"btn_{process_id}_{metric_name}_variance_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    process_id=process_id,
                    step_name=metric_name,
                    severity=severity,
                    impact_score=impact_score,
                    description=f"High variance detected in {metric_name} - inconsistent performance",
                    metrics={
                        'average': trend_data['average'],
                        'std_dev': trend_data['std_dev'],
                        'variance_ratio': trend_data['std_dev'] / trend_data['average']
                    },
                    identified_at=datetime.now().isoformat()
                )
                bottlenecks.append(bottleneck)
                self._save_bottleneck(bottleneck)
        
        return bottlenecks
    
    def _calculate_severity(self, trend_data: Dict) -> str:
        """Calculate severity based on trend data"""
        degradation = ((trend_data['recent_avg'] - trend_data['older_avg']) / 
                      trend_data['older_avg']) * 100
        
        if degradation > 50:
            return 'critical'
        elif degradation > 30:
            return 'high'
        elif degradation > 15:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_impact(self, trend_data: Dict) -> float:
        """Calculate impact score (0-100)"""
        degradation = ((trend_data['recent_avg'] - trend_data['older_avg']) / 
                      trend_data['older_avg']) * 100
        return min(100, max(0, degradation))
    
    def _save_bottleneck(self, bottleneck: Bottleneck):
        """Save bottleneck to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO bottlenecks
                (bottleneck_id, process_id, step_name, severity, impact_score,
                 description, metrics, identified_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                bottleneck.bottleneck_id,
                bottleneck.process_id,
                bottleneck.step_name,
                bottleneck.severity,
                bottleneck.impact_score,
                bottleneck.description,
                json.dumps(bottleneck.metrics),
                bottleneck.identified_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving bottleneck: {e}")
        finally:
            conn.close()


class ProcessOptimizationEngine:
    """Main engine for process optimization"""
    
    def __init__(self, db_path: str = 'data/vy_nexus.db'):
        self.db_path = db_path
        self.performance_analyzer = PerformanceAnalyzer(db_path)
        self.bottleneck_detector = BottleneckDetector(db_path)
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opportunity_id TEXT UNIQUE NOT NULL,
                process_id TEXT NOT NULL,
                opportunity_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                estimated_improvement REAL,
                estimated_time_savings REAL,
                implementation_effort TEXT,
                priority_score REAL,
                suggested_actions TEXT,
                status TEXT DEFAULT 'identified',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_process(self, process_id: str) -> Dict[str, Any]:
        """Comprehensive process analysis"""
        # Get performance trends
        trends = self.performance_analyzer.analyze_performance_trends(process_id)
        
        # Detect bottlenecks
        bottlenecks = self.bottleneck_detector.detect_bottlenecks(
            process_id, self.performance_analyzer
        )
        
        # Generate optimization opportunities
        opportunities = self._generate_opportunities(process_id, trends, bottlenecks)
        
        return {
            'process_id': process_id,
            'analysis_timestamp': datetime.now().isoformat(),
            'performance_trends': trends,
            'bottlenecks': [asdict(b) for b in bottlenecks],
            'optimization_opportunities': [asdict(o) for o in opportunities],
            'summary': self._generate_summary(trends, bottlenecks, opportunities)
        }
    
    def _generate_opportunities(self, process_id: str, trends: Dict,
                               bottlenecks: List[Bottleneck]) -> List[OptimizationOpportunity]:
        """Generate optimization opportunities"""
        opportunities = []
        
        # Opportunities from bottlenecks
        for bottleneck in bottlenecks:
            opportunity = self._create_opportunity_from_bottleneck(bottleneck)
            opportunities.append(opportunity)
            self._save_opportunity(opportunity)
        
        # Opportunities from trends
        if trends['status'] == 'success':
            for metric_name, trend_data in trends['trends'].items():
                if trend_data['std_dev'] > trend_data['average'] * 0.3:
                    # High variance - opportunity for stabilization
                    opportunity = OptimizationOpportunity(
                        opportunity_id=f"opp_{process_id}_stabilize_{metric_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        process_id=process_id,
                        opportunity_type='stabilization',
                        title=f"Stabilize {metric_name} performance",
                        description=f"Reduce variance in {metric_name} to improve consistency",
                        estimated_improvement=20.0,
                        estimated_time_savings=trend_data['std_dev'] * 0.5,
                        implementation_effort='medium',
                        priority_score=50.0,
                        suggested_actions=[
                            f"Identify root causes of variance in {metric_name}",
                            "Implement caching or memoization",
                            "Add resource pooling",
                            "Optimize resource allocation"
                        ],
                        created_at=datetime.now().isoformat()
                    )
                    opportunities.append(opportunity)
                    self._save_opportunity(opportunity)
        
        return opportunities
    
    def _create_opportunity_from_bottleneck(self, bottleneck: Bottleneck) -> OptimizationOpportunity:
        """Create optimization opportunity from bottleneck"""
        # Calculate estimated improvement based on severity
        improvement_map = {
            'critical': 50.0,
            'high': 35.0,
            'medium': 20.0,
            'low': 10.0
        }
        
        effort_map = {
            'critical': 'high',
            'high': 'medium',
            'medium': 'medium',
            'low': 'low'
        }
        
        estimated_improvement = improvement_map.get(bottleneck.severity, 15.0)
        implementation_effort = effort_map.get(bottleneck.severity, 'medium')
        
        # Priority score based on impact and severity
        priority_score = bottleneck.impact_score
        
        suggested_actions = [
            f"Investigate {bottleneck.step_name} for performance issues",
            "Profile code execution to identify slow operations",
            "Consider parallel processing or async operations",
            "Optimize database queries or API calls",
            "Add caching layer if applicable"
        ]
        
        return OptimizationOpportunity(
            opportunity_id=f"opp_{bottleneck.bottleneck_id}",
            process_id=bottleneck.process_id,
            opportunity_type='bottleneck_resolution',
            title=f"Resolve {bottleneck.severity} bottleneck in {bottleneck.step_name}",
            description=bottleneck.description,
            estimated_improvement=estimated_improvement,
            estimated_time_savings=bottleneck.metrics.get('recent_avg', 0) * (estimated_improvement / 100),
            implementation_effort=implementation_effort,
            priority_score=priority_score,
            suggested_actions=suggested_actions,
            created_at=datetime.now().isoformat()
        )
    
    def _save_opportunity(self, opportunity: OptimizationOpportunity):
        """Save optimization opportunity to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO optimization_opportunities
                (opportunity_id, process_id, opportunity_type, title, description,
                 estimated_improvement, estimated_time_savings, implementation_effort,
                 priority_score, suggested_actions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                opportunity.opportunity_id,
                opportunity.process_id,
                opportunity.opportunity_type,
                opportunity.title,
                opportunity.description,
                opportunity.estimated_improvement,
                opportunity.estimated_time_savings,
                opportunity.implementation_effort,
                opportunity.priority_score,
                json.dumps(opportunity.suggested_actions)
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving opportunity: {e}")
        finally:
            conn.close()
    
    def _generate_summary(self, trends: Dict, bottlenecks: List[Bottleneck],
                         opportunities: List[OptimizationOpportunity]) -> Dict[str, Any]:
        """Generate analysis summary"""
        total_bottlenecks = len(bottlenecks)
        critical_bottlenecks = sum(1 for b in bottlenecks if b.severity == 'critical')
        high_bottlenecks = sum(1 for b in bottlenecks if b.severity == 'high')
        
        total_opportunities = len(opportunities)
        high_priority = sum(1 for o in opportunities if o.priority_score >= 70)
        
        total_time_savings = sum(o.estimated_time_savings for o in opportunities)
        
        return {
            'total_bottlenecks': total_bottlenecks,
            'critical_bottlenecks': critical_bottlenecks,
            'high_bottlenecks': high_bottlenecks,
            'total_opportunities': total_opportunities,
            'high_priority_opportunities': high_priority,
            'estimated_total_time_savings': total_time_savings,
            'health_status': 'critical' if critical_bottlenecks > 0 else 
                           'warning' if high_bottlenecks > 0 else 'healthy'
        }
    
    def get_top_opportunities(self, limit: int = 10) -> List[OptimizationOpportunity]:
        """Get top optimization opportunities by priority"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT opportunity_id, process_id, opportunity_type, title, description,
                   estimated_improvement, estimated_time_savings, implementation_effort,
                   priority_score, suggested_actions, created_at
            FROM optimization_opportunities
            WHERE status = 'identified'
            ORDER BY priority_score DESC
            LIMIT ?
        ''', (limit,))
        
        opportunities = []
        for row in cursor.fetchall():
            opportunities.append(OptimizationOpportunity(
                opportunity_id=row[0],
                process_id=row[1],
                opportunity_type=row[2],
                title=row[3],
                description=row[4],
                estimated_improvement=row[5],
                estimated_time_savings=row[6],
                implementation_effort=row[7],
                priority_score=row[8],
                suggested_actions=json.loads(row[9]),
                created_at=row[10]
            ))
        
        conn.close()
        return opportunities
