"""Shortcut and Efficiency System

This module designs and manages shortcuts, efficiency improvements, and workflow
optimizations to reduce manual effort and increase productivity.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict, field
import hashlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Shortcut:
    """Represents a shortcut or efficiency improvement"""
    shortcut_id: str
    name: str
    description: str
    shortcut_type: str  # 'keyboard', 'command', 'automation', 'workflow', 'template'
    trigger: str  # What activates this shortcut
    action: str  # What the shortcut does
    context: List[str]  # Where this shortcut applies
    time_saved_seconds: float
    usage_count: int = 0
    success_rate: float = 100.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_used: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EfficiencyPattern:
    """Represents an identified efficiency pattern"""
    pattern_id: str
    pattern_type: str  # 'repetitive_action', 'manual_process', 'slow_workflow'
    description: str
    frequency: int  # How often this pattern occurs
    time_cost_seconds: float  # Time cost per occurrence
    total_time_cost: float  # Total time cost
    suggested_shortcuts: List[str]  # Shortcut IDs that could help
    priority_score: float  # 0-100
    identified_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class WorkflowOptimization:
    """Represents a workflow optimization opportunity"""
    optimization_id: str
    workflow_name: str
    current_steps: List[str]
    optimized_steps: List[str]
    steps_removed: int
    time_saved_per_execution: float
    estimated_annual_savings: float
    implementation_complexity: str  # 'low', 'medium', 'high'
    status: str  # 'proposed', 'approved', 'implemented', 'rejected'
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class ShortcutManager:
    """Manages shortcuts and efficiency improvements"""
    
    def __init__(self, db_path: str = 'data/vy_nexus.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shortcuts (
                shortcut_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                shortcut_type TEXT NOT NULL,
                trigger TEXT NOT NULL,
                action TEXT NOT NULL,
                context TEXT,
                time_saved_seconds REAL,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 100.0,
                created_at TEXT NOT NULL,
                last_used TEXT,
                metadata TEXT,
                UNIQUE(trigger, context)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS efficiency_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                description TEXT,
                frequency INTEGER,
                time_cost_seconds REAL,
                total_time_cost REAL,
                suggested_shortcuts TEXT,
                priority_score REAL,
                identified_at TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_optimizations (
                optimization_id TEXT PRIMARY KEY,
                workflow_name TEXT NOT NULL,
                current_steps TEXT,
                optimized_steps TEXT,
                steps_removed INTEGER,
                time_saved_per_execution REAL,
                estimated_annual_savings REAL,
                implementation_complexity TEXT,
                status TEXT DEFAULT 'proposed',
                created_at TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shortcut_usage_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shortcut_id TEXT NOT NULL,
                used_at TEXT NOT NULL,
                success BOOLEAN,
                time_saved REAL,
                context TEXT,
                FOREIGN KEY (shortcut_id) REFERENCES shortcuts(shortcut_id)
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_shortcuts_type 
            ON shortcuts(shortcut_type)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_patterns_priority 
            ON efficiency_patterns(priority_score DESC)
        ''')
        
        conn.commit()
        conn.close()
    
    def create_shortcut(self, shortcut: Shortcut) -> bool:
        """Create a new shortcut"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO shortcuts (
                    shortcut_id, name, description, shortcut_type, trigger, action,
                    context, time_saved_seconds, usage_count, success_rate,
                    created_at, last_used, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                shortcut.shortcut_id,
                shortcut.name,
                shortcut.description,
                shortcut.shortcut_type,
                shortcut.trigger,
                shortcut.action,
                json.dumps(shortcut.context),
                shortcut.time_saved_seconds,
                shortcut.usage_count,
                shortcut.success_rate,
                shortcut.created_at,
                shortcut.last_used,
                json.dumps(shortcut.metadata)
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Created shortcut: {shortcut.name}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Shortcut already exists: {shortcut.trigger}")
            return False
        except Exception as e:
            logger.error(f"Error creating shortcut: {e}")
            return False
    
    def log_shortcut_usage(self, shortcut_id: str, success: bool = True,
                          time_saved: Optional[float] = None,
                          context: Optional[Dict] = None) -> None:
        """Log usage of a shortcut"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Log the usage
        cursor.execute('''
            INSERT INTO shortcut_usage_log (shortcut_id, used_at, success, time_saved, context)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            shortcut_id,
            datetime.now().isoformat(),
            success,
            time_saved,
            json.dumps(context) if context else None
        ))
        
        # Update shortcut statistics
        cursor.execute('''
            UPDATE shortcuts
            SET usage_count = usage_count + 1,
                last_used = ?
            WHERE shortcut_id = ?
        ''', (datetime.now().isoformat(), shortcut_id))
        
        # Recalculate success rate
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful
            FROM shortcut_usage_log
            WHERE shortcut_id = ?
        ''', (shortcut_id,))
        
        row = cursor.fetchone()
        if row and row[0] > 0:
            success_rate = (row[1] / row[0]) * 100
            cursor.execute('''
                UPDATE shortcuts
                SET success_rate = ?
                WHERE shortcut_id = ?
            ''', (success_rate, shortcut_id))
        
        conn.commit()
        conn.close()
    
    def get_shortcuts_by_context(self, context: str) -> List[Shortcut]:
        """Get all shortcuts applicable to a context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT shortcut_id, name, description, shortcut_type, trigger, action,
                   context, time_saved_seconds, usage_count, success_rate,
                   created_at, last_used, metadata
            FROM shortcuts
            WHERE context LIKE ?
            ORDER BY usage_count DESC, success_rate DESC
        ''', (f'%{context}%',))
        
        shortcuts = []
        for row in cursor.fetchall():
            shortcuts.append(Shortcut(
                shortcut_id=row[0],
                name=row[1],
                description=row[2],
                shortcut_type=row[3],
                trigger=row[4],
                action=row[5],
                context=json.loads(row[6]),
                time_saved_seconds=row[7],
                usage_count=row[8],
                success_rate=row[9],
                created_at=row[10],
                last_used=row[11],
                metadata=json.loads(row[12]) if row[12] else {}
            ))
        
        conn.close()
        return shortcuts
    
    def get_most_valuable_shortcuts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get shortcuts with highest value (usage * time saved)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                shortcut_id,
                name,
                description,
                shortcut_type,
                usage_count,
                time_saved_seconds,
                (usage_count * time_saved_seconds) as total_time_saved,
                success_rate
            FROM shortcuts
            WHERE usage_count > 0
            ORDER BY total_time_saved DESC
            LIMIT ?
        ''', (limit,))
        
        shortcuts = []
        for row in cursor.fetchall():
            shortcuts.append({
                'shortcut_id': row[0],
                'name': row[1],
                'description': row[2],
                'type': row[3],
                'usage_count': row[4],
                'time_saved_per_use': row[5],
                'total_time_saved': row[6],
                'success_rate': row[7]
            })
        
        conn.close()
        return shortcuts


class EfficiencyAnalyzer:
    """Analyzes workflows to identify efficiency opportunities"""
    
    def __init__(self, db_path: str = 'data/vy_nexus.db'):
        self.db_path = db_path
        self.shortcut_manager = ShortcutManager(db_path)
    
    def identify_efficiency_patterns(self, workflow_data: List[Dict[str, Any]]) -> List[EfficiencyPattern]:
        """Identify efficiency patterns from workflow data"""
        patterns = []
        
        # Analyze for repetitive actions
        action_frequency = {}
        for entry in workflow_data:
            action = entry.get('action', '')
            if action:
                if action not in action_frequency:
                    action_frequency[action] = {
                        'count': 0,
                        'total_time': 0,
                        'contexts': set()
                    }
                action_frequency[action]['count'] += 1
                action_frequency[action]['total_time'] += entry.get('duration', 0)
                action_frequency[action]['contexts'].add(entry.get('context', 'general'))
        
        # Create patterns for high-frequency actions
        for action, data in action_frequency.items():
            if data['count'] >= 5:  # Threshold for pattern
                avg_time = data['total_time'] / data['count']
                priority = self._calculate_pattern_priority(
                    data['count'],
                    avg_time,
                    data['total_time']
                )
                
                pattern_id = hashlib.md5(
                    f"repetitive_{action}".encode()
                ).hexdigest()[:16]
                
                pattern = EfficiencyPattern(
                    pattern_id=pattern_id,
                    pattern_type='repetitive_action',
                    description=f"Repetitive action: {action}",
                    frequency=data['count'],
                    time_cost_seconds=avg_time,
                    total_time_cost=data['total_time'],
                    suggested_shortcuts=self._suggest_shortcuts_for_action(action),
                    priority_score=priority
                )
                patterns.append(pattern)
        
        return patterns
    
    def _calculate_pattern_priority(self, frequency: int, avg_time: float,
                                   total_time: float) -> float:
        """Calculate priority score for an efficiency pattern"""
        # Factors: frequency (40%), time per occurrence (30%), total time (30%)
        freq_score = min(frequency / 100, 1.0) * 40
        time_score = min(avg_time / 60, 1.0) * 30  # Normalize to 1 minute
        total_score = min(total_time / 3600, 1.0) * 30  # Normalize to 1 hour
        
        return freq_score + time_score + total_score
    
    def _suggest_shortcuts_for_action(self, action: str) -> List[str]:
        """Suggest shortcuts that could help with an action"""
        # This would integrate with the shortcut database
        # For now, return empty list
        return []
    
    def analyze_workflow_for_optimization(self, workflow_name: str,
                                         steps: List[str]) -> Optional[WorkflowOptimization]:
        """Analyze a workflow and suggest optimizations"""
        optimized_steps = []
        steps_removed = 0
        time_saved = 0
        
        # Identify redundant steps
        seen_steps = set()
        for step in steps:
            if step not in seen_steps:
                optimized_steps.append(step)
                seen_steps.add(step)
            else:
                steps_removed += 1
                time_saved += 30  # Assume 30 seconds per redundant step
        
        # Identify steps that can be combined
        combined_steps = self._combine_similar_steps(optimized_steps)
        if len(combined_steps) < len(optimized_steps):
            steps_removed += len(optimized_steps) - len(combined_steps)
            time_saved += (len(optimized_steps) - len(combined_steps)) * 20
            optimized_steps = combined_steps
        
        if steps_removed > 0:
            optimization_id = hashlib.md5(
                f"{workflow_name}_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:16]
            
            # Estimate annual savings (assume workflow runs 250 times/year)
            annual_savings = time_saved * 250
            
            complexity = 'low' if steps_removed <= 2 else 'medium' if steps_removed <= 5 else 'high'
            
            return WorkflowOptimization(
                optimization_id=optimization_id,
                workflow_name=workflow_name,
                current_steps=steps,
                optimized_steps=optimized_steps,
                steps_removed=steps_removed,
                time_saved_per_execution=time_saved,
                estimated_annual_savings=annual_savings,
                implementation_complexity=complexity,
                status='proposed'
            )
        
        return None
    
    def _combine_similar_steps(self, steps: List[str]) -> List[str]:
        """Combine similar steps that can be done together"""
        # Simple implementation - could be enhanced with NLP
        combined = []
        skip_next = False
        
        for i, step in enumerate(steps):
            if skip_next:
                skip_next = False
                continue
            
            if i < len(steps) - 1:
                next_step = steps[i + 1]
                # Check if steps are similar (simple keyword matching)
                if self._are_steps_similar(step, next_step):
                    combined.append(f"{step} + {next_step}")
                    skip_next = True
                    continue
            
            combined.append(step)
        
        return combined
    
    def _are_steps_similar(self, step1: str, step2: str) -> bool:
        """Check if two steps are similar enough to combine"""
        # Simple keyword-based similarity
        keywords1 = set(step1.lower().split())
        keywords2 = set(step2.lower().split())
        
        overlap = len(keywords1 & keywords2)
        total = len(keywords1 | keywords2)
        
        return (overlap / total) > 0.5 if total > 0 else False
    
    def generate_efficiency_report(self) -> Dict[str, Any]:
        """Generate comprehensive efficiency report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get total shortcuts
        cursor.execute('SELECT COUNT(*) FROM shortcuts')
        total_shortcuts = cursor.fetchone()[0]
        
        # Get total time saved
        cursor.execute('''
            SELECT SUM(usage_count * time_saved_seconds)
            FROM shortcuts
        ''')
        total_time_saved = cursor.fetchone()[0] or 0
        
        # Get most used shortcuts
        cursor.execute('''
            SELECT name, usage_count, time_saved_seconds
            FROM shortcuts
            ORDER BY usage_count DESC
            LIMIT 5
        ''')
        top_shortcuts = [{
            'name': row[0],
            'usage_count': row[1],
            'time_saved': row[2]
        } for row in cursor.fetchall()]
        
        # Get efficiency patterns
        cursor.execute('''
            SELECT COUNT(*), AVG(priority_score)
            FROM efficiency_patterns
        ''')
        pattern_stats = cursor.fetchone()
        
        # Get workflow optimizations
        cursor.execute('''
            SELECT status, COUNT(*), SUM(estimated_annual_savings)
            FROM workflow_optimizations
            GROUP BY status
        ''')
        optimization_stats = {}
        for row in cursor.fetchall():
            optimization_stats[row[0]] = {
                'count': row[1],
                'annual_savings': row[2] or 0
            }
        
        conn.close()
        
        return {
            'total_shortcuts': total_shortcuts,
            'total_time_saved_seconds': total_time_saved,
            'total_time_saved_hours': total_time_saved / 3600,
            'top_shortcuts': top_shortcuts,
            'efficiency_patterns': {
                'total': pattern_stats[0],
                'avg_priority': pattern_stats[1] or 0
            },
            'workflow_optimizations': optimization_stats,
            'generated_at': datetime.now().isoformat()
        }


class ShortcutRecommender:
    """Recommends shortcuts based on user behavior"""
    
    def __init__(self, db_path: str = 'data/vy_nexus.db'):
        self.db_path = db_path
    
    def recommend_shortcuts(self, current_context: str,
                          user_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Recommend shortcuts based on context and history"""
        recommendations = []
        
        # Analyze user history for patterns
        action_patterns = self._analyze_action_patterns(user_history)
        
        # Get existing shortcuts for this context
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT shortcut_id, name, description, trigger, time_saved_seconds,
                   usage_count, success_rate
            FROM shortcuts
            WHERE context LIKE ?
            ORDER BY (usage_count * time_saved_seconds * success_rate / 100) DESC
            LIMIT 10
        ''', (f'%{current_context}%',))
        
        for row in cursor.fetchall():
            # Calculate relevance score
            relevance = self._calculate_relevance(
                row[0],  # shortcut_id
                action_patterns,
                row[5],  # usage_count
                row[6]   # success_rate
            )
            
            if relevance > 0.3:  # Threshold for recommendation
                recommendations.append({
                    'shortcut_id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'trigger': row[3],
                    'time_saved': row[4],
                    'usage_count': row[5],
                    'success_rate': row[6],
                    'relevance_score': relevance
                })
        
        conn.close()
        
        # Sort by relevance
        recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return recommendations
    
    def _analyze_action_patterns(self, history: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze action patterns from user history"""
        patterns = {}
        for entry in history:
            action = entry.get('action', '')
            if action:
                patterns[action] = patterns.get(action, 0) + 1
        return patterns
    
    def _calculate_relevance(self, shortcut_id: str, action_patterns: Dict[str, int],
                           usage_count: int, success_rate: float) -> float:
        """Calculate relevance score for a shortcut"""
        # Base score from usage and success
        base_score = (usage_count / 100) * 0.4 + (success_rate / 100) * 0.3
        
        # Pattern matching score
        pattern_score = 0.3  # Default if no patterns match
        
        # Normalize to 0-1
        return min(base_score + pattern_score, 1.0)


if __name__ == '__main__':
    # Test the system
    print("Testing Shortcut and Efficiency System...\n")
    
    # Initialize managers
    shortcut_mgr = ShortcutManager()
    efficiency_analyzer = EfficiencyAnalyzer()
    recommender = ShortcutRecommender()
    
    # Create sample shortcuts
    shortcuts = [
        Shortcut(
            shortcut_id='sc_001',
            name='Quick File Search',
            description='Search files using Spotlight',
            shortcut_type='keyboard',
            trigger='cmd+space',
            action='Open Spotlight search',
            context=['file_management', 'general'],
            time_saved_seconds=15
        ),
        Shortcut(
            shortcut_id='sc_002',
            name='Terminal Quick Open',
            description='Open terminal in current directory',
            shortcut_type='command',
            trigger='open_terminal_here',
            action='Open terminal at current path',
            context=['development', 'file_management'],
            time_saved_seconds=10
        ),
        Shortcut(
            shortcut_id='sc_003',
            name='Auto-format Code',
            description='Format code with standard style',
            shortcut_type='automation',
            trigger='format_code',
            action='Run code formatter',
            context=['development', 'coding'],
            time_saved_seconds=30
        )
    ]
    
    for shortcut in shortcuts:
        shortcut_mgr.create_shortcut(shortcut)
    
    print("✅ Created sample shortcuts")
    
    # Log some usage
    shortcut_mgr.log_shortcut_usage('sc_001', success=True, time_saved=15)
    shortcut_mgr.log_shortcut_usage('sc_001', success=True, time_saved=12)
    shortcut_mgr.log_shortcut_usage('sc_002', success=True, time_saved=10)
    shortcut_mgr.log_shortcut_usage('sc_003', success=True, time_saved=28)
    shortcut_mgr.log_shortcut_usage('sc_003', success=True, time_saved=32)
    
    print("✅ Logged shortcut usage\n")
    
    # Get most valuable shortcuts
    valuable = shortcut_mgr.get_most_valuable_shortcuts(limit=5)
    print("📊 Most Valuable Shortcuts:")
    for sc in valuable:
        print(f"  - {sc['name']}: {sc['total_time_saved']:.1f}s saved (used {sc['usage_count']} times)")
    
    # Analyze workflow
    print("\n🔍 Analyzing Sample Workflow...")
    workflow_steps = [
        'Open file browser',
        'Navigate to project',
        'Open file browser',  # Duplicate
        'Open code editor',
        'Load file',
        'Edit code',
        'Save file',
        'Run tests',
        'Save file'  # Duplicate
    ]
    
    optimization = efficiency_analyzer.analyze_workflow_for_optimization(
        'Code Edit Workflow',
        workflow_steps
    )
    
    if optimization:
        print(f"\n✨ Workflow Optimization Found:")
        print(f"  Original steps: {len(optimization.current_steps)}")
        print(f"  Optimized steps: {len(optimization.optimized_steps)}")
        print(f"  Steps removed: {optimization.steps_removed}")
        print(f"  Time saved per execution: {optimization.time_saved_per_execution}s")
        print(f"  Estimated annual savings: {optimization.estimated_annual_savings/3600:.1f} hours")
    
    # Generate efficiency report
    print("\n📈 Efficiency Report:")
    report = efficiency_analyzer.generate_efficiency_report()
    print(f"  Total shortcuts: {report['total_shortcuts']}")
    print(f"  Total time saved: {report['total_time_saved_hours']:.2f} hours")
    print(f"  Top shortcuts:")
    for sc in report['top_shortcuts']:
        print(f"    - {sc['name']}: {sc['usage_count']} uses")
    
    print("\n✅ Shortcut and Efficiency System test complete!")
