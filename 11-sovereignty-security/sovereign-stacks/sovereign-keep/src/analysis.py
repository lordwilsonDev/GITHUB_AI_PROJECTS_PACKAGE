"""
Sovereign Keep Protocol - Semantic Analysis Engine
Implements entropy calculation, vector embeddings, and graph-based clustering.
"""

import math
import networkx as nx
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Tuple
import numpy as np
from datetime import datetime, timezone
from .text_utils import (
    normalize_text, shannon_entropy, to_utc_aware,
    strip_boilerplate, numeric_conflict, negation_conflict
)




# ============================================================================
# MODULE-LEVEL MODEL SINGLETON (Fix #1: Prevents repeated model loading)
# ============================================================================
_MODEL_CACHE = {}

def get_embedding_model(model_name='all-MiniLM-L6-v2'):
    """Get or create the embedding model singleton."""
    if model_name not in _MODEL_CACHE:
        print(f"[Analysis] Loading embedding model: {model_name}...")
        _MODEL_CACHE[model_name] = SentenceTransformer(model_name)
        print(f"[Analysis] ✓ Model loaded successfully.")
    return _MODEL_CACHE[model_name]


class SemanticAuditor:
    """
    Analyzes notes for semantic redundancy using vector embeddings and graph theory.
    Calculates information entropy to identify valuable vs. stale content.
    """
    
    def __init__(self, keep_client=None, model_name='all-MiniLM-L6-v2', quiet=False):
        """
        Initialize the semantic auditor.
        
        Args:
            keep_client: Authenticated gkeepapi.Keep instance (optional for testing)
            model_name: Sentence transformer model to use for embeddings
            quiet: If True, disable progress bars for deterministic output
        """
        self.keep = keep_client
        self.quiet = quiet
        # Use singleton model (Fix #1)
        self.model = get_embedding_model(model_name)
        
    def normalize(self, text: str) -> str:
        """Normalize text (wrapper for pure function)."""
        return normalize_text(text)
    
    def calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy (wrapper for pure function)."""
        return shannon_entropy(text)
    
    def calculate_vitality_score(self, note, alpha=0.7, beta=0.3) -> float:
        """
        Calculate vitality score combining entropy and recency.
        
        Args:
            note: gkeepapi Note object
            alpha: Weight for entropy component
            beta: Weight for age component
            
        Returns:
            float: Vitality score (higher = more valuable)
        """
        # Combine title and text for analysis
        full_text = f"{note.title} {note.text}"
        entropy = self.calculate_entropy(full_text)
        
        # Calculate age in days
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        last_updated = note.timestamps.updated
        age_days = (now - last_updated).days + 1  # +1 to avoid division by zero
        
        # Vitality = α * entropy + β * (1/age)
        # High entropy + recent = high vitality
        vitality = alpha * entropy + beta * (1.0 / age_days)
        
        return vitality
    
    def find_redundancy_clusters(self, notes=None, *, threshold=0.85, include_archived=False) -> List[List[str]]:
        """
        Find clusters of semantically similar notes using graph-based community detection.
        
        Args:
            notes: Optional list of note objects. If None, fetches from self.keep
            threshold: Cosine similarity threshold (0-1) for considering notes similar
            include_archived: Whether to include archived notes in analysis
            
        Returns:
            List of clusters, where each cluster is a list of note IDs
        """
        if notes is None:
            print("[Analysis] Fetching notes...")
            notes = list(self.keep.all())
        else:
            print(f"[Analysis] Using provided {len(notes)} notes...")
        
        # Filter notes
        if not include_archived:
            notes = [n for n in notes if not n.trashed and not n.archived]
        else:
            notes = [n for n in notes if not n.trashed]
        
        print(f"[Analysis] Analyzing {len(notes)} notes...")
        
        if len(notes) < 2:
            print("[Analysis] Not enough notes to find clusters.")
            return []
        
        # Create documents from title + body
        docs = []
        for note in notes:
            doc = f"{note.title} {note.text}".strip()
            if not doc:  # Handle empty notes
                doc = "[Empty Note]"
            docs.append(doc)
        
        print("[Analysis] Generating embeddings...")
        # Disable progress bar if quiet mode or not a TTY
        import sys
        show_progress = not self.quiet and sys.stdout.isatty()
        embeddings = self.model.encode(docs, convert_to_tensor=True, show_progress_bar=show_progress)
        
        print("[Analysis] Calculating similarity matrix...")
        cosine_scores = util.cos_sim(embeddings, embeddings)
        
        # Build graph
        print(f"[Analysis] Building similarity graph (threshold={threshold})...")
        G = nx.Graph()
        
        # Add all notes as nodes
        for note in notes:
            G.add_node(note.id)
        
        # Add edges for similar notes
        edge_count = 0
        for i in range(len(notes)):
            for j in range(i + 1, len(notes)):
                score = float(cosine_scores[i][j])
                if score >= threshold:
                    G.add_edge(notes[i].id, notes[j].id, weight=score)
                    edge_count += 1
        
        print(f"[Analysis] Found {edge_count} similarity connections.")
        
        # Find connected components (clusters)
        clusters = list(nx.connected_components(G))
        
        # Filter to only clusters with 2+ notes
        significant_clusters = [list(cluster) for cluster in clusters if len(cluster) > 1]
        
        print(f"[Analysis] ✓ Found {len(significant_clusters)} redundancy clusters.")
        
        return significant_clusters
    
    def get_similarity_score(self, note1, note2) -> float:
        """
        Calculate semantic similarity between two notes.
        
        Args:
            note1: First gkeepapi Note object
            note2: Second gkeepapi Note object
            
        Returns:
            float: Cosine similarity score (0-1)
        """
        doc1 = f"{note1.title} {note1.text}".strip() or "[Empty]"
        doc2 = f"{note2.title} {note2.text}".strip() or "[Empty]"
        
        embeddings = self.model.encode([doc1, doc2], convert_to_tensor=True)
        similarity = util.cos_sim(embeddings[0], embeddings[1])
        
        return float(similarity[0][0])
    
    def analyze_note_quality(self, note) -> Dict:
        """
        Comprehensive quality analysis of a single note.
        
        Args:
            note: gkeepapi Note object
            
        Returns:
            dict: Analysis results including entropy, vitality, length, etc.
        """
        full_text = f"{note.title} {note.text}"
        
        return {
            'id': note.id,
            'title': note.title,
            'length': len(full_text),
            'entropy': self.calculate_entropy(full_text),
            'vitality': self.calculate_vitality_score(note),
            'age_days': (datetime.datetime.now(datetime.timezone.utc) - note.timestamps.updated).days,
            'is_archived': note.archived,
            'is_trashed': note.trashed,
            'label_count': len(note.labels.all()),
        }


# Example usage
if __name__ == "__main__":
    import sys
    from auth import SovereignAuth
    
    if len(sys.argv) < 2:
        print("Usage: python analysis.py <your-email@gmail.com>")
        sys.exit(1)
    
    email = sys.argv[1]
    
    # Authenticate
    auth = SovereignAuth(email)
    keep = auth.login()
    auth.sync()
    
    # Run analysis
    auditor = SemanticAuditor(keep)
    
    print("\n=== Finding Redundancy Clusters ===")
    clusters = auditor.find_redundancy_clusters(threshold=0.85)
    
    if clusters:
        for i, cluster in enumerate(clusters, 1):
            print(f"\nCluster {i}: {len(cluster)} similar notes")
            for note_id in cluster:
                note = keep.get(note_id)
                print(f"  - {note.title[:50]}... (ID: {note_id[:8]}...)")
    else:
        print("No redundancy clusters found.")
    
    print("\n=== Sample Entropy Analysis ===")
    notes = [n for n in keep.all() if not n.trashed and not n.archived][:5]
    for note in notes:
        analysis = auditor.analyze_note_quality(note)
        print(f"\nNote: {analysis['title'][:40]}")
        print(f"  Entropy: {analysis['entropy']:.2f}")
        print(f"  Vitality: {analysis['vitality']:.4f}")
        print(f"  Age: {analysis['age_days']} days")
