#!/usr/bin/env python3
"""
Automation Script Installer
Installs and configures automation scripts in the system
Part of the Self-Evolving AI Ecosystem
"""

import json
import os
import stat
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil
import subprocess

class AutomationScriptInstaller:
    """Manages installation of automation scripts"""
    
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
        self.data_dir = self.base_dir / "data" / "script_installation"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Installation directories
        self.install_dirs = {
            "python": Path.home() / ".vy-nexus" / "scripts" / "python",
            "shell": Path.home() / ".vy-nexus" / "scripts" / "shell",
            "applescript": Path.home() / ".vy-nexus" / "scripts" / "applescript",
            "workflows": Path.home() / ".vy-nexus" / "workflows"
        }
        
        # Create installation directories
        for dir_path in self.install_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Installation tracking
        self.installations_file = self.data_dir / "installations.jsonl"
        self.active_scripts_file = self.data_dir / "active_scripts.json"
        
        # Script types and their handlers
        self.script_types = {
            "python": self._install_python_script,
            "shell": self._install_shell_script,
            "applescript": self._install_applescript,
            "workflow": self._install_workflow
        }
        
        self._initialized = True
    
    def install_script(
        self,
        script_id: str,
        script_type: str,
        name: str,
        content: str,
        description: str = "",
        dependencies: Optional[List[str]] = None,
        schedule: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Install an automation script"""
        
        if script_type not in self.script_types:
            return {
                "success": False,
                "error": f"Unsupported script type: {script_type}"
            }
        
        # Check dependencies
        if dependencies:
            dep_check = self._check_dependencies(dependencies)
            if not dep_check["all_satisfied"]:
                return {
                    "success": False,
                    "error": "Dependencies not satisfied",
                    "missing_dependencies": dep_check["missing"]
                }
        
        # Install the script
        install_handler = self.script_types[script_type]
        install_result = install_handler(script_id, name, content, metadata or {})
        
        if not install_result["success"]:
            return install_result
        
        # Create installation record
        installation = {
            "script_id": script_id,
            "script_type": script_type,
            "name": name,
            "description": description,
            "install_path": install_result["install_path"],
            "dependencies": dependencies or [],
            "schedule": schedule,
            "installed_at": datetime.now().isoformat(),
            "status": "active",
            "execution_count": 0,
            "last_execution": None,
            "metadata": metadata or {}
        }
        
        # Save installation record
        with open(self.installations_file, 'a') as f:
            f.write(json.dumps(installation) + '\n')
        
        # Update active scripts
        self._update_active_scripts(installation)
        
        # Set up schedule if provided
        if schedule:
            self._setup_schedule(script_id, install_result["install_path"], schedule)
        
        return {
            "success": True,
            "script_id": script_id,
            "install_path": install_result["install_path"],
            "installation": installation
        }
    
    def _install_python_script(
        self,
        script_id: str,
        name: str,
        content: str,
        metadata: Dict
    ) -> Dict[str, Any]:
        """Install a Python script"""
        install_dir = self.install_dirs["python"]
        script_path = install_dir / f"{script_id}.py"
        
        try:
            # Write script content
            with open(script_path, 'w') as f:
                f.write("#!/usr/bin/env python3\n")
                f.write(f'"""{name}"""\n\n')
                f.write(content)
            
            # Make executable
            script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
            
            # Create wrapper script for easy execution
            wrapper_path = install_dir / f"{script_id}_run.sh"
            with open(wrapper_path, 'w') as f:
                f.write("#!/bin/bash\n")
                f.write(f"python3 {script_path} \"$@\"\n")
            wrapper_path.chmod(wrapper_path.stat().st_mode | stat.S_IEXEC)
            
            return {
                "success": True,
                "install_path": str(script_path),
                "wrapper_path": str(wrapper_path)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _install_shell_script(
        self,
        script_id: str,
        name: str,
        content: str,
        metadata: Dict
    ) -> Dict[str, Any]:
        """Install a shell script"""
        install_dir = self.install_dirs["shell"]
        script_path = install_dir / f"{script_id}.sh"
        
        try:
            # Write script content
            with open(script_path, 'w') as f:
                f.write("#!/bin/bash\n")
                f.write(f"# {name}\n\n")
                f.write(content)
            
            # Make executable
            script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
            
            return {
                "success": True,
                "install_path": str(script_path)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _install_applescript(
        self,
        script_id: str,
        name: str,
        content: str,
        metadata: Dict
    ) -> Dict[str, Any]:
        """Install an AppleScript"""
        install_dir = self.install_dirs["applescript"]
        script_path = install_dir / f"{script_id}.scpt"
        
        try:
            # Write script content to temporary file
            temp_path = install_dir / f"{script_id}_temp.applescript"
            with open(temp_path, 'w') as f:
                f.write(f"-- {name}\n\n")
                f.write(content)
            
            # Compile AppleScript
            result = subprocess.run(
                ["osacompile", "-o", str(script_path), str(temp_path)],
                capture_output=True,
                text=True
            )
            
            # Remove temporary file
            temp_path.unlink()
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"AppleScript compilation failed: {result.stderr}"
                }
            
            return {
                "success": True,
                "install_path": str(script_path)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _install_workflow(
        self,
        script_id: str,
        name: str,
        content: str,
        metadata: Dict
    ) -> Dict[str, Any]:
        """Install a workflow definition"""
        install_dir = self.install_dirs["workflows"]
        workflow_path = install_dir / f"{script_id}.json"
        
        try:
            # Parse workflow content
            if isinstance(content, str):
                workflow_data = json.loads(content)
            else:
                workflow_data = content
            
            # Add metadata
            workflow_data["name"] = name
            workflow_data["script_id"] = script_id
            workflow_data["installed_at"] = datetime.now().isoformat()
            
            # Write workflow
            with open(workflow_path, 'w') as f:
                json.dump(workflow_data, f, indent=2)
            
            return {
                "success": True,
                "install_path": str(workflow_path)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _check_dependencies(self, dependencies: List[str]) -> Dict[str, Any]:
        """Check if dependencies are satisfied"""
        missing = []
        satisfied = []
        
        for dep in dependencies:
            # Check if it's a command
            if shutil.which(dep):
                satisfied.append(dep)
            # Check if it's a Python package
            elif self._check_python_package(dep):
                satisfied.append(dep)
            else:
                missing.append(dep)
        
        return {
            "all_satisfied": len(missing) == 0,
            "satisfied": satisfied,
            "missing": missing
        }
    
    def _check_python_package(self, package: str) -> bool:
        """Check if a Python package is installed"""
        try:
            result = subprocess.run(
                ["python3", "-c", f"import {package}"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def _setup_schedule(
        self,
        script_id: str,
        script_path: str,
        schedule: Dict
    ):
        """Set up scheduled execution for a script"""
        schedule_type = schedule.get("type", "cron")
        
        if schedule_type == "cron":
            self._setup_cron_schedule(script_id, script_path, schedule)
        elif schedule_type == "interval":
            self._setup_interval_schedule(script_id, script_path, schedule)
        elif schedule_type == "launchd":
            self._setup_launchd_schedule(script_id, script_path, schedule)
    
    def _setup_cron_schedule(
        self,
        script_id: str,
        script_path: str,
        schedule: Dict
    ):
        """Set up cron schedule"""
        cron_expression = schedule.get("cron_expression")
        if not cron_expression:
            return
        
        # Create cron entry
        cron_entry = f"{cron_expression} {script_path}\n"
        
        # Save to cron file for manual installation
        cron_file = self.data_dir / "cron_entries" / f"{script_id}.cron"
        cron_file.parent.mkdir(exist_ok=True)
        with open(cron_file, 'w') as f:
            f.write(cron_entry)
    
    def _setup_interval_schedule(
        self,
        script_id: str,
        script_path: str,
        schedule: Dict
    ):
        """Set up interval-based schedule"""
        interval_seconds = schedule.get("interval_seconds", 3600)
        
        # Create interval configuration
        interval_config = {
            "script_id": script_id,
            "script_path": script_path,
            "interval_seconds": interval_seconds,
            "last_run": None,
            "next_run": None
        }
        
        # Save configuration
        config_file = self.data_dir / "intervals" / f"{script_id}.json"
        config_file.parent.mkdir(exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(interval_config, f, indent=2)
    
    def _setup_launchd_schedule(
        self,
        script_id: str,
        script_path: str,
        schedule: Dict
    ):
        """Set up launchd schedule (macOS)"""
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.vy-nexus.{script_id}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{script_path}</string>
    </array>
    <key>StartInterval</key>
    <integer>{schedule.get('interval_seconds', 3600)}</integer>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
        
        # Save plist file
        plist_file = self.data_dir / "launchd" / f"com.vy-nexus.{script_id}.plist"
        plist_file.parent.mkdir(exist_ok=True)
        with open(plist_file, 'w') as f:
            f.write(plist_content)
    
    def _update_active_scripts(self, installation: Dict):
        """Update active scripts registry"""
        active_scripts = {}
        
        if self.active_scripts_file.exists():
            with open(self.active_scripts_file, 'r') as f:
                active_scripts = json.load(f)
        
        active_scripts[installation["script_id"]] = {
            "name": installation["name"],
            "type": installation["script_type"],
            "path": installation["install_path"],
            "status": installation["status"],
            "installed_at": installation["installed_at"]
        }
        
        with open(self.active_scripts_file, 'w') as f:
            json.dump(active_scripts, f, indent=2)
    
    def uninstall_script(self, script_id: str) -> Dict[str, Any]:
        """Uninstall a script"""
        installation = self._load_installation(script_id)
        if not installation:
            return {"success": False, "error": "Script not found"}
        
        try:
            # Remove script file
            install_path = Path(installation["install_path"])
            if install_path.exists():
                install_path.unlink()
            
            # Remove wrapper if exists
            wrapper_path = install_path.parent / f"{script_id}_run.sh"
            if wrapper_path.exists():
                wrapper_path.unlink()
            
            # Remove from active scripts
            if self.active_scripts_file.exists():
                with open(self.active_scripts_file, 'r') as f:
                    active_scripts = json.load(f)
                if script_id in active_scripts:
                    del active_scripts[script_id]
                with open(self.active_scripts_file, 'w') as f:
                    json.dump(active_scripts, f, indent=2)
            
            # Update installation record
            installation["status"] = "uninstalled"
            installation["uninstalled_at"] = datetime.now().isoformat()
            
            with open(self.installations_file, 'a') as f:
                f.write(json.dumps(installation) + '\n')
            
            return {"success": True, "script_id": script_id}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_script(
        self,
        script_id: str,
        args: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Execute an installed script"""
        installation = self._load_installation(script_id)
        if not installation:
            return {"success": False, "error": "Script not found"}
        
        if installation["status"] != "active":
            return {"success": False, "error": "Script is not active"}
        
        script_path = installation["install_path"]
        
        try:
            # Execute script
            cmd = [script_path]
            if args:
                cmd.extend(args)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Update execution count
            installation["execution_count"] = installation.get("execution_count", 0) + 1
            installation["last_execution"] = datetime.now().isoformat()
            
            with open(self.installations_file, 'a') as f:
                f.write(json.dumps(installation) + '\n')
            
            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _load_installation(self, script_id: str) -> Optional[Dict]:
        """Load installation record for a script"""
        if not self.installations_file.exists():
            return None
        
        installations = []
        with open(self.installations_file, 'r') as f:
            for line in f:
                installation = json.loads(line.strip())
                if installation["script_id"] == script_id:
                    installations.append(installation)
        
        if not installations:
            return None
        
        # Return most recent installation
        return max(installations, key=lambda x: x.get("installed_at", ""))
    
    def get_active_scripts(self) -> List[Dict[str, Any]]:
        """Get all active scripts"""
        if not self.active_scripts_file.exists():
            return []
        
        with open(self.active_scripts_file, 'r') as f:
            active_scripts = json.load(f)
        
        return [
            {"script_id": sid, **info}
            for sid, info in active_scripts.items()
        ]
    
    def get_installation_history(self, script_id: str) -> List[Dict[str, Any]]:
        """Get installation history for a script"""
        history = []
        
        if self.installations_file.exists():
            with open(self.installations_file, 'r') as f:
                for line in f:
                    installation = json.loads(line.strip())
                    if installation["script_id"] == script_id:
                        history.append(installation)
        
        return sorted(history, key=lambda x: x.get("installed_at", ""), reverse=True)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get installation statistics"""
        stats = {
            "total_installations": 0,
            "active_scripts": 0,
            "by_type": {},
            "total_executions": 0,
            "most_executed": []
        }
        
        installations = {}
        
        if self.installations_file.exists():
            with open(self.installations_file, 'r') as f:
                for line in f:
                    installation = json.loads(line.strip())
                    script_id = installation["script_id"]
                    
                    # Keep only latest installation per script
                    if script_id not in installations or \
                       installation.get("installed_at", "") > installations[script_id].get("installed_at", ""):
                        installations[script_id] = installation
        
        for installation in installations.values():
            stats["total_installations"] += 1
            
            if installation.get("status") == "active":
                stats["active_scripts"] += 1
            
            script_type = installation.get("script_type", "unknown")
            stats["by_type"][script_type] = stats["by_type"].get(script_type, 0) + 1
            
            stats["total_executions"] += installation.get("execution_count", 0)
        
        # Find most executed scripts
        most_executed = sorted(
            installations.values(),
            key=lambda x: x.get("execution_count", 0),
            reverse=True
        )[:5]
        
        stats["most_executed"] = [
            {
                "script_id": s["script_id"],
                "name": s["name"],
                "execution_count": s.get("execution_count", 0)
            }
            for s in most_executed
        ]
        
        return stats

def get_installer() -> AutomationScriptInstaller:
    """Get the singleton AutomationScriptInstaller instance"""
    return AutomationScriptInstaller()

if __name__ == "__main__":
    # Example usage
    installer = get_installer()
    
    # Install a test Python script
    result = installer.install_script(
        script_id="test_script_001",
        script_type="python",
        name="Test Script",
        content="print('Hello from automation!')",
        description="A test automation script"
    )
    
    print(f"Installation result: {json.dumps(result, indent=2)}")
    print(f"\nStatistics: {json.dumps(installer.get_statistics(), indent=2)}")
