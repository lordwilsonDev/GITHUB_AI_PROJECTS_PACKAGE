#!/usr/bin/env python3
"""
Persistence and Crash Recovery System

Provides:
- Task state persistence to disk
- Automatic checkpoint creation
- Crash recovery and resume
- Agent state snapshots
- Workflow history tracking
"""

import asyncio
import logging
import json
import pickle
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)


class PersistenceManager:
    """
    Manages persistence and recovery of system state.
    
    Features:
    - Automatic state snapshots
    - Task queue persistence
    - Agent state tracking
    - Crash recovery
    - Checkpoint management
    """
    
    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path.home() / 'ai-orchestration' / 'data'
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories
        self.checkpoints_dir = self.data_dir / 'checkpoints'
        self.tasks_dir = self.data_dir / 'tasks'
        self.agents_dir = self.data_dir / 'agents'
        self.workflows_dir = self.data_dir / 'workflows'
        
        for directory in [self.checkpoints_dir, self.tasks_dir, self.agents_dir, self.workflows_dir]:
            directory.mkdir(exist_ok=True)
        
        self.checkpoint_interval = 60  # seconds
        self.max_checkpoints = 10
        self.auto_checkpoint_task = None
        
        logger.info(f"PersistenceManager initialized (data_dir: {self.data_dir})")
    
    async def save_task_state(self, task_queue) -> bool:
        """Save current task queue state."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = self.tasks_dir / f'task_queue_{timestamp}.json'
            
            state = {
                'timestamp': datetime.now().isoformat(),
                'tasks': {},
                'stats': task_queue.stats
            }
            
            # Save all tasks
            for task_id, task in task_queue.tasks.items():
                state['tasks'][task_id] = task.to_dict()
            
            # Write to file
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.info(f"✅ Task state saved: {filepath.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save task state: {e}")
            return False
    
    async def load_task_state(self, task_queue, filepath: Path = None) -> bool:
        """Load task queue state from file."""
        try:
            if filepath is None:
                # Find most recent task state file
                task_files = sorted(self.tasks_dir.glob('task_queue_*.json'))
                if not task_files:
                    logger.warning("No task state files found")
                    return False
                filepath = task_files[-1]
            
            logger.info(f"Loading task state from: {filepath.name}")
            
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            # Restore tasks
            from task_queue import Task
            for task_id, task_data in state['tasks'].items():
                task = Task.from_dict(task_data)
                task_queue.tasks[task_id] = task
                
                # Re-queue pending tasks
                if task.status.value == 'pending' or task.status.value == 'queued':
                    import heapq
                    heapq.heappush(task_queue.pending_queue, task)
            
            # Restore stats
            task_queue.stats.update(state['stats'])
            
            logger.info(f"✅ Task state loaded: {len(state['tasks'])} tasks restored")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load task state: {e}")
            return False
    
    async def save_agent_state(self, agents: List) -> bool:
        """Save agent states."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = self.agents_dir / f'agents_{timestamp}.json'
            
            state = {
                'timestamp': datetime.now().isoformat(),
                'agents': []
            }
            
            for agent in agents:
                agent_data = agent.get_stats()
                state['agents'].append(agent_data)
            
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.info(f"✅ Agent state saved: {len(agents)} agents")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save agent state: {e}")
            return False
    
    async def create_checkpoint(self, system_state: Dict) -> bool:
        """Create a full system checkpoint."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            checkpoint_name = f'checkpoint_{timestamp}'
            checkpoint_path = self.checkpoints_dir / checkpoint_name
            checkpoint_path.mkdir(exist_ok=True)
            
            # Save system state
            state_file = checkpoint_path / 'system_state.json'
            with open(state_file, 'w') as f:
                json.dump(system_state, f, indent=2)
            
            logger.info(f"✅ Checkpoint created: {checkpoint_name}")
            
            # Cleanup old checkpoints
            await self._cleanup_old_checkpoints()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create checkpoint: {e}")
            return False
    
    async def _cleanup_old_checkpoints(self):
        """Remove old checkpoints, keeping only the most recent ones."""
        try:
            checkpoints = sorted(self.checkpoints_dir.glob('checkpoint_*'))
            
            if len(checkpoints) > self.max_checkpoints:
                to_remove = checkpoints[:-self.max_checkpoints]
                for checkpoint in to_remove:
                    shutil.rmtree(checkpoint)
                    logger.info(f"Removed old checkpoint: {checkpoint.name}")
        
        except Exception as e:
            logger.error(f"Error cleaning up checkpoints: {e}")
    
    async def load_latest_checkpoint(self) -> Optional[Dict]:
        """Load the most recent checkpoint."""
        try:
            checkpoints = sorted(self.checkpoints_dir.glob('checkpoint_*'))
            if not checkpoints:
                logger.warning("No checkpoints found")
                return None
            
            latest = checkpoints[-1]
            state_file = latest / 'system_state.json'
            
            if not state_file.exists():
                logger.warning(f"Checkpoint {latest.name} has no state file")
                return None
            
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            logger.info(f"✅ Loaded checkpoint: {latest.name}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Failed to load checkpoint: {e}")
            return None
    
    async def save_workflow_history(self, workflow_name: str, workflow_data: Dict) -> bool:
        """Save workflow execution history."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = self.workflows_dir / f'{workflow_name}_{timestamp}.json'
            
            history = {
                'workflow_name': workflow_name,
                'timestamp': datetime.now().isoformat(),
                'data': workflow_data
            }
            
            with open(filepath, 'w') as f:
                json.dump(history, f, indent=2)
            
            logger.info(f"✅ Workflow history saved: {workflow_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save workflow history: {e}")
            return False
    
    async def get_workflow_history(self, workflow_name: str = None) -> List[Dict]:
        """Get workflow execution history."""
        try:
            if workflow_name:
                pattern = f'{workflow_name}_*.json'
            else:
                pattern = '*.json'
            
            history_files = sorted(self.workflows_dir.glob(pattern))
            history = []
            
            for filepath in history_files:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    history.append(data)
            
            return history
            
        except Exception as e:
            logger.error(f"❌ Failed to get workflow history: {e}")
            return []
    
    async def start_auto_checkpoint(self, get_system_state_func):
        """Start automatic checkpoint creation."""
        async def checkpoint_loop():
            while True:
                try:
                    await asyncio.sleep(self.checkpoint_interval)
                    
                    # Get current system state
                    system_state = await get_system_state_func()
                    
                    # Create checkpoint
                    await self.create_checkpoint(system_state)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in auto-checkpoint: {e}")
        
        self.auto_checkpoint_task = asyncio.create_task(checkpoint_loop())
        logger.info(f"✅ Auto-checkpoint started (interval: {self.checkpoint_interval}s)")
    
    async def stop_auto_checkpoint(self):
        """Stop automatic checkpoint creation."""
        if self.auto_checkpoint_task:
            self.auto_checkpoint_task.cancel()
            try:
                await self.auto_checkpoint_task
            except asyncio.CancelledError:
                pass
            logger.info("✅ Auto-checkpoint stopped")
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics."""
        def get_dir_size(path: Path) -> int:
            total = 0
            for item in path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
            return total
        
        return {
            'total_size_mb': get_dir_size(self.data_dir) / (1024 * 1024),
            'checkpoints': len(list(self.checkpoints_dir.glob('checkpoint_*'))),
            'task_snapshots': len(list(self.tasks_dir.glob('*.json'))),
            'agent_snapshots': len(list(self.agents_dir.glob('*.json'))),
            'workflow_histories': len(list(self.workflows_dir.glob('*.json'))),
            'data_directory': str(self.data_dir)
        }


class CrashRecoveryManager:
    """
    Manages crash recovery and system resume.
    
    Features:
    - Detect crashes
    - Restore system state
    - Resume interrupted workflows
    - Retry failed tasks
    """
    
    def __init__(self, persistence_manager: PersistenceManager):
        self.persistence = persistence_manager
        self.recovery_log = []
        
        logger.info("CrashRecoveryManager initialized")
    
    async def detect_crash(self) -> bool:
        """Detect if system crashed previously."""
        # Check for crash marker file
        crash_marker = self.persistence.data_dir / '.crash_marker'
        
        if crash_marker.exists():
            logger.warning("⚠️ Previous crash detected")
            return True
        
        return False
    
    async def mark_running(self):
        """Mark system as running (create crash marker)."""
        crash_marker = self.persistence.data_dir / '.crash_marker'
        crash_marker.write_text(datetime.now().isoformat())
        logger.info("System marked as running")
    
    async def mark_clean_shutdown(self):
        """Mark clean shutdown (remove crash marker)."""
        crash_marker = self.persistence.data_dir / '.crash_marker'
        if crash_marker.exists():
            crash_marker.unlink()
        logger.info("Clean shutdown marked")
    
    async def recover_from_crash(self, task_queue, agents) -> Dict:
        """Recover system state after a crash."""
        logger.info("🔄 Starting crash recovery...")
        
        recovery_report = {
            'timestamp': datetime.now().isoformat(),
            'tasks_recovered': 0,
            'agents_recovered': 0,
            'workflows_resumed': 0,
            'errors': []
        }
        
        try:
            # Load latest checkpoint
            checkpoint = await self.persistence.load_latest_checkpoint()
            if checkpoint:
                logger.info(f"Loaded checkpoint from {checkpoint.get('timestamp')}")
            
            # Restore task queue
            task_restored = await self.persistence.load_task_state(task_queue)
            if task_restored:
                recovery_report['tasks_recovered'] = len(task_queue.tasks)
                logger.info(f"✅ Restored {recovery_report['tasks_recovered']} tasks")
            
            # Identify tasks that were running during crash
            running_tasks = []
            for task_id, task in task_queue.tasks.items():
                if task.status.value == 'running' or task.status.value == 'assigned':
                    running_tasks.append(task)
            
            # Reset running tasks to pending for retry
            for task in running_tasks:
                task.status = task_queue.TaskStatus.PENDING
                task.assigned_to = None
                task.started_at = None
                import heapq
                heapq.heappush(task_queue.pending_queue, task)
                logger.info(f"Reset task for retry: {task.task_id}")
            
            recovery_report['workflows_resumed'] = len(running_tasks)
            
            logger.info("✅ Crash recovery complete")
            self.recovery_log.append(recovery_report)
            
        except Exception as e:
            logger.error(f"❌ Error during crash recovery: {e}")
            recovery_report['errors'].append(str(e))
        
        return recovery_report
    
    def get_recovery_history(self) -> List[Dict]:
        """Get history of recovery operations."""
        return self.recovery_log.copy()


# Example usage and testing
async def test_persistence():
    """Test persistence and recovery system."""
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("Testing Persistence and Crash Recovery")
    print("="*60)
    
    # Create persistence manager
    print("\n[Test 1] Creating persistence manager...")
    persistence = PersistenceManager()
    
    # Create crash recovery manager
    print("\n[Test 2] Creating crash recovery manager...")
    recovery = CrashRecoveryManager(persistence)
    
    # Check for previous crash
    print("\n[Test 3] Checking for previous crash...")
    crashed = await recovery.detect_crash()
    if crashed:
        print("  ⚠️ Previous crash detected")
    else:
        print("  ✅ No previous crash")
    
    # Mark system as running
    print("\n[Test 4] Marking system as running...")
    await recovery.mark_running()
    
    # Create test task queue
    print("\n[Test 5] Creating test task queue...")
    from task_queue import TaskQueue, Task, TaskPriority
    task_queue = TaskQueue()
    
    # Add test tasks
    for i in range(10):
        task = Task(
            task_id=f"test_task_{i}",
            task_type="test",
            payload={'data': f'test {i}'},
            priority=TaskPriority.NORMAL
        )
        await task_queue.submit_task(task)
    
    # Save task state
    print("\n[Test 6] Saving task state...")
    await persistence.save_task_state(task_queue)
    
    # Create checkpoint
    print("\n[Test 7] Creating checkpoint...")
    system_state = {
        'timestamp': datetime.now().isoformat(),
        'tasks': len(task_queue.tasks),
        'status': 'running'
    }
    await persistence.create_checkpoint(system_state)
    
    # Save workflow history
    print("\n[Test 8] Saving workflow history...")
    workflow_data = {
        'tasks_submitted': 10,
        'tasks_completed': 5,
        'duration_seconds': 120
    }
    await persistence.save_workflow_history('test_workflow', workflow_data)
    
    # Get storage stats
    print("\n[Test 9] Storage statistics:")
    stats = persistence.get_storage_stats()
    print(json.dumps(stats, indent=2))
    
    # Simulate recovery
    print("\n[Test 10] Simulating crash recovery...")
    new_task_queue = TaskQueue()
    recovery_report = await recovery.recover_from_crash(new_task_queue, [])
    print("Recovery report:")
    print(json.dumps(recovery_report, indent=2))
    
    # Mark clean shutdown
    print("\n[Cleanup] Marking clean shutdown...")
    await recovery.mark_clean_shutdown()
    
    print("\n" + "="*60)
    print("Persistence Tests Complete")
    print("="*60)


if __name__ == '__main__':
    asyncio.run(test_persistence())
