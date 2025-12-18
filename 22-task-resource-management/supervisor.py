#!/usr/bin/env python3
"""
Supervisor: Process Watchdog for MoIE-OS Dual-Core Architecture

Monitors and restarts:
- jarvis_watchman.py (always-on speech recognition)
- nexus_pulse.py (5-minute interval orchestrator)

Uses heartbeat files to detect hangs/crashes.
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path
from datetime import datetime, timedelta
import json

class ProcessSupervisor:
    def __init__(self):
        self.home = Path.home()
        self.instances_dir = self.home / "instances"
        self.instances_dir.mkdir(exist_ok=True)
        
        self.processes = {}
        self.config = {
            "jarvis_watchman": {
                "script": self.home / "jarvis_watchman.py",
                "heartbeat_interval": 10,  # seconds (liveness ticker writes every 10s)
                "restart_on_failure": True,
                "max_restarts": 5,
                "restart_window": 300  # 5 minutes
            },
            "nexus_pulse": {
                "script": self.home / "nexus_pulse.py",
                "heartbeat_interval": 10,  # seconds (liveness ticker writes every 10s)
                "restart_on_failure": True,
                "max_restarts": 3,
                "restart_window": 600  # 10 minutes
            }
        }
        
        self.restart_history = {name: [] for name in self.config.keys()}
        
    def get_heartbeat_file(self, process_name):
        return self.instances_dir / f"{process_name}.heartbeat"
    
    def get_pid_file(self, process_name):
        return self.instances_dir / f"{process_name}.pid"
    
    def is_process_alive(self, process_name):
        """Check if process is alive via heartbeat file"""
        heartbeat_file = self.get_heartbeat_file(process_name)
        
        if not heartbeat_file.exists():
            return False
        
        try:
            with open(heartbeat_file, 'r') as f:
                data = json.load(f)
                last_beat = datetime.fromisoformat(data['timestamp'])
                max_age = timedelta(seconds=self.config[process_name]['heartbeat_interval'] * 2)
                
                if datetime.now() - last_beat > max_age:
                    print(f"⚠️  {process_name}: heartbeat stale ({datetime.now() - last_beat})")
                    return False
                    
                return True
        except Exception as e:
            print(f"❌ {process_name}: heartbeat read error: {e}")
            return False
    
    def start_process(self, process_name):
        """Start a managed process"""
        config = self.config[process_name]
        script = config['script']
        
        if not script.exists():
            print(f"❌ {process_name}: script not found: {script}")
            return False
        
        try:
            # Start process
            proc = subprocess.Popen(
                [sys.executable, str(script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True  # Detach from parent
            )
            
            # Save PID
            pid_file = self.get_pid_file(process_name)
            with open(pid_file, 'w') as f:
                f.write(str(proc.pid))
            
            self.processes[process_name] = proc
            print(f"✅ {process_name}: started (PID {proc.pid})")
            
            # Record restart
            self.restart_history[process_name].append(datetime.now())
            
            return True
            
        except Exception as e:
            print(f"❌ {process_name}: start failed: {e}")
            return False
    
    def stop_process(self, process_name):
        """Stop a managed process"""
        pid_file = self.get_pid_file(process_name)
        
        if not pid_file.exists():
            return
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            os.kill(pid, signal.SIGTERM)
            print(f"🛑 {process_name}: stopped (PID {pid})")
            
            # Clean up
            pid_file.unlink(missing_ok=True)
            self.get_heartbeat_file(process_name).unlink(missing_ok=True)
            
        except ProcessLookupError:
            print(f"⚠️  {process_name}: process already dead")
        except Exception as e:
            print(f"❌ {process_name}: stop error: {e}")
    
    def should_restart(self, process_name):
        """Check if process should be restarted based on restart limits"""
        config = self.config[process_name]
        
        if not config['restart_on_failure']:
            return False
        
        # Check restart rate
        history = self.restart_history[process_name]
        window = timedelta(seconds=config['restart_window'])
        recent = [t for t in history if datetime.now() - t < window]
        
        if len(recent) >= config['max_restarts']:
            print(f"⛔ {process_name}: restart limit reached ({len(recent)} in {config['restart_window']}s)")
            return False
        
        return True
    
    def monitor_loop(self):
        """Main monitoring loop"""
        print("🔍 Supervisor starting...")
        print(f"   Monitoring: {', '.join(self.config.keys())}")
        print(f"   Instances: {self.instances_dir}")
        
        # Start all processes
        for process_name in self.config.keys():
            self.start_process(process_name)
            time.sleep(2)  # Stagger starts
        
        print("\n👁️  Monitoring active (Ctrl+C to stop)\n")
        
        try:
            while True:
                for process_name in self.config.keys():
                    if not self.is_process_alive(process_name):
                        print(f"💀 {process_name}: DEAD")
                        
                        if self.should_restart(process_name):
                            print(f"🔄 {process_name}: restarting...")
                            self.stop_process(process_name)  # Clean up
                            time.sleep(1)
                            self.start_process(process_name)
                        else:
                            print(f"⛔ {process_name}: NOT restarting (limit reached)")
                
                time.sleep(10)  # Check every 10 seconds
                
        except KeyboardInterrupt:
            print("\n🛑 Supervisor shutting down...")
            for process_name in self.config.keys():
                self.stop_process(process_name)
            print("✅ Shutdown complete")

if __name__ == "__main__":
    supervisor = ProcessSupervisor()
    supervisor.monitor_loop()
