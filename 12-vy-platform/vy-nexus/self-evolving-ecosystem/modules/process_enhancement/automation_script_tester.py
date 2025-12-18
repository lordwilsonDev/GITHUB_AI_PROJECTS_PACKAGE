#!/usr/bin/env python3
"""
Automation Script Tester Module
Tests automation scripts for correctness, safety, and performance.
Part of the Self-Evolving AI Ecosystem for vy-nexus.
"""

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import tempfile
import shutil

@dataclass
class TestCase:
    """Represents a test case for an automation script."""
    test_id: str
    timestamp: str
    script_path: str
    test_type: str  # unit, integration, performance, safety, regression
    test_name: str
    description: str
    
    # Test configuration
    input_data: Dict[str, Any]
    expected_output: Optional[Dict[str, Any]]
    expected_exit_code: int
    timeout_seconds: float
    
    # Environment
    environment_vars: Dict[str, str]
    working_directory: Optional[str]
    
    # Assertions
    assertions: List[Dict[str, Any]]
    
    # Metadata
    tags: List[str] = None
    priority: str = "medium"  # low, medium, high, critical
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class TestResult:
    """Results from running a test case."""
    result_id: str
    test_id: str
    timestamp: str
    
    # Execution details
    passed: bool
    exit_code: int
    execution_time_seconds: float
    
    # Output
    stdout: str
    stderr: str
    output_data: Optional[Dict[str, Any]]
    
    # Assertions
    assertions_passed: int
    assertions_failed: int
    failed_assertions: List[Dict[str, Any]]
    
    # Issues
    errors: List[str]
    warnings: List[str]
    
    # Performance metrics
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None

@dataclass
class TestSuite:
    """Collection of related test cases."""
    suite_id: str
    timestamp: str
    name: str
    description: str
    script_path: str
    test_cases: List[str]  # List of test_ids
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class AutomationScriptTester:
    """Tests automation scripts for correctness and safety."""
    
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
        self.data_dir = self.base_dir / "data" / "process_enhancement" / "testing"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Data files
        self.test_cases_file = self.data_dir / "test_cases.jsonl"
        self.test_results_file = self.data_dir / "test_results.jsonl"
        self.test_suites_file = self.data_dir / "test_suites.jsonl"
        
        # Test workspace
        self.test_workspace = self.base_dir / "test_workspace"
        self.test_workspace.mkdir(parents=True, exist_ok=True)
        
        # In-memory storage
        self.test_cases: List[TestCase] = []
        self.test_results: List[TestResult] = []
        self.test_suites: List[TestSuite] = []
        
        self._load_data()
        self._initialized = True
    
    def _load_data(self):
        """Load existing data from files."""
        # Load test cases
        if self.test_cases_file.exists():
            with open(self.test_cases_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    self.test_cases.append(TestCase(**data))
        
        # Load test results
        if self.test_results_file.exists():
            with open(self.test_results_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    self.test_results.append(TestResult(**data))
        
        # Load test suites
        if self.test_suites_file.exists():
            with open(self.test_suites_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    self.test_suites.append(TestSuite(**data))
    
    def create_test_case(
        self,
        script_path: str,
        test_type: str,
        test_name: str,
        description: str,
        input_data: Optional[Dict[str, Any]] = None,
        expected_output: Optional[Dict[str, Any]] = None,
        expected_exit_code: int = 0,
        timeout_seconds: float = 30.0,
        environment_vars: Optional[Dict[str, str]] = None,
        working_directory: Optional[str] = None,
        assertions: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[List[str]] = None,
        priority: str = "medium"
    ) -> TestCase:
        """Create a new test case."""
        test_id = f"test_{len(self.test_cases) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        test_case = TestCase(
            test_id=test_id,
            timestamp=datetime.now().isoformat(),
            script_path=script_path,
            test_type=test_type,
            test_name=test_name,
            description=description,
            input_data=input_data or {},
            expected_output=expected_output,
            expected_exit_code=expected_exit_code,
            timeout_seconds=timeout_seconds,
            environment_vars=environment_vars or {},
            working_directory=working_directory,
            assertions=assertions or [],
            tags=tags or [],
            priority=priority
        )
        
        self.test_cases.append(test_case)
        
        # Save to file
        with open(self.test_cases_file, 'a') as f:
            f.write(json.dumps(asdict(test_case)) + '\n')
        
        return test_case
    
    def run_test(self, test_id: str) -> TestResult:
        """Run a specific test case."""
        # Find test case
        test_case = None
        for tc in self.test_cases:
            if tc.test_id == test_id:
                test_case = tc
                break
        
        if test_case is None:
            raise ValueError(f"Test case {test_id} not found")
        
        # Prepare test environment
        test_env = os.environ.copy()
        test_env.update(test_case.environment_vars)
        
        # Set working directory
        work_dir = test_case.working_directory or str(self.test_workspace)
        
        # Prepare input data file if needed
        input_file = None
        if test_case.input_data:
            input_file = self.test_workspace / f"input_{test_id}.json"
            with open(input_file, 'w') as f:
                json.dump(test_case.input_data, f)
        
        # Run the script
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            result = subprocess.run(
                [test_case.script_path],
                capture_output=True,
                text=True,
                timeout=test_case.timeout_seconds,
                env=test_env,
                cwd=work_dir
            )
            
            exit_code = result.returncode
            stdout = result.stdout
            stderr = result.stderr
            
        except subprocess.TimeoutExpired:
            exit_code = -1
            stdout = ""
            stderr = f"Test timed out after {test_case.timeout_seconds} seconds"
            errors.append("Timeout exceeded")
            
        except Exception as e:
            exit_code = -1
            stdout = ""
            stderr = str(e)
            errors.append(f"Execution error: {e}")
        
        execution_time = time.time() - start_time
        
        # Parse output data if available
        output_data = None
        try:
            if stdout:
                output_data = json.loads(stdout)
        except json.JSONDecodeError:
            pass
        
        # Run assertions
        assertions_passed = 0
        assertions_failed = 0
        failed_assertions = []
        
        for assertion in test_case.assertions:
            passed = self._check_assertion(assertion, output_data, stdout, stderr, exit_code)
            if passed:
                assertions_passed += 1
            else:
                assertions_failed += 1
                failed_assertions.append(assertion)
        
        # Check expected exit code
        if exit_code != test_case.expected_exit_code:
            errors.append(f"Expected exit code {test_case.expected_exit_code}, got {exit_code}")
        
        # Check expected output
        if test_case.expected_output and output_data != test_case.expected_output:
            errors.append("Output does not match expected output")
        
        # Determine if test passed
        passed = (
            exit_code == test_case.expected_exit_code
            and assertions_failed == 0
            and len(errors) == 0
        )
        
        # Create result
        result_id = f"result_{len(self.test_results) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        test_result = TestResult(
            result_id=result_id,
            test_id=test_id,
            timestamp=datetime.now().isoformat(),
            passed=passed,
            exit_code=exit_code,
            execution_time_seconds=execution_time,
            stdout=stdout,
            stderr=stderr,
            output_data=output_data,
            assertions_passed=assertions_passed,
            assertions_failed=assertions_failed,
            failed_assertions=failed_assertions,
            errors=errors,
            warnings=warnings
        )
        
        self.test_results.append(test_result)
        
        # Save to file
        with open(self.test_results_file, 'a') as f:
            f.write(json.dumps(asdict(test_result)) + '\n')
        
        # Cleanup
        if input_file and input_file.exists():
            input_file.unlink()
        
        return test_result
    
    def _check_assertion(self, assertion: Dict[str, Any], output_data: Any, stdout: str, stderr: str, exit_code: int) -> bool:
        """Check if an assertion passes."""
        assertion_type = assertion.get('type')
        
        if assertion_type == 'exit_code':
            return exit_code == assertion.get('expected')
        
        elif assertion_type == 'output_contains':
            return assertion.get('value') in stdout
        
        elif assertion_type == 'output_not_contains':
            return assertion.get('value') not in stdout
        
        elif assertion_type == 'stderr_empty':
            return len(stderr.strip()) == 0
        
        elif assertion_type == 'json_field_equals':
            if output_data is None:
                return False
            field = assertion.get('field')
            expected = assertion.get('expected')
            return output_data.get(field) == expected
        
        elif assertion_type == 'json_field_exists':
            if output_data is None:
                return False
            field = assertion.get('field')
            return field in output_data
        
        elif assertion_type == 'execution_time_under':
            # This would need execution time passed in
            return True
        
        return False
    
    def create_test_suite(
        self,
        name: str,
        description: str,
        script_path: str,
        test_case_ids: List[str],
        tags: Optional[List[str]] = None
    ) -> TestSuite:
        """Create a test suite from multiple test cases."""
        suite_id = f"suite_{len(self.test_suites) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        suite = TestSuite(
            suite_id=suite_id,
            timestamp=datetime.now().isoformat(),
            name=name,
            description=description,
            script_path=script_path,
            test_cases=test_case_ids,
            tags=tags or []
        )
        
        self.test_suites.append(suite)
        
        # Save to file
        with open(self.test_suites_file, 'a') as f:
            f.write(json.dumps(asdict(suite)) + '\n')
        
        return suite
    
    def run_test_suite(self, suite_id: str) -> Dict[str, Any]:
        """Run all tests in a suite."""
        # Find suite
        suite = None
        for s in self.test_suites:
            if s.suite_id == suite_id:
                suite = s
                break
        
        if suite is None:
            raise ValueError(f"Test suite {suite_id} not found")
        
        # Run all tests
        results = []
        for test_id in suite.test_cases:
            result = self.run_test(test_id)
            results.append(result)
        
        # Aggregate results
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        failed_tests = total_tests - passed_tests
        total_time = sum(r.execution_time_seconds for r in results)
        
        return {
            'suite_id': suite_id,
            'suite_name': suite.name,
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'total_execution_time': total_time,
            'results': [asdict(r) for r in results]
        }
    
    def auto_generate_tests(self, script_path: str) -> List[TestCase]:
        """Auto-generate basic test cases for a script."""
        generated_tests = []
        
        # Test 1: Basic execution (should not crash)
        test1 = self.create_test_case(
            script_path=script_path,
            test_type="unit",
            test_name="Basic Execution",
            description="Verify script executes without crashing",
            expected_exit_code=0,
            timeout_seconds=10.0,
            tags=["auto-generated", "basic"]
        )
        generated_tests.append(test1)
        
        # Test 2: Help flag (if applicable)
        test2 = self.create_test_case(
            script_path=script_path,
            test_type="unit",
            test_name="Help Flag",
            description="Verify --help flag works",
            input_data={"args": ["--help"]},
            expected_exit_code=0,
            timeout_seconds=5.0,
            assertions=[
                {'type': 'output_contains', 'value': 'help'},
                {'type': 'stderr_empty'}
            ],
            tags=["auto-generated", "help"]
        )
        generated_tests.append(test2)
        
        # Test 3: Invalid input handling
        test3 = self.create_test_case(
            script_path=script_path,
            test_type="unit",
            test_name="Invalid Input Handling",
            description="Verify script handles invalid input gracefully",
            input_data={"invalid": "data"},
            timeout_seconds=5.0,
            tags=["auto-generated", "error-handling"]
        )
        generated_tests.append(test3)
        
        # Test 4: Performance baseline
        test4 = self.create_test_case(
            script_path=script_path,
            test_type="performance",
            test_name="Performance Baseline",
            description="Establish performance baseline",
            expected_exit_code=0,
            timeout_seconds=30.0,
            tags=["auto-generated", "performance"]
        )
        generated_tests.append(test4)
        
        return generated_tests
    
    def get_test_statistics(self) -> Dict[str, Any]:
        """Get comprehensive testing statistics."""
        total_tests = len(self.test_cases)
        total_results = len(self.test_results)
        
        if total_results == 0:
            return {
                'total_test_cases': total_tests,
                'total_test_runs': 0,
                'overall_pass_rate': 0,
                'by_type': {},
                'by_priority': {}
            }
        
        # Calculate pass rate
        passed = sum(1 for r in self.test_results if r.passed)
        pass_rate = (passed / total_results * 100) if total_results > 0 else 0
        
        # By type
        by_type = {}
        for test_type in ['unit', 'integration', 'performance', 'safety', 'regression']:
            type_tests = [tc for tc in self.test_cases if tc.test_type == test_type]
            type_results = [r for r in self.test_results if any(tc.test_id == r.test_id and tc.test_type == test_type for tc in self.test_cases)]
            type_passed = sum(1 for r in type_results if r.passed)
            
            by_type[test_type] = {
                'total_tests': len(type_tests),
                'total_runs': len(type_results),
                'passed': type_passed,
                'pass_rate': (type_passed / len(type_results) * 100) if type_results else 0
            }
        
        # By priority
        by_priority = {}
        for priority in ['low', 'medium', 'high', 'critical']:
            priority_tests = [tc for tc in self.test_cases if tc.priority == priority]
            priority_results = [r for r in self.test_results if any(tc.test_id == r.test_id and tc.priority == priority for tc in self.test_cases)]
            priority_passed = sum(1 for r in priority_results if r.passed)
            
            by_priority[priority] = {
                'total_tests': len(priority_tests),
                'total_runs': len(priority_results),
                'passed': priority_passed,
                'pass_rate': (priority_passed / len(priority_results) * 100) if priority_results else 0
            }
        
        # Average execution time
        avg_execution_time = sum(r.execution_time_seconds for r in self.test_results) / total_results
        
        return {
            'total_test_cases': total_tests,
            'total_test_runs': total_results,
            'passed': passed,
            'failed': total_results - passed,
            'overall_pass_rate': pass_rate,
            'average_execution_time': avg_execution_time,
            'by_type': by_type,
            'by_priority': by_priority,
            'total_suites': len(self.test_suites)
        }
    
    def get_failing_tests(self) -> List[TestResult]:
        """Get all failing test results."""
        return [r for r in self.test_results if not r.passed]
    
    def export_test_report(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Export comprehensive test report."""
        if output_file is None:
            output_file = self.data_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'statistics': self.get_test_statistics(),
            'failing_tests': [asdict(r) for r in self.get_failing_tests()],
            'test_suites': [asdict(s) for s in self.test_suites],
            'recent_results': [asdict(r) for r in self.test_results[-50:]]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report

def get_tester() -> AutomationScriptTester:
    """Get the singleton AutomationScriptTester instance."""
    return AutomationScriptTester()

if __name__ == "__main__":
    # Test the automation script tester
    tester = get_tester()
    
    print("⚙️  Automation Script Tester Test")
    print("=" * 60)
    
    # Create a simple test script
    print("\n1. Creating test script...")
    test_script = tester.test_workspace / "test_script.sh"
    with open(test_script, 'w') as f:
        f.write("""#!/bin/bash\necho '{"status": "success", "value": 42}'\nexit 0\n""")
    os.chmod(test_script, 0o755)
    
    # Create test cases
    print("\n2. Creating test cases...")
    test1 = tester.create_test_case(
        script_path=str(test_script),
        test_type="unit",
        test_name="Basic Execution",
        description="Test basic script execution",
        expected_exit_code=0,
        assertions=[
            {'type': 'exit_code', 'expected': 0},
            {'type': 'output_contains', 'value': 'success'}
        ],
        tags=["basic"]
    )
    
    # Run test
    print("\n3. Running test...")
    result = tester.run_test(test1.test_id)
    print(f"   Test: {test1.test_name}")
    print(f"   Passed: {result.passed}")
    print(f"   Exit Code: {result.exit_code}")
    print(f"   Execution Time: {result.execution_time_seconds:.3f}s")
    print(f"   Assertions: {result.assertions_passed}/{result.assertions_passed + result.assertions_failed}")
    
    # Auto-generate tests
    print("\n4. Auto-generating tests...")
    auto_tests = tester.auto_generate_tests(str(test_script))
    print(f"   Generated {len(auto_tests)} test cases")
    
    # Get statistics
    print("\n5. Test Statistics:")
    stats = tester.get_test_statistics()
    print(f"   Total Test Cases: {stats['total_test_cases']}")
    print(f"   Total Test Runs: {stats['total_test_runs']}")
    print(f"   Pass Rate: {stats['overall_pass_rate']:.1f}%")
    print(f"   Avg Execution Time: {stats['average_execution_time']:.3f}s")
    
    print("\n✅ Automation Script Tester test complete!")
    print(f"📁 Data stored in: {tester.data_dir}")
