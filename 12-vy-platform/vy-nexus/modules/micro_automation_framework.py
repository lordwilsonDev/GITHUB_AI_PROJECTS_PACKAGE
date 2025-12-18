#!/usr/bin/env python3
"""
Micro-Automation Framework for vy-nexus
Creates, manages, and executes small, focused automation scripts
for repetitive tasks identified by the system.

Author: vy-nexus Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
import time
import hashlib
import subprocess
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging


class AutomationType(Enum):
    """Types of micro-automations"""
    SHELL_SCRIPT = "shell_script"
    PYTHON_SCRIPT = "python_script"
    APPLESCRIPT = "applescript"
    KEYBOARD_SHORTCUT = "keyboard_shortcut"
    API_CALL = "api_call"
    FILE_OPERATION = "file_operation"
    BROWSER_AUTOMATION = "browser_automation"
    SYSTEM_COMMAND = "system_command"


class ExecutionStatus(Enum):
    """Execution status of automations"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class MicroAutomation:
    """Represents a single micro-automation"""
    automation_id: str
    name: str
    description: str
    automation_type: AutomationType
    script_content: str
    trigger_conditions: Dict[str, Any]
    parameters: Dict[str, Any]
    created_at: str
    last_executed: Optional[str] = None
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    average_execution_time: float = 0.0
    enabled: bool = True
    priority: int = 5  # 1-10, higher = more important
    tags: List[str] = None
    dependencies: List[str] = None  # Other automation IDs this depends on
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class ExecutionResult:
    """Result of an automation execution"""
    automation_id: str
    status: ExecutionStatus
    start_time: str
    end_time: str
    execution_time: float
    output: str
    error: Optional[str] = None
    return_code: Optional[int] = None


class MicroAutomationFramework:
    """Framework for creating and managing micro-automations"""
    
    def __init__(self, storage_dir: str = "~/vy-nexus/automations"):
        self.storage_dir = os.path.expanduser(storage_dir)
        self.automations_file = os.path.join(self.storage_dir, "automations.json")
        self.execution_log_file = os.path.join(self.storage_dir, "execution_log.json")
        self.scripts_dir = os.path.join(self.storage_dir, "scripts")
        
        # Create directories
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(self.scripts_dir, exist_ok=True)
        
        # In-memory storage
        self.automations: Dict[str, MicroAutomation] = {}
        self.execution_history: List[ExecutionResult] = []
        self.running_automations: Dict[str, threading.Thread] = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Load existing automations
        self._load_automations()
        self._load_execution_history()
    
    def create_automation(
        self,
        name: str,
        description: str,
        automation_type: AutomationType,
        script_content: str,
        trigger_conditions: Dict[str, Any] = None,
        parameters: Dict[str, Any] = None,
        priority: int = 5,
        tags: List[str] = None,
        dependencies: List[str] = None
    ) -> str:
        """Create a new micro-automation"""
        
        # Generate unique ID
        automation_id = self._generate_automation_id(name, script_content)
        
        # Check if already exists
        if automation_id in self.automations:
            self.logger.warning(f"Automation {automation_id} already exists")
            return automation_id
        
        # Create automation object
        automation = MicroAutomation(
            automation_id=automation_id,
            name=name,
            description=description,
            automation_type=automation_type,
            script_content=script_content,
            trigger_conditions=trigger_conditions or {},
            parameters=parameters or {},
            created_at=datetime.now().isoformat(),
            priority=priority,
            tags=tags or [],
            dependencies=dependencies or []
        )
        
        # Save script to file
        self._save_script(automation)
        
        # Store automation
        self.automations[automation_id] = automation
        self._save_automations()
        
        self.logger.info(f"Created automation: {name} ({automation_id})")
        return automation_id
    
    def execute_automation(
        self,
        automation_id: str,
        async_execution: bool = False,
        timeout: int = 300
    ) -> ExecutionResult:
        """Execute a micro-automation"""
        
        if automation_id not in self.automations:
            raise ValueError(f"Automation {automation_id} not found")
        
        automation = self.automations[automation_id]
        
        if not automation.enabled:
            raise ValueError(f"Automation {automation_id} is disabled")
        
        # Check dependencies
        if not self._check_dependencies(automation):
            raise ValueError(f"Dependencies not met for {automation_id}")
        
        if async_execution:
            thread = threading.Thread(
                target=self._execute_automation_internal,
                args=(automation, timeout)
            )
            thread.start()
            self.running_automations[automation_id] = thread
            return None
        else:
            return self._execute_automation_internal(automation, timeout)
    
    def _execute_automation_internal(
        self,
        automation: MicroAutomation,
        timeout: int
    ) -> ExecutionResult:
        """Internal method to execute automation"""
        
        start_time = datetime.now()
        status = ExecutionStatus.RUNNING
        output = ""
        error = None
        return_code = None
        
        try:
            # Execute based on type
            if automation.automation_type == AutomationType.SHELL_SCRIPT:
                output, error, return_code = self._execute_shell_script(
                    automation, timeout
                )
            elif automation.automation_type == AutomationType.PYTHON_SCRIPT:
                output, error, return_code = self._execute_python_script(
                    automation, timeout
                )
            elif automation.automation_type == AutomationType.APPLESCRIPT:
                output, error, return_code = self._execute_applescript(
                    automation, timeout
                )
            elif automation.automation_type == AutomationType.SYSTEM_COMMAND:
                output, error, return_code = self._execute_system_command(
                    automation, timeout
                )
            else:
                raise NotImplementedError(
                    f"Automation type {automation.automation_type} not implemented"
                )
            
            # Determine status
            if return_code == 0:
                status = ExecutionStatus.SUCCESS
                automation.success_count += 1
            else:
                status = ExecutionStatus.FAILED
                automation.failure_count += 1
        
        except subprocess.TimeoutExpired:
            status = ExecutionStatus.TIMEOUT
            error = f"Execution timed out after {timeout} seconds"
            automation.failure_count += 1
        
        except Exception as e:
            status = ExecutionStatus.FAILED
            error = str(e)
            automation.failure_count += 1
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Update automation stats
        automation.execution_count += 1
        automation.last_executed = end_time.isoformat()
        automation.average_execution_time = (
            (automation.average_execution_time * (automation.execution_count - 1) +
             execution_time) / automation.execution_count
        )
        
        # Create result
        result = ExecutionResult(
            automation_id=automation.automation_id,
            status=status,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            execution_time=execution_time,
            output=output,
            error=error,
            return_code=return_code
        )
        
        # Log execution
        self.execution_history.append(result)
        self._save_execution_history()
        self._save_automations()
        
        # Remove from running
        if automation.automation_id in self.running_automations:
            del self.running_automations[automation.automation_id]
        
        return result
    
    def _execute_shell_script(
        self,
        automation: MicroAutomation,
        timeout: int
    ) -> tuple:
        """Execute a shell script"""
        script_path = self._get_script_path(automation)
        
        # Make executable
        os.chmod(script_path, 0o755)
        
        # Execute
        result = subprocess.run(
            [script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=self.scripts_dir
        )
        
        return result.stdout, result.stderr, result.returncode
    
    def _execute_python_script(
        self,
        automation: MicroAutomation,
        timeout: int
    ) -> tuple:
        """Execute a Python script"""
        script_path = self._get_script_path(automation)
        
        # Execute
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=self.scripts_dir
        )
        
        return result.stdout, result.stderr, result.returncode
    
    def _execute_applescript(
        self,
        automation: MicroAutomation,
        timeout: int
    ) -> tuple:
        """Execute an AppleScript"""
        script_path = self._get_script_path(automation)
        
        # Execute
        result = subprocess.run(
            ["osascript", script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=self.scripts_dir
        )
        
        return result.stdout, result.stderr, result.returncode
    
    def _execute_system_command(
        self,
        automation: MicroAutomation,
        timeout: int
    ) -> tuple:
        """Execute a system command"""
        
        # Execute command directly
        result = subprocess.run(
            automation.script_content,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=self.scripts_dir
        )
        
        return result.stdout, result.stderr, result.returncode
    
    def _check_dependencies(self, automation: MicroAutomation) -> bool:
        """Check if all dependencies are met"""
        for dep_id in automation.dependencies:
            if dep_id not in self.automations:
                return False
            
            dep = self.automations[dep_id]
            if not dep.enabled:
                return False
            
            # Check if dependency has been executed successfully recently
            if dep.success_count == 0:
                return False
        
        return True
    
    def get_automation(self, automation_id: str) -> Optional[MicroAutomation]:
        """Get automation by ID"""
        return self.automations.get(automation_id)
    
    def list_automations(
        self,
        tags: List[str] = None,
        enabled_only: bool = False
    ) -> List[MicroAutomation]:
        """List all automations with optional filtering"""
        automations = list(self.automations.values())
        
        if tags:
            automations = [
                a for a in automations
                if any(tag in a.tags for tag in tags)
            ]
        
        if enabled_only:
            automations = [a for a in automations if a.enabled]
        
        return sorted(automations, key=lambda x: x.priority, reverse=True)
    
    def enable_automation(self, automation_id: str):
        """Enable an automation"""
        if automation_id in self.automations:
            self.automations[automation_id].enabled = True
            self._save_automations()
    
    def disable_automation(self, automation_id: str):
        """Disable an automation"""
        if automation_id in self.automations:
            self.automations[automation_id].enabled = False
            self._save_automations()
    
    def delete_automation(self, automation_id: str):
        """Delete an automation"""
        if automation_id in self.automations:
            automation = self.automations[automation_id]
            
            # Delete script file
            script_path = self._get_script_path(automation)
            if os.path.exists(script_path):
                os.remove(script_path)
            
            # Remove from memory
            del self.automations[automation_id]
            self._save_automations()
    
    def get_execution_history(
        self,
        automation_id: Optional[str] = None,
        limit: int = 100
    ) -> List[ExecutionResult]:
        """Get execution history"""
        history = self.execution_history
        
        if automation_id:
            history = [h for h in history if h.automation_id == automation_id]
        
        return history[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get framework statistics"""
        total_automations = len(self.automations)
        enabled_automations = sum(1 for a in self.automations.values() if a.enabled)
        total_executions = sum(a.execution_count for a in self.automations.values())
        total_successes = sum(a.success_count for a in self.automations.values())
        total_failures = sum(a.failure_count for a in self.automations.values())
        
        success_rate = (
            (total_successes / total_executions * 100)
            if total_executions > 0 else 0
        )
        
        return {
            "total_automations": total_automations,
            "enabled_automations": enabled_automations,
            "disabled_automations": total_automations - enabled_automations,
            "total_executions": total_executions,
            "total_successes": total_successes,
            "total_failures": total_failures,
            "success_rate": round(success_rate, 2),
            "running_automations": len(self.running_automations)
        }
    
    def generate_report(self) -> str:
        """Generate a comprehensive report"""
        stats = self.get_statistics()
        automations = self.list_automations()
        
        report = []
        report.append("=" * 80)
        report.append("MICRO-AUTOMATION FRAMEWORK REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append("STATISTICS:")
        report.append("-" * 80)
        report.append(f"Total Automations: {stats['total_automations']}")
        report.append(f"Enabled: {stats['enabled_automations']}")
        report.append(f"Disabled: {stats['disabled_automations']}")
        report.append(f"Total Executions: {stats['total_executions']}")
        report.append(f"Success Rate: {stats['success_rate']}%")
        report.append(f"Currently Running: {stats['running_automations']}")
        report.append("")
        
        report.append("TOP AUTOMATIONS BY EXECUTION COUNT:")
        report.append("-" * 80)
        top_automations = sorted(
            automations,
            key=lambda x: x.execution_count,
            reverse=True
        )[:10]
        
        for i, automation in enumerate(top_automations, 1):
            success_rate = (
                (automation.success_count / automation.execution_count * 100)
                if automation.execution_count > 0 else 0
            )
            report.append(
                f"{i}. {automation.name} - "
                f"Executions: {automation.execution_count}, "
                f"Success Rate: {success_rate:.1f}%, "
                f"Avg Time: {automation.average_execution_time:.2f}s"
            )
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def _generate_automation_id(self, name: str, script_content: str) -> str:
        """Generate unique automation ID"""
        content = f"{name}:{script_content}:{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _get_script_path(self, automation: MicroAutomation) -> str:
        """Get path to script file"""
        extension_map = {
            AutomationType.SHELL_SCRIPT: ".sh",
            AutomationType.PYTHON_SCRIPT: ".py",
            AutomationType.APPLESCRIPT: ".scpt",
        }
        
        extension = extension_map.get(automation.automation_type, ".txt")
        return os.path.join(
            self.scripts_dir,
            f"{automation.automation_id}{extension}"
        )
    
    def _save_script(self, automation: MicroAutomation):
        """Save script to file"""
        script_path = self._get_script_path(automation)
        
        with open(script_path, 'w') as f:
            f.write(automation.script_content)
    
    def _load_automations(self):
        """Load automations from file"""
        if os.path.exists(self.automations_file):
            try:
                with open(self.automations_file, 'r') as f:
                    data = json.load(f)
                    for auto_data in data:
                        auto_data['automation_type'] = AutomationType(
                            auto_data['automation_type']
                        )
                        automation = MicroAutomation(**auto_data)
                        self.automations[automation.automation_id] = automation
            except Exception as e:
                self.logger.error(f"Error loading automations: {e}")
    
    def _save_automations(self):
        """Save automations to file"""
        try:
            data = []
            for automation in self.automations.values():
                auto_dict = asdict(automation)
                auto_dict['automation_type'] = automation.automation_type.value
                data.append(auto_dict)
            
            with open(self.automations_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving automations: {e}")
    
    def _load_execution_history(self):
        """Load execution history from file"""
        if os.path.exists(self.execution_log_file):
            try:
                with open(self.execution_log_file, 'r') as f:
                    data = json.load(f)
                    for result_data in data[-1000:]:  # Keep last 1000
                        result_data['status'] = ExecutionStatus(
                            result_data['status']
                        )
                        result = ExecutionResult(**result_data)
                        self.execution_history.append(result)
            except Exception as e:
                self.logger.error(f"Error loading execution history: {e}")
    
    def _save_execution_history(self):
        """Save execution history to file"""
        try:
            data = []
            for result in self.execution_history[-1000:]:  # Keep last 1000
                result_dict = asdict(result)
                result_dict['status'] = result.status.value
                data.append(result_dict)
            
            with open(self.execution_log_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving execution history: {e}")


if __name__ == "__main__":
    # Test the framework
    print("Testing Micro-Automation Framework...\n")
    
    framework = MicroAutomationFramework()
    
    # Create a simple shell script automation
    shell_script = """#!/bin/bash
echo "Hello from micro-automation!"
date
"""
    
    auto_id = framework.create_automation(
        name="Test Shell Script",
        description="A simple test automation",
        automation_type=AutomationType.SHELL_SCRIPT,
        script_content=shell_script,
        priority=8,
        tags=["test", "shell"]
    )
    
    print(f"Created automation: {auto_id}\n")
    
    # Execute it
    result = framework.execute_automation(auto_id)
    print(f"Execution result: {result.status.value}")
    print(f"Output: {result.output}")
    print(f"Execution time: {result.execution_time:.2f}s\n")
    
    # Create a Python script automation
    python_script = """#!/usr/bin/env python3
import sys
print("Python automation running!")
print(f"Python version: {sys.version}")
"""
    
    auto_id2 = framework.create_automation(
        name="Test Python Script",
        description="A simple Python automation",
        automation_type=AutomationType.PYTHON_SCRIPT,
        script_content=python_script,
        priority=7,
        tags=["test", "python"]
    )
    
    print(f"Created automation: {auto_id2}\n")
    
    # Execute it
    result2 = framework.execute_automation(auto_id2)
    print(f"Execution result: {result2.status.value}")
    print(f"Output: {result2.output}")
    print(f"Execution time: {result2.execution_time:.2f}s\n")
    
    # Generate report
    print(framework.generate_report())
