#!/usr/bin/env python3
"""
Rollback and Restore Utilities
Provides functionality to restore system to pre-optimization state
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SystemRestorer:
    """Restores system settings from backups"""
    
    def __init__(self, backup_dir: Optional[Path] = None):
        self.backup_dir = backup_dir or Path.home() / '.m1_optimizer_backups'
        self.backup_dir.mkdir(exist_ok=True)
        
    def list_backups(self) -> List[Path]:
        """List all available backups"""
        backups = sorted(self.backup_dir.glob('backup_*.json'), reverse=True)
        return backups
    
    def get_latest_backup(self) -> Optional[Path]:
        """Get the most recent backup"""
        backups = self.list_backups()
        return backups[0] if backups else None
    
    def load_backup(self, backup_path: Path) -> Dict:
        """Load backup data from file"""
        try:
            with open(backup_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load backup: {e}")
            return {}
    
    def restore_defaults(self, backup_data: Dict, dry_run=False) -> List[str]:
        """Restore macOS defaults from backup"""
        restored = []
        defaults = backup_data.get('defaults', {})
        
        for key, value in defaults.items():
            domain, setting = key.rsplit('.', 1)
            
            # Determine the type and construct command
            if value.lower() in ['true', 'false', '1', '0']:
                bool_val = value.lower() in ['true', '1']
                cmd = ['defaults', 'write', domain, setting, '-bool', str(bool_val).lower()]
            elif value.replace('.', '').replace('-', '').isdigit():
                # Numeric value
                if '.' in value:
                    cmd = ['defaults', 'write', domain, setting, '-float', value]
                else:
                    cmd = ['defaults', 'write', domain, setting, '-int', value]
            else:
                cmd = ['defaults', 'write', domain, setting, value]
            
            if dry_run:
                logger.info(f"[DRY RUN] Would restore {key} to {value}")
                restored.append(key)
            else:
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    logger.info(f"✓ Restored {key}")
                    restored.append(key)
                except subprocess.CalledProcessError as e:
                    logger.error(f"✗ Failed to restore {key}: {e}")
        
        return restored
    
    def restore_spotlight(self, backup_data: Dict, dry_run=False) -> bool:
        """Restore Spotlight indexing state"""
        spotlight = backup_data.get('spotlight', {})
        
        if not spotlight:
            logger.warning("No Spotlight backup data found")
            return False
        
        was_enabled = spotlight.get('enabled', True)
        
        if dry_run:
            logger.info(f"[DRY RUN] Would restore Spotlight to: {'enabled' if was_enabled else 'disabled'}")
            return True
        
        if was_enabled:
            logger.info("Restoring Spotlight requires sudo: sudo mdutil -i on /")
            return False
        else:
            logger.info("Spotlight was disabled in backup, no action needed")
            return True
    
    def restore_launchctl_services(self, backup_data: Dict, dry_run=False) -> List[str]:
        """Restore launchctl service states"""
        restored = []
        services = backup_data.get('launchctl', {})
        
        import os
        uid = os.getuid()
        
        for service, state in services.items():
            if state.get('exists'):
                # Service existed, try to enable it
                cmd = ['launchctl', 'enable', f'user/{uid}/{service}']
                
                if dry_run:
                    logger.info(f"[DRY RUN] Would enable service {service}")
                    restored.append(service)
                else:
                    try:
                        subprocess.run(cmd, check=True, capture_output=True)
                        logger.info(f"✓ Enabled service {service}")
                        restored.append(service)
                    except subprocess.CalledProcessError as e:
                        logger.error(f"✗ Failed to enable {service}: {e}")
        
        return restored
    
    def full_restore(self, backup_path: Optional[Path] = None, dry_run=False) -> Dict:
        """Perform full system restore"""
        if backup_path is None:
            backup_path = self.get_latest_backup()
        
        if backup_path is None:
            logger.error("No backup found")
            return {'error': 'No backup available'}
        
        logger.info(f"Restoring from: {backup_path}")
        backup_data = self.load_backup(backup_path)
        
        if not backup_data:
            return {'error': 'Failed to load backup'}
        
        results = {
            'backup_file': str(backup_path),
            'timestamp': backup_data.get('timestamp'),
            'defaults_restored': self.restore_defaults(backup_data, dry_run),
            'services_restored': self.restore_launchctl_services(backup_data, dry_run),
        }
        
        # Restart affected services
        if not dry_run and results['defaults_restored']:
            logger.info("Restarting Dock and Finder...")
            subprocess.run(['killall', 'Dock'], capture_output=True)
            subprocess.run(['killall', 'Finder'], capture_output=True)
        
        return results
    
    def print_restore_report(self, results: Dict):
        """Print formatted restore report"""
        print("\n" + "="*70)
        print("SYSTEM RESTORE REPORT")
        print("="*70)
        
        print(f"\nBackup File: {results.get('backup_file')}")
        print(f"Backup Timestamp: {results.get('timestamp')}")
        
        defaults = results.get('defaults_restored', [])
        print(f"\nDefaults Restored: {len(defaults)}")
        for item in defaults[:10]:  # Show first 10
            print(f"  ✓ {item}")
        if len(defaults) > 10:
            print(f"  ... and {len(defaults) - 10} more")
        
        services = results.get('services_restored', [])
        if services:
            print(f"\nServices Restored: {len(services)}")
            for service in services:
                print(f"  ✓ {service}")
        
        print("\n" + "="*70)
        print("\nRestore complete. You may need to restart your system for all changes to take effect.")
        print("="*70 + "\n")


class OllamaRestorer:
    """Restores Ollama configuration"""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
    
    def clear_environment_variables(self) -> List[str]:
        """Clear Ollama environment variables"""
        cleared = []
        env_vars = [
            'OLLAMA_NUM_PARALLEL',
            'OLLAMA_MAX_LOADED_MODELS',
            'OLLAMA_KEEP_ALIVE',
            'OLLAMA_MAX_QUEUE',
            'OLLAMA_FLASH_ATTENTION',
        ]
        
        for var in env_vars:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would unset {var}")
                cleared.append(var)
            else:
                try:
                    subprocess.run(
                        ['launchctl', 'unsetenv', var],
                        check=True, capture_output=True
                    )
                    logger.info(f"✓ Unset {var}")
                    cleared.append(var)
                except subprocess.CalledProcessError as e:
                    logger.error(f"✗ Failed to unset {var}: {e}")
        
        return cleared
    
    def restart_ollama(self) -> bool:
        """Restart Ollama service"""
        if self.dry_run:
            logger.info("[DRY RUN] Would restart Ollama")
            return True
        
        try:
            # Stop Ollama
            subprocess.run(['pkill', '-x', 'ollama'], capture_output=True)
            logger.info("Stopped Ollama")
            
            # Wait a moment
            import time
            time.sleep(2)
            
            # Start Ollama
            subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info("Started Ollama")
            
            return True
        except Exception as e:
            logger.error(f"Failed to restart Ollama: {e}")
            return False


def main():
    """Main rollback utility"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rollback M1 optimizations')
    parser.add_argument('--list-backups', action='store_true', help='List available backups')
    parser.add_argument('--restore', metavar='BACKUP_FILE', help='Restore from specific backup')
    parser.add_argument('--restore-latest', action='store_true', help='Restore from latest backup')
    parser.add_argument('--clear-ollama', action='store_true', help='Clear Ollama environment variables')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    restorer = SystemRestorer()
    
    if args.list_backups:
        backups = restorer.list_backups()
        print("\nAvailable Backups:")
        print("="*70)
        for i, backup in enumerate(backups, 1):
            print(f"{i}. {backup.name}")
        print()
        return
    
    if args.restore_latest:
        results = restorer.full_restore(dry_run=args.dry_run)
        restorer.print_restore_report(results)
        return
    
    if args.restore:
        backup_path = Path(args.restore)
        if not backup_path.exists():
            print(f"Error: Backup file not found: {backup_path}")
            return
        results = restorer.full_restore(backup_path, dry_run=args.dry_run)
        restorer.print_restore_report(results)
        return
    
    if args.clear_ollama:
        ollama_restorer = OllamaRestorer(dry_run=args.dry_run)
        cleared = ollama_restorer.clear_environment_variables()
        print(f"\nCleared {len(cleared)} Ollama environment variables")
        if not args.dry_run:
            ollama_restorer.restart_ollama()
        return
    
    parser.print_help()


if __name__ == '__main__':
    main()
