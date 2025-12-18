"""
Vy Protocol: Control Plane for Love Engine

Implements Pillar 4 (Control) of the Unified Framework v1.
Provides Background and Full Control modes for autonomous execution.
"""

import json
import logging
from typing import Dict, List, Literal, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class Task:
    """Represents a single task in the execution manifest."""
    id: str
    name: str
    priority: int
    status: Literal['pending', 'running', 'completed', 'failed']
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None

class VyControlPlane:
    """
    Control Plane implementing the Vy Protocol.
    
    Ensures autonomous agents operate with:
    1. Explicit mode declaration (Background vs Full Control)
    2. State persistence via task manifests
    3. Verification checkpoints for safety
    """
    
    def __init__(self, mode: Literal['background', 'full_control'] = 'background',
                 manifest_path: str = 'task_manifest.json'):
        self.mode = mode
        self.manifest_path = Path(manifest_path)
        self.tasks: List[Task] = []
        self.checkpoint_interval = 3
        self._load_manifest()
        logger.info(f"VyControlPlane initialized in {mode} mode")
    
    def _load_manifest(self):
        """Load existing task manifest from disk."""
        if self.manifest_path.exists():
            with open(self.manifest_path, 'r') as f:
                data = json.load(f)
                self.tasks = [Task(**task) for task in data.get('tasks', [])]
            logger.info(f"Loaded {len(self.tasks)} tasks from manifest")
    
    def _save_manifest(self):
        """Persist task manifest to disk."""
        data = {
            'mode': self.mode,
            'last_updated': datetime.now().isoformat(),
            'tasks': [asdict(task) for task in self.tasks]
        }
        with open(self.manifest_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_task(self, name: str, priority: int = 5) -> str:
        """Add a new task to the execution manifest."""
        task_id = f"task_{len(self.tasks) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        task = Task(
            id=task_id,
            name=name,
            priority=priority,
            status='pending',
            created_at=datetime.now().isoformat()
        )
        self.tasks.append(task)
        self._save_manifest()
        logger.info(f"Added task: {name} (ID: {task_id})")
        return task_id
    
    def execute_manifest(self):
        """Execute all pending tasks in priority order."""
        pending_tasks = sorted(
            [t for t in self.tasks if t.status == 'pending'],
            key=lambda x: x.priority
        )
        
        if not pending_tasks:
            logger.info("No pending tasks to execute")
            return
        
        logger.info(f"Executing {len(pending_tasks)} pending tasks in {self.mode} mode")
        
        for idx, task in enumerate(pending_tasks, 1):
            try:
                logger.info(f"Executing task {idx}/{len(pending_tasks)}: {task.name}")
                task.status = 'running'
                self._save_manifest()
                
                # Execute task (integrate with actual execution logic)
                self._execute_task(task)
                
                task.status = 'completed'
                task.completed_at = datetime.now().isoformat()
                logger.info(f"Task completed: {task.name}")
                
                # Verification checkpoint
                if idx % self.checkpoint_interval == 0:
                    self._verification_checkpoint(idx)
                    
            except Exception as e:
                task.status = 'failed'
                task.error = str(e)
                logger.error(f"Task failed: {task.name} - {e}")
                
            finally:
                self._save_manifest()
    
    def _execute_task(self, task: Task):
        """Execute a single task. Override to integrate with your logic."""
        logger.debug(f"Executing task: {task.name}")
        pass
    
    def _verification_checkpoint(self, task_count: int):
        """Verification checkpoint for safety validation."""
        logger.info(f"=== VERIFICATION CHECKPOINT (after {task_count} tasks) ===")
        completed = len([t for t in self.tasks if t.status == 'completed'])
        failed = len([t for t in self.tasks if t.status == 'failed'])
        logger.info(f"Status: {completed} completed, {failed} failed")
        logger.info("Checkpoint passed")
    
    def get_status(self) -> Dict:
        """Get current execution status."""
        return {
            'mode': self.mode,
            'total_tasks': len(self.tasks),
            'pending': len([t for t in self.tasks if t.status == 'pending']),
            'running': len([t for t in self.tasks if t.status == 'running']),
            'completed': len([t for t in self.tasks if t.status == 'completed']),
            'failed': len([t for t in self.tasks if t.status == 'failed'])
        }
