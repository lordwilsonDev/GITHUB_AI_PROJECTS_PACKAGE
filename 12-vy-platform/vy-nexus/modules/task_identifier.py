#!/usr/bin/env python3
"""
Repetitive Task Identifier Module

This module identifies repetitive tasks that can be automated.
It analyzes task patterns, frequencies, and characteristics to determine
automation potential.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, Counter
import statistics
import hashlib


class TaskSignature:
    """
    Represents a unique signature for a task based on its characteristics.
    """
    
    @staticmethod
    def generate(task_type: str, metadata: Optional[Dict] = None) -> str:
        """
        Generate a unique signature for a task.
        
        Args:
            task_type: Type of the task
            metadata: Task metadata
        
        Returns:
            Signature hash string
        """
        # Extract key characteristics
        characteristics = {
            "type": task_type,
            "tools": [],
            "steps": [],
            "inputs": []
        }
        
        if metadata:
            characteristics["tools"] = metadata.get("tools_used", [])
            characteristics["steps"] = metadata.get("steps", [])
            characteristics["inputs"] = sorted(metadata.get("input_types", []))
        
        # Create deterministic string representation
        sig_string = json.dumps(characteristics, sort_keys=True)
        
        # Generate hash
        return hashlib.md5(sig_string.encode()).hexdigest()
    
    @staticmethod
    def similarity(sig1: str, sig2: str, metadata1: Optional[Dict] = None, metadata2: Optional[Dict] = None) -> float:
        """
        Calculate similarity between two task signatures.
        
        Args:
            sig1: First signature
            sig2: Second signature
            metadata1: Metadata for first task
            metadata2: Metadata for second task
        
        Returns:
            Similarity score (0-1)
        """
        # Exact match
        if sig1 == sig2:
            return 1.0
        
        # Compare metadata if available
        if metadata1 and metadata2:
            tools1 = set(metadata1.get("tools_used", []))
            tools2 = set(metadata2.get("tools_used", []))
            
            if tools1 and tools2:
                # Jaccard similarity for tools
                intersection = len(tools1 & tools2)
                union = len(tools1 | tools2)
                return intersection / union if union > 0 else 0.0
        
        return 0.0


class RepetitiveTaskIdentifier:
    """
    Identifies repetitive tasks that are candidates for automation.
    """
    
    def __init__(self, db_path: str = "data/vy_nexus.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize task identification tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Task signatures table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_signatures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signature_hash TEXT UNIQUE NOT NULL,
                task_type TEXT NOT NULL,
                occurrence_count INTEGER DEFAULT 1,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                avg_duration_seconds REAL,
                success_rate REAL DEFAULT 1.0,
                automation_score REAL DEFAULT 0.0,
                metadata TEXT
            )
        """)
        
        # Automation candidates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS automation_candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signature_id INTEGER,
                candidate_name TEXT NOT NULL,
                description TEXT,
                automation_type TEXT,
                priority INTEGER DEFAULT 5,
                estimated_time_savings REAL,
                complexity_score REAL DEFAULT 0.5,
                status TEXT DEFAULT 'identified',
                identified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (signature_id) REFERENCES task_signatures(id)
            )
        """)
        
        # Task patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_description TEXT,
                frequency TEXT,
                task_signatures TEXT,
                automation_potential REAL DEFAULT 0.5,
                identified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def analyze_task(self, task_id: int) -> Dict[str, Any]:
        """
        Analyze a task and update signature database.
        
        Args:
            task_id: ID of the task to analyze
        
        Returns:
            Analysis results
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get task details
        cursor.execute("""
            SELECT task_type, status, duration_seconds, metadata
            FROM tasks
            WHERE id = ?
        """, (task_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return {"status": "error", "message": "Task not found"}
        
        task_type, status, duration, metadata_json = result
        metadata = json.loads(metadata_json) if metadata_json else {}
        
        # Generate signature
        signature = TaskSignature.generate(task_type, metadata)
        
        # Check if signature exists
        cursor.execute("""
            SELECT id, occurrence_count, avg_duration_seconds, success_rate
            FROM task_signatures
            WHERE signature_hash = ?
        """, (signature,))
        
        sig_result = cursor.fetchone()
        
        if sig_result:
            # Update existing signature
            sig_id, count, avg_duration, success_rate = sig_result
            
            new_count = count + 1
            new_avg_duration = ((avg_duration * count) + (duration or 0)) / new_count if duration else avg_duration
            
            # Update success rate
            success_increment = 1 if status == 'completed' else 0
            new_success_rate = ((success_rate * count) + success_increment) / new_count
            
            # Calculate automation score
            automation_score = self._calculate_automation_score(
                new_count, new_avg_duration, new_success_rate
            )
            
            cursor.execute("""
                UPDATE task_signatures
                SET occurrence_count = ?,
                    last_seen = CURRENT_TIMESTAMP,
                    avg_duration_seconds = ?,
                    success_rate = ?,
                    automation_score = ?
                WHERE id = ?
            """, (new_count, new_avg_duration, new_success_rate, automation_score, sig_id))
        else:
            # Insert new signature
            success_rate = 1.0 if status == 'completed' else 0.0
            automation_score = self._calculate_automation_score(1, duration or 0, success_rate)
            
            cursor.execute("""
                INSERT INTO task_signatures
                (signature_hash, task_type, avg_duration_seconds, success_rate, automation_score, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (signature, task_type, duration, success_rate, automation_score, json.dumps(metadata)))
            
            sig_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "signature_id": sig_id,
            "signature_hash": signature,
            "automation_score": automation_score
        }
    
    def _calculate_automation_score(self, count: int, avg_duration: float, success_rate: float) -> float:
        """
        Calculate automation potential score.
        
        Args:
            count: Number of occurrences
            avg_duration: Average duration in seconds
            success_rate: Success rate (0-1)
        
        Returns:
            Automation score (0-1)
        """
        # Frequency score (more frequent = higher score)
        frequency_score = min(1.0, count / 10.0)  # Max at 10 occurrences
        
        # Duration score (longer tasks = higher potential savings)
        duration_score = min(1.0, avg_duration / 600.0)  # Max at 10 minutes
        
        # Success rate score (higher success = easier to automate)
        success_score = success_rate
        
        # Weighted combination
        automation_score = (
            frequency_score * 0.4 +
            duration_score * 0.3 +
            success_score * 0.3
        )
        
        return automation_score
    
    def identify_repetitive_tasks(self, min_occurrences: int = 3, days: int = 30) -> List[Dict[str, Any]]:
        """
        Identify repetitive tasks that occur frequently.
        
        Args:
            min_occurrences: Minimum number of occurrences to consider
            days: Number of days to look back
        
        Returns:
            List of repetitive task signatures
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT id, signature_hash, task_type, occurrence_count, 
                   avg_duration_seconds, success_rate, automation_score, metadata
            FROM task_signatures
            WHERE occurrence_count >= ? AND last_seen > ?
            ORDER BY automation_score DESC, occurrence_count DESC
        """, (min_occurrences, cutoff_date))
        
        results = cursor.fetchall()
        conn.close()
        
        repetitive_tasks = []
        for row in results:
            metadata = json.loads(row[7]) if row[7] else {}
            repetitive_tasks.append({
                "signature_id": row[0],
                "signature_hash": row[1],
                "task_type": row[2],
                "occurrence_count": row[3],
                "avg_duration_seconds": row[4],
                "success_rate": row[5],
                "automation_score": row[6],
                "tools_used": metadata.get("tools_used", []),
                "estimated_time_savings": row[3] * row[4] if row[4] else 0
            })
        
        return repetitive_tasks
    
    def create_automation_candidate(
        self,
        signature_id: int,
        candidate_name: str,
        description: str,
        automation_type: str = "script",
        priority: int = 5,
        complexity_score: float = 0.5,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Create an automation candidate from a repetitive task.
        
        Args:
            signature_id: ID of the task signature
            candidate_name: Name for the automation candidate
            description: Description of what to automate
            automation_type: Type of automation (script, workflow, macro, etc.)
            priority: Priority level (1-10)
            complexity_score: Estimated complexity (0-1)
            metadata: Additional metadata
        
        Returns:
            Candidate ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get signature details for time savings calculation
        cursor.execute("""
            SELECT occurrence_count, avg_duration_seconds
            FROM task_signatures
            WHERE id = ?
        """, (signature_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            raise ValueError(f"Signature ID {signature_id} not found")
        
        occurrence_count, avg_duration = result
        estimated_time_savings = occurrence_count * avg_duration if avg_duration else 0
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT INTO automation_candidates
            (signature_id, candidate_name, description, automation_type, 
             priority, estimated_time_savings, complexity_score, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (signature_id, candidate_name, description, automation_type,
              priority, estimated_time_savings, complexity_score, metadata_json))
        
        candidate_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return candidate_id
    
    def identify_task_patterns(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Identify patterns in task execution (sequences, timing, etc.).
        
        Args:
            days: Number of days to analyze
        
        Returns:
            List of identified patterns
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Get tasks in chronological order
        cursor.execute("""
            SELECT task_type, created_at, metadata
            FROM tasks
            WHERE created_at > ?
            ORDER BY created_at ASC
        """, (cutoff_date,))
        
        tasks = cursor.fetchall()
        
        patterns = []
        
        # Identify sequential patterns (tasks that often follow each other)
        if len(tasks) >= 2:
            sequences = []
            for i in range(len(tasks) - 1):
                sequences.append((tasks[i][0], tasks[i+1][0]))
            
            sequence_counts = Counter(sequences)
            
            for (task1, task2), count in sequence_counts.most_common(10):
                if count >= 3:  # Minimum occurrences
                    pattern_id = self._record_pattern(
                        "sequential",
                        f"{task1} -> {task2}",
                        f"Occurs {count} times",
                        [task1, task2],
                        min(1.0, count / 10.0)
                    )
                    
                    patterns.append({
                        "pattern_id": pattern_id,
                        "type": "sequential",
                        "description": f"{task1} followed by {task2}",
                        "frequency": count,
                        "automation_potential": min(1.0, count / 10.0)
                    })
        
        # Identify time-based patterns (tasks at similar times)
        time_patterns = defaultdict(list)
        for task_type, created_at, metadata in tasks:
            dt = datetime.fromisoformat(created_at)
            hour = dt.hour
            time_patterns[(task_type, hour)].append(dt)
        
        for (task_type, hour), occurrences in time_patterns.items():
            if len(occurrences) >= 3:
                pattern_id = self._record_pattern(
                    "temporal",
                    f"{task_type} at hour {hour}",
                    f"Occurs {len(occurrences)} times around {hour}:00",
                    [task_type],
                    min(1.0, len(occurrences) / 10.0)
                )
                
                patterns.append({
                    "pattern_id": pattern_id,
                    "type": "temporal",
                    "description": f"{task_type} typically occurs around {hour}:00",
                    "frequency": len(occurrences),
                    "automation_potential": min(1.0, len(occurrences) / 10.0)
                })
        
        conn.close()
        return patterns
    
    def _record_pattern(
        self,
        pattern_type: str,
        description: str,
        frequency: str,
        task_signatures: List[str],
        automation_potential: float
    ) -> int:
        """
        Record a discovered pattern in the database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO task_patterns
            (pattern_type, pattern_description, frequency, task_signatures, automation_potential)
            VALUES (?, ?, ?, ?, ?)
        """, (pattern_type, description, frequency, json.dumps(task_signatures), automation_potential))
        
        pattern_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return pattern_id
    
    def get_automation_candidates(self, min_priority: int = 5) -> List[Dict[str, Any]]:
        """
        Get all automation candidates sorted by priority and time savings.
        
        Args:
            min_priority: Minimum priority level
        
        Returns:
            List of automation candidates
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ac.id, ac.candidate_name, ac.description, ac.automation_type,
                   ac.priority, ac.estimated_time_savings, ac.complexity_score,
                   ac.status, ts.task_type, ts.occurrence_count
            FROM automation_candidates ac
            JOIN task_signatures ts ON ac.signature_id = ts.id
            WHERE ac.priority >= ? AND ac.status != 'completed'
            ORDER BY ac.priority DESC, ac.estimated_time_savings DESC
        """, (min_priority,))
        
        results = cursor.fetchall()
        conn.close()
        
        candidates = []
        for row in results:
            candidates.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "automation_type": row[3],
                "priority": row[4],
                "estimated_time_savings_seconds": row[5],
                "complexity_score": row[6],
                "status": row[7],
                "task_type": row[8],
                "occurrence_count": row[9]
            })
        
        return candidates
    
    def generate_automation_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate a comprehensive automation opportunities report.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Comprehensive report dictionary
        """
        repetitive_tasks = self.identify_repetitive_tasks(min_occurrences=3, days=days)
        patterns = self.identify_task_patterns(days=days)
        candidates = self.get_automation_candidates(min_priority=1)
        
        # Calculate total potential time savings
        total_time_savings = sum(t["estimated_time_savings"] for t in repetitive_tasks)
        
        # Identify top opportunities
        top_opportunities = sorted(
            repetitive_tasks,
            key=lambda x: x["automation_score"],
            reverse=True
        )[:5]
        
        report = {
            "report_date": datetime.now().isoformat(),
            "analysis_period_days": days,
            "summary": {
                "total_repetitive_tasks": len(repetitive_tasks),
                "total_patterns_identified": len(patterns),
                "total_automation_candidates": len(candidates),
                "total_potential_time_savings_seconds": total_time_savings,
                "total_potential_time_savings_hours": total_time_savings / 3600
            },
            "top_opportunities": top_opportunities,
            "patterns": patterns,
            "automation_candidates": candidates
        }
        
        return report


if __name__ == "__main__":
    # Example usage
    identifier = RepetitiveTaskIdentifier()
    
    # Generate report
    report = identifier.generate_automation_report(days=30)
    print("Automation Opportunities Report:")
    print(json.dumps(report, indent=2))
