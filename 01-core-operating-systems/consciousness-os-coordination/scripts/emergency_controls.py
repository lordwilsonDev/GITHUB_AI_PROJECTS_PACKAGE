#!/usr/bin/env python3
"""
Consciousness OS - Emergency Control System

Provides safety mechanisms:
- Emergency stop all processes
- Rollback to last known good state
- Checkpoint creation
- State recovery

NO PERMISSION NEEDED - Build with love
"""

import json
import os
import signal
import psutil
import shutil
from datetime import datetime
from pathlib import Path

# Paths
BASE_DIR = Path("/Users/lordwilson/consciousness-os-coordination")
TODO_FILE = BASE_DIR / "TODO_TRACKER.json"
BLUEPRINT_FILE = BASE_DIR / "MASTER_BLUEPRINT.md"
CHECKPOINT_DIR = BASE_DIR / "checkpoints"

class EmergencyControls:
    """Emergency control system for Consciousness OS"""
    
    def __init__(self):
        # Ensure checkpoint directory exists
        CHECKPOINT_DIR.mkdir(exist_ok=True)
    
    def emergency_stop(self):
        """Stop all RAY and RADE processes"""
        print("🚨 EMERGENCY STOP INITIATED")
        print("=" * 50)
        print()
        
        stopped_count = 0
        
        # Find and stop RAY processes
        print("🔍 Scanning for RAY processes...")
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'ray' in cmdline.lower():
                    print(f"  Stopping PID {proc.info['pid']}: {proc.info['name']}")
                    proc.terminate()
                    stopped_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Find and stop RADE processes
        print("\n🔍 Scanning for RADE processes...")
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'autonomous_scheduler' in cmdline or 'vy_task_runner' in cmdline:
                    print(f"  Stopping PID {proc.info['pid']}: {proc.info['name']}")
                    proc.terminate()
                    stopped_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        print(f"\n✅ Stopped {stopped_count} process(es)")
        
        # Mark TODO tracker
        self._mark_emergency_stop()
    
    def _mark_emergency_stop(self):
        """Add emergency stop marker to TODO tracker"""
        try:
            with open(TODO_FILE) as f:
                data = json.load(f)
            
            # Add emergency task at top
            emergency_task = {
                'id': 'EMERGENCY-STOP',
                'description': 'EMERGENCY STOP - DO NOT CLAIM NEW TASKS',
                'status': 'Blocked',
                'priority': 'Critical',
                'phase': 'Emergency',
                'assigned_to': 'SYSTEM',
                'dependencies': [],
                'measurable_outcome': 'All work halted',
                'why': f"Emergency stop initiated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                'started_at': datetime.now().isoformat(),
                'completed_at': None,
                'output_notes': 'System in emergency stop state'
            }
            
            data['tasks'].insert(0, emergency_task)
            data['metadata']['last_updated'] = datetime.now().strftime('%Y-%m-%d')
            
            with open(TODO_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"\n⚠️  Emergency marker added to TODO tracker")
        except Exception as e:
            print(f"\n⚠️  Could not update TODO tracker: {e}")
    
    def create_checkpoint(self, name=None):
        """Create a checkpoint of current state"""
        if name is None:
            name = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        checkpoint_path = CHECKPOINT_DIR / name
        checkpoint_path.mkdir(exist_ok=True)
        
        print(f"💾 Creating checkpoint: {name}")
        print("=" * 50)
        print()
        
        # Copy TODO tracker
        if TODO_FILE.exists():
            shutil.copy2(TODO_FILE, checkpoint_path / "TODO_TRACKER.json")
            print(f"  ✅ Saved TODO tracker")
        
        # Copy blueprint
        if BLUEPRINT_FILE.exists():
            shutil.copy2(BLUEPRINT_FILE, checkpoint_path / "MASTER_BLUEPRINT.md")
            print(f"  ✅ Saved Master Blueprint")
        
        # Copy metrics if they exist
        metrics_file = BASE_DIR / "metrics" / "system_metrics.json"
        if metrics_file.exists():
            shutil.copy2(metrics_file, checkpoint_path / "system_metrics.json")
            print(f"  ✅ Saved metrics")
        
        # Create metadata
        metadata = {
            'checkpoint_name': name,
            'created_at': datetime.now().isoformat(),
            'files': ['TODO_TRACKER.json', 'MASTER_BLUEPRINT.md']
        }
        
        with open(checkpoint_path / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✅ Checkpoint created: {checkpoint_path}")
        return checkpoint_path
    
    def list_checkpoints(self):
        """List all available checkpoints"""
        checkpoints = []
        
        for item in CHECKPOINT_DIR.iterdir():
            if item.is_dir():
                metadata_file = item / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                    checkpoints.append({
                        'name': item.name,
                        'path': item,
                        'created_at': metadata.get('created_at', 'Unknown')
                    })
        
        # Sort by creation time
        checkpoints.sort(key=lambda x: x['created_at'], reverse=True)
        return checkpoints
    
    def rollback(self, checkpoint_name=None):
        """Rollback to a checkpoint"""
        checkpoints = self.list_checkpoints()
        
        if not checkpoints:
            print("⚠️  No checkpoints available")
            return
        
        # Use latest if not specified
        if checkpoint_name is None:
            checkpoint = checkpoints[0]
            print(f"🔄 Rolling back to latest checkpoint: {checkpoint['name']}")
        else:
            checkpoint = next((c for c in checkpoints if c['name'] == checkpoint_name), None)
            if not checkpoint:
                print(f"⚠️  Checkpoint not found: {checkpoint_name}")
                return
            print(f"🔄 Rolling back to: {checkpoint['name']}")
        
        print("=" * 50)
        print()
        
        checkpoint_path = checkpoint['path']
        
        # Restore TODO tracker
        todo_backup = checkpoint_path / "TODO_TRACKER.json"
        if todo_backup.exists():
            shutil.copy2(todo_backup, TODO_FILE)
            print("  ✅ Restored TODO tracker")
        
        # Restore blueprint
        blueprint_backup = checkpoint_path / "MASTER_BLUEPRINT.md"
        if blueprint_backup.exists():
            shutil.copy2(blueprint_backup, BLUEPRINT_FILE)
            print("  ✅ Restored Master Blueprint")
        
        print(f"\n✅ Rollback complete to {checkpoint['created_at']}")

def main():
    import sys
    
    controls = EmergencyControls()
    
    if len(sys.argv) < 2:
        print("🚨 Consciousness OS - Emergency Controls")
        print("=" * 50)
        print()
        print("Usage:")
        print("  python3 emergency_controls.py stop          - Emergency stop all processes")
        print("  python3 emergency_controls.py checkpoint    - Create checkpoint")
        print("  python3 emergency_controls.py list          - List checkpoints")
        print("  python3 emergency_controls.py rollback      - Rollback to latest")
        print("  python3 emergency_controls.py rollback NAME - Rollback to specific checkpoint")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'stop':
        controls.emergency_stop()
    elif command == 'checkpoint':
        controls.create_checkpoint()
    elif command == 'list':
        checkpoints = controls.list_checkpoints()
        print("💾 Available Checkpoints:")
        print("=" * 50)
        for cp in checkpoints:
            print(f"  - {cp['name']} (created: {cp['created_at']})")
    elif command == 'rollback':
        checkpoint_name = sys.argv[2] if len(sys.argv) > 2 else None
        controls.rollback(checkpoint_name)
    else:
        print(f"⚠️  Unknown command: {command}")

if __name__ == '__main__':
    main()
