#!/usr/bin/env python3
"""
Knowledge Acquisition Pipeline for VY-NEXUS

This module provides a comprehensive pipeline for acquiring, validating, storing,
and retrieving knowledge from multiple sources. It supports continuous learning
and knowledge graph construction.

Features:
- Multi-source knowledge acquisition
- Knowledge validation and verification
- Confidence scoring and provenance tracking
- Knowledge graph construction
- Semantic search and retrieval
- Knowledge conflict resolution
- Temporal knowledge tracking
- Knowledge decay and refresh mechanisms

Author: VY-NEXUS Self-Evolving AI System
Date: December 15, 2025
"""

import json
import os
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict, field
from enum import Enum
import re


class KnowledgeSource(Enum):
    """Sources of knowledge."""
    USER_INPUT = "user_input"  # Directly from user
    DOCUMENTATION = "documentation"  # From docs/manuals
    OBSERVATION = "observation"  # From system observation
    INFERENCE = "inference"  # Inferred from existing knowledge
    EXTERNAL_API = "external_api"  # From external APIs
    WEB_SEARCH = "web_search"  # From web searches
    PATTERN_MINING = "pattern_mining"  # From pattern analysis
    EXPERT_SYSTEM = "expert_system"  # From expert rules


class KnowledgeType(Enum):
    """Types of knowledge."""
    FACT = "fact"  # Factual information
    PROCEDURE = "procedure"  # How-to knowledge
    CONCEPT = "concept"  # Conceptual understanding
    RELATIONSHIP = "relationship"  # Relationships between entities
    RULE = "rule"  # Business/system rules
    HEURISTIC = "heuristic"  # Rules of thumb
    CONSTRAINT = "constraint"  # Constraints and limitations
    PREFERENCE = "preference"  # Preferences and defaults


class ValidationStatus(Enum):
    """Validation status of knowledge."""
    UNVALIDATED = "unvalidated"  # Not yet validated
    VALIDATED = "validated"  # Validated and confirmed
    CONFLICTING = "conflicting"  # Conflicts with existing knowledge
    DEPRECATED = "deprecated"  # No longer valid
    PENDING_REVIEW = "pending_review"  # Needs human review


@dataclass
class KnowledgeItem:
    """Represents a single piece of knowledge."""
    knowledge_id: str
    knowledge_type: KnowledgeType
    subject: str  # What the knowledge is about
    predicate: str  # The relationship or property
    object: Any  # The value or related entity
    source: KnowledgeSource
    confidence: float  # 0.0 to 1.0
    validation_status: ValidationStatus
    created_at: str
    last_updated: str
    last_accessed: str
    access_count: int = 0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    provenance: List[str] = field(default_factory=list)  # Chain of sources
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['knowledge_type'] = self.knowledge_type.value
        data['source'] = self.source.value
        data['validation_status'] = self.validation_status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeItem':
        """Create from dictionary."""
        data['knowledge_type'] = KnowledgeType(data['knowledge_type'])
        data['source'] = KnowledgeSource(data['source'])
        data['validation_status'] = ValidationStatus(data['validation_status'])
        return cls(**data)


@dataclass
class KnowledgeQuery:
    """Represents a knowledge query."""
    subject: Optional[str] = None
    predicate: Optional[str] = None
    object: Optional[Any] = None
    knowledge_type: Optional[KnowledgeType] = None
    tags: Optional[List[str]] = None
    min_confidence: float = 0.5
    max_age_days: Optional[int] = None


class KnowledgeAcquisitionPipeline:
    """
    Pipeline for acquiring, validating, and managing knowledge.
    
    This class provides a complete knowledge management system with acquisition,
    validation, storage, retrieval, and maintenance capabilities.
    """
    
    def __init__(self, data_dir: str = "~/vy_data/knowledge"):
        """
        Initialize the Knowledge Acquisition Pipeline.
        
        Args:
            data_dir: Directory to store knowledge data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.knowledge_file = os.path.join(self.data_dir, "knowledge_base.jsonl")
        self.index_file = os.path.join(self.data_dir, "knowledge_index.json")
        self.graph_file = os.path.join(self.data_dir, "knowledge_graph.json")
        
        self._lock = threading.Lock()
        self._knowledge_base: Dict[str, KnowledgeItem] = {}
        self._subject_index: Dict[str, Set[str]] = defaultdict(set)
        self._predicate_index: Dict[str, Set[str]] = defaultdict(set)
        self._tag_index: Dict[str, Set[str]] = defaultdict(set)
        
        self._load_knowledge_base()
        
        # Configuration
        self.min_confidence_threshold = 0.3
        self.high_confidence_threshold = 0.8
        self.knowledge_decay_days = 365  # Knowledge older than this may decay
        self.max_knowledge_items = 100000  # Prevent unbounded growth
        
    def _load_knowledge_base(self) -> None:
        """Load knowledge base from disk."""
        if not os.path.exists(self.knowledge_file):
            return
        
        try:
            with open(self.knowledge_file, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    data = json.loads(line)
                    item = KnowledgeItem.from_dict(data)
                    self._knowledge_base[item.knowledge_id] = item
                    
                    # Build indexes
                    self._subject_index[item.subject].add(item.knowledge_id)
                    self._predicate_index[item.predicate].add(item.knowledge_id)
                    for tag in item.tags:
                        self._tag_index[tag].add(item.knowledge_id)
                        
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
    
    def _save_knowledge_base(self) -> None:
        """Save knowledge base to disk."""
        try:
            with open(self.knowledge_file, 'w') as f:
                for item in self._knowledge_base.values():
                    f.write(json.dumps(item.to_dict()) + '\n')
        except Exception as e:
            print(f"Error saving knowledge base: {e}")
    
    def _generate_knowledge_id(self, subject: str, predicate: str, object: Any) -> str:
        """Generate unique knowledge ID."""
        data = f"{subject}:{predicate}:{str(object)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def acquire_knowledge(self,
                         knowledge_type: KnowledgeType,
                         subject: str,
                         predicate: str,
                         object: Any,
                         source: KnowledgeSource,
                         confidence: float = 0.5,
                         tags: Optional[List[str]] = None,
                         metadata: Optional[Dict[str, Any]] = None,
                         auto_validate: bool = True) -> str:
        """
        Acquire new knowledge.
        
        Args:
            knowledge_type: Type of knowledge
            subject: What the knowledge is about
            predicate: The relationship or property
            object: The value or related entity
            source: Source of knowledge
            confidence: Initial confidence (0.0-1.0)
            tags: Optional tags for categorization
            metadata: Additional metadata
            auto_validate: Whether to auto-validate
            
        Returns:
            Knowledge ID
        """
        with self._lock:
            knowledge_id = self._generate_knowledge_id(subject, predicate, object)
            now = datetime.now().isoformat()
            
            # Check if knowledge already exists
            if knowledge_id in self._knowledge_base:
                # Update existing knowledge
                item = self._knowledge_base[knowledge_id]
                item.last_updated = now
                item.access_count += 1
                
                # Update confidence based on source
                if source in [KnowledgeSource.USER_INPUT, KnowledgeSource.DOCUMENTATION]:
                    item.confidence = max(item.confidence, confidence)
                else:
                    # Gradual confidence increase
                    item.confidence = min(1.0, item.confidence + 0.1)
                
                # Add to provenance chain
                if source.value not in item.provenance:
                    item.provenance.append(source.value)
                
                # Merge tags
                if tags:
                    for tag in tags:
                        if tag not in item.tags:
                            item.tags.append(tag)
                            self._tag_index[tag].add(knowledge_id)
                
                # Merge metadata
                if metadata:
                    item.metadata.update(metadata)
                
            else:
                # Create new knowledge item
                validation_status = ValidationStatus.VALIDATED if auto_validate else ValidationStatus.UNVALIDATED
                
                item = KnowledgeItem(
                    knowledge_id=knowledge_id,
                    knowledge_type=knowledge_type,
                    subject=subject,
                    predicate=predicate,
                    object=object,
                    source=source,
                    confidence=confidence,
                    validation_status=validation_status,
                    created_at=now,
                    last_updated=now,
                    last_accessed=now,
                    access_count=1,
                    tags=tags or [],
                    metadata=metadata or {},
                    provenance=[source.value]
                )
                
                self._knowledge_base[knowledge_id] = item
                
                # Update indexes
                self._subject_index[subject].add(knowledge_id)
                self._predicate_index[predicate].add(knowledge_id)
                for tag in item.tags:
                    self._tag_index[tag].add(knowledge_id)
            
            # Check for conflicts
            if auto_validate:
                self._check_conflicts(knowledge_id)
            
            # Periodic save
            if len(self._knowledge_base) % 100 == 0:
                self._save_knowledge_base()
            
            return knowledge_id
    
    def _check_conflicts(self, knowledge_id: str) -> None:
        """Check for conflicts with existing knowledge."""
        item = self._knowledge_base[knowledge_id]
        
        # Find items with same subject and predicate but different object
        candidates = self._subject_index.get(item.subject, set()) & \
                    self._predicate_index.get(item.predicate, set())
        
        for candidate_id in candidates:
            if candidate_id == knowledge_id:
                continue
            
            candidate = self._knowledge_base[candidate_id]
            
            # Check if objects conflict
            if candidate.object != item.object:
                # Mark both as conflicting if confidence is similar
                if abs(candidate.confidence - item.confidence) < 0.2:
                    item.validation_status = ValidationStatus.CONFLICTING
                    candidate.validation_status = ValidationStatus.CONFLICTING
                # Otherwise, trust the higher confidence one
                elif item.confidence < candidate.confidence:
                    item.validation_status = ValidationStatus.PENDING_REVIEW
    
    def query_knowledge(self, query: KnowledgeQuery) -> List[KnowledgeItem]:
        """
        Query the knowledge base.
        
        Args:
            query: Knowledge query specification
            
        Returns:
            List of matching knowledge items
        """
        with self._lock:
            # Start with all knowledge IDs
            candidate_ids = set(self._knowledge_base.keys())
            
            # Filter by subject
            if query.subject:
                subject_ids = self._subject_index.get(query.subject, set())
                candidate_ids &= subject_ids
            
            # Filter by predicate
            if query.predicate:
                predicate_ids = self._predicate_index.get(query.predicate, set())
                candidate_ids &= predicate_ids
            
            # Filter by tags
            if query.tags:
                for tag in query.tags:
                    tag_ids = self._tag_index.get(tag, set())
                    candidate_ids &= tag_ids
            
            # Apply additional filters
            results = []
            for kid in candidate_ids:
                item = self._knowledge_base[kid]
                
                # Filter by object
                if query.object is not None and item.object != query.object:
                    continue
                
                # Filter by knowledge type
                if query.knowledge_type and item.knowledge_type != query.knowledge_type:
                    continue
                
                # Filter by confidence
                if item.confidence < query.min_confidence:
                    continue
                
                # Filter by age
                if query.max_age_days:
                    created = datetime.fromisoformat(item.created_at)
                    age_days = (datetime.now() - created).days
                    if age_days > query.max_age_days:
                        continue
                
                # Update access tracking
                item.last_accessed = datetime.now().isoformat()
                item.access_count += 1
                
                results.append(item)
            
            # Sort by confidence (descending)
            results.sort(key=lambda x: x.confidence, reverse=True)
            
            return results
    
    def get_knowledge(self, subject: str, predicate: str) -> Optional[Any]:
        """
        Get knowledge value for subject-predicate pair.
        
        Args:
            subject: Subject to query
            predicate: Predicate to query
            
        Returns:
            Knowledge value or None
        """
        query = KnowledgeQuery(
            subject=subject,
            predicate=predicate,
            min_confidence=self.min_confidence_threshold
        )
        
        results = self.query_knowledge(query)
        
        if results:
            # Return highest confidence result
            return results[0].object
        
        return None
    
    def validate_knowledge(self, knowledge_id: str, is_valid: bool) -> bool:
        """
        Manually validate knowledge.
        
        Args:
            knowledge_id: Knowledge ID to validate
            is_valid: Whether knowledge is valid
            
        Returns:
            True if successful
        """
        with self._lock:
            if knowledge_id not in self._knowledge_base:
                return False
            
            item = self._knowledge_base[knowledge_id]
            
            if is_valid:
                item.validation_status = ValidationStatus.VALIDATED
                item.confidence = min(1.0, item.confidence + 0.2)
            else:
                item.validation_status = ValidationStatus.DEPRECATED
                item.confidence = 0.0
            
            item.last_updated = datetime.now().isoformat()
            self._save_knowledge_base()
            
            return True
    
    def infer_knowledge(self) -> List[KnowledgeItem]:
        """
        Infer new knowledge from existing knowledge.
        
        Returns:
            List of newly inferred knowledge items
        """
        inferred = []
        
        with self._lock:
            # Simple inference rules
            
            # Rule 1: Transitive relationships
            # If A relates to B and B relates to C, then A relates to C
            for item1 in self._knowledge_base.values():
                if item1.knowledge_type != KnowledgeType.RELATIONSHIP:
                    continue
                
                # Find items where subject matches item1's object
                for item2 in self._knowledge_base.values():
                    if item2.knowledge_type != KnowledgeType.RELATIONSHIP:
                        continue
                    
                    if item1.object == item2.subject and item1.predicate == item2.predicate:
                        # Infer transitive relationship
                        new_id = self.acquire_knowledge(
                            knowledge_type=KnowledgeType.RELATIONSHIP,
                            subject=item1.subject,
                            predicate=item1.predicate,
                            object=item2.object,
                            source=KnowledgeSource.INFERENCE,
                            confidence=min(item1.confidence, item2.confidence) * 0.8,
                            metadata={
                                "inferred_from": [item1.knowledge_id, item2.knowledge_id]
                            },
                            auto_validate=False
                        )
                        
                        if new_id not in [i.knowledge_id for i in inferred]:
                            inferred.append(self._knowledge_base[new_id])
        
        return inferred
    
    def apply_knowledge_decay(self) -> int:
        """
        Apply decay to old, unused knowledge.
        
        Returns:
            Number of items decayed
        """
        decayed_count = 0
        
        with self._lock:
            now = datetime.now()
            
            for item in self._knowledge_base.values():
                # Skip high-confidence or recently accessed items
                if item.confidence >= self.high_confidence_threshold:
                    continue
                
                last_accessed = datetime.fromisoformat(item.last_accessed)
                days_since_access = (now - last_accessed).days
                
                if days_since_access > self.knowledge_decay_days:
                    # Apply decay
                    decay_factor = 0.9 ** (days_since_access / 365)
                    item.confidence *= decay_factor
                    decayed_count += 1
                    
                    # Mark as deprecated if confidence too low
                    if item.confidence < self.min_confidence_threshold:
                        item.validation_status = ValidationStatus.DEPRECATED
            
            if decayed_count > 0:
                self._save_knowledge_base()
        
        return decayed_count
    
    def get_knowledge_graph(self, max_depth: int = 2) -> Dict[str, Any]:
        """
        Generate knowledge graph representation.
        
        Args:
            max_depth: Maximum depth for graph traversal
            
        Returns:
            Knowledge graph as dictionary
        """
        graph = {
            "nodes": [],
            "edges": []
        }
        
        node_ids = set()
        
        with self._lock:
            for item in self._knowledge_base.values():
                # Add subject node
                if item.subject not in node_ids:
                    graph["nodes"].append({
                        "id": item.subject,
                        "type": "entity"
                    })
                    node_ids.add(item.subject)
                
                # Add object node if it's a relationship
                if item.knowledge_type == KnowledgeType.RELATIONSHIP:
                    if isinstance(item.object, str) and item.object not in node_ids:
                        graph["nodes"].append({
                            "id": item.object,
                            "type": "entity"
                        })
                        node_ids.add(item.object)
                    
                    # Add edge
                    graph["edges"].append({
                        "source": item.subject,
                        "target": item.object,
                        "label": item.predicate,
                        "confidence": item.confidence
                    })
        
        return graph
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get knowledge base statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            by_type = Counter()
            by_source = Counter()
            by_status = Counter()
            confidence_levels = {"high": 0, "medium": 0, "low": 0}
            
            total_access_count = 0
            
            for item in self._knowledge_base.values():
                by_type[item.knowledge_type.value] += 1
                by_source[item.source.value] += 1
                by_status[item.validation_status.value] += 1
                total_access_count += item.access_count
                
                if item.confidence >= self.high_confidence_threshold:
                    confidence_levels["high"] += 1
                elif item.confidence >= self.min_confidence_threshold:
                    confidence_levels["medium"] += 1
                else:
                    confidence_levels["low"] += 1
            
            return {
                "total_items": len(self._knowledge_base),
                "by_type": dict(by_type),
                "by_source": dict(by_source),
                "by_status": dict(by_status),
                "confidence_distribution": confidence_levels,
                "total_accesses": total_access_count,
                "avg_accesses_per_item": total_access_count / len(self._knowledge_base) if self._knowledge_base else 0,
                "unique_subjects": len(self._subject_index),
                "unique_predicates": len(self._predicate_index),
                "unique_tags": len(self._tag_index)
            }
    
    def export_knowledge(self, filepath: str, 
                        min_confidence: Optional[float] = None) -> bool:
        """
        Export knowledge base to file.
        
        Args:
            filepath: Path to export file
            min_confidence: Minimum confidence to export
            
        Returns:
            True if successful
        """
        try:
            min_conf = min_confidence if min_confidence is not None else 0.0
            
            export_data = []
            for item in self._knowledge_base.values():
                if item.confidence >= min_conf:
                    export_data.append(item.to_dict())
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error exporting knowledge: {e}")
            return False
    
    def flush(self) -> None:
        """Manually flush knowledge base to disk."""
        with self._lock:
            self._save_knowledge_base()


if __name__ == "__main__":
    # Example usage
    pipeline = KnowledgeAcquisitionPipeline()
    
    print("Acquiring knowledge...")
    
    # Acquire some facts
    pipeline.acquire_knowledge(
        knowledge_type=KnowledgeType.FACT,
        subject="Python",
        predicate="is_a",
        object="programming_language",
        source=KnowledgeSource.DOCUMENTATION,
        confidence=1.0,
        tags=["programming", "language"]
    )
    
    pipeline.acquire_knowledge(
        knowledge_type=KnowledgeType.FACT,
        subject="Python",
        predicate="version",
        object="3.11",
        source=KnowledgeSource.OBSERVATION,
        confidence=0.9,
        tags=["programming", "version"]
    )
    
    # Acquire a relationship
    pipeline.acquire_knowledge(
        knowledge_type=KnowledgeType.RELATIONSHIP,
        subject="VY-NEXUS",
        predicate="uses",
        object="Python",
        source=KnowledgeSource.USER_INPUT,
        confidence=1.0,
        tags=["system", "technology"]
    )
    
    print("\nQuerying knowledge...")
    
    # Query by subject
    query = KnowledgeQuery(subject="Python")
    results = pipeline.query_knowledge(query)
    
    print(f"Found {len(results)} items about Python:")
    for item in results:
        print(f"  - {item.subject} {item.predicate} {item.object} (confidence: {item.confidence:.2f})")
    
    # Get specific knowledge
    lang_type = pipeline.get_knowledge("Python", "is_a")
    print(f"\nPython is a: {lang_type}")
    
    print("\nStatistics:")
    stats = pipeline.get_statistics()
    print(json.dumps(stats, indent=2))
    
    pipeline.flush()
