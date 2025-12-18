#!/usr/bin/env python3
"""
System Health Check Automation

Checks and reports on:
- Disk space usage
- Memory usage
- Running processes
- System uptime
- Network connectivity

Usage: python3 automations/system_health_check.py
"""

import subprocess
import shutil
import psutil
import platform
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SystemHealthCheck:
    def __init__(self):
        self.report = []
        self.warnings = []
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def add_section(self, title):
        """Add a section header to the report"""
        self.report.append("\n" + "="*60)
        self.report.append(f"  {title}")
        self.report.append("="*60)
    
    def add_line(self, text):
        """Add a line to the report"""
        self.report.append(text)
    
    def add_warning(self, warning):
        """Add a warning"""
        self.warnings.append(warning)
        self.add_line(f"⚠️  WARNING: {warning}")
    
    def check_disk_space(self):
        """Check disk space usage"""
        self.add_section("💾 DISK SPACE")
        
        # Get disk usage for root partition
        usage = shutil.disk_usage("/")
        total_gb = usage.total / (1024**3)
        used_gb = usage.used / (1024**3)
        free_gb = usage.free / (1024**3)
        percent_used = (usage.used / usage.total) * 100
        
        self.add_line(f"Total: {total_gb:.2f} GB")
        self.add_line(f"Used: {used_gb:.2f} GB ({percent_used:.1f}%)")
        self.add_line(f"Free: {free_gb:.2f} GB")
        
        # Warning if less than 10GB free
        if free_gb < 10:
            self.add_warning(f"Low disk space: Only {free_gb:.2f} GB remaining")
        elif percent_used > 90:
            self.add_warning(f"Disk usage high: {percent_used:.1f}% used")
        else:
            self.add_line("✅ Disk space healthy")
    
    def check_memory(self):
        """Check memory usage"""
        self.add_section("🧠 MEMORY")
        
        mem = psutil.virtual_memory()
        total_gb = mem.total / (1024**3)
        used_gb = mem.used / (1024**3)
        available_gb = mem.available / (1024**3)
        percent_used = mem.percent
        
        self.add_line(f"Total: {total_gb:.2f} GB")
        self.add_line(f"Used: {used_gb:.2f} GB ({percent_used:.1f}%)")
        self.add_line(f"Available: {available_gb:.2f} GB")
        
        if percent_used > 90:
            self.add_warning(f"High memory usage: {percent_used:.1f}%")
        else:
            self.add_line("✅ Memory usage healthy")
    
    def check_cpu(self):
        """Check CPU usage"""
        self.add_section("📊 CPU")
        
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        self.add_line(f"CPU Cores: {cpu_count}")
        self.add_line(f"Current Usage: {cpu_percent}%")
        
        if cpu_percent > 80:
            self.add_warning(f"High CPU usage: {cpu_percent}%")
        else:
            self.add_line("✅ CPU usage normal")
    
    def check_uptime(self):
        """Check system uptime"""
        self.add_section("⏰ SYSTEM UPTIME")
        
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        days = uptime.days
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        
        self.add_line(f"Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.add_line(f"Uptime: {days} days, {hours} hours, {minutes} minutes")
        
        if days > 30:
            self.add_warning(f"System has been running for {days} days - consider restarting")
        else:
            self.add_line("✅ Uptime healthy")
    
    def check_top_processes(self):
        """Check top memory-consuming processes"""
        self.add_section("📊 TOP PROCESSES (by Memory)")
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by memory usage
        processes.sort(key=lambda x: x['memory_percent'], reverse=True)
        
        # Show top 5
        self.add_line("\nTop 5 processes:")
        for i, proc in enumerate(processes[:5], 1):
            name = proc['name'][:30]  # Truncate long names
            mem = proc['memory_percent']
            self.add_line(f"  {i}. {name:<30} {mem:>6.2f}%")
    
    def check_network(self):
        """Check network connectivity"""
        self.add_section("🌐 NETWORK")
        
        try:
            # Try to ping Google DNS
            result = subprocess.run(
                ["ping", "-c", "1", "8.8.8.8"],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                self.add_line("✅ Internet connectivity: OK")
            else:
                self.add_warning("No internet connectivity")
        except subprocess.TimeoutExpired:
            self.add_warning("Network check timed out")
        except Exception as e:
            self.add_warning(f"Network check failed: {e}")
    
    def check_ollama(self):
        """Check if Ollama is running"""
        self.add_section("🦖 OLLAMA STATUS")
        
        try:
            result = subprocess.run(
                ["curl", "-s", "http://localhost:11434/api/tags"],
                capture_output=True,
                timeout=2
            )
            
            if result.returncode == 0 and result.stdout:
                self.add_line("✅ Ollama is running")
                # Try to parse models
                import json
                try:
                    data = json.loads(result.stdout)
                    if 'models' in data:
                        self.add_line(f"Models available: {len(data['models'])}")
                except:
                    pass
            else:
                self.add_line("⚠️  Ollama is not running")
        except Exception as e:
            self.add_line(f"⚠️  Could not check Ollama: {e}")
    
    def run_full_check(self):
        """Run all health checks"""
        print("\n🔍 RUNNING SYSTEM HEALTH CHECK...\n")
        
        self.add_section(f"📊 SYSTEM HEALTH REPORT - {self.timestamp}")
        self.add_line(f"System: {platform.system()} {platform.release()}")
        self.add_line(f"Machine: {platform.machine()}")
        
        self.check_disk_space()
        self.check_memory()
        self.check_cpu()
        self.check_uptime()
        self.check_top_processes()
        self.check_network()
        self.check_ollama()
        
        # Print report
        for line in self.report:
            print(line)
        
        # Summary
        print("\n" + "="*60)
        if self.warnings:
            print(f"⚠️  {len(self.warnings)} WARNING(S) FOUND")
            print("="*60)
        else:
            print("✅ ALL SYSTEMS HEALTHY")
            print("="*60)
        
        print()
        
        # Save report to file
        self.save_report()
    
    def save_report(self):
        """Save report to file"""
        report_dir = os.path.expanduser("~/level33_sovereign/reports")
        os.makedirs(report_dir, exist_ok=True)
        
        filename = f"health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(report_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write("\n".join(self.report))
        
        print(f"💾 Report saved to: {filepath}")

if __name__ == "__main__":
    checker = SystemHealthCheck()
    checker.run_full_check()
