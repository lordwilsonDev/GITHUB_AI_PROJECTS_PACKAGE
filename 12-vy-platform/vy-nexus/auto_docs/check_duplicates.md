# check_duplicates.py

**Location**: `/Users/lordwilson/vy-nexus/check_duplicates.py`

Duplicate File Checker for Vy-Nexus
Scans the entire vy-nexus directory for duplicate files based on:
1. Exact filename matches in different directories
2. Content hash matches (same content, possibly different names)
3. Similar filenames (potential typos or versions)

## Functions

### `get_file_hash(filepath)`

Calculate SHA-256 hash of file content.

### `scan_directory(root_path)`

Scan directory and collect file information.

### `find_duplicates(files_by_name, files_by_hash)`

Identify duplicate files.

### `generate_report(duplicates, all_files, output_path)`

Generate detailed duplicate report.

### `main()`

Main execution.

## Dependencies

- `collections`
- `datetime`
- `hashlib`
- `json`
- `os`
- `pathlib`

---
*Auto-generated: 2025-12-18 12:51:47*
