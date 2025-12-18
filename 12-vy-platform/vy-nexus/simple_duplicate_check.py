#!/usr/bin/env python3
"""
Simple Duplicate File Checker for Vy-Nexus
"""

import os
import hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def get_file_hash(filepath):
    """Calculate SHA-256 hash of file content."""
    try:
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except:
        return None

def main():
    root_path = Path.home() / "vy-nexus"
    skip_dirs = {'.git', '__pycache__', 'venv', 'node_modules', '.pytest_cache', 'Lords Love'}
    
    files_by_name = defaultdict(list)
    files_by_hash = defaultdict(list)
    total_files = 0
    
    print(f"Scanning {root_path}...\n")
    
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for filename in files:
            if filename.startswith('.') or filename.endswith(('.pyc', '.log')):
                continue
            
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, root_path)
            
            try:
                stat_info = os.stat(filepath)
                file_size = stat_info.st_size
                
                file_info = {
                    'name': filename,
                    'path': rel_path,
                    'size': file_size
                }
                
                # Hash files under 10MB
                if file_size < 10 * 1024 * 1024:
                    file_hash = get_file_hash(filepath)
                    if file_hash:
                        file_info['hash'] = file_hash
                        files_by_hash[file_hash].append(file_info)
                
                files_by_name[filename].append(file_info)
                total_files += 1
            except:
                pass
    
    # Generate report
    report = []
    report.append("=" * 80)
    report.append("VY-NEXUS DUPLICATE FILE REPORT")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    report.append(f"\nTotal files scanned: {total_files}\n")
    
    # Find exact name duplicates
    name_dups = []
    for filename, file_list in files_by_name.items():
        if len(file_list) > 1:
            name_dups.append((filename, file_list))
    
    # Find content duplicates
    content_dups = []
    for file_hash, file_list in files_by_hash.items():
        if len(file_list) > 1:
            content_dups.append((file_hash, file_list))
    
    report.append(f"Exact name duplicates: {len(name_dups)}")
    report.append(f"Content duplicates: {len(content_dups)}\n")
    
    if name_dups:
        report.append("\n" + "=" * 80)
        report.append("EXACT NAME DUPLICATES")
        report.append("=" * 80)
        for filename, file_list in name_dups:
            report.append(f"\nFilename: {filename} ({len(file_list)} copies)")
            for f in file_list:
                report.append(f"  - {f['path']} ({f['size']} bytes)")
    else:
        report.append("\n✅ No exact name duplicates found!")
    
    if content_dups:
        report.append("\n" + "=" * 80)
        report.append("CONTENT DUPLICATES")
        report.append("=" * 80)
        for file_hash, file_list in content_dups:
            report.append(f"\nHash: {file_hash[:16]}... ({len(file_list)} files)")
            for f in file_list:
                report.append(f"  - {f['name']} -> {f['path']} ({f['size']} bytes)")
    else:
        report.append("\n✅ No content duplicates found!")
    
    report.append("\n" + "=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)
    
    # Write report
    report_text = "\n".join(report)
    report_path = Path.home() / "Lords Love" / "DUPLICATE_CHECK_REPORT.txt"
    with open(report_path, 'w') as f:
        f.write(report_text)
    
    # Print to console
    print(report_text)
    print(f"\nReport saved to: {report_path}")
    
    return 0 if (not name_dups and not content_dups) else 1

if __name__ == "__main__":
    exit(main())
