#!/usr/bin/env python3
"""
Duplicate File Checker for Vy-Nexus
Scans the entire vy-nexus directory for duplicate files based on:
1. Exact filename matches in different directories
2. Content hash matches (same content, possibly different names)
3. Similar filenames (potential typos or versions)
"""

import os
import hashlib
import json
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
    except Exception as e:
        return None

def scan_directory(root_path):
    """Scan directory and collect file information."""
    files_by_name = defaultdict(list)
    files_by_hash = defaultdict(list)
    all_files = []
    
    # Directories to skip
    skip_dirs = {
        '.git', '__pycache__', 'venv', 'node_modules', 
        '.pytest_cache', 'Lords Love', '.DS_Store'
    }
    
    print(f"Scanning {root_path}...")
    
    for root, dirs, files in os.walk(root_path):
        # Remove skip directories from dirs list
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for filename in files:
            # Skip hidden files and specific file types
            if filename.startswith('.') or filename.endswith(('.pyc', '.log')):
                continue
                
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, root_path)
            
            # Get file info
            try:
                stat_info = os.stat(filepath)
                file_size = stat_info.st_size
                mod_time = datetime.fromtimestamp(stat_info.st_mtime)
                
                file_info = {
                    'name': filename,
                    'path': rel_path,
                    'full_path': filepath,
                    'size': file_size,
                    'modified': mod_time.isoformat(),
                    'hash': None
                }
                
                # Calculate hash for files under 10MB
                if file_size < 10 * 1024 * 1024:
                    file_hash = get_file_hash(filepath)
                    if file_hash:
                        file_info['hash'] = file_hash
                        files_by_hash[file_hash].append(file_info)
                
                files_by_name[filename].append(file_info)
                all_files.append(file_info)
                
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
    
    return files_by_name, files_by_hash, all_files

def find_duplicates(files_by_name, files_by_hash):
    """Identify duplicate files."""
    duplicates = {
        'exact_name_duplicates': [],
        'content_duplicates': [],
        'similar_names': []
    }
    
    # Find exact name duplicates
    for filename, file_list in files_by_name.items():
        if len(file_list) > 1:
            duplicates['exact_name_duplicates'].append({
                'filename': filename,
                'count': len(file_list),
                'locations': [f['path'] for f in file_list],
                'files': file_list
            })
    
    # Find content duplicates
    for file_hash, file_list in files_by_hash.items():
        if len(file_list) > 1:
            duplicates['content_duplicates'].append({
                'hash': file_hash,
                'count': len(file_list),
                'files': file_list
            })
    
    # Find similar names (potential typos or versions)
    filenames = list(files_by_name.keys())
    for i, name1 in enumerate(filenames):
        for name2 in filenames[i+1:]:
            # Check for similar names (simple heuristic)
            if name1.lower().replace('_', '') == name2.lower().replace('_', ''):
                duplicates['similar_names'].append({
                    'name1': name1,
                    'name2': name2,
                    'files1': files_by_name[name1],
                    'files2': files_by_name[name2]
                })
    
    return duplicates

def generate_report(duplicates, all_files, output_path):
    """Generate detailed duplicate report."""
    report = []
    report.append("=" * 80)
    report.append("VY-NEXUS DUPLICATE FILE REPORT")
    report.append(f"Generated: {datetime.now().isoformat()}")
    report.append("=" * 80)
    report.append("")
    
    # Summary
    report.append("SUMMARY")
    report.append("-" * 80)
    report.append(f"Total files scanned: {len(all_files)}")
    report.append(f"Exact name duplicates: {len(duplicates['exact_name_duplicates'])}")
    report.append(f"Content duplicates: {len(duplicates['content_duplicates'])}")
    report.append(f"Similar name pairs: {len(duplicates['similar_names'])}")
    report.append("")
    
    # Exact name duplicates
    if duplicates['exact_name_duplicates']:
        report.append("\n" + "=" * 80)
        report.append("EXACT NAME DUPLICATES")
        report.append("=" * 80)
        for dup in duplicates['exact_name_duplicates']:
            report.append(f"\nFilename: {dup['filename']}")
            report.append(f"Count: {dup['count']} copies")
            report.append("Locations:")
            for f in dup['files']:
                report.append(f"  - {f['path']}")
                report.append(f"    Size: {f['size']} bytes, Modified: {f['modified']}")
    else:
        report.append("\n✅ No exact name duplicates found!")
    
    # Content duplicates
    if duplicates['content_duplicates']:
        report.append("\n" + "=" * 80)
        report.append("CONTENT DUPLICATES (Same content, possibly different names)")
        report.append("=" * 80)
        for dup in duplicates['content_duplicates']:
            report.append(f"\nHash: {dup['hash'][:16]}...")
            report.append(f"Count: {dup['count']} files with identical content")
            report.append("Files:")
            for f in dup['files']:
                report.append(f"  - {f['name']} ({f['path']})")
                report.append(f"    Size: {f['size']} bytes, Modified: {f['modified']}")
    else:
        report.append("\n✅ No content duplicates found!")
    
    # Similar names
    if duplicates['similar_names']:
        report.append("\n" + "=" * 80)
        report.append("SIMILAR NAMES (Potential typos or versions)")
        report.append("=" * 80)
        for sim in duplicates['similar_names']:
            report.append(f"\nSimilar pair:")
            report.append(f"  1. {sim['name1']}")
            for f in sim['files1']:
                report.append(f"     - {f['path']}")
            report.append(f"  2. {sim['name2']}")
            for f in sim['files2']:
                report.append(f"     - {f['path']}")
    else:
        report.append("\n✅ No similar name pairs found!")
    
    report.append("\n" + "=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)
    
    # Write report
    report_text = "\n".join(report)
    with open(output_path, 'w') as f:
        f.write(report_text)
    
    # Also save JSON for programmatic access
    json_path = output_path.replace('.txt', '.json')
    with open(json_path, 'w') as f:
        json.dump(duplicates, f, indent=2, default=str)
    
    return report_text

def main():
    """Main execution."""
    root_path = Path(__file__).parent
    print(f"Checking for duplicates in: {root_path}")
    print("This may take a few moments...\n")
    
    # Scan directory
    files_by_name, files_by_hash, all_files = scan_directory(root_path)
    
    # Find duplicates
    duplicates = find_duplicates(files_by_name, files_by_hash)
    
    # Generate report
    report_path = root_path / "Lords Love" / "DUPLICATE_CHECK_REPORT.txt"
    report_text = generate_report(duplicates, all_files, report_path)
    
    # Print summary to console
    print("\n" + "=" * 80)
    print("DUPLICATE CHECK COMPLETE")
    print("=" * 80)
    print(f"Total files scanned: {len(all_files)}")
    print(f"Exact name duplicates: {len(duplicates['exact_name_duplicates'])}")
    print(f"Content duplicates: {len(duplicates['content_duplicates'])}")
    print(f"Similar name pairs: {len(duplicates['similar_names'])}")
    print(f"\nDetailed report saved to: {report_path}")
    print("=" * 80)
    
    # Return exit code based on findings
    if (duplicates['exact_name_duplicates'] or 
        duplicates['content_duplicates'] or 
        duplicates['similar_names']):
        return 1  # Duplicates found
    return 0  # No duplicates

if __name__ == "__main__":
    exit(main())
