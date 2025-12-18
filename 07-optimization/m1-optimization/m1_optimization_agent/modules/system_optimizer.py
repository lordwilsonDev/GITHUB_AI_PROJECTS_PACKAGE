#!/usr/bin/env python3
"""
System Optimizer Module
Handles macOS system-level optimizations for M1 systems.
"""

import os
import subprocess
import json
from typing import Dict, List, Optional
from loguru import logger


class SystemOptimizer:
    """Handles system-level optimizations for macOS M1 systems."""
    
    def __init__(self):
        self.backup_file = "config/system_backup.json"
        self._ensure_backup_exists()
    
    def _ensure_backup_exists(self):
        """Ensure backup directory exists."""
        os.makedirs(os.path.dirname(self.backup_file), exist_ok=True)
    
    def _run_command(self, command: List[str], sudo: bool = False) -> Dict:
        """Execute a system command and return result."""
        try:
            if sudo:
                command = ['sudo'] + command
            
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
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {' '.join(command)}")
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _backup_setting(self, key: str, value: any):
        """Backup a setting before changing it."""
        try:
            backup = {}
            if os.path.exists(self.backup_file):
                with open(self.backup_file, 'r') as f:
                    backup = json.load(f)
            
            backup[key] = value
            
            with open(self.backup_file, 'w') as f:
                json.dump(backup, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to backup setting {key}: {e}")
    
    def optimize_windowserver(self, disable_transparency: bool = True, 
                            disable_animations: bool = True,
                            aggressive: bool = False) -> Dict:
        """Optimize WindowServer by reducing visual effects.
        
        Args:
            disable_transparency: Disable transparency effects
            disable_animations: Disable window animations
            aggressive: Apply aggressive optimizations (all animations)
        
        Returns:
            Dict with success status and applied changes
        """
        logger.info("Starting WindowServer optimization")
        results = {"success": True, "changes": []}
        
        try:
            # Disable transparency
            if disable_transparency:
                # Note: This is typically done via System Settings > Accessibility > Display
                # We'll use defaults write for the animation settings
                result = self._run_command([
                    'defaults', 'write', 'com.apple.universalaccess',
                    'reduceTransparency', '-bool', 'true'
                ])
                if result["success"]:
                    results["changes"].append("Transparency disabled")
                    logger.info("Transparency disabled")
            
            # Disable window animations
            if disable_animations:
                commands = [
                    ['defaults', 'write', 'NSGlobalDomain', 'NSAutomaticWindowAnimationsEnabled', '-bool', 'false'],
                    ['defaults', 'write', 'NSGlobalDomain', 'NSWindowResizeTime', '-float', '0.001'],
                ]
                
                for cmd in commands:
                    result = self._run_command(cmd)
                    if result["success"]:
                        results["changes"].append(f"Applied: {' '.join(cmd[2:4])}")
            
            # Aggressive mode: disable all animations
            if aggressive:
                aggressive_commands = [
                    ['defaults', 'write', 'com.apple.finder', 'DisableAllAnimations', '-bool', 'true'],
                    ['defaults', 'write', 'com.apple.dock', 'launchanim', '-bool', 'false'],
                    ['defaults', 'write', 'com.apple.dock', 'expose-animation-duration', '-float', '0'],
                    ['defaults', 'write', 'com.apple.dock', 'autohide-time-modifier', '-float', '0'],
                    ['defaults', 'write', 'com.apple.dock', 'autohide-delay', '-float', '0'],
                ]
                
                for cmd in aggressive_commands:
                    result = self._run_command(cmd)
                    if result["success"]:
                        results["changes"].append(f"Applied: {' '.join(cmd[2:4])}")
                
                # Restart Dock and Finder to apply changes
                self._run_command(['killall', 'Dock'])
                self._run_command(['killall', 'Finder'])
                results["changes"].append("Restarted Dock and Finder")
            
            logger.info(f"WindowServer optimization complete: {len(results['changes'])} changes applied")
            
        except Exception as e:
            logger.error(f"WindowServer optimization failed: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results
    
    def manage_spotlight(self, action: str, volume: str = "/") -> Dict:
        """Manage Spotlight indexing.
        
        Args:
            action: 'disable', 'enable', or 'rebuild'
            volume: Volume path (default: /)
        
        Returns:
            Dict with success status and message
        """
        logger.info(f"Managing Spotlight: {action} on {volume}")
        results = {"success": True, "action": action}
        
        try:
            if action == "disable":
                result = self._run_command(['sudo', 'mdutil', '-i', 'off', volume], sudo=False)
                if result["success"]:
                    results["message"] = f"Spotlight indexing disabled on {volume}"
                    logger.info(results["message"])
                else:
                    results["success"] = False
                    results["error"] = result.get("stderr", "Failed to disable Spotlight")
            
            elif action == "enable":
                result = self._run_command(['sudo', 'mdutil', '-i', 'on', volume], sudo=False)
                if result["success"]:
                    results["message"] = f"Spotlight indexing enabled on {volume}"
                    logger.info(results["message"])
                else:
                    results["success"] = False
                    results["error"] = result.get("stderr", "Failed to enable Spotlight")
            
            elif action == "rebuild":
                result = self._run_command(['sudo', 'mdutil', '-E', volume], sudo=False)
                if result["success"]:
                    results["message"] = f"Spotlight index rebuild initiated on {volume}"
                    results["warning"] = "Rebuild is resource-intensive. Avoid during inference."
                    logger.info(results["message"])
                else:
                    results["success"] = False
                    results["error"] = result.get("stderr", "Failed to rebuild Spotlight")
            
            else:
                results["success"] = False
                results["error"] = f"Unknown action: {action}"
        
        except Exception as e:
            logger.error(f"Spotlight management failed: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results
    
    def disable_background_services(self, services: List[str]) -> Dict:
        """Disable resource-intensive background services.
        
        Args:
            services: List of service names to disable (e.g., ['photoanalysisd', 'mediaanalysisd'])
        
        Returns:
            Dict with success status and disabled services
        """
        logger.info(f"Disabling background services: {services}")
        results = {"success": True, "disabled": [], "failed": []}
        
        service_map = {
            "photoanalysisd": "com.apple.photoanalysisd",
            "mediaanalysisd": "com.apple.mediaanalysisd",
            "photolibraryd": "com.apple.photolibraryd",
        }
        
        try:
            uid = os.getuid()
            
            for service in services:
                service_id = service_map.get(service, service)
                
                # Try to disable the service
                result = self._run_command([
                    'launchctl', 'disable', f'user/{uid}/{service_id}'
                ])
                
                if result["success"]:
                    results["disabled"].append(service)
                    logger.info(f"Disabled service: {service}")
                    
                    # Try to kill the process if it's running
                    kill_result = self._run_command(['killall', '-STOP', service])
                    if kill_result["success"]:
                        logger.info(f"Stopped running process: {service}")
                else:
                    results["failed"].append(service)
                    logger.warning(f"Failed to disable service: {service}")
            
            if results["failed"]:
                results["warning"] = f"Some services could not be disabled: {results['failed']}"
        
        except Exception as e:
            logger.error(f"Failed to disable background services: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results
    
    def setup_python_env(self, env_name: str, install_mlx: bool = False,
                        install_pytorch_mps: bool = False) -> Dict:
        """Setup Python environment using uv.
        
        Args:
            env_name: Name of the virtual environment
            install_mlx: Install MLX for native M1 support
            install_pytorch_mps: Install PyTorch with MPS support
        
        Returns:
            Dict with success status and installation details
        """
        logger.info(f"Setting up Python environment: {env_name}")
        results = {"success": True, "env_name": env_name, "packages": []}
        
        try:
            # Check if uv is installed
            uv_check = self._run_command(['which', 'uv'])
            
            if not uv_check["success"]:
                results["warning"] = "uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
                logger.warning(results["warning"])
                # Fall back to standard venv
                result = self._run_command(['python3', '-m', 'venv', env_name])
                if result["success"]:
                    results["method"] = "venv"
                else:
                    results["success"] = False
                    results["error"] = "Failed to create virtual environment"
                    return results
            else:
                # Use uv to create environment
                result = self._run_command(['uv', 'venv', env_name])
                if result["success"]:
                    results["method"] = "uv"
                    logger.info(f"Created environment with uv: {env_name}")
                else:
                    results["success"] = False
                    results["error"] = "Failed to create uv environment"
                    return results
            
            # Install packages
            pip_cmd = 'uv pip' if results["method"] == "uv" else f'{env_name}/bin/pip'
            
            if install_mlx:
                mlx_result = self._run_command(pip_cmd.split() + ['install', 'mlx', 'mlx-lm'])
                if mlx_result["success"]:
                    results["packages"].append("mlx")
                    logger.info("Installed MLX")
            
            if install_pytorch_mps:
                torch_result = self._run_command(pip_cmd.split() + ['install', 'torch', 'torchvision'])
                if torch_result["success"]:
                    results["packages"].append("pytorch")
                    logger.info("Installed PyTorch")
            
            results["message"] = f"Environment '{env_name}' created successfully"
        
        except Exception as e:
            logger.error(f"Python environment setup failed: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results
    
    def restore_defaults(self) -> Dict:
        """Restore system to default settings using backup."""
        logger.info("Restoring system defaults")
        results = {"success": True, "restored": []}
        
        try:
            if not os.path.exists(self.backup_file):
                results["warning"] = "No backup file found"
                return results
            
            with open(self.backup_file, 'r') as f:
                backup = json.load(f)
            
            # Restore transparency
            if 'reduceTransparency' in backup:
                self._run_command([
                    'defaults', 'write', 'com.apple.universalaccess',
                    'reduceTransparency', '-bool', str(backup['reduceTransparency']).lower()
                ])
                results["restored"].append("transparency")
            
            # Restore animations
            self._run_command(['defaults', 'delete', 'NSGlobalDomain', 'NSAutomaticWindowAnimationsEnabled'])
            self._run_command(['defaults', 'delete', 'NSGlobalDomain', 'NSWindowResizeTime'])
            results["restored"].append("animations")
            
            # Restart Dock and Finder
            self._run_command(['killall', 'Dock'])
            self._run_command(['killall', 'Finder'])
            
            logger.info(f"Restored {len(results['restored'])} settings")
        
        except Exception as e:
            logger.error(f"Failed to restore defaults: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results
