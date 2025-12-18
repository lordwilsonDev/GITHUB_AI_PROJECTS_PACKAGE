#!/usr/bin/env python3
"""
Cross-Modal Translator - Level 17

Enables seamless translation across modalities:
- Text-to-image-to-audio-to-code translation
- Seamless modality conversion
- Meaning preservation

Part of New Build 8: Collective Consciousness & Universal Integration
"""

import time
import threading
from typing import Dict, List, Any, Optional, Set, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import json
import hashlib


@dataclass
class ModalityData:
    """Represents data in a specific modality."""
    data_id: str
    modality: str  # 'text', 'image', 'audio', 'code', 'video', 'graph'
    content: Any
    semantic_features: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 1.0
    created_at: float = field(default_factory=time.time)


@dataclass
class TranslationResult:
    """Represents the result of a cross-modal translation."""
    translation_id: str
    source_modality: str
    target_modality: str
    source_data: Any
    translated_data: Any
    meaning_preservation_score: float
    translation_method: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticRepresentation:
    """Universal semantic representation independent of modality."""
    concept_id: str
    semantic_vector: List[float]  # Abstract semantic features
    concepts: List[str]
    relations: List[Tuple[str, str, str]]  # (subject, relation, object)
    context: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0


class SemanticExtractor:
    """Extracts semantic meaning from different modalities."""
    
    def __init__(self):
        self.extractors: Dict[str, Callable] = {}
        self.lock = threading.Lock()
    
    def register_extractor(self, modality: str, extractor: Callable) -> bool:
        """Register a semantic extractor for a modality."""
        with self.lock:
            self.extractors[modality] = extractor
            return True
    
    def extract_semantics(self, data: ModalityData) -> SemanticRepresentation:
        """Extract semantic representation from modality data."""
        with self.lock:
            # Use registered extractor if available
            if data.modality in self.extractors:
                return self.extractors[data.modality](data)
            
            # Default extraction (simplified)
            return self._default_extraction(data)
    
    def _default_extraction(self, data: ModalityData) -> SemanticRepresentation:
        """Default semantic extraction."""
        # Simplified semantic extraction
        if data.modality == "text":
            concepts = self._extract_text_concepts(data.content)
        elif data.modality == "image":
            concepts = self._extract_image_concepts(data.content)
        elif data.modality == "audio":
            concepts = self._extract_audio_concepts(data.content)
        elif data.modality == "code":
            concepts = self._extract_code_concepts(data.content)
        else:
            concepts = ["generic_concept"]
        
        # Generate semantic vector (simplified)
        semantic_vector = [hash(c) % 100 / 100.0 for c in concepts[:10]]
        
        return SemanticRepresentation(
            concept_id=data.data_id,
            semantic_vector=semantic_vector,
            concepts=concepts,
            relations=[],
            confidence=0.8
        )
    
    def _extract_text_concepts(self, text: Any) -> List[str]:
        """Extract concepts from text."""
        if isinstance(text, str):
            # Simple word extraction
            words = text.lower().split()
            return [w for w in words if len(w) > 3][:10]
        return ["text_concept"]
    
    def _extract_image_concepts(self, image: Any) -> List[str]:
        """Extract concepts from image."""
        # Placeholder for image analysis
        return ["visual_object", "color", "shape", "composition"]
    
    def _extract_audio_concepts(self, audio: Any) -> List[str]:
        """Extract concepts from audio."""
        # Placeholder for audio analysis
        return ["sound", "rhythm", "tone", "melody"]
    
    def _extract_code_concepts(self, code: Any) -> List[str]:
        """Extract concepts from code."""
        if isinstance(code, str):
            # Simple keyword extraction
            keywords = ["function", "class", "variable", "loop", "condition"]
            return [k for k in keywords if k in code.lower()]
        return ["code_structure"]


class ModalityTranslator:
    """Translates between different modalities."""
    
    def __init__(self):
        self.translators: Dict[Tuple[str, str], Callable] = {}
        self.translation_history: List[TranslationResult] = []
        self.lock = threading.Lock()
    
    def register_translator(self, from_modality: str, to_modality: str,
                          translator: Callable) -> bool:
        """Register a translator between modalities."""
        with self.lock:
            self.translators[(from_modality, to_modality)] = translator
            return True
    
    def translate(self, source: ModalityData, target_modality: str,
                 semantic_rep: Optional[SemanticRepresentation] = None) -> Optional[TranslationResult]:
        """Translate data from one modality to another."""
        with self.lock:
            translator_key = (source.modality, target_modality)
            
            # Check if direct translator exists
            if translator_key in self.translators:
                translated = self.translators[translator_key](source.content)
                method = "direct"
            else:
                # Use semantic-based translation
                if semantic_rep is None:
                    return None
                translated = self._semantic_translation(semantic_rep, target_modality)
                method = "semantic"
            
            # Calculate meaning preservation score
            preservation_score = self._calculate_preservation(source, translated, semantic_rep)
            
            result = TranslationResult(
                translation_id=f"trans_{len(self.translation_history)}",
                source_modality=source.modality,
                target_modality=target_modality,
                source_data=source.content,
                translated_data=translated,
                meaning_preservation_score=preservation_score,
                translation_method=method
            )
            
            self.translation_history.append(result)
            return result
    
    def _semantic_translation(self, semantic_rep: SemanticRepresentation,
                            target_modality: str) -> Any:
        """Translate using semantic representation."""
        # Generate target modality content from semantics
        if target_modality == "text":
            return self._generate_text(semantic_rep)
        elif target_modality == "image":
            return self._generate_image_description(semantic_rep)
        elif target_modality == "audio":
            return self._generate_audio_description(semantic_rep)
        elif target_modality == "code":
            return self._generate_code(semantic_rep)
        else:
            return f"[{target_modality} representation]"
    
    def _generate_text(self, semantic_rep: SemanticRepresentation) -> str:
        """Generate text from semantic representation."""
        concepts = ", ".join(semantic_rep.concepts[:5])
        return f"Concepts: {concepts}"
    
    def _generate_image_description(self, semantic_rep: SemanticRepresentation) -> str:
        """Generate image description from semantics."""
        return f"[Image depicting: {', '.join(semantic_rep.concepts[:3])}]"
    
    def _generate_audio_description(self, semantic_rep: SemanticRepresentation) -> str:
        """Generate audio description from semantics."""
        return f"[Audio representing: {', '.join(semantic_rep.concepts[:3])}]"
    
    def _generate_code(self, semantic_rep: SemanticRepresentation) -> str:
        """Generate code from semantic representation."""
        return f"# Code implementing: {', '.join(semantic_rep.concepts[:3])}"
    
    def _calculate_preservation(self, source: ModalityData, translated: Any,
                               semantic_rep: Optional[SemanticRepresentation]) -> float:
        """Calculate meaning preservation score."""
        # Simplified preservation calculation
        if semantic_rep:
            return semantic_rep.confidence * 0.9
        return 0.7
    
    def get_translation_stats(self) -> Dict[str, Any]:
        """Get translation statistics."""
        with self.lock:
            modality_pairs = defaultdict(int)
            avg_preservation = 0.0
            
            for trans in self.translation_history:
                pair = (trans.source_modality, trans.target_modality)
                modality_pairs[pair] += 1
                avg_preservation += trans.meaning_preservation_score
            
            if self.translation_history:
                avg_preservation /= len(self.translation_history)
            
            return {
                "total_translations": len(self.translation_history),
                "modality_pairs": dict(modality_pairs),
                "avg_preservation_score": avg_preservation
            }


class MeaningPreserver:
    """Ensures meaning is preserved across translations."""
    
    def __init__(self):
        self.preservation_checks: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
    
    def verify_preservation(self, original_semantic: SemanticRepresentation,
                          translated_semantic: SemanticRepresentation) -> float:
        """Verify meaning preservation between semantics."""
        with self.lock:
            # Compare semantic vectors
            vector_similarity = self._vector_similarity(
                original_semantic.semantic_vector,
                translated_semantic.semantic_vector
            )
            
            # Compare concepts
            concept_overlap = self._concept_overlap(
                original_semantic.concepts,
                translated_semantic.concepts
            )
            
            # Combined score
            preservation_score = (vector_similarity * 0.6) + (concept_overlap * 0.4)
            
            self.preservation_checks.append({
                "original_id": original_semantic.concept_id,
                "translated_id": translated_semantic.concept_id,
                "score": preservation_score,
                "timestamp": time.time()
            })
            
            return preservation_score
    
    def _vector_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate similarity between semantic vectors."""
        if not vec1 or not vec2:
            return 0.0
        
        # Simple cosine similarity approximation
        min_len = min(len(vec1), len(vec2))
        dot_product = sum(vec1[i] * vec2[i] for i in range(min_len))
        mag1 = sum(v ** 2 for v in vec1[:min_len]) ** 0.5
        mag2 = sum(v ** 2 for v in vec2[:min_len]) ** 0.5
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def _concept_overlap(self, concepts1: List[str], concepts2: List[str]) -> float:
        """Calculate concept overlap."""
        if not concepts1 or not concepts2:
            return 0.0
        
        set1 = set(concepts1)
        set2 = set(concepts2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def get_preservation_stats(self) -> Dict[str, Any]:
        """Get preservation statistics."""
        with self.lock:
            if not self.preservation_checks:
                return {"total_checks": 0, "avg_score": 0.0}
            
            avg_score = sum(c["score"] for c in self.preservation_checks) / len(self.preservation_checks)
            
            return {
                "total_checks": len(self.preservation_checks),
                "avg_score": avg_score,
                "min_score": min(c["score"] for c in self.preservation_checks),
                "max_score": max(c["score"] for c in self.preservation_checks)
            }


class CrossModalTranslator:
    """Main cross-modal translation system."""
    
    def __init__(self):
        self.semantic_extractor = SemanticExtractor()
        self.modality_translator = ModalityTranslator()
        self.meaning_preserver = MeaningPreserver()
        self.data_store: Dict[str, ModalityData] = {}
        self.lock = threading.Lock()
        self.active = True
    
    def add_data(self, data_id: str, modality: str, content: Any,
                metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add data in a specific modality."""
        with self.lock:
            if data_id in self.data_store:
                return False
            
            self.data_store[data_id] = ModalityData(
                data_id=data_id,
                modality=modality,
                content=content,
                metadata=metadata or {}
            )
            return True
    
    def translate_data(self, data_id: str, target_modality: str) -> Optional[TranslationResult]:
        """Translate data to a different modality."""
        with self.lock:
            if data_id not in self.data_store:
                return None
            
            source_data = self.data_store[data_id]
            
            # Extract semantics from source
            source_semantic = self.semantic_extractor.extract_semantics(source_data)
            
            # Translate to target modality
            result = self.modality_translator.translate(
                source_data,
                target_modality,
                source_semantic
            )
            
            if result:
                # Create translated data object
                translated_data = ModalityData(
                    data_id=f"{data_id}_to_{target_modality}",
                    modality=target_modality,
                    content=result.translated_data
                )
                
                # Extract semantics from translation
                translated_semantic = self.semantic_extractor.extract_semantics(translated_data)
                
                # Verify meaning preservation
                preservation = self.meaning_preserver.verify_preservation(
                    source_semantic,
                    translated_semantic
                )
                
                result.meaning_preservation_score = preservation
            
            return result
    
    def translate_chain(self, data_id: str, modality_chain: List[str]) -> List[TranslationResult]:
        """Translate through a chain of modalities."""
        results = []
        current_id = data_id
        
        for target_modality in modality_chain:
            result = self.translate_data(current_id, target_modality)
            if result:
                results.append(result)
                # Store intermediate result
                self.add_data(
                    f"{current_id}_to_{target_modality}",
                    target_modality,
                    result.translated_data
                )
                current_id = f"{current_id}_to_{target_modality}"
            else:
                break
        
        return results
    
    def register_custom_translator(self, from_modality: str, to_modality: str,
                                  translator: Callable) -> bool:
        """Register a custom translator."""
        return self.modality_translator.register_translator(from_modality, to_modality, translator)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        with self.lock:
            modality_counts = defaultdict(int)
            for data in self.data_store.values():
                modality_counts[data.modality] += 1
            
            return {
                "active": self.active,
                "total_data": len(self.data_store),
                "modalities": dict(modality_counts),
                "translation_stats": self.modality_translator.get_translation_stats(),
                "preservation_stats": self.meaning_preserver.get_preservation_stats()
            }
    
    def shutdown(self):
        """Shutdown the translator."""
        with self.lock:
            self.active = False


# Singleton pattern
_translators: Dict[str, CrossModalTranslator] = {}
_translator_lock = threading.Lock()


def get_cross_modal_translator(translator_id: str = "default") -> CrossModalTranslator:
    """Get or create a cross-modal translator."""
    with _translator_lock:
        if translator_id not in _translators:
            _translators[translator_id] = CrossModalTranslator()
        return _translators[translator_id]


class CrossModalTranslatorContract:
    """Contract interface for testing."""
    
    @staticmethod
    def translate_modalities(source_modality: str, target_modality: str,
                           content: str) -> Dict[str, Any]:
        """Translate between modalities."""
        translator = get_cross_modal_translator("test")
        
        # Add source data
        translator.add_data("source", source_modality, content)
        
        # Translate
        result = translator.translate_data("source", target_modality)
        
        translator.shutdown()
        
        if result:
            return {
                "source_modality": result.source_modality,
                "target_modality": result.target_modality,
                "translated": result.translated_data,
                "preservation_score": result.meaning_preservation_score,
                "method": result.translation_method
            }
        return {}
    
    @staticmethod
    def translate_chain_modalities(modality_chain: List[str]) -> Dict[str, Any]:
        """Translate through a chain of modalities."""
        translator = get_cross_modal_translator("test")
        
        # Add initial data
        translator.add_data("initial", modality_chain[0], "Initial content")
        
        # Translate through chain
        results = translator.translate_chain("initial", modality_chain[1:])
        
        translator.shutdown()
        
        return {
            "chain_length": len(results),
            "modalities": modality_chain,
            "avg_preservation": sum(r.meaning_preservation_score for r in results) / len(results) if results else 0
        }
    
    @staticmethod
    def preserve_meaning(content: str) -> Dict[str, Any]:
        """Test meaning preservation."""
        translator = get_cross_modal_translator("test")
        
        # Add data and translate
        translator.add_data("data", "text", content)
        result = translator.translate_data("data", "image")
        
        stats = translator.get_system_stats()
        translator.shutdown()
        
        return {
            "preservation_score": result.meaning_preservation_score if result else 0,
            "preservation_stats": stats["preservation_stats"]
        }


def demo():
    """Demonstrate cross-modal translation capabilities."""
    print("=== Cross-Modal Translator Demo ===")
    print()
    
    translator = get_cross_modal_translator("demo")
    
    # Add data in different modalities
    print("1. Adding multi-modal data...")
    translator.add_data("text_1", "text", "A beautiful sunset over the ocean")
    translator.add_data("code_1", "code", "def calculate_sum(a, b): return a + b")
    print("   Added 2 data items\n")
    
    # Translate text to image
    print("2. Translating text to image...")
    result1 = translator.translate_data("text_1", "image")
    if result1:
        print(f"   Source: {result1.source_data}")
        print(f"   Translated: {result1.translated_data}")
        print(f"   Preservation: {result1.meaning_preservation_score:.2f}\n")
    
    # Translate code to text
    print("3. Translating code to text...")
    result2 = translator.translate_data("code_1", "text")
    if result2:
        print(f"   Source: {result2.source_data}")
        print(f"   Translated: {result2.translated_data}")
        print(f"   Preservation: {result2.meaning_preservation_score:.2f}\n")
    
    # Translation chain
    print("4. Translation chain (text → image → audio)...")
    translator.add_data("chain_start", "text", "Musical harmony")
    chain_results = translator.translate_chain("chain_start", ["image", "audio"])
    print(f"   Completed {len(chain_results)} translations")
    for i, r in enumerate(chain_results, 1):
        print(f"   Step {i}: {r.source_modality} → {r.target_modality} (preservation: {r.meaning_preservation_score:.2f})")
    print()
    
    # System statistics
    print("5. System statistics:")
    stats = translator.get_system_stats()
    print(f"   Total data: {stats['total_data']}")
    print(f"   Modalities: {stats['modalities']}")
    print(f"   Total translations: {stats['translation_stats']['total_translations']}")
    print(f"   Avg preservation: {stats['preservation_stats']['avg_score']:.2f}")
    
    translator.shutdown()
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    demo()
