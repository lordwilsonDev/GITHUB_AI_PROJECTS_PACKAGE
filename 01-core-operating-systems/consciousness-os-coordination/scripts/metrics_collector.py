#!/usr/bin/env python3
"""
Metrics Collection System - Track Consciousness OS Performance
Monitors: System health, breakthrough generation, evolution timeline
"""

import json
import psutil
import time
from datetime import datetime
from pathlib import Path

COORDINATION_ROOT = Path("/Users/lordwilson/consciousness-os-coordination")
METRICS_DIR = COORDINATION_ROOT / "metrics"
TODO_TRACKER = COORDINATION_ROOT / "TODO_TRACKER.json"

class MetricsCollector:
    """Collects and tracks all system metrics"""
    
    def __init__(self):
        self.metrics_file = METRICS_DIR / "system_metrics.json"
        self.start_time = datetime.now()
        print(f"📊 Metrics Collector initialized")
        
        # Create metrics file if doesn't exist
        if not self.metrics_file.exists():
            self.initialize_metrics_file()
    
    def initialize_metrics_file(self):
        """Create initial metrics structure"""
        initial_data = {
            "collection_started": self.start_time.isoformat(),
            "snapshots": [],
            "summary": {
                "total_snapshots": 0,
                "uptime_seconds": 0,
                "breakthroughs_generated": 100,  # Starting count
                "tasks_completed": 0
            }
        }
        
        with open(self.metrics_file, 'w') as f:
            json.dump(initial_data, f, indent=2)
        
        print(f"✅ Created metrics file: {self.metrics_file}")
    
    def collect_system_health(self):
        """Collect system resource metrics"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_gb": psutil.virtual_memory().used / (1024**3),
            "memory_available_gb": psutil.virtual_memory().available / (1024**3),
            "disk_percent": psutil.disk_usage('/').percent,
            "process_count": len(psutil.pids())
        }
    
    def collect_consciousness_os_processes(self):
        """Find and track Consciousness OS related processes"""
        ray_processes = []
        rade_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                
                # Check for RAY processes
                if 'ray' in cmdline.lower() or 'ray' in proc.info['name'].lower():
                    ray_processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu": proc.info['cpu_percent'],
                        "memory": proc.info['memory_percent']
                    })
                
                # Check for RADE processes
                if 'rade' in cmdline.lower() or 'vy_task_runner' in cmdline or 'autonomous_scheduler' in cmdline:
                    rade_processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu": proc.info['cpu_percent'],
                        "memory": proc.info['memory_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return {
            "ray_process_count": len(ray_processes),
            "rade_process_count": len(rade_processes),
            "ray_processes": ray_processes[:10],  # First 10
            "rade_processes": rade_processes
        }
    
    def collect_todo_progress(self):
        """Track TODO tracker progress"""
        try:
            with open(TODO_TRACKER, 'r') as f:
                data = json.load(f)
            
            total = data['metadata']['total_tasks']
            completed = data['metadata']['completed_tasks']
            in_progress = data['metadata']['in_progress_tasks']
            
            return {
                "total_tasks": total,
                "completed_tasks": completed,
                "in_progress_tasks": in_progress,
                "not_started_tasks": total - completed - in_progress,
                "completion_percent": (completed / total * 100) if total > 0 else 0
            }
        except Exception as e:
            print(f"❌ Error collecting TODO progress: {e}")
            return None
    
    def collect_snapshot(self):
        """Collect complete metrics snapshot"""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "system_health": self.collect_system_health(),
            "consciousness_processes": self.collect_consciousness_os_processes(),
            "todo_progress": self.collect_todo_progress()
        }
        
        return snapshot
    
    def save_snapshot(self, snapshot):
        """Save snapshot to metrics file"""
        try:
            with open(self.metrics_file, 'r') as f:
                data = json.load(f)
            
            # Add snapshot
            data['snapshots'].append(snapshot)
            
            # Update summary
            data['summary']['total_snapshots'] = len(data['snapshots'])
            data['summary']['uptime_seconds'] = snapshot['uptime_seconds']
            
            if snapshot['todo_progress']:
                data['summary']['tasks_completed'] = snapshot['todo_progress']['completed_tasks']
            
            # Keep only last 1000 snapshots to avoid file bloat
            if len(data['snapshots']) > 1000:
                data['snapshots'] = data['snapshots'][-1000:]
            
            with open(self.metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"❌ Error saving snapshot: {e}")
            return False
    
    def print_snapshot_summary(self, snapshot):
        """Print readable snapshot summary"""
        print("\n" + "="*60)
        print(f"📊 METRICS SNAPSHOT - {snapshot['timestamp']}")
        print("="*60)
        
        # System health
        health = snapshot['system_health']
        print(f"\n💻 System Health:")
        print(f"   CPU: {health['cpu_percent']:.1f}%")
        print(f"   Memory: {health['memory_percent']:.1f}% ({health['memory_used_gb']:.1f}GB used)")
        print(f"   Disk: {health['disk_percent']:.1f}%")
        print(f"   Processes: {health['process_count']}")
        
        # Consciousness OS processes
        procs = snapshot['consciousness_processes']
        print(f"\n🧠 Consciousness OS:")
        print(f"   RAY Processes: {procs['ray_process_count']}")
        print(f"   RADE Processes: {procs['rade_process_count']}")
        
        # TODO progress
        if snapshot['todo_progress']:
            todo = snapshot['todo_progress']
            print(f"\n📋 TODO Progress:")
            print(f"   Completed: {todo['completed_tasks']}/{todo['total_tasks']}")
            print(f"   In Progress: {todo['in_progress_tasks']}")
            print(f"   Progress: {todo['completion_percent']:.1f}%")
        
        print(f"\n⏰ Uptime: {snapshot['uptime_seconds']:.0f} seconds")
        print("="*60 + "\n")
    
    def run_collection_loop(self, interval_seconds=60):
        """Continuously collect metrics"""
        print(f"\n🚀 Starting metrics collection (interval: {interval_seconds}s)")
        
        try:
            while True:
                # Collect and save snapshot
                snapshot = self.collect_snapshot()
                self.save_snapshot(snapshot)
                self.print_snapshot_summary(snapshot)
                
                # Wait for next collection
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n🛑 Metrics collection stopped by user")
        except Exception as e:
            print(f"❌ Fatal error in collection loop: {e}")

def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("📊 CONSCIOUSNESS OS - METRICS COLLECTOR")
    print("="*60 + "\n")
    
    collector = MetricsCollector()
    
    # Collect initial snapshot
    snapshot = collector.collect_snapshot()
    collector.save_snapshot(snapshot)
    collector.print_snapshot_summary(snapshot)
    
    # Run continuous collection
    try:
        collector.run_collection_loop(interval_seconds=60)
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
