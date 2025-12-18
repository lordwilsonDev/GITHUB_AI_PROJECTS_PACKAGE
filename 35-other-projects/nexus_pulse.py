#!/usr/bin/env python3
"""
Nexus Pulse: 5-Minute Interval Orchestrator

Scans Inbox, processes tasks, commits evidence.
Runs in isolated process to prevent blocking Jarvis.
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import signal
import threading

class NexusPulse:
    def __init__(self):
        self.home = Path.home()
        self.instances_dir = self.home / "instances"
        self.instances_dir.mkdir(exist_ok=True)
        
        self.inbox_dir = self.home / "Inbox"
        self.inbox_dir.mkdir(exist_ok=True)
        
        # Create inbox state directories
        self.inbox_pending = self.inbox_dir / "000_pending"
        self.inbox_claimed = self.inbox_dir / "001_claimed"
        self.inbox_done = self.inbox_dir / "003_done"
        self.inbox_failed = self.inbox_dir / "999_failed"
        
        for d in [self.inbox_pending, self.inbox_claimed, self.inbox_done, self.inbox_failed]:
            d.mkdir(exist_ok=True)
        
        self.heartbeat_file = self.instances_dir / "nexus_pulse.heartbeat"
        self.running = True
        
        # Register signal handlers
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)
        
    def update_heartbeat(self, status='pulsing'):
        """Write heartbeat file atomically with schema version"""
        try:
            # Prepare heartbeat data with schema version
            heartbeat_data = {
                'schema': 'hb.v1',
                'ts': time.time(),
                'pid': os.getpid(),
                'status': status
            }
            
            # Atomic write: write to temp file, then rename
            temp_file = str(self.heartbeat_file) + '.tmp'
            with open(temp_file, 'w') as f:
                json.dump(heartbeat_data, f)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
            
            # Atomic rename (POSIX guarantees atomicity)
            os.rename(temp_file, self.heartbeat_file)
        except Exception as e:
            print(f"Heartbeat error: {e}")
    
    def heartbeat_ticker(self):
        """Background thread that writes heartbeat every 10s (liveness proof)"""
        while self.running:
            self.update_heartbeat('alive')
            time.sleep(10)
    
    def shutdown(self, signum, frame):
        """Graceful shutdown"""
        print("\n🛑 Nexus Pulse shutting down...")
        self.running = False
        self.heartbeat_file.unlink(missing_ok=True)
        sys.exit(0)
    
    def git_commit_if_dirty(self):
        """Only commit if there are changes"""
        try:
            # Check if dirty
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.home,
                capture_output=True,
                text=True
            )
            
            if not result.stdout.strip():
                # No changes
                return True
            
            # Commit changes
            timestamp = datetime.now().strftime('%H:%M:%S')
            subprocess.run(['git', 'add', '.'], cwd=self.home, check=True)
            subprocess.run(
                ['git', 'commit', '-m', f'NEXUS PULSE: {timestamp}'],
                cwd=self.home,
                check=True
            )
            
            # Try to push (graceful failure)
            try:
                subprocess.run(
                    ['git', 'push'],
                    cwd=self.home,
                    check=True,
                    timeout=10
                )
                print("  ✅ Git: committed and pushed")
            except subprocess.TimeoutExpired:
                print("  ⚠️  Git: push timeout (offline?)")
            except subprocess.CalledProcessError as e:
                print(f"  ⚠️  Git: push failed ({e}) - commit saved locally")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Git error: {e}")
            return False
    
    def reclaim_stale_tasks(self):
        """Reclaim tasks stuck in claimed with expired leases"""
        reclaimed = 0
        for item in self.inbox_claimed.iterdir():
            if not item.is_file() or item.suffix == '.json':
                continue
            
            claim_file = self.inbox_claimed / f"{item.name}.claim.json"
            if not claim_file.exists():
                # No claim metadata - move back to pending
                item.rename(self.inbox_pending / item.name)
                reclaimed += 1
                continue
            
            try:
                with open(claim_file, 'r') as f:
                    claim = json.load(f)
                claimed_at = datetime.fromisoformat(claim['claimed_at'])
                lease_seconds = claim.get('lease_seconds', 600)
                
                if datetime.now() - claimed_at > timedelta(seconds=lease_seconds):
                    # Lease expired - move to failed
                    item.rename(self.inbox_failed / item.name)
                    claim_file.unlink()
                    reclaimed += 1
                    print(f"  ♻️  Reclaimed stale: {item.name}")
            except Exception as e:
                print(f"  ⚠️  Claim check error: {item.name} - {e}")
        
        return reclaimed
    
    def process_inbox(self):
        """Process inbox with atomic claim/move pattern + lease metadata"""
        processed = 0
        
        # Scan pending
        for item in self.inbox_pending.iterdir():
            if not item.is_file():
                continue
            
            try:
                # Atomic claim: move to claimed
                claimed_path = self.inbox_claimed / item.name
                item.rename(claimed_path)
                
                # Write claim lease
                claim_file = self.inbox_claimed / f"{item.name}.claim.json"
                with open(claim_file, 'w') as f:
                    json.dump({
                        'claimed_at': datetime.now().isoformat(),
                        'owner': 'nexus_pulse',
                        'lease_seconds': 600
                    }, f)
                
                # Process (stub for now)
                print(f"  📥 Processing: {item.name}")
                time.sleep(0.1)  # Simulate work
                
                # Move to done and clean up claim
                done_path = self.inbox_done / item.name
                claimed_path.rename(done_path)
                claim_file.unlink(missing_ok=True)
                
                processed += 1
                
            except Exception as e:
                print(f"  ❌ Failed: {item.name} - {e}")
                # Move to failed
                try:
                    failed_path = self.inbox_failed / item.name
                    claim_file = self.inbox_claimed / f"{item.name}.claim.json"
                    if claimed_path.exists():
                        claimed_path.rename(failed_path)
                        claim_file.unlink(missing_ok=True)
                    elif item.exists():
                        item.rename(failed_path)
                except:
                    pass
        
        return processed
    
    def pulse_loop(self):
        """Main pulse loop (5-minute interval)"""
        print("⚡ Nexus Pulse starting...")
        print(f"   PID: {os.getpid()}")
        print(f"   Heartbeat: {self.heartbeat_file}")
        print(f"   Liveness ticker: 10s interval")
        print(f"   Inbox: {self.inbox_dir}")
        print(f"   Interval: 5 minutes")
        print("\n   Note: This is a process isolation stub.")
        print("   Full orchestration will be added in capability upgrade.\n")
        
        # Start background heartbeat ticker
        ticker = threading.Thread(target=self.heartbeat_ticker, daemon=True)
        ticker.start()
        
        # Reclaim stale tasks on startup
        reclaimed = self.reclaim_stale_tasks()
        if reclaimed > 0:
            print(f"  ♻️  Startup: reclaimed {reclaimed} stale tasks\n")
        
        pulse_count = 0
        while self.running:
            # Execute pulse (heartbeat handled by ticker)
            print(f"\n⚡ PULSE #{pulse_count + 1} [{datetime.now().strftime('%H:%M:%S')}]")
            
            # Process inbox
            processed = self.process_inbox()
            print(f"  📥 Inbox: {processed} items processed")
            
            # Git commit
            self.git_commit_if_dirty()
            
            pulse_count += 1
            
            # Wait 5 minutes (or until shutdown)
            for i in range(30):  # 30 * 10s = 5 min
                if not self.running:
                    break
                time.sleep(10)

if __name__ == "__main__":
    pulse = NexusPulse()
    pulse.pulse_loop()
