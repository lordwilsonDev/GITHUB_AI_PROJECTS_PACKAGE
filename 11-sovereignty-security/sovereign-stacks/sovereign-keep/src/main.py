#!/usr/bin/env python3
"""
Sovereign Keep Protocol - Main Orchestration Script
Automated Google Keep management with semantic analysis and intelligent pruning.
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from auth import SovereignAuth
from analysis import SemanticAuditor
from action import SovereignReaper


def main():
    parser = argparse.ArgumentParser(
        description='Sovereign Keep Protocol - Automated Knowledge Management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (safe, no changes):
  python main.py user@gmail.com
  
  # Execute with custom threshold:
  python main.py user@gmail.com --execute --threshold 0.90
  
  # Verbose output:
  python main.py user@gmail.com --verbose
  
  # Backup before processing:
  python main.py user@gmail.com --backup --execute
        """
    )
    
    parser.add_argument('email', help='Google account email')
    parser.add_argument('--execute', action='store_true',
                        help='Actually perform actions (default is dry-run)')
    parser.add_argument('--threshold', type=float, default=0.85,
                        help='Similarity threshold for clustering (0-1, default: 0.85)')
    parser.add_argument('--backup', action='store_true',
                        help='Export backup before processing')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    parser.add_argument('--include-archived', action='store_true',
                        help='Include archived notes in analysis')
    
    args = parser.parse_args()
    
    print("")
    print("="*70)
    print("  SOVEREIGN KEEP PROTOCOL")
    print("  Autonomous Knowledge Management & Semantic Hygiene")
    print("="*70)
    print(f"\nAccount: {args.email}")
    print(f"Mode: {'EXECUTE' if args.execute else 'DRY RUN (safe)'}")
    print(f"Similarity Threshold: {args.threshold}")
    print(f"Backup: {'Yes' if args.backup else 'No'}")
    print("")
    
    try:
        # Phase 1: Authentication
        print("\n[Phase 1/5] Authentication")
        print("-" * 70)
        auth = SovereignAuth(args.email)
        keep = auth.login()
        
        # Phase 2: Sync
        print("\n[Phase 2/5] Synchronization")
        print("-" * 70)
        if not auth.sync():
            print("[Error] Sync failed. Aborting.")
            sys.exit(1)
        
        # Phase 3: Backup (optional)
        if args.backup:
            print("\n[Phase 3/5] Backup")
            print("-" * 70)
            from backup import BackupManager
            backup_mgr = BackupManager(keep)
            backup_path = backup_mgr.export_all()
            print(f"[Backup] ✓ Backup saved to {backup_path}")
        else:
            print("\n[Phase 3/5] Backup (skipped)")
            print("-" * 70)
            print("[Backup] Skipped (use --backup to enable)")
        
        # Phase 4: Semantic Analysis
        print("\n[Phase 4/5] Semantic Analysis")
        print("-" * 70)
        auditor = SemanticAuditor(keep)
        clusters = auditor.find_redundancy_clusters(
            threshold=args.threshold,
            include_archived=args.include_archived
        )
        
        if not clusters:
            print("\n" + "="*70)
            print("  ✓ NO REDUNDANCY FOUND")
            print("  Your notes are well-organized!")
            print("="*70)
            sys.exit(0)
        
        # Phase 5: Action (Pruning)
        print("\n[Phase 5/5] Cluster Processing")
        print("-" * 70)
        
        if not args.execute:
            print("\n⚠ DRY RUN MODE - No changes will be made")
            print("  Add --execute flag to actually archive notes\n")
        
        reaper = SovereignReaper(keep, dry_run=not args.execute)
        results = reaper.process_all_clusters(clusters, auditor)
        
        # Final Summary
        print("\n" + "="*70)
        print("  PROCESSING SUMMARY")
        print("="*70)
        print(f"Total clusters found:     {results['total_clusters']}")
        print(f"Clusters processed:       {results['processed']}")
        print(f"Clusters skipped:         {results['skipped']}")
        print(f"Total notes archived:     {results['total_archived']}")
        print("="*70)
        
        if args.execute:
            print("\n[Final Sync] Saving changes to Google Keep...")
            if auth.sync():
                print("[Final Sync] ✓ Changes saved successfully!")
                print("\n✓ Check your Google Keep to verify the changes.")
                print("✓ Archived notes are tagged with 'AutoPruned' for easy review.")
                
                # Export log
                reaper.export_log_csv()
                print("✓ Actions log saved to data/actions_log.csv")
            else:
                print("[Final Sync] ✗ Sync failed. Changes may not be saved.")
                sys.exit(1)
        else:
            print("\n⚠ This was a DRY RUN. No changes were made.")
            print("  Run with --execute to actually archive redundant notes.")
        
        print("\n" + "="*70)
        print("  SOVEREIGN KEEP PROTOCOL - COMPLETE")
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n[Interrupted] Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[Fatal Error] {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
