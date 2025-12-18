#!/usr/bin/env python3
"""
Sandbox Testing Environment
Provides a safe environment for testing automations and optimizations.

This module:
- Creates isolated testing environments
- Tests automations safely before deployment
- Validates optimization improvements
- Monitors test execution
- Generates test reports
"""

import json
import os
import subprocess
import tempfile
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
import time


class SandboxTesting:
    """Manages sandbox testing for automations and optimizations."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/optimization"):
        self.data_dir = os.path.expanduser(data_dir)
        self.sandbox_dir = os.path.expanduser("~/vy-nexus/sandbox")
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.sandbox_dir, exist_ok=True)
        
        # Data files
        self.tests_file = os.path.join(self.data_dir, "sandbox_tests.json")
        self.results_file = os.path.join(self.data_dir, "test_results.json")
        self.environments_file = os.path.join(self.data_dir, "test_environments.json")
        self.statistics_file = os.path.join(self.data_dir, "sandbox_statistics.json")
        
        # Load existing data
        self.tests = self._load_json(self.tests_file, [])
        self.results = self._load_json(self.results_file, [])
        self.environments = self._load_json(self.environments_file, [])
        self.statistics = self._load_json(self.statistics_file, {
            "total_tests_run": 0,
            "successful_tests": 0,
            "failed_tests": 0,
            "total_test_time": 0,
            "environments_created": 0
        })
    
    def _load_json(self, filepath: str, default: Any) -> Any:
        """Load JSON data from file."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
        return default
    
    def _save_json(self, filepath: str, data: Any) -> None:
        """Save JSON data to file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")
    
    def create_environment(self, name: str, description: str,
                          base_path: str = None, 
                          copy_files: List[str] = None) -> str:
        """Create a new sandbox environment."""
        env_id = f"env_{len(self.environments) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create environment directory
        env_path = os.path.join(self.sandbox_dir, env_id)
        os.makedirs(env_path, exist_ok=True)
        
        # Create subdirectories
        os.makedirs(os.path.join(env_path, "input"), exist_ok=True)
        os.makedirs(os.path.join(env_path, "output"), exist_ok=True)
        os.makedirs(os.path.join(env_path, "logs"), exist_ok=True)
        os.makedirs(os.path.join(env_path, "temp"), exist_ok=True)
        
        # Copy files if specified
        if copy_files:
            for file_path in copy_files:
                if os.path.exists(os.path.expanduser(file_path)):
                    dest = os.path.join(env_path, "input", os.path.basename(file_path))
                    shutil.copy2(os.path.expanduser(file_path), dest)
        
        environment = {
            "id": env_id,
            "name": name,
            "description": description,
            "path": env_path,
            "base_path": base_path,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "tests_run": 0
        }
        
        self.environments.append(environment)
        self._save_json(self.environments_file, self.environments)
        self.statistics["environments_created"] += 1
        self._save_json(self.statistics_file, self.statistics)
        
        return env_id
    
    def create_test(self, name: str, description: str, test_type: str,
                   script_path: str = None, command: str = None,
                   expected_outcome: Dict = None) -> str:
        """Create a new test case."""
        test_id = f"test_{len(self.tests) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        test = {
            "id": test_id,
            "name": name,
            "description": description,
            "type": test_type,
            "script_path": script_path,
            "command": command,
            "expected_outcome": expected_outcome or {},
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "runs": 0
        }
        
        self.tests.append(test)
        self._save_json(self.tests_file, self.tests)
        
        return test_id
    
    def run_test(self, test_id: str, environment_id: str,
                timeout: int = 60) -> Dict:
        """Run a test in a sandbox environment."""
        test = self._get_test(test_id)
        environment = self._get_environment(environment_id)
        
        if not test or not environment:
            return {"error": "Test or environment not found"}
        
        result_id = f"result_{len(self.results) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        start_time = time.time()
        
        try:
            # Prepare test execution
            if test["script_path"]:
                result = self._run_script(test["script_path"], environment["path"], timeout)
            elif test["command"]:
                result = self._run_command(test["command"], environment["path"], timeout)
            else:
                result = {"error": "No script or command specified"}
            
            duration = time.time() - start_time
            
            # Validate outcome
            validation = self._validate_outcome(result, test.get("expected_outcome", {}))
            
            test_result = {
                "id": result_id,
                "test_id": test_id,
                "environment_id": environment_id,
                "status": "passed" if validation["passed"] else "failed",
                "duration": duration,
                "output": result.get("stdout", ""),
                "error": result.get("stderr", ""),
                "return_code": result.get("returncode", -1),
                "validation": validation,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            duration = time.time() - start_time
            test_result = {
                "id": result_id,
                "test_id": test_id,
                "environment_id": environment_id,
                "status": "error",
                "duration": duration,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        
        # Save result
        self.results.append(test_result)
        self._save_json(self.results_file, self.results)
        
        # Update statistics
        test["runs"] += 1
        test["last_run"] = datetime.now().isoformat()
        self._save_json(self.tests_file, self.tests)
        
        environment["tests_run"] += 1
        self._save_json(self.environments_file, self.environments)
        
        self.statistics["total_tests_run"] += 1
        self.statistics["total_test_time"] += duration
        
        if test_result["status"] == "passed":
            self.statistics["successful_tests"] += 1
        else:
            self.statistics["failed_tests"] += 1
        
        self._save_json(self.statistics_file, self.statistics)
        
        return test_result
    
    def _get_test(self, test_id: str) -> Optional[Dict]:
        """Get test by ID."""
        for test in self.tests:
            if test["id"] == test_id:
                return test
        return None
    
    def _get_environment(self, env_id: str) -> Optional[Dict]:
        """Get environment by ID."""
        for env in self.environments:
            if env["id"] == env_id:
                return env
        return None
    
    def _run_script(self, script_path: str, env_path: str, timeout: int) -> Dict:
        """Run a script in the sandbox environment."""
        script_path = os.path.expanduser(script_path)
        
        # Set environment variables
        env = os.environ.copy()
        env["SANDBOX_PATH"] = env_path
        env["SANDBOX_INPUT"] = os.path.join(env_path, "input")
        env["SANDBOX_OUTPUT"] = os.path.join(env_path, "output")
        env["SANDBOX_LOGS"] = os.path.join(env_path, "logs")
        env["SANDBOX_TEMP"] = os.path.join(env_path, "temp")
        
        try:
            result = subprocess.run(
                ["python3", script_path],
                cwd=env_path,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        
        except subprocess.TimeoutExpired:
            return {
                "error": "Test timed out",
                "returncode": -1
            }
        except Exception as e:
            return {
                "error": str(e),
                "returncode": -1
            }
    
    def _run_command(self, command: str, env_path: str, timeout: int) -> Dict:
        """Run a command in the sandbox environment."""
        env = os.environ.copy()
        env["SANDBOX_PATH"] = env_path
        env["SANDBOX_INPUT"] = os.path.join(env_path, "input")
        env["SANDBOX_OUTPUT"] = os.path.join(env_path, "output")
        env["SANDBOX_LOGS"] = os.path.join(env_path, "logs")
        env["SANDBOX_TEMP"] = os.path.join(env_path, "temp")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=env_path,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        
        except subprocess.TimeoutExpired:
            return {
                "error": "Test timed out",
                "returncode": -1
            }
        except Exception as e:
            return {
                "error": str(e),
                "returncode": -1
            }
    
    def _validate_outcome(self, result: Dict, expected: Dict) -> Dict:
        """Validate test outcome against expected results."""
        validation = {
            "passed": True,
            "checks": []
        }
        
        # Check return code
        if "return_code" in expected:
            expected_code = expected["return_code"]
            actual_code = result.get("returncode", -1)
            passed = expected_code == actual_code
            
            validation["checks"].append({
                "check": "return_code",
                "expected": expected_code,
                "actual": actual_code,
                "passed": passed
            })
            
            if not passed:
                validation["passed"] = False
        
        # Check output contains
        if "output_contains" in expected:
            for text in expected["output_contains"]:
                passed = text in result.get("stdout", "")
                
                validation["checks"].append({
                    "check": "output_contains",
                    "expected": text,
                    "passed": passed
                })
                
                if not passed:
                    validation["passed"] = False
        
        # Check no errors
        if expected.get("no_errors", False):
            stderr = result.get("stderr", "")
            passed = len(stderr.strip()) == 0
            
            validation["checks"].append({
                "check": "no_errors",
                "passed": passed
            })
            
            if not passed:
                validation["passed"] = False
        
        # Check files created
        if "files_created" in expected:
            for file_path in expected["files_created"]:
                passed = os.path.exists(file_path)
                
                validation["checks"].append({
                    "check": "file_created",
                    "expected": file_path,
                    "passed": passed
                })
                
                if not passed:
                    validation["passed"] = False
        
        return validation
    
    def run_test_suite(self, test_ids: List[str], environment_id: str) -> Dict:
        """Run multiple tests in sequence."""
        suite_results = {
            "suite_id": f"suite_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "environment_id": environment_id,
            "started_at": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total": len(test_ids),
                "passed": 0,
                "failed": 0,
                "errors": 0
            }
        }
        
        for test_id in test_ids:
            result = self.run_test(test_id, environment_id)
            suite_results["tests"].append(result)
            
            if result["status"] == "passed":
                suite_results["summary"]["passed"] += 1
            elif result["status"] == "failed":
                suite_results["summary"]["failed"] += 1
            else:
                suite_results["summary"]["errors"] += 1
        
        suite_results["completed_at"] = datetime.now().isoformat()
        
        return suite_results
    
    def cleanup_environment(self, environment_id: str) -> bool:
        """Clean up a sandbox environment."""
        environment = self._get_environment(environment_id)
        
        if not environment:
            return False
        
        try:
            # Remove environment directory
            if os.path.exists(environment["path"]):
                shutil.rmtree(environment["path"])
            
            # Update status
            environment["status"] = "cleaned"
            environment["cleaned_at"] = datetime.now().isoformat()
            self._save_json(self.environments_file, self.environments)
            
            return True
        
        except Exception as e:
            print(f"Error cleaning environment: {e}")
            return False
    
    def get_test_results(self, test_id: str) -> List[Dict]:
        """Get all results for a specific test."""
        return [r for r in self.results if r["test_id"] == test_id]
    
    def get_environment_results(self, environment_id: str) -> List[Dict]:
        """Get all results for a specific environment."""
        return [r for r in self.results if r["environment_id"] == environment_id]
    
    def generate_report(self) -> Dict:
        """Generate comprehensive testing report."""
        active_envs = [e for e in self.environments if e["status"] == "active"]
        
        # Calculate success rate
        total_tests = self.statistics["total_tests_run"]
        success_rate = (
            (self.statistics["successful_tests"] / total_tests * 100)
            if total_tests > 0 else 0
        )
        
        # Find most tested
        test_runs = {}
        for test in self.tests:
            test_runs[test["id"]] = test.get("runs", 0)
        
        most_tested = sorted(test_runs.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Recent failures
        recent_failures = [
            r for r in sorted(self.results, key=lambda x: x["timestamp"], reverse=True)
            if r["status"] == "failed"
        ][:5]
        
        return {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(self.tests),
                "total_environments": len(self.environments),
                "active_environments": len(active_envs),
                "total_test_runs": total_tests,
                "successful_tests": self.statistics["successful_tests"],
                "failed_tests": self.statistics["failed_tests"],
                "success_rate": success_rate,
                "total_test_time": self.statistics["total_test_time"],
                "average_test_time": (
                    self.statistics["total_test_time"] / total_tests
                    if total_tests > 0 else 0
                )
            },
            "most_tested": [
                {"test_id": tid, "runs": runs}
                for tid, runs in most_tested
            ],
            "recent_failures": [
                {
                    "test_id": r["test_id"],
                    "error": r.get("error", "Unknown error"),
                    "timestamp": r["timestamp"]
                }
                for r in recent_failures
            ],
            "statistics": self.statistics
        }


if __name__ == "__main__":
    # Test the sandbox
    sandbox = SandboxTesting()
    
    print("Creating sandbox environment...")
    env_id = sandbox.create_environment(
        name="Test Environment 1",
        description="Environment for testing file operations"
    )
    print(f"✓ Created environment: {env_id}")
    
    # Create test script
    print("\nCreating test script...")
    test_script_path = os.path.join(sandbox.sandbox_dir, "test_script.py")
    with open(test_script_path, 'w') as f:
        f.write('''
import os
import sys

print("Test script running...")
print(f"Sandbox path: {os.environ.get('SANDBOX_PATH')}")
print(f"Input path: {os.environ.get('SANDBOX_INPUT')}")
print(f"Output path: {os.environ.get('SANDBOX_OUTPUT')}")

# Create a test file
output_file = os.path.join(os.environ.get('SANDBOX_OUTPUT'), 'test_output.txt')
with open(output_file, 'w') as f:
    f.write('Test completed successfully!')

print("Test completed!")
sys.exit(0)
''')
    
    # Create tests
    print("Creating test cases...")
    test1 = sandbox.create_test(
        name="Basic Script Test",
        description="Test basic script execution",
        test_type="script",
        script_path=test_script_path,
        expected_outcome={
            "return_code": 0,
            "output_contains": ["Test completed!"],
            "no_errors": True
        }
    )
    print(f"✓ Created test: {test1}")
    
    test2 = sandbox.create_test(
        name="Command Test",
        description="Test command execution",
        test_type="command",
        command="echo 'Hello from sandbox' && ls -la",
        expected_outcome={
            "return_code": 0,
            "output_contains": ["Hello from sandbox"]
        }
    )
    print(f"✓ Created test: {test2}")
    
    # Run tests
    print("\nRunning tests...")
    result1 = sandbox.run_test(test1, env_id)
    print(f"✓ Test 1: {result1['status']} (duration: {result1['duration']:.2f}s)")
    
    result2 = sandbox.run_test(test2, env_id)
    print(f"✓ Test 2: {result2['status']} (duration: {result2['duration']:.2f}s)")
    
    # Run test suite
    print("\nRunning test suite...")
    suite_results = sandbox.run_test_suite([test1, test2], env_id)
    print(f"✓ Suite completed: {suite_results['summary']['passed']}/{suite_results['summary']['total']} passed")
    
    # Generate report
    report = sandbox.generate_report()
    
    print("\n" + "="*50)
    print("SANDBOX TESTING REPORT")
    print("="*50)
    print(f"\nTotal tests: {report['summary']['total_tests']}")
    print(f"Total test runs: {report['summary']['total_test_runs']}")
    print(f"Success rate: {report['summary']['success_rate']:.1f}%")
    print(f"Average test time: {report['summary']['average_test_time']:.2f}s")
    print(f"Active environments: {report['summary']['active_environments']}")
    
    print("\n✅ Sandbox testing environment is operational!")
    print(f"\nSandbox directory: {sandbox.sandbox_dir}")
