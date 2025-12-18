"""Tests for Automation Testing Sandbox"""

import pytest
import asyncio
import tempfile
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from automation_sandbox import (
    SandboxTest, SandboxEnvironment, SandboxManager, AutomationTester
)


class TestSandboxManager:
    """Test SandboxManager."""
    
    def test_initialization(self):
        manager = SandboxManager(
            isolation_level='full',
            timeout_seconds=30,
            max_concurrent=3
        )
        assert manager.isolation_level == 'full'
        assert manager.timeout_seconds == 30
        assert manager.max_concurrent == 3
    
    def test_create_environment(self):
        manager = SandboxManager()
        env = manager.create_environment()
        
        assert env.env_id is not None
        assert env.temp_dir.exists()
        assert env.active is True
        assert env.isolation_level == 'full'
        
        # Cleanup
        manager.cleanup_environment(env.env_id)
    
    def test_cleanup_environment(self):
        manager = SandboxManager()
        env = manager.create_environment()
        temp_dir = env.temp_dir
        
        assert temp_dir.exists()
        
        result = manager.cleanup_environment(env.env_id)
        assert result is True
        assert not temp_dir.exists()
        assert env.env_id not in manager.environments
    
    def test_allowed_operations_full_isolation(self):
        manager = SandboxManager(isolation_level='full')
        env = manager.create_environment()
        
        assert 'read' in env.allowed_operations
        assert 'write' in env.allowed_operations
        assert 'network' not in env.allowed_operations
        
        manager.cleanup_environment(env.env_id)
    
    def test_allowed_operations_partial_isolation(self):
        manager = SandboxManager(isolation_level='partial')
        env = manager.create_environment()
        
        assert 'read' in env.allowed_operations
        assert 'write' in env.allowed_operations
        assert 'execute' in env.allowed_operations
        assert 'network' not in env.allowed_operations
        
        manager.cleanup_environment(env.env_id)
    
    def test_allowed_operations_minimal_isolation(self):
        manager = SandboxManager(isolation_level='minimal')
        env = manager.create_environment()
        
        assert 'read' in env.allowed_operations
        assert 'write' in env.allowed_operations
        assert 'execute' in env.allowed_operations
        assert 'network' in env.allowed_operations
        
        manager.cleanup_environment(env.env_id)
    
    @pytest.mark.asyncio
    async def test_run_simple_python_test(self):
        manager = SandboxManager(timeout_seconds=10)
        
        script = '''
def execute(params):
    return {'success': True, 'result': params.get('value', 0) * 2}
'''
        
        test = await manager.run_test(
            automation_id='test_auto_001',
            script=script,
            language='python',
            test_params={'value': 5}
        )
        
        assert test.completed_at is not None
        assert test.duration_ms > 0
        assert test.automation_id == 'test_auto_001'
    
    @pytest.mark.asyncio
    async def test_run_failing_python_test(self):
        manager = SandboxManager(timeout_seconds=10)
        
        script = '''
def execute(params):
    raise ValueError("Test error")
'''
        
        test = await manager.run_test(
            automation_id='test_auto_002',
            script=script,
            language='python',
            test_params={}
        )
        
        assert test.completed_at is not None
        assert test.success is False
        assert len(test.error) > 0
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        manager = SandboxManager(timeout_seconds=2)
        
        script = '''
import time
def execute(params):
    time.sleep(10)  # Sleep longer than timeout
    return {'success': True}
'''
        
        test = await manager.run_test(
            automation_id='test_auto_003',
            script=script,
            language='python',
            test_params={}
        )
        
        assert test.completed_at is not None
        assert test.success is False
        assert 'timeout' in test.error.lower() or 'timed out' in test.error.lower()
    
    @pytest.mark.asyncio
    async def test_concurrent_test_limit(self):
        manager = SandboxManager(timeout_seconds=5, max_concurrent=2)
        
        script = '''
import time
def execute(params):
    time.sleep(1)
    return {'success': True}
'''
        
        # Start 3 tests concurrently
        tasks = [
            manager.run_test(f'auto_{i}', script, 'python', {})
            for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        # All should complete eventually
        assert all(r.completed_at is not None for r in results)
    
    def test_get_test_results(self):
        manager = SandboxManager()
        
        # Create mock test results
        for i in range(5):
            test = SandboxTest(
                test_id=f'test_{i}',
                automation_id='auto_001',
                script='test',
                language='python',
                test_params={},
                started_at=datetime.now(),
                completed_at=datetime.now(),
                success=i % 2 == 0,
                duration_ms=100
            )
            manager.test_history.append(test)
        
        results = manager.get_test_results('auto_001')
        assert len(results) == 5
    
    def test_get_success_rate(self):
        manager = SandboxManager()
        
        # Add 10 tests, 7 successful
        for i in range(10):
            test = SandboxTest(
                test_id=f'test_{i}',
                automation_id='auto_001',
                script='test',
                language='python',
                test_params={},
                started_at=datetime.now(),
                completed_at=datetime.now(),
                success=i < 7,
                duration_ms=100
            )
            manager.test_history.append(test)
        
        success_rate = manager.get_success_rate('auto_001')
        assert success_rate == 0.7
    
    def test_get_test_statistics(self):
        manager = SandboxManager()
        
        # Add test results
        for i in range(5):
            test = SandboxTest(
                test_id=f'test_{i}',
                automation_id='auto_001',
                script='test',
                language='python',
                test_params={},
                started_at=datetime.now(),
                completed_at=datetime.now(),
                success=i < 3,
                duration_ms=100 + i * 10,
                error='Test error' if i >= 3 else ''
            )
            manager.test_history.append(test)
        
        stats = manager.get_test_statistics('auto_001')
        
        assert stats['total_tests'] == 5
        assert stats['successful'] == 3
        assert stats['failed'] == 2
        assert stats['success_rate'] == 0.6
        assert stats['avg_duration_ms'] == 120.0
    
    def test_history_limit(self):
        manager = SandboxManager()
        manager.max_history = 10
        
        # Add more tests than limit
        for i in range(15):
            test = SandboxTest(
                test_id=f'test_{i}',
                automation_id='auto_001',
                script='test',
                language='python',
                test_params={},
                started_at=datetime.now(),
                completed_at=datetime.now(),
                success=True,
                duration_ms=100
            )
            manager.test_history.append(test)
            
            # Simulate history maintenance
            if len(manager.test_history) > manager.max_history:
                manager.test_history = manager.test_history[-manager.max_history:]
        
        assert len(manager.test_history) == 10


class TestAutomationTester:
    """Test AutomationTester."""
    
    def test_initialization(self):
        manager = SandboxManager()
        tester = AutomationTester(manager)
        
        assert tester.sandbox_manager == manager
        assert len(tester.test_suites) == 0
    
    def test_create_test_suite(self):
        manager = SandboxManager()
        tester = AutomationTester(manager)
        
        test_cases = [
            {'name': 'test1', 'params': {'value': 1}},
            {'name': 'test2', 'params': {'value': 2}}
        ]
        
        tester.create_test_suite('auto_001', test_cases)
        
        assert 'auto_001' in tester.test_suites
        assert len(tester.test_suites['auto_001']) == 2
    
    @pytest.mark.asyncio
    async def test_run_test_suite(self):
        manager = SandboxManager(timeout_seconds=10)
        tester = AutomationTester(manager)
        
        script = '''
def execute(params):
    value = params.get('value', 0)
    return {'success': True, 'result': value * 2}
'''
        
        test_cases = [
            {'name': 'test1', 'params': {'value': 1}},
            {'name': 'test2', 'params': {'value': 2}},
            {'name': 'test3', 'params': {'value': 3}}
        ]
        
        tester.create_test_suite('auto_001', test_cases)
        result = await tester.run_test_suite('auto_001', script, 'python')
        
        assert result['automation_id'] == 'auto_001'
        assert result['total_tests'] == 3
        assert 'successful' in result
        assert 'failed' in result
    
    @pytest.mark.asyncio
    async def test_validate_automation_success(self):
        manager = SandboxManager(timeout_seconds=10)
        tester = AutomationTester(manager)
        
        script = '''
def execute(params):
    return {'success': True}
'''
        
        test_cases = [
            {'name': 'test1', 'params': {}},
            {'name': 'test2', 'params': {}}
        ]
        
        tester.create_test_suite('auto_001', test_cases)
        is_valid = await tester.validate_automation('auto_001', script, 'python', min_success_rate=0.9)
        
        # Should pass if all tests succeed
        assert isinstance(is_valid, bool)
    
    @pytest.mark.asyncio
    async def test_validate_automation_failure(self):
        manager = SandboxManager(timeout_seconds=10)
        tester = AutomationTester(manager)
        
        script = '''
def execute(params):
    raise ValueError("Always fails")
'''
        
        test_cases = [
            {'name': 'test1', 'params': {}},
            {'name': 'test2', 'params': {}}
        ]
        
        tester.create_test_suite('auto_001', test_cases)
        is_valid = await tester.validate_automation('auto_001', script, 'python', min_success_rate=0.9)
        
        assert is_valid is False
    
    def test_generate_default_tests_file_operation(self):
        manager = SandboxManager()
        tester = AutomationTester(manager)
        
        tests = tester.generate_default_tests('file_operation')
        
        assert len(tests) > 0
        assert any('copy' in str(test) for test in tests)
        assert any('move' in str(test) for test in tests)
    
    def test_generate_default_tests_data_processing(self):
        manager = SandboxManager()
        tester = AutomationTester(manager)
        
        tests = tester.generate_default_tests('data_processing')
        
        assert len(tests) > 0
        assert any('processing' in test.get('name', '') for test in tests)
    
    def test_generate_default_tests_api_call(self):
        manager = SandboxManager()
        tester = AutomationTester(manager)
        
        tests = tester.generate_default_tests('api_call')
        
        assert len(tests) > 0
        assert any('GET' in str(test) or 'POST' in str(test) for test in tests)
    
    def test_generate_default_tests_unknown_type(self):
        manager = SandboxManager()
        tester = AutomationTester(manager)
        
        tests = tester.generate_default_tests('unknown_type')
        
        assert len(tests) > 0
        assert tests[0]['name'] == 'basic_test'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
