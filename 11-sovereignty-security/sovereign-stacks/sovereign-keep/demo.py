#!/usr/bin/env python3
"""
Demo script to test the Sovereign Keep Protocol with sample data.
"""

import json
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.analysis import SemanticAuditor

class MockNote:
    """Mock note object for demo."""
    def __init__(self, data):
        self.id = data.get('title', 'untitled')
        self.title = data.get('title', '')
        self.text = data.get('textContent', '')
        self.labels = [label['name'] for label in data.get('labels', [])]
        self.color = data.get('color', 'DEFAULT')
        self.trashed = data.get('isTrashed', False)
        self.archived = data.get('isArchived', False)
        self.pinned = data.get('isPinned', False)
        
        # Convert timestamp
        timestamp_usec = data.get('userEditedTimestampUsec', 0)
        self.updated = datetime.fromtimestamp(timestamp_usec / 1000000)

class MockKeep:
    """Mock Keep client for demo."""
    def __init__(self, notes_data):
        self.notes = [MockNote(note) for note in notes_data]
    
    def all(self):
        return self.notes

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Demo the Sovereign Keep Protocol')
    parser.add_argument('--threshold', type=float, 
                       default=float(os.getenv('THRESHOLD', 0.85)),
                       help='Similarity threshold for clustering (default: 0.85)')
    parser.add_argument('--quiet', action='store_true',
                       help='Disable progress bars for deterministic output')
    args = parser.parse_args()
    
    threshold = args.threshold
    quiet = args.quiet
    
    print("\n" + "="*70)
    print("  SOVEREIGN KEEP PROTOCOL - DEMO")
    print("="*70 + "\n")
    
    # Load sample data
    demo_file = Path(__file__).parent / 'demo_data' / 'sample_notes.json'
    print(f"Loading sample notes from: {demo_file}")
    
    with open(demo_file, 'r') as f:
        notes_data = json.load(f)
    
    print(f"Loaded {len(notes_data)} sample notes\n")
    
    # Create mock Keep client
    mock_keep = MockKeep(notes_data)
    
    # Initialize semantic auditor
    print("Initializing Semantic Auditor...")
    print("  - Loading all-MiniLM-L6-v2 model...")
    auditor = SemanticAuditor(mock_keep, quiet=quiet)
    print("  ✓ Model loaded\n")
    
    # Calculate entropy for all notes
    print("Analyzing note vitality (entropy + age)...")
    print("-" * 70)
    
    vitality_scores = []
    for note in mock_keep.all():
        if not note.trashed and not note.archived:
            entropy = auditor.calculate_entropy(note.text)
            age_days = (datetime.now() - note.updated).days
            # Calculate vitality: higher entropy = more valuable, older = less valuable
            vitality = entropy / (1 + age_days / 30.0)  # Decay over months
            vitality_scores.append((note.title, entropy, age_days, vitality))
    
    # Sort by vitality
    vitality_scores.sort(key=lambda x: x[3], reverse=True)
    
    print(f"{'Note Title':<35} {'Entropy':<10} {'Age (days)':<12} {'Vitality'}")
    print("-" * 70)
    for title, entropy, age, vitality in vitality_scores:
        print(f"{title[:34]:<35} {entropy:<10.2f} {age:<12} {vitality:.2f}")
    
    # Find redundancy clusters
    print("\n" + "="*70)
    print(f"Finding redundancy clusters (similarity threshold: {threshold})...")
    print("="*70 + "\n")
    
    clusters = auditor.find_redundancy_clusters(threshold=threshold)
    
    if clusters:
        print(f"Found {len(clusters)} redundancy cluster(s):\n")
        
        for i, cluster in enumerate(clusters, 1):
            print(f"Cluster {i}: {len(cluster)} similar notes")
            print("-" * 70)
            
            # Get notes in cluster
            cluster_notes = [n for n in mock_keep.all() if n.id in cluster]
            
            for note in cluster_notes:
                print(f"  • {note.title}")
                print(f"    Preview: {note.text[:60]}...")
                print(f"    Labels: {', '.join(note.labels) if note.labels else 'None'}")
                print(f"    Updated: {note.updated.strftime('%Y-%m-%d')}")
                print()
            
            # Identify survivor
            survivor = max(cluster_notes, key=lambda n: (len(n.text), n.updated))
            print(f"  → Recommended survivor: '{survivor.title}'")
            print(f"    (Most detailed: {len(survivor.text)} chars)\n")
    else:
        print("No redundancy clusters found.\n")
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total notes analyzed: {len([n for n in mock_keep.all() if not n.trashed and not n.archived])}")
    print(f"Redundancy clusters found: {len(clusters)}")
    print(f"Potential duplicates: {sum(len(c) - 1 for c in clusters)}")
    print(f"\nHighest vitality: {vitality_scores[0][0]} ({vitality_scores[0][3]:.2f})")
    print(f"Lowest vitality: {vitality_scores[-1][0]} ({vitality_scores[-1][3]:.2f})")
    print("\n" + "="*70)
    print("Demo complete! The semantic analysis engine is working correctly.")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
