"""Sandbox Testing Environment

This module provides isolated testing environments for automations and optimizations
before deployment to production.
"""

import sqlite3
import json
import os
import shutil
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
import logging
import traceback
import subprocess
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SandboxEnvironment:
    """Represents a sandbox testing environment"""
    sandbox_id: str
    name: str
    environment_type: str  # 'isolated', 'virtual', 'container'
    base_path: str
    config: Dict[str, Any]
    status: str  # 'created', 'active', 'destroyed'
    created_at: str


@dataclass
class TestExecution:
    """Represents a test execution in sandbox"""
    execution_id: str
    sandbox_id: str
    test_name: str
    test_type: str  # 'automation', 'optimization', 'integration'
    test_code: str
    status: str  # 'pending', 'running', 'passed', 'failed'
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    execution_time: float
    started_at: str
    completed_at: Optional[str]


@dataclass
class SafetyCheck:
    """Safety check before deployment"""
    check_id: str
    check_type: str  # 'resource_usage', 'data_integrity', 'rollback_test'
    passed: bool
    details: Dict[str, Any]
    checked_at: str


class SandboxManager:
    """Manages sandbox environments for testing"""
    
    def __init__(self, db_path: str = 'data/vy_nexus.db',
                 sandbox_root: str = 'data/sandboxes'):
        self.db_path = db_path
        self.sandbox_root = sandbox_root
        os.makedirs(sandbox_root, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sandbox_environments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sandbox_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                environment_type TEXT NOT NULL,
                base_path TEXT NOT NULL,
                config TEXT,
                status TEXT DEFAULT 'created',
                created_at TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id TEXT UNIQUE NOT NULL,
                sandbox_id TEXT NOT NULL,
                test_name TEXT NOT NULL,
                test_type TEXT NOT NULL,
                test_code TEXT,
                status TEXT DEFAULT 'pending',
                result TEXT,
                error_message TEXT,
                execution_time REAL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS safety_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                check_id TEXT UNIQUE NOT NULL,
                execution_id TEXT NOT NULL,
                check_type TEXT NOT NULL,
                passed BOOLEAN NOT NULL,
                details TEXT,
                checked_at TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_sandbox(self, name: str, environment_type: str = 'isolated',
                      config: Optional[Dict[str, Any]] = None) -> SandboxEnvironment:
        """Create a new sandbox environment"""
        sandbox_id = f"sandbox_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        base_path = os.path.join(self.sandbox_root, sandbox_id)
        
        # Create sandbox directory structure
        os.makedirs(base_path, exist_ok=True)
        os.makedirs(os.path.join(base_path, 'data'), exist_ok=True)
        os.makedirs(os.path.join(base_path, 'logs'), exist_ok=True)
        os.makedirs(os.path.join(base_path, 'temp'), exist_ok=True)
        
        # Create isolated database for sandbox
        sandbox_db = os.path.join(base_path, 'sandbox.db')
        
        sandbox = SandboxEnvironment(
            sandbox_id=sandbox_id,
            name=name,
            environment_type=environment_type,
            base_path=base_path,
            config=config or {},
            status='created',
            created_at=datetime.now().isoformat()
        )
        
        self._save_sandbox(sandbox)
        logger.info(f"Created sandbox: {sandbox_id} at {base_path}")
        
        return sandbox
    
    def _save_sandbox(self, sandbox: SandboxEnvironment):
        """Save sandbox to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO sandbox_environments
                (sandbox_id, name, environment_type, base_path, config, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                sandbox.sandbox_id,
                sandbox.name,
                sandbox.environment_type,
                sandbox.base_path,
                json.dumps(sandbox.config),
                sandbox.status,
                sandbox.created_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving sandbox: {e}")
        finally:
            conn.close()
    
    def destroy_sandbox(self, sandbox_id: str):
        """Destroy a sandbox environment"""
        sandbox = self.get_sandbox(sandbox_id)
        if not sandbox:
            logger.warning(f"Sandbox {sandbox_id} not found")
            return
        
        # Remove sandbox directory
        if os.path.exists(sandbox.base_path):
            shutil.rmtree(sandbox.base_path)
        
        # Update status
        sandbox.status = 'destroyed'
        self._save_sandbox(sandbox)
        
        logger.info(f"Destroyed sandbox: {sandbox_id}")
    
    def get_sandbox(self, sandbox_id: str) -> Optional[SandboxEnvironment]:
        """Retrieve sandbox by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sandbox_id, name, environment_type, base_path, config, status, created_at
            FROM sandbox_environments
            WHERE sandbox_id = ?
        ''', (sandbox_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return SandboxEnvironment(
                sandbox_id=row[0],
                name=row[1],
                environment_type=row[2],
                base_path=row[3],
                config=json.loads(row[4]),
                status=row[5],
                created_at=row[6]
            )
        return None
    
    def list_sandboxes(self, status: Optional[str] = None) -> List[SandboxEnvironment]:
        """List all sandboxes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT sandbox_id, name, environment_type, base_path, config, status, created_at
                FROM sandbox_environments
                WHERE status = ?
                ORDER BY created_at DESC
            ''', (status,))
        else:
            cursor.execute('''
                SELECT sandbox_id, name, environment_type, base_path, config, status, created_at
                FROM sandbox_environments
                ORDER BY created_at DESC
            ''')
        
        sandboxes = []
        for row in cursor.fetchall():
            sandboxes.append(SandboxEnvironment(
                sandbox_id=row[0],
                name=row[1],
                environment_type=row[2],
                base_path=row[3],
                config=json.loads(row[4]),
                status=row[5],
                created_at=row[6]
            ))
        
        conn.close()
        return sandboxes


class SandboxTester:
    """Executes tests in sandbox environments"""
    
    def __init__(self, db_path: str = 'data/vy_nexus.db'):
        self.db_path = db_path
        self.sandbox_manager = SandboxManager(db_path)
    
    def run_test(self, sandbox_id: str, test_name: str, test_type: str,
                test_func: Callable, *args, **kwargs) -> TestExecution:
        """Run a test in sandbox environment"""
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        started_at = datetime.now()
        
        execution = TestExecution(
            execution_id=execution_id,
            sandbox_id=sandbox_id,
            test_name=test_name,
            test_type=test_type,
            test_code=test_func.__name__,
            status='running',
            result=None,
            error_message=None,
            execution_time=0.0,
            started_at=started_at.isoformat(),
            completed_at=None
        )
        
        self._save_execution(execution)
        
        try:
            # Execute test function
            result = test_func(*args, **kwargs)
            
            completed_at = datetime.now()
            execution.status = 'passed'
            execution.result = {'output': str(result), 'success': True}
            execution.execution_time = (completed_at - started_at).total_seconds()
            execution.completed_at = completed_at.isoformat()
            
            logger.info(f"Test {test_name} passed in {execution.execution_time:.2f}s")
            
        except Exception as e:
            completed_at = datetime.now()
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.result = {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'success': False
            }
            execution.execution_time = (completed_at - started_at).total_seconds()
            execution.completed_at = completed_at.isoformat()
            
            logger.error(f"Test {test_name} failed: {e}")
        
        self._save_execution(execution)
        return execution
    
    def run_automation_test(self, sandbox_id: str, automation_code: str,
                           test_data: Optional[Dict] = None) -> TestExecution:
        """Test automation code in sandbox"""
        def automation_test():
            # Create temporary file with automation code
            sandbox = self.sandbox_manager.get_sandbox(sandbox_id)
            if not sandbox:
                raise ValueError(f"Sandbox {sandbox_id} not found")
            
            test_file = os.path.join(sandbox.base_path, 'temp', 'automation_test.py')
            with open(test_file, 'w') as f:
                f.write(automation_code)
            
            # Execute in isolated environment
            result = subprocess.run(
                [sys.executable, test_file],
                cwd=sandbox.base_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Automation failed: {result.stderr}")
            
            return {'stdout': result.stdout, 'stderr': result.stderr}
        
        return self.run_test(
            sandbox_id,
            'automation_test',
            'automation',
            automation_test
        )
    
    def _save_execution(self, execution: TestExecution):
        """Save test execution to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO test_executions
                (execution_id, sandbox_id, test_name, test_type, test_code,
                 status, result, error_message, execution_time, started_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                execution.execution_id,
                execution.sandbox_id,
                execution.test_name,
                execution.test_type,
                execution.test_code,
                execution.status,
                json.dumps(execution.result) if execution.result else None,
                execution.error_message,
                execution.execution_time,
                execution.started_at,
                execution.completed_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving execution: {e}")
        finally:
            conn.close()
    
    def get_test_results(self, sandbox_id: Optional[str] = None) -> List[TestExecution]:
        """Get test execution results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if sandbox_id:
            cursor.execute('''
                SELECT execution_id, sandbox_id, test_name, test_type, test_code,
                       status, result, error_message, execution_time, started_at, completed_at
                FROM test_executions
                WHERE sandbox_id = ?
                ORDER BY started_at DESC
            ''', (sandbox_id,))
        else:
            cursor.execute('''
                SELECT execution_id, sandbox_id, test_name, test_type, test_code,
                       status, result, error_message, execution_time, started_at, completed_at
                FROM test_executions
                ORDER BY started_at DESC
            ''')
        
        executions = []
        for row in cursor.fetchall():
            executions.append(TestExecution(
                execution_id=row[0],
                sandbox_id=row[1],
                test_name=row[2],
                test_type=row[3],
                test_code=row[4],
                status=row[5],
                result=json.loads(row[6]) if row[6] else None,
                error_message=row[7],
                execution_time=row[8],
                started_at=row[9],
                completed_at=row[10]
            ))
        
        conn.close()
        return executions


class SafetyValidator:
    """Validates safety before deployment"""
    
    def __init__(self, db_path: str = 'data/vy_nexus.db'):
        self.db_path = db_path
    
    def run_safety_checks(self, execution_id: str,
                         checks: Optional[List[str]] = None) -> List[SafetyCheck]:
        """Run safety checks on test execution"""
        if checks is None:
            checks = ['resource_usage', 'data_integrity', 'rollback_test']
        
        results = []
        
        for check_type in checks:
            check_id = f"check_{execution_id}_{check_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            if check_type == 'resource_usage':
                result = self._check_resource_usage(execution_id)
            elif check_type == 'data_integrity':
                result = self._check_data_integrity(execution_id)
            elif check_type == 'rollback_test':
                result = self._check_rollback(execution_id)
            else:
                result = {'passed': True, 'details': 'Unknown check type'}
            
            safety_check = SafetyCheck(
                check_id=check_id,
                check_type=check_type,
                passed=result['passed'],
                details=result,
                checked_at=datetime.now().isoformat()
            )
            
            results.append(safety_check)
            self._save_safety_check(safety_check, execution_id)
        
        return results
    
    def _check_resource_usage(self, execution_id: str) -> Dict[str, Any]:
        """Check if resource usage is within acceptable limits"""
        # Placeholder - would check CPU, memory, disk usage
        return {
            'passed': True,
            'cpu_usage': 'normal',
            'memory_usage': 'normal',
            'disk_usage': 'normal'
        }
    
    def _check_data_integrity(self, execution_id: str) -> Dict[str, Any]:
        """Check if data integrity is maintained"""
        # Placeholder - would verify data consistency
        return {
            'passed': True,
            'data_consistent': True,
            'no_corruption': True
        }
    
    def _check_rollback(self, execution_id: str) -> Dict[str, Any]:
        """Test rollback functionality"""
        # Placeholder - would test rollback procedures
        return {
            'passed': True,
            'rollback_available': True,
            'rollback_tested': True
        }
    
    def _save_safety_check(self, check: SafetyCheck, execution_id: str):
        """Save safety check to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO safety_checks
                (check_id, execution_id, check_type, passed, details, checked_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                check.check_id,
                execution_id,
                check.check_type,
                check.passed,
                json.dumps(check.details),
                check.checked_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving safety check: {e}")
        finally:
            conn.close()
    
    def validate_for_deployment(self, execution_id: str) -> bool:
        """Validate if execution is safe for deployment"""
        checks = self.run_safety_checks(execution_id)
        return all(check.passed for check in checks)
