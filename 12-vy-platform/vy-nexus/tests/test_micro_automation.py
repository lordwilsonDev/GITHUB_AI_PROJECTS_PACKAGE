#!/usr/bin/env python3
"""
Tests for Micro-Automation Framework
"""

import pytest
import sqlite3
import json
import os
import tempfile
from datetime import datetime
import sys
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.micro_automation import (
    MicroAutomation,
    MicroAutomationFramework,
    AutomationStatus,
    AutomationType
)


@pytest.fixture
def output():
    return {'status': 'success'}


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def automation_framework(temp_db):
    """Create an automation framework instance"""
    return MicroAutomationFramework(temp_db)


# Test automation functions (helper functions, not actual tests)
def success_func(**kwargs):
    """Test function that always succeeds"""
    return {"status": "success", "data": kwargs.get("data", "test")}


def failure_func(**kwargs):
    """Test function that always fails"""
    raise ValueError("Intentional test failure")


def retry_func(**kwargs):
    """Test function that fails first time, succeeds second time"""
    if not hasattr(retry_func, 'call_count'):
        retry_func.call_count = 0
    retry_func.call_count += 1
    
    if retry_func.call_count == 1:
        raise ValueError("First attempt fails")
    return {"status": "success", "attempt": retry_func.call_count}


def validation_func(output):
    """Test validation function"""
    return output.get("status") == "success"


def rollback_func(**kwargs):
    """Test rollback function"""
    # Just mark that rollback was called
    if not hasattr(rollback_func, 'called'):
        rollback_func.called = False
    rollback_func.called = True


class TestMicroAutomation:
    """Test suite for MicroAutomation"""
    
    def test_initialization(self):
        """Test automation initialization"""
        automation = MicroAutomation(
            automation_id="test_001",
            name="Test Automation",
            description="Test description",
            automation_type=AutomationType.SCRIPT,
            execute_func=success_func
        )
        
        assert automation.automation_id == "test_001"
        assert automation.name == "Test Automation"
        assert automation.status == AutomationStatus.PENDING
        assert automation.retry_count == 0
    
    def test_successful_execution(self):
        """Test successful automation execution"""
        automation = MicroAutomation(
            automation_id="test_002",
            name="Success Test",
            description="Should succeed",
            automation_type=AutomationType.SCRIPT,
            execute_func=success_func
        )
        
        result = automation.execute(data="test_data")
        
        assert result["status"] == "success"
        assert result["output"]["data"] == "test_data"
        assert automation.status == AutomationStatus.COMPLETED
        assert result["retry_count"] == 0
    
    def test_failed_execution(self):
        """Test failed automation execution"""
        automation = MicroAutomation(
            automation_id="test_003",
            name="Failure Test",
            description="Should fail",
            automation_type=AutomationType.SCRIPT,
            execute_func=failure_func,
            max_retries=2
        )
        
        result = automation.execute()
        
        assert result["status"] == "failed"
        assert automation.status == AutomationStatus.FAILED
        assert result["retry_count"] == 3  # Initial + 2 retries = 3 total attempts
        assert result["error"] is not None
    
    def test_retry_logic(self):
        """Test retry logic on failure"""
        # Reset call count
        if hasattr(retry_func, 'call_count'):
            retry_func.call_count = 0
        
        automation = MicroAutomation(
            automation_id="test_004",
            name="Retry Test",
            description="Should succeed on retry",
            automation_type=AutomationType.SCRIPT,
            execute_func=retry_func,
            max_retries=3,
            retry_delay=0.1
        )
        
        result = automation.execute()
        
        assert result["status"] == "success"
        assert result["retry_count"] == 1  # Failed once, succeeded on retry
        assert automation.status == AutomationStatus.COMPLETED
    
    def test_validation(self):
        """Test output validation"""
        automation = MicroAutomation(
            automation_id="test_005",
            name="Validation Test",
            description="Test with validation",
            automation_type=AutomationType.SCRIPT,
            execute_func=success_func,
            validation_func=validation_func
        )
        
        result = automation.execute()
        
        assert result["status"] == "success"
        assert automation.status == AutomationStatus.COMPLETED
    
    def test_rollback(self):
        """Test rollback on failure"""
        # Reset rollback flag
        if hasattr(rollback_func, 'called'):
            rollback_func.called = False
        
        automation = MicroAutomation(
            automation_id="test_006",
            name="Rollback Test",
            description="Test rollback",
            automation_type=AutomationType.SCRIPT,
            execute_func=failure_func,
            max_retries=1,
            rollback_func=rollback_func
        )
        
        result = automation.execute()
        
        assert result["status"] == "failed"
        assert result["rollback"] == "success"
        assert rollback_func.called == True
    
    def test_execution_history(self):
        """Test that execution history is recorded"""
        automation = MicroAutomation(
            automation_id="test_007",
            name="History Test",
            description="Test history",
            automation_type=AutomationType.SCRIPT,
            execute_func=success_func
        )
        
        # Execute multiple times
        automation.execute()
        automation.execute()
        
        assert len(automation.execution_history) == 2
        assert all(h["status"] == "success" for h in automation.execution_history)


class TestMicroAutomationFramework:
    """Test suite for MicroAutomationFramework"""
    
    def test_initialization(self, automation_framework):
        """Test framework initialization"""
        assert automation_framework.db_path is not None
        
        # Check tables exist
        conn = sqlite3.connect(automation_framework.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('automation_definitions', 'automation_executions', 'automation_schedules', 'automation_dependencies')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert 'automation_definitions' in tables
        assert 'automation_executions' in tables
        assert 'automation_schedules' in tables
        assert 'automation_dependencies' in tables
    
    def test_register_automation(self, automation_framework):
        """Test registering an automation"""
        automation = automation_framework.register_automation(
            automation_id="reg_test_001",
            name="Registration Test",
            description="Test registration",
            automation_type=AutomationType.SCRIPT,
            execute_func=success_func
        )
        
        assert automation.automation_id == "reg_test_001"
        assert "reg_test_001" in automation_framework.automations
        
        # Verify in database
        all_automations = automation_framework.get_all_automations()
        assert len(all_automations) == 1
        assert all_automations[0]["automation_id"] == "reg_test_001"
    
    def test_execute_automation(self, automation_framework):
        """Test executing a registered automation"""
        automation_framework.register_automation(
            automation_id="exec_test_001",
            name="Execution Test",
            description="Test execution",
            automation_type=AutomationType.SCRIPT,
            execute_func=success_func
        )
        
        result = automation_framework.execute_automation("exec_test_001", data="test")
        
        assert result["status"] == "success"
        assert result["output"]["data"] == "test"
    
    def test_execute_nonexistent_automation(self, automation_framework):
        """Test executing non-existent automation"""
        result = automation_framework.execute_automation("nonexistent")
        
        assert result["status"] == "error"
        assert "not found" in result["error"]
    
    def test_execution_recorded(self, automation_framework):
        """Test that executions are recorded in database"""
        automation_framework.register_automation(
            automation_id="record_test_001",
            name="Record Test",
            description="Test recording",
            automation_type=AutomationType.SCRIPT,
            execute_func=success_func
        )
        
        automation_framework.execute_automation("record_test_001")
        
        # Check execution history
        history = automation_framework.get_execution_history("record_test_001")
        assert len(history) == 1
        assert history[0]["automation_id"] == "record_test_001"
        assert history[0]["status"] == "success"
    
    def test_execute_workflow(self, automation_framework):
        """Test executing a workflow of automations"""
        # Register multiple automations
        automation_framework.register_automation(
            automation_id="workflow_001",
            name="Workflow Step 1",
            description="First step",
            automation_type=AutomationType.WORKFLOW,
            execute_func=success_func
        )
        
        automation_framework.register_automation(
            automation_id="workflow_002",
            name="Workflow Step 2",
            description="Second step",
            automation_type=AutomationType.WORKFLOW,
            execute_func=success_func
        )
        
        # Execute workflow
        results = automation_framework.execute_workflow(["workflow_001", "workflow_002"])
        
        assert len(results) == 2
        assert all(r["status"] == "success" for r in results)
    
    def test_workflow_stops_on_failure(self, automation_framework):
        """Test that workflow stops when an automation fails"""
        automation_framework.register_automation(
            automation_id="workflow_fail_001",
            name="Failing Step",
            description="Will fail",
            automation_type=AutomationType.WORKFLOW,
            execute_func=failure_func,
            max_retries=1
        )
        
        automation_framework.register_automation(
            automation_id="workflow_success_001",
            name="Success Step",
            description="Should not execute",
            automation_type=AutomationType.WORKFLOW,
            execute_func=success_func
        )
        
        results = automation_framework.execute_workflow(
            ["workflow_fail_001", "workflow_success_001"]
        )
        
        # Should only have one result (the failed one)
        assert len(results) == 1
        assert results[0]["status"] == "failed"
    
    def test_add_dependency(self, automation_framework):
        """Test adding dependencies between automations"""
        automation_framework.register_automation(
            automation_id="dep_001",
            name="Dependent",
            description="Depends on another",
            automation_type=AutomationType.SCRIPT,
            execute_func=success_func
        )
        
        automation_framework.register_automation(
            automation_id="dep_002",
            name="Dependency",
            description="Required first",
            automation_type=AutomationType.SCRIPT,
            execute_func=success_func
        )
        
        automation_framework.add_dependency("dep_001", "dep_002", "sequential")
        
        # Verify dependency was added
        conn = sqlite3.connect(automation_framework.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM automation_dependencies
            WHERE automation_id = 'dep_001' AND depends_on_automation_id = 'dep_002'
        """)
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 1
    
    def test_get_automation_stats(self, automation_framework):
        """Test getting automation statistics"""
        automation_framework.register_automation(
            automation_id="stats_test_001",
            name="Stats Test",
            description="Test stats",
            automation_type=AutomationType.SCRIPT,
            execute_func=success_func
        )
        
        # Execute multiple times
        for i in range(5):
            automation_framework.execute_automation("stats_test_001")
        
        stats = automation_framework.get_automation_stats("stats_test_001", days=1)
        
        assert stats["automation_id"] == "stats_test_001"
        assert stats["total_executions"] == 5
        assert stats["successful_executions"] == 5
        assert stats["success_rate"] == 1.0
    
    def test_disable_enable_automation(self, automation_framework):
        """Test disabling and enabling automations"""
        automation_framework.register_automation(
            automation_id="toggle_test_001",
            name="Toggle Test",
            description="Test enable/disable",
            automation_type=AutomationType.SCRIPT,
            execute_func=success_func
        )
        
        # Disable
        automation_framework.disable_automation("toggle_test_001")
        
        # Check status
        automations = automation_framework.get_all_automations()
        assert automations[0]["enabled"] == False
        
        # Enable
        automation_framework.enable_automation("toggle_test_001")
        
        automations = automation_framework.get_all_automations()
        assert automations[0]["enabled"] == True
    
    def test_get_execution_history(self, automation_framework):
        """Test getting execution history"""
        automation_framework.register_automation(
            automation_id="history_test_001",
            name="History Test",
            description="Test history",
            automation_type=AutomationType.SCRIPT,
            execute_func=success_func
        )
        
        # Execute multiple times
        for i in range(3):
            automation_framework.execute_automation("history_test_001", data=f"test_{i}")
        
        # Get history
        history = automation_framework.get_execution_history("history_test_001", limit=10)
        
        assert len(history) == 3
        assert all(h["automation_id"] == "history_test_001" for h in history)
        
        # Get all history (no filter)
        all_history = automation_framework.get_execution_history(limit=100)
        assert len(all_history) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
