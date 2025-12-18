#!/usr/bin/env python3
"""
Standalone Analyzer for Sovereign Keep Protocol

Analyzes notes from Google Takeout export without requiring Keep API access.
This is the production-ready version that works with exported data.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import argparse

from analysis import SemanticAuditor
from takeout_parser import TakeoutParser, TakeoutNote


class MockKeepNote:
    """Mock Keep note object for compatibility with SemanticAuditor."""
    
    def __init__(self, takeout_note: TakeoutNote):
        self.id = takeout_note.id
        self.title = takeout_note.title
        self.text = takeout_note.text
        self.labels = takeout_note.labels
        self.color = takeout_note.color
        self.archived = takeout_note.archived
        self.trashed = takeout_note.trashed
        self.pinned = takeout_note.pinned
        
        # Mock timestamps object
        class Timestamps:
            def __init__(self, created, updated):
                self.created = created
                self.updated = updated
        
        self.timestamps = Timestamps(takeout_note.created, takeout_note.updated)


class StandaloneAnalyzer:
    """Analyzes notes from Takeout export."""
    
    def __init__(self, takeout_path: str, threshold: float = 0.85):
        """
        Initialize analyzer.
        
        Args:
            takeout_path: Path to Takeout/Keep directory
            threshold: Similarity threshold for clustering (0.0-1.0)
        """
        self.takeout_path = takeout_path
        self.threshold = threshold
        self.parser = TakeoutParser(takeout_path)
        self.notes = []
        self.mock_notes = []
    
    def load_notes(self):
        """Load and parse notes from Takeout export."""
        print("\n=== Loading Notes from Takeout ===")
        self.notes = self.parser.parse_all_notes()
        
        # Filter to active notes only
        active_notes = self.parser.filter_active_notes(self.notes)
        
        # Convert to mock Keep notes for analysis
        self.mock_notes = [MockKeepNote(note) for note in active_notes]
        
        print(f"Loaded {len(self.mock_notes)} active notes for analysis")
    
    def analyze(self) -> Dict:
        """Run semantic analysis on loaded notes."""
        if not self.mock_notes:
            raise ValueError("No notes loaded. Call load_notes() first.")
        
        print("\n=== Running Semantic Analysis ===")
        print("This may take a few moments...\n")
        
        # Create mock Keep client
        class MockKeep:
            def __init__(self, notes):
                self._notes = notes
            
            def all(self):
                return self._notes
        
        mock_keep = MockKeep(self.mock_notes)
        auditor = SemanticAuditor(mock_keep)
        
        # Calculate entropy and vitality for all notes
        print("1. Calculating information entropy...")
        note_stats = []
        for note in self.mock_notes:
            content = f"{note.title} {note.text}"
            entropy = auditor.calculate_entropy(content)
            vitality = auditor.calculate_vitality_score(note)
            
            note_stats.append({
                'id': note.id,
                'title': note.title,
                'entropy': entropy,
                'vitality': vitality,
                'length': len(content),
                'age_days': (datetime.now() - note.timestamps.updated).days
            })
        
        # Sort by vitality (lowest = candidates for archival)
        note_stats.sort(key=lambda x: x['vitality'])
        
        # Find redundancy clusters
        print("2. Detecting semantic duplicates...")
        clusters = auditor.find_redundancy_clusters(threshold=self.threshold)
        
        # Prepare results
        results = {
            'total_notes': len(self.mock_notes),
            'threshold': self.threshold,
            'analysis_date': datetime.now().isoformat(),
            'note_statistics': note_stats,
            'redundancy_clusters': [],
            'low_vitality_notes': note_stats[:10],  # Bottom 10
            'high_vitality_notes': note_stats[-10:]  # Top 10
        }
        
        # Process clusters
        if clusters:
            print(f"3. Found {len(clusters)} redundancy clusters")
            for i, cluster in enumerate(clusters, 1):
                cluster_notes = []
                for note_id in cluster:
                    note = next((n for n in self.mock_notes if n.id == note_id), None)
                    if note:
                        cluster_notes.append({
                            'id': note.id,
                            'title': note.title,
                            'text_preview': note.text[:100] + '...' if len(note.text) > 100 else note.text,
                            'length': len(note.text)
                        })
                
                # Identify survivor (longest/most detailed)
                survivor = max(cluster_notes, key=lambda x: x['length'])
                
                results['redundancy_clusters'].append({
                    'cluster_id': i,
                    'size': len(cluster_notes),
                    'survivor': survivor,
                    'duplicates': [n for n in cluster_notes if n['id'] != survivor['id']]
                })
        else:
            print("3. No redundancy clusters found")
        
        return results
    
    def generate_report(self, results: Dict, output_path: str = None):
        """Generate human-readable analysis report."""
        if output_path is None:
            output_path = '../data/analysis_report.txt'
        
        report_lines = []
        report_lines.append("="*70)
        report_lines.append("SOVEREIGN KEEP PROTOCOL - ANALYSIS REPORT")
        report_lines.append("="*70)
        report_lines.append(f"Analysis Date: {results['analysis_date']}")
        report_lines.append(f"Total Notes Analyzed: {results['total_notes']}")
        report_lines.append(f"Similarity Threshold: {results['threshold']}")
        report_lines.append("="*70)
        
        # Redundancy clusters
        report_lines.append("\n### REDUNDANCY CLUSTERS (Duplicate Thoughts) ###\n")
        if results['redundancy_clusters']:
            for cluster in results['redundancy_clusters']:
                report_lines.append(f"\nCluster {cluster['cluster_id']}: {cluster['size']} similar notes")
                report_lines.append(f"  KEEP: '{cluster['survivor']['title']}'")
                report_lines.append(f"        (ID: {cluster['survivor']['id']}, Length: {cluster['survivor']['length']} chars)")
                report_lines.append("  ARCHIVE:")
                for dup in cluster['duplicates']:
                    report_lines.append(f"    - '{dup['title']}'")
                    report_lines.append(f"      (ID: {dup['id']}, Length: {dup['length']} chars)")
                    report_lines.append(f"      Preview: {dup['text_preview']}")
        else:
            report_lines.append("No redundancy clusters found. Your notes are well-organized!")
        
        # Low vitality notes
        report_lines.append("\n\n### LOW VITALITY NOTES (Candidates for Archival) ###\n")
        report_lines.append("These notes have low information density and/or are very old:\n")
        for i, note in enumerate(results['low_vitality_notes'][:5], 1):
            report_lines.append(f"{i}. '{note['title']}'")
            report_lines.append(f"   Vitality: {note['vitality']:.3f} | Entropy: {note['entropy']:.2f} | Age: {note['age_days']} days")
            report_lines.append(f"   ID: {note['id']}\n")
        
        # High vitality notes
        report_lines.append("\n### HIGH VITALITY NOTES (Your Best Ideas) ###\n")
        report_lines.append("These notes have high information density and are valuable:\n")
        for i, note in enumerate(reversed(results['high_vitality_notes'][-5:]), 1):
            report_lines.append(f"{i}. '{note['title']}'")
            report_lines.append(f"   Vitality: {note['vitality']:.3f} | Entropy: {note['entropy']:.2f} | Age: {note['age_days']} days")
            report_lines.append(f"   ID: {note['id']}\n")
        
        # Summary
        report_lines.append("\n" + "="*70)
        report_lines.append("SUMMARY")
        report_lines.append("="*70)
        total_duplicates = sum(len(c['duplicates']) for c in results['redundancy_clusters'])
        report_lines.append(f"Total duplicate notes found: {total_duplicates}")
        report_lines.append(f"Total redundancy clusters: {len(results['redundancy_clusters'])}")
        report_lines.append(f"Potential space savings: {total_duplicates} notes can be archived")
        report_lines.append("\nNext Steps:")
        report_lines.append("1. Review the redundancy clusters above")
        report_lines.append("2. Manually archive duplicate notes in Google Keep")
        report_lines.append("3. Consider archiving low-vitality notes")
        report_lines.append("4. Re-run analysis periodically to maintain hygiene")
        report_lines.append("="*70)
        
        report_text = '\n'.join(report_lines)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"\n✓ Report saved to: {output_path}")
        
        # Also print to console
        print("\n" + report_text)
        
        return report_text
    
    def export_results_json(self, results: Dict, output_path: str = None):
        """Export results as JSON for programmatic access."""
        if output_path is None:
            output_path = '../data/analysis_results.json'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"✓ JSON results saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Sovereign Keep Protocol - Standalone Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python standalone_analyzer.py ~/Downloads/Takeout/Keep
  python standalone_analyzer.py ~/Downloads/Takeout/Keep --threshold 0.90
  python standalone_analyzer.py ~/Downloads/Takeout/Keep --output-dir ./reports
        """
    )
    
    parser.add_argument(
        'takeout_path',
        help='Path to the Takeout/Keep directory'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.85,
        help='Similarity threshold for clustering (0.0-1.0, default: 0.85)'
    )
    parser.add_argument(
        '--output-dir',
        default='../data',
        help='Directory for output files (default: ../data)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize analyzer
        analyzer = StandaloneAnalyzer(args.takeout_path, args.threshold)
        
        # Load notes
        analyzer.load_notes()
        
        if len(analyzer.mock_notes) == 0:
            print("\nNo active notes found to analyze.")
            return
        
        # Run analysis
        results = analyzer.analyze()
        
        # Generate reports
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = output_dir / 'analysis_report.txt'
        json_path = output_dir / 'analysis_results.json'
        
        analyzer.generate_report(results, str(report_path))
        analyzer.export_results_json(results, str(json_path))
        
        print("\n" + "="*70)
        print("✓ ANALYSIS COMPLETE")
        print("="*70)
        
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nMake sure you've exported your Keep notes via Google Takeout:")
        print("1. Go to https://takeout.google.com")
        print("2. Select only 'Keep'")
        print("3. Download and extract the archive")
        print("4. Run this script with the path to the 'Keep' folder")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
