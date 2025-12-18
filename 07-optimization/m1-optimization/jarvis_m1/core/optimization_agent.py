#!/usr/bin/env python3
"""
Optimization Agent - Reduces system density and improves efficiency
"""

import os
import json
from datetime import datetime

class OptimizationAgent:
    def __init__(self, base_path="."):
        self.base_path = base_path
        self.optimizations = []
        self.density_reduced = 0
        
    def remove_duplicate_code(self):
        """Identify and report duplicate code"""
        print("\n⚡ OPTIMIZATION AGENT: Analyzing code duplication...")
        
        duplicates_found = 0
        files_analyzed = 0
        
        for root, dirs, files in os.walk(self.base_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            
            for file in files:
                if file.endswith('.py'):
                    files_analyzed += 1
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            
                            # Simple duplicate detection
                            seen_lines = {}
                            for i, line in enumerate(lines):
                                stripped = line.strip()
                                if stripped and len(stripped) > 20:
                                    if stripped in seen_lines:
                                        duplicates_found += 1
                                    else:
                                        seen_lines[stripped] = i
                    except Exception as e:
                        pass
        
        print(f"   Analyzed {files_analyzed} files")
        print(f"   Found {duplicates_found} duplicate lines")
        
        if duplicates_found > 0:
            self.optimizations.append(f"Identified {duplicates_found} duplicate lines")
        
        return duplicates_found
    
    def optimize_imports(self):
        """Optimize import statements"""
        print("\n⚡ OPTIMIZATION AGENT: Optimizing imports...")
        
        import re
        unused_imports = 0
        
        for root, dirs, files in os.walk(self.base_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            # Find all imports
                            imports = re.findall(r'^import\s+(\w+)', content, re.MULTILINE)
                            
                            for imp in imports:
                                # Check if import is used (appears more than once)
                                if content.count(imp) == 1:
                                    unused_imports += 1
                    except Exception as e:
                        pass
        
        print(f"   Found {unused_imports} potentially unused imports")
        
        if unused_imports > 0:
            self.optimizations.append(f"Identified {unused_imports} unused imports")
        
        return unused_imports
    
    def reduce_complexity(self):
        """Identify overly complex files"""
        print("\n⚡ OPTIMIZATION AGENT: Analyzing complexity...")
        
        complex_files = []
        total_complexity = 0
        
        for root, dirs, files in os.walk(self.base_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            line_count = len(lines)
                            total_complexity += line_count
                            
                            # Flag files over 500 lines
                            if line_count > 500:
                                complex_files.append({
                                    'file': file,
                                    'lines': line_count
                                })
                    except Exception as e:
                        pass
        
        print(f"   Total system complexity: {total_complexity} lines")
        print(f"   Found {len(complex_files)} complex files (>500 lines)")
        
        if complex_files:
            self.optimizations.append(f"Identified {len(complex_files)} files for refactoring")
            for cf in complex_files[:3]:  # Show top 3
                print(f"      - {cf['file']}: {cf['lines']} lines")
        
        return complex_files
    
    def clean_temporary_files(self):
        """Remove temporary and cache files"""
        print("\n⚡ OPTIMIZATION AGENT: Cleaning temporary files...")
        
        temp_patterns = ['.pyc', '__pycache__', '.DS_Store', '.tmp']
        cleaned = 0
        
        for root, dirs, files in os.walk(self.base_path):
            # Remove __pycache__ directories
            if '__pycache__' in dirs:
                pycache_path = os.path.join(root, '__pycache__')
                try:
                    import shutil
                    shutil.rmtree(pycache_path)
                    cleaned += 1
                    print(f"   Removed: {pycache_path}")
                except Exception as e:
                    pass
            
            # Remove temp files
            for file in files:
                if any(file.endswith(pattern) for pattern in temp_patterns):
                    filepath = os.path.join(root, file)
                    try:
                        os.remove(filepath)
                        cleaned += 1
                    except Exception as e:
                        pass
        
        if cleaned > 0:
            print(f"   ✅ Cleaned {cleaned} temporary files/directories")
            self.optimizations.append(f"Cleaned {cleaned} temporary files")
            self.density_reduced += cleaned
        else:
            print("   No temporary files to clean")
        
        return cleaned
    
    def generate_report(self):
        """Generate optimization report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'optimizations': self.optimizations,
            'density_reduced': self.density_reduced,
            'total_optimizations': len(self.optimizations)
        }
        
        report_path = os.path.join(self.base_path, 'optimization_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Optimization report saved to: {report_path}")
        return report
    
    def run(self):
        """Run full optimization process"""
        print("\n" + "="*60)
        print("⚡ OPTIMIZATION AGENT ACTIVATED")
        print("="*60)
        
        self.remove_duplicate_code()
        self.optimize_imports()
        self.reduce_complexity()
        self.clean_temporary_files()
        report = self.generate_report()
        
        print("\n✅ Optimization complete!")
        print(f"   Total optimizations: {len(self.optimizations)}")
        print(f"   Density reduced: {self.density_reduced} items")
        
        return report

if __name__ == "__main__":
    agent = OptimizationAgent(".")
    agent.run()
