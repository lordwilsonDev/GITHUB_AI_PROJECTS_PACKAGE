#!/usr/bin/env python3
"""
Semantic Analysis Test Script for Sovereign Keep Protocol
Tests the semantic clustering without modifying any notes.
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from auth import SovereignAuth
from analysis import SemanticAuditor

def test_semantic_analysis(email, threshold=0.85):
    """
    Test semantic analysis and display potential duplicates.
    """
    print("="*60)
    print("Sovereign Keep Protocol - Semantic Analysis Test")
    print("="*60)
    print(f"\nEmail: {email}")
    print(f"Similarity Threshold: {threshold}")
    print("\n" + "-"*60 + "\n")
    
    try:
        # Authenticate
        print("Authenticating...")
        auth = SovereignAuth(email)
        keep = auth.login()
        print("✅ Authenticated\n")
        
        # Sync
        print("Syncing with Google Keep...")
        keep.sync()
        print("✅ Synced\n")
        
        # Initialize semantic auditor
        print("Loading semantic analysis model...")
        print("(First run may take 30-60 seconds to download model)")
        auditor = SemanticAuditor(keep)
        print("✅ Model loaded\n")
        
        # Get active notes
        all_notes = list(keep.all())
        active_notes = [n for n in all_notes if not n.trashed and not n.archived]
        
        print(f"Analyzing {len(active_notes)} active notes...\n")
        
        # Calculate entropy for all notes
        print("Calculating information entropy...")
        entropy_scores = []
        for note in active_notes:
            text = f"{note.title} {note.text}"
            entropy = auditor.calculate_entropy(text)
            age_days = (datetime.now() - note.timestamps.updated).days
            entropy_scores.append({
                'note': note,
                'entropy': entropy,
                'age_days': age_days,
                'length': len(text)
            })
        
        # Sort by entropy
        entropy_scores.sort(key=lambda x: x['entropy'], reverse=True)
        
        print("\nTop 5 Highest Entropy Notes (Most Unique):")
        for i, item in enumerate(entropy_scores[:5], 1):
            title = item['note'].title or "(Untitled)"
            print(f"  {i}. {title}")
            print(f"     Entropy: {item['entropy']:.2f} | Age: {item['age_days']} days | Length: {item['length']} chars")
        
        print("\nTop 5 Lowest Entropy Notes (Most Repetitive):")
        for i, item in enumerate(entropy_scores[-5:], 1):
            title = item['note'].title or "(Untitled)"
            print(f"  {i}. {title}")
            print(f"     Entropy: {item['entropy']:.2f} | Age: {item['age_days']} days | Length: {item['length']} chars")
        
        # Find redundancy clusters
        print(f"\n" + "-"*60)
        print(f"Finding semantic clusters (threshold: {threshold})...")
        print("This may take 1-2 minutes for large note collections...\n")
        
        clusters = auditor.find_redundancy_clusters(threshold=threshold)
        
        if not clusters:
            print("✅ No redundant clusters found!")
            print("\nYour notes are semantically diverse.")
            print("Try lowering the threshold (e.g., 0.80) to find looser similarities.")
        else:
            print(f"Found {len(clusters)} redundant clusters:\n")
            
            for i, cluster in enumerate(clusters, 1):
                print(f"\nCluster {i} ({len(cluster)} notes):")
                cluster_notes = [keep.get(nid) for nid in cluster]
                
                for j, note in enumerate(cluster_notes, 1):
                    title = note.title or "(Untitled)"
                    text_preview = note.text[:60] + "..." if len(note.text) > 60 else note.text
                    age_days = (datetime.now() - note.timestamps.updated).days
                    print(f"  {j}. {title}")
                    print(f"     Preview: {text_preview}")
                    print(f"     Age: {age_days} days | Length: {len(note.text)} chars")
                    if note.labels:
                        labels = ", ".join([l.name for l in note.labels])
                        print(f"     Labels: {labels}")
                
                # Identify survivor
                survivor = max(cluster_notes, key=lambda n: (len(n.text), n.timestamps.updated))
                survivor_title = survivor.title or "(Untitled)"
                print(f"  ➡️  Recommended survivor: {survivor_title}")
        
        print("\n" + "="*60)
        print("✅ Semantic analysis completed!")
        print("="*60)
        print("\nThis was a DRY RUN - no notes were modified.")
        print("\nTo execute archival, use: python src/main.py --execute")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_semantic.py your.email@gmail.com [threshold]")
        print("Example: python test_semantic.py user@gmail.com 0.85")
        sys.exit(1)
    
    email = sys.argv[1]
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.85
    
    success = test_semantic_analysis(email, threshold)
    sys.exit(0 if success else 1)
