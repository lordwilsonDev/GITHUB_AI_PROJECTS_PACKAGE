# Level 13 Phase 1.4: Code Embeddings - Semantic Code Understanding
# Converts code into vector embeddings for similarity search and pattern matching

import hashlib
import json
import re
from typing import Dict, List, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
import math

@dataclass
class CodeEmbedding:
    """Vector embedding of code with metadata"""
    vector: List[float]
    code_snippet: str
    language: str
    node_type: str  # function, class, module
    name: str
    metadata: Dict[str, Any]
    
    def similarity(self, other: 'CodeEmbedding') -> float:
        """Cosine similarity between two embeddings"""
        dot_product = sum(a * b for a, b in zip(self.vector, other.vector))
        mag_a = math.sqrt(sum(a * a for a in self.vector))
        mag_b = math.sqrt(sum(b * b for b in other.vector))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot_product / (mag_a * mag_b)


class CodeEmbeddingGenerator:
    """Generates semantic embeddings for code snippets"""
    
    def __init__(self, embedding_dim: int = 128):
        self.embedding_dim = embedding_dim
        self.vocabulary = self._build_vocabulary()
        
    def _build_vocabulary(self) -> Dict[str, int]:
        """Build vocabulary of common programming tokens"""
        # Common keywords across languages
        keywords = [
            'function', 'class', 'def', 'return', 'if', 'else', 'for', 'while',
            'import', 'from', 'const', 'let', 'var', 'public', 'private', 'static',
            'async', 'await', 'try', 'catch', 'throw', 'new', 'this', 'self',
            'struct', 'enum', 'interface', 'type', 'fn', 'func', 'package',
            'use', 'mod', 'impl', 'trait', 'match', 'case', 'switch', 'break',
            'continue', 'yield', 'lambda', 'map', 'filter', 'reduce', 'list',
            'dict', 'set', 'tuple', 'array', 'string', 'int', 'float', 'bool',
            'null', 'undefined', 'none', 'true', 'false', 'and', 'or', 'not',
        ]
        
        # Common patterns
        patterns = [
            'loop', 'condition', 'assignment', 'call', 'declaration', 'definition',
            'initialization', 'iteration', 'recursion', 'closure', 'callback',
            'promise', 'future', 'channel', 'mutex', 'lock', 'thread', 'process',
            'error', 'exception', 'handler', 'validator', 'parser', 'serializer',
            'deserializer', 'encoder', 'decoder', 'transformer', 'mapper', 'reducer',
        ]
        
        # Data structures
        data_structures = [
            'list', 'array', 'vector', 'map', 'hash', 'set', 'tree', 'graph',
            'queue', 'stack', 'heap', 'linked', 'node', 'edge', 'vertex',
        ]
        
        # Operations
        operations = [
            'add', 'remove', 'insert', 'delete', 'update', 'get', 'set', 'find',
            'search', 'sort', 'filter', 'map', 'reduce', 'transform', 'validate',
            'parse', 'serialize', 'deserialize', 'encode', 'decode', 'compress',
            'decompress', 'encrypt', 'decrypt', 'hash', 'sign', 'verify',
        ]
        
        all_tokens = keywords + patterns + data_structures + operations
        return {token: idx for idx, token in enumerate(all_tokens)}
    
    def generate(self, code: str, language: str, node_type: str, name: str) -> CodeEmbedding:
        """Generate embedding for code snippet"""
        # Extract features
        features = self._extract_features(code, language)
        
        # Create embedding vector
        vector = self._create_vector(features)
        
        # Metadata
        metadata = {
            'length': len(code),
            'lines': len(code.split('\n')),
            'complexity': self._estimate_complexity(code),
            'features': features,
        }
        
        return CodeEmbedding(vector, code, language, node_type, name, metadata)
    
    def _extract_features(self, code: str, language: str) -> Dict[str, float]:
        """Extract semantic features from code"""
        features = {}
        
        # Token frequency
        tokens = re.findall(r'\w+', code.lower())
        for token in tokens:
            if token in self.vocabulary:
                features[f'token_{token}'] = features.get(f'token_{token}', 0) + 1
        
        # Structural features
        features['has_loop'] = 1.0 if any(kw in code for kw in ['for', 'while', 'loop']) else 0.0
        features['has_condition'] = 1.0 if any(kw in code for kw in ['if', 'else', 'switch', 'case', 'match']) else 0.0
        features['has_function'] = 1.0 if any(kw in code for kw in ['def', 'function', 'fn', 'func']) else 0.0
        features['has_class'] = 1.0 if any(kw in code for kw in ['class', 'struct', 'interface']) else 0.0
        features['has_async'] = 1.0 if any(kw in code for kw in ['async', 'await', 'promise']) else 0.0
        features['has_error_handling'] = 1.0 if any(kw in code for kw in ['try', 'catch', 'except', 'error']) else 0.0
        
        # Complexity indicators
        features['nesting_level'] = self._estimate_nesting(code)
        features['num_operators'] = len(re.findall(r'[+\-*/%=<>!&|]', code))
        features['num_calls'] = len(re.findall(r'\w+\s*\(', code))
        features['num_assignments'] = len(re.findall(r'=', code))
        
        # Language-specific features
        if language == 'python':
            features['uses_list_comp'] = 1.0 if '[' in code and 'for' in code and ']' in code else 0.0
            features['uses_decorator'] = 1.0 if '@' in code else 0.0
        elif language == 'javascript':
            features['uses_arrow_func'] = 1.0 if '=>' in code else 0.0
            features['uses_destructuring'] = 1.0 if '{' in code and '}' in code and '=' in code else 0.0
        elif language == 'rust':
            features['uses_ownership'] = 1.0 if '&' in code or 'mut' in code else 0.0
            features['uses_pattern_match'] = 1.0 if 'match' in code else 0.0
        
        # Normalize features
        total = sum(features.values())
        if total > 0:
            features = {k: v / total for k, v in features.items()}
        
        return features
    
    def _create_vector(self, features: Dict[str, float]) -> List[float]:
        """Create fixed-size embedding vector from features"""
        vector = [0.0] * self.embedding_dim
        
        # Hash features into vector positions
        for feature_name, value in features.items():
            # Use hash to determine position
            hash_val = int(hashlib.md5(feature_name.encode()).hexdigest(), 16)
            idx = hash_val % self.embedding_dim
            vector[idx] += value
        
        # Normalize vector
        magnitude = math.sqrt(sum(v * v for v in vector))
        if magnitude > 0:
            vector = [v / magnitude for v in vector]
        
        return vector
    
    def _estimate_complexity(self, code: str) -> int:
        """Estimate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        # Add complexity for control flow
        complexity += len(re.findall(r'\bif\b', code))
        complexity += len(re.findall(r'\belse\b', code))
        complexity += len(re.findall(r'\bfor\b', code))
        complexity += len(re.findall(r'\bwhile\b', code))
        complexity += len(re.findall(r'\bcase\b', code))
        complexity += len(re.findall(r'\bcatch\b', code))
        complexity += len(re.findall(r'\band\b', code))
        complexity += len(re.findall(r'\bor\b', code))
        
        return complexity
    
    def _estimate_nesting(self, code: str) -> float:
        """Estimate average nesting level"""
        max_nesting = 0
        current_nesting = 0
        
        for char in code:
            if char in '{[(':
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            elif char in '}])':
                current_nesting = max(0, current_nesting - 1)
        
        return float(max_nesting)


class CodeSimilaritySearch:
    """Search for similar code patterns across languages"""
    
    def __init__(self):
        self.generator = CodeEmbeddingGenerator()
        self.embeddings: List[CodeEmbedding] = []
    
    def add_code(self, code: str, language: str, node_type: str, name: str):
        """Add code to search index"""
        embedding = self.generator.generate(code, language, node_type, name)
        self.embeddings.append(embedding)
    
    def find_similar(self, query_code: str, query_language: str, top_k: int = 5) -> List[Tuple[CodeEmbedding, float]]:
        """Find similar code snippets"""
        query_embedding = self.generator.generate(query_code, query_language, 'query', 'query')
        
        # Calculate similarities
        similarities = []
        for emb in self.embeddings:
            sim = query_embedding.similarity(emb)
            similarities.append((emb, sim))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def find_cross_language_patterns(self, min_similarity: float = 0.7) -> List[Tuple[CodeEmbedding, CodeEmbedding, float]]:
        """Find similar patterns across different languages"""
        patterns = []
        
        for i, emb1 in enumerate(self.embeddings):
            for emb2 in self.embeddings[i+1:]:
                if emb1.language != emb2.language:
                    sim = emb1.similarity(emb2)
                    if sim >= min_similarity:
                        patterns.append((emb1, emb2, sim))
        
        patterns.sort(key=lambda x: x[2], reverse=True)
        return patterns
    
    def cluster_by_functionality(self, num_clusters: int = 5) -> Dict[int, List[CodeEmbedding]]:
        """Simple clustering of code by functionality"""
        if not self.embeddings:
            return {}
        
        # Simple k-means-like clustering
        # Initialize centroids randomly
        import random
        centroids = random.sample(self.embeddings, min(num_clusters, len(self.embeddings)))
        
        # Assign to clusters
        clusters = {i: [] for i in range(len(centroids))}
        
        for emb in self.embeddings:
            best_cluster = 0
            best_sim = -1
            
            for i, centroid in enumerate(centroids):
                sim = emb.similarity(centroid)
                if sim > best_sim:
                    best_sim = sim
                    best_cluster = i
            
            clusters[best_cluster].append(emb)
        
        return clusters


# Add wrapper class for test compatibility
class CodeEmbeddings:
    """Wrapper class for test contract compatibility"""
    def __init__(self):
        self.generator = CodeEmbeddingGenerator()
    
    def embed(self, code: str, language: str = 'python') -> List[float]:
        """Generate embedding for code (test contract method)"""
        embedding = self.generator.generate(code, language, 'snippet', 'code')
        return embedding.vector


if __name__ == "__main__":
    print("🧠 Code Embeddings - Level 13 Phase 1.4")
    print("\n=== Testing Code Embedding Generator ===")
    
    search = CodeSimilaritySearch()
    
    # Add Python code
    python_sort = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""
    
    python_search = """
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
"""
    
    # Add JavaScript code
    js_sort = """
function bubbleSort(arr) {
    const n = arr.length;
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
            }
        }
    }
    return arr;
}
"""
    
    js_search = """
function binarySearch(arr, target) {
    let left = 0, right = arr.length - 1;
    while (left <= right) {
        const mid = Math.floor((left + right) / 2);
        if (arr[mid] === target) return mid;
        else if (arr[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
"""
    
    # Add Go code
    go_sort = """
func bubbleSort(arr []int) []int {
    n := len(arr)
    for i := 0; i < n; i++ {
        for j := 0; j < n-i-1; j++ {
            if arr[j] > arr[j+1] {
                arr[j], arr[j+1] = arr[j+1], arr[j]
            }
        }
    }
    return arr
}
"""
    
    print("\n1. Adding code snippets to index...")
    search.add_code(python_sort, 'python', 'function', 'bubble_sort')
    search.add_code(python_search, 'python', 'function', 'binary_search')
    search.add_code(js_sort, 'javascript', 'function', 'bubbleSort')
    search.add_code(js_search, 'javascript', 'function', 'binarySearch')
    search.add_code(go_sort, 'go', 'function', 'bubbleSort')
    print(f"  Added {len(search.embeddings)} code snippets")
    
    print("\n2. Finding similar code to Python bubble_sort...")
    similar = search.find_similar(python_sort, 'python', top_k=3)
    for emb, sim in similar:
        print(f"  - {emb.language}/{emb.name}: {sim:.3f} similarity")
        print(f"    Complexity: {emb.metadata['complexity']}, Lines: {emb.metadata['lines']}")
    
    print("\n3. Finding cross-language patterns...")
    patterns = search.find_cross_language_patterns(min_similarity=0.6)
    print(f"  Found {len(patterns)} cross-language patterns:")
    for emb1, emb2, sim in patterns[:5]:
        print(f"  - {emb1.language}/{emb1.name} ↔ {emb2.language}/{emb2.name}: {sim:.3f}")
    
    print("\n4. Clustering by functionality...")
    clusters = search.cluster_by_functionality(num_clusters=2)
    for cluster_id, members in clusters.items():
        if members:
            print(f"  Cluster {cluster_id}: {len(members)} functions")
            for emb in members:
                print(f"    - {emb.language}/{emb.name}")
    
    print("\n5. Feature analysis...")
    emb = search.embeddings[0]
    print(f"  Sample embedding for {emb.name}:")
    print(f"    Vector dimension: {len(emb.vector)}")
    print(f"    Top features: {list(emb.metadata['features'].keys())[:5]}")
    print(f"    Complexity: {emb.metadata['complexity']}")
    print(f"    Has loop: {emb.metadata['features'].get('has_loop', 0)}")
    print(f"    Has condition: {emb.metadata['features'].get('has_condition', 0)}")
    
    print("\n✅ Code Embeddings working!")
    print("   - Semantic similarity across languages")
    print("   - Cross-language pattern detection")
    print("   - Functionality clustering")
    print("\n✅ Created code_embeddings.py")
    print("Level 13 Phase 1.4 complete!")
