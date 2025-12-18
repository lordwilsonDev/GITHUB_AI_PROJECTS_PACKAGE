#!/usr/bin/env python3
"""
Process Manager Module
Handles process priority optimization and management.
"""

import os
import subprocess
import psutil
from typing import Dict, List, Optional
from loguru import logger


class ProcessManager:
    """Manages process priorities and scheduling for optimal M1 performance."""
    
    def __init__(self):
        pass
    
    def _run_command(self, command: List[str]) -> Dict:
        """Execute a system command and return result."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return {"success": False, "error": str(e)}
    
    def find_process_pid(self, process_name: str) -> List[int]:
        """Find PIDs for a given process name.
        
        Args:
            process_name: Name of the process to find
        
        Returns:
            List of PIDs matching the process name
        """
        pids = []
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if process_name.lower() in proc.info['name'].lower():
                    pids.append(proc.info['pid'])
        except Exception as e:
            logger.error(f"Failed to find process {process_name}: {e}")
        
        return pids
    
    def optimize_priority(self, process_name: str, priority: str = "high") -> Dict:
        """Optimize process priority using taskpolicy.
        
        Args:
            process_name: Name of the process (e.g., 'ollama', 'python')
            priority: Priority level ('high', 'normal', 'low')
        
        Returns:
            Dict with success status and applied changes
        """
        logger.info(f"Optimizing priority for {process_name} to {priority}")
        
        results = {
            "success": True,
            "process_name": process_name,
            "priority": priority,
            "applied_to_pids": []
        }
        
        try:
            # Find process PIDs
            pids = self.find_process_pid(process_name)
            
            if not pids:
                results["success"] = False
                results["error"] = f"No processes found matching '{process_name}'"
                logger.warning(results["error"])
                return results
            
            # Apply taskpolicy to each PID
            for pid in pids:
                if priority == "high":
                    # Promote to foreground/high priority
                    # -B: background (but we use it to promote)
                    # -t 5: highest throughput tier
                    result = self._run_command(['taskpolicy', '-B', '-t', '5', '-p', str(pid)])
                elif priority == "normal":
                    # Reset to normal
                    result = self._run_command(['taskpolicy', '-d', '-p', str(pid)])
                elif priority == "low":
                    # Demote to background
                    result = self._run_command(['taskpolicy', '-b', '-p', str(pid)])
                else:
                    results["success"] = False
                    results["error"] = f"Unknown priority level: {priority}"
                    return results
                
                if result["success"]:
                    results["applied_to_pids"].append(pid)
                    logger.info(f"Applied {priority} priority to PID {pid}")
                else:
                    logger.warning(f"Failed to apply priority to PID {pid}: {result.get('stderr', '')}")
            
            results["message"] = f"Priority optimization applied to {len(results['applied_to_pids'])} process(es)"
        
        except Exception as e:
            logger.error(f"Priority optimization failed: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results
    
    def disable_app_nap(self, global_disable: bool = True) -> Dict:
        """Disable App Nap to prevent process throttling.
        
        Args:
            global_disable: If True, disable globally; otherwise per-app
        
        Returns:
            Dict with success status
        """
        logger.info(f"Disabling App Nap (global={global_disable})")
        
        results = {"success": True}
        
        try:
            if global_disable:
                result = self._run_command([
                    'defaults', 'write', 'NSGlobalDomain',
                    'NSAppSleepDisabled', '-bool', 'YES'
                ])
                
                if result["success"]:
                    results["message"] = "App Nap disabled globally"
                    logger.info(results["message"])
                else:
                    results["success"] = False
                    results["error"] = "Failed to disable App Nap"
        
        except Exception as e:
            logger.error(f"Failed to disable App Nap: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results
    
    def prevent_sleep(self, enable: bool = True) -> Dict:
        """Prevent system sleep during inference tasks.
        
        Args:
            enable: If True, prevent sleep; if False, allow sleep
        
        Returns:
            Dict with success status and caffeinate PID if enabled
        """
        logger.info(f"{'Preventing' if enable else 'Allowing'} system sleep")
        
        results = {"success": True, "enabled": enable}
        
        try:
            if enable:
                # Start caffeinate in background
                # -i: prevent idle sleep
                # -d: prevent display sleep
                # -s: prevent system sleep
                process = subprocess.Popen(
                    ['caffeinate', '-i', '-d', '-s'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                results["caffeinate_pid"] = process.pid
                results["message"] = f"System sleep prevention enabled (PID: {process.pid})"
                logger.info(results["message"])
            else:
                # Kill existing caffeinate processes
                result = self._run_command(['killall', 'caffeinate'])
                results["message"] = "System sleep prevention disabled"
                logger.info(results["message"])
        
        except Exception as e:
            logger.error(f"Failed to manage sleep prevention: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results
    
    def get_process_info(self, process_name: str) -> Dict:
        """Get detailed information about a process.
        
        Args:
            process_name: Name of the process
        
        Returns:
            Dict with process information
        """
        logger.info(f"Getting info for process: {process_name}")
        
        results = {
            "success": True,
            "process_name": process_name,
            "instances": []
        }
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                            'status', 'num_threads', 'create_time']):
                if process_name.lower() in proc.info['name'].lower():
                    results["instances"].append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu_percent": proc.info['cpu_percent'],
                        "memory_percent": round(proc.info['memory_percent'], 2),
                        "status": proc.info['status'],
                        "num_threads": proc.info['num_threads'],
                        "create_time": proc.info['create_time']
                    })
            
            if not results["instances"]:
                results["message"] = f"No processes found matching '{process_name}'"
            else:
                results["message"] = f"Found {len(results['instances'])} instance(s)"
        
        except Exception as e:
            logger.error(f"Failed to get process info: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results
    
    def kill_process(self, process_name: str, force: bool = False) -> Dict:
        """Kill a process by name.
        
        Args:
            process_name: Name of the process to kill
            force: If True, use SIGKILL; otherwise use SIGTERM
        
        Returns:
            Dict with success status
        """
        logger.info(f"Killing process: {process_name} (force={force})")
        
        results = {
            "success": True,
            "process_name": process_name,
            "killed_pids": []
        }
        
        try:
            signal = '-9' if force else '-15'
            result = self._run_command(['killall', signal, process_name])
            
            if result["success"]:
                results["message"] = f"Process '{process_name}' terminated"
                logger.info(results["message"])
            else:
                results["success"] = False
                results["error"] = f"Failed to kill process: {result.get('stderr', '')}"
        
        except Exception as e:
            logger.error(f"Failed to kill process: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results
