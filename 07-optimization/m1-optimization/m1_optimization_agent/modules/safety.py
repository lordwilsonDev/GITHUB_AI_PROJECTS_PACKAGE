#!/usr/bin/env python3
"""
Safety Module
Provides safety checks, validation, and rollback capabilities.
"""

import os
import json
import subprocess
import shutil
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from loguru import logger
import psutil


class SafetyManager:
    """Manages safety checks and rollback capabilities for system optimizations."""
    
    def __init__(self):
        self.backup_dir = "config/backups"
        self.restore_points_file = "config/restore_points.json"
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """Ensure backup directory exists."""
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def _run_command(self, command: List[str]) -> Dict:
        """Execute a system command safely."""
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
                "stderr": result.stderr
            }
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return {"success": False, "error": str(e)}
    
    def pre_optimization_checks(self) -> Dict:
        """Perform safety checks before applying optimizations.
        
        Returns:
            Dict with check results and warnings
        """
        logger.info("Running pre-optimization safety checks")
        
        checks = {
            "timestamp": datetime.now().isoformat(),
            "passed": True,
            "warnings": [],
            "errors": [],
            "system_info": {}
        }
        
        try:
            # Check 1: Verify running on Apple Silicon
            chip_result = self._run_command(['sysctl', '-n', 'machdep.cpu.brand_string'])
            if chip_result['success']:
                chip = chip_result['stdout'].strip()
                checks['system_info']['chip'] = chip
                
                if 'Apple' not in chip:
                    checks['warnings'].append(
                        "Not running on Apple Silicon. Optimizations are designed for M1/M2/M3 chips."
                    )
            
            # Check 2: Verify sufficient disk space
            disk = psutil.disk_usage('/')
            checks['system_info']['disk_free_gb'] = round(disk.free / (1024**3), 2)
            
            if disk.percent > 95:
                checks['errors'].append(
                    f"Critical: Disk usage is {disk.percent}%. Free up space before proceeding."
                )
                checks['passed'] = False
            elif disk.percent > 90:
                checks['warnings'].append(
                    f"Warning: Disk usage is {disk.percent}%. Consider freeing up space."
                )
            
            # Check 3: Check memory status
            mem = psutil.virtual_memory()
            checks['system_info']['ram_gb'] = round(mem.total / (1024**3), 2)
            checks['system_info']['ram_available_gb'] = round(mem.available / (1024**3), 2)
            
            if mem.percent > 90:
                checks['warnings'].append(
                    f"Memory usage is high ({mem.percent}%). Close applications before optimizing."
                )
            
            # Check 4: Verify Ollama installation
            ollama_check = self._run_command(['which', 'ollama'])
            checks['system_info']['ollama_installed'] = ollama_check['success']
            
            if not ollama_check['success']:
                checks['warnings'].append(
                    "Ollama not found. Install from https://ollama.ai"
                )
            
            # Check 5: Check for running critical processes
            critical_processes = ['Time Machine', 'Software Update', 'App Store']
            running_critical = []
            
            for proc in psutil.process_iter(['name']):
                if any(critical in proc.info['name'] for critical in critical_processes):
                    running_critical.append(proc.info['name'])
            
            if running_critical:
                checks['warnings'].append(
                    f"Critical processes running: {', '.join(running_critical)}. "
                    "Consider waiting for them to complete."
                )
            
            # Check 6: Verify backup capability
            if not os.access(self.backup_dir, os.W_OK):
                checks['errors'].append(
                    f"Cannot write to backup directory: {self.backup_dir}"
                )
                checks['passed'] = False
            
            # Check 7: Check for existing backups
            if os.path.exists(self.restore_points_file):
                with open(self.restore_points_file, 'r') as f:
                    restore_points = json.load(f)
                checks['system_info']['existing_restore_points'] = len(restore_points)
            else:
                checks['system_info']['existing_restore_points'] = 0
            
            logger.info(f"Pre-optimization checks completed. Passed: {checks['passed']}")
        
        except Exception as e:
            logger.error(f"Pre-optimization checks failed: {e}")
            checks['passed'] = False
            checks['errors'].append(f"Check failed: {str(e)}")
        
        return checks
    
    def create_restore_point(self, description: str = "Manual restore point") -> Dict:
        """Create a system restore point before making changes.
        
        Args:
            description: Description of the restore point
        
        Returns:
            Dict with restore point information
        """
        logger.info(f"Creating restore point: {description}")
        
        restore_point = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "settings": {},
            "success": True
        }
        
        try:
            # Backup current system settings
            settings_to_backup = [
                ('com.apple.universalaccess', 'reduceTransparency'),
                ('NSGlobalDomain', 'NSAutomaticWindowAnimationsEnabled'),
                ('NSGlobalDomain', 'NSWindowResizeTime'),
                ('NSGlobalDomain', 'NSAppSleepDisabled'),
                ('com.apple.finder', 'DisableAllAnimations'),
                ('com.apple.dock', 'launchanim'),
            ]
            
            for domain, key in settings_to_backup:
                result = self._run_command(['defaults', 'read', domain, key])
                if result['success']:
                    restore_point['settings'][f"{domain}.{key}"] = result['stdout'].strip()
            
            # Check Spotlight status
            spotlight_result = self._run_command(['mdutil', '-s', '/'])
            if spotlight_result['success']:
                restore_point['settings']['spotlight_status'] = spotlight_result['stdout'].strip()
            
            # Check running services
            services_to_check = ['photoanalysisd', 'mediaanalysisd']
            for service in services_to_check:
                result = self._run_command(['pgrep', '-x', service])
                restore_point['settings'][f'{service}_running'] = result['success']
            
            # Get current Ollama environment
            ollama_env = {}
            for var in ['OLLAMA_NUM_PARALLEL', 'OLLAMA_MAX_LOADED_MODELS', 'OLLAMA_KEEP_ALIVE', 'OLLAMA_NUM_CTX']:
                value = os.getenv(var)
                if value:
                    ollama_env[var] = value
            restore_point['settings']['ollama_env'] = ollama_env
            
            # Save restore point
            restore_points = []
            if os.path.exists(self.restore_points_file):
                with open(self.restore_points_file, 'r') as f:
                    restore_points = json.load(f)
            
            restore_points.append(restore_point)
            
            # Keep only last 10 restore points
            restore_points = restore_points[-10:]
            
            with open(self.restore_points_file, 'w') as f:
                json.dump(restore_points, f, indent=2)
            
            # Create a detailed backup file
            backup_file = os.path.join(self.backup_dir, f"restore_{restore_point['id']}.json")
            with open(backup_file, 'w') as f:
                json.dump(restore_point, f, indent=2)
            
            restore_point['backup_file'] = backup_file
            logger.info(f"Restore point created: {restore_point['id']}")
        
        except Exception as e:
            logger.error(f"Failed to create restore point: {e}")
            restore_point['success'] = False
            restore_point['error'] = str(e)
        
        return restore_point
    
    def list_restore_points(self) -> List[Dict]:
        """List all available restore points.
        
        Returns:
            List of restore point dictionaries
        """
        if not os.path.exists(self.restore_points_file):
            return []
        
        try:
            with open(self.restore_points_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to list restore points: {e}")
            return []
    
    def restore_from_point(self, restore_point_id: str) -> Dict:
        """Restore system to a previous restore point.
        
        Args:
            restore_point_id: ID of the restore point to restore from
        
        Returns:
            Dict with restoration results
        """
        logger.info(f"Restoring from restore point: {restore_point_id}")
        
        results = {
            "success": True,
            "restore_point_id": restore_point_id,
            "restored_settings": [],
            "failed_settings": []
        }
        
        try:
            # Find the restore point
            restore_points = self.list_restore_points()
            restore_point = None
            
            for rp in restore_points:
                if rp['id'] == restore_point_id:
                    restore_point = rp
                    break
            
            if not restore_point:
                results['success'] = False
                results['error'] = f"Restore point {restore_point_id} not found"
                return results
            
            settings = restore_point.get('settings', {})
            
            # Restore defaults settings
            for key, value in settings.items():
                if '.' in key and not key.endswith('_running') and key != 'ollama_env' and key != 'spotlight_status':
                    domain, setting = key.rsplit('.', 1)
                    
                    # Determine the type and restore
                    if value.lower() in ['true', 'false', '1', '0']:
                        bool_value = value.lower() in ['true', '1']
                        result = self._run_command([
                            'defaults', 'write', domain, setting, '-bool', str(bool_value).lower()
                        ])
                    else:
                        result = self._run_command([
                            'defaults', 'write', domain, setting, value
                        ])
                    
                    if result['success']:
                        results['restored_settings'].append(key)
                    else:
                        results['failed_settings'].append(key)
            
            # Restore Spotlight status
            if 'spotlight_status' in settings:
                if 'disabled' in settings['spotlight_status'].lower():
                    self._run_command(['sudo', 'mdutil', '-i', 'off', '/'])
                else:
                    self._run_command(['sudo', 'mdutil', '-i', 'on', '/'])
                results['restored_settings'].append('spotlight')
            
            # Restore Ollama environment
            if 'ollama_env' in settings:
                for var, value in settings['ollama_env'].items():
                    self._run_command(['launchctl', 'setenv', var, value])
                    os.environ[var] = value
                results['restored_settings'].append('ollama_environment')
            
            # Restart affected services
            self._run_command(['killall', 'Dock'])
            self._run_command(['killall', 'Finder'])
            
            logger.info(f"Restored {len(results['restored_settings'])} settings")
        
        except Exception as e:
            logger.error(f"Restoration failed: {e}")
            results['success'] = False
            results['error'] = str(e)
        
        return results
    
    def validate_optimization_level(self, level: str, ram_gb: int) -> Tuple[bool, List[str]]:
        """Validate if an optimization level is safe for the system.
        
        Args:
            level: Optimization level (conservative, moderate, aggressive)
            ram_gb: System RAM in GB
        
        Returns:
            Tuple of (is_safe, list_of_warnings)
        """
        warnings = []
        is_safe = True
        
        # Check RAM constraints
        if ram_gb == 8 and level == 'aggressive':
            warnings.append(
                "Aggressive optimization on 8GB RAM may impact system stability. "
                "Ensure no other applications are running."
            )
        
        # Check current memory usage
        mem = psutil.virtual_memory()
        if mem.percent > 80 and level in ['moderate', 'aggressive']:
            warnings.append(
                f"Current memory usage is {mem.percent}%. "
                "Close applications before applying optimizations."
            )
        
        # Check disk space
        disk = psutil.disk_usage('/')
        if disk.percent > 90:
            warnings.append(
                f"Disk usage is {disk.percent}%. Free up space before proceeding."
            )
            if disk.percent > 95:
                is_safe = False
        
        return is_safe, warnings
    
    def emergency_restore(self) -> Dict:
        """Emergency restore to safe defaults.
        
        Returns:
            Dict with restoration results
        """
        logger.warning("Performing emergency restore to safe defaults")
        
        results = {
            "success": True,
            "actions": []
        }
        
        try:
            # Restore UI settings to defaults
            ui_commands = [
                ['defaults', 'delete', 'com.apple.universalaccess', 'reduceTransparency'],
                ['defaults', 'delete', 'NSGlobalDomain', 'NSAutomaticWindowAnimationsEnabled'],
                ['defaults', 'delete', 'NSGlobalDomain', 'NSWindowResizeTime'],
                ['defaults', 'delete', 'NSGlobalDomain', 'NSAppSleepDisabled'],
                ['defaults', 'delete', 'com.apple.finder', 'DisableAllAnimations'],
                ['defaults', 'delete', 'com.apple.dock', 'launchanim'],
            ]
            
            for cmd in ui_commands:
                self._run_command(cmd)
            results['actions'].append('UI settings restored to defaults')
            
            # Re-enable Spotlight
            self._run_command(['sudo', 'mdutil', '-i', 'on', '/'])
            results['actions'].append('Spotlight re-enabled')
            
            # Reset Ollama environment to safe defaults
            safe_ollama_env = {
                'OLLAMA_NUM_PARALLEL': '1',
                'OLLAMA_MAX_LOADED_MODELS': '1',
                'OLLAMA_KEEP_ALIVE': '5m',
                'OLLAMA_NUM_CTX': '2048'
            }
            
            for var, value in safe_ollama_env.items():
                self._run_command(['launchctl', 'setenv', var, value])
            results['actions'].append('Ollama environment reset to safe defaults')
            
            # Restart services
            self._run_command(['killall', 'Dock'])
            self._run_command(['killall', 'Finder'])
            results['actions'].append('System services restarted')
            
            logger.info("Emergency restore completed")
        
        except Exception as e:
            logger.error(f"Emergency restore failed: {e}")
            results['success'] = False
            results['error'] = str(e)
        
        return results
    
    def verify_system_health(self) -> Dict:
        """Verify system health after optimizations.
        
        Returns:
            Dict with health check results
        """
        logger.info("Verifying system health")
        
        health = {
            "timestamp": datetime.now().isoformat(),
            "healthy": True,
            "issues": [],
            "metrics": {}
        }
        
        try:
            # Check memory
            mem = psutil.virtual_memory()
            health['metrics']['memory_percent'] = mem.percent
            
            if mem.percent > 95:
                health['healthy'] = False
                health['issues'].append("Critical: Memory usage > 95%")
            elif mem.percent > 85:
                health['issues'].append("Warning: Memory usage > 85%")
            
            # Check swap
            swap = psutil.swap_memory()
            health['metrics']['swap_percent'] = swap.percent
            
            if swap.percent > 75:
                health['healthy'] = False
                health['issues'].append("Critical: Swap usage > 75%")
            elif swap.percent > 50:
                health['issues'].append("Warning: Swap usage > 50%")
            
            # Check CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            health['metrics']['cpu_percent'] = cpu_percent
            
            if cpu_percent > 95:
                health['issues'].append("Warning: CPU usage > 95%")
            
            # Check disk
            disk = psutil.disk_usage('/')
            health['metrics']['disk_percent'] = disk.percent
            
            if disk.percent > 95:
                health['healthy'] = False
                health['issues'].append("Critical: Disk usage > 95%")
            
            # Check if Ollama is responsive
            ollama_check = self._run_command(['pgrep', '-x', 'ollama'])
            health['metrics']['ollama_running'] = ollama_check['success']
            
            if not health['issues']:
                health['message'] = "System is healthy"
            else:
                health['message'] = f"Found {len(health['issues'])} issue(s)"
            
            logger.info(f"Health check completed. Healthy: {health['healthy']}")
        
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            health['healthy'] = False
            health['issues'].append(f"Health check error: {str(e)}")
        
        return health
