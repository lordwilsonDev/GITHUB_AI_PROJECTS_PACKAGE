#!/usr/bin/env python3
"""
Process Management Module
Manages process priority and scheduling for optimal LLM performance
"""

import subprocess
import psutil
import os
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ProcessManager:
    """Manages process priority and resource allocation"""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.optimized_processes = []
        
    def find_process_by_name(self, process_name: str) -> List[int]:
        """Find process IDs by name"""
        pids = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == process_name:
                    pids.append(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        return pids
    
    def promote_to_performance_cores(self, pid: int, process_name: str = None) -> bool:
        """Promote process to performance cores using taskpolicy"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would promote PID {pid} to performance cores")
            return True
        
        try:
            # Use taskpolicy -B to promote to background (performance) tier
            subprocess.run(
                ['taskpolicy', '-B', '-p', str(pid)],
                check=True, capture_output=True
            )
            
            name = process_name or f"PID {pid}"
            logger.info(f"✓ Promoted {name} to performance cores")
            self.optimized_processes.append({'pid': pid, 'name': name})
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Failed to promote PID {pid}: {e}")
            return False
    
    def set_throughput_tier(self, pid: int, tier: int = 5, process_name: str = None) -> bool:
        """Set throughput tier for process (0-5, 5 is highest)"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would set PID {pid} to throughput tier {tier}")
            return True
        
        try:
            subprocess.run(
                ['taskpolicy', '-t', str(tier), '-p', str(pid)],
                check=True, capture_output=True
            )
            
            name = process_name or f"PID {pid}"
            logger.info(f"✓ Set {name} to throughput tier {tier}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Failed to set throughput tier for PID {pid}: {e}")
            return False
    
    def optimize_ollama(self) -> bool:
        """Optimize Ollama process if running"""
        logger.info("Looking for Ollama process...")
        
        pids = self.find_process_by_name('ollama')
        
        if not pids:
            logger.warning("Ollama process not found")
            return False
        
        success = True
        for pid in pids:
            if not self.promote_to_performance_cores(pid, 'ollama'):
                success = False
            if not self.set_throughput_tier(pid, 5, 'ollama'):
                success = False
        
        return success
    
    def optimize_python_process(self, script_name: Optional[str] = None) -> bool:
        """Optimize Python processes"""
        logger.info("Looking for Python processes...")
        
        optimized = False
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['name'] in ['python', 'python3', 'Python']:
                    # If script_name specified, only optimize matching processes
                    if script_name:
                        cmdline = proc.info.get('cmdline', [])
                        if not any(script_name in arg for arg in cmdline):
                            continue
                    
                    pid = proc.info['pid']
                    if self.promote_to_performance_cores(pid, f"python (PID {pid})"):
                        self.set_throughput_tier(pid, 5, f"python (PID {pid})")
                        optimized = True
                        
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Error optimizing Python processes: {e}")
        
        if not optimized:
            logger.warning("No Python processes found to optimize")
        
        return optimized
    
    def suspend_resource_hogs(self, aggressive=False) -> List[str]:
        """Suspend known resource-intensive processes"""
        suspended = []
        
        processes_to_suspend = [
            'photoanalysisd',
            'mediaanalysisd',
        ]
        
        if aggressive:
            processes_to_suspend.extend([
                'mds_stores',
                'mdworker',
            ])
        
        for proc_name in processes_to_suspend:
            pids = self.find_process_by_name(proc_name)
            
            for pid in pids:
                if self._suspend_process(pid, proc_name):
                    suspended.append(proc_name)
        
        return suspended
    
    def _suspend_process(self, pid: int, name: str) -> bool:
        """Suspend a process using SIGSTOP"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would suspend {name} (PID {pid})")
            return True
        
        try:
            subprocess.run(
                ['kill', '-STOP', str(pid)],
                check=True, capture_output=True
            )
            logger.info(f"✓ Suspended {name} (PID {pid})")
            logger.warning(f"Note: {name} will remain suspended until resumed or system restart")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Failed to suspend {name}: {e}")
            return False
    
    def resume_process(self, pid: int, name: str = None) -> bool:
        """Resume a suspended process using SIGCONT"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would resume PID {pid}")
            return True
        
        try:
            subprocess.run(
                ['kill', '-CONT', str(pid)],
                check=True, capture_output=True
            )
            logger.info(f"✓ Resumed {name or 'process'} (PID {pid})")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Failed to resume PID {pid}: {e}")
            return False
    
    def get_process_info(self, pid: int) -> Optional[Dict]:
        """Get detailed process information"""
        try:
            proc = psutil.Process(pid)
            return {
                'pid': pid,
                'name': proc.name(),
                'status': proc.status(),
                'cpu_percent': proc.cpu_percent(interval=0.1),
                'memory_percent': proc.memory_percent(),
                'num_threads': proc.num_threads(),
                'cmdline': ' '.join(proc.cmdline()),
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    
    def generate_process_wrapper(self, output_path) -> bool:
        """Generate wrapper script for running processes with optimization"""
        from pathlib import Path
        
        script_content = """#!/bin/bash
# Process Optimization Wrapper
# Runs a command with optimized process priority

if [ $# -eq 0 ]; then
    echo "Usage: $0 <command> [args...]"
    echo "Example: $0 python my_script.py"
    exit 1
fi

echo "Starting process with optimization..."

# Start the process in background
"$@" &
PID=$!

echo "Process started with PID: $PID"

# Wait a moment for process to initialize
sleep 1

# Optimize the process
echo "Optimizing process priority..."
taskpolicy -B -p $PID 2>/dev/null && echo "  ✓ Promoted to performance cores"
taskpolicy -t 5 -p $PID 2>/dev/null && echo "  ✓ Set to highest throughput tier"

echo "Process optimization complete"
echo "Waiting for process to complete..."

# Wait for the process to finish
wait $PID
EXIT_CODE=$?

echo "Process completed with exit code: $EXIT_CODE"
exit $EXIT_CODE
"""
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create process wrapper at {output_path}")
            return True
        
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(script_content)
            os.chmod(output_path, 0o755)
            logger.info(f"✓ Created process wrapper: {output_path}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to create process wrapper: {e}")
            return False
    
    def monitor_process_performance(self, pid: int, duration_seconds=60) -> List[Dict]:
        """Monitor process performance over time"""
        import time
        
        logger.info(f"Monitoring PID {pid} for {duration_seconds} seconds...")
        
        samples = []
        start_time = time.time()
        
        try:
            proc = psutil.Process(pid)
            
            while time.time() - start_time < duration_seconds:
                sample = {
                    'timestamp': time.time() - start_time,
                    'cpu_percent': proc.cpu_percent(interval=1),
                    'memory_percent': proc.memory_percent(),
                    'num_threads': proc.num_threads(),
                    'status': proc.status(),
                }
                samples.append(sample)
                logger.info(f"Sample at {sample['timestamp']:.1f}s: "
                          f"CPU={sample['cpu_percent']:.1f}%, "
                          f"Memory={sample['memory_percent']:.1f}%")
                
        except psutil.NoSuchProcess:
            logger.warning(f"Process {pid} terminated during monitoring")
        except KeyboardInterrupt:
            logger.info("Monitoring interrupted by user")
        
        return samples
    
    def print_optimization_summary(self):
        """Print summary of optimized processes"""
        print("\n" + "="*70)
        print("PROCESS OPTIMIZATION SUMMARY")
        print("="*70)
        
        if self.optimized_processes:
            print(f"\nOptimized {len(self.optimized_processes)} process(es):")
            for proc in self.optimized_processes:
                print(f"  ✓ {proc['name']} (PID {proc['pid']})")
        else:
            print("\nNo processes optimized yet.")
        
        print("\n" + "="*70 + "\n")
