#!/usr/bin/env python3
"""
M1 LLM Optimization Agent
Based on level33 High-Performance Architecture for Local LLM Inference

This agent systematically optimizes macOS M1 systems for peak local LLM performance
by managing OS resources, configuring Ollama, and optimizing the Python environment.
"""

import os
import sys
import subprocess
import json
import argparse
import platform
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('m1_optimizer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class M1SystemAnalyzer:
    """Analyzes M1 system configuration and constraints"""
    
    def __init__(self):
        self.system_info = {}
        self.ram_gb = 0
        self.chip_type = ""
        self.is_m1 = False
        
    def analyze(self) -> Dict:
        """Perform comprehensive system analysis"""
        logger.info("Starting system analysis...")
        
        # Check if running on macOS
        if platform.system() != 'Darwin':
            logger.error("This optimizer is designed for macOS only")
            sys.exit(1)
            
        # Get chip information
        self._get_chip_info()
        
        # Get memory information
        self._get_memory_info()
        
        # Check Ollama installation
        self._check_ollama()
        
        # Check Python environment
        self._check_python_env()
        
        # Analyze current resource usage
        self._analyze_resource_usage()
        
        return self.system_info
    
    def _get_chip_info(self):
        """Detect Apple Silicon chip type"""
        try:
            result = subprocess.run(
                ['sysctl', '-n', 'machdep.cpu.brand_string'],
                capture_output=True, text=True, check=True
            )
            chip_name = result.stdout.strip()
            self.chip_type = chip_name
            self.is_m1 = 'M1' in chip_name or 'M2' in chip_name or 'M3' in chip_name
            self.system_info['chip'] = chip_name
            logger.info(f"Detected chip: {chip_name}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to detect chip: {e}")
            
    def _get_memory_info(self):
        """Get total system RAM"""
        try:
            result = subprocess.run(
                ['sysctl', '-n', 'hw.memsize'],
                capture_output=True, text=True, check=True
            )
            mem_bytes = int(result.stdout.strip())
            self.ram_gb = mem_bytes / (1024**3)
            self.system_info['ram_gb'] = round(self.ram_gb, 1)
            logger.info(f"Total RAM: {self.ram_gb:.1f} GB")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get memory info: {e}")
            
    def _check_ollama(self):
        """Check if Ollama is installed"""
        try:
            result = subprocess.run(
                ['which', 'ollama'],
                capture_output=True, text=True
            )
            ollama_installed = result.returncode == 0
            self.system_info['ollama_installed'] = ollama_installed
            
            if ollama_installed:
                # Get Ollama version
                version_result = subprocess.run(
                    ['ollama', '--version'],
                    capture_output=True, text=True
                )
                self.system_info['ollama_version'] = version_result.stdout.strip()
                logger.info(f"Ollama detected: {version_result.stdout.strip()}")
            else:
                logger.warning("Ollama not found in PATH")
        except Exception as e:
            logger.error(f"Error checking Ollama: {e}")
            self.system_info['ollama_installed'] = False
            
    def _check_python_env(self):
        """Check Python environment and key packages"""
        self.system_info['python_version'] = sys.version
        
        # Check for uv
        try:
            result = subprocess.run(
                ['which', 'uv'],
                capture_output=True, text=True
            )
            self.system_info['uv_installed'] = result.returncode == 0
        except:
            self.system_info['uv_installed'] = False
            
        # Check for PyTorch MPS support
        try:
            import torch
            self.system_info['pytorch_installed'] = True
            self.system_info['mps_available'] = torch.backends.mps.is_available()
        except ImportError:
            self.system_info['pytorch_installed'] = False
            self.system_info['mps_available'] = False
            
        # Check for MLX
        try:
            import mlx
            self.system_info['mlx_installed'] = True
        except ImportError:
            self.system_info['mlx_installed'] = False
            
    def _analyze_resource_usage(self):
        """Analyze current resource usage"""
        try:
            # Get memory pressure
            result = subprocess.run(
                ['memory_pressure'],
                capture_output=True, text=True, timeout=5
            )
            self.system_info['memory_pressure'] = result.stdout
            
            # Check for resource-heavy processes
            ps_result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True, text=True
            )
            
            # Look for known resource hogs
            resource_hogs = []
            for line in ps_result.stdout.split('\n'):
                if any(proc in line.lower() for proc in 
                       ['photoanalysisd', 'mediaanalysisd', 'mds_stores', 'mdworker']):
                    resource_hogs.append(line.split()[10] if len(line.split()) > 10 else 'unknown')
                    
            self.system_info['resource_hogs'] = list(set(resource_hogs))
            
        except Exception as e:
            logger.warning(f"Could not analyze resource usage: {e}")


class OSOptimizer:
    """Handles macOS system-level optimizations"""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.backup_file = Path.home() / '.m1_optimizer_backup.json'
        self.changes_made = []
        
    def optimize(self, aggressive=False):
        """Apply OS-level optimizations"""
        logger.info("Starting OS optimizations...")
        
        # Backup current settings
        self._backup_settings()
        
        # Reduce WindowServer load
        self._optimize_windowserver()
        
        # Manage Spotlight
        if aggressive:
            self._disable_spotlight()
        
        # Disable animations
        self._disable_animations()
        
        # Manage background daemons
        self._manage_background_daemons(aggressive)
        
        # Disable App Nap
        self._disable_app_nap()
        
        logger.info(f"OS optimizations complete. Changes made: {len(self.changes_made)}")
        return self.changes_made
    
    def _backup_settings(self):
        """Backup current system settings"""
        backup = {
            'timestamp': subprocess.run(['date'], capture_output=True, text=True).stdout.strip(),
            'settings': {}
        }
        
        # Backup key defaults
        settings_to_backup = [
            ('NSGlobalDomain', 'NSAutomaticWindowAnimationsEnabled'),
            ('NSGlobalDomain', 'NSWindowResizeTime'),
            ('com.apple.finder', 'DisableAllAnimations'),
            ('com.apple.dock', 'launchanim'),
            ('NSGlobalDomain', 'NSAppSleepDisabled'),
        ]
        
        for domain, key in settings_to_backup:
            try:
                result = subprocess.run(
                    ['defaults', 'read', domain, key],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    backup['settings'][f"{domain}.{key}"] = result.stdout.strip()
            except:
                pass
                
        with open(self.backup_file, 'w') as f:
            json.dump(backup, f, indent=2)
        logger.info(f"Settings backed up to {self.backup_file}")
    
    def _optimize_windowserver(self):
        """Reduce WindowServer resource consumption"""
        logger.info("Optimizing WindowServer...")
        
        # Enable Reduce Transparency
        cmd = ['defaults', 'write', 'com.apple.universalaccess', 'reduceTransparency', '-bool', 'true']
        self._execute_command(cmd, "Enable Reduce Transparency")
        
    def _disable_animations(self):
        """Disable system animations"""
        logger.info("Disabling animations...")
        
        commands = [
            (['defaults', 'write', 'NSGlobalDomain', 'NSAutomaticWindowAnimationsEnabled', '-bool', 'false'],
             "Disable window animations"),
            (['defaults', 'write', 'NSGlobalDomain', 'NSWindowResizeTime', '-float', '0.001'],
             "Accelerate window resize"),
            (['defaults', 'write', 'com.apple.finder', 'DisableAllAnimations', '-bool', 'true'],
             "Disable Finder animations"),
            (['defaults', 'write', 'com.apple.dock', 'launchanim', '-bool', 'false'],
             "Disable Dock animations"),
            (['defaults', 'write', 'com.apple.dock', 'expose-animation-duration', '-float', '0'],
             "Disable Mission Control animations"),
        ]
        
        for cmd, desc in commands:
            self._execute_command(cmd, desc)
            
        # Restart Dock and Finder to apply changes
        if not self.dry_run:
            subprocess.run(['killall', 'Dock'], capture_output=True)
            subprocess.run(['killall', 'Finder'], capture_output=True)
            logger.info("Restarted Dock and Finder")
    
    def _disable_spotlight(self):
        """Disable Spotlight indexing"""
        logger.info("Disabling Spotlight indexing...")
        cmd = ['sudo', 'mdutil', '-i', 'off', '/']
        self._execute_command(cmd, "Disable Spotlight indexing", requires_sudo=True)
    
    def _manage_background_daemons(self, aggressive=False):
        """Manage resource-heavy background processes"""
        logger.info("Managing background daemons...")
        
        if aggressive:
            # Disable photoanalysisd
            uid = os.getuid()
            cmd = ['launchctl', 'disable', f'user/{uid}/com.apple.photoanalysisd']
            self._execute_command(cmd, "Disable photoanalysisd")
    
    def _disable_app_nap(self):
        """Disable App Nap globally"""
        logger.info("Disabling App Nap...")
        cmd = ['defaults', 'write', 'NSGlobalDomain', 'NSAppSleepDisabled', '-bool', 'YES']
        self._execute_command(cmd, "Disable App Nap")
    
    def _execute_command(self, cmd: List[str], description: str, requires_sudo=False):
        """Execute a system command"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would execute: {' '.join(cmd)}")
            return
            
        try:
            if requires_sudo:
                logger.warning(f"Command requires sudo: {description}")
                logger.warning("Please run this script with sudo for full functionality")
                return
                
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"✓ {description}")
            self.changes_made.append(description)
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Failed: {description} - {e.stderr}")


class OllamaOptimizer:
    """Optimizes Ollama configuration for M1 systems"""
    
    def __init__(self, ram_gb: float, dry_run=False):
        self.ram_gb = ram_gb
        self.dry_run = dry_run
        self.env_vars = {}
        
    def optimize(self) -> Dict[str, str]:
        """Generate optimal Ollama environment variables"""
        logger.info("Optimizing Ollama configuration...")
        
        # Determine optimal settings based on RAM
        if self.ram_gb <= 8:
            self.env_vars = {
                'OLLAMA_NUM_PARALLEL': '1',
                'OLLAMA_MAX_LOADED_MODELS': '1',
                'OLLAMA_KEEP_ALIVE': '5m',
            }
            logger.info("Configured for 8GB RAM (conservative)")
        elif self.ram_gb <= 16:
            self.env_vars = {
                'OLLAMA_NUM_PARALLEL': '1',
                'OLLAMA_MAX_LOADED_MODELS': '1',
                'OLLAMA_KEEP_ALIVE': '10m',
            }
            logger.info("Configured for 16GB RAM (balanced)")
        else:
            self.env_vars = {
                'OLLAMA_NUM_PARALLEL': '2',
                'OLLAMA_MAX_LOADED_MODELS': '2',
                'OLLAMA_KEEP_ALIVE': '15m',
            }
            logger.info("Configured for >16GB RAM (performance)")
            
        return self.env_vars
    
    def apply_configuration(self):
        """Apply Ollama environment variables"""
        if self.dry_run:
            logger.info("[DRY RUN] Would set Ollama environment variables:")
            for key, value in self.env_vars.items():
                logger.info(f"  {key}={value}")
            return
            
        logger.info("Applying Ollama configuration...")
        
        for key, value in self.env_vars.items():
            try:
                subprocess.run(
                    ['launchctl', 'setenv', key, value],
                    check=True, capture_output=True
                )
                logger.info(f"✓ Set {key}={value}")
            except subprocess.CalledProcessError as e:
                logger.error(f"✗ Failed to set {key}: {e}")
    
    def generate_startup_script(self, output_path: Path):
        """Generate a startup script for Ollama with optimizations"""
        script_content = f"""#!/bin/bash
# M1 Ollama Optimization Startup Script
# Generated by M1 LLM Optimizer

# Set environment variables
{chr(10).join([f'export {k}="{v}"' for k, v in self.env_vars.items()])}

# Start Ollama server
echo "Starting Ollama with optimized settings..."
ollama serve
"""
        
        if not self.dry_run:
            with open(output_path, 'w') as f:
                f.write(script_content)
            os.chmod(output_path, 0o755)
            logger.info(f"✓ Generated startup script: {output_path}")
        else:
            logger.info(f"[DRY RUN] Would generate startup script at {output_path}")


class ModelRecommender:
    """Recommends optimal models based on system constraints"""
    
    def __init__(self, ram_gb: float):
        self.ram_gb = ram_gb
        self.recommendations = []
        
    def get_recommendations(self) -> List[Dict]:
        """Generate model recommendations"""
        logger.info(f"Generating model recommendations for {self.ram_gb}GB RAM...")
        
        if self.ram_gb <= 8:
            self.recommendations = [
                {
                    'model': 'llama3.2:3b-q4_K_M',
                    'size': '~2GB',
                    'use_case': 'General assistant, extremely fast',
                    'context_limit': 4096,
                    'priority': 1
                },
                {
                    'model': 'mistral:7b-q4_K_M',
                    'size': '~4.1GB',
                    'use_case': 'Reasoning and code, fits tightly',
                    'context_limit': 2048,
                    'priority': 2
                },
                {
                    'model': 'phi3:3.8b-mini-q4_K_M',
                    'size': '~2.3GB',
                    'use_case': 'Efficient reasoning',
                    'context_limit': 4096,
                    'priority': 3
                }
            ]
        elif self.ram_gb <= 16:
            self.recommendations = [
                {
                    'model': 'llama3.1:8b-q5_K_M',
                    'size': '~5.5GB',
                    'use_case': 'General purpose, higher accuracy',
                    'context_limit': 8192,
                    'priority': 1
                },
                {
                    'model': 'mistral:7b-q8_0',
                    'size': '~7.7GB',
                    'use_case': 'High precision reasoning',
                    'context_limit': 4096,
                    'priority': 2
                },
                {
                    'model': 'codellama:7b-q5_K_M',
                    'size': '~5GB',
                    'use_case': 'Code generation',
                    'context_limit': 4096,
                    'priority': 3
                }
            ]
        else:
            self.recommendations = [
                {
                    'model': 'llama3.1:8b-q8_0',
                    'size': '~8.5GB',
                    'use_case': 'Maximum quality general purpose',
                    'context_limit': 16384,
                    'priority': 1
                },
                {
                    'model': 'mixtral:8x7b-q4_K_M',
                    'size': '~26GB',
                    'use_case': 'Advanced reasoning (if RAM allows)',
                    'context_limit': 8192,
                    'priority': 2
                },
                {
                    'model': 'codellama:13b-q5_K_M',
                    'size': '~9GB',
                    'use_case': 'Advanced code generation',
                    'context_limit': 8192,
                    'priority': 3
                }
            ]
            
        return self.recommendations
    
    def print_recommendations(self):
        """Print formatted recommendations"""
        print("\n" + "="*70)
        print(f"MODEL RECOMMENDATIONS FOR {self.ram_gb}GB RAM")
        print("="*70)
        
        for rec in self.recommendations:
            print(f"\n{rec['priority']}. {rec['model']}")
            print(f"   Size: {rec['size']}")
            print(f"   Use Case: {rec['use_case']}")
            print(f"   Recommended Context: {rec['context_limit']} tokens")
            print(f"   Pull command: ollama pull {rec['model'].split(':')[0]}")
        
        print("\n" + "="*70)
        print("\nIMPORTANT NOTES:")
        print("- Always use Q4_K_M or Q5_K_M quantization for best balance")
        print("- Limit context window to prevent OOM crashes")
        print("- Monitor memory pressure during inference")
        print("="*70 + "\n")


class ProcessOptimizer:
    """Manages process priority and scheduling"""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        
    def optimize_process(self, process_name: str):
        """Optimize a specific process for performance"""
        logger.info(f"Optimizing process: {process_name}")
        
        # Find process ID
        try:
            result = subprocess.run(
                ['pgrep', '-x', process_name],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                logger.warning(f"Process {process_name} not found")
                return
                
            pids = result.stdout.strip().split('\n')
            
            for pid in pids:
                if pid:
                    self._promote_process(int(pid), process_name)
                    
        except Exception as e:
            logger.error(f"Error optimizing process {process_name}: {e}")
    
    def _promote_process(self, pid: int, name: str):
        """Promote process to high priority"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would promote PID {pid} ({name}) to high priority")
            return
            
        try:
            # Use taskpolicy to promote to performance cores
            subprocess.run(
                ['taskpolicy', '-B', '-p', str(pid)],
                check=True, capture_output=True
            )
            logger.info(f"✓ Promoted PID {pid} ({name}) to performance cores")
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Failed to promote PID {pid}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='M1 LLM Optimization Agent - Optimize macOS M1 for local LLM inference'
    )
    parser.add_argument('--analyze', action='store_true', help='Analyze system only')
    parser.add_argument('--optimize-os', action='store_true', help='Apply OS optimizations')
    parser.add_argument('--optimize-ollama', action='store_true', help='Configure Ollama')
    parser.add_argument('--recommend-models', action='store_true', help='Show model recommendations')
    parser.add_argument('--aggressive', action='store_true', help='Apply aggressive optimizations')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without applying')
    parser.add_argument('--all', action='store_true', help='Run all optimizations')
    
    args = parser.parse_args()
    
    # If no arguments, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    print("\n" + "="*70)
    print("M1 LLM OPTIMIZATION AGENT")
    print("Based on level33 High-Performance Architecture")
    print("="*70 + "\n")
    
    # Always analyze first
    analyzer = M1SystemAnalyzer()
    system_info = analyzer.analyze()
    
    print("\nSYSTEM ANALYSIS:")
    print(f"  Chip: {system_info.get('chip', 'Unknown')}")
    print(f"  RAM: {system_info.get('ram_gb', 0)}GB")
    print(f"  Ollama: {'Installed' if system_info.get('ollama_installed') else 'Not Found'}")
    print(f"  PyTorch MPS: {'Available' if system_info.get('mps_available') else 'Not Available'}")
    print(f"  MLX: {'Installed' if system_info.get('mlx_installed') else 'Not Installed'}")
    print(f"  uv: {'Installed' if system_info.get('uv_installed') else 'Not Installed'}")
    
    if system_info.get('resource_hogs'):
        print(f"\n  ⚠️  Resource-heavy processes detected: {', '.join(system_info['resource_hogs'])}")
    
    if args.analyze:
        print("\nAnalysis complete.")
        return
    
    ram_gb = system_info.get('ram_gb', 8)
    
    # OS Optimization
    if args.optimize_os or args.all:
        print("\n" + "-"*70)
        os_optimizer = OSOptimizer(dry_run=args.dry_run)
        changes = os_optimizer.optimize(aggressive=args.aggressive)
        print(f"\nOS optimization complete. {len(changes)} changes applied.")
    
    # Ollama Optimization
    if args.optimize_ollama or args.all:
        print("\n" + "-"*70)
        ollama_optimizer = OllamaOptimizer(ram_gb, dry_run=args.dry_run)
        env_vars = ollama_optimizer.optimize()
        ollama_optimizer.apply_configuration()
        
        # Generate startup script
        script_path = Path.home() / 'm1_llm_optimizer' / 'start_ollama.sh'
        ollama_optimizer.generate_startup_script(script_path)
        print(f"\nOllama configuration complete.")
        print(f"Startup script generated: {script_path}")
    
    # Model Recommendations
    if args.recommend_models or args.all:
        print("\n" + "-"*70)
        recommender = ModelRecommender(ram_gb)
        recommender.get_recommendations()
        recommender.print_recommendations()
    
    print("\n" + "="*70)
    print("OPTIMIZATION COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("1. Restart your system to apply all changes")
    print("2. Use the generated startup script to run Ollama")
    print("3. Pull recommended models based on your RAM")
    print("4. Monitor system performance with Activity Monitor")
    print("\nFor thermal management, consider installing Macs Fan Control")
    print("Backup saved to: ~/.m1_optimizer_backup.json")
    print("\n")


if __name__ == '__main__':
    main()
