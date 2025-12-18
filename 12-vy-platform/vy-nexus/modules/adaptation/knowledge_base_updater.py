#!/usr/bin/env python3
"""
Dynamic Knowledge Base Updater

Automatically updates the knowledge base with new discoveries, learnings,
and insights from user interactions and system operations.

Features:
- Real-time knowledge capture from interactions
- Automatic categorization and tagging
- Relevance scoring and prioritization
- Knowledge validation and verification
- Duplicate detection and merging
- Knowledge graph construction
- Search optimization
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict
import hashlib


class KnowledgeBaseUpdater:
    """Manages dynamic updates to the knowledge base."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/knowledge"):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Knowledge storage files
        self.knowledge_file = os.path.join(self.data_dir, "knowledge_base.json")
        self.categories_file = os.path.join(self.data_dir, "categories.json")
        self.tags_file = os.path.join(self.data_dir, "tags.json")
        self.graph_file = os.path.join(self.data_dir, "knowledge_graph.json")
        self.updates_file = os.path.join(self.data_dir, "update_history.json")
        
        # Load existing data
        self.knowledge_base = self._load_json(self.knowledge_file, {})
        self.categories = self._load_json(self.categories_file, {})
        self.tags = self._load_json(self.tags_file, {})
        self.knowledge_graph = self._load_json(self.graph_file, {"nodes": {}, "edges": []})
        self.update_history = self._load_json(self.updates_file, [])
    
    def _load_json(self, filepath: str, default):
        """Load JSON file or return default."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except:
                return default
        return default
    
    def _save_json(self, filepath: str, data):
        """Save data to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _generate_knowledge_id(self, content: str) -> str:
        """Generate unique ID for knowledge entry."""
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def add_knowledge(self, 
                     content: str,
                     category: str,
                     tags: List[str] = None,
                     source: str = "user_interaction",
                     confidence: float = 0.8,
                     metadata: Dict = None) -> str:
        """
        Add new knowledge to the base.
        
        Args:
            content: The knowledge content
            category: Knowledge category
            tags: List of tags
            source: Source of knowledge
            confidence: Confidence score (0-1)
            metadata: Additional metadata
        
        Returns:
            Knowledge ID
        """
        knowledge_id = self._generate_knowledge_id(content)
        
        # Check for duplicates
        if knowledge_id in self.knowledge_base:
            return self._update_existing_knowledge(knowledge_id, confidence, source)
        
        # Create knowledge entry
        entry = {
            "id": knowledge_id,
            "content": content,
            "category": category,
            "tags": tags or [],
            "source": source,
            "confidence": confidence,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "access_count": 0,
            "validation_count": 0,
            "metadata": metadata or {}
        }
        
        # Add to knowledge base
        self.knowledge_base[knowledge_id] = entry
        
        # Update categories and tags
        self._update_category(category, knowledge_id)
        for tag in (tags or []):
            self._update_tag(tag, knowledge_id)
        
        # Update knowledge graph
        self._add_to_graph(knowledge_id, entry)
        
        # Record update
        self._record_update("add", knowledge_id, entry)
        
        # Save changes
        self._save_all()
        
        return knowledge_id
    
    def _update_existing_knowledge(self, knowledge_id: str, confidence: float, source: str) -> str:
        """Update existing knowledge entry."""
        entry = self.knowledge_base[knowledge_id]
        
        # Update confidence (weighted average)
        old_confidence = entry["confidence"]
        entry["confidence"] = (old_confidence + confidence) / 2
        
        # Update metadata
        entry["updated_at"] = datetime.now().isoformat()
        entry["validation_count"] += 1
        
        if source not in entry.get("sources", []):
            if "sources" not in entry:
                entry["sources"] = [entry["source"]]
            entry["sources"].append(source)
        
        self._record_update("update", knowledge_id, entry)
        self._save_all()
        
        return knowledge_id
    
    def update_from_interaction(self, interaction_data: Dict) -> List[str]:
        """
        Extract and add knowledge from user interaction.
        
        Args:
            interaction_data: Interaction data dictionary
        
        Returns:
            List of knowledge IDs added
        """
        knowledge_ids = []
        
        # Extract learnings from interaction
        learnings = self._extract_learnings(interaction_data)
        
        for learning in learnings:
            kid = self.add_knowledge(
                content=learning["content"],
                category=learning["category"],
                tags=learning["tags"],
                source="interaction_analysis",
                confidence=learning["confidence"],
                metadata={"interaction_id": interaction_data.get("id")}
            )
            knowledge_ids.append(kid)
        
        return knowledge_ids
    
    def _extract_learnings(self, interaction_data: Dict) -> List[Dict]:
        """Extract learnings from interaction data."""
        learnings = []
        
        # Extract from task completion
        if interaction_data.get("task_completed"):
            task = interaction_data.get("task", "")
            method = interaction_data.get("method", "")
            
            if task and method:
                learnings.append({
                    "content": f"Task '{task}' can be completed using: {method}",
                    "category": "task_methods",
                    "tags": ["task", "method", "completion"],
                    "confidence": 0.9
                })
        
        # Extract from errors
        if interaction_data.get("errors"):
            for error in interaction_data["errors"]:
                if error.get("solution"):
                    learnings.append({
                        "content": f"Error '{error['type']}' solved by: {error['solution']}",
                        "category": "error_solutions",
                        "tags": ["error", "solution", error["type"]],
                        "confidence": 0.85
                    })
        
        # Extract from user feedback
        if interaction_data.get("feedback"):
            feedback = interaction_data["feedback"]
            if feedback.get("positive"):
                learnings.append({
                    "content": f"User prefers: {feedback['positive']}",
                    "category": "user_preferences",
                    "tags": ["preference", "positive"],
                    "confidence": 0.8
                })
        
        # Extract from discoveries
        if interaction_data.get("discoveries"):
            for discovery in interaction_data["discoveries"]:
                learnings.append({
                    "content": discovery["content"],
                    "category": discovery.get("category", "general"),
                    "tags": discovery.get("tags", ["discovery"]),
                    "confidence": discovery.get("confidence", 0.7)
                })
        
        return learnings
    
    def search_knowledge(self, query: str, category: str = None, tags: List[str] = None, limit: int = 10) -> List[Dict]:
        """
        Search knowledge base.
        
        Args:
            query: Search query
            category: Filter by category
            tags: Filter by tags
            limit: Maximum results
        
        Returns:
            List of matching knowledge entries
        """
        results = []
        query_lower = query.lower()
        
        for kid, entry in self.knowledge_base.items():
            # Apply filters
            if category and entry["category"] != category:
                continue
            
            if tags:
                if not any(tag in entry["tags"] for tag in tags):
                    continue
            
            # Calculate relevance score
            score = 0
            content_lower = entry["content"].lower()
            
            # Exact match
            if query_lower in content_lower:
                score += 10
            
            # Word matches
            query_words = query_lower.split()
            for word in query_words:
                if word in content_lower:
                    score += 2
            
            # Tag matches
            for tag in entry["tags"]:
                if tag.lower() in query_lower:
                    score += 3
            
            # Confidence boost
            score *= entry["confidence"]
            
            if score > 0:
                result = entry.copy()
                result["relevance_score"] = score
                results.append(result)
                
                # Update access count
                entry["access_count"] += 1
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return results[:limit]
    
    def _update_category(self, category: str, knowledge_id: str):
        """Update category index."""
        if category not in self.categories:
            self.categories[category] = {
                "knowledge_ids": [],
                "count": 0,
                "created_at": datetime.now().isoformat()
            }
        
        if knowledge_id not in self.categories[category]["knowledge_ids"]:
            self.categories[category]["knowledge_ids"].append(knowledge_id)
            self.categories[category]["count"] += 1
    
    def _update_tag(self, tag: str, knowledge_id: str):
        """Update tag index."""
        if tag not in self.tags:
            self.tags[tag] = {
                "knowledge_ids": [],
                "count": 0,
                "created_at": datetime.now().isoformat()
            }
        
        if knowledge_id not in self.tags[tag]["knowledge_ids"]:
            self.tags[tag]["knowledge_ids"].append(knowledge_id)
            self.tags[tag]["count"] += 1
    
    def _add_to_graph(self, knowledge_id: str, entry: Dict):
        """Add knowledge to graph structure."""
        # Add node
        self.knowledge_graph["nodes"][knowledge_id] = {
            "id": knowledge_id,
            "category": entry["category"],
            "tags": entry["tags"],
            "confidence": entry["confidence"]
        }
        
        # Find related knowledge and create edges
        for existing_id, existing_entry in self.knowledge_base.items():
            if existing_id == knowledge_id:
                continue
            
            # Calculate relationship strength
            strength = self._calculate_relationship_strength(entry, existing_entry)
            
            if strength > 0.3:  # Threshold for creating edge
                self.knowledge_graph["edges"].append({
                    "from": knowledge_id,
                    "to": existing_id,
                    "strength": strength,
                    "created_at": datetime.now().isoformat()
                })
    
    def _calculate_relationship_strength(self, entry1: Dict, entry2: Dict) -> float:
        """Calculate relationship strength between two knowledge entries."""
        strength = 0.0
        
        # Same category
        if entry1["category"] == entry2["category"]:
            strength += 0.3
        
        # Shared tags
        shared_tags = set(entry1["tags"]) & set(entry2["tags"])
        strength += len(shared_tags) * 0.15
        
        # Content similarity (simple word overlap)
        words1 = set(entry1["content"].lower().split())
        words2 = set(entry2["content"].lower().split())
        overlap = len(words1 & words2)
        if overlap > 0:
            strength += min(overlap * 0.05, 0.4)
        
        return min(strength, 1.0)
    
    def _record_update(self, action: str, knowledge_id: str, entry: Dict):
        """Record update in history."""
        self.update_history.append({
            "action": action,
            "knowledge_id": knowledge_id,
            "category": entry["category"],
            "timestamp": datetime.now().isoformat(),
            "confidence": entry["confidence"]
        })
        
        # Keep only last 1000 updates
        if len(self.update_history) > 1000:
            self.update_history = self.update_history[-1000:]
    
    def _save_all(self):
        """Save all data files."""
        self._save_json(self.knowledge_file, self.knowledge_base)
        self._save_json(self.categories_file, self.categories)
        self._save_json(self.tags_file, self.tags)
        self._save_json(self.graph_file, self.knowledge_graph)
        self._save_json(self.updates_file, self.update_history)
    
    def get_statistics(self) -> Dict:
        """Get knowledge base statistics."""
        return {
            "total_knowledge": len(self.knowledge_base),
            "total_categories": len(self.categories),
            "total_tags": len(self.tags),
            "total_edges": len(self.knowledge_graph["edges"]),
            "recent_updates": len([u for u in self.update_history if self._is_recent(u["timestamp"])]),
            "avg_confidence": sum(e["confidence"] for e in self.knowledge_base.values()) / max(len(self.knowledge_base), 1),
            "top_categories": sorted(self.categories.items(), key=lambda x: x[1]["count"], reverse=True)[:5],
            "top_tags": sorted(self.tags.items(), key=lambda x: x[1]["count"], reverse=True)[:10]
        }
    
    def _is_recent(self, timestamp: str, hours: int = 24) -> bool:
        """Check if timestamp is recent."""
        try:
            ts = datetime.fromisoformat(timestamp)
            now = datetime.now()
            return (now - ts).total_seconds() < hours * 3600
        except:
            return False
    
    def validate_knowledge(self, knowledge_id: str, is_valid: bool):
        """Validate or invalidate knowledge entry."""
        if knowledge_id in self.knowledge_base:
            entry = self.knowledge_base[knowledge_id]
            
            if is_valid:
                entry["confidence"] = min(entry["confidence"] + 0.1, 1.0)
                entry["validation_count"] += 1
            else:
                entry["confidence"] = max(entry["confidence"] - 0.2, 0.0)
            
            entry["updated_at"] = datetime.now().isoformat()
            self._save_all()
    
    def merge_duplicate_knowledge(self, id1: str, id2: str) -> str:
        """Merge two duplicate knowledge entries."""
        if id1 not in self.knowledge_base or id2 not in self.knowledge_base:
            return None
        
        entry1 = self.knowledge_base[id1]
        entry2 = self.knowledge_base[id2]
        
        # Merge into entry with higher confidence
        if entry1["confidence"] >= entry2["confidence"]:
            primary, secondary = id1, id2
        else:
            primary, secondary = id2, id1
        
        primary_entry = self.knowledge_base[primary]
        secondary_entry = self.knowledge_base[secondary]
        
        # Merge tags
        primary_entry["tags"] = list(set(primary_entry["tags"] + secondary_entry["tags"]))
        
        # Update confidence
        primary_entry["confidence"] = (primary_entry["confidence"] + secondary_entry["confidence"]) / 2
        
        # Merge metadata
        primary_entry["metadata"].update(secondary_entry["metadata"])
        
        # Update counts
        primary_entry["access_count"] += secondary_entry["access_count"]
        primary_entry["validation_count"] += secondary_entry["validation_count"]
        
        # Remove secondary
        del self.knowledge_base[secondary]
        
        self._save_all()
        return primary


def test_knowledge_base_updater():
    """Test the knowledge base updater."""
    print("Testing Knowledge Base Updater...")
    
    updater = KnowledgeBaseUpdater()
    
    # Test adding knowledge
    print("\n1. Adding knowledge...")
    kid1 = updater.add_knowledge(
        content="Python is great for automation tasks",
        category="programming",
        tags=["python", "automation"],
        confidence=0.9
    )
    print(f"   Added knowledge: {kid1}")
    
    kid2 = updater.add_knowledge(
        content="Use async/await for concurrent operations",
        category="programming",
        tags=["python", "async", "performance"],
        confidence=0.85
    )
    print(f"   Added knowledge: {kid2}")
    
    # Test searching
    print("\n2. Searching knowledge...")
    results = updater.search_knowledge("python automation")
    print(f"   Found {len(results)} results")
    for r in results:
        print(f"   - {r['content'][:50]}... (score: {r['relevance_score']:.2f})")
    
    # Test updating from interaction
    print("\n3. Updating from interaction...")
    interaction = {
        "id": "test_interaction_1",
        "task_completed": True,
        "task": "file processing",
        "method": "using pandas for CSV files",
        "feedback": {
            "positive": "fast processing with pandas"
        }
    }
    kids = updater.update_from_interaction(interaction)
    print(f"   Added {len(kids)} knowledge entries from interaction")
    
    # Test statistics
    print("\n4. Knowledge base statistics:")
    stats = updater.get_statistics()
    print(f"   Total knowledge: {stats['total_knowledge']}")
    print(f"   Total categories: {stats['total_categories']}")
    print(f"   Total tags: {stats['total_tags']}")
    print(f"   Average confidence: {stats['avg_confidence']:.2f}")
    
    print("\n✅ Knowledge Base Updater test complete!")


if __name__ == "__main__":
    test_knowledge_base_updater()
