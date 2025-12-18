#!/usr/bin/env python3
"""
Thermal Manager Module
Handles thermal management and fan control for M1 systems.
"""

import os
import subprocess
from typing import Dict, Optional
from loguru import logger


class ThermalManager:
    """Manages thermal settings and fan control for M1 systems."""
    
    def __init__(self):
        self.macs_fan_control_path = "/Applications/Macs Fan Control.app/Contents/MacOS/Macs Fan Control"
    
    def _run_command(self, command: list) -> Dict:
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
                "stderr": result.stderr
            }
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return {"success": False, "error": str(e)}
    
    def check_macs_fan_control_installed(self) -> bool:
        """Check if Macs Fan Control is installed."""
        return os.path.exists(self.macs_fan_control_path)
    
    def manage(self, min_fan_speed: Optional[int] = None, enable: bool = True) -> Dict:
        """Manage thermal settings and fan control.
        
        Args:
            min_fan_speed: Minimum fan speed in RPM (e.g., 3000)
            enable: Enable custom fan control
        
        Returns:
            Dict with success status and applied settings
        """
        logger.info(f"Managing thermal settings (enable={enable}, min_speed={min_fan_speed})")
        
        results = {
            "success": True,
            "enabled": enable,
            "method": "none"
        }
        
        try:
            # Check if Macs Fan Control is installed
            if self.check_macs_fan_control_installed():
                results["method"] = "macs_fan_control"
                
                if enable and min_fan_speed:
                    # Launch Macs Fan Control with custom settings
                    # Note: This launches the app; actual fan control requires GUI interaction
                    # or configuration file modification
                    result = self._run_command([
                        self.macs_fan_control_path,
                        '/minimized'
                    ])
                    
                    if result["success"]:
                        results["message"] = f"Macs Fan Control launched. Set minimum fan speed to {min_fan_speed} RPM via GUI."
                        results["note"] = "Manual configuration required in Macs Fan Control GUI"
                        logger.info(results["message"])
                    else:
                        results["success"] = False
                        results["error"] = "Failed to launch Macs Fan Control"
                else:
                    results["message"] = "Macs Fan Control is installed but not configured"
            else:
                results["method"] = "system_default"
                results["warning"] = "Macs Fan Control not installed. Install from https://crystalidea.com/macs-fan-control"
                results["message"] = "Using system default thermal management"
                logger.warning(results["warning"])
            
            # Provide thermal monitoring information
            thermal_info = self._get_thermal_info()
            if thermal_info:
                results["thermal_info"] = thermal_info
        
        except Exception as e:
            logger.error(f"Thermal management failed: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results
    
    def _get_thermal_info(self) -> Optional[Dict]:
        """Get current thermal information."""
        try:
            # Try to get thermal level
            result = self._run_command(['sysctl', 'machdep.xcpm.cpu_thermal_level'])
            
            if result["success"]:
                thermal_level = result['stdout'].strip().split(':')[-1].strip()
                return {
                    "thermal_level": thermal_level,
                    "note": "0=cool, higher values indicate warmer temperatures"
                }
            
            return None
        except Exception as e:
            logger.debug(f"Could not get thermal info: {e}")
            return None
    
    def get_recommendations(self) -> Dict:
        """Get thermal management recommendations."""
        logger.info("Getting thermal recommendations")
        
        recommendations = {
            "success": True,
            "recommendations": []
        }
        
        try:
            # Check if Macs Fan Control is installed
            if not self.check_macs_fan_control_installed():
                recommendations["recommendations"].append({
                    "priority": "medium",
                    "category": "thermal",
                    "recommendation": "Install Macs Fan Control for better thermal management during intensive AI workloads",
                    "url": "https://crystalidea.com/macs-fan-control"
                })
            
            # General recommendations
            recommendations["recommendations"].extend([
                {
                    "priority": "high",
                    "category": "thermal",
                    "recommendation": "For MacBook Air (fanless), use a laptop stand or cooling pad to improve passive cooling"
                },
                {
                    "priority": "medium",
                    "category": "thermal",
                    "recommendation": "For Mac Mini/MacBook Pro, set minimum fan speed to 3000 RPM during inference to prevent thermal throttling"
                },
                {
                    "priority": "low",
                    "category": "thermal",
                    "recommendation": "Monitor thermal throttling using Activity Monitor or iStat Menus during long inference sessions"
                }
            ])
        
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            recommendations["success"] = False
            recommendations["error"] = str(e)
        
        return recommendations
