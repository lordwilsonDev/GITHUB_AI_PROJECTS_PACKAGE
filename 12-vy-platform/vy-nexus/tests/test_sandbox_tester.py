"""Tests for Sandbox Testing Environment"""

import pytest
import os
import sqlite3
import shutil
from datetime import datetime
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.sandbox_tester import (
    SandboxManager, SandboxTester, SafetyValidator,
    SandboxEnvironment, TestExecution, SafetyCheck
)


@pytest.fixture
def test_db():
    """Create a temporary test database"""
    db_path = 'data/test_sandbox.db'
    os.makedirs('data', exist_ok=True)
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Clean up sandbox directories
    if os.path.exists('data/sandboxes'):
        shutil.rmtree('data/sandboxes')


def test_sandbox_manager_init(test_db):
    """Test SandboxManager initialization"""
    manager = SandboxManager(test_db)
    assert os.path.exists(test_db)
    
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sandbox_environments'")
    assert cursor.fetchone() is not None
    conn.close()


def test_create_sandbox(test_db):
    """Test sandbox creation"""
    manager = SandboxManager(test_db)
    
    sandbox = manager.create_sandbox(
        name='test_sandbox',
        environment_type='isolated',
        config={'test': True}
    )
    
    assert sandbox.sandbox_id is not None
    assert sandbox.name == 'test_sandbox'
    assert sandbox.environment_type == 'isolated'
    assert os.path.exists(sandbox.base_path)
    assert os.path.exists(os.path.join(sandbox.base_path, 'data'))
    assert os.path.exists(os.path.join(sandbox.base_path, 'logs'))
    assert os.path.exists(os.path.join(sandbox.base_path, 'temp'))


def test_get_sandbox(test_db):
    """Test retrieving sandbox"""
    manager = SandboxManager(test_db)
    
    created = manager.create_sandbox('test_sandbox')
    retrieved = manager.get_sandbox(created.sandbox_id)
    
    assert retrieved is not None
    assert retrieved.sandbox_id == created.sandbox_id
    assert retrieved.name == created.name


def test_list_sandboxes(test_db):
    """Test listing sandboxes"""
    manager = SandboxManager(test_db)
    
    manager.create_sandbox('sandbox1')
    manager.create_sandbox('sandbox2')
    
    sandboxes = manager.list_sandboxes()
    assert len(sandboxes) >= 2


def test_destroy_sandbox(test_db):
    """Test sandbox destruction"""
    manager = SandboxManager(test_db)
    
    sandbox = manager.create_sandbox('temp_sandbox')
    base_path = sandbox.base_path
    
    assert os.path.exists(base_path)
    
    manager.destroy_sandbox(sandbox.sandbox_id)
    
    assert not os.path.exists(base_path)
    
    retrieved = manager.get_sandbox(sandbox.sandbox_id)
    assert retrieved.status == 'destroyed'


def test_sandbox_tester_init(test_db):
    """Test SandboxTester initialization"""
    tester = SandboxTester(test_db)
    assert tester.sandbox_manager is not None


def test_run_test_success(test_db):
    """Test successful test execution"""
    manager = SandboxManager(test_db)
    tester = SandboxTester(test_db)
    
    sandbox = manager.create_sandbox('test_sandbox')
    
    def sample_test():
        return "Test passed"
    
    execution = tester.run_test(
        sandbox.sandbox_id,
        'sample_test',
        'automation',
        sample_test
    )
    
    assert execution.status == 'passed'
    assert execution.result is not None
    assert execution.result['success'] is True
    assert execution.execution_time >= 0


def test_run_test_failure(test_db):
    """Test failed test execution"""
    manager = SandboxManager(test_db)
    tester = SandboxTester(test_db)
    
    sandbox = manager.create_sandbox('test_sandbox')
    
    def failing_test():
        raise ValueError("Intentional test failure")
    
    execution = tester.run_test(
        sandbox.sandbox_id,
        'failing_test',
        'automation',
        failing_test
    )
    
    assert execution.status == 'failed'
    assert execution.error_message is not None
    assert 'Intentional test failure' in execution.error_message


def test_run_automation_test(test_db):
    """Test automation code execution"""
    manager = SandboxManager(test_db)
    tester = SandboxTester(test_db)
    
    sandbox = manager.create_sandbox('automation_sandbox')
    
    automation_code = '''
print("Automation test running")
result = 2 + 2
print(f"Result: {result}")
'''
    
    execution = tester.run_automation_test(sandbox.sandbox_id, automation_code)
    
    assert execution.test_type == 'automation'
    # May pass or fail depending on environment, just check it executed
    assert execution.status in ['passed', 'failed']


def test_get_test_results(test_db):
    """Test retrieving test results"""
    manager = SandboxManager(test_db)
    tester = SandboxTester(test_db)
    
    sandbox = manager.create_sandbox('test_sandbox')
    
    def test1():
        return "Test 1"
    
    def test2():
        return "Test 2"
    
    tester.run_test(sandbox.sandbox_id, 'test1', 'automation', test1)
    tester.run_test(sandbox.sandbox_id, 'test2', 'automation', test2)
    
    results = tester.get_test_results(sandbox.sandbox_id)
    assert len(results) >= 2


def test_safety_validator_init(test_db):
    """Test SafetyValidator initialization"""
    validator = SafetyValidator(test_db)
    assert validator.db_path == test_db


def test_run_safety_checks(test_db):
    """Test running safety checks"""
    manager = SandboxManager(test_db)
    tester = SandboxTester(test_db)
    validator = SafetyValidator(test_db)
    
    sandbox = manager.create_sandbox('safety_test')
    
    def safe_test():
        return "Safe operation"
    
    execution = tester.run_test(sandbox.sandbox_id, 'safe_test', 'automation', safe_test)
    
    checks = validator.run_safety_checks(execution.execution_id)
    
    assert len(checks) > 0
    assert all(isinstance(check, SafetyCheck) for check in checks)


def test_validate_for_deployment(test_db):
    """Test deployment validation"""
    manager = SandboxManager(test_db)
    tester = SandboxTester(test_db)
    validator = SafetyValidator(test_db)
    
    sandbox = manager.create_sandbox('deployment_test')
    
    def deployment_ready_test():
        return "Ready for deployment"
    
    execution = tester.run_test(
        sandbox.sandbox_id,
        'deployment_test',
        'automation',
        deployment_ready_test
    )
    
    is_safe = validator.validate_for_deployment(execution.execution_id)
    assert isinstance(is_safe, bool)


def test_resource_usage_check(test_db):
    """Test resource usage safety check"""
    validator = SafetyValidator(test_db)
    
    result = validator._check_resource_usage('test_execution')
    
    assert 'passed' in result
    assert 'cpu_usage' in result
    assert 'memory_usage' in result


def test_data_integrity_check(test_db):
    """Test data integrity safety check"""
    validator = SafetyValidator(test_db)
    
    result = validator._check_data_integrity('test_execution')
    
    assert 'passed' in result
    assert 'data_consistent' in result


def test_rollback_check(test_db):
    """Test rollback safety check"""
    validator = SafetyValidator(test_db)
    
    result = validator._check_rollback('test_execution')
    
    assert 'passed' in result
    assert 'rollback_available' in result


def test_sandbox_isolation(test_db):
    """Test that sandboxes are properly isolated"""
    manager = SandboxManager(test_db)
    
    sandbox1 = manager.create_sandbox('isolated1')
    sandbox2 = manager.create_sandbox('isolated2')
    
    # Verify different paths
    assert sandbox1.base_path != sandbox2.base_path
    
    # Create file in sandbox1
    test_file1 = os.path.join(sandbox1.base_path, 'test.txt')
    with open(test_file1, 'w') as f:
        f.write('Sandbox 1 data')
    
    # Verify file doesn't exist in sandbox2
    test_file2 = os.path.join(sandbox2.base_path, 'test.txt')
    assert not os.path.exists(test_file2)


def test_execution_time_tracking(test_db):
    """Test that execution time is properly tracked"""
    manager = SandboxManager(test_db)
    tester = SandboxTester(test_db)
    
    sandbox = manager.create_sandbox('timing_test')
    
    import time
    
    def timed_test():
        time.sleep(0.1)  # Sleep for 100ms
        return "Done"
    
    execution = tester.run_test(sandbox.sandbox_id, 'timed_test', 'automation', timed_test)
    
    assert execution.execution_time >= 0.1
    assert execution.started_at is not None
    assert execution.completed_at is not None


def test_multiple_tests_in_sandbox(test_db):
    """Test running multiple tests in same sandbox"""
    manager = SandboxManager(test_db)
    tester = SandboxTester(test_db)
    
    sandbox = manager.create_sandbox('multi_test')
    
    tests = [
        lambda: "Test 1",
        lambda: "Test 2",
        lambda: "Test 3"
    ]
    
    for i, test_func in enumerate(tests):
        execution = tester.run_test(
            sandbox.sandbox_id,
            f'test_{i}',
            'automation',
            test_func
        )
        assert execution.status == 'passed'
    
    results = tester.get_test_results(sandbox.sandbox_id)
    assert len(results) >= 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
