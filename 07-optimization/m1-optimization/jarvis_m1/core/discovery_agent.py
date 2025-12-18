#!/usr/bin/env python3
"""
Discovery Agent - Analyzes logs and code to find patterns and governance cycles
"""

import os
import re
import json
from datetime import datetime

class DiscoveryAgent:
    def __init__(self, base_path="."):
        self.base_path = base_path
        self.patterns = []
        self.governance_cycles = 0
        self.issues_found = []
        
    def scan_logs(self):
        """Scan log files for patterns and issues"""
        print("\n🔍 DISCOVERY AGENT: Scanning system logs...")
        
        log_patterns = [
            r'ERROR',
            r'WARN',
            r'CRITICAL',
            r'Exception',
            r'Traceback'
        ]
        
        error_count = 0
        log_files = []
        
        # Find log files
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.endswith('.log') or 'log' in file.lower():
                    log_files.append(os.path.join(root, file))
        
        print(f"   Found {len(log_files)} log files")
        
        # Scan for errors
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for pattern in log_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        error_count += len(matches)
            except Exception as e:
                pass
        
        print(f"   Detected {error_count} error entries in logs")
        self.issues_found.append(f"Log errors: {error_count}")
        return error_count
    
    def detect_governance_cycles(self):
        """Detect governance cycles in the codebase"""
        print("\n🔍 DISCOVERY AGENT: Detecting governance cycles...")
        
        governance_keywords = [
            'validate', 'check', 'verify', 'audit', 'monitor',
            'safety', 'governance', 'constraint', 'guard', 'protect'
        ]
        
        cycles = 0
        
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.endswith('.py'):
                    try:
                        filepath = os.path.join(root, file)
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().lower()
                            for keyword in governance_keywords:
                                if keyword in content:
                                    cycles += 1
                                    break
                    except Exception as e:
                        pass
        
        self.governance_cycles = cycles
        print(f"   Found {cycles} governance cycles")
        return cycles
    
    def analyze_code_quality(self):
        """Analyze code for potential issues"""
        print("\n🔍 DISCOVERY AGENT: Analyzing code quality...")
        
        issues = []
        total_files = 0
        files_with_issues = 0
        
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.endswith('.py'):
                    total_files += 1
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            
                            # Check for common issues
                            has_issue = False
                            
                            # Check for very long files
                            if len(lines) > 1000:
                                issues.append(f"{file}: Very long file ({len(lines)} lines)")
                                has_issue = True
                            
                            # Check for duplicate code patterns
                            line_set = set()
                            duplicates = 0
                            for line in lines:
                                stripped = line.strip()
                                if stripped and len(stripped) > 20:
                                    if stripped in line_set:
                                        duplicates += 1
                                    line_set.add(stripped)
                            
                            if duplicates > 10:
                                issues.append(f"{file}: High code duplication ({duplicates} duplicate lines)")
                                has_issue = True
                            
                            if has_issue:
                                files_with_issues += 1
                                
                    except Exception as e:
                        pass
        
        print(f"   Analyzed {total_files} Python files")
        print(f"   Found issues in {files_with_issues} files")
        
        self.issues_found.extend(issues[:5])  # Keep top 5 issues
        return issues
    
    def generate_report(self):
        """Generate discovery report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'governance_cycles': self.governance_cycles,
            'issues_found': self.issues_found,
            'patterns_detected': len(self.patterns)
        }
        
        report_path = os.path.join(self.base_path, 'discovery_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Discovery report saved to: {report_path}")
        return report
    
    def run(self):
        """Run full discovery process"""
        print("\n" + "="*60)
        print("🔍 DISCOVERY AGENT ACTIVATED")
        print("="*60)
        
        self.scan_logs()
        self.detect_governance_cycles()
        self.analyze_code_quality()
        report = self.generate_report()
        
        print("\n✅ Discovery complete!")
        print(f"   Governance cycles: {self.governance_cycles}")
        print(f"   Issues identified: {len(self.issues_found)}")
        
        return report

if __name__ == "__main__":
    agent = DiscoveryAgent(".")
    agent.run()
