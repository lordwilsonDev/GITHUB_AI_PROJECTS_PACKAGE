"""
Sovereign Keep Protocol - Action Layer (Reaper)
Implements safe, reversible note archival and cluster processing.
"""

from typing import List
import datetime


class SovereignReaper:
    """
    Processes redundancy clusters by archiving duplicates while preserving
    the most valuable note. Never deletes - only archives with tombstone links.
    """
    
    def __init__(self, keep_client, dry_run=True):
        """
        Initialize the reaper.
        
        Args:
            keep_client: Authenticated gkeepapi.Keep instance
            dry_run: If True, only simulate actions without making changes
        """
        self.keep = keep_client
        self.dry_run = dry_run
        self.actions_log = []
        
    def process_cluster(self, note_ids: List[str], auditor=None) -> dict:
        """
        Process a cluster of similar notes by selecting a survivor and archiving the rest.
        
        Args:
            note_ids: List of note IDs in the cluster
            auditor: Optional SemanticAuditor for similarity scoring
            
        Returns:
            dict: Processing results including survivor ID and archived IDs
        """
        if len(note_ids) < 2:
            return {'status': 'skipped', 'reason': 'cluster too small'}
        
        # Fetch all notes in cluster
        notes = [self.keep.get(nid) for nid in note_ids]
        
        # Check for label divergence - don't merge notes with different contexts
        labels_sets = [set(n.labels.all()) for n in notes]
        if len(labels_sets) > 1:
            # Check if there's significant label divergence
            all_labels = set().union(*labels_sets)
            if len(all_labels) > 0:
                # If notes have completely different labels, be cautious
                unique_label_counts = [len(labels) for labels in labels_sets]
                if max(unique_label_counts) - min(unique_label_counts) > 2:
                    print(f"[Reaper] ⚠ Cluster has significant label divergence, skipping merge")
                    return {'status': 'skipped', 'reason': 'label divergence'}
        
        # Ranking criteria:
        # 1. Length of text (more detail = better)
        # 2. Last updated timestamp (more recent = better)
        # 3. Number of labels (more context = better)
        def rank_note(note):
            full_text = f"{note.title} {note.text}"
            return (
                len(full_text),
                note.timestamps.updated,
                len(note.labels.all())
            )
        
        # Select survivor (highest ranked note)
        survivor = max(notes, key=rank_note)
        
        print(f"\n[Reaper] Processing cluster of {len(notes)} notes")
        print(f"[Reaper] Survivor: '{survivor.title[:50]}...' (ID: {survivor.id[:8]}...)")
        print(f"[Reaper]   Length: {len(survivor.title + survivor.text)} chars")
        print(f"[Reaper]   Updated: {survivor.timestamps.updated}")
        
        # Process redundant notes
        archived_ids = []
        for note in notes:
            if note.id == survivor.id:
                continue
            
            # Calculate similarity if auditor provided
            similarity = None
            if auditor:
                try:
                    similarity = auditor.get_similarity_score(survivor, note)
                except:
                    pass
            
            print(f"\n[Reaper] Archiving: '{note.title[:50]}...'")
            if similarity:
                print(f"[Reaper]   Similarity to survivor: {similarity:.3f}")
            
            if not self.dry_run:
                # Archive the note
                note.archived = True
                
                # Add tombstone link to survivor
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                tombstone = f"\n\n---\n[Auto-Archived on {timestamp}]\n"
                tombstone += f"Merged into: {survivor.title}\n"
                tombstone += f"Survivor ID: {survivor.id}\n"
                if similarity:
                    tombstone += f"Similarity: {similarity:.2%}\n"
                note.text += tombstone
                
                # Add AutoPruned label for easy review/undo
                try:
                    label = self.keep.findLabel('AutoPruned')
                    if not label:
                        label = self.keep.createLabel('AutoPruned')
                    note.labels.add(label)
                except Exception as e:
                    print(f"[Reaper] Warning: Could not add label: {e}")
                
                archived_ids.append(note.id)
            else:
                print(f"[Reaper]   [DRY RUN] Would archive this note")
                archived_ids.append(note.id)
            
            # Log the action
            self.actions_log.append({
                'action': 'archive',
                'note_id': note.id,
                'note_title': note.title,
                'survivor_id': survivor.id,
                'survivor_title': survivor.title,
                'similarity': similarity,
                'timestamp': datetime.datetime.now(),
                'dry_run': self.dry_run
            })
        
        return {
            'status': 'success',
            'survivor_id': survivor.id,
            'survivor_title': survivor.title,
            'archived_ids': archived_ids,
            'archived_count': len(archived_ids)
        }
    
    def process_all_clusters(self, clusters: List[List[str]], auditor=None) -> dict:
        """
        Process multiple clusters.
        
        Args:
            clusters: List of clusters (each cluster is a list of note IDs)
            auditor: Optional SemanticAuditor for similarity scoring
            
        Returns:
            dict: Summary of all processing results
        """
        results = {
            'total_clusters': len(clusters),
            'processed': 0,
            'skipped': 0,
            'total_archived': 0,
            'cluster_results': []
        }
        
        for i, cluster in enumerate(clusters, 1):
            print(f"\n{'='*60}")
            print(f"Cluster {i}/{len(clusters)}")
            print(f"{'='*60}")
            
            result = self.process_cluster(cluster, auditor)
            results['cluster_results'].append(result)
            
            if result['status'] == 'success':
                results['processed'] += 1
                results['total_archived'] += result['archived_count']
            else:
                results['skipped'] += 1
        
        return results
    
    def get_actions_log(self):
        """Return the log of all actions taken."""
        return self.actions_log
    
    def export_log_csv(self, filepath="data/actions_log.csv"):
        """
        Export actions log to CSV for review.
        
        Args:
            filepath: Path to save CSV file
        """
        import csv
        from pathlib import Path
        
        Path(filepath).parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w', newline='') as f:
            if not self.actions_log:
                return
            
            fieldnames = self.actions_log[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.actions_log)
        
        print(f"[Reaper] Actions log exported to {filepath}")
    
    def undo_last_batch(self):
        """
        Undo the last batch of archival actions by unarchiving notes
        and removing AutoPruned labels.
        """
        if self.dry_run:
            print("[Reaper] Cannot undo in dry-run mode")
            return
        
        if not self.actions_log:
            print("[Reaper] No actions to undo")
            return
        
        # Get unique note IDs from last batch
        note_ids = list(set(action['note_id'] for action in self.actions_log))
        
        print(f"[Reaper] Undoing archival of {len(note_ids)} notes...")
        
        for note_id in note_ids:
            try:
                note = self.keep.get(note_id)
                note.archived = False
                
                # Remove AutoPruned label
                label = self.keep.findLabel('AutoPruned')
                if label and label in note.labels.all():
                    note.labels.remove(label)
                
                print(f"[Reaper] ✓ Restored: {note.title[:50]}...")
            except Exception as e:
                print(f"[Reaper] ✗ Failed to restore {note_id}: {e}")
        
        print("[Reaper] Undo complete. Remember to sync!")


# Example usage
if __name__ == "__main__":
    import sys
    from auth import SovereignAuth
    from analysis import SemanticAuditor
    
    if len(sys.argv) < 2:
        print("Usage: python action.py <your-email@gmail.com> [--execute]")
        print("  --execute: Actually perform actions (default is dry-run)")
        sys.exit(1)
    
    email = sys.argv[1]
    execute = '--execute' in sys.argv
    
    # Authenticate
    auth = SovereignAuth(email)
    keep = auth.login()
    auth.sync()
    
    # Run analysis
    auditor = SemanticAuditor(keep)
    clusters = auditor.find_redundancy_clusters(threshold=0.85)
    
    if not clusters:
        print("\n[Action] No redundancy clusters found. Your notes are well-organized!")
        sys.exit(0)
    
    # Process clusters
    reaper = SovereignReaper(keep, dry_run=not execute)
    
    if not execute:
        print("\n" + "="*60)
        print("DRY RUN MODE - No changes will be made")
        print("="*60)
    
    results = reaper.process_all_clusters(clusters, auditor)
    
    # Print summary
    print("\n" + "="*60)
    print("PROCESSING SUMMARY")
    print("="*60)
    print(f"Total clusters found: {results['total_clusters']}")
    print(f"Clusters processed: {results['processed']}")
    print(f"Clusters skipped: {results['skipped']}")
    print(f"Total notes archived: {results['total_archived']}")
    
    if not execute:
        print("\nThis was a DRY RUN. To actually archive notes, run with --execute flag.")
    else:
        print("\nChanges made! Syncing with Google Keep...")
        auth.sync()
        print("Done! Check your Google Keep to verify.")
        
        # Export log
        reaper.export_log_csv()
