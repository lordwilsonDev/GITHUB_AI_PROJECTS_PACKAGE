#!/usr/bin/env python3
"""
OS Optimizer Module
Advanced macOS system optimizations for M1 LLM inference
"""

import subprocess
import os
import json
from pathlib import Path
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class AdvancedOSOptimizer:
    """Advanced OS-level optimizations based on level33 architecture"""
    
    def __init__(self, dry_run=False, backup_dir=None):
        self.dry_run = dry_run
        self.backup_dir = backup_dir or Path.home() / '.m1_optimizer_backups'
        self.backup_dir.mkdir(exist_ok=True)
        self.changes_log = []
        
    def create_full_backup(self) -> Path:
        """Create comprehensive backup of all settings"""
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f'backup_{timestamp}.json'
        
        backup_data = {
            'timestamp': timestamp,
            'defaults': self._backup_defaults(),
            'launchctl': self._backup_launchctl_state(),
            'spotlight': self._backup_spotlight_state(),
        }
        
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
            
        logger.info(f"Full backup created: {backup_file}")
        return backup_file
    
    def _backup_defaults(self) -> Dict:
        """Backup macOS defaults settings"""
        settings = {}
        
        defaults_to_backup = [
            ('NSGlobalDomain', 'NSAutomaticWindowAnimationsEnabled'),
            ('NSGlobalDomain', 'NSWindowResizeTime'),
            ('NSGlobalDomain', 'NSAppSleepDisabled'),
            ('com.apple.finder', 'DisableAllAnimations'),
            ('com.apple.dock', 'launchanim'),
            ('com.apple.dock', 'expose-animation-duration'),
            ('com.apple.universalaccess', 'reduceTransparency'),
            ('com.apple.dock', 'autohide'),
            ('com.apple.dock', 'autohide-delay'),
        ]
        
        for domain, key in defaults_to_backup:
            try:
                result = subprocess.run(
                    ['defaults', 'read', domain, key],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    settings[f"{domain}.{key}"] = result.stdout.strip()
            except Exception as e:
                logger.debug(f"Could not backup {domain}.{key}: {e}")
                
        return settings
    
    def _backup_launchctl_state(self) -> Dict:
        """Backup launchctl service states"""
        services = {}
        
        services_to_check = [
            'com.apple.photoanalysisd',
            'com.apple.mediaanalysisd',
        ]
        
        uid = os.getuid()
        for service in services_to_check:
            try:
                result = subprocess.run(
                    ['launchctl', 'print', f'user/{uid}/{service}'],
                    capture_output=True, text=True
                )
                services[service] = {
                    'exists': result.returncode == 0,
                    'output': result.stdout if result.returncode == 0 else None
                }
            except Exception as e:
                logger.debug(f"Could not check service {service}: {e}")
                
        return services
    
    def _backup_spotlight_state(self) -> Dict:
        """Backup Spotlight indexing state"""
        try:
            result = subprocess.run(
                ['mdutil', '-s', '/'],
                capture_output=True, text=True
            )
            return {
                'status': result.stdout.strip(),
                'enabled': 'Indexing enabled' in result.stdout
            }
        except Exception as e:
            logger.debug(f"Could not backup Spotlight state: {e}")
            return {}
    
    def optimize_windowserver(self, level='moderate') -> List[str]:
        """Optimize WindowServer and UI rendering
        
        Args:
            level: 'minimal', 'moderate', or 'aggressive'
        """
        changes = []
        
        commands = []
        
        if level in ['moderate', 'aggressive']:
            # Reduce transparency
            commands.append((
                ['defaults', 'write', 'com.apple.universalaccess', 'reduceTransparency', '-bool', 'true'],
                'Enable Reduce Transparency'
            ))
            
            # Disable window animations
            commands.append((
                ['defaults', 'write', 'NSGlobalDomain', 'NSAutomaticWindowAnimationsEnabled', '-bool', 'false'],
                'Disable window animations'
            ))
            
            # Accelerate window resize
            commands.append((
                ['defaults', 'write', 'NSGlobalDomain', 'NSWindowResizeTime', '-float', '0.001'],
                'Accelerate window resize'
            ))
        
        if level == 'aggressive':
            # Disable Finder animations
            commands.append((
                ['defaults', 'write', 'com.apple.finder', 'DisableAllAnimations', '-bool', 'true'],
                'Disable Finder animations'
            ))
            
            # Disable Dock animations
            commands.append((
                ['defaults', 'write', 'com.apple.dock', 'launchanim', '-bool', 'false'],
                'Disable Dock launch animations'
            ))
            
            # Disable Mission Control animations
            commands.append((
                ['defaults', 'write', 'com.apple.dock', 'expose-animation-duration', '-float', '0'],
                'Disable Mission Control animations'
            ))
            
            # Auto-hide Dock with no delay
            commands.append((
                ['defaults', 'write', 'com.apple.dock', 'autohide', '-bool', 'true'],
                'Enable Dock auto-hide'
            ))
            
            commands.append((
                ['defaults', 'write', 'com.apple.dock', 'autohide-delay', '-float', '0'],
                'Remove Dock auto-hide delay'
            ))
        
        for cmd, description in commands:
            if self._execute_command(cmd, description):
                changes.append(description)
        
        # Restart affected services
        if changes and not self.dry_run:
            subprocess.run(['killall', 'Dock'], capture_output=True)
            subprocess.run(['killall', 'Finder'], capture_output=True)
            logger.info("Restarted Dock and Finder")
        
        return changes
    
    def manage_spotlight(self, action='disable') -> bool:
        """Manage Spotlight indexing
        
        Args:
            action: 'disable', 'enable', or 'status'
        """
        if action == 'status':
            result = subprocess.run(
                ['mdutil', '-s', '/'],
                capture_output=True, text=True
            )
            logger.info(f"Spotlight status: {result.stdout.strip()}")
            return True
        
        if action == 'disable':
            logger.warning("Disabling Spotlight requires sudo privileges")
            if self.dry_run:
                logger.info("[DRY RUN] Would disable Spotlight indexing")
                return True
            
            # This requires sudo, so we'll provide instructions
            logger.info("To disable Spotlight, run: sudo mdutil -i off /")
            return False
        
        if action == 'enable':
            logger.info("To enable Spotlight, run: sudo mdutil -i on /")
            return False
        
        return False
    
    def manage_background_services(self, aggressive=False) -> List[str]:
        """Manage resource-intensive background services"""
        changes = []
        uid = os.getuid()
        
        services_to_disable = []
        
        if aggressive:
            services_to_disable = [
                ('com.apple.photoanalysisd', 'Photo Analysis'),
                ('com.apple.mediaanalysisd', 'Media Analysis'),
            ]
        
        for service, name in services_to_disable:
            cmd = ['launchctl', 'disable', f'user/{uid}/{service}']
            if self._execute_command(cmd, f'Disable {name}'):
                changes.append(f'Disabled {name}')
        
        return changes
    
    def disable_app_nap(self) -> bool:
        """Disable App Nap globally"""
        cmd = ['defaults', 'write', 'NSGlobalDomain', 'NSAppSleepDisabled', '-bool', 'YES']
        return self._execute_command(cmd, 'Disable App Nap globally')
    
    def optimize_energy_settings(self) -> List[str]:
        """Optimize energy settings for performance"""
        changes = []
        
        # Note: pmset requires sudo, so we provide instructions
        recommendations = [
            "sudo pmset -a sleep 0  # Disable sleep",
            "sudo pmset -a disksleep 0  # Disable disk sleep",
            "sudo pmset -a displaysleep 15  # Display sleep after 15 min",
            "sudo pmset -a powernap 0  # Disable Power Nap",
        ]
        
        logger.info("Energy optimization requires sudo. Recommended commands:")
        for rec in recommendations:
            logger.info(f"  {rec}")
        
        return recommendations
    
    def create_caffeinate_wrapper(self, output_path: Path) -> bool:
        """Create a caffeinate wrapper script for long-running tasks"""
        script_content = """#!/bin/bash
# Caffeinate Wrapper for LLM Inference
# Prevents system sleep during inference tasks

if [ $# -eq 0 ]; then
    echo "Usage: $0 <command> [args...]"
    echo "Example: $0 python my_llm_script.py"
    exit 1
fi

echo "Running with caffeinate to prevent sleep..."
caffeinate -i "$@"
"""
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create caffeinate wrapper at {output_path}")
            return True
        
        try:
            with open(output_path, 'w') as f:
                f.write(script_content)
            os.chmod(output_path, 0o755)
            logger.info(f"Created caffeinate wrapper: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create caffeinate wrapper: {e}")
            return False
    
    def _execute_command(self, cmd: List[str], description: str) -> bool:
        """Execute a system command with logging"""
        if self.dry_run:
            logger.info(f"[DRY RUN] {description}: {' '.join(cmd)}")
            self.changes_log.append(f"[DRY RUN] {description}")
            return True
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"✓ {description}")
            self.changes_log.append(description)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Failed: {description} - {e.stderr}")
            return False
    
    def restore_from_backup(self, backup_file: Path) -> bool:
        """Restore settings from a backup file"""
        try:
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            logger.info(f"Restoring from backup: {backup_file}")
            
            # Restore defaults
            for key, value in backup_data.get('defaults', {}).items():
                domain, setting = key.rsplit('.', 1)
                # Determine type and restore
                if value.lower() in ['true', 'false', '1', '0']:
                    bool_val = value.lower() in ['true', '1']
                    cmd = ['defaults', 'write', domain, setting, '-bool', str(bool_val).lower()]
                else:
                    cmd = ['defaults', 'write', domain, setting, value]
                
                self._execute_command(cmd, f'Restore {key}')
            
            logger.info("Restore complete. Restart Dock and Finder for changes to take effect.")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return False
    
    def generate_optimization_report(self) -> str:
        """Generate a report of all changes made"""
        report = "\n" + "="*70 + "\n"
        report += "OS OPTIMIZATION REPORT\n"
        report += "="*70 + "\n\n"
        
        if self.changes_log:
            report += "Changes Applied:\n"
            for i, change in enumerate(self.changes_log, 1):
                report += f"  {i}. {change}\n"
        else:
            report += "No changes applied.\n"
        
        report += "\n" + "="*70 + "\n"
        return report
