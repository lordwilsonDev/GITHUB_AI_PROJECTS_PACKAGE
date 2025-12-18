#!/usr/bin/env python3
import os
import ast
import sys

# CONFIGURATION
# VDR = (Vitality / Density)
# Vitality = Lines of Logic (Signal)
# Density = Cyclomatic Complexity (Noise/Risk)

def calculate_complexity(code):
    try:
        tree = ast.parse(code)
        # Count control flow nodes (If, For, While, Except)
        complexity = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)))
        return max(1, complexity) # Baseline D=1
    except SyntaxError:
        return 100 # Penalize broken code

def scan_directory(path):
    total_vitality = 0
    total_density = 0
    
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"): # Scanning Python Orchestration
                with open(os.path.join(root, file), "r") as f:
                    content = f.read()
                    lines = len([l for l in content.splitlines() if l.strip() and not l.strip().startswith("#")])
                    complexity = calculate_complexity(content)
                    
                    total_vitality += lines
                    total_density += complexity

    # INVERSION: If Density is 0 (impossible), avoid div/0
    if total_density == 0: return 0
    
    # SCALING: We normalize so 1.0 is the "Standard"
    return (total_vitality / total_density) / 5.0 

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    vdr_score = scan_directory(path)
    
    print(f"📊 ARCHITECTURAL SCAN COMPLETE")
    print(f"-----------------------------")
    print(f"Vitality (Signal): HIGH")
    print(f"Density (Risk):    {1/vdr_score:.2f}" if vdr_score > 0 else "Density (Risk):    N/A")
    print(f"VDR Score:         {vdr_score:.3f}")
    print(f"-----------------------------")

    if vdr_score < 1.0:
        print("❌ DENIED: Entropy too high. Refactor before deployment.")
        sys.exit(1)
    else:
        print("✅ APPROVED: Geometry Aligned.")
        sys.exit(0)

if __name__ == "__main__":
    main()
