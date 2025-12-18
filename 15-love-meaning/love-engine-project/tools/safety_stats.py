#!/usr/bin/env python3
"""
CLI tool to analyze Love Engine safety decision statistics
"""

import json
import os
from collections import Counter

def analyze_safety_decisions(file_path):
    """Analyze all safety decisions in the log file"""
    if not os.path.exists(file_path):
        print(f"Log file not found: {file_path}")
        return
    
    total_decisions = 0
    blocked_count = 0
    thermodynamic_stats = Counter()
    crc_values = []
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
                total_decisions += 1
                
                # Count blocked decisions
                thermo_adj = data.get('thermodynamic_adjustment', '')
                thermodynamic_stats[thermo_adj] += 1
                
                if thermo_adj == 'heating_blocked':
                    blocked_count += 1
                
                # Collect CRC values for distribution
                crc_raw = data.get('CRC_raw')
                if crc_raw is not None:
                    crc_values.append(crc_raw)
                    
            except json.JSONDecodeError as e:
                print(f"Warning: Could not parse line: {e}")
                continue
    
    # Print results
    print(f"Total Decisions: {total_decisions}")
    
    if total_decisions > 0:
        blocked_percentage = (blocked_count / total_decisions) * 100
        print(f"heating_blocked: {blocked_count} ({blocked_percentage:.1f}%)")
        
        print("\nThermodynamic Adjustment Distribution:")
        for adjustment, count in thermodynamic_stats.most_common():
            percentage = (count / total_decisions) * 100
            print(f"  {adjustment}: {count} ({percentage:.1f}%)")
        
        # CRC distribution (bonus feature)
        if crc_values:
            print("\nCRC_raw Distribution:")
            crc_counter = Counter(crc_values)
            for crc_val, count in crc_counter.most_common():
                percentage = (count / len(crc_values)) * 100
                print(f"  {crc_val}: {count} ({percentage:.1f}%)")
        else:
            print("\nCRC_raw Distribution: No CRC values found (all null)")
    else:
        print("No decisions found in log file.")

def main():
    log_file = 'logs/safety_decisions.jsonl'
    print(f"Analyzing safety decisions from {log_file}...")
    print()
    analyze_safety_decisions(log_file)

if __name__ == '__main__':
    main()
