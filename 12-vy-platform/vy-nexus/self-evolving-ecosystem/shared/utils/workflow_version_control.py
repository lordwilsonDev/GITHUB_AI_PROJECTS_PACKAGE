"""\nWorkflow Version Control System for Self-Evolving AI Ecosystem\nMaintains version history and tracks performance metrics across iterations\n"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import difflib
from dataclasses import dataclass, asdict


@dataclass
class WorkflowVersion:
    """Represents a workflow version"""
    version_id: str
    workflow_id: str
    version_number: int
    workflow_data: Dict[str, Any]
    changes_summary: str
    created_by: str
    created_at: str
    performance_metrics: Dict[str, float]
    tags: List[str]


class WorkflowVersionControl:
    """\n    Version control system for workflows with performance tracking.\n    Maintains complete history and enables comparison across iterations.\n    """
    
    def __init__(self, db_path: str = "/Users/lordwilson/vy-nexus/data/workflow_versions.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize workflow version control database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Workflows table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT UNIQUE NOT NULL,
                workflow_name TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                description TEXT,
                current_version INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # Workflow versions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_id TEXT UNIQUE NOT NULL,
                workflow_id TEXT NOT NULL,
                version_number INTEGER NOT NULL,
                workflow_data TEXT NOT NULL,
                workflow_hash TEXT NOT NULL,
                changes_summary TEXT,
                created_by TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                parent_version_id TEXT,
                tags TEXT,
                metadata TEXT,
                UNIQUE(workflow_id, version_number)
            )
        ''')
        
        # Version performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS version_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                measurement_timestamp TEXT NOT NULL,
                sample_size INTEGER,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Version comparisons table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS version_comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comparison_id TEXT UNIQUE NOT NULL,
                workflow_id TEXT NOT NULL,
                version_a_id TEXT NOT NULL,
                version_b_id TEXT NOT NULL,
                comparison_type TEXT NOT NULL,
                comparison_result TEXT NOT NULL,
                performance_delta TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # Workflow deployments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_deployments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deployment_id TEXT UNIQUE NOT NULL,
                workflow_id TEXT NOT NULL,
                version_id TEXT NOT NULL,
                environment TEXT NOT NULL,
                deployment_status TEXT NOT NULL,
                deployed_at TEXT,
                rolled_back_at TEXT,
                rollback_reason TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_workflows_name ON workflows(workflow_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_versions_workflow ON workflow_versions(workflow_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_versions_number ON workflow_versions(version_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_perf_version ON version_performance(version_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_comparisons_workflow ON version_comparisons(workflow_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_deployments_workflow ON workflow_deployments(workflow_id)')
        
        conn.commit()
        conn.close()
    
    def _generate_workflow_id(self, workflow_name: str) -> str:
        """Generate unique workflow ID"""
        content = f"{workflow_name}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _generate_version_id(self, workflow_id: str, version_number: int) -> str:
        """Generate unique version ID"""
        content = f"{workflow_id}_v{version_number}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _calculate_workflow_hash(self, workflow_data: Dict[str, Any]) -> str:
        """Calculate hash of workflow data for change detection"""
        data_str = json.dumps(workflow_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    # ==================== Workflow Management ====================
    
    def create_workflow(self, workflow_name: str, workflow_type: str,
                       workflow_data: Dict[str, Any],
                       description: Optional[str] = None,
                       created_by: str = "system",
                       tags: Optional[List[str]] = None,
                       metadata: Optional[Dict] = None) -> str:
        """\n        Create a new workflow with initial version.\n        \n        Args:\n            workflow_name: Name of the workflow\n            workflow_type: Type of workflow\n            workflow_data: Workflow definition/configuration\n            description: Optional description\n            created_by: Creator identifier\n            tags: Optional tags\n            metadata: Additional metadata\n        \n        Returns:\n            Workflow ID\n        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        workflow_id = self._generate_workflow_id(workflow_name)
        
        # Create workflow
        cursor.execute('''
            INSERT INTO workflows (workflow_id, workflow_name, workflow_type, description, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            workflow_id,
            workflow_name,
            workflow_type,
            description,
            json.dumps(metadata or {})
        ))
        
        # Create initial version
        version_id = self._generate_version_id(workflow_id, 1)
        workflow_hash = self._calculate_workflow_hash(workflow_data)
        
        cursor.execute('''
            INSERT INTO workflow_versions 
            (version_id, workflow_id, version_number, workflow_data, workflow_hash, 
             changes_summary, created_by, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            version_id,
            workflow_id,
            1,
            json.dumps(workflow_data),
            workflow_hash,
            "Initial version",
            created_by,
            json.dumps(tags or [])
        ))
        
        conn.commit()
        conn.close()
        
        return workflow_id
    
    def create_version(self, workflow_id: str, workflow_data: Dict[str, Any],
                      changes_summary: str,
                      created_by: str = "system",
                      tags: Optional[List[str]] = None,
                      metadata: Optional[Dict] = None) -> str:
        """\n        Create a new version of an existing workflow.\n        \n        Args:\n            workflow_id: Workflow ID\n            workflow_data: Updated workflow definition\n            changes_summary: Summary of changes\n            created_by: Creator identifier\n            tags: Optional tags\n            metadata: Additional metadata\n        \n        Returns:\n            Version ID\n        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current version number
        cursor.execute('SELECT current_version FROM workflows WHERE workflow_id = ?', (workflow_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            raise ValueError(f"Workflow {workflow_id} not found")
        
        current_version = row[0]
        new_version = current_version + 1
        
        # Get parent version ID
        cursor.execute(
            'SELECT version_id FROM workflow_versions WHERE workflow_id = ? AND version_number = ?',
            (workflow_id, current_version)
        )
        parent_version_id = cursor.fetchone()[0]
        
        # Create new version
        version_id = self._generate_version_id(workflow_id, new_version)
        workflow_hash = self._calculate_workflow_hash(workflow_data)
        
        cursor.execute('''
            INSERT INTO workflow_versions 
            (version_id, workflow_id, version_number, workflow_data, workflow_hash, 
             changes_summary, created_by, parent_version_id, tags, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            version_id,
            workflow_id,
            new_version,
            json.dumps(workflow_data),
            workflow_hash,
            changes_summary,
            created_by,
            parent_version_id,
            json.dumps(tags or []),
            json.dumps(metadata or {})
        ))
        
        # Update workflow current version
        cursor.execute('''
            UPDATE workflows 
            SET current_version = ?, updated_at = ?
            WHERE workflow_id = ?
        ''', (new_version, datetime.now().isoformat(), workflow_id))
        
        conn.commit()
        conn.close()
        
        return version_id
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow information"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM workflows WHERE workflow_id = ?', (workflow_id,))
        row = cursor.fetchone()
        
        if row:
            workflow = {
                'workflow_id': row['workflow_id'],
                'workflow_name': row['workflow_name'],
                'workflow_type': row['workflow_type'],
                'description': row['description'],
                'current_version': row['current_version'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else {}
            }
            conn.close()
            return workflow
        
        conn.close()
        return None
    
    def get_version(self, version_id: str) -> Optional[WorkflowVersion]:
        """Get specific workflow version"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM workflow_versions WHERE version_id = ?', (version_id,))
        row = cursor.fetchone()
        
        if row:
            # Get performance metrics for this version
            cursor.execute(
                'SELECT metric_name, AVG(metric_value) as avg_value FROM version_performance WHERE version_id = ? GROUP BY metric_name',
                (version_id,)
            )
            perf_metrics = {r[0]: r[1] for r in cursor.fetchall()}
            
            version = WorkflowVersion(
                version_id=row['version_id'],
                workflow_id=row['workflow_id'],
                version_number=row['version_number'],
                workflow_data=json.loads(row['workflow_data']),
                changes_summary=row['changes_summary'],
                created_by=row['created_by'],
                created_at=row['created_at'],
                performance_metrics=perf_metrics,
                tags=json.loads(row['tags']) if row['tags'] else []
            )
            
            conn.close()
            return version
        
        conn.close()
        return None
    
    def get_version_history(self, workflow_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """\n        Get version history for a workflow.\n        \n        Args:\n            workflow_id: Workflow ID\n            limit: Maximum number of versions to return\n        \n        Returns:\n            List of version dictionaries\n        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM workflow_versions 
            WHERE workflow_id = ?
            ORDER BY version_number DESC
            LIMIT ?
        ''', (workflow_id, limit))
        
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            history.append({
                'version_id': row['version_id'],
                'version_number': row['version_number'],
                'changes_summary': row['changes_summary'],
                'created_by': row['created_by'],
                'created_at': row['created_at'],
                'tags': json.loads(row['tags']) if row['tags'] else []
            })
        
        conn.close()
        return history
    
    # ==================== Performance Tracking ====================
    
    def record_performance_metric(self, version_id: str, metric_name: str,
                                 metric_value: float, metric_unit: Optional[str] = None,
                                 sample_size: Optional[int] = None,
                                 metadata: Optional[Dict] = None):
        """\n        Record performance metric for a workflow version.\n        \n        Args:\n            version_id: Version ID\n            metric_name: Name of metric\n            metric_value: Metric value\n            metric_unit: Unit of measurement\n            sample_size: Number of samples\n            metadata: Additional metadata\n        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO version_performance 
            (version_id, metric_name, metric_value, metric_unit, measurement_timestamp, sample_size, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            version_id,
            metric_name,
            metric_value,
            metric_unit,
            datetime.now().isoformat(),
            sample_size,
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
    
    def get_performance_metrics(self, version_id: str) -> Dict[str, Any]:
        """Get performance metrics for a version"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT metric_name, AVG(metric_value) as avg_value, 
                   MIN(metric_value) as min_value, MAX(metric_value) as max_value,
                   COUNT(*) as count
            FROM version_performance 
            WHERE version_id = ?
            GROUP BY metric_name
        ''', (version_id,))
        
        metrics = {}
        for row in cursor.fetchall():
            metrics[row[0]] = {
                'avg': row[1],
                'min': row[2],
                'max': row[3],
                'count': row[4]
            }
        
        conn.close()
        return metrics
    
    def compare_performance(self, version_a_id: str, version_b_id: str) -> Dict[str, Any]:
        """\n        Compare performance metrics between two versions.\n        \n        Args:\n            version_a_id: First version ID\n            version_b_id: Second version ID\n        \n        Returns:\n            Comparison results\n        """
        metrics_a = self.get_performance_metrics(version_a_id)
        metrics_b = self.get_performance_metrics(version_b_id)
        
        comparison = {
            'version_a': version_a_id,
            'version_b': version_b_id,
            'metrics': {}
        }
        
        # Compare common metrics
        common_metrics = set(metrics_a.keys()) & set(metrics_b.keys())
        
        for metric in common_metrics:
            a_val = metrics_a[metric]['avg']
            b_val = metrics_b[metric]['avg']
            
            improvement = ((b_val - a_val) / a_val * 100) if a_val != 0 else 0
            
            comparison['metrics'][metric] = {
                'version_a_avg': a_val,
                'version_b_avg': b_val,
                'improvement_percent': improvement,
                'better_version': version_b_id if b_val > a_val else version_a_id
            }
        
        return comparison
    
    # ==================== Version Comparison ====================
    
    def compare_versions(self, version_a_id: str, version_b_id: str,
                        comparison_type: str = "full") -> str:
        """\n        Compare two workflow versions.\n        \n        Args:\n            version_a_id: First version ID\n            version_b_id: Second version ID\n            comparison_type: Type of comparison (full, data_only, performance_only)\n        \n        Returns:\n            Comparison ID\n        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get versions
        version_a = self.get_version(version_a_id)
        version_b = self.get_version(version_b_id)
        
        if not version_a or not version_b:
            conn.close()
            raise ValueError("One or both versions not found")
        
        comparison_result = {}
        
        if comparison_type in ['full', 'data_only']:
            # Compare workflow data
            data_a = json.dumps(version_a.workflow_data, indent=2, sort_keys=True).splitlines()
            data_b = json.dumps(version_b.workflow_data, indent=2, sort_keys=True).splitlines()
            
            diff = list(difflib.unified_diff(data_a, data_b, lineterm=''))
            comparison_result['data_diff'] = diff
            comparison_result['data_changed'] = len(diff) > 0
        
        if comparison_type in ['full', 'performance_only']:
            # Compare performance
            perf_comparison = self.compare_performance(version_a_id, version_b_id)
            comparison_result['performance'] = perf_comparison
        
        # Save comparison
        comparison_id = hashlib.md5(f"{version_a_id}_{version_b_id}_{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        cursor.execute('''
            INSERT INTO version_comparisons 
            (comparison_id, workflow_id, version_a_id, version_b_id, comparison_type, 
             comparison_result, performance_delta)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            comparison_id,
            version_a.workflow_id,
            version_a_id,
            version_b_id,
            comparison_type,
            json.dumps(comparison_result),
            json.dumps(comparison_result.get('performance', {}))
        ))
        
        conn.commit()
        conn.close()
        
        return comparison_id
    
    # ==================== Deployment Tracking ====================
    
    def deploy_version(self, workflow_id: str, version_id: str,
                      environment: str, metadata: Optional[Dict] = None) -> str:
        """\n        Record workflow version deployment.\n        \n        Args:\n            workflow_id: Workflow ID\n            version_id: Version ID to deploy\n            environment: Deployment environment\n            metadata: Additional metadata\n        \n        Returns:\n            Deployment ID\n        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        deployment_id = hashlib.md5(f"{workflow_id}_{version_id}_{environment}_{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        cursor.execute('''
            INSERT INTO workflow_deployments 
            (deployment_id, workflow_id, version_id, environment, deployment_status, deployed_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            deployment_id,
            workflow_id,
            version_id,
            environment,
            'deployed',
            datetime.now().isoformat(),
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
        
        return deployment_id
    
    def rollback_deployment(self, deployment_id: str, reason: str):
        """\n        Rollback a deployment.\n        \n        Args:\n            deployment_id: Deployment ID\n            reason: Rollback reason\n        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE workflow_deployments 
            SET deployment_status = 'rolled_back', rolled_back_at = ?, rollback_reason = ?
            WHERE deployment_id = ?
        ''', (datetime.now().isoformat(), reason, deployment_id))
        
        conn.commit()
        conn.close()
    
    def get_deployment_history(self, workflow_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get deployment history for a workflow"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM workflow_deployments 
            WHERE workflow_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (workflow_id, limit))
        
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            history.append({
                'deployment_id': row['deployment_id'],
                'version_id': row['version_id'],
                'environment': row['environment'],
                'deployment_status': row['deployment_status'],
                'deployed_at': row['deployed_at'],
                'rolled_back_at': row['rolled_back_at'],
                'rollback_reason': row['rollback_reason']
            })
        
        conn.close()
        return history


# Global workflow version control instance
_global_wvc = None

def get_workflow_version_control() -> WorkflowVersionControl:
    """Get the global workflow version control instance"""
    global _global_wvc
    if _global_wvc is None:
        _global_wvc = WorkflowVersionControl()
    return _global_wvc


if __name__ == "__main__":
    # Test the workflow version control system
    wvc = get_workflow_version_control()
    
    # Create a workflow
    workflow_data_v1 = {
        'name': 'Data Processing Workflow',
        'steps': [
            {'step': 1, 'action': 'load_data', 'params': {'source': 'database'}},
            {'step': 2, 'action': 'transform', 'params': {'method': 'normalize'}},
            {'step': 3, 'action': 'save', 'params': {'destination': 'cache'}}
        ],
        'config': {'timeout': 30, 'retry': 3}
    }
    
    workflow_id = wvc.create_workflow(
        workflow_name="Data Processing",
        workflow_type="data_pipeline",
        workflow_data=workflow_data_v1,
        description="Main data processing workflow",
        created_by="system",
        tags=['production', 'data']
    )
    
    print(f"Created workflow: {workflow_id}")
    
    # Get initial version
    history = wvc.get_version_history(workflow_id)
    version_1_id = history[0]['version_id']
    
    # Record performance metrics for v1
    wvc.record_performance_metric(version_1_id, 'execution_time_ms', 1250.5, 'milliseconds', sample_size=100)
    wvc.record_performance_metric(version_1_id, 'success_rate', 0.95, 'percentage', sample_size=100)
    
    # Create version 2 with improvements
    workflow_data_v2 = workflow_data_v1.copy()
    workflow_data_v2['config']['timeout'] = 60  # Increased timeout
    workflow_data_v2['steps'].append({'step': 4, 'action': 'validate', 'params': {}})
    
    version_2_id = wvc.create_version(
        workflow_id=workflow_id,
        workflow_data=workflow_data_v2,
        changes_summary="Increased timeout and added validation step",
        created_by="optimizer",
        tags=['production', 'data', 'validated']
    )
    
    # Record performance metrics for v2
    wvc.record_performance_metric(version_2_id, 'execution_time_ms', 1180.2, 'milliseconds', sample_size=100)
    wvc.record_performance_metric(version_2_id, 'success_rate', 0.98, 'percentage', sample_size=100)
    
    # Compare versions
    comparison = wvc.compare_performance(version_1_id, version_2_id)
    print(f"\nPerformance Comparison:")
    for metric, data in comparison['metrics'].items():
        print(f"  {metric}: {data['improvement_percent']:.2f}% improvement")
    
    # Deploy version 2
    deployment_id = wvc.deploy_version(workflow_id, version_2_id, 'production')
    print(f"\nDeployed version 2: {deployment_id}")
    
    print("\n✅ Workflow version control test complete!")
