#!/usr/bin/env python3
"""
Authentication Test Script for Sovereign Keep Protocol
Tests the three-tier authentication system without modifying any notes.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from auth import SovereignAuth

def test_authentication(email):
    """
    Test the authentication flow and display account information.
    """
    print("="*60)
    print("Sovereign Keep Protocol - Authentication Test")
    print("="*60)
    print(f"\nTesting authentication for: {email}")
    print("\nThis will test the three-tier authentication system:")
    print("  1. Session restoration from cache")
    print("  2. Resume with master token from keyring")
    print("  3. Fresh login with app password")
    print("\n" + "-"*60 + "\n")
    
    try:
        # Initialize authentication
        auth = SovereignAuth(email)
        keep = auth.login()
        
        print("\n✅ Authentication successful!\n")
        
        # Sync with Google Keep
        print("Syncing with Google Keep...")
        keep.sync()
        print("✅ Sync complete!\n")
        
        # Display account statistics
        all_notes = list(keep.all())
        active_notes = [n for n in all_notes if not n.trashed and not n.archived]
        archived_notes = [n for n in all_notes if n.archived]
        trashed_notes = [n for n in all_notes if n.trashed]
        
        print("="*60)
        print("Account Statistics")
        print("="*60)
        print(f"Total notes: {len(all_notes)}")
        print(f"  Active: {len(active_notes)}")
        print(f"  Archived: {len(archived_notes)}")
        print(f"  Trashed: {len(trashed_notes)}")
        
        # Display labels
        labels = list(keep.labels())
        if labels:
            print(f"\nLabels: {len(labels)}")
            for label in labels[:10]:  # Show first 10
                print(f"  - {label.name}")
            if len(labels) > 10:
                print(f"  ... and {len(labels) - 10} more")
        
        # Show sample notes (first 5 active)
        if active_notes:
            print(f"\nSample Active Notes (first 5):")
            for i, note in enumerate(active_notes[:5], 1):
                title = note.title or "(Untitled)"
                text_preview = note.text[:50] + "..." if len(note.text) > 50 else note.text
                print(f"  {i}. {title}")
                if text_preview:
                    print(f"     {text_preview}")
        
        print("\n" + "="*60)
        print("✅ Authentication test completed successfully!")
        print("="*60)
        print("\nSession has been cached for future runs.")
        print("Next time you run the script, it will use the cached session.")
        print("\nYou can now proceed with semantic analysis.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        print("\nTroubleshooting:")
        print("  1. If you have 2FA enabled, use an App Password")
        print("     Generate at: https://myaccount.google.com/apppasswords")
        print("  2. If you see 'NeedsBrowser' error, wait 15 minutes and retry")
        print("  3. Delete data/session.pickle if session is corrupted")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_auth.py your.email@gmail.com")
        sys.exit(1)
    
    email = sys.argv[1]
    success = test_authentication(email)
    sys.exit(0 if success else 1)
