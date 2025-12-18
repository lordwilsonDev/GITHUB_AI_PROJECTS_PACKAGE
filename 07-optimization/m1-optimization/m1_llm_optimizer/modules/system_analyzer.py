#!/usr/bin/env python3
"""
System Analyzer Module
Detailed system analysis for M1 optimization
"""

import subprocess
import platform
import psutil
import json
from typing import Dict, List
from pathlib import Path


class DetailedSystemAnalyzer:
    """Performs deep system analysis for optimization planning"""
    
    def __init__(self):
        self.metrics = {}
        
    def analyze_memory_pressure(self) -> Dict:
        """Analyze current memory pressure and usage patterns"""
        try:
            # Get memory stats
            vm = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            memory_analysis = {
                'total_gb': round(vm.total / (1024**3), 2),
                'available_gb': round(vm.available / (1024**3), 2),
                'used_gb': round(vm.used / (1024**3), 2),
                'percent_used': vm.percent,
                'swap_total_gb': round(swap.total / (1024**3), 2),
                'swap_used_gb': round(swap.used / (1024**3), 2),
                'swap_percent': swap.percent,
            }
            
            # Determine memory pressure level
            if vm.percent < 60:
                memory_analysis['pressure_level'] = 'LOW'
                memory_analysis['recommendation'] = 'System has adequate free memory'
            elif vm.percent < 80:
                memory_analysis['pressure_level'] = 'MODERATE'
                memory_analysis['recommendation'] = 'Consider closing unused applications'
            else:
                memory_analysis['pressure_level'] = 'HIGH'
                memory_analysis['recommendation'] = 'Critical: Close applications or use smaller models'
                
            return memory_analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_cpu_architecture(self) -> Dict:
        """Analyze CPU core configuration"""
        try:
            cpu_info = {
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'cpu_percent': psutil.cpu_percent(interval=1),
            }
            
            # Get per-core usage
            per_cpu = psutil.cpu_percent(interval=1, percpu=True)
            cpu_info['per_core_usage'] = per_cpu
            
            # Detect performance vs efficiency cores (M1 has 4P + 4E typically)
            result = subprocess.run(
                ['sysctl', '-n', 'hw.perflevel0.physicalcpu'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                cpu_info['performance_cores'] = int(result.stdout.strip())
                
            result = subprocess.run(
                ['sysctl', '-n', 'hw.perflevel1.physicalcpu'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                cpu_info['efficiency_cores'] = int(result.stdout.strip())
                
            return cpu_info
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_disk_io(self) -> Dict:
        """Analyze disk I/O patterns"""
        try:
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            disk_analysis = {
                'total_gb': round(disk.total / (1024**3), 2),
                'used_gb': round(disk.used / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2),
                'percent_used': disk.percent,
                'read_mb': round(disk_io.read_bytes / (1024**2), 2) if disk_io else 0,
                'write_mb': round(disk_io.write_bytes / (1024**2), 2) if disk_io else 0,
            }
            
            # Check if disk is getting full (important for swap)
            if disk.percent > 90:
                disk_analysis['warning'] = 'Disk nearly full - may impact swap performance'
            elif disk.percent > 80:
                disk_analysis['warning'] = 'Disk usage high - monitor swap space'
                
            return disk_analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def find_resource_hogs(self, top_n=10) -> List[Dict]:
        """Identify processes consuming the most resources"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    if pinfo['cpu_percent'] > 0 or pinfo['memory_percent'] > 0:
                        processes.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'],
                            'cpu_percent': round(pinfo['cpu_percent'], 2),
                            'memory_percent': round(pinfo['memory_percent'], 2),
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by memory usage (most critical for LLM)
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            
            return processes[:top_n]
            
        except Exception as e:
            return [{'error': str(e)}]
    
    def check_thermal_state(self) -> Dict:
        """Check thermal state (requires additional tools)"""
        thermal_info = {'available': False}
        
        try:
            # Try to get thermal info via powermetrics (requires sudo)
            result = subprocess.run(
                ['sudo', '-n', 'powermetrics', '--samplers', 'thermal', '-n', '1'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                thermal_info['available'] = True
                thermal_info['data'] = result.stdout
            else:
                thermal_info['note'] = 'Thermal monitoring requires sudo access'
                
        except subprocess.TimeoutExpired:
            thermal_info['note'] = 'Thermal check timed out'
        except Exception as e:
            thermal_info['note'] = f'Thermal monitoring not available: {str(e)}'
            
        return thermal_info
    
    def analyze_spotlight_activity(self) -> Dict:
        """Check Spotlight indexing activity"""
        spotlight_info = {'active': False, 'processes': []}
        
        try:
            # Check for Spotlight processes
            spotlight_procs = ['mds', 'mds_stores', 'mdworker']
            
            for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
                try:
                    if any(sp in proc.info['name'].lower() for sp in spotlight_procs):
                        spotlight_info['active'] = True
                        spotlight_info['processes'].append({
                            'name': proc.info['name'],
                            'cpu': round(proc.info['cpu_percent'], 2),
                            'memory': round(proc.info['memory_percent'], 2),
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Check indexing status
            result = subprocess.run(
                ['mdutil', '-s', '/'],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                spotlight_info['status'] = result.stdout.strip()
                spotlight_info['enabled'] = 'Indexing enabled' in result.stdout
                
        except Exception as e:
            spotlight_info['error'] = str(e)
            
        return spotlight_info
    
    def generate_report(self) -> Dict:
        """Generate comprehensive system report"""
        report = {
            'memory': self.analyze_memory_pressure(),
            'cpu': self.analyze_cpu_architecture(),
            'disk': self.analyze_disk_io(),
            'top_processes': self.find_resource_hogs(),
            'spotlight': self.analyze_spotlight_activity(),
            'thermal': self.check_thermal_state(),
        }
        
        return report
    
    def print_report(self, report: Dict):
        """Print formatted system report"""
        print("\n" + "="*70)
        print("DETAILED SYSTEM ANALYSIS")
        print("="*70)
        
        # Memory
        mem = report.get('memory', {})
        print("\nMEMORY:")
        print(f"  Total: {mem.get('total_gb', 0)}GB")
        print(f"  Used: {mem.get('used_gb', 0)}GB ({mem.get('percent_used', 0)}%)")
        print(f"  Available: {mem.get('available_gb', 0)}GB")
        print(f"  Swap Used: {mem.get('swap_used_gb', 0)}GB / {mem.get('swap_total_gb', 0)}GB")
        print(f"  Pressure Level: {mem.get('pressure_level', 'UNKNOWN')}")
        print(f"  Recommendation: {mem.get('recommendation', 'N/A')}")
        
        # CPU
        cpu = report.get('cpu', {})
        print("\nCPU:")
        print(f"  Performance Cores: {cpu.get('performance_cores', 'Unknown')}")
        print(f"  Efficiency Cores: {cpu.get('efficiency_cores', 'Unknown')}")
        print(f"  Overall Usage: {cpu.get('cpu_percent', 0)}%")
        
        # Disk
        disk = report.get('disk', {})
        print("\nDISK:")
        print(f"  Total: {disk.get('total_gb', 0)}GB")
        print(f"  Used: {disk.get('used_gb', 0)}GB ({disk.get('percent_used', 0)}%)")
        print(f"  Free: {disk.get('free_gb', 0)}GB")
        if 'warning' in disk:
            print(f"  ⚠️  {disk['warning']}")
        
        # Top Processes
        print("\nTOP MEMORY-CONSUMING PROCESSES:")
        for i, proc in enumerate(report.get('top_processes', [])[:5], 1):
            print(f"  {i}. {proc.get('name', 'Unknown')} - "
                  f"CPU: {proc.get('cpu_percent', 0)}%, "
                  f"Memory: {proc.get('memory_percent', 0)}%")
        
        # Spotlight
        spotlight = report.get('spotlight', {})
        print("\nSPOTLIGHT:")
        print(f"  Indexing Enabled: {spotlight.get('enabled', 'Unknown')}")
        if spotlight.get('active'):
            print(f"  Active Processes: {len(spotlight.get('processes', []))}")
            print("  ⚠️  Spotlight is consuming resources")
        
        print("\n" + "="*70 + "\n")
