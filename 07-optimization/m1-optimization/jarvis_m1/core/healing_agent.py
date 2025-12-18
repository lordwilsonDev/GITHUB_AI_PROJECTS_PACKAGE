#!/usr/bin/env python3
"""
Healing Agent - Automatically fixes broken code and system issues
"""

import os
import re
import json
import shutil
from datetime import datetime

class HealingAgent:
    def __init__(self, base_path="."):
        self.base_path = base_path
        self.fixes_applied = []
        self.backup_dir = os.path.join(base_path, '.healing_backups')
        
        # Create backup directory
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def backup_file(self, filepath):
        """Create backup before modifying"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.basename(filepath)
        backup_path = os.path.join(self.backup_dir, f"{filename}.{timestamp}.bak")
        shutil.copy2(filepath, backup_path)
        return backup_path
    
    def fix_ouroboros_detection(self):
        """Fix the ouroboros.py governance cycle detection"""
        print("\n💉 HEALING AGENT: Fixing ouroboros.py detection...")
        
        ouroboros_path = os.path.join(self.base_path, 'core', 'ouroboros.py')
        
        if not os.path.exists(ouroboros_path):
            print("   ⚠️  ouroboros.py not found")
            return False
        
        # Backup original
        backup_path = self.backup_file(ouroboros_path)
        print(f"   Backed up to: {backup_path}")
        
        # Read current content
        with open(ouroboros_path, 'r') as f:
            content = f.read()
        
        # Check if already fixed
        if 'governance_cycles' in content:
            print("   Already fixed - governance cycle detection present")
            return True
        
        # Create improved version
        new_content = '''#!/usr/bin/env python3

import os
import re

def calculate_vdr(path="."):
    """Calculate Vitality-to-Density Ratio (VDR)"""
    
    # Count governance cycles
    governance_cycles = 0
    governance_keywords = [
        'validate', 'check', 'verify', 'audit', 'monitor',
        'safety', 'governance', 'constraint', 'guard', 'protect'
    ]
    
    # Count refactors and complexity
    refactors = 0
    complexity = 0
    total_files = 0
    
    for root, dirs, files in os.walk(path):
        # Skip hidden and backup directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        
        for file in files:
            if file.endswith(".py"):
                total_files += 1
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = content.split('\\n')
                        complexity += len(lines)
                        
                        # Detect governance cycles
                        content_lower = content.lower()
                        for keyword in governance_keywords:
                            if keyword in content_lower:
                                governance_cycles += 1
                                break
                        
                        # Count refactors (functions, classes)
                        refactors += len(re.findall(r'\\bdef\\s+\\w+', content))
                        refactors += len(re.findall(r'\\bclass\\s+\\w+', content))
                except Exception as e:
                    pass
    
    # VDR Formula: (Vitality) / (Density / 100)
    # Vitality = governance_cycles + refactors
    vitality = governance_cycles + refactors
    
    if complexity == 0:
        vdr = 0.0
    else:
        vdr = vitality / (complexity / 100)
    
    print(f"🔥 Vitality: {vitality}")
    print(f"   - Governance Cycles: {governance_cycles}")
    print(f"   - Refactors (functions/classes): {refactors}")
    print(f"🪨 Density (LOC): {complexity}")
    print(f"   - Total Python files: {total_files}")
    print(f"🧱 VDR SCORE: {vdr:.3f}")
    print()
    
    if vdr < 1.0:
        print("⚠️  METABOLIC COLLAPSE IMMINENT. TRIGGERING SUBTRACTION.")
        print(f"   System is at {vdr*100:.1f}% efficiency")
    else:
        print("✅  SYSTEM IS ANTIFRAGILE.")
        print(f"   System has {(vdr-1)*100:.1f}% free energy")
    
    return vdr

if __name__ == "__main__":
    calculate_vdr()
'''
        
        # Write improved version
        with open(ouroboros_path, 'w') as f:
            f.write(new_content)
        
        self.fixes_applied.append("Fixed ouroboros.py governance cycle detection")
        print("   ✅ Fixed governance cycle detection")
        return True
    
    def clean_error_logs(self):
        """Clean up old error logs"""
        print("\n💉 HEALING AGENT: Cleaning error logs...")
        
        cleaned = 0
        log_files = []
        
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.endswith('.log'):
                    log_files.append(os.path.join(root, file))
        
        for log_file in log_files:
            try:
                # Check file size
                size = os.path.getsize(log_file)
                if size > 1024 * 1024:  # > 1MB
                    # Truncate large log files
                    with open(log_file, 'w') as f:
                        f.write(f"# Log cleaned by Healing Agent at {datetime.now()}\n")
                    cleaned += 1
                    print(f"   Cleaned: {log_file} ({size} bytes)")
            except Exception as e:
                pass
        
        if cleaned > 0:
            self.fixes_applied.append(f"Cleaned {cleaned} log files")
            print(f"   ✅ Cleaned {cleaned} log files")
        else:
            print("   No large log files to clean")
        
        return cleaned
    
    def fix_import_errors(self):
        """Detect and suggest fixes for import errors"""
        print("\n💉 HEALING AGENT: Checking for import errors...")
        
        import_issues = []
        
        for root, dirs, files in os.walk(self.base_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            # Check for common import issues
                            imports = re.findall(r'^import\s+(\w+)', content, re.MULTILINE)
                            from_imports = re.findall(r'^from\s+(\w+)', content, re.MULTILINE)
                            
                            all_imports = imports + from_imports
                            
                            # Check if imports are used
                            for imp in all_imports:
                                if content.count(imp) == 1:  # Only appears in import line
                                    import_issues.append(f"{file}: Unused import '{imp}'")
                    except Exception as e:
                        pass
        
        if import_issues:
            print(f"   Found {len(import_issues)} potential import issues")
            self.fixes_applied.append(f"Detected {len(import_issues)} import issues")
        else:
            print("   No import issues detected")
        
        return import_issues
    
    def generate_report(self):
        """Generate healing report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'fixes_applied': self.fixes_applied,
            'total_fixes': len(self.fixes_applied)
        }
        
        report_path = os.path.join(self.base_path, 'healing_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Healing report saved to: {report_path}")
        return report
    
    def run(self):
        """Run full healing process"""
        print("\n" + "="*60)
        print("💉 HEALING AGENT ACTIVATED")
        print("="*60)
        
        self.fix_ouroboros_detection()
        self.clean_error_logs()
        self.fix_import_errors()
        report = self.generate_report()
        
        print("\n✅ Healing complete!")
        print(f"   Total fixes applied: {len(self.fixes_applied)}")
        
        return report

if __name__ == "__main__":
    agent = HealingAgent(".")
    agent.run()
