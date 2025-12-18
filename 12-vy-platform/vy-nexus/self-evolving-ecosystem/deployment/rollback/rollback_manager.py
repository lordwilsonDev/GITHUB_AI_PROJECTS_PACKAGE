"""\nRollback Manager for Self-Evolving AI Ecosystem\nProvides comprehensive backup and rollback mechanisms for all system modifications\n"""

import sqlite3
import json
import shutil
import gzip
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pickle
import subprocess
import os


class RollbackManager:
    """\n    Comprehensive rollback manager with backup and recovery capabilities.\n    Ensures all system modifications can be safely reverted.\n    """
    
    def __init__(self, 
                 backup_root: str = "/Users/lordwilson/vy-nexus/data/rollback",
                 db_path: str = "/Users/lordwilson/vy-nexus/data/rollback_manager.db"):
        self.backup_root = Path(backup_root)
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create backup subdirectories
        self.snapshots_dir = self.backup_root / "snapshots"
        self.incremental_dir = self.backup_root / "incremental"
        self.system_state_dir = self.backup_root / "system_state"
        self.config_dir = self.backup_root / "config"
        
        for dir_path in [self.snapshots_dir, self.incremental_dir, 
                        self.system_state_dir, self.config_dir]:
            dir_path.mkdir(exist_ok=True)
        
        self._init_database()
    
    def _init_database(self):
        """Initialize rollback tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Snapshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id TEXT UNIQUE NOT NULL,
                snapshot_type TEXT NOT NULL,
                snapshot_name TEXT NOT NULL,
                description TEXT,
                backup_path TEXT NOT NULL,
                checksum TEXT NOT NULL,
                size_bytes INTEGER,
                compressed BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT,
                metadata TEXT
            )
        ''')
        
        # Modifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS modifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                modification_id TEXT UNIQUE NOT NULL,
                modification_type TEXT NOT NULL,
                component TEXT NOT NULL,
                description TEXT,
                before_snapshot_id TEXT,
                after_snapshot_id TEXT,
                rollback_procedure TEXT,
                applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
                rolled_back_at TEXT,
                rollback_reason TEXT,
                status TEXT DEFAULT 'applied',
                metadata TEXT
            )
        ''')
        
        # Rollback history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rollback_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rollback_id TEXT UNIQUE NOT NULL,
                modification_id TEXT NOT NULL,
                rollback_type TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                duration_ms REAL,
                performed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                performed_by TEXT,
                metadata TEXT
            )
        ''')
        
        # System state checkpoints table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checkpoint_id TEXT UNIQUE NOT NULL,
                checkpoint_name TEXT NOT NULL,
                checkpoint_type TEXT NOT NULL,
                system_state TEXT NOT NULL,
                health_status TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_snapshots_type ON snapshots(snapshot_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_modifications_component ON modifications(component)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_modifications_status ON modifications(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rollback_modification ON rollback_history(modification_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_checkpoints_type ON system_checkpoints(checkpoint_type)')
        
        conn.commit()
        conn.close()
    
    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID with prefix"""
        content = f"{prefix}_{datetime.now().isoformat()}_{os.urandom(8).hex()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    # ==================== Snapshot Management ====================
    
    def create_snapshot(self, snapshot_type: str, snapshot_name: str,
                       source_paths: List[str],
                       description: Optional[str] = None,
                       compress: bool = True,
                       expires_days: Optional[int] = None,
                       metadata: Optional[Dict] = None) -> str:
        """\n        Create a snapshot of specified paths.\n        \n        Args:\n            snapshot_type: Type of snapshot (full, incremental, config, data)\n            snapshot_name: Name for the snapshot\n            source_paths: List of paths to backup\n            description: Optional description\n            compress: Whether to compress the snapshot\n            expires_days: Days until snapshot expires (None = never)\n            metadata: Additional metadata\n        \n        Returns:\n            Snapshot ID\n        """
        snapshot_id = self._generate_id('snapshot')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create snapshot directory
        snapshot_dir = self.snapshots_dir / f"{snapshot_type}_{timestamp}_{snapshot_id}"
        snapshot_dir.mkdir(exist_ok=True)
        
        # Backup each source path
        total_size = 0
        for source_path in source_paths:
            source = Path(source_path)
            if not source.exists():
                continue
            
            if source.is_file():
                dest = snapshot_dir / source.name
                if compress:
                    with open(source, 'rb') as f_in:
                        with gzip.open(f"{dest}.gz", 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    total_size += Path(f"{dest}.gz").stat().st_size
                else:
                    shutil.copy2(source, dest)
                    total_size += dest.stat().st_size
            elif source.is_dir():
                dest = snapshot_dir / source.name
                if compress:
                    # Create tar.gz archive
                    archive_path = f"{dest}.tar.gz"
                    shutil.make_archive(str(dest), 'gztar', source.parent, source.name)
                    total_size += Path(archive_path).stat().st_size
                else:
                    shutil.copytree(source, dest)
                    total_size += sum(f.stat().st_size for f in dest.rglob('*') if f.is_file())
        
        # Calculate checksum of snapshot directory
        checksum = self._calculate_checksum_dir(snapshot_dir)
        
        # Calculate expiration
        expires_at = None
        if expires_days:
            expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat()
        
        # Record snapshot
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO snapshots 
            (snapshot_id, snapshot_type, snapshot_name, description, backup_path, 
             checksum, size_bytes, compressed, expires_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            snapshot_id,
            snapshot_type,
            snapshot_name,
            description,
            str(snapshot_dir),
            checksum,
            total_size,
            compress,
            expires_at,
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
        
        return snapshot_id
    
    def _calculate_checksum_dir(self, directory: Path) -> str:
        """Calculate checksum of directory contents"""
        sha256 = hashlib.sha256()
        for file_path in sorted(directory.rglob('*')):
            if file_path.is_file():
                sha256.update(str(file_path.relative_to(directory)).encode())
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(8192), b''):
                        sha256.update(chunk)
        return sha256.hexdigest()
    
    def restore_snapshot(self, snapshot_id: str, 
                        restore_paths: Optional[Dict[str, str]] = None,
                        verify_checksum: bool = True) -> bool:
        """\n        Restore from a snapshot.\n        \n        Args:\n            snapshot_id: Snapshot ID to restore\n            restore_paths: Optional mapping of source to destination paths\n            verify_checksum: Whether to verify checksum before restore\n        \n        Returns:\n            True if successful\n        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM snapshots WHERE snapshot_id = ?', (snapshot_id,))
        snapshot = cursor.fetchone()
        conn.close()
        
        if not snapshot:
            raise ValueError(f"Snapshot {snapshot_id} not found")
        
        snapshot_dir = Path(snapshot['backup_path'])
        
        if not snapshot_dir.exists():
            raise FileNotFoundError(f"Snapshot directory {snapshot_dir} not found")
        
        # Verify checksum
        if verify_checksum:
            current_checksum = self._calculate_checksum_dir(snapshot_dir)
            if current_checksum != snapshot['checksum']:
                raise ValueError("Snapshot checksum verification failed")
        
        # Restore files
        compressed = bool(snapshot['compressed'])
        
        for item in snapshot_dir.iterdir():
            if compressed and item.suffix == '.gz':
                # Decompress file
                if restore_paths and item.stem in restore_paths:
                    dest = Path(restore_paths[item.stem])
                else:
                    dest = Path.cwd() / item.stem
                
                with gzip.open(item, 'rb') as f_in:
                    with open(dest, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            elif item.suffix == '.tar':
                # Extract tar archive
                if restore_paths and item.stem in restore_paths:
                    extract_dir = Path(restore_paths[item.stem])
                else:
                    extract_dir = Path.cwd()
                
                shutil.unpack_archive(item, extract_dir)
            else:
                # Copy file/directory
                if restore_paths and item.name in restore_paths:
                    dest = Path(restore_paths[item.name])
                else:
                    dest = Path.cwd() / item.name
                
                if item.is_file():
                    shutil.copy2(item, dest)
                else:
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
        
        return True
    
    # ==================== Modification Tracking ====================
    
    def record_modification(self, modification_type: str, component: str,
                          description: str,
                          before_state: Optional[Dict] = None,
                          after_state: Optional[Dict] = None,
                          rollback_procedure: Optional[str] = None,
                          metadata: Optional[Dict] = None) -> str:
        """\n        Record a system modification with rollback information.\n        \n        Args:\n            modification_type: Type of modification\n            component: Component being modified\n            description: Description of modification\n            before_state: State before modification\n            after_state: State after modification\n            rollback_procedure: Procedure to rollback\n            metadata: Additional metadata\n        \n        Returns:\n            Modification ID\n        """
        modification_id = self._generate_id('mod')
        
        # Create snapshots if states provided
        before_snapshot_id = None
        after_snapshot_id = None
        
        if before_state:
            before_snapshot_id = self._create_state_snapshot(
                f"{component}_before",
                before_state,
                f"Before {modification_type}"
            )
        
        if after_state:
            after_snapshot_id = self._create_state_snapshot(
                f"{component}_after",
                after_state,
                f"After {modification_type}"
            )
        
        # Record modification
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO modifications 
            (modification_id, modification_type, component, description, 
             before_snapshot_id, after_snapshot_id, rollback_procedure, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            modification_id,
            modification_type,
            component,
            description,
            before_snapshot_id,
            after_snapshot_id,
            rollback_procedure,
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
        
        return modification_id
    
    def _create_state_snapshot(self, name: str, state: Dict, description: str) -> str:
        """Create snapshot of state data"""
        snapshot_id = self._generate_id('state')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save state to file
        state_file = self.system_state_dir / f"{name}_{timestamp}_{snapshot_id}.json.gz"
        with gzip.open(state_file, 'wt') as f:
            json.dump(state, f, indent=2)
        
        checksum = self._calculate_checksum(state_file)
        size = state_file.stat().st_size
        
        # Record snapshot
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO snapshots 
            (snapshot_id, snapshot_type, snapshot_name, description, backup_path, 
             checksum, size_bytes, compressed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            snapshot_id,
            'state',
            name,
            description,
            str(state_file),
            checksum,
            size,
            True
        ))
        
        conn.commit()
        conn.close()
        
        return snapshot_id
    
    def rollback_modification(self, modification_id: str, 
                            reason: str,
                            performed_by: str = "system") -> bool:
        """\n        Rollback a modification.\n        \n        Args:\n            modification_id: Modification ID to rollback\n            reason: Reason for rollback\n            performed_by: Who performed the rollback\n        \n        Returns:\n            True if successful\n        """
        import time
        start_time = time.time()
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get modification
        cursor.execute('SELECT * FROM modifications WHERE modification_id = ?', (modification_id,))
        modification = cursor.fetchone()
        
        if not modification:
            conn.close()
            raise ValueError(f"Modification {modification_id} not found")
        
        if modification['status'] == 'rolled_back':
            conn.close()
            raise ValueError(f"Modification {modification_id} already rolled back")
        
        rollback_id = self._generate_id('rollback')
        success = False
        error_message = None
        
        try:
            # Restore before state if available
            if modification['before_snapshot_id']:
                self.restore_snapshot(modification['before_snapshot_id'])
            
            # Execute rollback procedure if provided
            if modification['rollback_procedure']:
                exec(modification['rollback_procedure'])
            
            # Update modification status
            cursor.execute('''
                UPDATE modifications 
                SET status = 'rolled_back', rolled_back_at = ?, rollback_reason = ?
                WHERE modification_id = ?
            ''', (datetime.now().isoformat(), reason, modification_id))
            
            success = True
        
        except Exception as e:
            error_message = str(e)
            success = False
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Record rollback
        cursor.execute('''
            INSERT INTO rollback_history 
            (rollback_id, modification_id, rollback_type, success, error_message, 
             duration_ms, performed_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            rollback_id,
            modification_id,
            'full',
            success,
            error_message,
            duration_ms,
            performed_by
        ))
        
        conn.commit()
        conn.close()
        
        if not success:
            raise RuntimeError(f"Rollback failed: {error_message}")
        
        return success
    
    # ==================== System Checkpoints ====================
    
    def create_system_checkpoint(self, checkpoint_name: str, 
                                checkpoint_type: str,
                                system_state: Dict[str, Any],
                                health_status: str = "healthy",
                                metadata: Optional[Dict] = None) -> str:
        """\n        Create a system checkpoint.\n        \n        Args:\n            checkpoint_name: Name for checkpoint\n            checkpoint_type: Type of checkpoint\n            system_state: Current system state\n            health_status: System health status\n            metadata: Additional metadata\n        \n        Returns:\n            Checkpoint ID\n        """
        checkpoint_id = self._generate_id('checkpoint')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_checkpoints 
            (checkpoint_id, checkpoint_name, checkpoint_type, system_state, health_status, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            checkpoint_id,
            checkpoint_name,
            checkpoint_type,
            json.dumps(system_state),
            health_status,
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
        
        return checkpoint_id
    
    def restore_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """Restore system to a checkpoint"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM system_checkpoints WHERE checkpoint_id = ?', (checkpoint_id,))
        checkpoint = cursor.fetchone()
        conn.close()
        
        if not checkpoint:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
        
        return json.loads(checkpoint['system_state'])
    
    # ==================== Cleanup & Maintenance ====================
    
    def cleanup_expired_snapshots(self):
        """Remove expired snapshots"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        # Get expired snapshots
        cursor.execute('''
            SELECT snapshot_id, backup_path FROM snapshots 
            WHERE expires_at IS NOT NULL AND expires_at < ?
        ''', (now,))
        
        expired = cursor.fetchall()
        
        for snapshot_id, backup_path in expired:
            # Delete backup files
            path = Path(backup_path)
            if path.exists():
                if path.is_file():
                    path.unlink()
                else:
                    shutil.rmtree(path)
            
            # Delete from database
            cursor.execute('DELETE FROM snapshots WHERE snapshot_id = ?', (snapshot_id,))
        
        conn.commit()
        conn.close()
        
        return len(expired)
    
    def get_rollback_history(self, modification_id: Optional[str] = None,
                            limit: int = 50) -> List[Dict[str, Any]]:
        """Get rollback history"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if modification_id:
            cursor.execute('''
                SELECT * FROM rollback_history 
                WHERE modification_id = ?
                ORDER BY performed_at DESC
                LIMIT ?
            ''', (modification_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM rollback_history 
                ORDER BY performed_at DESC
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            history.append({
                'rollback_id': row['rollback_id'],
                'modification_id': row['modification_id'],
                'rollback_type': row['rollback_type'],
                'success': bool(row['success']),
                'error_message': row['error_message'],
                'duration_ms': row['duration_ms'],
                'performed_at': row['performed_at'],
                'performed_by': row['performed_by']
            })
        
        conn.close()
        return history


# Global rollback manager instance
_global_rollback_manager = None

def get_rollback_manager() -> RollbackManager:
    """Get the global rollback manager instance"""
    global _global_rollback_manager
    if _global_rollback_manager is None:
        _global_rollback_manager = RollbackManager()
    return _global_rollback_manager


if __name__ == "__main__":
    # Test the rollback manager
    rm = get_rollback_manager()
    
    # Create a snapshot
    snapshot_id = rm.create_snapshot(
        snapshot_type="config",
        snapshot_name="test_config",
        source_paths=["/Users/lordwilson/vy-nexus/self-evolving-ecosystem/shared/utils/config.py"],
        description="Test configuration snapshot",
        compress=True,
        expires_days=30
    )
    print(f"Created snapshot: {snapshot_id}")
    
    # Record a modification
    mod_id = rm.record_modification(
        modification_type="config_update",
        component="learning-engine",
        description="Updated learning rate",
        before_state={'learning_rate': 0.01},
        after_state={'learning_rate': 0.02},
        rollback_procedure="# Restore learning rate\nconfig['learning_rate'] = 0.01"
    )
    print(f"Recorded modification: {mod_id}")
    
    # Create system checkpoint
    checkpoint_id = rm.create_system_checkpoint(
        checkpoint_name="pre_deployment",
        checkpoint_type="deployment",
        system_state={
            'features_enabled': ['learning-engine', 'process-optimization'],
            'version': '1.0.0',
            'health': 'healthy'
        },
        health_status="healthy"
    )
    print(f"Created checkpoint: {checkpoint_id}")
    
    print("\n✅ Rollback manager test complete!")
