#!/usr/bin/env python3
"""
Learning Engine - Core component for monitoring and learning from user interactions

This module implements the continuous learning capabilities of the vy-nexus system,
including interaction monitoring, pattern recognition, and adaptive learning.
"""

import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib


class InteractionMonitor:
    """
    Monitors all user interactions and logs them for analysis.
    Tracks commands, requests, responses, outcomes, and context.
    """
    
    def __init__(self, db_path: str = "data/interactions.db"):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """Initialize the interactions database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Interactions table - stores all user interactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                interaction_type TEXT NOT NULL,
                user_input TEXT,
                system_response TEXT,
                outcome TEXT,
                success BOOLEAN,
                duration_seconds REAL,
                context TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tasks table - tracks task completions and failures
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                task_description TEXT NOT NULL,
                status TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_seconds REAL,
                steps_count INTEGER,
                success BOOLEAN,
                failure_reason TEXT,
                context TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Patterns table - stores identified patterns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_hash TEXT UNIQUE NOT NULL,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                confidence REAL,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                metadata TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        self.logger.info("Interaction database initialized")
    
    def log_interaction(self, 
                       interaction_type: str,
                       user_input: Optional[str] = None,
                       system_response: Optional[str] = None,
                       outcome: Optional[str] = None,
                       success: bool = True,
                       duration: Optional[float] = None,
                       context: Optional[Dict] = None,
                       metadata: Optional[Dict] = None) -> int:
        """
        Log a user interaction to the database.
        
        Args:
            interaction_type: Type of interaction (e.g., 'command', 'query', 'task')
            user_input: The user's input/request
            system_response: The system's response
            outcome: The outcome of the interaction
            success: Whether the interaction was successful
            duration: Duration in seconds
            context: Additional context information
            metadata: Additional metadata
            
        Returns:
            The ID of the logged interaction
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        context_json = json.dumps(context) if context else None
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT INTO interactions 
            (timestamp, interaction_type, user_input, system_response, 
             outcome, success, duration_seconds, context, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, interaction_type, user_input, system_response,
              outcome, success, duration, context_json, metadata_json))
        
        interaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        self.logger.debug(f"Logged interaction {interaction_id}: {interaction_type}")
        return interaction_id
    
    def log_task(self,
                task_description: str,
                status: str,
                start_time: datetime,
                end_time: Optional[datetime] = None,
                steps_count: Optional[int] = None,
                success: bool = True,
                failure_reason: Optional[str] = None,
                context: Optional[Dict] = None) -> str:
        """
        Log a task execution to the database.
        
        Args:
            task_description: Description of the task
            status: Current status (e.g., 'started', 'completed', 'failed')
            start_time: When the task started
            end_time: When the task ended (if completed)
            steps_count: Number of steps taken
            success: Whether the task succeeded
            failure_reason: Reason for failure (if applicable)
            context: Additional context
            
        Returns:
            The task ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Generate unique task ID
        task_id = hashlib.md5(
            f"{task_description}{start_time.isoformat()}".encode()
        ).hexdigest()[:16]
        
        duration = None
        if end_time:
            duration = (end_time - start_time).total_seconds()
        
        context_json = json.dumps(context) if context else None
        
        cursor.execute("""
            INSERT OR REPLACE INTO tasks
            (task_id, task_description, status, start_time, end_time,
             duration_seconds, steps_count, success, failure_reason, context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (task_id, task_description, status, start_time.isoformat(),
              end_time.isoformat() if end_time else None,
              duration, steps_count, success, failure_reason, context_json))
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Logged task {task_id}: {status}")
        return task_id
    
    def get_recent_interactions(self, limit: int = 100) -> List[Dict]:
        """Retrieve recent interactions from the database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM interactions
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        interactions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return interactions
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get statistics about task completions and failures."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total tasks
        cursor.execute("SELECT COUNT(*) FROM tasks")
        total_tasks = cursor.fetchone()[0]
        
        # Successful tasks
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE success = 1")
        successful_tasks = cursor.fetchone()[0]
        
        # Failed tasks
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE success = 0")
        failed_tasks = cursor.fetchone()[0]
        
        # Average duration
        cursor.execute("""
            SELECT AVG(duration_seconds) FROM tasks 
            WHERE duration_seconds IS NOT NULL
        """)
        avg_duration = cursor.fetchone()[0] or 0
        
        # Average steps
        cursor.execute("""
            SELECT AVG(steps_count) FROM tasks 
            WHERE steps_count IS NOT NULL
        """)
        avg_steps = cursor.fetchone()[0] or 0
        
        conn.close()
        
        success_rate = (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            'total_tasks': total_tasks,
            'successful_tasks': successful_tasks,
            'failed_tasks': failed_tasks,
            'success_rate': round(success_rate, 2),
            'average_duration_seconds': round(avg_duration, 2),
            'average_steps': round(avg_steps, 2)
        }


class PatternRecognizer:
    """
    Identifies patterns in user interactions and behaviors.
    Detects recurring workflows, preferences, and optimization opportunities.
    """
    
    def __init__(self, db_path: str = "data/interactions.db"):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
    
    def identify_recurring_tasks(self, min_frequency: int = 3) -> List[Dict]:
        """
        Identify tasks that occur frequently and could be automated.
        
        Args:
            min_frequency: Minimum number of occurrences to consider
            
        Returns:
            List of recurring task patterns
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT task_description, COUNT(*) as frequency,
                   AVG(duration_seconds) as avg_duration,
                   AVG(steps_count) as avg_steps,
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count
            FROM tasks
            GROUP BY task_description
            HAVING frequency >= ?
            ORDER BY frequency DESC
        """, (min_frequency,))
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                'task_description': row[0],
                'frequency': row[1],
                'avg_duration': round(row[2] or 0, 2),
                'avg_steps': round(row[3] or 0, 2),
                'success_count': row[4],
                'success_rate': round((row[4] / row[1] * 100), 2)
            })
        
        conn.close()
        return patterns
    
    def detect_workflow_sequences(self, window_minutes: int = 60) -> List[Dict]:
        """
        Detect common sequences of interactions that form workflows.
        
        Args:
            window_minutes: Time window to consider interactions as part of same workflow
            
        Returns:
            List of detected workflow sequences
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT interaction_type, timestamp
            FROM interactions
            ORDER BY timestamp ASC
        """)
        
        interactions = cursor.fetchall()
        conn.close()
        
        # Simple sequence detection (can be enhanced with more sophisticated algorithms)
        sequences = []
        current_sequence = []
        last_timestamp = None
        
        for interaction in interactions:
            current_time = datetime.fromisoformat(interaction['timestamp'])
            
            if last_timestamp is None:
                current_sequence = [interaction['interaction_type']]
            else:
                time_diff = (current_time - last_timestamp).total_seconds() / 60
                
                if time_diff <= window_minutes:
                    current_sequence.append(interaction['interaction_type'])
                else:
                    if len(current_sequence) > 1:
                        sequences.append(current_sequence.copy())
                    current_sequence = [interaction['interaction_type']]
            
            last_timestamp = current_time
        
        # Add last sequence
        if len(current_sequence) > 1:
            sequences.append(current_sequence)
        
        return sequences
    
    def store_pattern(self, pattern_type: str, pattern_data: Dict, 
                     confidence: float = 0.8) -> str:
        """
        Store an identified pattern in the database.
        
        Args:
            pattern_type: Type of pattern (e.g., 'recurring_task', 'workflow_sequence')
            pattern_data: The pattern data
            confidence: Confidence score (0-1)
            
        Returns:
            Pattern hash ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        pattern_json = json.dumps(pattern_data)
        pattern_hash = hashlib.md5(pattern_json.encode()).hexdigest()[:16]
        timestamp = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO patterns
            (pattern_hash, pattern_type, pattern_data, confidence, 
             first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (pattern_hash, pattern_type, pattern_json, confidence,
              timestamp, timestamp))
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Stored pattern {pattern_hash}: {pattern_type}")
        return pattern_hash


class LearningEngine:
    """
    Main learning engine that coordinates monitoring, pattern recognition,
    and adaptive learning.
    """
    
    def __init__(self, config_path: str = "data/configurations.json"):
        self.config = self._load_config(config_path)
        self.monitor = InteractionMonitor()
        self.pattern_recognizer = PatternRecognizer()
        self.logger = logging.getLogger(__name__)
        
        # Set up logging
        self._setup_logging()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file not found: {config_path}")
            return {}
    
    def _setup_logging(self):
        """Set up logging configuration."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / "learning.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def process_interaction(self, **kwargs) -> int:
        """Process and log a user interaction."""
        return self.monitor.log_interaction(**kwargs)
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """
        Analyze interactions to identify patterns and learning opportunities.
        
        Returns:
            Dictionary containing analysis results
        """
        self.logger.info("Starting pattern analysis...")
        
        # Identify recurring tasks
        recurring_tasks = self.pattern_recognizer.identify_recurring_tasks()
        
        # Detect workflow sequences
        workflow_sequences = self.pattern_recognizer.detect_workflow_sequences()
        
        # Get task statistics
        task_stats = self.monitor.get_task_statistics()
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'recurring_tasks': recurring_tasks,
            'workflow_sequences_count': len(workflow_sequences),
            'task_statistics': task_stats,
            'automation_opportunities': len([t for t in recurring_tasks if t['frequency'] >= 5])
        }
        
        self.logger.info(f"Pattern analysis complete. Found {len(recurring_tasks)} recurring tasks")
        
        return analysis
    
    def generate_learning_report(self) -> str:
        """
        Generate a comprehensive learning report.
        
        Returns:
            Formatted report string
        """
        analysis = self.analyze_patterns()
        
        report = []
        report.append("=" * 60)
        report.append("LEARNING ENGINE REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {analysis['timestamp']}")
        report.append("")
        
        # Task Statistics
        report.append("TASK STATISTICS:")
        report.append("-" * 60)
        stats = analysis['task_statistics']
        report.append(f"Total Tasks: {stats['total_tasks']}")
        report.append(f"Successful: {stats['successful_tasks']}")
        report.append(f"Failed: {stats['failed_tasks']}")
        report.append(f"Success Rate: {stats['success_rate']}%")
        report.append(f"Average Duration: {stats['average_duration_seconds']}s")
        report.append(f"Average Steps: {stats['average_steps']}")
        report.append("")
        
        # Recurring Tasks
        report.append("RECURRING TASKS:")
        report.append("-" * 60)
        for task in analysis['recurring_tasks'][:10]:  # Top 10
            report.append(f"  - {task['task_description']}")
            report.append(f"    Frequency: {task['frequency']}, Success Rate: {task['success_rate']}%")
        report.append("")
        
        # Automation Opportunities
        report.append("AUTOMATION OPPORTUNITIES:")
        report.append("-" * 60)
        report.append(f"Tasks suitable for automation: {analysis['automation_opportunities']}")
        report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)


if __name__ == "__main__":
    # Example usage and testing
    engine = LearningEngine()
    
    # Log some sample interactions
    engine.process_interaction(
        interaction_type="command",
        user_input="Create a new file",
        system_response="File created successfully",
        outcome="success",
        success=True,
        duration=2.5
    )
    
    # Generate report
    print(engine.generate_learning_report())
