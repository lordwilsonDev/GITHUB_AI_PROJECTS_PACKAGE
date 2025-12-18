#!/usr/bin/env python3
"""Validate cross-references in documentation files"""

import os
import re
from pathlib import Path

BASE_PATH = "/Users/lordwilson/vy-nexus"
DOCS = [
    "LEARNING_PATTERNS.md",
    "SIDE_NOTES_FOR_NEXT_JOB.md",
    "EFFICIENCY_IMPROVEMENTS.md",
    "AUTOMATION_SETUP.md",
    "TESTING_CHECKLIST.md",
    "NEW_EFFICIENCY_IMPROVEMENTS_2025-12-12.md"
]

def validate_file_references(content, doc_name):
    """Find and validate file path references"""
    # Pattern: /Users/lordwilson/... or relative paths in backticks
    path_pattern = r'`(/[^`]+)`|`([^/`]+\.(?:ts|py|sh|md|json|yaml))`'
    matches = re.findall(path_pattern, content)
    
    issues = []
    checked = set()
    
    for match in matches:
        path = match[0] or match[1]
        
        # Skip if already checked
        if path in checked:
            continue
        checked.add(path)
        
        # Determine full path
        if path.startswith('/'):
            full_path = path
        else:
            full_path = os.path.join(BASE_PATH, path)
        
        # Check if exists
        if not os.path.exists(full_path):
            issues.append(f"  ❌ Missing: {path}")
    
    return issues

def main():
    print("🔍 VALIDATING DOCUMENTATION CROSS-REFERENCES...\n")
    
    total_issues = 0
    total_checked = 0
    
    for doc in DOCS:
        doc_path = os.path.join(BASE_PATH, doc)
        if not os.path.exists(doc_path):
            print(f"⚠️  {doc}: File not found (skipping)")
            continue
        
        with open(doc_path, 'r') as f:
            content = f.read()
        
        issues = validate_file_references(content, doc)
        total_checked += 1
        
        if issues:
            print(f"📄 {doc}:")
            for issue in issues:
                print(issue)
            print()
            total_issues += len(issues)
        else:
            print(f"✅ {doc}: All references valid")
    
    print(f"\n{'='*70}")
    print(f"\n📊 SUMMARY:\n")
    print(f"  Documents checked: {total_checked}")
    print(f"  Issues found: {total_issues}")
    
    if total_issues == 0:
        print("\n✅ All documentation references are valid!")
        return 0
    else:
        print(f"\n⚠️  Found {total_issues} broken reference(s). Please fix.")
        return 1

if __name__ == "__main__":
    exit(main())
