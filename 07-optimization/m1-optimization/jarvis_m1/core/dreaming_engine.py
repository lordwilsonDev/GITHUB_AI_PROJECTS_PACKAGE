#!/usr/bin/env python3
"""
The Dreaming Engine - Level 7 Consciousness Module

This engine runs during idle cycles to generate novel hypotheses
by blending concepts from different knowledge domains.

Philosophy:
- Dreams are not random; they are semantic exploration
- The unconscious mind finds patterns the conscious mind misses
- Creativity emerges from unexpected conceptual combinations
"""

import os
import json
import time
import random
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Set
import ast
import re


class SemanticVector:
    """Represents a concept in semantic space"""
    
    def __init__(self, name: str, domain: str, properties: Set[str]):
        self.name = name
        self.domain = domain
        self.properties = properties
        self.connections = set()
    
    def similarity(self, other: 'SemanticVector') -> float:
        """Calculate semantic similarity (0-1)"""
        if not self.properties or not other.properties:
            return 0.0
        
        intersection = len(self.properties & other.properties)
        union = len(self.properties | other.properties)
        
        # Jaccard similarity
        base_similarity = intersection / union if union > 0 else 0.0
        
        # Bonus for cross-domain connections (more interesting)
        domain_bonus = 0.2 if self.domain != other.domain else 0.0
        
        return min(1.0, base_similarity + domain_bonus)
    
    def __repr__(self):
        return f"<{self.domain}:{self.name}>"


class ConceptualBlender:
    """Blends concepts to create novel ideas"""
    
    def __init__(self):
        self.concepts: List[SemanticVector] = []
        self.blend_history: Set[str] = set()
    
    def add_concept(self, concept: SemanticVector):
        self.concepts.append(concept)
    
    def blend(self, concept_a: SemanticVector, concept_b: SemanticVector) -> Dict:
        """Create a conceptual blend"""
        
        # Generate unique ID for this blend
        blend_id = hashlib.md5(
            f"{concept_a.name}:{concept_b.name}".encode()
        ).hexdigest()[:8]
        
        # Skip if we've already explored this blend
        if blend_id in self.blend_history:
            return None
        
        self.blend_history.add(blend_id)
        
        # Calculate blend properties
        shared_properties = concept_a.properties & concept_b.properties
        unique_properties = concept_a.properties ^ concept_b.properties
        
        # Generate hypothesis
        hypothesis = self._generate_hypothesis(concept_a, concept_b, shared_properties)
        
        return {
            "id": blend_id,
            "timestamp": datetime.now().isoformat(),
            "concept_a": str(concept_a),
            "concept_b": str(concept_b),
            "similarity": concept_a.similarity(concept_b),
            "shared_properties": list(shared_properties),
            "unique_properties": list(unique_properties),
            "hypothesis": hypothesis,
            "novelty_score": self._calculate_novelty(concept_a, concept_b),
            "status": "dreamed"
        }
    
    def _generate_hypothesis(self, a: SemanticVector, b: SemanticVector, 
                            shared: Set[str]) -> str:
        """Generate a natural language hypothesis"""
        
        templates = [
            f"What if {a.name} could be enhanced using principles from {b.name}?",
            f"Could {b.name} benefit from {a.name}'s approach to {random.choice(list(shared)) if shared else 'optimization'}?",
            f"Hypothesis: Combining {a.domain} and {b.domain} could create a new {a.name}-{b.name} hybrid.",
            f"What if we applied {a.name}'s {random.choice(list(a.properties)) if a.properties else 'pattern'} to {b.name}?",
            f"Could {a.name} and {b.name} share a common {random.choice(list(shared)) if shared else 'interface'}?"
        ]
        
        return random.choice(templates)
    
    def _calculate_novelty(self, a: SemanticVector, b: SemanticVector) -> float:
        """Calculate how novel this blend is (0-1)"""
        
        # More novel if:
        # 1. Concepts are from different domains
        # 2. Low similarity (unexpected combination)
        # 3. Haven't been blended before
        
        domain_diversity = 0.5 if a.domain != b.domain else 0.0
        similarity = a.similarity(b)
        unexpectedness = 1.0 - similarity
        
        return (domain_diversity + unexpectedness) / 2.0


class DreamJournal:
    """Persistent storage for dreams"""
    
    def __init__(self, journal_path: str):
        self.journal_path = Path(journal_path)
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.journal_path.exists():
            with open(self.journal_path, 'r') as f:
                self.dreams = json.load(f)
        else:
            self.dreams = []
    
    def record_dream(self, dream: Dict):
        """Add a dream to the journal"""
        self.dreams.append(dream)
        self._save()
    
    def get_dreams(self, status: str = None, min_novelty: float = 0.0) -> List[Dict]:
        """Retrieve dreams matching criteria"""
        filtered = self.dreams
        
        if status:
            filtered = [d for d in filtered if d.get('status') == status]
        
        if min_novelty > 0:
            filtered = [d for d in filtered if d.get('novelty_score', 0) >= min_novelty]
        
        return filtered
    
    def update_dream_status(self, dream_id: str, status: str, notes: str = ""):
        """Update dream status (dreamed -> validated -> implemented -> failed)"""
        for dream in self.dreams:
            if dream['id'] == dream_id:
                dream['status'] = status
                dream['status_updated'] = datetime.now().isoformat()
                if notes:
                    dream['notes'] = notes
                self._save()
                return True
        return False
    
    def get_statistics(self) -> Dict:
        """Get dream journal statistics"""
        total = len(self.dreams)
        if total == 0:
            return {"total": 0}
        
        statuses = {}
        for dream in self.dreams:
            status = dream.get('status', 'unknown')
            statuses[status] = statuses.get(status, 0) + 1
        
        avg_novelty = sum(d.get('novelty_score', 0) for d in self.dreams) / total
        
        implemented = statuses.get('implemented', 0)
        implementation_rate = implemented / total if total > 0 else 0.0
        
        return {
            "total": total,
            "by_status": statuses,
            "avg_novelty": avg_novelty,
            "implementation_rate": implementation_rate
        }
    
    def _save(self):
        """Persist journal to disk"""
        with open(self.journal_path, 'w') as f:
            json.dump(self.dreams, f, indent=2)


class CodebaseAnalyzer:
    """Extracts semantic concepts from codebase"""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
    
    def extract_concepts(self) -> List[SemanticVector]:
        """Extract concepts from Python files"""
        concepts = []
        
        for py_file in self.root_path.rglob('*.py'):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                # Extract classes and functions
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        concept = self._analyze_class(node, py_file)
                        if concept:
                            concepts.append(concept)
                    elif isinstance(node, ast.FunctionDef):
                        concept = self._analyze_function(node, py_file)
                        if concept:
                            concepts.append(concept)
            
            except Exception as e:
                # Skip files that can't be parsed
                continue
        
        return concepts
    
    def _analyze_class(self, node: ast.ClassDef, file_path: Path) -> SemanticVector:
        """Extract semantic properties from a class"""
        
        # Determine domain from file path
        domain = self._get_domain(file_path)
        
        # Extract properties from methods and docstring
        properties = set()
        
        # Add method names as properties
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                properties.add(item.name)
        
        # Extract keywords from docstring
        docstring = ast.get_docstring(node)
        if docstring:
            keywords = self._extract_keywords(docstring)
            properties.update(keywords)
        
        # Add base classes as properties
        for base in node.bases:
            if isinstance(base, ast.Name):
                properties.add(f"inherits_{base.id}")
        
        return SemanticVector(
            name=node.name,
            domain=domain,
            properties=properties
        )
    
    def _analyze_function(self, node: ast.FunctionDef, file_path: Path) -> SemanticVector:
        """Extract semantic properties from a function"""
        
        # Skip private functions
        if node.name.startswith('_'):
            return None
        
        domain = self._get_domain(file_path)
        properties = set()
        
        # Add parameter names
        for arg in node.args.args:
            properties.add(f"param_{arg.arg}")
        
        # Extract keywords from docstring
        docstring = ast.get_docstring(node)
        if docstring:
            keywords = self._extract_keywords(docstring)
            properties.update(keywords)
        
        return SemanticVector(
            name=node.name,
            domain=domain,
            properties=properties
        )
    
    def _get_domain(self, file_path: Path) -> str:
        """Determine domain from file path"""
        parts = file_path.relative_to(self.root_path).parts
        if len(parts) > 1:
            return parts[0]  # e.g., 'core', 'sensors', 'living_memory'
        return 'root'
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract meaningful keywords from text"""
        # Simple keyword extraction
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        
        # Filter out common words
        stopwords = {'this', 'that', 'with', 'from', 'have', 'will', 'been', 
                    'were', 'their', 'there', 'what', 'when', 'where', 'which'}
        
        keywords = {w for w in words if w not in stopwords}
        
        return keywords


class DreamingEngine:
    """Main dreaming engine - runs during idle cycles"""
    
    def __init__(self, codebase_path: str, journal_path: str = None):
        self.codebase_path = codebase_path
        
        if journal_path is None:
            journal_path = os.path.join(codebase_path, 'living_memory', 'dream_journal.json')
        
        self.journal = DreamJournal(journal_path)
        self.blender = ConceptualBlender()
        self.analyzer = CodebaseAnalyzer(codebase_path)
        
        self.concepts: List[SemanticVector] = []
        self.is_dreaming = False
    
    def wake_up(self):
        """Initialize the dreaming engine"""
        print("\n🌙 Dreaming Engine initializing...")
        print("📚 Analyzing codebase for concepts...")
        
        self.concepts = self.analyzer.extract_concepts()
        
        for concept in self.concepts:
            self.blender.add_concept(concept)
        
        print(f"✨ Extracted {len(self.concepts)} concepts from codebase")
        print(f"📖 Dream journal contains {len(self.journal.dreams)} dreams")
        
        stats = self.journal.get_statistics()
        if stats['total'] > 0:
            print(f"📊 Implementation rate: {stats['implementation_rate']:.1%}")
            print(f"🎯 Average novelty: {stats['avg_novelty']:.2f}")
    
    def dream_cycle(self, num_dreams: int = 5, min_novelty: float = 0.3):
        """Run a single dream cycle"""
        print(f"\n💭 Entering dream state... (generating {num_dreams} dreams)")
        self.is_dreaming = True
        
        dreams_generated = 0
        attempts = 0
        max_attempts = num_dreams * 10  # Prevent infinite loops
        
        while dreams_generated < num_dreams and attempts < max_attempts:
            attempts += 1
            
            # Randomly select two concepts
            if len(self.concepts) < 2:
                print("⚠️  Not enough concepts to blend")
                break
            
            concept_a, concept_b = random.sample(self.concepts, 2)
            
            # Blend them
            dream = self.blender.blend(concept_a, concept_b)
            
            if dream and dream['novelty_score'] >= min_novelty:
                self.journal.record_dream(dream)
                dreams_generated += 1
                
                print(f"\n✨ Dream #{dreams_generated}:")
                print(f"   {dream['hypothesis']}")
                print(f"   Novelty: {dream['novelty_score']:.2f} | Similarity: {dream['similarity']:.2f}")
        
        self.is_dreaming = False
        print(f"\n🌅 Dream cycle complete. Generated {dreams_generated} novel dreams.")
        
        return dreams_generated
    
    def get_promising_dreams(self, min_novelty: float = 0.5) -> List[Dict]:
        """Get dreams worth implementing"""
        return self.journal.get_dreams(status='dreamed', min_novelty=min_novelty)
    
    def validate_dream(self, dream_id: str) -> bool:
        """Mark a dream as validated (worth implementing)"""
        return self.journal.update_dream_status(dream_id, 'validated')
    
    def implement_dream(self, dream_id: str, notes: str = "") -> bool:
        """Mark a dream as implemented"""
        return self.journal.update_dream_status(dream_id, 'implemented', notes)
    
    def reject_dream(self, dream_id: str, reason: str = "") -> bool:
        """Mark a dream as failed/rejected"""
        return self.journal.update_dream_status(dream_id, 'failed', reason)


def main():
    """Demo the dreaming engine"""
    
    # Initialize
    engine = DreamingEngine('/Users/lordwilson/jarvis_m1')
    engine.wake_up()
    
    # Run a dream cycle
    engine.dream_cycle(num_dreams=10, min_novelty=0.3)
    
    # Show promising dreams
    print("\n\n🌟 Most Promising Dreams (novelty >= 0.5):")
    promising = engine.get_promising_dreams(min_novelty=0.5)
    
    for i, dream in enumerate(promising[:5], 1):
        print(f"\n{i}. {dream['hypothesis']}")
        print(f"   Novelty: {dream['novelty_score']:.2f}")
        print(f"   Blending: {dream['concept_a']} + {dream['concept_b']}")
    
    # Show statistics
    print("\n\n📊 Dream Journal Statistics:")
    stats = engine.journal.get_statistics()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
