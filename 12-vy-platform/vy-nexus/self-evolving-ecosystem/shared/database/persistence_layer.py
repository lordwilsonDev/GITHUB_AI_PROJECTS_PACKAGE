"""\nData Persistence Layer for Self-Evolving AI Ecosystem\nProvides robust storage with backup and rollback mechanisms\n"""

import sqlite3
import json
import pickle
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from contextlib import contextmanager
import hashlib
import gzip
import threading


class PersistenceLayer:
    """\n    Robust data persistence layer with backup and rollback support.\n    Handles learning data, patterns, optimizations, and system state.\n    """
    
    def __init__(self, db_path: str = "/Users/lordwilson/vy-nexus/data/ecosystem.db",
                 backup_dir: str = "/Users/lordwilson/vy-nexus/data/backups"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self._lock = threading.Lock()
        self._init_database()
        self._init_backup_system()
    
    def _init_database(self):
        """Initialize all database tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Learning patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id TEXT UNIQUE NOT NULL,
                    pattern_type TEXT NOT NULL,
                    feature TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    data TEXT NOT NULL,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    version INTEGER DEFAULT 1
                )
            ''')
            
            # User interactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    interaction_id TEXT UNIQUE NOT NULL,
                    interaction_type TEXT NOT NULL,
                    feature TEXT NOT NULL,
                    data TEXT NOT NULL,
                    success BOOLEAN,
                    timestamp TEXT NOT NULL,
                    metadata TEXT
                )
            ''')
            
            # Optimizations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS optimizations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    optimization_id TEXT UNIQUE NOT NULL,
                    optimization_type TEXT NOT NULL,
                    feature TEXT NOT NULL,
                    before_metric REAL NOT NULL,
                    after_metric REAL NOT NULL,
                    improvement_percent REAL,
                    status TEXT DEFAULT 'pending',
                    applied_at TEXT,
                    data TEXT NOT NULL,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # System state table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    state_id TEXT UNIQUE NOT NULL,
                    feature TEXT NOT NULL,
                    state_type TEXT NOT NULL,
                    state_data TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT
                )
            ''')
            
            # Backup history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS backup_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backup_id TEXT UNIQUE NOT NULL,
                    backup_type TEXT NOT NULL,
                    backup_path TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    size_bytes INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            # Version history table for rollback
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS version_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id TEXT UNIQUE NOT NULL,
                    table_name TEXT NOT NULL,
                    record_id TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    data_before TEXT,
                    data_after TEXT,
                    timestamp TEXT NOT NULL,
                    metadata TEXT
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_patterns_feature ON learning_patterns(feature)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_patterns_type ON learning_patterns(pattern_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_interactions_feature ON user_interactions(feature)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON user_interactions(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_optimizations_feature ON optimizations(feature)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_optimizations_status ON optimizations(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_state_feature ON system_state(feature)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_version_table_record ON version_history(table_name, record_id)')
            
            conn.commit()
    
    def _init_backup_system(self):
        """Initialize backup system and schedule automatic backups"""
        # Create backup subdirectories
        (self.backup_dir / "daily").mkdir(exist_ok=True)
        (self.backup_dir / "weekly").mkdir(exist_ok=True)
        (self.backup_dir / "monthly").mkdir(exist_ok=True)
        (self.backup_dir / "snapshots").mkdir(exist_ok=True)
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _calculate_checksum(self, data: str) -> str:
        """Calculate SHA-256 checksum of data"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _record_version(self, table_name: str, record_id: str, operation: str,
                       data_before: Optional[Dict] = None, data_after: Optional[Dict] = None):
        """Record version history for rollback capability"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            version_id = f"{table_name}_{record_id}_{datetime.now().isoformat()}"
            
            cursor.execute('''
                INSERT INTO version_history 
                (version_id, table_name, record_id, operation, data_before, data_after, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                version_id,
                table_name,
                record_id,
                operation,
                json.dumps(data_before) if data_before else None,
                json.dumps(data_after) if data_after else None,
                datetime.now().isoformat()
            ))
            
            conn.commit()
    
    # ==================== Learning Patterns ====================
    
    def save_learning_pattern(self, pattern_id: str, pattern_type: str, 
                             feature: str, confidence: float, 
                             data: Dict[str, Any], metadata: Optional[Dict] = None) -> bool:
        """\n        Save a learning pattern with version tracking.\n        \n        Args:\n            pattern_id: Unique pattern identifier\n            pattern_type: Type of pattern\n            feature: Feature name\n            confidence: Confidence score (0.0 to 1.0)\n            data: Pattern data\n            metadata: Optional metadata\n        \n        Returns:\n            True if successful\n        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if pattern exists
                cursor.execute('SELECT data, version FROM learning_patterns WHERE pattern_id = ?', (pattern_id,))
                existing = cursor.fetchone()
                
                data_json = json.dumps(data)
                metadata_json = json.dumps(metadata or {})
                
                if existing:
                    # Update existing pattern
                    old_data = json.loads(existing['data'])
                    new_version = existing['version'] + 1
                    
                    # Record version history
                    self._record_version(
                        'learning_patterns',
                        pattern_id,
                        'update',
                        data_before={'data': old_data, 'confidence': confidence},
                        data_after={'data': data, 'confidence': confidence}
                    )
                    
                    cursor.execute('''
                        UPDATE learning_patterns 
                        SET confidence = ?, data = ?, metadata = ?, 
                            updated_at = ?, version = ?
                        WHERE pattern_id = ?
                    ''', (confidence, data_json, metadata_json, datetime.now().isoformat(), 
                         new_version, pattern_id))
                else:
                    # Insert new pattern
                    cursor.execute('''
                        INSERT INTO learning_patterns 
                        (pattern_id, pattern_type, feature, confidence, data, metadata)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (pattern_id, pattern_type, feature, confidence, data_json, metadata_json))
                    
                    # Record version history
                    self._record_version(
                        'learning_patterns',
                        pattern_id,
                        'insert',
                        data_after={'data': data, 'confidence': confidence}
                    )
                
                conn.commit()
                return True
    
    def get_learning_patterns(self, feature: Optional[str] = None,
                             pattern_type: Optional[str] = None,
                             min_confidence: float = 0.0,
                             limit: int = 100) -> List[Dict[str, Any]]:
        """\n        Retrieve learning patterns with filters.\n        \n        Args:\n            feature: Filter by feature name\n            pattern_type: Filter by pattern type\n            min_confidence: Minimum confidence threshold\n            limit: Maximum number of results\n        \n        Returns:\n            List of pattern dictionaries\n        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM learning_patterns WHERE confidence >= ?"
            params = [min_confidence]
            
            if feature:
                query += " AND feature = ?"
                params.append(feature)
            
            if pattern_type:
                query += " AND pattern_type = ?"
                params.append(pattern_type)
            
            query += " ORDER BY confidence DESC, updated_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            patterns = []
            for row in rows:
                patterns.append({
                    'pattern_id': row['pattern_id'],
                    'pattern_type': row['pattern_type'],
                    'feature': row['feature'],
                    'confidence': row['confidence'],
                    'data': json.loads(row['data']),
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'version': row['version']
                })
            
            return patterns
    
    # ==================== User Interactions ====================
    
    def save_interaction(self, interaction_id: str, interaction_type: str,
                        feature: str, data: Dict[str, Any], 
                        success: bool, metadata: Optional[Dict] = None) -> bool:
        """\n        Save user interaction data.\n        \n        Args:\n            interaction_id: Unique interaction identifier\n            interaction_type: Type of interaction\n            feature: Feature name\n            data: Interaction data\n            success: Whether interaction was successful\n            metadata: Optional metadata\n        \n        Returns:\n            True if successful\n        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO user_interactions 
                    (interaction_id, interaction_type, feature, data, success, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    interaction_id,
                    interaction_type,
                    feature,
                    json.dumps(data),
                    success,
                    datetime.now().isoformat(),
                    json.dumps(metadata or {})
                ))
                
                conn.commit()
                return True
    
    def get_interactions(self, feature: Optional[str] = None,
                        interaction_type: Optional[str] = None,
                        success_only: bool = False,
                        hours: int = 24,
                        limit: int = 1000) -> List[Dict[str, Any]]:
        """\n        Retrieve user interactions with filters.\n        \n        Args:\n            feature: Filter by feature name\n            interaction_type: Filter by interaction type\n            success_only: Only return successful interactions\n            hours: Number of hours to look back\n            limit: Maximum number of results\n        \n        Returns:\n            List of interaction dictionaries\n        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            query = "SELECT * FROM user_interactions WHERE timestamp >= ?"
            params = [start_time]
            
            if feature:
                query += " AND feature = ?"
                params.append(feature)
            
            if interaction_type:
                query += " AND interaction_type = ?"
                params.append(interaction_type)
            
            if success_only:
                query += " AND success = 1"
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            interactions = []
            for row in rows:
                interactions.append({
                    'interaction_id': row['interaction_id'],
                    'interaction_type': row['interaction_type'],
                    'feature': row['feature'],
                    'data': json.loads(row['data']),
                    'success': bool(row['success']),
                    'timestamp': row['timestamp'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {}
                })
            
            return interactions
    
    # ==================== Optimizations ====================
    
    def save_optimization(self, optimization_id: str, optimization_type: str,
                         feature: str, before_metric: float, after_metric: float,
                         data: Dict[str, Any], metadata: Optional[Dict] = None) -> bool:
        """\n        Save optimization result.\n        \n        Args:\n            optimization_id: Unique optimization identifier\n            optimization_type: Type of optimization\n            feature: Feature name\n            before_metric: Metric value before optimization\n            after_metric: Metric value after optimization\n            data: Optimization data\n            metadata: Optional metadata\n        \n        Returns:\n            True if successful\n        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                improvement = ((after_metric - before_metric) / before_metric * 100) if before_metric > 0 else 0
                
                cursor.execute('''
                    INSERT INTO optimizations 
                    (optimization_id, optimization_type, feature, before_metric, after_metric, 
                     improvement_percent, data, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    optimization_id,
                    optimization_type,
                    feature,
                    before_metric,
                    after_metric,
                    improvement,
                    json.dumps(data),
                    json.dumps(metadata or {})
                ))
                
                conn.commit()
                return True
    
    def apply_optimization(self, optimization_id: str) -> bool:
        """Mark optimization as applied"""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE optimizations 
                    SET status = 'applied', applied_at = ?
                    WHERE optimization_id = ?
                ''', (datetime.now().isoformat(), optimization_id))
                
                conn.commit()
                return True
    
    # ==================== System State ====================
    
    def save_system_state(self, state_id: str, feature: str, state_type: str,
                         state_data: Dict[str, Any], metadata: Optional[Dict] = None) -> bool:
        """\n        Save system state snapshot.\n        \n        Args:\n            state_id: Unique state identifier\n            feature: Feature name\n            state_type: Type of state\n            state_data: State data\n            metadata: Optional metadata\n        \n        Returns:\n            True if successful\n        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                data_json = json.dumps(state_data)
                checksum = self._calculate_checksum(data_json)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO system_state 
                    (state_id, feature, state_type, state_data, checksum, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    state_id,
                    feature,
                    state_type,
                    data_json,
                    checksum,
                    datetime.now().isoformat(),
                    json.dumps(metadata or {})
                ))
                
                conn.commit()
                return True
    
    def get_system_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve system state by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM system_state WHERE state_id = ?', (state_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'state_id': row['state_id'],
                    'feature': row['feature'],
                    'state_type': row['state_type'],
                    'state_data': json.loads(row['state_data']),
                    'checksum': row['checksum'],
                    'timestamp': row['timestamp'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {}
                }
            
            return None
    
    # ==================== Backup & Rollback ====================
    
    def create_backup(self, backup_type: str = "manual", 
                     compress: bool = True) -> str:
        """\n        Create database backup.\n        \n        Args:\n            backup_type: Type of backup (manual, daily, weekly, monthly)\n            compress: Whether to compress the backup\n        \n        Returns:\n            Backup ID\n        """
        with self._lock:
            backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Determine backup directory
            if backup_type in ['daily', 'weekly', 'monthly']:
                backup_subdir = self.backup_dir / backup_type
            else:
                backup_subdir = self.backup_dir / "snapshots"
            
            backup_subdir.mkdir(exist_ok=True)
            
            # Create backup file path
            backup_filename = f"{backup_id}.db"
            if compress:
                backup_filename += ".gz"
            
            backup_path = backup_subdir / backup_filename
            
            # Copy database
            if compress:
                with open(self.db_path, 'rb') as f_in:
                    with gzip.open(backup_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(self.db_path, backup_path)
            
            # Calculate checksum
            with open(backup_path, 'rb') as f:
                checksum = hashlib.sha256(f.read()).hexdigest()
            
            # Record backup in history
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO backup_history 
                    (backup_id, backup_type, backup_path, checksum, size_bytes, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    backup_id,
                    backup_type,
                    str(backup_path),
                    checksum,
                    backup_path.stat().st_size,
                    json.dumps({'compressed': compress})
                ))
                
                conn.commit()
            
            return backup_id
    
    def restore_backup(self, backup_id: str) -> bool:
        """\n        Restore database from backup.\n        \n        Args:\n            backup_id: Backup ID to restore\n        \n        Returns:\n            True if successful\n        """
        with self._lock:
            # Get backup info
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM backup_history WHERE backup_id = ?', (backup_id,))
                backup_info = cursor.fetchone()
            
            if not backup_info:
                raise ValueError(f"Backup {backup_id} not found")
            
            backup_path = Path(backup_info['backup_path'])
            
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup file {backup_path} not found")
            
            # Create safety backup of current database
            safety_backup_id = self.create_backup(backup_type="pre_restore", compress=True)
            
            try:
                # Restore backup
                metadata = json.loads(backup_info['metadata'])
                
                if metadata.get('compressed', False):
                    with gzip.open(backup_path, 'rb') as f_in:
                        with open(self.db_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                else:
                    shutil.copy2(backup_path, self.db_path)
                
                # Verify checksum
                with open(self.db_path, 'rb') as f:
                    if backup_info['checksum'] == hashlib.sha256(f.read()).hexdigest():
                        return True
                    else:
                        # Checksum mismatch, restore safety backup
                        self.restore_backup(safety_backup_id)
                        raise ValueError("Backup checksum verification failed")
            
            except Exception as e:
                # Restore safety backup on error
                self.restore_backup(safety_backup_id)
                raise e
    
    def rollback_to_version(self, table_name: str, record_id: str, 
                           timestamp: Optional[str] = None) -> bool:
        """\n        Rollback a record to a previous version.\n        \n        Args:\n            table_name: Name of the table\n            record_id: Record identifier\n            timestamp: Timestamp to rollback to (None for previous version)\n        \n        Returns:\n            True if successful\n        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get version history
                if timestamp:
                    cursor.execute('''
                        SELECT * FROM version_history 
                        WHERE table_name = ? AND record_id = ? AND timestamp <= ?
                        ORDER BY timestamp DESC LIMIT 1
                    ''', (table_name, record_id, timestamp))
                else:
                    cursor.execute('''
                        SELECT * FROM version_history 
                        WHERE table_name = ? AND record_id = ?
                        ORDER BY timestamp DESC LIMIT 2
                    ''', (table_name, record_id))
                
                versions = cursor.fetchall()
                
                if len(versions) < 2:
                    return False  # No previous version to rollback to
                
                # Get the version to restore
                restore_version = versions[1] if not timestamp else versions[0]
                
                if restore_version['data_before']:
                    data = json.loads(restore_version['data_before'])
                    
                    # Restore data based on table
                    if table_name == 'learning_patterns':
                        cursor.execute('''
                            UPDATE learning_patterns 
                            SET data = ?, confidence = ?, updated_at = ?
                            WHERE pattern_id = ?
                        ''', (
                            json.dumps(data['data']),
                            data['confidence'],
                            datetime.now().isoformat(),
                            record_id
                        ))
                    
                    conn.commit()
                    return True
                
                return False
    
    def cleanup_old_backups(self, keep_daily: int = 7, keep_weekly: int = 4, 
                           keep_monthly: int = 12):
        """\n        Clean up old backups based on retention policy.\n        \n        Args:\n            keep_daily: Number of daily backups to keep\n            keep_weekly: Number of weekly backups to keep\n            keep_monthly: Number of monthly backups to keep\n        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                for backup_type, keep_count in [('daily', keep_daily), 
                                               ('weekly', keep_weekly), 
                                               ('monthly', keep_monthly)]:
                    # Get backups to delete
                    cursor.execute('''
                        SELECT backup_id, backup_path FROM backup_history 
                        WHERE backup_type = ?
                        ORDER BY created_at DESC
                        LIMIT -1 OFFSET ?
                    ''', (backup_type, keep_count))
                    
                    old_backups = cursor.fetchall()
                    
                    for backup in old_backups:
                        # Delete backup file
                        backup_path = Path(backup['backup_path'])
                        if backup_path.exists():
                            backup_path.unlink()
                        
                        # Delete from history
                        cursor.execute('DELETE FROM backup_history WHERE backup_id = ?', 
                                     (backup['backup_id'],))
                
                conn.commit()


# Global persistence layer instance
_global_persistence = None

def get_persistence_layer() -> PersistenceLayer:
    """Get the global persistence layer instance"""
    global _global_persistence
    if _global_persistence is None:
        _global_persistence = PersistenceLayer()
    return _global_persistence


if __name__ == "__main__":
    # Test the persistence layer
    persistence = get_persistence_layer()
    
    # Test learning pattern storage
    persistence.save_learning_pattern(
        pattern_id="test_pattern_001",
        pattern_type="user_preference",
        feature="learning-engine",
        confidence=0.85,
        data={'preference': 'morning_tasks', 'frequency': 0.9},
        metadata={'source': 'interaction_analysis'}
    )
    
    patterns = persistence.get_learning_patterns(feature="learning-engine")
    print(f"Retrieved {len(patterns)} patterns")
    
    # Test backup
    backup_id = persistence.create_backup(backup_type="manual", compress=True)
    print(f"Created backup: {backup_id}")
    
    print("\n✅ Persistence layer test complete!")
