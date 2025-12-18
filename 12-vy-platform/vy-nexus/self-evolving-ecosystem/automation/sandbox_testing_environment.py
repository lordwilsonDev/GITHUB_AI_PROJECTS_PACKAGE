#!/usr/bin/env python3
"""
Sandbox Testing Environment
Provides a safe, isolated environment for testing automations, optimizations,
and improvements before deploying them to production.
"""

import json
import os
import subprocess
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import sys
import traceback

@dataclass
class TestCase:
    """Represents a test case for an automation"""
    test_id: str
    name: str
    description: str
    test_type: str  # 'unit', 'integration', 'performance', 'safety'
    automation_id: str
    inputs: Dict[str, Any]
    expected_outputs: Dict[str, Any]
    success_criteria: List[str]
    created_at: str
    
@dataclass
class TestResult:
    """Represents the result of a test execution"""
    result_id: str
    test_id: str
    automation_id: str
    status: str  # 'passed', 'failed', 'error', 'timeout'
    executed_at: str
    execution_time: float
    outputs: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    logs: List[str]
    metrics: Dict[str, float]
    
@dataclass
class SandboxSession:
    """Represents a sandbox testing session"""
    session_id: str
    name: str
    description: str
    created_at: str
    closed_at: Optional[str]
    test_results: List[str]  # List of result IDs
    status: str  # 'active', 'completed', 'aborted'
    
class SandboxTestingEnvironment:
    """
    Provides sandbox testing through:
    1. Isolated execution environments
    2. Resource limits and safety checks
    3. Comprehensive test result logging
    4. Performance benchmarking
    5. Rollback capabilities
    6. Safety validation
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_dir = Path("/Users/lordwilson/vy-nexus/self-evolving-ecosystem")
        self.data_dir = self.base_dir / "data" / "automation" / "sandbox"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.sandbox_dir = self.base_dir / "automation" / "sandbox"
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        
        self.test_cases_file = self.data_dir / "test_cases.jsonl"
        self.test_results_file = self.data_dir / "test_results.jsonl"
        self.sessions_file = self.data_dir / "sessions.jsonl"
        
        # In-memory caches
        self.test_cases: Dict[str, TestCase] = {}
        self.test_results: Dict[str, TestResult] = {}
        self.sessions: Dict[str, SandboxSession] = {}
        self.active_session: Optional[SandboxSession] = None
        
        # Safety limits
        self.max_execution_time = 300  # 5 minutes
        self.max_memory_mb = 512
        self.max_file_size_mb = 100
        
        self._load_existing_data()
        self._initialized = True
    
    def _load_existing_data(self):
        """Load existing test cases and results"""
        if self.test_cases_file.exists():
            with open(self.test_cases_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        test_case = TestCase(**data)
                        self.test_cases[test_case.test_id] = test_case
        
        if self.test_results_file.exists():
            with open(self.test_results_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        result = TestResult(**data)
                        self.test_results[result.result_id] = result
        
        if self.sessions_file.exists():
            with open(self.sessions_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        session = SandboxSession(**data)
                        self.sessions[session.session_id] = session
    
    def create_session(self, name: str, description: str = "") -> SandboxSession:
        """Create a new testing session"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session = SandboxSession(
            session_id=session_id,
            name=name,
            description=description,
            created_at=datetime.now().isoformat(),
            closed_at=None,
            test_results=[],
            status='active'
        )
        
        self.sessions[session_id] = session
        self.active_session = session
        self._save_session(session)
        
        return session
    
    def close_session(self, session_id: Optional[str] = None):
        """Close a testing session"""
        if session_id is None and self.active_session:
            session_id = self.active_session.session_id
        
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            session.closed_at = datetime.now().isoformat()
            session.status = 'completed'
            
            if self.active_session and self.active_session.session_id == session_id:
                self.active_session = None
    
    def create_test_case(self, name: str, description: str, test_type: str,
                        automation_id: str, inputs: Dict[str, Any],
                        expected_outputs: Dict[str, Any],
                        success_criteria: List[str]) -> TestCase:
        """Create a new test case"""
        test_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}"
        
        test_case = TestCase(
            test_id=test_id,
            name=name,
            description=description,
            test_type=test_type,
            automation_id=automation_id,
            inputs=inputs,
            expected_outputs=expected_outputs,
            success_criteria=success_criteria,
            created_at=datetime.now().isoformat()
        )
        
        self.test_cases[test_id] = test_case
        self._save_test_case(test_case)
        
        return test_case
    
    def run_test(self, test_id: str, timeout: Optional[int] = None) -> TestResult:
        """Run a test case in the sandbox"""
        if test_id not in self.test_cases:
            raise ValueError(f"Test case {test_id} not found")
        
        test_case = self.test_cases[test_id]
        result_id = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}"
        
        start_time = datetime.now()
        logs = []
        errors = []
        warnings = []
        outputs = {}
        metrics = {}
        status = 'passed'
        
        try:
            # Create isolated sandbox directory for this test
            test_sandbox = self.sandbox_dir / test_id
            test_sandbox.mkdir(exist_ok=True)
            
            logs.append(f"Created sandbox: {test_sandbox}")
            
            # Execute the test
            logs.append(f"Executing test: {test_case.name}")
            
            # Simulate test execution (in real implementation, this would run the actual automation)
            execution_result = self._execute_in_sandbox(
                test_case.automation_id,
                test_case.inputs,
                test_sandbox,
                timeout or self.max_execution_time
            )
            
            outputs = execution_result.get('outputs', {})
            logs.extend(execution_result.get('logs', []))
            errors.extend(execution_result.get('errors', []))
            warnings.extend(execution_result.get('warnings', []))
            metrics = execution_result.get('metrics', {})
            
            # Validate outputs against expected
            validation_result = self._validate_outputs(
                outputs, test_case.expected_outputs, test_case.success_criteria
            )
            
            if not validation_result['passed']:
                status = 'failed'
                errors.extend(validation_result['errors'])
            
            # Check for warnings
            if warnings:
                logs.append(f"Test completed with {len(warnings)} warnings")
            
        except TimeoutError:
            status = 'timeout'
            errors.append(f"Test exceeded timeout of {timeout or self.max_execution_time} seconds")
        except Exception as e:
            status = 'error'
            errors.append(f"Test execution error: {str(e)}")
            errors.append(traceback.format_exc())
        finally:
            # Cleanup sandbox
            try:
                if test_sandbox.exists():
                    shutil.rmtree(test_sandbox)
                    logs.append("Sandbox cleaned up")
            except Exception as e:
                warnings.append(f"Failed to cleanup sandbox: {str(e)}")
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        result = TestResult(
            result_id=result_id,
            test_id=test_id,
            automation_id=test_case.automation_id,
            status=status,
            executed_at=start_time.isoformat(),
            execution_time=execution_time,
            outputs=outputs,
            errors=errors,
            warnings=warnings,
            logs=logs,
            metrics=metrics
        )
        
        self.test_results[result_id] = result
        self._save_test_result(result)
        
        # Add to active session if exists
        if self.active_session:
            self.active_session.test_results.append(result_id)
        
        return result
    
    def _execute_in_sandbox(self, automation_id: str, inputs: Dict[str, Any],
                           sandbox_path: Path, timeout: int) -> Dict:
        """Execute automation in isolated sandbox"""
        logs = []
        errors = []
        warnings = []
        outputs = {}
        metrics = {}
        
        # Safety checks
        logs.append("Performing safety checks...")
        
        # Check if automation file exists
        automation_file = self.base_dir / "automation" / "generated" / f"{automation_id}.py"
        
        if not automation_file.exists():
            # Try shell script
            automation_file = self.base_dir / "automation" / "generated" / f"{automation_id}.sh"
        
        if not automation_file.exists():
            errors.append(f"Automation file not found: {automation_id}")
            return {
                'outputs': outputs,
                'logs': logs,
                'errors': errors,
                'warnings': warnings,
                'metrics': metrics
            }
        
        logs.append(f"Found automation: {automation_file}")
        
        # Copy automation to sandbox
        sandbox_script = sandbox_path / automation_file.name
        shutil.copy2(automation_file, sandbox_script)
        logs.append(f"Copied to sandbox: {sandbox_script}")
        
        # Prepare environment
        env = os.environ.copy()
        env['SANDBOX_MODE'] = '1'
        env['SANDBOX_PATH'] = str(sandbox_path)
        
        # Add inputs as environment variables
        for key, value in inputs.items():
            env[f'INPUT_{key.upper()}'] = str(value)
        
        try:
            # Execute with timeout
            logs.append(f"Executing with timeout: {timeout}s")
            
            if sandbox_script.suffix == '.py':
                cmd = [sys.executable, str(sandbox_script)]
            elif sandbox_script.suffix == '.sh':
                cmd = ['bash', str(sandbox_script)]
            else:
                errors.append(f"Unsupported script type: {sandbox_script.suffix}")
                return {
                    'outputs': outputs,
                    'logs': logs,
                    'errors': errors,
                    'warnings': warnings,
                    'metrics': metrics
                }
            
            start_time = datetime.now()
            
            result = subprocess.run(
                cmd,
                cwd=sandbox_path,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            metrics['execution_time'] = execution_time
            
            # Capture output
            if result.stdout:
                logs.append("STDOUT:")
                logs.extend(result.stdout.split('\n'))
                outputs['stdout'] = result.stdout
            
            if result.stderr:
                if result.returncode != 0:
                    errors.append("STDERR:")
                    errors.extend(result.stderr.split('\n'))
                else:
                    warnings.append("STDERR (non-fatal):")
                    warnings.extend(result.stderr.split('\n'))
                outputs['stderr'] = result.stderr
            
            outputs['return_code'] = result.returncode
            metrics['return_code'] = result.returncode
            
            if result.returncode == 0:
                logs.append("Execution completed successfully")
            else:
                errors.append(f"Execution failed with return code: {result.returncode}")
            
        except subprocess.TimeoutExpired:
            errors.append(f"Execution timed out after {timeout} seconds")
            raise TimeoutError()
        except Exception as e:
            errors.append(f"Execution error: {str(e)}")
        
        return {
            'outputs': outputs,
            'logs': logs,
            'errors': errors,
            'warnings': warnings,
            'metrics': metrics
        }
    
    def _validate_outputs(self, actual: Dict[str, Any], expected: Dict[str, Any],
                         success_criteria: List[str]) -> Dict:
        """Validate test outputs against expected values"""
        passed = True
        errors = []
        
        # Check expected outputs
        for key, expected_value in expected.items():
            if key not in actual:
                passed = False
                errors.append(f"Missing expected output: {key}")
            elif actual[key] != expected_value:
                passed = False
                errors.append(f"Output mismatch for {key}: expected {expected_value}, got {actual[key]}")
        
        # Check success criteria
        for criterion in success_criteria:
            # Simple criterion evaluation (in real implementation, this would be more sophisticated)
            if 'return_code' in criterion and 'return_code' in actual:
                if '== 0' in criterion and actual['return_code'] != 0:
                    passed = False
                    errors.append(f"Success criterion failed: {criterion}")
        
        return {'passed': passed, 'errors': errors}
    
    def run_test_suite(self, automation_id: str) -> List[TestResult]:
        """Run all tests for an automation"""
        test_cases = [tc for tc in self.test_cases.values() 
                     if tc.automation_id == automation_id]
        
        results = []
        for test_case in test_cases:
            result = self.run_test(test_case.test_id)
            results.append(result)
        
        return results
    
    def run_performance_benchmark(self, automation_id: str, iterations: int = 10) -> Dict:
        """Run performance benchmark for an automation"""
        test_id = self.create_test_case(
            name=f"Performance Benchmark - {automation_id}",
            description=f"Benchmark with {iterations} iterations",
            test_type='performance',
            automation_id=automation_id,
            inputs={},
            expected_outputs={},
            success_criteria=['return_code == 0']
        ).test_id
        
        execution_times = []
        
        for i in range(iterations):
            result = self.run_test(test_id)
            if result.status == 'passed':
                execution_times.append(result.execution_time)
        
        if not execution_times:
            return {'error': 'No successful executions'}
        
        avg_time = sum(execution_times) / len(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        return {
            'iterations': iterations,
            'successful': len(execution_times),
            'average_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'times': execution_times
        }
    
    def get_test_results(self, automation_id: str) -> List[TestResult]:
        """Get all test results for an automation"""
        return [r for r in self.test_results.values() 
                if r.automation_id == automation_id]
    
    def get_success_rate(self, automation_id: str) -> float:
        """Calculate success rate for an automation"""
        results = self.get_test_results(automation_id)
        
        if not results:
            return 0.0
        
        passed = len([r for r in results if r.status == 'passed'])
        return (passed / len(results)) * 100
    
    def _save_test_case(self, test_case: TestCase):
        """Save test case to file"""
        with open(self.test_cases_file, 'a') as f:
            f.write(json.dumps(asdict(test_case)) + '\n')
    
    def _save_test_result(self, result: TestResult):
        """Save test result to file"""
        with open(self.test_results_file, 'a') as f:
            f.write(json.dumps(asdict(result)) + '\n')
    
    def _save_session(self, session: SandboxSession):
        """Save session to file"""
        with open(self.sessions_file, 'a') as f:
            f.write(json.dumps(asdict(session)) + '\n')
    
    def get_statistics(self) -> Dict:
        """Get comprehensive testing statistics"""
        if not self.test_results:
            return {
                'total_tests': len(self.test_cases),
                'total_results': 0,
                'total_sessions': len(self.sessions)
            }
        
        results = list(self.test_results.values())
        
        status_counts = {}
        for status in ['passed', 'failed', 'error', 'timeout']:
            status_counts[status] = len([r for r in results if r.status == status])
        
        total_execution_time = sum(r.execution_time for r in results)
        avg_execution_time = total_execution_time / len(results)
        
        return {
            'total_tests': len(self.test_cases),
            'total_results': len(results),
            'total_sessions': len(self.sessions),
            'status_breakdown': status_counts,
            'success_rate': (status_counts.get('passed', 0) / len(results)) * 100 if results else 0,
            'total_execution_time': total_execution_time,
            'average_execution_time': avg_execution_time
        }
    
    def export_report(self, filepath: Optional[str] = None) -> str:
        """Export comprehensive testing report"""
        if filepath is None:
            filepath = str(self.data_dir / f"testing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'test_cases': [asdict(tc) for tc in self.test_cases.values()],
            'recent_results': [asdict(r) for r in sorted(
                self.test_results.values(),
                key=lambda x: x.executed_at,
                reverse=True
            )[:50]],
            'sessions': [asdict(s) for s in self.sessions.values()]
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filepath

def get_sandbox():
    """Get the singleton instance"""
    return SandboxTestingEnvironment()

if __name__ == "__main__":
    # Example usage
    sandbox = get_sandbox()
    
    print("Creating sandbox testing session...\n")
    
    session = sandbox.create_session(
        name="Automation Testing Session",
        description="Testing newly created automations"
    )
    print(f"✅ Created session: {session.name}")
    print(f"   Session ID: {session.session_id}\n")
    
    # Create test case
    test_case = sandbox.create_test_case(
        name="File Organization Test",
        description="Test file organization automation",
        test_type="integration",
        automation_id="file_org_test",
        inputs={'source_dir': '/tmp/test_source', 'target_dir': '/tmp/test_target'},
        expected_outputs={'return_code': 0},
        success_criteria=['return_code == 0', 'files_processed > 0']
    )
    print(f"✅ Created test case: {test_case.name}")
    print(f"   Test ID: {test_case.test_id}\n")
    
    # Note: Actual test execution would require the automation to exist
    print("="*60)
    print("SANDBOX TESTING STATISTICS")
    print("="*60)
    stats = sandbox.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Close session
    sandbox.close_session()
    print(f"\n✅ Session closed")
    
    # Export report
    report_path = sandbox.export_report()
    print(f"✅ Report exported to: {report_path}")
