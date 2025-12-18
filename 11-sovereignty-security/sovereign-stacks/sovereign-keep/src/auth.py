"""
Sovereign Keep Protocol - Authentication Layer
Implements resilient, multi-tier authentication for Google Keep access.
"""

import gkeepapi
import keyring
import pickle
import os
from pathlib import Path


class SovereignAuth:
    """
    Handles authentication to Google Keep with three-tier fallback strategy:
    1. Session restoration from pickle file (fastest, preserves sync state)
    2. Resume with Master Token from OS keyring
    3. Fresh login with app password (one-time setup)
    """
    
    def __init__(self, username, data_dir="data"):
        """
        Initialize the authentication handler.
        
        Args:
            username: Google account email
            data_dir: Directory for storing session cache
        """
        self.username = username
        self.keep = gkeepapi.Keep()
        self.token_service = "gkeep-sovereign-token"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.session_file = self.data_dir / "session.pickle"
        self.session_backup = self.data_dir / "session.bak"
        
    def login(self):
        """
        Attempt login using three-tier fallback strategy.
        
        Returns:
            gkeepapi.Keep: Authenticated Keep client
            
        Raises:
            ConnectionError: If all authentication methods fail
        """
        # Tier 1: Try to load serialized session (fastest, preserves sync state)
        if self.session_file.exists():
            try:
                print(f"[Auth] Attempting session restoration from {self.session_file}...")
                with open(self.session_file, 'rb') as f:
                    state = pickle.load(f)
                    self.keep.restore(state)
                print("[Auth] ✓ Session restored from cache.")
                return self.keep
            except Exception as e:
                print(f"[Auth] ✗ Session cache invalid: {e}")
                # Backup corrupted session for debugging
                if self.session_file.exists():
                    self.session_file.rename(self.session_backup)
                    print(f"[Auth] Corrupted session backed up to {self.session_backup}")

        # Tier 2: Try to resume with Master Token from Keyring
        print("[Auth] Attempting to retrieve master token from keyring...")
        master_token = keyring.get_password(self.token_service, self.username)
        if master_token:
            try:
                print("[Auth] Master token found, attempting resume...")
                self.keep.resume(self.username, master_token)
                self.save_session()
                print("[Auth] ✓ Resumed with Master Token.")
                return self.keep
            except gkeepapi.exception.LoginException as e:
                print(f"[Auth] ✗ Master token expired or invalid: {e}")
                # Clear invalid token
                keyring.delete_password(self.token_service, self.username)

        # Tier 3: Fallback to Manual Login (One-time setup)
        print("[Auth] Fresh login required.")
        print("[Auth] Note: If you have 2FA enabled, you must use an App Password.")
        print("[Auth] Generate one at: https://myaccount.google.com/apppasswords")
        password = input(f"[Auth] Enter password/app password for {self.username}: ")
        
        try:
            print("[Auth] Attempting login...")
            self.keep.login(self.username, password)
            
            # Extract and save master token for next time
            token = self.keep.getMasterToken()
            keyring.set_password(self.token_service, self.username, token)
            self.save_session()
            
            print("[Auth] ✓ Login successful. Token cached for future use.")
            return self.keep
            
        except gkeepapi.exception.LoginException as e:
            raise ConnectionError(f"[Auth] ✗ Fatal Login Failure: {e}")

    def save_session(self):
        """
        Save the internal Keep state (cookies, sync tokens) to disk.
        This enables fast session restoration without re-authentication.
        """
        try:
            state = self.keep.dump()
            with open(self.session_file, 'wb') as f:
                pickle.dump(state, f)
            print(f"[Auth] Session state saved to {self.session_file}")
        except Exception as e:
            print(f"[Auth] Warning: Failed to save session: {e}")
    
    def sync(self):
        """
        Sync with Google Keep servers with error handling.
        
        Returns:
            bool: True if sync successful, False otherwise
        """
        try:
            print("[Auth] Syncing with Google Keep...")
            self.keep.sync()
            # Save session after successful sync to preserve state
            self.save_session()
            print("[Auth] ✓ Sync successful.")
            return True
        except Exception as e:
            print(f"[Auth] ✗ Sync failed: {e}")
            # Backup potentially corrupted session
            if self.session_file.exists():
                self.session_file.rename(self.session_backup)
                print(f"[Auth] Session backed up. Next run will attempt fresh login.")
            return False


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python auth.py <your-email@gmail.com>")
        sys.exit(1)
    
    email = sys.argv[1]
    auth = SovereignAuth(email)
    
    try:
        keep = auth.login()
        print(f"\n[Test] Successfully authenticated as {email}")
        print(f"[Test] Syncing notes...")
        auth.sync()
        
        notes = list(keep.all())
        print(f"[Test] Found {len(notes)} total notes")
        
        active_notes = [n for n in notes if not n.trashed and not n.archived]
        print(f"[Test] {len(active_notes)} active notes")
        
    except Exception as e:
        print(f"\n[Test] Authentication test failed: {e}")
        sys.exit(1)
