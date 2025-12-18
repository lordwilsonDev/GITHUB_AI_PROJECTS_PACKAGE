"""
Task Prioritization Algorithm Module

This module implements intelligent task prioritization based on multiple factors:
- Urgency and deadlines
- Importance and impact  
- Dependencies and prerequisites
- User preferences and patterns
- Resource availability
- Historical completion data

Author: Vy Self-Evolving AI Ecosystem
Phase: 4 - Real-Time Adaptation System
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class Priority(Enum):
    """Task priority levels"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    MINIMAL = 1


class TaskStatus(Enum):
    """Task status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Task representation"""
    task_id: str
    title: str
    description: str
    urgency_score: float  # 0.0 to 1.0
    importance_score: float  # 0.0 to 1.0
    estimated_duration: int  # minutes
    deadline: Optional[str]  # ISO format
    dependencies: List[str]  # task_ids
    status: str
    created_at: str
    updated_at: str
    completed_at: Optional[str]
    user_id: str
    context: str
    tags: List[str]


@dataclass  
class PriorityScore:
    """Calculated priority score with breakdown"""
    task_id: str
    total_score: float
    urgency_component: float
    importance_component: float
    deadline_component: float
    dependency_component: float
    user_preference_component: float
    calculated_at: str
    priority_level: str


class TaskPrioritizer:
    """Calculates task priorities using multiple factors"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()
        
        # Weights for different priority components
        self.weights = {
            'urgency': 0.25,
            'importance': 0.30,
            'deadline': 0.25,
            'dependency': 0.10,
            'user_preference': 0.10
        }
    
    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                urgency_score REAL,
                importance_score REAL,
                estimated_duration INTEGER,
                deadline TEXT,
                dependencies TEXT,
                status TEXT,
                created_at TEXT,
                updated_at TEXT,
                completed_at TEXT,
                user_id TEXT,
                context TEXT,
                tags TEXT
            )
        ''')
        
        # Priority scores table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS priority_scores (
                task_id TEXT,
                total_score REAL,
                urgency_component REAL,
                importance_component REAL,
                deadline_component REAL,
                dependency_component REAL,
                user_preference_component REAL,
                calculated_at TEXT,
                priority_level TEXT,
                PRIMARY KEY (task_id, calculated_at)
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_preferences (
                user_id TEXT,
                preference_type TEXT,
                preference_value TEXT,
                weight REAL,
                updated_at TEXT,
                PRIMARY KEY (user_id, preference_type)
            )
        ''')
        
        # Task completion history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_history (
                history_id TEXT PRIMARY KEY,
                task_id TEXT,
                user_id TEXT,
                actual_duration INTEGER,
                estimated_duration INTEGER,
                priority_at_completion TEXT,
                completed_at TEXT,
                context TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_task(self, task: Task) -> str:
        """Add a new task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks
            (task_id, title, description, urgency_score, importance_score,
             estimated_duration, deadline, dependencies, status, created_at,
             updated_at, completed_at, user_id, context, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.task_id, task.title, task.description, task.urgency_score,
            task.importance_score, task.estimated_duration, task.deadline,
            json.dumps(task.dependencies), task.status, task.created_at,
            task.updated_at, task.completed_at, task.user_id, task.context,
            json.dumps(task.tags)
        ))
        
        conn.commit()
        conn.close()
        
        return task.task_id
    
    def calculate_priority(self, task_id: str) -> PriorityScore:
        """Calculate comprehensive priority score for a task"""
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Calculate each component
        urgency = self._calculate_urgency_component(task)
        importance = self._calculate_importance_component(task)
        deadline = self._calculate_deadline_component(task)
        dependency = self._calculate_dependency_component(task)
        user_pref = self._calculate_user_preference_component(task)
        
        # Calculate weighted total
        total_score = (
            urgency * self.weights['urgency'] +
            importance * self.weights['importance'] +
            deadline * self.weights['deadline'] +
            dependency * self.weights['dependency'] +
            user_pref * self.weights['user_preference']
        )
        
        # Determine priority level
        if total_score >= 0.8:
            priority_level = Priority.CRITICAL.name
        elif total_score >= 0.6:
            priority_level = Priority.HIGH.name
        elif total_score >= 0.4:
            priority_level = Priority.MEDIUM.name
        elif total_score >= 0.2:
            priority_level = Priority.LOW.name
        else:
            priority_level = Priority.MINIMAL.name
        
        priority_score = PriorityScore(
            task_id=task_id,
            total_score=total_score,
            urgency_component=urgency,
            importance_component=importance,
            deadline_component=deadline,
            dependency_component=dependency,
            user_preference_component=user_pref,
            calculated_at=datetime.now().isoformat(),
            priority_level=priority_level
        )
        
        # Store in database
        self._store_priority_score(priority_score)
        
        return priority_score
    
    def _calculate_urgency_component(self, task: Task) -> float:
        """Calculate urgency component (0.0 to 1.0)"""
        return task.urgency_score
    
    def _calculate_importance_component(self, task: Task) -> float:
        """Calculate importance component (0.0 to 1.0)"""
        return task.importance_score
    
    def _calculate_deadline_component(self, task: Task) -> float:
        """Calculate deadline urgency (0.0 to 1.0)"""
        if not task.deadline:
            return 0.3  # Neutral score for no deadline
        
        deadline = datetime.fromisoformat(task.deadline)
        now = datetime.now()
        time_until_deadline = (deadline - now).total_seconds()
        
        if time_until_deadline < 0:
            return 1.0  # Overdue - maximum urgency
        
        # Convert to hours
        hours_until = time_until_deadline / 3600
        
        # Exponential decay - closer deadline = higher score
        if hours_until < 1:
            return 0.95
        elif hours_until < 4:
            return 0.90
        elif hours_until < 24:
            return 0.80
        elif hours_until < 72:
            return 0.60
        elif hours_until < 168:  # 1 week
            return 0.40
        else:
            return 0.20
    
    def _calculate_dependency_component(self, task: Task) -> float:
        """Calculate dependency impact (0.0 to 1.0)"""
        if not task.dependencies:
            return 0.5  # No dependencies - neutral
        
        # Check how many tasks depend on this one
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM tasks
            WHERE dependencies LIKE ?
        ''', (f'%"{task.task_id}"%',))
        
        dependent_count = cursor.fetchone()[0]
        conn.close()
        
        # More dependents = higher priority
        if dependent_count == 0:
            return 0.3
        elif dependent_count == 1:
            return 0.5
        elif dependent_count == 2:
            return 0.7
        else:
            return 0.9
    
    def _calculate_user_preference_component(self, task: Task) -> float:
        """Calculate user preference component (0.0 to 1.0)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if user has preferences for this context
        cursor.execute('''
            SELECT preference_value, weight
            FROM task_preferences
            WHERE user_id = ? AND preference_type = 'context'
        ''', (task.user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            preferred_context, weight = result
            if task.context == preferred_context:
                return 0.8 * weight
        
        return 0.5  # Neutral if no preference
    
    def _store_priority_score(self, score: PriorityScore):
        """Store priority score in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO priority_scores
            (task_id, total_score, urgency_component, importance_component,
             deadline_component, dependency_component, user_preference_component,
             calculated_at, priority_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            score.task_id, score.total_score, score.urgency_component,
            score.importance_component, score.deadline_component,
            score.dependency_component, score.user_preference_component,
            score.calculated_at, score.priority_level
        ))
        
        conn.commit()
        conn.close()
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Task(
                task_id=row[0], title=row[1], description=row[2],
                urgency_score=row[3], importance_score=row[4],
                estimated_duration=row[5], deadline=row[6],
                dependencies=json.loads(row[7]), status=row[8],
                created_at=row[9], updated_at=row[10], completed_at=row[11],
                user_id=row[12], context=row[13], tags=json.loads(row[14])
            )
        return None
    
    def get_prioritized_tasks(self, user_id: str, status: Optional[str] = None,
                             limit: Optional[int] = None) -> List[Tuple[Task, PriorityScore]]:
        """Get tasks sorted by priority"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT task_id FROM tasks WHERE user_id = ?'
        params = [user_id]
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        cursor.execute(query, params)
        task_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Calculate priorities for all tasks
        task_priorities = []
        for task_id in task_ids:
            task = self.get_task(task_id)
            priority = self.calculate_priority(task_id)
            task_priorities.append((task, priority))
        
        # Sort by total score descending
        task_priorities.sort(key=lambda x: x[1].total_score, reverse=True)
        
        if limit:
            return task_priorities[:limit]
        return task_priorities


class AdaptivePrioritizer:
    """Adaptive task prioritization that learns from user behavior"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.prioritizer = TaskPrioritizer(db_path)
    
    def record_task_completion(self, task_id: str, actual_duration: int):
        """Record task completion for learning"""
        task = self.prioritizer.get_task(task_id)
        if not task:
            return
        
        # Get priority at completion
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT priority_level FROM priority_scores
            WHERE task_id = ?
            ORDER BY calculated_at DESC
            LIMIT 1
        ''', (task_id,))
        
        result = cursor.fetchone()
        priority_at_completion = result[0] if result else "UNKNOWN"
        
        # Record in history
        history_id = f"hist_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        cursor.execute('''
            INSERT INTO task_history
            (history_id, task_id, user_id, actual_duration, estimated_duration,
             priority_at_completion, completed_at, context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            history_id, task_id, task.user_id, actual_duration,
            task.estimated_duration, priority_at_completion,
            datetime.now().isoformat(), task.context
        ))
        
        # Update task status
        cursor.execute('''
            UPDATE tasks
            SET status = ?, completed_at = ?, updated_at = ?
            WHERE task_id = ?
        ''', (TaskStatus.COMPLETED.value, datetime.now().isoformat(),
              datetime.now().isoformat(), task_id))
        
        conn.commit()
        conn.close()
        
        # Learn from completion
        self._learn_from_completion(task, actual_duration)
    
    def _learn_from_completion(self, task: Task, actual_duration: int):
        """Learn from task completion to adjust future priorities"""
        # Analyze if estimation was accurate
        if task.estimated_duration > 0:
            accuracy = 1.0 - abs(actual_duration - task.estimated_duration) / task.estimated_duration
            
            # If consistently off, adjust weight preferences
            if accuracy < 0.5:
                self._adjust_weights_for_user(task.user_id, task.context)
    
    def _adjust_weights_for_user(self, user_id: str, context: str):
        """Adjust prioritization weights based on user patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store or update preference
        cursor.execute('''
            INSERT OR REPLACE INTO task_preferences
            (user_id, preference_type, preference_value, weight, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, 'context', context, 0.8, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_next_task_recommendation(self, user_id: str, 
                                    available_time: int) -> Optional[Task]:
        """Recommend next task based on priority and available time"""
        prioritized = self.prioritizer.get_prioritized_tasks(
            user_id, status=TaskStatus.PENDING.value
        )
        
        # Find highest priority task that fits in available time
        for task, priority in prioritized:
            if task.estimated_duration <= available_time:
                # Check dependencies are met
                if self._dependencies_met(task):
                    return task
        
        return None
    
    def _dependencies_met(self, task: Task) -> bool:
        """Check if all task dependencies are completed"""
        if not task.dependencies:
            return True
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for dep_id in task.dependencies:
            cursor.execute(
                'SELECT status FROM tasks WHERE task_id = ?',
                (dep_id,)
            )
            result = cursor.fetchone()
            if not result or result[0] != TaskStatus.COMPLETED.value:
                conn.close()
                return False
        
        conn.close()
        return True
    
    def get_priority_analytics(self, user_id: str, days: int = 30) -> Dict:
        """Get analytics on task priorities and completion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Get completion stats by priority
        cursor.execute('''
            SELECT priority_at_completion, COUNT(*), AVG(actual_duration)
            FROM task_history
            WHERE user_id = ? AND completed_at > ?
            GROUP BY priority_at_completion
        ''', (user_id, cutoff))
        
        priority_stats = {}
        for row in cursor.fetchall():
            priority_stats[row[0]] = {
                'count': row[1],
                'avg_duration': row[2]
            }
        
        # Get estimation accuracy
        cursor.execute('''
            SELECT AVG(ABS(actual_duration - estimated_duration) * 1.0 / estimated_duration)
            FROM task_history
            WHERE user_id = ? AND completed_at > ? AND estimated_duration > 0
        ''', (user_id, cutoff))
        
        avg_error = cursor.fetchone()[0] or 0
        estimation_accuracy = max(0, 1.0 - avg_error)
        
        conn.close()
        
        return {
            'priority_stats': priority_stats,
            'estimation_accuracy': estimation_accuracy,
            'period_days': days,
            'generated_at': datetime.now().isoformat()
        }
