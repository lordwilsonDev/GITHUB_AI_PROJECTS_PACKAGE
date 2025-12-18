#!/usr/bin/env python3
"""
Jarvis Watchman: Always-On Speech Recognition

Listens for wake word "Jarvis" and processes voice commands.
Runs in isolated process to prevent mic freezes from affecting Nexus.
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
import signal
import threading

class JarvisWatchman:
    def __init__(self):
        self.home = Path.home()
        self.instances_dir = self.home / "instances"
        self.instances_dir.mkdir(exist_ok=True)
        
        self.heartbeat_file = self.instances_dir / "jarvis_watchman.heartbeat"
        self.running = True
        
        # Register signal handlers
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)
        
    def update_heartbeat(self, status='listening'):
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
        print("\n🛑 Jarvis shutting down...")
        self.running = False
        self.heartbeat_file.unlink(missing_ok=True)
        sys.exit(0)
    
    def listen_loop(self):
        """Main listening loop (stub for now)"""
        print("🎤 Jarvis Watchman starting...")
        print(f"   PID: {os.getpid()}")
        print(f"   Heartbeat: {self.heartbeat_file}")
        print("   Liveness ticker: 10s interval")
        print("   Status: LISTENING (stub mode - no actual speech recognition yet)")
        print("\n   Note: This is a process isolation stub.")
        print("   Real speech recognition will be added in capability upgrade.\n")
        
        # Start background heartbeat ticker
        ticker = threading.Thread(target=self.heartbeat_ticker, daemon=True)
        ticker.start()
        
        iteration = 0
        while self.running:
            # Stub: simulate listening (heartbeat handled by ticker)
            if iteration % 6 == 0:  # Every minute
                print(f"🎤 [{datetime.now().strftime('%H:%M:%S')}] Listening... (iteration {iteration})")
            
            iteration += 1
            time.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    watchman = JarvisWatchman()
    watchman.listen_loop()
