#!/usr/bin/env python3
"""
Research Automation Module

This module automates research for new tools, techniques, and methodologies.
It continuously learns about emerging technologies and best practices.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict, Counter
import re


class ResearchTopic:
    """Enumeration of research topic categories"""
    TOOLS = "tools"
    TECHNIQUES = "techniques"
    METHODOLOGIES = "methodologies"
    TECHNOLOGIES = "technologies"
    BEST_PRACTICES = "best_practices"
    PRODUCTIVITY = "productivity"
    AUTOMATION = "automation"


class ResearchAutomation:
    """
    Automates research and learning about new tools, techniques, and methodologies.
    """
    
    def __init__(self, db_path: str = "data/vy_nexus.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize research tracking tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Research topics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS research_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                topic_name TEXT NOT NULL,
                priority INTEGER DEFAULT 5,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_researched TIMESTAMP,
                research_count INTEGER DEFAULT 0,
                metadata TEXT,
                UNIQUE(category, topic_name)
            )
        """)
        
        # Research findings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS research_findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER,
                finding_type TEXT,
                title TEXT,
                description TEXT,
                source TEXT,
                relevance_score REAL DEFAULT 0.5,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (topic_id) REFERENCES research_topics(id)
            )
        """)
        
        # Learning objectives table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_objectives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                objective_type TEXT,
                objective_name TEXT,
                description TEXT,
                priority INTEGER DEFAULT 5,
                status TEXT DEFAULT 'active',
                progress REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Knowledge base table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                topic TEXT,
                content TEXT,
                confidence_score REAL DEFAULT 0.5,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source TEXT,
                tags TEXT,
                metadata TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_research_topic(
        self,
        category: str,
        topic_name: str,
        priority: int = 5,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Add a new research topic to the queue.
        
        Args:
            category: Topic category (tools, techniques, etc.)
            topic_name: Name of the topic to research
            priority: Priority level (1-10, higher is more important)
            metadata: Additional metadata about the topic
        
        Returns:
            Topic ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        try:
            cursor.execute("""
                INSERT INTO research_topics (category, topic_name, priority, metadata)
                VALUES (?, ?, ?, ?)
            """, (category, topic_name, priority, metadata_json))
            topic_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            # Topic already exists, update priority if higher
            cursor.execute("""
                SELECT id, priority FROM research_topics
                WHERE category = ? AND topic_name = ?
            """, (category, topic_name))
            result = cursor.fetchone()
            topic_id = result[0]
            if priority > result[1]:
                cursor.execute("""
                    UPDATE research_topics
                    SET priority = ?, metadata = ?
                    WHERE id = ?
                """, (priority, metadata_json, topic_id))
        
        conn.commit()
        conn.close()
        
        return topic_id
    
    def record_finding(
        self,
        topic_id: int,
        finding_type: str,
        title: str,
        description: str,
        source: str = "automated_research",
        relevance_score: float = 0.5,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Record a research finding.
        
        Args:
            topic_id: ID of the research topic
            finding_type: Type of finding (tool, technique, best_practice, etc.)
            title: Title of the finding
            description: Detailed description
            source: Source of the information
            relevance_score: How relevant this finding is (0-1)
            metadata: Additional metadata
        
        Returns:
            Finding ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT INTO research_findings
            (topic_id, finding_type, title, description, source, relevance_score, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (topic_id, finding_type, title, description, source, relevance_score, metadata_json))
        
        finding_id = cursor.lastrowid
        
        # Update topic research count
        cursor.execute("""
            UPDATE research_topics
            SET research_count = research_count + 1,
                last_researched = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (topic_id,))
        
        conn.commit()
        conn.close()
        
        return finding_id
    
    def add_to_knowledge_base(
        self,
        category: str,
        topic: str,
        content: str,
        confidence_score: float = 0.5,
        source: str = "research",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Add knowledge to the knowledge base.
        
        Args:
            category: Knowledge category
            topic: Specific topic
            content: The knowledge content
            confidence_score: Confidence in this knowledge (0-1)
            source: Source of the knowledge
            tags: List of tags for categorization
            metadata: Additional metadata
        
        Returns:
            Knowledge ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tags_json = json.dumps(tags) if tags else None
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT INTO knowledge_base
            (category, topic, content, confidence_score, source, tags, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (category, topic, content, confidence_score, source, tags_json, metadata_json))
        
        knowledge_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return knowledge_id
    
    def get_priority_research_topics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the highest priority research topics.
        
        Args:
            limit: Maximum number of topics to return
        
        Returns:
            List of research topics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, category, topic_name, priority, status, research_count, last_researched
            FROM research_topics
            WHERE status != 'completed'
            ORDER BY priority DESC, research_count ASC
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        topics = []
        for row in results:
            topics.append({
                "id": row[0],
                "category": row[1],
                "topic_name": row[2],
                "priority": row[3],
                "status": row[4],
                "research_count": row[5],
                "last_researched": row[6]
            })
        
        return topics
    
    def get_findings_for_topic(self, topic_id: int) -> List[Dict[str, Any]]:
        """Get all findings for a specific research topic"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, finding_type, title, description, source, relevance_score, timestamp
            FROM research_findings
            WHERE topic_id = ?
            ORDER BY relevance_score DESC, timestamp DESC
        """, (topic_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        findings = []
        for row in results:
            findings.append({
                "id": row[0],
                "finding_type": row[1],
                "title": row[2],
                "description": row[3],
                "source": row[4],
                "relevance_score": row[5],
                "timestamp": row[6]
            })
        
        return findings
    
    def search_knowledge_base(
        self,
        query: str,
        category: Optional[str] = None,
        min_confidence: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge base.
        
        Args:
            query: Search query
            category: Optional category filter
            min_confidence: Minimum confidence score
        
        Returns:
            List of matching knowledge entries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simple keyword search (in production, use FTS or vector search)
        query_lower = query.lower()
        
        if category:
            cursor.execute("""
                SELECT id, category, topic, content, confidence_score, last_updated, source, tags
                FROM knowledge_base
                WHERE category = ? AND confidence_score >= ?
            """, (category, min_confidence))
        else:
            cursor.execute("""
                SELECT id, category, topic, content, confidence_score, last_updated, source, tags
                FROM knowledge_base
                WHERE confidence_score >= ?
            """, (min_confidence,))
        
        results = cursor.fetchall()
        conn.close()
        
        # Filter by query match
        matches = []
        for row in results:
            content_lower = row[3].lower()
            topic_lower = row[2].lower()
            
            if query_lower in content_lower or query_lower in topic_lower:
                matches.append({
                    "id": row[0],
                    "category": row[1],
                    "topic": row[2],
                    "content": row[3],
                    "confidence_score": row[4],
                    "last_updated": row[5],
                    "source": row[6],
                    "tags": json.loads(row[7]) if row[7] else []
                })
        
        return matches


class LearningObjectiveManager:
    """
    Manages learning objectives and tracks progress.
    """
    
    def __init__(self, db_path: str = "data/vy_nexus.db"):
        self.db_path = db_path
        self.research = ResearchAutomation(db_path)
    
    def create_objective(
        self,
        objective_type: str,
        objective_name: str,
        description: str,
        priority: int = 5,
        metadata: Optional[Dict] = None
    ) -> int:
        """Create a new learning objective"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT INTO learning_objectives
            (objective_type, objective_name, description, priority, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (objective_type, objective_name, description, priority, metadata_json))
        
        objective_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return objective_id
    
    def update_progress(self, objective_id: int, progress: float):
        """
        Update progress on a learning objective.
        
        Args:
            objective_id: ID of the objective
            progress: Progress value (0.0 to 1.0)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clamp progress between 0 and 1
        progress = max(0.0, min(1.0, progress))
        
        # If progress is 1.0, mark as completed
        if progress >= 1.0:
            cursor.execute("""
                UPDATE learning_objectives
                SET progress = ?, status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (progress, objective_id))
        else:
            cursor.execute("""
                UPDATE learning_objectives
                SET progress = ?
                WHERE id = ?
            """, (progress, objective_id))
        
        conn.commit()
        conn.close()
    
    def get_active_objectives(self) -> List[Dict[str, Any]]:
        """Get all active learning objectives"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, objective_type, objective_name, description, priority, progress, created_at
            FROM learning_objectives
            WHERE status = 'active'
            ORDER BY priority DESC, created_at ASC
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        objectives = []
        for row in results:
            objectives.append({
                "id": row[0],
                "objective_type": row[1],
                "objective_name": row[2],
                "description": row[3],
                "priority": row[4],
                "progress": row[5],
                "created_at": row[6]
            })
        
        return objectives
    
    def generate_daily_learning_plan(self) -> Dict[str, Any]:
        """
        Generate a daily learning plan based on objectives and research topics.
        
        Returns:
            Dictionary with learning plan
        """
        objectives = self.get_active_objectives()
        research_topics = self.research.get_priority_research_topics(limit=5)
        
        plan = {
            "date": datetime.now().isoformat(),
            "priority_objectives": [],
            "research_topics": [],
            "estimated_time_hours": 0
        }
        
        # Add top 3 objectives
        for obj in objectives[:3]:
            plan["priority_objectives"].append({
                "name": obj["objective_name"],
                "type": obj["objective_type"],
                "progress": obj["progress"],
                "priority": obj["priority"]
            })
            # Estimate 1-2 hours per objective
            plan["estimated_time_hours"] += 1.5
        
        # Add research topics
        for topic in research_topics:
            plan["research_topics"].append({
                "category": topic["category"],
                "topic": topic["topic_name"],
                "priority": topic["priority"]
            })
            # Estimate 30 minutes per research topic
            plan["estimated_time_hours"] += 0.5
        
        return plan


class TrendAnalyzer:
    """
    Analyzes trends in tools, technologies, and methodologies.
    """
    
    def __init__(self, db_path: str = "data/vy_nexus.db"):
        self.db_path = db_path
    
    def analyze_tool_usage_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze which tools are being used most frequently.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dictionary with trend analysis
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Check if interactions table exists and has tool_used column
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='interactions'
        """)
        
        if not cursor.fetchone():
            conn.close()
            return {"status": "no_data", "message": "No interaction data available"}
        
        # Get tool usage from metadata
        cursor.execute("""
            SELECT metadata FROM interactions
            WHERE timestamp > ? AND metadata IS NOT NULL
        """, (cutoff_date,))
        
        tool_usage = Counter()
        for row in cursor.fetchall():
            try:
                metadata = json.loads(row[0])
                if 'tool_used' in metadata:
                    tool_usage[metadata['tool_used']] += 1
            except (json.JSONDecodeError, KeyError):
                continue
        
        conn.close()
        
        if not tool_usage:
            return {"status": "no_data", "message": "No tool usage data found"}
        
        # Get top tools
        top_tools = tool_usage.most_common(10)
        
        return {
            "status": "success",
            "period_days": days,
            "top_tools": [{"tool": tool, "usage_count": count} for tool, count in top_tools],
            "total_tools_used": len(tool_usage),
            "total_usage_events": sum(tool_usage.values())
        }
    
    def identify_knowledge_gaps(self) -> List[Dict[str, Any]]:
        """
        Identify areas where knowledge is lacking or confidence is low.
        
        Returns:
            List of knowledge gaps
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find topics with low confidence or few entries
        cursor.execute("""
            SELECT category, topic, AVG(confidence_score) as avg_confidence, COUNT(*) as entry_count
            FROM knowledge_base
            GROUP BY category, topic
            HAVING avg_confidence < 0.6 OR entry_count < 3
            ORDER BY avg_confidence ASC, entry_count ASC
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        gaps = []
        for row in results:
            gaps.append({
                "category": row[0],
                "topic": row[1],
                "avg_confidence": row[2],
                "entry_count": row[3],
                "gap_type": "low_confidence" if row[2] < 0.6 else "insufficient_data"
            })
        
        return gaps


if __name__ == "__main__":
    # Example usage
    research = ResearchAutomation()
    
    # Add research topics
    topic_id = research.add_research_topic(
        ResearchTopic.TOOLS,
        "AI Code Assistants",
        priority=8,
        metadata={"reason": "Improve development efficiency"}
    )
    
    # Record a finding
    research.record_finding(
        topic_id,
        "tool",
        "GitHub Copilot",
        "AI-powered code completion tool that suggests code based on context",
        source="GitHub",
        relevance_score=0.9
    )
    
    # Add to knowledge base
    research.add_to_knowledge_base(
        "tools",
        "AI Code Assistants",
        "GitHub Copilot uses OpenAI Codex to suggest code completions. Best for: Python, JavaScript, TypeScript.",
        confidence_score=0.8,
        tags=["ai", "coding", "productivity"]
    )
    
    print("Research automation example completed successfully!")
