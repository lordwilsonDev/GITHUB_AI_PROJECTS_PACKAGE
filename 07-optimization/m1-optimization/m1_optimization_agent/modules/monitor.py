#!/usr/bin/env python3
"""
System Monitor Module
Monitors system resources, temperature, and process status.
"""

import os
import subprocess
import psutil
import json
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger


class SystemMonitor:
    """Monitors system resources and status for M1 optimization."""
    
    def __init__(self):
        self.log_file = "logs/system_monitor.json"
        self._ensure_log_exists()
    
    def _ensure_log_exists(self):
        """Ensure log directory exists."""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def _run_command(self, command: List[str]) -> Dict:
        """Execute a system command and return result."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict:
        """Get comprehensive system status.
        
        Returns:
            Dict with system metrics including RAM, CPU, processes, and temperature
        """
        logger.info("Gathering system status")
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "memory": self._get_memory_info(),
            "cpu": self._get_cpu_info(),
            "processes": self._get_process_info(),
            "disk": self._get_disk_info(),
            "system": self._get_system_info()
        }
        
        # Try to get temperature (may require additional tools)
        temp_info = self._get_temperature_info()
        if temp_info:
            status["temperature"] = temp_info
        
        # Log status
        self._log_status(status)
        
        return status
    
    def _get_memory_info(self) -> Dict:
        """Get memory usage information."""
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "used_gb": round(mem.used / (1024**3), 2),
                "percent_used": mem.percent,
                "free_gb": round(mem.free / (1024**3), 2),
                "active_gb": round(mem.active / (1024**3), 2),
                "inactive_gb": round(mem.inactive / (1024**3), 2),
                "wired_gb": round(mem.wired / (1024**3), 2),
                "swap": {
                    "total_gb": round(swap.total / (1024**3), 2),
                    "used_gb": round(swap.used / (1024**3), 2),
                    "percent_used": swap.percent
                },
                "status": self._assess_memory_status(mem.percent)
            }
        except Exception as e:
            logger.error(f"Failed to get memory info: {e}")
            return {"error": str(e)}
    
    def _assess_memory_status(self, percent: float) -> str:
        """Assess memory status based on usage percentage."""
        if percent < 60:
            return "healthy"
        elif percent < 80:
            return "moderate"
        elif percent < 90:
            return "high"
        else:
            return "critical"
    
    def _get_cpu_info(self) -> Dict:
        """Get CPU usage information."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            cpu_freq = psutil.cpu_freq()
            
            return {
                "percent_overall": psutil.cpu_percent(interval=0.1),
                "percent_per_core": cpu_percent,
                "core_count": psutil.cpu_count(logical=False),
                "logical_count": psutil.cpu_count(logical=True),
                "frequency_mhz": {
                    "current": cpu_freq.current if cpu_freq else None,
                    "min": cpu_freq.min if cpu_freq else None,
                    "max": cpu_freq.max if cpu_freq else None
                },
                "load_average": os.getloadavg(),
                "status": self._assess_cpu_status(psutil.cpu_percent(interval=0.1))
            }
        except Exception as e:
            logger.error(f"Failed to get CPU info: {e}")
            return {"error": str(e)}
    
    def _assess_cpu_status(self, percent: float) -> str:
        """Assess CPU status based on usage percentage."""
        if percent < 50:
            return "idle"
        elif percent < 75:
            return "moderate"
        elif percent < 90:
            return "high"
        else:
            return "saturated"
    
    def _get_process_info(self) -> Dict:
        """Get information about key processes."""
        try:
            processes = {
                "ollama": [],
                "python": [],
                "windowserver": [],
                "spotlight": [],
                "photoanalysisd": []
            }
            
            # Search for specific processes
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    name = proc.info['name'].lower()
                    
                    if 'ollama' in name:
                        processes['ollama'].append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "cpu_percent": proc.info['cpu_percent'],
                            "memory_percent": round(proc.info['memory_percent'], 2),
                            "status": proc.info['status']
                        })
                    elif 'python' in name:
                        processes['python'].append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "cpu_percent": proc.info['cpu_percent'],
                            "memory_percent": round(proc.info['memory_percent'], 2)
                        })
                    elif 'windowserver' in name:
                        processes['windowserver'].append({
                            "pid": proc.info['pid'],
                            "cpu_percent": proc.info['cpu_percent'],
                            "memory_percent": round(proc.info['memory_percent'], 2)
                        })
                    elif 'mds' in name or 'spotlight' in name:
                        processes['spotlight'].append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "cpu_percent": proc.info['cpu_percent']
                        })
                    elif 'photoanalysis' in name:
                        processes['photoanalysisd'].append({
                            "pid": proc.info['pid'],
                            "cpu_percent": proc.info['cpu_percent'],
                            "memory_percent": round(proc.info['memory_percent'], 2)
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Get top memory consumers
            top_memory = sorted(
                [p for p in psutil.process_iter(['pid', 'name', 'memory_percent'])],
                key=lambda x: x.info['memory_percent'],
                reverse=True
            )[:5]
            
            processes['top_memory_consumers'] = [
                {
                    "pid": p.info['pid'],
                    "name": p.info['name'],
                    "memory_percent": round(p.info['memory_percent'], 2)
                }
                for p in top_memory
            ]
            
            return processes
        except Exception as e:
            logger.error(f"Failed to get process info: {e}")
            return {"error": str(e)}
    
    def _get_disk_info(self) -> Dict:
        """Get disk usage information."""
        try:
            disk = psutil.disk_usage('/')
            
            return {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent_used": disk.percent,
                "status": "critical" if disk.percent > 90 else "healthy"
            }
        except Exception as e:
            logger.error(f"Failed to get disk info: {e}")
            return {"error": str(e)}
    
    def _get_system_info(self) -> Dict:
        """Get general system information."""
        try:
            # Get macOS version
            version_result = self._run_command(['sw_vers', '-productVersion'])
            
            # Get chip info
            chip_result = self._run_command(['sysctl', '-n', 'machdep.cpu.brand_string'])
            
            # Get uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            return {
                "macos_version": version_result['stdout'].strip() if version_result['success'] else "unknown",
                "chip": chip_result['stdout'].strip() if chip_result['success'] else "unknown",
                "uptime_hours": round(uptime.total_seconds() / 3600, 2),
                "boot_time": boot_time.isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {"error": str(e)}
    
    def _get_temperature_info(self) -> Optional[Dict]:
        """Get temperature information (requires additional tools like powermetrics)."""
        try:
            # Try to get temperature using powermetrics (requires sudo)
            # This is a simplified version - full implementation would need sudo access
            result = self._run_command(['sysctl', 'machdep.xcpm.cpu_thermal_level'])
            
            if result['success']:
                thermal_level = result['stdout'].strip().split(':')[-1].strip()
                return {
                    "thermal_level": thermal_level,
                    "note": "Thermal level (0=cool, higher=warmer)"
                }
            
            return None
        except Exception as e:
            logger.debug(f"Could not get temperature info: {e}")
            return None
    
    def _log_status(self, status: Dict):
        """Log status to file."""
        try:
            # Read existing logs
            logs = []
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    logs = json.load(f)
            
            # Append new status
            logs.append(status)
            
            # Keep only last 100 entries
            logs = logs[-100:]
            
            # Write back
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to log status: {e}")
    
    def check_optimization_status(self) -> Dict:
        """Check if optimizations are currently applied."""
        logger.info("Checking optimization status")
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "optimizations": {}
        }
        
        try:
            # Check transparency setting
            transparency_result = self._run_command([
                'defaults', 'read', 'com.apple.universalaccess', 'reduceTransparency'
            ])
            status['optimizations']['reduce_transparency'] = (
                transparency_result['success'] and '1' in transparency_result['stdout']
            )
            
            # Check animation settings
            animation_result = self._run_command([
                'defaults', 'read', 'NSGlobalDomain', 'NSAutomaticWindowAnimationsEnabled'
            ])
            status['optimizations']['animations_disabled'] = (
                animation_result['success'] and '0' in animation_result['stdout']
            )
            
            # Check if Spotlight is disabled
            spotlight_result = self._run_command(['mdutil', '-s', '/'])
            if spotlight_result['success']:
                status['optimizations']['spotlight_disabled'] = 'disabled' in spotlight_result['stdout'].lower()
            
            # Check if Ollama is running
            ollama_result = self._run_command(['pgrep', '-x', 'ollama'])
            status['optimizations']['ollama_running'] = ollama_result['success']
            
            # Check for photoanalysisd
            photo_result = self._run_command(['pgrep', '-x', 'photoanalysisd'])
            status['optimizations']['photoanalysisd_running'] = photo_result['success']
            
        except Exception as e:
            logger.error(f"Failed to check optimization status: {e}")
            status['error'] = str(e)
        
        return status
    
    def get_recommendations(self) -> Dict:
        """Get optimization recommendations based on current system state."""
        logger.info("Generating recommendations")
        
        status = self.get_status()
        recommendations = []
        
        try:
            # Check memory
            mem_percent = status['memory']['percent_used']
            if mem_percent > 80:
                recommendations.append({
                    "priority": "high",
                    "category": "memory",
                    "issue": f"Memory usage is high ({mem_percent}%)",
                    "recommendation": "Close unnecessary applications, reduce OLLAMA_NUM_PARALLEL to 1, or use a smaller model"
                })
            
            # Check swap usage
            swap_percent = status['memory']['swap']['percent_used']
            if swap_percent > 50:
                recommendations.append({
                    "priority": "high",
                    "category": "memory",
                    "issue": f"Swap usage is high ({swap_percent}%)",
                    "recommendation": "System is swapping heavily. Consider using a smaller model or reducing context window size"
                })
            
            # Check CPU
            cpu_percent = status['cpu']['percent_overall']
            if cpu_percent > 85:
                recommendations.append({
                    "priority": "medium",
                    "category": "cpu",
                    "issue": f"CPU usage is high ({cpu_percent}%)",
                    "recommendation": "Check for background processes consuming CPU (Spotlight, photoanalysisd)"
                })
            
            # Check WindowServer
            windowserver_procs = status['processes'].get('windowserver', [])
            if windowserver_procs and windowserver_procs[0]['memory_percent'] > 5:
                recommendations.append({
                    "priority": "low",
                    "category": "ui",
                    "issue": "WindowServer is consuming significant memory",
                    "recommendation": "Disable transparency and animations to reduce WindowServer overhead"
                })
            
            # Check Spotlight
            spotlight_procs = status['processes'].get('spotlight', [])
            if spotlight_procs and any(p['cpu_percent'] > 10 for p in spotlight_procs):
                recommendations.append({
                    "priority": "medium",
                    "category": "indexing",
                    "issue": "Spotlight is actively indexing",
                    "recommendation": "Disable Spotlight indexing on the main volume to free up CPU and I/O"
                })
            
            # Check photoanalysisd
            photo_procs = status['processes'].get('photoanalysisd', [])
            if photo_procs:
                recommendations.append({
                    "priority": "medium",
                    "category": "background_services",
                    "issue": "photoanalysisd is running",
                    "recommendation": "Disable photoanalysisd to free up Neural Engine and GPU resources"
                })
            
            # Check disk space
            disk_percent = status['disk']['percent_used']
            if disk_percent > 85:
                recommendations.append({
                    "priority": "high",
                    "category": "disk",
                    "issue": f"Disk usage is high ({disk_percent}%)",
                    "recommendation": "Free up disk space. Low disk space can impact swap performance"
                })
            
            if not recommendations:
                recommendations.append({
                    "priority": "info",
                    "category": "general",
                    "issue": "System appears healthy",
                    "recommendation": "No immediate optimizations needed"
                })
        
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            recommendations.append({
                "priority": "error",
                "category": "system",
                "issue": "Failed to analyze system",
                "recommendation": str(e)
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "recommendations": recommendations,
            "count": len(recommendations)
        }
