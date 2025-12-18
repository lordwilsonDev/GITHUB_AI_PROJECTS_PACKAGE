"""Shortcut and Efficiency Improvement System

This module identifies opportunities for shortcuts, optimizations, and efficiency
improvements in workflows and processes.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Shortcut:
    """Represents a shortcut or efficiency improvement"""
    shortcut_id: str
    shortcut_type: str  # 'keyboard', 'workflow', 'automation', 'caching', 'parallel'
    title: str
    description: str
    original_steps: List[str]
    optimized_steps: List[str]
    time_saved_per_use: float  # seconds
    complexity_reduction: float  # percentage
    implementation_code: Optional[str]
    prerequisites: List[str]
    created_at: str
    status: str  # 'identified', 'implemented', 'tested', 'deployed'


@dataclass
class EfficiencyMetric:
    """Metrics for measuring efficiency improvements"""
    metric_id: str
    process_id: str
    metric_type: str  # 'time', 'steps', 'errors', 'resources'
    before_value: float
    after_value: float
    improvement_percentage: float
    measured_at: str


@dataclass
class WorkflowOptimization:
    """Optimization suggestion for a workflow"""
    optimization_id: str
    workflow_id: str
    optimization_type: str
    title: str
    description: str
    current_approach: str
    suggested_approach: str
    estimated_improvement: float
    effort_required: str  # 'low', 'medium', 'high'
    priority: int  # 1-10
    created_at: str


class ShortcutIdentifier:
    """Identifies potential shortcuts and efficiency improvements"""
    
    def __init__(self, db_path: str = 'data/vy_nexus.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shortcuts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shortcut_id TEXT UNIQUE NOT NULL,
                shortcut_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                original_steps TEXT,
                optimized_steps TEXT,
                time_saved_per_use REAL,
                complexity_reduction REAL,
                implementation_code TEXT,
                prerequisites TEXT,
                status TEXT DEFAULT 'identified',
                created_at TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_shortcuts_type 
            ON shortcuts(shortcut_type, status)
        ''')
        
        conn.commit()
        conn.close()
    
    def identify_keyboard_shortcuts(self, workflow_steps: List[str]) -> List[Shortcut]:
        """Identify keyboard shortcut opportunities"""
        shortcuts = []
        
        # Common patterns that can be replaced with keyboard shortcuts
        patterns = {
            'click menu': {'shortcut': 'Cmd+Key', 'time_saved': 2.0},
            'right click': {'shortcut': 'Ctrl+Click or Cmd+Click', 'time_saved': 1.0},
            'copy and paste': {'shortcut': 'Cmd+C, Cmd+V', 'time_saved': 1.5},
            'save file': {'shortcut': 'Cmd+S', 'time_saved': 1.0},
            'find text': {'shortcut': 'Cmd+F', 'time_saved': 2.0},
            'switch window': {'shortcut': 'Cmd+Tab', 'time_saved': 1.5},
            'close window': {'shortcut': 'Cmd+W', 'time_saved': 0.5},
        }
        
        for i, step in enumerate(workflow_steps):
            step_lower = step.lower()
            for pattern, info in patterns.items():
                if pattern in step_lower:
                    shortcut = Shortcut(
                        shortcut_id=f"kbd_{i}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        shortcut_type='keyboard',
                        title=f"Use keyboard shortcut for: {pattern}",
                        description=f"Replace '{step}' with {info['shortcut']}",
                        original_steps=[step],
                        optimized_steps=[f"Press {info['shortcut']}"],
                        time_saved_per_use=info['time_saved'],
                        complexity_reduction=30.0,
                        implementation_code=None,
                        prerequisites=[],
                        created_at=datetime.now().isoformat(),
                        status='identified'
                    )
                    shortcuts.append(shortcut)
                    self._save_shortcut(shortcut)
        
        return shortcuts
    
    def identify_workflow_shortcuts(self, workflow_steps: List[str]) -> List[Shortcut]:
        """Identify workflow optimization opportunities"""
        shortcuts = []
        
        # Look for repetitive sequences
        if len(workflow_steps) >= 3:
            # Check for repeated patterns
            for window_size in range(2, min(5, len(workflow_steps))):
                for i in range(len(workflow_steps) - window_size):
                    pattern = workflow_steps[i:i+window_size]
                    # Count occurrences
                    count = 0
                    for j in range(len(workflow_steps) - window_size + 1):
                        if workflow_steps[j:j+window_size] == pattern:
                            count += 1
                    
                    if count >= 2:  # Pattern repeats
                        shortcut = Shortcut(
                            shortcut_id=f"wf_{i}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                            shortcut_type='workflow',
                            title=f"Create macro for repeated {window_size}-step sequence",
                            description=f"Pattern repeats {count} times in workflow",
                            original_steps=pattern * count,
                            optimized_steps=[f"Execute macro '{pattern[0][:20]}...' {count} times"],
                            time_saved_per_use=len(pattern) * count * 0.5,
                            complexity_reduction=50.0,
                            implementation_code=f"# Macro: {json.dumps(pattern)}",
                            prerequisites=['Macro system'],
                            created_at=datetime.now().isoformat(),
                            status='identified'
                        )
                        shortcuts.append(shortcut)
                        self._save_shortcut(shortcut)
                        break  # Only report once per pattern
        
        return shortcuts
    
    def identify_automation_opportunities(self, task_history: List[Dict]) -> List[Shortcut]:
        """Identify tasks that can be automated"""
        shortcuts = []
        
        # Group tasks by similarity
        task_groups = defaultdict(list)
        for task in task_history:
            task_type = task.get('type', 'unknown')
            task_groups[task_type].append(task)
        
        # Look for frequently repeated tasks
        for task_type, tasks in task_groups.items():
            if len(tasks) >= 3:  # Repeated at least 3 times
                avg_duration = sum(t.get('duration', 0) for t in tasks) / len(tasks)
                
                shortcut = Shortcut(
                    shortcut_id=f"auto_{task_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    shortcut_type='automation',
                    title=f"Automate {task_type} task",
                    description=f"Task performed {len(tasks)} times, avg duration {avg_duration:.1f}s",
                    original_steps=[f"Manually perform {task_type}"],
                    optimized_steps=[f"Run automated {task_type} script"],
                    time_saved_per_use=avg_duration * 0.8,  # 80% time savings
                    complexity_reduction=70.0,
                    implementation_code=f"# Automation for {task_type}",
                    prerequisites=['Automation framework'],
                    created_at=datetime.now().isoformat(),
                    status='identified'
                )
                shortcuts.append(shortcut)
                self._save_shortcut(shortcut)
        
        return shortcuts
    
    def identify_caching_opportunities(self, data_access_patterns: List[Dict]) -> List[Shortcut]:
        """Identify opportunities for caching"""
        shortcuts = []
        
        # Track frequently accessed data
        access_counts = defaultdict(int)
        for access in data_access_patterns:
            data_id = access.get('data_id')
            access_counts[data_id] += 1
        
        # Identify hot data
        for data_id, count in access_counts.items():
            if count >= 5:  # Accessed 5+ times
                shortcut = Shortcut(
                    shortcut_id=f"cache_{data_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    shortcut_type='caching',
                    title=f"Cache frequently accessed data: {data_id}",
                    description=f"Data accessed {count} times",
                    original_steps=[f"Fetch {data_id} from source each time"],
                    optimized_steps=[f"Cache {data_id} in memory/disk"],
                    time_saved_per_use=0.5,  # Assume 0.5s per cache hit
                    complexity_reduction=20.0,
                    implementation_code=f"# Cache implementation for {data_id}",
                    prerequisites=['Caching system'],
                    created_at=datetime.now().isoformat(),
                    status='identified'
                )
                shortcuts.append(shortcut)
                self._save_shortcut(shortcut)
        
        return shortcuts
    
    def identify_parallelization_opportunities(self, workflow_steps: List[Dict]) -> List[Shortcut]:
        """Identify steps that can be parallelized"""
        shortcuts = []
        
        # Look for independent steps that can run in parallel
        independent_groups = []
        current_group = []
        
        for i, step in enumerate(workflow_steps):
            dependencies = step.get('dependencies', [])
            
            # If step has no dependencies on current group, add to group
            if not any(dep in [s.get('id') for s in current_group] for dep in dependencies):
                current_group.append(step)
            else:
                # Start new group
                if len(current_group) >= 2:
                    independent_groups.append(current_group)
                current_group = [step]
        
        if len(current_group) >= 2:
            independent_groups.append(current_group)
        
        # Create shortcuts for parallelizable groups
        for i, group in enumerate(independent_groups):
            if len(group) >= 2:
                total_time = sum(s.get('duration', 1.0) for s in group)
                max_time = max(s.get('duration', 1.0) for s in group)
                time_saved = total_time - max_time
                
                shortcut = Shortcut(
                    shortcut_id=f"parallel_{i}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    shortcut_type='parallel',
                    title=f"Parallelize {len(group)} independent steps",
                    description=f"Steps can run concurrently, saving {time_saved:.1f}s",
                    original_steps=[s.get('name', f'Step {i}') for s in group],
                    optimized_steps=[f"Run {len(group)} steps in parallel"],
                    time_saved_per_use=time_saved,
                    complexity_reduction=40.0,
                    implementation_code=f"# Parallel execution for group {i}",
                    prerequisites=['Async/parallel execution framework'],
                    created_at=datetime.now().isoformat(),
                    status='identified'
                )
                shortcuts.append(shortcut)
                self._save_shortcut(shortcut)
        
        return shortcuts
    
    def _save_shortcut(self, shortcut: Shortcut):
        """Save shortcut to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO shortcuts
                (shortcut_id, shortcut_type, title, description, original_steps,
                 optimized_steps, time_saved_per_use, complexity_reduction,
                 implementation_code, prerequisites, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                shortcut.shortcut_id,
                shortcut.shortcut_type,
                shortcut.title,
                shortcut.description,
                json.dumps(shortcut.original_steps),
                json.dumps(shortcut.optimized_steps),
                shortcut.time_saved_per_use,
                shortcut.complexity_reduction,
                shortcut.implementation_code,
                json.dumps(shortcut.prerequisites),
                shortcut.status,
                shortcut.created_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving shortcut: {e}")
        finally:
            conn.close()
    
    def get_shortcuts(self, shortcut_type: Optional[str] = None,
                     status: Optional[str] = None) -> List[Shortcut]:
        """Retrieve shortcuts from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT shortcut_id, shortcut_type, title, description, original_steps,
                   optimized_steps, time_saved_per_use, complexity_reduction,
                   implementation_code, prerequisites, status, created_at
            FROM shortcuts
            WHERE 1=1
        '''
        params = []
        
        if shortcut_type:
            query += ' AND shortcut_type = ?'
            params.append(shortcut_type)
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        query += ' ORDER BY time_saved_per_use DESC'
        
        cursor.execute(query, params)
        
        shortcuts = []
        for row in cursor.fetchall():
            shortcuts.append(Shortcut(
                shortcut_id=row[0],
                shortcut_type=row[1],
                title=row[2],
                description=row[3],
                original_steps=json.loads(row[4]),
                optimized_steps=json.loads(row[5]),
                time_saved_per_use=row[6],
                complexity_reduction=row[7],
                implementation_code=row[8],
                prerequisites=json.loads(row[9]),
                status=row[10],
                created_at=row[11]
            ))
        
        conn.close()
        return shortcuts


class EfficiencyAnalyzer:
    """Analyzes efficiency improvements and their impact"""
    
    def __init__(self, db_path: str = 'data/vy_nexus.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS efficiency_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_id TEXT UNIQUE NOT NULL,
                process_id TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                before_value REAL NOT NULL,
                after_value REAL NOT NULL,
                improvement_percentage REAL NOT NULL,
                measured_at TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def measure_improvement(self, process_id: str, metric_type: str,
                           before_value: float, after_value: float) -> EfficiencyMetric:
        """Measure efficiency improvement"""
        improvement_pct = ((before_value - after_value) / before_value) * 100 if before_value > 0 else 0
        
        metric = EfficiencyMetric(
            metric_id=f"metric_{process_id}_{metric_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            process_id=process_id,
            metric_type=metric_type,
            before_value=before_value,
            after_value=after_value,
            improvement_percentage=improvement_pct,
            measured_at=datetime.now().isoformat()
        )
        
        self._save_metric(metric)
        return metric
    
    def _save_metric(self, metric: EfficiencyMetric):
        """Save efficiency metric to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO efficiency_metrics
                (metric_id, process_id, metric_type, before_value, after_value,
                 improvement_percentage, measured_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                metric.metric_id,
                metric.process_id,
                metric.metric_type,
                metric.before_value,
                metric.after_value,
                metric.improvement_percentage,
                metric.measured_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving metric: {e}")
        finally:
            conn.close()
    
    def get_improvement_summary(self, process_id: Optional[str] = None) -> Dict[str, Any]:
        """Get summary of efficiency improvements"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if process_id:
            cursor.execute('''
                SELECT metric_type, AVG(improvement_percentage), COUNT(*)
                FROM efficiency_metrics
                WHERE process_id = ?
                GROUP BY metric_type
            ''', (process_id,))
        else:
            cursor.execute('''
                SELECT metric_type, AVG(improvement_percentage), COUNT(*)
                FROM efficiency_metrics
                GROUP BY metric_type
            ''')
        
        summary = {}
        for row in cursor.fetchall():
            summary[row[0]] = {
                'avg_improvement': row[1],
                'measurement_count': row[2]
            }
        
        conn.close()
        return summary


class EfficiencyImprovementEngine:
    """Main engine for efficiency improvements"""
    
    def __init__(self, db_path: str = 'data/vy_nexus.db'):
        self.db_path = db_path
        self.shortcut_identifier = ShortcutIdentifier(db_path)
        self.efficiency_analyzer = EfficiencyAnalyzer(db_path)
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_optimizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                optimization_id TEXT UNIQUE NOT NULL,
                workflow_id TEXT NOT NULL,
                optimization_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                current_approach TEXT,
                suggested_approach TEXT,
                estimated_improvement REAL,
                effort_required TEXT,
                priority INTEGER,
                status TEXT DEFAULT 'suggested',
                created_at TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_workflow(self, workflow_id: str, workflow_steps: List[str],
                        task_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Comprehensive workflow analysis for efficiency improvements"""
        
        # Identify various types of shortcuts
        keyboard_shortcuts = self.shortcut_identifier.identify_keyboard_shortcuts(workflow_steps)
        workflow_shortcuts = self.shortcut_identifier.identify_workflow_shortcuts(workflow_steps)
        
        automation_shortcuts = []
        if task_history:
            automation_shortcuts = self.shortcut_identifier.identify_automation_opportunities(task_history)
        
        all_shortcuts = keyboard_shortcuts + workflow_shortcuts + automation_shortcuts
        
        # Calculate total potential savings
        total_time_saved = sum(s.time_saved_per_use for s in all_shortcuts)
        avg_complexity_reduction = (sum(s.complexity_reduction for s in all_shortcuts) / 
                                    len(all_shortcuts)) if all_shortcuts else 0
        
        return {
            'workflow_id': workflow_id,
            'analysis_timestamp': datetime.now().isoformat(),
            'shortcuts_identified': len(all_shortcuts),
            'shortcuts_by_type': {
                'keyboard': len(keyboard_shortcuts),
                'workflow': len(workflow_shortcuts),
                'automation': len(automation_shortcuts)
            },
            'total_time_saved_per_execution': total_time_saved,
            'avg_complexity_reduction': avg_complexity_reduction,
            'shortcuts': [asdict(s) for s in all_shortcuts],
            'recommendations': self._generate_recommendations(all_shortcuts)
        }
    
    def _generate_recommendations(self, shortcuts: List[Shortcut]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Prioritize by time savings
        high_impact = [s for s in shortcuts if s.time_saved_per_use > 2.0]
        if high_impact:
            recommendations.append(
                f"Implement {len(high_impact)} high-impact shortcuts that save >2s each"
            )
        
        # Group by type
        by_type = defaultdict(list)
        for s in shortcuts:
            by_type[s.shortcut_type].append(s)
        
        for stype, slist in by_type.items():
            total_savings = sum(s.time_saved_per_use for s in slist)
            recommendations.append(
                f"Focus on {stype} optimizations: {len(slist)} opportunities, {total_savings:.1f}s total savings"
            )
        
        return recommendations
    
    def get_top_shortcuts(self, limit: int = 10) -> List[Shortcut]:
        """Get top shortcuts by time savings"""
        return self.shortcut_identifier.get_shortcuts()[:limit]
