"""Automation Testing Sandbox

Provides isolated environment for testing automations before deployment.
"""

import asyncio
import logging
import subprocess
import tempfile
import os
import json
import signal
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)


@dataclass
class SandboxTest:
    """Represents a sandbox test execution."""
    test_id: str
    automation_id: str
    script: str
    language: str
    test_params: Dict[str, Any]
    started_at: datetime
    completed_at: Optional[datetime] = None
    success: bool = False
    output: str = ""
    error: str = ""
    duration_ms: float = 0.0
    exit_code: Optional[int] = None
    resource_usage: Dict[str, float] = field(default_factory=dict)


@dataclass
class SandboxEnvironment:
    """Represents an isolated sandbox environment."""
    env_id: str
    temp_dir: Path
    isolation_level: str  # 'full', 'partial', 'minimal'
    max_execution_time: int  # seconds
    max_memory_mb: int
    max_cpu_percent: float
    allowed_operations: List[str]
    created_at: datetime
    active: bool = True


class SandboxManager:
    """Manages sandbox environments for automation testing."""
    
    def __init__(self, 
                 isolation_level: str = 'full',
                 timeout_seconds: int = 30,
                 max_concurrent: int = 3):
        self.isolation_level = isolation_level
        self.timeout_seconds = timeout_seconds
        self.max_concurrent = max_concurrent
        self.active_tests: Dict[str, SandboxTest] = {}
        self.test_history: List[SandboxTest] = []
        self.environments: Dict[str, SandboxEnvironment] = {}
        self.max_history = 1000
        logger.info(f"SandboxManager initialized with {isolation_level} isolation")
    
    def create_environment(self) -> SandboxEnvironment:
        """Create a new sandbox environment."""
        env_id = f"sandbox_{int(datetime.now().timestamp() * 1000)}"
        temp_dir = Path(tempfile.mkdtemp(prefix=f"vy_sandbox_{env_id}_"))
        
        environment = SandboxEnvironment(
            env_id=env_id,
            temp_dir=temp_dir,
            isolation_level=self.isolation_level,
            max_execution_time=self.timeout_seconds,
            max_memory_mb=512,  # 512MB limit
            max_cpu_percent=50.0,  # 50% CPU limit
            allowed_operations=self._get_allowed_operations(),
            created_at=datetime.now()
        )
        
        self.environments[env_id] = environment
        logger.info(f"Created sandbox environment: {env_id} at {temp_dir}")
        return environment
    
    def _get_allowed_operations(self) -> List[str]:
        """Get allowed operations based on isolation level."""
        if self.isolation_level == 'minimal':
            return ['read', 'write', 'execute', 'network', 'system']
        elif self.isolation_level == 'partial':
            return ['read', 'write', 'execute']
        else:  # full isolation
            return ['read', 'write']
    
    def cleanup_environment(self, env_id: str) -> bool:
        """Clean up a sandbox environment."""
        if env_id not in self.environments:
            return False
        
        env = self.environments[env_id]
        try:
            # Remove temporary directory
            if env.temp_dir.exists():
                shutil.rmtree(env.temp_dir)
            
            env.active = False
            del self.environments[env_id]
            logger.info(f"Cleaned up sandbox environment: {env_id}")
            return True
        except Exception as e:
            logger.error(f"Error cleaning up environment {env_id}: {e}")
            return False
    
    async def run_test(self, 
                      automation_id: str,
                      script: str,
                      language: str,
                      test_params: Dict[str, Any]) -> SandboxTest:
        """Run an automation test in sandbox."""
        # Check concurrent limit
        while len(self.active_tests) >= self.max_concurrent:
            await asyncio.sleep(0.5)
        
        test_id = f"test_{automation_id}_{int(datetime.now().timestamp() * 1000)}"
        test = SandboxTest(
            test_id=test_id,
            automation_id=automation_id,
            script=script,
            language=language,
            test_params=test_params,
            started_at=datetime.now()
        )
        
        self.active_tests[test_id] = test
        
        try:
            # Create sandbox environment
            env = self.create_environment()
            
            # Execute test
            if language == 'python':
                await self._run_python_test(test, env)
            elif language == 'bash':
                await self._run_bash_test(test, env)
            elif language == 'applescript':
                await self._run_applescript_test(test, env)
            else:
                test.error = f"Unsupported language: {language}"
                test.success = False
            
            # Cleanup
            self.cleanup_environment(env.env_id)
            
        except Exception as e:
            test.error = str(e)
            test.success = False
            logger.error(f"Test {test_id} failed: {e}")
        
        finally:
            test.completed_at = datetime.now()
            test.duration_ms = (
                test.completed_at - test.started_at
            ).total_seconds() * 1000
            
            # Move to history
            del self.active_tests[test_id]
            self.test_history.append(test)
            
            # Maintain history limit
            if len(self.test_history) > self.max_history:
                self.test_history = self.test_history[-self.max_history:]
        
        return test
    
    async def _run_python_test(self, test: SandboxTest, env: SandboxEnvironment) -> None:
        """Run Python script in sandbox."""
        # Create script file
        script_file = env.temp_dir / "test_script.py"
        script_file.write_text(test.script)
        
        # Create params file
        params_file = env.temp_dir / "params.json"
        params_file.write_text(json.dumps(test.test_params))
        
        # Prepare execution wrapper
        wrapper_script = f'''
import sys
import json
import resource
import signal

# Set resource limits
resource.setrlimit(resource.RLIMIT_AS, ({env.max_memory_mb * 1024 * 1024}, {env.max_memory_mb * 1024 * 1024}))
resource.setrlimit(resource.RLIMIT_CPU, ({env.max_execution_time}, {env.max_execution_time}))

# Load parameters
with open('{params_file}', 'r') as f:
    params = json.load(f)

# Execute script
sys.path.insert(0, '{env.temp_dir}')
import test_script

if hasattr(test_script, 'execute'):
    result = test_script.execute(params)
    print(json.dumps(result))
else:
    print(json.dumps({{'error': 'No execute function found'}}))
'''
        
        wrapper_file = env.temp_dir / "wrapper.py"
        wrapper_file.write_text(wrapper_script)
        
        # Execute with timeout
        try:
            process = await asyncio.create_subprocess_exec(
                'python3', str(wrapper_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(env.temp_dir)
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout_seconds
                )
                
                test.output = stdout.decode('utf-8')
                test.error = stderr.decode('utf-8')
                test.exit_code = process.returncode
                test.success = process.returncode == 0
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                test.error = f"Test timed out after {self.timeout_seconds} seconds"
                test.success = False
                
        except Exception as e:
            test.error = f"Execution error: {str(e)}"
            test.success = False
    
    async def _run_bash_test(self, test: SandboxTest, env: SandboxEnvironment) -> None:
        """Run Bash script in sandbox."""
        script_file = env.temp_dir / "test_script.sh"
        script_file.write_text(test.script)
        script_file.chmod(0o755)
        
        # Create params as environment variables
        env_vars = os.environ.copy()
        for key, value in test.test_params.items():
            env_vars[f"PARAM_{key.upper()}"] = str(value)
        
        try:
            process = await asyncio.create_subprocess_exec(
                'bash', str(script_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(env.temp_dir),
                env=env_vars
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout_seconds
                )
                
                test.output = stdout.decode('utf-8')
                test.error = stderr.decode('utf-8')
                test.exit_code = process.returncode
                test.success = process.returncode == 0
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                test.error = f"Test timed out after {self.timeout_seconds} seconds"
                test.success = False
                
        except Exception as e:
            test.error = f"Execution error: {str(e)}"
            test.success = False
    
    async def _run_applescript_test(self, test: SandboxTest, env: SandboxEnvironment) -> None:
        """Run AppleScript in sandbox."""
        script_file = env.temp_dir / "test_script.scpt"
        script_file.write_text(test.script)
        
        try:
            process = await asyncio.create_subprocess_exec(
                'osascript', str(script_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(env.temp_dir)
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout_seconds
                )
                
                test.output = stdout.decode('utf-8')
                test.error = stderr.decode('utf-8')
                test.exit_code = process.returncode
                test.success = process.returncode == 0
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                test.error = f"Test timed out after {self.timeout_seconds} seconds"
                test.success = False
                
        except Exception as e:
            test.error = f"Execution error: {str(e)}"
            test.success = False
    
    def get_test_results(self, automation_id: str) -> List[SandboxTest]:
        """Get all test results for an automation."""
        return [
            test for test in self.test_history
            if test.automation_id == automation_id
        ]
    
    def get_success_rate(self, automation_id: str) -> float:
        """Calculate success rate for an automation."""
        tests = self.get_test_results(automation_id)
        if not tests:
            return 0.0
        
        successful = sum(1 for test in tests if test.success)
        return successful / len(tests)
    
    def get_test_statistics(self, automation_id: str) -> Dict[str, Any]:
        """Get comprehensive test statistics."""
        tests = self.get_test_results(automation_id)
        
        if not tests:
            return {
                'automation_id': automation_id,
                'total_tests': 0,
                'success_rate': 0.0
            }
        
        successful_tests = [t for t in tests if t.success]
        failed_tests = [t for t in tests if not t.success]
        
        return {
            'automation_id': automation_id,
            'total_tests': len(tests),
            'successful': len(successful_tests),
            'failed': len(failed_tests),
            'success_rate': len(successful_tests) / len(tests),
            'avg_duration_ms': sum(t.duration_ms for t in tests) / len(tests),
            'min_duration_ms': min(t.duration_ms for t in tests),
            'max_duration_ms': max(t.duration_ms for t in tests),
            'common_errors': self._get_common_errors(failed_tests),
            'last_test': tests[-1].started_at.isoformat() if tests else None
        }
    
    def _get_common_errors(self, failed_tests: List[SandboxTest]) -> List[Dict[str, Any]]:
        """Get most common errors from failed tests."""
        error_counts = {}
        for test in failed_tests:
            error = test.error[:100]  # First 100 chars
            error_counts[error] = error_counts.get(error, 0) + 1
        
        common = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return [{'error': err, 'count': count} for err, count in common]


class AutomationTester:
    """High-level automation testing interface."""
    
    def __init__(self, sandbox_manager: SandboxManager):
        self.sandbox_manager = sandbox_manager
        self.test_suites: Dict[str, List[Dict[str, Any]]] = {}
    
    def create_test_suite(self, automation_id: str, 
                         test_cases: List[Dict[str, Any]]) -> None:
        """Create a test suite for an automation."""
        self.test_suites[automation_id] = test_cases
        logger.info(f"Created test suite for {automation_id} with {len(test_cases)} cases")
    
    async def run_test_suite(self, automation_id: str, 
                           script: str, 
                           language: str) -> Dict[str, Any]:
        """Run all tests in a suite."""
        if automation_id not in self.test_suites:
            return {
                'automation_id': automation_id,
                'error': 'No test suite found'
            }
        
        test_cases = self.test_suites[automation_id]
        results = []
        
        for test_case in test_cases:
            test_result = await self.sandbox_manager.run_test(
                automation_id=automation_id,
                script=script,
                language=language,
                test_params=test_case.get('params', {})
            )
            results.append(test_result)
        
        # Calculate suite statistics
        successful = sum(1 for r in results if r.success)
        
        return {
            'automation_id': automation_id,
            'total_tests': len(results),
            'successful': successful,
            'failed': len(results) - successful,
            'success_rate': successful / len(results) if results else 0.0,
            'results': results,
            'passed': successful == len(results)
        }
    
    async def validate_automation(self, automation_id: str,
                                 script: str,
                                 language: str,
                                 min_success_rate: float = 0.9) -> bool:
        """Validate an automation is ready for deployment."""
        suite_result = await self.run_test_suite(automation_id, script, language)
        
        if 'error' in suite_result:
            return False
        
        return suite_result['success_rate'] >= min_success_rate
    
    def generate_default_tests(self, automation_type: str) -> List[Dict[str, Any]]:
        """Generate default test cases based on automation type."""
        if automation_type == 'file_operation':
            return [
                {'name': 'basic_copy', 'params': {'operation': 'copy', 'source': '/tmp/test.txt', 'destination': '/tmp/test_copy.txt'}},
                {'name': 'basic_move', 'params': {'operation': 'move', 'source': '/tmp/test.txt', 'destination': '/tmp/test_moved.txt'}},
                {'name': 'error_handling', 'params': {'operation': 'copy', 'source': '/nonexistent/file.txt', 'destination': '/tmp/out.txt'}}
            ]
        elif automation_type == 'data_processing':
            return [
                {'name': 'basic_processing', 'params': {'input_file': '/tmp/data.json', 'output_file': '/tmp/result.json', 'operation': 'transform'}},
                {'name': 'empty_data', 'params': {'input_file': '/tmp/empty.json', 'output_file': '/tmp/result.json', 'operation': 'transform'}}
            ]
        elif automation_type == 'api_call':
            return [
                {'name': 'get_request', 'params': {'url': 'https://api.example.com/data', 'method': 'GET'}},
                {'name': 'post_request', 'params': {'url': 'https://api.example.com/data', 'method': 'POST', 'data': {'key': 'value'}}}
            ]
        else:
            return [
                {'name': 'basic_test', 'params': {}}
            ]
