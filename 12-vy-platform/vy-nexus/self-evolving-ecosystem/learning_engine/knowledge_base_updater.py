#!/usr/bin/env python3
"""
Knowledge Base Updater
Automatically updates and maintains the knowledge base with new discoveries
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict, field
from pathlib import Path
from collections import defaultdict
import hashlib

@dataclass
class KnowledgeEntry:
    """Represents a knowledge base entry"""
    id: str
    title: str
    content: str
    category: str
    tags: List[str]
    source: str  # user_input, research, experimentation, observation
    created_at: str
    updated_at: str
    confidence: float = 0.8  # 0-1
    verified: bool = False
    verification_count: int = 0
    usage_count: int = 0
    last_used: Optional[str] = None
    related_entries: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: int = 1

@dataclass
class KnowledgeUpdate:
    """Represents an update to the knowledge base"""
    timestamp: str
    update_type: str  # add, modify, verify, deprecate, link
    entry_id: str
    changes: Dict[str, Any]
    reason: str
    source: str

class KnowledgeBaseUpdater:
    """Manages knowledge base updates and maintenance"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_dir = Path("/Users/lordwilson/vy-nexus/self-evolving-ecosystem/data/knowledge_base")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.entries_file = self.base_dir / "entries.jsonl"
        self.updates_file = self.base_dir / "updates.jsonl"
        self.index_file = self.base_dir / "index.json"
        self.categories_file = self.base_dir / "categories.json"
        
        self.entries: Dict[str, KnowledgeEntry] = {}
        self.category_index: Dict[str, List[str]] = defaultdict(list)
        self.tag_index: Dict[str, List[str]] = defaultdict(list)
        
        self.load_knowledge_base()
        
        self._initialized = True
    
    def load_knowledge_base(self):
        """Load knowledge base from storage"""
        if self.entries_file.exists():
            with open(self.entries_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        # Handle default factory fields
                        if 'related_entries' not in data:
                            data['related_entries'] = []
                        if 'metadata' not in data:
                            data['metadata'] = {}
                        entry = KnowledgeEntry(**data)
                        self.entries[entry.id] = entry
                        
                        # Update indices
                        self.category_index[entry.category].append(entry.id)
                        for tag in entry.tags:
                            self.tag_index[tag].append(entry.id)
    
    def _generate_entry_id(self, title: str, category: str) -> str:
        """Generate unique entry ID"""
        content = f"{title}_{category}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def add_entry(self, title: str, content: str, category: str,
                 tags: List[str], source: str = "user_input",
                 confidence: float = 0.8, **metadata) -> KnowledgeEntry:
        """Add new knowledge entry"""
        entry_id = self._generate_entry_id(title, category)
        
        # Check for duplicates
        existing = self._find_similar_entries(title, content)
        if existing:
            # Update existing entry instead
            return self.update_entry(
                existing[0].id,
                content=content,
                tags=list(set(existing[0].tags + tags)),
                verification_count=existing[0].verification_count + 1,
                reason="Duplicate entry merged"
            )
        
        entry = KnowledgeEntry(
            id=entry_id,
            title=title,
            content=content,
            category=category,
            tags=tags,
            source=source,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            confidence=confidence,
            metadata=metadata
        )
        
        self.entries[entry_id] = entry
        self.category_index[category].append(entry_id)
        for tag in tags:
            self.tag_index[tag].append(entry_id)
        
        self._save_entry(entry)
        self._record_update("add", entry_id, {"title": title}, "New entry added", source)
        self._update_indices()
        
        return entry
    
    def update_entry(self, entry_id: str, reason: str = "Manual update",
                    **updates) -> Optional[KnowledgeEntry]:
        """Update existing knowledge entry"""
        if entry_id not in self.entries:
            return None
        
        entry = self.entries[entry_id]
        changes = {}
        
        for key, value in updates.items():
            if hasattr(entry, key) and value is not None:
                old_value = getattr(entry, key)
                if old_value != value:
                    changes[key] = {"old": old_value, "new": value}
                    setattr(entry, key, value)
        
        if changes:
            entry.updated_at = datetime.now().isoformat()
            entry.version += 1
            
            self._save_entry(entry)
            self._record_update("modify", entry_id, changes, reason, "system")
        
        return entry
    
    def verify_entry(self, entry_id: str, verification_source: str = "system") -> bool:
        """Verify a knowledge entry"""
        if entry_id not in self.entries:
            return False
        
        entry = self.entries[entry_id]
        entry.verification_count += 1
        entry.confidence = min(1.0, entry.confidence + 0.05)
        
        if entry.verification_count >= 3 and not entry.verified:
            entry.verified = True
            entry.confidence = min(1.0, entry.confidence + 0.1)
        
        entry.updated_at = datetime.now().isoformat()
        
        self._save_entry(entry)
        self._record_update(
            "verify",
            entry_id,
            {"verification_count": entry.verification_count, "verified": entry.verified},
            f"Verified by {verification_source}",
            verification_source
        )
        
        return True
    
    def record_usage(self, entry_id: str) -> bool:
        """Record that an entry was used"""
        if entry_id not in self.entries:
            return False
        
        entry = self.entries[entry_id]
        entry.usage_count += 1
        entry.last_used = datetime.now().isoformat()
        
        # Increase confidence slightly with usage
        entry.confidence = min(1.0, entry.confidence + 0.01)
        
        self._save_entry(entry)
        return True
    
    def link_entries(self, entry_id1: str, entry_id2: str, reason: str = "") -> bool:
        """Create a link between two knowledge entries"""
        if entry_id1 not in self.entries or entry_id2 not in self.entries:
            return False
        
        entry1 = self.entries[entry_id1]
        entry2 = self.entries[entry_id2]
        
        if entry_id2 not in entry1.related_entries:
            entry1.related_entries.append(entry_id2)
            self._save_entry(entry1)
        
        if entry_id1 not in entry2.related_entries:
            entry2.related_entries.append(entry_id1)
            self._save_entry(entry2)
        
        self._record_update(
            "link",
            entry_id1,
            {"linked_to": entry_id2},
            reason or "Entries linked",
            "system"
        )
        
        return True
    
    def deprecate_entry(self, entry_id: str, reason: str) -> bool:
        """Mark an entry as deprecated"""
        if entry_id not in self.entries:
            return False
        
        entry = self.entries[entry_id]
        entry.metadata["deprecated"] = True
        entry.metadata["deprecation_reason"] = reason
        entry.metadata["deprecated_at"] = datetime.now().isoformat()
        entry.confidence = 0.0
        
        self._save_entry(entry)
        self._record_update("deprecate", entry_id, {"deprecated": True}, reason, "system")
        
        return True
    
    def search_entries(self, query: str = None, category: str = None,
                      tags: List[str] = None, min_confidence: float = 0.0,
                      verified_only: bool = False) -> List[KnowledgeEntry]:
        """Search knowledge base"""
        results = list(self.entries.values())
        
        # Filter by category
        if category:
            results = [e for e in results if e.category == category]
        
        # Filter by tags
        if tags:
            results = [e for e in results if any(tag in e.tags for tag in tags)]
        
        # Filter by confidence
        results = [e for e in results if e.confidence >= min_confidence]
        
        # Filter verified only
        if verified_only:
            results = [e for e in results if e.verified]
        
        # Filter deprecated
        results = [e for e in results if not e.metadata.get("deprecated", False)]
        
        # Text search
        if query:
            query_lower = query.lower()
            results = [
                e for e in results
                if query_lower in e.title.lower() or query_lower in e.content.lower()
            ]
        
        # Sort by confidence and usage
        results.sort(key=lambda e: (e.confidence, e.usage_count), reverse=True)
        
        return results
    
    def get_entry_by_id(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Get entry by ID"""
        return self.entries.get(entry_id)
    
    def get_related_entries(self, entry_id: str, depth: int = 1) -> List[KnowledgeEntry]:
        """Get related entries up to specified depth"""
        if entry_id not in self.entries:
            return []
        
        related = set()
        to_process = [(entry_id, 0)]
        processed = set()
        
        while to_process:
            current_id, current_depth = to_process.pop(0)
            
            if current_id in processed or current_depth > depth:
                continue
            
            processed.add(current_id)
            
            if current_id != entry_id:
                related.add(current_id)
            
            if current_depth < depth and current_id in self.entries:
                entry = self.entries[current_id]
                for related_id in entry.related_entries:
                    if related_id not in processed:
                        to_process.append((related_id, current_depth + 1))
        
        return [self.entries[eid] for eid in related if eid in self.entries]
    
    def _find_similar_entries(self, title: str, content: str) -> List[KnowledgeEntry]:
        """Find similar entries to avoid duplicates"""
        similar = []
        title_lower = title.lower()
        
        for entry in self.entries.values():
            if entry.title.lower() == title_lower:
                similar.append(entry)
            elif title_lower in entry.title.lower() or entry.title.lower() in title_lower:
                # Check content similarity (simple approach)
                content_words = set(content.lower().split())
                entry_words = set(entry.content.lower().split())
                overlap = len(content_words & entry_words)
                total = len(content_words | entry_words)
                
                if total > 0 and overlap / total > 0.7:  # 70% similarity
                    similar.append(entry)
        
        return similar
    
    def auto_discover_knowledge(self, source_data: Dict[str, Any],
                               source_type: str) -> List[KnowledgeEntry]:
        """Automatically discover and add knowledge from various sources"""
        discovered = []
        
        if source_type == "task_completion":
            # Extract knowledge from completed tasks
            if "learnings" in source_data:
                for learning in source_data["learnings"]:
                    entry = self.add_entry(
                        title=learning.get("title", "Task Learning"),
                        content=learning.get("content", ""),
                        category="task_knowledge",
                        tags=learning.get("tags", ["task", "learning"]),
                        source="task_completion",
                        confidence=0.7,
                        task_id=source_data.get("task_id")
                    )
                    discovered.append(entry)
        
        elif source_type == "user_feedback":
            # Extract knowledge from user feedback
            if "insights" in source_data:
                entry = self.add_entry(
                    title=f"User Preference: {source_data.get('aspect', 'General')}",
                    content=source_data["insights"],
                    category="user_preferences",
                    tags=["user", "preference", source_data.get("aspect", "general")],
                    source="user_feedback",
                    confidence=0.9
                )
                discovered.append(entry)
        
        elif source_type == "error_resolution":
            # Extract knowledge from error resolutions
            entry = self.add_entry(
                title=f"Error Resolution: {source_data.get('error_type', 'Unknown')}",
                content=source_data.get("resolution", ""),
                category="troubleshooting",
                tags=["error", "resolution", source_data.get("error_type", "unknown")],
                source="error_resolution",
                confidence=0.8,
                error_code=source_data.get("error_code")
            )
            discovered.append(entry)
        
        return discovered
    
    def maintain_knowledge_base(self) -> Dict[str, int]:
        """Perform maintenance on knowledge base"""
        stats = {
            "entries_reviewed": 0,
            "low_confidence_flagged": 0,
            "unused_flagged": 0,
            "links_created": 0
        }
        
        cutoff_date = datetime.now() - timedelta(days=90)
        
        for entry in self.entries.values():
            stats["entries_reviewed"] += 1
            
            # Flag low confidence entries
            if entry.confidence < 0.5 and not entry.metadata.get("low_confidence_flagged"):
                entry.metadata["low_confidence_flagged"] = True
                entry.metadata["flagged_at"] = datetime.now().isoformat()
                self._save_entry(entry)
                stats["low_confidence_flagged"] += 1
            
            # Flag unused entries
            if entry.usage_count == 0:
                created = datetime.fromisoformat(entry.created_at)
                if created < cutoff_date and not entry.metadata.get("unused_flagged"):
                    entry.metadata["unused_flagged"] = True
                    entry.metadata["flagged_at"] = datetime.now().isoformat()
                    self._save_entry(entry)
                    stats["unused_flagged"] += 1
            
            # Auto-link related entries
            for other_entry in self.entries.values():
                if entry.id != other_entry.id and other_entry.id not in entry.related_entries:
                    # Check if they share tags or category
                    shared_tags = set(entry.tags) & set(other_entry.tags)
                    if len(shared_tags) >= 2 or (entry.category == other_entry.category and shared_tags):
                        self.link_entries(entry.id, other_entry.id, "Auto-linked based on similarity")
                        stats["links_created"] += 1
        
        return stats
    
    def get_knowledge_stats(self) -> Dict:
        """Get statistics about knowledge base"""
        total = len(self.entries)
        by_category = dict(self.category_index)
        by_source = defaultdict(int)
        
        verified_count = 0
        avg_confidence = 0
        total_usage = 0
        deprecated_count = 0
        
        for entry in self.entries.values():
            by_source[entry.source] += 1
            if entry.verified:
                verified_count += 1
            avg_confidence += entry.confidence
            total_usage += entry.usage_count
            if entry.metadata.get("deprecated"):
                deprecated_count += 1
        
        if total > 0:
            avg_confidence /= total
        
        return {
            "total_entries": total,
            "by_category": {k: len(v) for k, v in by_category.items()},
            "by_source": dict(by_source),
            "verified_count": verified_count,
            "deprecated_count": deprecated_count,
            "average_confidence": round(avg_confidence, 2),
            "total_usage": total_usage,
            "total_tags": len(self.tag_index)
        }
    
    def _save_entry(self, entry: KnowledgeEntry):
        """Save entry to storage"""
        with open(self.entries_file, 'a') as f:
            f.write(json.dumps(asdict(entry)) + '\n')
    
    def _record_update(self, update_type: str, entry_id: str,
                      changes: Dict[str, Any], reason: str, source: str):
        """Record an update to the knowledge base"""
        update = KnowledgeUpdate(
            timestamp=datetime.now().isoformat(),
            update_type=update_type,
            entry_id=entry_id,
            changes=changes,
            reason=reason,
            source=source
        )
        
        with open(self.updates_file, 'a') as f:
            f.write(json.dumps(asdict(update)) + '\n')
    
    def _update_indices(self):
        """Update search indices"""
        index_data = {
            "last_updated": datetime.now().isoformat(),
            "total_entries": len(self.entries),
            "categories": {k: len(v) for k, v in self.category_index.items()},
            "tags": {k: len(v) for k, v in self.tag_index.items()}
        }
        
        with open(self.index_file, 'w') as f:
            json.dump(index_data, f, indent=2)
    
    def export_knowledge_base(self, category: str = None) -> Dict:
        """Export knowledge base"""
        entries = list(self.entries.values())
        
        if category:
            entries = [e for e in entries if e.category == category]
        
        return {
            "generated_at": datetime.now().isoformat(),
            "total_entries": len(entries),
            "entries": [asdict(e) for e in entries],
            "stats": self.get_knowledge_stats()
        }

def get_updater() -> KnowledgeBaseUpdater:
    """Get singleton instance of knowledge base updater"""
    return KnowledgeBaseUpdater()

if __name__ == "__main__":
    # Example usage
    updater = get_updater()
    
    # Add knowledge entry
    entry = updater.add_entry(
        title="Python Best Practice: Use List Comprehensions",
        content="List comprehensions are more Pythonic and often faster than traditional for loops for creating lists.",
        category="programming",
        tags=["python", "best_practice", "performance"],
        source="research",
        confidence=0.9
    )
    print(f"Added entry: {entry.title}")
    
    # Search knowledge base
    results = updater.search_entries(query="python", min_confidence=0.7)
    print(f"Found {len(results)} entries about Python")
    
    # Get stats
    stats = updater.get_knowledge_stats()
    print(f"Knowledge base stats: {stats}")
