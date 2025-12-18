"""\nKnowledge Base System for Self-Evolving AI Ecosystem\nFacilitates continuous knowledge acquisition and easy updating\n"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from collections import defaultdict
import hashlib
import re


class KnowledgeBase:
    """\n    Self-evolving knowledge base that continuously acquires and updates knowledge.\n    Supports patterns, learnings, optimizations, and workflows with versioning.\n    """
    
    def __init__(self, db_path: str = "/Users/lordwilson/vy-nexus/data/knowledge_base.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize knowledge base database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Knowledge entries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                source TEXT,
                tags TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                last_accessed TEXT,
                version INTEGER DEFAULT 1
            )
        ''')
        
        # Knowledge relationships table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_entry_id TEXT NOT NULL,
                to_entry_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                strength REAL DEFAULT 1.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(from_entry_id, to_entry_id, relationship_type)
            )
        ''')
        
        # Knowledge evolution history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_evolution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id TEXT NOT NULL,
                evolution_type TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                reason TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Knowledge validation table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_validation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id TEXT NOT NULL,
                validation_type TEXT NOT NULL,
                result BOOLEAN NOT NULL,
                details TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entries_category ON knowledge_entries(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entries_tags ON knowledge_entries(tags)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entries_confidence ON knowledge_entries(confidence)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_from ON knowledge_relationships(from_entry_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_to ON knowledge_relationships(to_entry_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_evolution_entry ON knowledge_evolution(entry_id)')
        
        conn.commit()
        conn.close()
    
    def _generate_entry_id(self, category: str, title: str) -> str:
        """Generate unique entry ID"""
        content = f"{category}_{title}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    # ==================== Knowledge Entry Management ====================
    
    def add_knowledge(self, category: str, title: str, content: str,
                     subcategory: Optional[str] = None,
                     confidence: float = 1.0,
                     source: Optional[str] = None,
                     tags: Optional[List[str]] = None,
                     metadata: Optional[Dict] = None) -> str:
        """\n        Add new knowledge entry.\n        \n        Args:\n            category: Knowledge category (patterns, learnings, optimizations, workflows)\n            title: Entry title\n            content: Entry content\n            subcategory: Optional subcategory\n            confidence: Confidence score (0.0 to 1.0)\n            source: Source of knowledge\n            tags: List of tags\n            metadata: Additional metadata\n        \n        Returns:\n            Entry ID\n        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        entry_id = self._generate_entry_id(category, title)
        tags_str = json.dumps(tags or [])
        
        cursor.execute('''
            INSERT OR REPLACE INTO knowledge_entries 
            (entry_id, category, subcategory, title, content, confidence, source, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (entry_id, category, subcategory, title, content, confidence, source, tags_str))
        
        # Record evolution
        cursor.execute('''
            INSERT INTO knowledge_evolution (entry_id, evolution_type, new_value, reason)
            VALUES (?, ?, ?, ?)
        ''', (entry_id, 'created', content, 'Initial knowledge entry'))
        
        conn.commit()
        conn.close()
        
        return entry_id
    
    def update_knowledge(self, entry_id: str, content: Optional[str] = None,
                        confidence: Optional[float] = None,
                        tags: Optional[List[str]] = None,
                        reason: str = "Knowledge update") -> bool:
        """\n        Update existing knowledge entry.\n        \n        Args:\n            entry_id: Entry ID to update\n            content: New content (if updating)\n            confidence: New confidence score (if updating)\n            tags: New tags (if updating)\n            reason: Reason for update\n        \n        Returns:\n            True if successful\n        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current values
        cursor.execute('SELECT content, confidence, tags FROM knowledge_entries WHERE entry_id = ?', (entry_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False
        
        old_content, old_confidence, old_tags = row
        
        # Update fields
        updates = []
        params = []
        
        if content is not None:
            updates.append('content = ?')
            params.append(content)
            # Record evolution
            cursor.execute('''
                INSERT INTO knowledge_evolution (entry_id, evolution_type, old_value, new_value, reason)
                VALUES (?, ?, ?, ?, ?)
            ''', (entry_id, 'content_update', old_content, content, reason))
        
        if confidence is not None:
            updates.append('confidence = ?')
            params.append(confidence)
            # Record evolution
            cursor.execute('''
                INSERT INTO knowledge_evolution (entry_id, evolution_type, old_value, new_value, reason)
                VALUES (?, ?, ?, ?, ?)
            ''', (entry_id, 'confidence_update', str(old_confidence), str(confidence), reason))
        
        if tags is not None:
            updates.append('tags = ?')
            params.append(json.dumps(tags))
        
        if updates:
            updates.append('updated_at = ?')
            params.append(datetime.now().isoformat())
            
            updates.append('version = version + 1')
            
            params.append(entry_id)
            
            query = f"UPDATE knowledge_entries SET {', '.join(updates)} WHERE entry_id = ?"
            cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_knowledge(self, entry_id: str, track_access: bool = True) -> Optional[Dict[str, Any]]:
        """\n        Retrieve knowledge entry by ID.\n        \n        Args:\n            entry_id: Entry ID\n            track_access: Whether to track access for analytics\n        \n        Returns:\n            Knowledge entry dictionary or None\n        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM knowledge_entries WHERE entry_id = ?', (entry_id,))
        row = cursor.fetchone()
        
        if row:
            if track_access:
                # Update access tracking
                cursor.execute('''
                    UPDATE knowledge_entries 
                    SET access_count = access_count + 1, last_accessed = ?
                    WHERE entry_id = ?
                ''', (datetime.now().isoformat(), entry_id))
                conn.commit()
            
            entry = {
                'entry_id': row['entry_id'],
                'category': row['category'],
                'subcategory': row['subcategory'],
                'title': row['title'],
                'content': row['content'],
                'confidence': row['confidence'],
                'source': row['source'],
                'tags': json.loads(row['tags']) if row['tags'] else [],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'access_count': row['access_count'],
                'last_accessed': row['last_accessed'],
                'version': row['version']
            }
            
            conn.close()
            return entry
        
        conn.close()
        return None
    
    def search_knowledge(self, query: Optional[str] = None,
                        category: Optional[str] = None,
                        subcategory: Optional[str] = None,
                        tags: Optional[List[str]] = None,
                        min_confidence: float = 0.0,
                        limit: int = 100) -> List[Dict[str, Any]]:
        """\n        Search knowledge base with filters.\n        \n        Args:\n            query: Text search query\n            category: Filter by category\n            subcategory: Filter by subcategory\n            tags: Filter by tags\n            min_confidence: Minimum confidence threshold\n            limit: Maximum results\n        \n        Returns:\n            List of matching knowledge entries\n        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        sql = "SELECT * FROM knowledge_entries WHERE confidence >= ?"
        params = [min_confidence]
        
        if category:
            sql += " AND category = ?"
            params.append(category)
        
        if subcategory:
            sql += " AND subcategory = ?"
            params.append(subcategory)
        
        if query:
            sql += " AND (title LIKE ? OR content LIKE ?)"
            search_term = f"%{query}%"
            params.extend([search_term, search_term])
        
        if tags:
            # Search for any of the tags
            tag_conditions = []
            for tag in tags:
                tag_conditions.append("tags LIKE ?")
                params.append(f'%"{tag}"%')
            sql += f" AND ({' OR '.join(tag_conditions)})"
        
        sql += " ORDER BY confidence DESC, access_count DESC, updated_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                'entry_id': row['entry_id'],
                'category': row['category'],
                'subcategory': row['subcategory'],
                'title': row['title'],
                'content': row['content'],
                'confidence': row['confidence'],
                'source': row['source'],
                'tags': json.loads(row['tags']) if row['tags'] else [],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'access_count': row['access_count'],
                'version': row['version']
            })
        
        conn.close()
        return results
    
    # ==================== Knowledge Relationships ====================
    
    def add_relationship(self, from_entry_id: str, to_entry_id: str,
                        relationship_type: str, strength: float = 1.0) -> bool:
        """\n        Add relationship between knowledge entries.\n        \n        Args:\n            from_entry_id: Source entry ID\n            to_entry_id: Target entry ID\n            relationship_type: Type of relationship (related_to, depends_on, improves, etc.)\n            strength: Relationship strength (0.0 to 1.0)\n        \n        Returns:\n            True if successful\n        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO knowledge_relationships 
            (from_entry_id, to_entry_id, relationship_type, strength)
            VALUES (?, ?, ?, ?)
        ''', (from_entry_id, to_entry_id, relationship_type, strength))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_related_knowledge(self, entry_id: str, 
                             relationship_type: Optional[str] = None,
                             min_strength: float = 0.0) -> List[Dict[str, Any]]:
        """\n        Get knowledge entries related to a given entry.\n        \n        Args:\n            entry_id: Entry ID\n            relationship_type: Filter by relationship type\n            min_strength: Minimum relationship strength\n        \n        Returns:\n            List of related knowledge entries\n        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        sql = '''
            SELECT e.*, r.relationship_type, r.strength
            FROM knowledge_entries e
            JOIN knowledge_relationships r ON e.entry_id = r.to_entry_id
            WHERE r.from_entry_id = ? AND r.strength >= ?
        '''
        params = [entry_id, min_strength]
        
        if relationship_type:
            sql += " AND r.relationship_type = ?"
            params.append(relationship_type)
        
        sql += " ORDER BY r.strength DESC"
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                'entry_id': row['entry_id'],
                'category': row['category'],
                'title': row['title'],
                'content': row['content'],
                'confidence': row['confidence'],
                'relationship_type': row['relationship_type'],
                'relationship_strength': row['strength']
            })
        
        conn.close()
        return results
    
    # ==================== Knowledge Validation ====================
    
    def validate_knowledge(self, entry_id: str, validation_type: str,
                          result: bool, details: Optional[str] = None) -> bool:
        """\n        Record knowledge validation result.\n        \n        Args:\n            entry_id: Entry ID\n            validation_type: Type of validation\n            result: Validation result (True/False)\n            details: Optional validation details\n        \n        Returns:\n            True if successful\n        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO knowledge_validation (entry_id, validation_type, result, details)
            VALUES (?, ?, ?, ?)
        ''', (entry_id, validation_type, result, details))
        
        # If validation failed, reduce confidence
        if not result:
            cursor.execute('''
                UPDATE knowledge_entries 
                SET confidence = confidence * 0.9
                WHERE entry_id = ?
            ''', (entry_id,))
        
        conn.commit()
        conn.close()
        
        return True
    
    # ==================== Knowledge Analytics ====================
    
    def get_knowledge_stats(self, category: Optional[str] = None) -> Dict[str, Any]:
        """\n        Get knowledge base statistics.\n        \n        Args:\n            category: Optional category filter\n        \n        Returns:\n            Statistics dictionary\n        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total entries
        if category:
            cursor.execute('SELECT COUNT(*) FROM knowledge_entries WHERE category = ?', (category,))
        else:
            cursor.execute('SELECT COUNT(*) FROM knowledge_entries')
        stats['total_entries'] = cursor.fetchone()[0]
        
        # Entries by category
        cursor.execute('SELECT category, COUNT(*) FROM knowledge_entries GROUP BY category')
        stats['by_category'] = dict(cursor.fetchall())
        
        # Average confidence
        if category:
            cursor.execute('SELECT AVG(confidence) FROM knowledge_entries WHERE category = ?', (category,))
        else:
            cursor.execute('SELECT AVG(confidence) FROM knowledge_entries')
        stats['avg_confidence'] = cursor.fetchone()[0] or 0.0
        
        # Most accessed
        cursor.execute('''
            SELECT entry_id, title, access_count 
            FROM knowledge_entries 
            ORDER BY access_count DESC 
            LIMIT 10
        ''')
        stats['most_accessed'] = [
            {'entry_id': row[0], 'title': row[1], 'access_count': row[2]}
            for row in cursor.fetchall()
        ]
        
        # Recent updates
        cursor.execute('''
            SELECT entry_id, title, updated_at 
            FROM knowledge_entries 
            ORDER BY updated_at DESC 
            LIMIT 10
        ''')
        stats['recent_updates'] = [
            {'entry_id': row[0], 'title': row[1], 'updated_at': row[2]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return stats
    
    def get_evolution_history(self, entry_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """\n        Get evolution history for a knowledge entry.\n        \n        Args:\n            entry_id: Entry ID\n            limit: Maximum history entries\n        \n        Returns:\n            List of evolution events\n        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM knowledge_evolution 
            WHERE entry_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (entry_id, limit))
        
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            history.append({
                'evolution_type': row['evolution_type'],
                'old_value': row['old_value'],
                'new_value': row['new_value'],
                'reason': row['reason'],
                'timestamp': row['timestamp']
            })
        
        conn.close()
        return history


# Global knowledge base instance
_global_kb = None

def get_knowledge_base() -> KnowledgeBase:
    """Get the global knowledge base instance"""
    global _global_kb
    if _global_kb is None:
        _global_kb = KnowledgeBase()
    return _global_kb


if __name__ == "__main__":
    # Test the knowledge base
    kb = get_knowledge_base()
    
    # Add knowledge entries
    pattern_id = kb.add_knowledge(
        category="patterns",
        title="User prefers morning tasks",
        content="User consistently completes high-priority tasks in the morning (6-10 AM) with 90% success rate.",
        subcategory="user_behavior",
        confidence=0.9,
        source="interaction_analysis",
        tags=["productivity", "timing", "user_preference"]
    )
    
    optimization_id = kb.add_knowledge(
        category="optimizations",
        title="Priority queue scheduling",
        content="Using priority queue algorithm reduced task completion time by 15%.",
        subcategory="task_scheduling",
        confidence=0.95,
        source="performance_testing",
        tags=["scheduling", "performance", "algorithm"]
    )
    
    # Add relationship
    kb.add_relationship(pattern_id, optimization_id, "improves", strength=0.8)
    
    # Search knowledge
    results = kb.search_knowledge(query="morning", min_confidence=0.7)
    print(f"Found {len(results)} knowledge entries")
    
    # Get stats
    stats = kb.get_knowledge_stats()
    print(f"\nKnowledge Base Stats:")
    print(f"Total entries: {stats['total_entries']}")
    print(f"Average confidence: {stats['avg_confidence']:.2f}")
    
    print("\n✅ Knowledge base test complete!")
