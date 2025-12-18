#!/usr/bin/env python3
"""
Extract training dataset from Love Engine logs for MiniMind
"""

import json
import pandas as pd
import sys
from pathlib import Path

def extract_labeled_data(log_file):
    """Extract labeled entries from JSONL logs"""
    labeled_entries = []
    
    if not Path(log_file).exists():
        print(f"Error: {log_file} not found")
        return pd.DataFrame()
    
    with open(log_file, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    data = json.loads(line.strip())
                    if data.get('human_ok') is not None:
                        labeled_entries.append(data)
                except json.JSONDecodeError:
                    continue
    
    if not labeled_entries:
        print("No labeled entries found!")
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame(labeled_entries)
    
    # Feature engineering for MiniMind
    df['message_length'] = df['message'].str.len()
    df['answer_length'] = df['answer'].str.len()
    df['safety_triggered'] = df['safety_raw'] != 'safe'
    df['love_applied'] = df['love_vector_applied']
    df['thermo_cooled'] = df['thermodynamic_adjustment'] == 'cooled'
    
    # Target variable
    df['target'] = df['human_ok'].astype(int)
    
    return df

def main():
    log_file = sys.argv[1] if len(sys.argv) > 1 else 'love_logs.jsonl'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'minimind_dataset.csv'
    
    print(f"Extracting labeled data from {log_file}...")
    
    df = extract_labeled_data(log_file)
    
    if df.empty:
        print("No data to extract. Run labeling first!")
        sys.exit(1)
    
    # Save dataset
    df.to_csv(output_file, index=False)
    
    print(f"Dataset saved to {output_file}")
    print(f"Total samples: {len(df)}")
    print(f"Positive samples (human_ok=True): {df['target'].sum()}")
    print(f"Negative samples (human_ok=False): {len(df) - df['target'].sum()}")
    
    # Show feature summary
    print("\nFeature summary:")
    features = ['message_length', 'answer_length', 'safety_triggered', 'love_applied', 'thermo_cooled']
    for feature in features:
        if feature in df.columns:
            print(f"  {feature}: {df[feature].describe()}")

if __name__ == '__main__':
    main()
