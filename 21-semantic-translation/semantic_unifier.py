#!/usr/bin/env python3
"""
Semantic Unification Engine - Level 17

Enables universal semantic alignment through:
- Concept alignment across domains
- Universal semantic representation
- Meaning synthesis

Part of New Build 8: Collective Consciousness & Universal Integration
"""

import time
import threading
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import json
import hashlib


@dataclass
class Concept:
    """Represents a semantic concept."""
    concept_id: str
    name: str
    domain: str
    definition: str
    semantic_features: List[float] = field(default_factory=list)
    related_concepts: Set[str] = field(default_factory=set)
    synonyms: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0


@dataclass
class ConceptAlignment:
    """Represents alignment between concepts."""
    alignment_id: str
    concept1_id: str
    concept2_id: str
    alignment_type: str  # 'equivalent', 'similar', 'related', 'subsumes', 'part_of'
    similarity_score: float
    semantic_distance: float
    alignment_method: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class UnifiedConcept:
    """Represents a unified concept across domains."""
    unified_id: str
    source_concepts: List[str]
    unified_name: str
    unified_definition: str
    domains: Set[str] = field(default_factory=set)
    semantic_features: List[float] = field(default_factory=list)
    confidence: float = 1.0
    created_at: float = field(default_factory=time.time)


class ConceptAligner:
    """Aligns concepts across different domains."""
    
    def __init__(self):
        self.concepts: Dict[str, Concept] = {}
        self.alignments: List[ConceptAlignment] = []
        self.lock = threading.Lock()
    
    def add_concept(self, concept_id: str, name: str, domain: str,
                   definition: str, semantic_features: Optional[List[float]] = None) -> bool:
        """Add a concept to the aligner."""
        with self.lock:
            if concept_id in self.concepts:
                return False
            
            self.concepts[concept_id] = Concept(
                concept_id=concept_id,
                name=name,
                domain=domain,
                definition=definition,
                semantic_features=semantic_features or self._generate_features(name, definition)
            )
            return True
    
    def _generate_features(self, name: str, definition: str) -> List[float]:
        """Generate semantic features from name and definition."""
        # Simplified feature generation using hashing
        text = f"{name} {definition}".lower()
        features = []
        for i in range(10):
            hash_val = hash(text + str(i)) % 1000
            features.append(hash_val / 1000.0)
        return features
    
    def align_concepts(self, concept1_id: str, concept2_id: str,
                      method: str = "semantic") -> Optional[ConceptAlignment]:
        """Align two concepts."""
        with self.lock:
            if concept1_id not in self.concepts or concept2_id not in self.concepts:
                return None
            
            concept1 = self.concepts[concept1_id]
            concept2 = self.concepts[concept2_id]
            
            # Calculate similarity
            similarity = self._calculate_similarity(concept1, concept2, method)
            
            # Determine alignment type
            alignment_type = self._determine_alignment_type(similarity)
            
            # Calculate semantic distance
            distance = 1.0 - similarity
            
            alignment = ConceptAlignment(
                alignment_id=f"align_{len(self.alignments)}",
                concept1_id=concept1_id,
                concept2_id=concept2_id,
                alignment_type=alignment_type,
                similarity_score=similarity,
                semantic_distance=distance,
                alignment_method=method
            )
            
            self.alignments.append(alignment)
            
            # Update related concepts
            concept1.related_concepts.add(concept2_id)
            concept2.related_concepts.add(concept1_id)
            
            return alignment
    
    def _calculate_similarity(self, concept1: Concept, concept2: Concept,
                            method: str) -> float:
        """Calculate similarity between concepts."""
        if method == "semantic":
            return self._semantic_similarity(concept1.semantic_features, concept2.semantic_features)
        elif method == "lexical":
            return self._lexical_similarity(concept1.name, concept2.name)
        elif method == "definition":
            return self._definition_similarity(concept1.definition, concept2.definition)
        else:
            # Combined method
            sem_sim = self._semantic_similarity(concept1.semantic_features, concept2.semantic_features)
            lex_sim = self._lexical_similarity(concept1.name, concept2.name)
            def_sim = self._definition_similarity(concept1.definition, concept2.definition)
            return (sem_sim * 0.5) + (lex_sim * 0.2) + (def_sim * 0.3)
    
    def _semantic_similarity(self, features1: List[float], features2: List[float]) -> float:
        """Calculate semantic similarity using feature vectors."""
        if not features1 or not features2:
            return 0.0
        
        min_len = min(len(features1), len(features2))
        dot_product = sum(features1[i] * features2[i] for i in range(min_len))
        mag1 = sum(f ** 2 for f in features1[:min_len]) ** 0.5
        mag2 = sum(f ** 2 for f in features2[:min_len]) ** 0.5
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def _lexical_similarity(self, name1: str, name2: str) -> float:
        """Calculate lexical similarity."""
        name1_lower = name1.lower()
        name2_lower = name2.lower()
        
        if name1_lower == name2_lower:
            return 1.0
        
        # Simple character overlap
        set1 = set(name1_lower)
        set2 = set(name2_lower)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _definition_similarity(self, def1: str, def2: str) -> float:
        """Calculate definition similarity."""
        words1 = set(def1.lower().split())
        words2 = set(def2.lower().split())
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _determine_alignment_type(self, similarity: float) -> str:
        """Determine alignment type based on similarity."""
        if similarity >= 0.9:
            return "equivalent"
        elif similarity >= 0.7:
            return "similar"
        elif similarity >= 0.5:
            return "related"
        else:
            return "distant"
    
    def find_alignments(self, concept_id: str, min_similarity: float = 0.5) -> List[ConceptAlignment]:
        """Find all alignments for a concept."""
        with self.lock:
            return [
                a for a in self.alignments
                if (a.concept1_id == concept_id or a.concept2_id == concept_id)
                and a.similarity_score >= min_similarity
            ]
    
    def get_alignment_stats(self) -> Dict[str, Any]:
        """Get alignment statistics."""
        with self.lock:
            type_counts = defaultdict(int)
            for alignment in self.alignments:
                type_counts[alignment.alignment_type] += 1
            
            avg_similarity = sum(a.similarity_score for a in self.alignments) / len(self.alignments) if self.alignments else 0
            
            return {
                "total_concepts": len(self.concepts),
                "total_alignments": len(self.alignments),
                "alignment_types": dict(type_counts),
                "avg_similarity": avg_similarity
            }


class UniversalSemanticSpace:
    """Represents a universal semantic space."""
    
    def __init__(self, dimensions: int = 100):
        self.dimensions = dimensions
        self.concept_embeddings: Dict[str, List[float]] = {}
        self.domain_spaces: Dict[str, Dict[str, List[float]]] = defaultdict(dict)
        self.lock = threading.Lock()
    
    def embed_concept(self, concept_id: str, concept: Concept) -> List[float]:
        """Embed a concept in universal semantic space."""
        with self.lock:
            # Use existing features or generate new ones
            if concept.semantic_features:
                embedding = concept.semantic_features[:self.dimensions]
                # Pad if necessary
                while len(embedding) < self.dimensions:
                    embedding.append(0.0)
            else:
                # Generate embedding
                embedding = self._generate_embedding(concept)
            
            self.concept_embeddings[concept_id] = embedding
            self.domain_spaces[concept.domain][concept_id] = embedding
            
            return embedding
    
    def _generate_embedding(self, concept: Concept) -> List[float]:
        """Generate embedding for a concept."""
        text = f"{concept.name} {concept.definition}".lower()
        embedding = []
        for i in range(self.dimensions):
            hash_val = hash(text + str(i)) % 10000
            embedding.append(hash_val / 10000.0)
        return embedding
    
    def project_to_domain(self, concept_id: str, target_domain: str) -> Optional[List[float]]:
        """Project a concept to a specific domain space."""
        with self.lock:
            if concept_id not in self.concept_embeddings:
                return None
            
            # Simple projection (could be more sophisticated)
            universal_embedding = self.concept_embeddings[concept_id]
            
            # Apply domain-specific transformation (simplified)
            domain_hash = hash(target_domain) % 100
            projection = [
                e * (1.0 + domain_hash / 1000.0)
                for e in universal_embedding
            ]
            
            return projection
    
    def find_nearest_concepts(self, embedding: List[float], k: int = 5) -> List[Tuple[str, float]]:
        """Find k nearest concepts to an embedding."""
        with self.lock:
            distances = []
            
            for concept_id, concept_embedding in self.concept_embeddings.items():
                distance = self._euclidean_distance(embedding, concept_embedding)
                distances.append((concept_id, distance))
            
            # Sort by distance and return top k
            distances.sort(key=lambda x: x[1])
            return distances[:k]
    
    def _euclidean_distance(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate Euclidean distance."""
        min_len = min(len(vec1), len(vec2))
        return sum((vec1[i] - vec2[i]) ** 2 for i in range(min_len)) ** 0.5


class MeaningSynthesizer:
    """Synthesizes unified meanings from multiple concepts."""
    
    def __init__(self):
        self.unified_concepts: Dict[str, UnifiedConcept] = {}
        self.synthesis_history: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
    
    def synthesize_concepts(self, concept_ids: List[str], concepts: Dict[str, Concept],
                          method: str = "merge") -> Optional[UnifiedConcept]:
        """Synthesize multiple concepts into a unified concept."""
        with self.lock:
            if not concept_ids:
                return None
            
            # Get concepts
            source_concepts = [concepts[cid] for cid in concept_ids if cid in concepts]
            if not source_concepts:
                return None
            
            # Synthesize based on method
            if method == "merge":
                unified = self._merge_concepts(source_concepts)
            elif method == "abstract":
                unified = self._abstract_concepts(source_concepts)
            elif method == "intersect":
                unified = self._intersect_concepts(source_concepts)
            else:
                return None
            
            unified_id = f"unified_{len(self.unified_concepts)}"
            unified.unified_id = unified_id
            
            self.unified_concepts[unified_id] = unified
            
            # Record synthesis
            self.synthesis_history.append({
                "unified_id": unified_id,
                "source_concepts": concept_ids,
                "method": method,
                "timestamp": time.time()
            })
            
            return unified
    
    def _merge_concepts(self, concepts: List[Concept]) -> UnifiedConcept:
        """Merge concepts by combining their features."""
        # Combine names
        names = [c.name for c in concepts]
        unified_name = " + ".join(names[:3])  # Limit to 3
        
        # Combine definitions
        definitions = [c.definition for c in concepts]
        unified_definition = "; ".join(definitions[:3])
        
        # Merge semantic features (average)
        all_features = [c.semantic_features for c in concepts if c.semantic_features]
        if all_features:
            max_len = max(len(f) for f in all_features)
            unified_features = []
            for i in range(max_len):
                values = [f[i] for f in all_features if i < len(f)]
                unified_features.append(sum(values) / len(values) if values else 0.0)
        else:
            unified_features = []
        
        # Collect domains
        domains = set(c.domain for c in concepts)
        
        # Calculate confidence
        avg_confidence = sum(c.confidence for c in concepts) / len(concepts)
        
        return UnifiedConcept(
            unified_id="",  # Will be set by caller
            source_concepts=[c.concept_id for c in concepts],
            unified_name=unified_name,
            unified_definition=unified_definition,
            domains=domains,
            semantic_features=unified_features,
            confidence=avg_confidence
        )
    
    def _abstract_concepts(self, concepts: List[Concept]) -> UnifiedConcept:
        """Abstract common patterns from concepts."""
        # Find common words in names
        name_words = [set(c.name.lower().split()) for c in concepts]
        common_words = set.intersection(*name_words) if name_words else set()
        unified_name = " ".join(sorted(common_words)) if common_words else "Abstract Concept"
        
        # Abstract definition
        unified_definition = f"Abstract concept representing {len(concepts)} related concepts"
        
        return UnifiedConcept(
            unified_id="",
            source_concepts=[c.concept_id for c in concepts],
            unified_name=unified_name,
            unified_definition=unified_definition,
            domains=set(c.domain for c in concepts),
            confidence=0.8
        )
    
    def _intersect_concepts(self, concepts: List[Concept]) -> UnifiedConcept:
        """Find intersection of concepts."""
        # Similar to abstract but focuses on commonalities
        unified_name = f"Intersection of {len(concepts)} concepts"
        unified_definition = "Common semantic core across concepts"
        
        return UnifiedConcept(
            unified_id="",
            source_concepts=[c.concept_id for c in concepts],
            unified_name=unified_name,
            unified_definition=unified_definition,
            domains=set(c.domain for c in concepts),
            confidence=0.7
        )
    
    def get_synthesis_stats(self) -> Dict[str, Any]:
        """Get synthesis statistics."""
        with self.lock:
            method_counts = defaultdict(int)
            for record in self.synthesis_history:
                method_counts[record["method"]] += 1
            
            return {
                "total_unified": len(self.unified_concepts),
                "synthesis_count": len(self.synthesis_history),
                "methods_used": dict(method_counts)
            }


class SemanticUnifier:
    """Main semantic unification engine."""
    
    def __init__(self, dimensions: int = 100):
        self.concept_aligner = ConceptAligner()
        self.semantic_space = UniversalSemanticSpace(dimensions)
        self.meaning_synthesizer = MeaningSynthesizer()
        self.lock = threading.Lock()
        self.active = True
    
    def add_concept(self, concept_id: str, name: str, domain: str,
                   definition: str) -> bool:
        """Add a concept to the unifier."""
        # Add to aligner
        if not self.concept_aligner.add_concept(concept_id, name, domain, definition):
            return False
        
        # Embed in semantic space
        concept = self.concept_aligner.concepts[concept_id]
        self.semantic_space.embed_concept(concept_id, concept)
        
        return True
    
    def align_concepts(self, concept1_id: str, concept2_id: str) -> Optional[ConceptAlignment]:
        """Align two concepts."""
        return self.concept_aligner.align_concepts(concept1_id, concept2_id)
    
    def unify_concepts(self, concept_ids: List[str], method: str = "merge") -> Optional[UnifiedConcept]:
        """Unify multiple concepts."""
        return self.meaning_synthesizer.synthesize_concepts(
            concept_ids,
            self.concept_aligner.concepts,
            method
        )
    
    def find_similar_concepts(self, concept_id: str, k: int = 5) -> List[Tuple[str, float]]:
        """Find similar concepts in semantic space."""
        if concept_id not in self.semantic_space.concept_embeddings:
            return []
        
        embedding = self.semantic_space.concept_embeddings[concept_id]
        return self.semantic_space.find_nearest_concepts(embedding, k + 1)[1:]  # Exclude self
    
    def cross_domain_alignment(self, domain1: str, domain2: str) -> List[ConceptAlignment]:
        """Find alignments between concepts from different domains."""
        alignments = []
        
        # Get concepts from each domain
        concepts1 = [c for c in self.concept_aligner.concepts.values() if c.domain == domain1]
        concepts2 = [c for c in self.concept_aligner.concepts.values() if c.domain == domain2]
        
        # Align concepts (limit for performance)
        for c1 in concepts1[:5]:
            for c2 in concepts2[:5]:
                alignment = self.concept_aligner.align_concepts(c1.concept_id, c2.concept_id)
                if alignment and alignment.similarity_score >= 0.5:
                    alignments.append(alignment)
        
        return alignments
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        with self.lock:
            return {
                "active": self.active,
                "alignment_stats": self.concept_aligner.get_alignment_stats(),
                "semantic_space_dims": self.semantic_space.dimensions,
                "embedded_concepts": len(self.semantic_space.concept_embeddings),
                "synthesis_stats": self.meaning_synthesizer.get_synthesis_stats()
            }
    
    def shutdown(self):
        """Shutdown the unifier."""
        with self.lock:
            self.active = False


# Singleton pattern
_unifiers: Dict[str, SemanticUnifier] = {}
_unifier_lock = threading.Lock()


def get_semantic_unifier(unifier_id: str = "default", dimensions: int = 100) -> SemanticUnifier:
    """Get or create a semantic unifier."""
    with _unifier_lock:
        if unifier_id not in _unifiers:
            _unifiers[unifier_id] = SemanticUnifier(dimensions)
        return _unifiers[unifier_id]


class SemanticUnifierContract:
    """Contract interface for testing."""
    
    @staticmethod
    def align_cross_domain(domain1: str, domain2: str) -> Dict[str, Any]:
        """Align concepts across domains."""
        unifier = get_semantic_unifier("test")
        
        # Add concepts from domain1
        unifier.add_concept("d1_c1", "Concept A", domain1, "Definition A")
        unifier.add_concept("d1_c2", "Concept B", domain1, "Definition B")
        
        # Add concepts from domain2
        unifier.add_concept("d2_c1", "Concept A", domain2, "Definition A")
        unifier.add_concept("d2_c2", "Concept C", domain2, "Definition C")
        
        # Align
        alignments = unifier.cross_domain_alignment(domain1, domain2)
        
        unifier.shutdown()
        
        return {
            "domain1": domain1,
            "domain2": domain2,
            "alignments_found": len(alignments),
            "avg_similarity": sum(a.similarity_score for a in alignments) / len(alignments) if alignments else 0
        }
    
    @staticmethod
    def unify_meanings(concept_count: int) -> Dict[str, Any]:
        """Unify multiple concepts."""
        unifier = get_semantic_unifier("test")
        
        # Add concepts
        concept_ids = []
        for i in range(concept_count):
            cid = f"concept_{i}"
            unifier.add_concept(cid, f"Concept {i}", "test_domain", f"Definition {i}")
            concept_ids.append(cid)
        
        # Unify
        unified = unifier.unify_concepts(concept_ids, "merge")
        
        unifier.shutdown()
        
        if unified:
            return {
                "source_count": len(unified.source_concepts),
                "unified_name": unified.unified_name,
                "domains": list(unified.domains),
                "confidence": unified.confidence
            }
        return {}
    
    @staticmethod
    def represent_universal(concept_name: str) -> Dict[str, Any]:
        """Create universal semantic representation."""
        unifier = get_semantic_unifier("test")
        
        # Add concept
        unifier.add_concept("concept_1", concept_name, "universal", f"Universal concept: {concept_name}")
        
        # Get embedding
        embedding = unifier.semantic_space.concept_embeddings.get("concept_1")
        
        # Find similar
        unifier.add_concept("concept_2", concept_name + " variant", "universal", "Similar concept")
        similar = unifier.find_similar_concepts("concept_1")
        
        stats = unifier.get_system_stats()
        unifier.shutdown()
        
        return {
            "concept": concept_name,
            "embedding_dims": len(embedding) if embedding else 0,
            "similar_count": len(similar),
            "stats": stats
        }


def demo():
    """Demonstrate semantic unification capabilities."""
    print("=== Semantic Unification Engine Demo ===")
    print()
    
    unifier = get_semantic_unifier("demo")
    
    # Add concepts from different domains
    print("1. Adding concepts from multiple domains...")
    unifier.add_concept("sci_energy", "Energy", "science", "Capacity to do work")
    unifier.add_concept("phil_energy", "Energy", "philosophy", "Vital force or spirit")
    unifier.add_concept("tech_power", "Power", "technology", "Rate of energy transfer")
    print("   Added 3 concepts\n")
    
    # Align concepts
    print("2. Aligning concepts...")
    alignment1 = unifier.align_concepts("sci_energy", "phil_energy")
    alignment2 = unifier.align_concepts("sci_energy", "tech_power")
    if alignment1:
        print(f"   Science-Philosophy alignment: {alignment1.similarity_score:.2f} ({alignment1.alignment_type})")
    if alignment2:
        print(f"   Science-Technology alignment: {alignment2.similarity_score:.2f} ({alignment2.alignment_type})\n")
    
    # Find similar concepts
    print("3. Finding similar concepts...")
    similar = unifier.find_similar_concepts("sci_energy", k=2)
    for concept_id, distance in similar:
        print(f"   {concept_id}: distance = {distance:.2f}")
    print()
    
    # Unify concepts
    print("4. Unifying concepts...")
    unified = unifier.unify_concepts(["sci_energy", "phil_energy", "tech_power"], "merge")
    if unified:
        print(f"   Unified name: {unified.unified_name}")
        print(f"   Domains: {unified.domains}")
        print(f"   Confidence: {unified.confidence:.2f}\n")
    
    # Cross-domain alignment
    print("5. Cross-domain alignment...")
    cross_alignments = unifier.cross_domain_alignment("science", "philosophy")
    print(f"   Found {len(cross_alignments)} cross-domain alignments\n")
    
    # System statistics
    print("6. System statistics:")
    stats = unifier.get_system_stats()
    print(f"   Total concepts: {stats['alignment_stats']['total_concepts']}")
    print(f"   Total alignments: {stats['alignment_stats']['total_alignments']}")
    print(f"   Embedded concepts: {stats['embedded_concepts']}")
    print(f"   Unified concepts: {stats['synthesis_stats']['total_unified']}")
    
    unifier.shutdown()
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    demo()
