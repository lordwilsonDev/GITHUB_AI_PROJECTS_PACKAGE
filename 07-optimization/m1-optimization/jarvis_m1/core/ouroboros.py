#!/usr/bin/env python3

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
                        lines = content.split('\n')
                        complexity += len(lines)
                        
                        # Detect governance cycles
                        content_lower = content.lower()
                        for keyword in governance_keywords:
                            if keyword in content_lower:
                                governance_cycles += 1
                                break
                        
                        # Count refactors (functions, classes)
                        refactors += len(re.findall(r'\bdef\s+\w+', content))
                        refactors += len(re.findall(r'\bclass\s+\w+', content))
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
