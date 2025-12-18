"""
Dynamic Knowledge Base Updater Module

This module manages a dynamic knowledge base that continuously learns and updates
from user interactions, task completions, and external sources.

Features:
- Store and retrieve knowledge entries
- Automatic knowledge extraction from interactions
- Knowledge relevance scoring and ranking
- Knowledge deprecation and updates
- Context-aware knowledge retrieval
- Knowledge graph relationships

Author: Vy Self-Evolving AI Ecosystem
Phase: 4 - Real-Time Adaptation System
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import re


class KnowledgeType(Enum):
    """Types of knowledge entries"""
    FACT = "fact"
    PROCEDURE = "procedure"
    PREFERENCE = "preference"
    PATTERN = "pattern"
    INSIGHT = "insight"
    RULE = "rule"
    EXAMPLE = "example"


class KnowledgeStatus(Enum):
    """Status of knowledge entries"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    PENDING_VERIFICATION = "pending_verification"
    ARCHIVED = "archived"


@dataclass
class KnowledgeEntry:
    """Knowledge base entry"""
    entry_id: str
    knowledge_type: str
    title: str
    content: str
    context: str
    tags: List[str]
    relevance_score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    source: str
    created_at: str
    updated_at: str
    last_accessed: str
    access_count: int
    status: str
    related_entries: List[str]  # entry_ids
    metadata: Dict


@dataclass
class KnowledgeQuery:
    """Query for knowledge retrieval"""
    query_text: str
    context: Optional[str]
    knowledge_types: Optional[List[str]]
    min_relevance: float
    max_results: int


@dataclass
class KnowledgeUpdate:
    """Update to existing knowledge"""
    entry_id: str
    update_type: str  # refinement, correction, expansion
    new_content: Optional[str]
    new_relevance: Optional[float]
    new_confidence: Optional[float]
    reason: str
    updated_by: str
    timestamp: str


class KnowledgeExtractor:
    """Extracts knowledge from various sources"""
    
    def __init__(self):
        self.extraction_patterns = {
            'fact': r'(?:is|are|was|were)\s+(.+?)(?:\.|$)',
            'procedure': r'(?:to|how to)\s+(.+?)(?:,|\.|$)',
            'preference': r'(?:prefer|like|want)\s+(.+?)(?:\.|$)',
            'rule': r'(?:always|never|must|should)\s+(.+?)(?:\.|$)'
        }
    
    def extract_from_text(self, text: str, context: str = "general") -> List[Dict]:
        """Extract knowledge from text"""
        extracted = []
        
        # Extract facts
        facts = re.findall(self.extraction_patterns['fact'], text, re.IGNORECASE)
        for fact in facts:
            if len(fact.strip()) > 5:  # Minimum length
                extracted.append({
                    'type': KnowledgeType.FACT.value,
                    'content': fact.strip(),
                    'context': context,
                    'confidence': 0.7
                })
        
        # Extract procedures
        procedures = re.findall(self.extraction_patterns['procedure'], text, re.IGNORECASE)
        for proc in procedures:
            if len(proc.strip()) > 5:
                extracted.append({
                    'type': KnowledgeType.PROCEDURE.value,
                    'content': proc.strip(),
                    'context': context,
                    'confidence': 0.8
                })
        
        # Extract preferences
        preferences = re.findall(self.extraction_patterns['preference'], text, re.IGNORECASE)
        for pref in preferences:
            if len(pref.strip()) > 5:
                extracted.append({
                    'type': KnowledgeType.PREFERENCE.value,
                    'content': pref.strip(),
                    'context': context,
                    'confidence': 0.9
                })
        
        # Extract rules
        rules = re.findall(self.extraction_patterns['rule'], text, re.IGNORECASE)
        for rule in rules:
            if len(rule.strip()) > 5:
                extracted.append({
                    'type': KnowledgeType.RULE.value,
                    'content': rule.strip(),
                    'context': context,
                    'confidence': 0.85
                })
        
        return extracted
    
    def extract_from_interaction(self, interaction_data: Dict) -> List[Dict]:
        """Extract knowledge from user interaction"""
        extracted = []
        
        if 'user_message' in interaction_data:
            text_extracts = self.extract_from_text(
                interaction_data['user_message'],
                interaction_data.get('context', 'general')
            )
            extracted.extend(text_extracts)
        
        # Extract patterns from successful completions
        if interaction_data.get('success', False):
            extracted.append({
                'type': KnowledgeType.PATTERN.value,
                'content': f"Successful pattern: {interaction_data.get('action', 'unknown')}",
                'context': interaction_data.get('context', 'general'),
                'confidence': 0.75
            })
        
        return extracted
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for tagging"""
        # Simple keyword extraction - remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                       'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were'}
        
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if w not in common_words and len(w) > 3]
        
        # Return unique keywords, limited to top 10 by frequency
        from collections import Counter
        keyword_counts = Counter(keywords)
        return [k for k, _ in keyword_counts.most_common(10)]


class KnowledgeBaseManager:
    """Manages the knowledge base"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.extractor = KnowledgeExtractor()
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Knowledge entries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_entries (
                entry_id TEXT PRIMARY KEY,
                knowledge_type TEXT,
                title TEXT,
                content TEXT,
                context TEXT,
                tags TEXT,
                relevance_score REAL,
                confidence REAL,
                source TEXT,
                created_at TEXT,
                updated_at TEXT,
                last_accessed TEXT,
                access_count INTEGER,
                status TEXT,
                related_entries TEXT,
                metadata TEXT
            )
        ''')
        
        # Knowledge updates history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_updates (
                update_id TEXT PRIMARY KEY,
                entry_id TEXT,
                update_type TEXT,
                new_content TEXT,
                new_relevance REAL,
                new_confidence REAL,
                reason TEXT,
                updated_by TEXT,
                timestamp TEXT
            )
        ''')
        
        # Knowledge relationships
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_relationships (
                relationship_id TEXT PRIMARY KEY,
                entry_id_1 TEXT,
                entry_id_2 TEXT,
                relationship_type TEXT,
                strength REAL,
                created_at TEXT
            )
        ''')
        
        # Knowledge access log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_access_log (
                log_id TEXT PRIMARY KEY,
                entry_id TEXT,
                accessed_by TEXT,
                query_context TEXT,
                relevance_at_access REAL,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_entry(self, entry: KnowledgeEntry) -> str:
        """Add new knowledge entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO knowledge_entries
            (entry_id, knowledge_type, title, content, context, tags,
             relevance_score, confidence, source, created_at, updated_at,
             last_accessed, access_count, status, related_entries, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry.entry_id, entry.knowledge_type, entry.title, entry.content,
            entry.context, json.dumps(entry.tags), entry.relevance_score,
            entry.confidence, entry.source, entry.created_at, entry.updated_at,
            entry.last_accessed, entry.access_count, entry.status,
            json.dumps(entry.related_entries), json.dumps(entry.metadata)
        ))
        
        conn.commit()
        conn.close()
        
        return entry.entry_id
    
    def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Retrieve knowledge entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM knowledge_entries WHERE entry_id = ?', (entry_id,))
        row = cursor.fetchone()
        
        # Update access count and last accessed
        if row:
            cursor.execute('''
                UPDATE knowledge_entries
                SET access_count = access_count + 1,
                    last_accessed = ?
                WHERE entry_id = ?
            ''', (datetime.now().isoformat(), entry_id))
            conn.commit()
        
        conn.close()
        
        if row:
            return KnowledgeEntry(
                entry_id=row[0], knowledge_type=row[1], title=row[2],
                content=row[3], context=row[4], tags=json.loads(row[5]),
                relevance_score=row[6], confidence=row[7], source=row[8],
                created_at=row[9], updated_at=row[10], last_accessed=row[11],
                access_count=row[12], status=row[13],
                related_entries=json.loads(row[14]), metadata=json.loads(row[15])
            )
        return None
    
    def search_knowledge(self, query: KnowledgeQuery) -> List[KnowledgeEntry]:
        """Search knowledge base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query
        sql = 'SELECT * FROM knowledge_entries WHERE status = ? AND relevance_score >= ?'
        params = [KnowledgeStatus.ACTIVE.value, query.min_relevance]
        
        if query.context:
            sql += ' AND context = ?'
            params.append(query.context)
        
        if query.knowledge_types:
            placeholders = ','.join(['?'] * len(query.knowledge_types))
            sql += f' AND knowledge_type IN ({placeholders})'
            params.extend(query.knowledge_types)
        
        # Search in content and title
        sql += ' AND (content LIKE ? OR title LIKE ?)'
        search_term = f'%{query.query_text}%'
        params.extend([search_term, search_term])
        
        sql += ' ORDER BY relevance_score DESC, access_count DESC LIMIT ?'
        params.append(query.max_results)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            entry = KnowledgeEntry(
                entry_id=row[0], knowledge_type=row[1], title=row[2],
                content=row[3], context=row[4], tags=json.loads(row[5]),
                relevance_score=row[6], confidence=row[7], source=row[8],
                created_at=row[9], updated_at=row[10], last_accessed=row[11],
                access_count=row[12], status=row[13],
                related_entries=json.loads(row[14]), metadata=json.loads(row[15])
            )
            results.append(entry)
            
            # Log access
            self._log_access(entry.entry_id, query.query_text, query.context or "general")
        
        return results
    
    def update_entry(self, update: KnowledgeUpdate):
        """Update existing knowledge entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Record update in history
        update_id = f"upd_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        cursor.execute('''
            INSERT INTO knowledge_updates
            (update_id, entry_id, update_type, new_content, new_relevance,
             new_confidence, reason, updated_by, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            update_id, update.entry_id, update.update_type, update.new_content,
            update.new_relevance, update.new_confidence, update.reason,
            update.updated_by, update.timestamp
        ))
        
        # Apply updates to entry
        updates = []
        params = []
        
        if update.new_content:
            updates.append('content = ?')
            params.append(update.new_content)
        
        if update.new_relevance is not None:
            updates.append('relevance_score = ?')
            params.append(update.new_relevance)
        
        if update.new_confidence is not None:
            updates.append('confidence = ?')
            params.append(update.new_confidence)
        
        updates.append('updated_at = ?')
        params.append(datetime.now().isoformat())
        
        params.append(update.entry_id)
        
        if updates:
            sql = f"UPDATE knowledge_entries SET {', '.join(updates)} WHERE entry_id = ?"
            cursor.execute(sql, params)
        
        conn.commit()
        conn.close()
    
    def deprecate_entry(self, entry_id: str, reason: str):
        """Mark entry as deprecated"""
        update = KnowledgeUpdate(
            entry_id=entry_id,
            update_type="deprecation",
            new_content=None,
            new_relevance=0.0,
            new_confidence=None,
            reason=reason,
            updated_by="system",
            timestamp=datetime.now().isoformat()
        )
        
        self.update_entry(update)
        
        # Update status
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE knowledge_entries SET status = ? WHERE entry_id = ?',
            (KnowledgeStatus.DEPRECATED.value, entry_id)
        )
        conn.commit()
        conn.close()
    
    def _log_access(self, entry_id: str, query: str, context: str):
        """Log knowledge access"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        log_id = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Get current relevance
        cursor.execute('SELECT relevance_score FROM knowledge_entries WHERE entry_id = ?',
                      (entry_id,))
        result = cursor.fetchone()
        relevance = result[0] if result else 0.0
        
        cursor.execute('''
            INSERT INTO knowledge_access_log
            (log_id, entry_id, accessed_by, query_context, relevance_at_access, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (log_id, entry_id, "user", context, relevance, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def create_relationship(self, entry_id_1: str, entry_id_2: str,
                          relationship_type: str, strength: float = 0.5):
        """Create relationship between knowledge entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        relationship_id = f"rel_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        cursor.execute('''
            INSERT INTO knowledge_relationships
            (relationship_id, entry_id_1, entry_id_2, relationship_type, strength, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (relationship_id, entry_id_1, entry_id_2, relationship_type,
              strength, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_related_entries(self, entry_id: str, min_strength: float = 0.3) -> List[str]:
        """Get related knowledge entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT entry_id_2, strength FROM knowledge_relationships
            WHERE entry_id_1 = ? AND strength >= ?
            UNION
            SELECT entry_id_1, strength FROM knowledge_relationships
            WHERE entry_id_2 = ? AND strength >= ?
            ORDER BY strength DESC
        ''', (entry_id, min_strength, entry_id, min_strength))
        
        related = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return related


class DynamicKnowledgeUpdater:
    """Automatically updates knowledge base from various sources"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.manager = KnowledgeBaseManager(db_path)
        self.extractor = KnowledgeExtractor()
    
    def process_interaction(self, interaction_data: Dict) -> List[str]:
        """Process interaction and extract knowledge"""
        extracted = self.extractor.extract_from_interaction(interaction_data)
        
        added_entries = []
        for item in extracted:
            # Check if similar knowledge exists
            existing = self._find_similar_entry(item['content'], item['context'])
            
            if existing:
                # Update existing entry
                self._update_existing_entry(existing, item)
            else:
                # Create new entry
                entry_id = self._create_new_entry(item, interaction_data)
                added_entries.append(entry_id)
        
        return added_entries
    
    def _find_similar_entry(self, content: str, context: str) -> Optional[KnowledgeEntry]:
        """Find similar existing entry"""
        query = KnowledgeQuery(
            query_text=content[:50],  # Use first 50 chars
            context=context,
            knowledge_types=None,
            min_relevance=0.5,
            max_results=1
        )
        
        results = self.manager.search_knowledge(query)
        return results[0] if results else None
    
    def _create_new_entry(self, item: Dict, source_data: Dict) -> str:
        """Create new knowledge entry"""
        entry_id = f"kb_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Extract keywords for tags
        tags = self.extractor.extract_keywords(item['content'])
        
        entry = KnowledgeEntry(
            entry_id=entry_id,
            knowledge_type=item['type'],
            title=item['content'][:100],  # First 100 chars as title
            content=item['content'],
            context=item['context'],
            tags=tags,
            relevance_score=0.7,  # Initial relevance
            confidence=item.get('confidence', 0.7),
            source=source_data.get('source', 'interaction'),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            last_accessed=datetime.now().isoformat(),
            access_count=0,
            status=KnowledgeStatus.ACTIVE.value,
            related_entries=[],
            metadata=source_data
        )
        
        self.manager.add_entry(entry)
        return entry_id
    
    def _update_existing_entry(self, entry: KnowledgeEntry, new_item: Dict):
        """Update existing entry with new information"""
        # Increase confidence if information is reinforced
        new_confidence = min(1.0, entry.confidence + 0.05)
        
        update = KnowledgeUpdate(
            entry_id=entry.entry_id,
            update_type="refinement",
            new_content=None,
            new_relevance=None,
            new_confidence=new_confidence,
            reason="Reinforced by new interaction",
            updated_by="system",
            timestamp=datetime.now().isoformat()
        )
        
        self.manager.update_entry(update)
    
    def auto_deprecate_stale_knowledge(self, days_threshold: int = 90):
        """Automatically deprecate knowledge that hasn't been accessed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days_threshold)).isoformat()
        
        cursor.execute('''
            SELECT entry_id FROM knowledge_entries
            WHERE last_accessed < ? AND status = ?
        ''', (cutoff_date, KnowledgeStatus.ACTIVE.value))
        
        stale_entries = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        for entry_id in stale_entries:
            self.manager.deprecate_entry(
                entry_id,
                f"Not accessed for {days_threshold} days"
            )
        
        return len(stale_entries)
    
    def get_knowledge_statistics(self) -> Dict:
        """Get statistics about knowledge base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total entries by type
        cursor.execute('''
            SELECT knowledge_type, COUNT(*), AVG(confidence), AVG(relevance_score)
            FROM knowledge_entries
            WHERE status = ?
            GROUP BY knowledge_type
        ''', (KnowledgeStatus.ACTIVE.value,))
        
        type_stats = {}
        for row in cursor.fetchall():
            type_stats[row[0]] = {
                'count': row[1],
                'avg_confidence': row[2],
                'avg_relevance': row[3]
            }
        
        # Total entries
        cursor.execute('SELECT COUNT(*) FROM knowledge_entries WHERE status = ?',
                      (KnowledgeStatus.ACTIVE.value,))
        total_active = cursor.fetchone()[0]
        
        # Most accessed
        cursor.execute('''
            SELECT entry_id, title, access_count
            FROM knowledge_entries
            WHERE status = ?
            ORDER BY access_count DESC
            LIMIT 10
        ''', (KnowledgeStatus.ACTIVE.value,))
        
        most_accessed = [{'entry_id': row[0], 'title': row[1], 'count': row[2]}
                        for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'total_active_entries': total_active,
            'entries_by_type': type_stats,
            'most_accessed': most_accessed,
            'generated_at': datetime.now().isoformat()
        }


# Example usage
if __name__ == "__main__":
    # Initialize updater
    updater = DynamicKnowledgeUpdater("test_knowledge.db")
    
    # Process sample interaction
    interaction = {
        'user_message': 'I prefer to use Python for data analysis. The pandas library is very useful.',
        'context': 'programming',
        'success': True,
        'action': 'data_analysis',
        'source': 'user_interaction'
    }
    
    added = updater.process_interaction(interaction)
    print(f"Added {len(added)} knowledge entries")
    
    # Search knowledge
    query = KnowledgeQuery(
        query_text="Python",
        context="programming",
        knowledge_types=None,
        min_relevance=0.5,
        max_results=5
    )
    
    results = updater.manager.search_knowledge(query)
    print(f"\nFound {len(results)} results for 'Python'")
    for result in results:
        print(f"- {result.title} (confidence: {result.confidence:.2f})")
    
    # Get statistics
    stats = updater.get_knowledge_statistics()
    print(f"\nKnowledge Base Statistics:")
    print(f"Total active entries: {stats['total_active_entries']}")
    print(f"Entries by type: {stats['entries_by_type']}")
