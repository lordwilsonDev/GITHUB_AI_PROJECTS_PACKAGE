#!/usr/bin/env python3
"""
Automation Script Manager

Manages automation scripts with version control, execution monitoring,
and automatic optimization capabilities.

Features:
- Script lifecycle management (create, update, deprecate)
- Version control and rollback
- Execution monitoring and logging
- Performance tracking and optimization
- Dependency management
- Security validation
- Automatic error recovery
"""

import json
import os
import hashlib
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class AutomationScriptManager:
    """Manages automation scripts with comprehensive lifecycle management."""
    
    def __init__(self, base_dir: str = "~/vy-nexus/data/automation_scripts"):
        self.base_dir = Path(base_dir).expanduser()
        self.scripts_dir = self.base_dir / "scripts"
        self.versions_dir = self.base_dir / "versions"
        self.logs_dir = self.base_dir / "logs"
        self.metadata_file = self.base_dir / "script_metadata.json"
        self.execution_log = self.base_dir / "execution_log.json"
        
        # Create directories
        for directory in [self.scripts_dir, self.versions_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.metadata = self._load_metadata()
        self.execution_history = self._load_execution_log()
    
    def _load_metadata(self) -> Dict:
        """Load script metadata."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"scripts": {}, "last_updated": None}
    
    def _save_metadata(self):
        """Save script metadata."""
        self.metadata["last_updated"] = datetime.now().isoformat()
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _load_execution_log(self) -> List[Dict]:
        """Load execution history."""
        if self.execution_log.exists():
            with open(self.execution_log, 'r') as f:
                return json.load(f)
        return []
    
    def _save_execution_log(self):
        """Save execution history."""
        with open(self.execution_log, 'w') as f:
            json.dump(self.execution_history, f, indent=2)
    
    def _calculate_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of script content."""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def create_script(self, script_id: str, content: str, 
                     description: str = "", tags: List[str] = None,
                     dependencies: List[str] = None) -> Dict:
        """Create a new automation script."""
        if script_id in self.metadata["scripts"]:
            return {"success": False, "error": "Script already exists"}
        
        # Validate script content
        validation = self._validate_script(content)
        if not validation["valid"]:
            return {"success": False, "error": validation["error"]}
        
        # Create script file
        script_path = self.scripts_dir / f"{script_id}.py"
        with open(script_path, 'w') as f:
            f.write(content)
        
        # Create version
        version_id = self._create_version(script_id, content, "Initial version")
        
        # Store metadata
        self.metadata["scripts"][script_id] = {
            "description": description,
            "tags": tags or [],
            "dependencies": dependencies or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "current_version": version_id,
            "status": "active",
            "execution_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "avg_execution_time": 0,
            "last_executed": None
        }
        
        self._save_metadata()
        
        return {
            "success": True,
            "script_id": script_id,
            "version_id": version_id,
            "path": str(script_path)
        }
    
    def update_script(self, script_id: str, content: str, 
                     change_description: str = "") -> Dict:
        """Update an existing script."""
        if script_id not in self.metadata["scripts"]:
            return {"success": False, "error": "Script not found"}
        
        # Validate script content
        validation = self._validate_script(content)
        if not validation["valid"]:
            return {"success": False, "error": validation["error"]}
        
        # Check if content actually changed
        script_path = self.scripts_dir / f"{script_id}.py"
        if script_path.exists():
            with open(script_path, 'r') as f:
                old_content = f.read()
            if self._calculate_hash(old_content) == self._calculate_hash(content):
                return {"success": False, "error": "No changes detected"}
        
        # Create new version
        version_id = self._create_version(script_id, content, change_description)
        
        # Update script file
        with open(script_path, 'w') as f:
            f.write(content)
        
        # Update metadata
        self.metadata["scripts"][script_id]["current_version"] = version_id
        self.metadata["scripts"][script_id]["updated_at"] = datetime.now().isoformat()
        self._save_metadata()
        
        return {
            "success": True,
            "script_id": script_id,
            "version_id": version_id
        }
    
    def _create_version(self, script_id: str, content: str, 
                       description: str) -> str:
        """Create a version snapshot of a script."""
        version_id = f"v{int(time.time())}"
        version_dir = self.versions_dir / script_id
        version_dir.mkdir(exist_ok=True)
        
        version_file = version_dir / f"{version_id}.py"
        with open(version_file, 'w') as f:
            f.write(content)
        
        # Store version metadata
        version_meta_file = version_dir / f"{version_id}.json"
        version_meta = {
            "version_id": version_id,
            "created_at": datetime.now().isoformat(),
            "description": description,
            "hash": self._calculate_hash(content)
        }
        with open(version_meta_file, 'w') as f:
            json.dump(version_meta, f, indent=2)
        
        return version_id
    
    def _validate_script(self, content: str) -> Dict:
        """Validate script content for security and syntax."""
        # Check for dangerous operations
        dangerous_patterns = [
            "os.system",
            "eval(",
            "exec(",
            "__import__",
            "rm -rf",
            "format(",  # Can be dangerous with user input
        ]
        
        for pattern in dangerous_patterns:
            if pattern in content:
                return {
                    "valid": False,
                    "error": f"Potentially dangerous operation detected: {pattern}"
                }
        
        # Try to compile the script
        try:
            compile(content, '<string>', 'exec')
        except SyntaxError as e:
            return {
                "valid": False,
                "error": f"Syntax error: {str(e)}"
            }
        
        return {"valid": True}
    
    def execute_script(self, script_id: str, args: List[str] = None,
                      timeout: int = 300) -> Dict:
        """Execute an automation script."""
        if script_id not in self.metadata["scripts"]:
            return {"success": False, "error": "Script not found"}
        
        script_meta = self.metadata["scripts"][script_id]
        if script_meta["status"] != "active":
            return {"success": False, "error": f"Script status: {script_meta['status']}"}
        
        script_path = self.scripts_dir / f"{script_id}.py"
        if not script_path.exists():
            return {"success": False, "error": "Script file not found"}
        
        # Prepare execution
        start_time = time.time()
        log_file = self.logs_dir / f"{script_id}_{int(start_time)}.log"
        
        try:
            # Execute script
            cmd = ["python3", str(script_path)] + (args or [])
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            success = result.returncode == 0
            
            # Log execution
            log_entry = {
                "script_id": script_id,
                "timestamp": datetime.now().isoformat(),
                "success": success,
                "execution_time": execution_time,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "args": args
            }
            
            # Save detailed log
            with open(log_file, 'w') as f:
                json.dump(log_entry, f, indent=2)
            
            # Update execution history
            self.execution_history.append({
                "script_id": script_id,
                "timestamp": log_entry["timestamp"],
                "success": success,
                "execution_time": execution_time
            })
            self._save_execution_log()
            
            # Update metadata
            script_meta["execution_count"] += 1
            script_meta["last_executed"] = log_entry["timestamp"]
            
            if success:
                script_meta["success_count"] += 1
            else:
                script_meta["failure_count"] += 1
            
            # Update average execution time
            total_time = (script_meta["avg_execution_time"] * 
                         (script_meta["execution_count"] - 1) + execution_time)
            script_meta["avg_execution_time"] = total_time / script_meta["execution_count"]
            
            self._save_metadata()
            
            return {
                "success": success,
                "execution_time": execution_time,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "log_file": str(log_file)
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Script execution timeout ({timeout}s)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}"
            }
    
    def rollback_script(self, script_id: str, version_id: str) -> Dict:
        """Rollback script to a previous version."""
        if script_id not in self.metadata["scripts"]:
            return {"success": False, "error": "Script not found"}
        
        version_file = self.versions_dir / script_id / f"{version_id}.py"
        if not version_file.exists():
            return {"success": False, "error": "Version not found"}
        
        # Read version content
        with open(version_file, 'r') as f:
            content = f.read()
        
        # Update current script
        script_path = self.scripts_dir / f"{script_id}.py"
        with open(script_path, 'w') as f:
            f.write(content)
        
        # Update metadata
        self.metadata["scripts"][script_id]["current_version"] = version_id
        self.metadata["scripts"][script_id]["updated_at"] = datetime.now().isoformat()
        self._save_metadata()
        
        return {"success": True, "script_id": script_id, "version_id": version_id}
    
    def get_script_performance(self, script_id: str) -> Dict:
        """Get performance metrics for a script."""
        if script_id not in self.metadata["scripts"]:
            return {"success": False, "error": "Script not found"}
        
        script_meta = self.metadata["scripts"][script_id]
        
        # Calculate success rate
        total_executions = script_meta["execution_count"]
        success_rate = 0
        if total_executions > 0:
            success_rate = (script_meta["success_count"] / total_executions) * 100
        
        # Get recent executions
        recent_executions = [
            e for e in self.execution_history[-50:]
            if e["script_id"] == script_id
        ]
        
        return {
            "success": True,
            "script_id": script_id,
            "total_executions": total_executions,
            "success_count": script_meta["success_count"],
            "failure_count": script_meta["failure_count"],
            "success_rate": success_rate,
            "avg_execution_time": script_meta["avg_execution_time"],
            "last_executed": script_meta["last_executed"],
            "recent_executions": recent_executions
        }
    
    def deprecate_script(self, script_id: str, reason: str = "") -> Dict:
        """Mark a script as deprecated."""
        if script_id not in self.metadata["scripts"]:
            return {"success": False, "error": "Script not found"}
        
        self.metadata["scripts"][script_id]["status"] = "deprecated"
        self.metadata["scripts"][script_id]["deprecated_at"] = datetime.now().isoformat()
        self.metadata["scripts"][script_id]["deprecation_reason"] = reason
        self._save_metadata()
        
        return {"success": True, "script_id": script_id}
    
    def list_scripts(self, status: str = None, tags: List[str] = None) -> List[Dict]:
        """List all scripts with optional filtering."""
        scripts = []
        
        for script_id, meta in self.metadata["scripts"].items():
            # Filter by status
            if status and meta["status"] != status:
                continue
            
            # Filter by tags
            if tags and not any(tag in meta["tags"] for tag in tags):
                continue
            
            scripts.append({
                "script_id": script_id,
                "description": meta["description"],
                "status": meta["status"],
                "tags": meta["tags"],
                "execution_count": meta["execution_count"],
                "success_rate": (meta["success_count"] / meta["execution_count"] * 100)
                               if meta["execution_count"] > 0 else 0,
                "last_executed": meta["last_executed"]
            })
        
        return scripts


def test_automation_script_manager():
    """Test the automation script manager."""
    manager = AutomationScriptManager()
    
    # Test script creation
    test_script = '''
import sys
print("Hello from automation script!")
print(f"Args: {sys.argv[1:]}")
'''
    
    result = manager.create_script(
        "test_hello",
        test_script,
        "Simple test script",
        tags=["test", "demo"]
    )
    print(f"Create script: {result}")
    
    # Test script execution
    exec_result = manager.execute_script("test_hello", ["arg1", "arg2"])
    print(f"\nExecute script: {exec_result}")
    
    # Test script update
    updated_script = '''
import sys
print("Updated automation script!")
print(f"Args: {sys.argv[1:]}")
print("New feature added")
'''
    
    update_result = manager.update_script(
        "test_hello",
        updated_script,
        "Added new feature"
    )
    print(f"\nUpdate script: {update_result}")
    
    # Test performance metrics
    perf = manager.get_script_performance("test_hello")
    print(f"\nPerformance metrics: {perf}")
    
    # Test list scripts
    scripts = manager.list_scripts(status="active")
    print(f"\nActive scripts: {len(scripts)}")
    for script in scripts:
        print(f"  - {script['script_id']}: {script['description']}")


if __name__ == "__main__":
    test_automation_script_manager()
