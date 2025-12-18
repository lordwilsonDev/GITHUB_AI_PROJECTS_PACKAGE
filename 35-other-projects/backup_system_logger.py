#!/usr/bin/env python3
"""
Vy Cognitive Sovereignty Stack - Comprehensive Backup Logger
Date: December 17, 2025
Purpose: Log all backup operations with timestamps, status, and verification
"""

import os
import json
import datetime
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Any

class BackupLogger:
    def __init__(self, log_dir="/Users/lordwilson/backup_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"backup_session_{self.session_id}.json"
        self.text_log = self.log_dir / f"backup_session_{self.session_id}.log"
        self.operations = []
        
    def log_operation(self, operation_type: str, target: str, status: str, 
                     details: Dict[str, Any] = None):
        """Log a backup operation with full details"""
        timestamp = datetime.datetime.now().isoformat()
        operation = {
            "timestamp": timestamp,
            "operation_type": operation_type,
            "target": target,
            "status": status,
            "details": details or {}
        }
        self.operations.append(operation)
        
        # Write to text log immediately
        with open(self.text_log, 'a') as f:
            f.write(f"[{timestamp}] {operation_type}: {target} - {status}\n")
            if details:
                f.write(f"  Details: {json.dumps(details, indent=2)}\n")
        
        # Update JSON log
        self._save_json()
        
    def log_directory_scan(self, directory: str, file_count: int, total_size: int):
        """Log directory scanning results"""
        self.log_operation(
            "DIRECTORY_SCAN",
            directory,
            "COMPLETE",
            {
                "file_count": file_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            }
        )
        
    def log_git_operation(self, repo_path: str, operation: str, result: str):
        """Log git operations (init, add, commit, push)"""
        self.log_operation(
            f"GIT_{operation.upper()}",
            repo_path,
            result,
            {"git_operation": operation}
        )
        
    def log_file_hash(self, file_path: str, hash_value: str):
        """Log file hash for verification"""
        self.log_operation(
            "FILE_HASH",
            file_path,
            "COMPUTED",
            {"sha256": hash_value}
        )
        
    def log_github_push(self, repo_name: str, commit_hash: str, status: str):
        """Log GitHub push operations"""
        self.log_operation(
            "GITHUB_PUSH",
            repo_name,
            status,
            {"commit_hash": commit_hash}
        )
        
    def log_verification(self, target: str, verification_type: str, result: bool):
        """Log verification checks"""
        self.log_operation(
            "VERIFICATION",
            target,
            "PASSED" if result else "FAILED",
            {"verification_type": verification_type}
        )
        
    def log_error(self, operation: str, target: str, error_message: str):
        """Log errors"""
        self.log_operation(
            "ERROR",
            target,
            "FAILED",
            {
                "operation": operation,
                "error": error_message
            }
        )
        
    def _save_json(self):
        """Save operations to JSON file"""
        with open(self.log_file, 'w') as f:
            json.dump({
                "session_id": self.session_id,
                "start_time": self.operations[0]["timestamp"] if self.operations else None,
                "operations": self.operations,
                "total_operations": len(self.operations)
            }, f, indent=2)
            
    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary of all operations"""
        summary = {
            "session_id": self.session_id,
            "total_operations": len(self.operations),
            "operations_by_type": {},
            "operations_by_status": {},
            "errors": []
        }
        
        for op in self.operations:
            op_type = op["operation_type"]
            status = op["status"]
            
            summary["operations_by_type"][op_type] = \
                summary["operations_by_type"].get(op_type, 0) + 1
            summary["operations_by_status"][status] = \
                summary["operations_by_status"].get(status, 0) + 1
                
            if status == "FAILED":
                summary["errors"].append({
                    "operation": op_type,
                    "target": op["target"],
                    "details": op.get("details", {})
                })
                
        return summary
        
    def save_summary(self):
        """Save summary to file"""
        summary = self.generate_summary()
        summary_file = self.log_dir / f"backup_summary_{self.session_id}.json"
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
            
        # Also create human-readable summary
        text_summary = self.log_dir / f"backup_summary_{self.session_id}.txt"
        with open(text_summary, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("VY COGNITIVE SOVEREIGNTY STACK - BACKUP SUMMARY\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Session ID: {summary['session_id']}\n")
            f.write(f"Total Operations: {summary['total_operations']}\n\n")
            
            f.write("Operations by Type:\n")
            for op_type, count in summary["operations_by_type"].items():
                f.write(f"  {op_type}: {count}\n")
            
            f.write("\nOperations by Status:\n")
            for status, count in summary["operations_by_status"].items():
                f.write(f"  {status}: {count}\n")
                
            if summary["errors"]:
                f.write("\n" + "=" * 80 + "\n")
                f.write("ERRORS ENCOUNTERED:\n")
                f.write("=" * 80 + "\n")
                for error in summary["errors"]:
                    f.write(f"\nOperation: {error['operation']}\n")
                    f.write(f"Target: {error['target']}\n")
                    f.write(f"Details: {json.dumps(error['details'], indent=2)}\n")
                    
        return summary

def compute_file_hash(file_path: str) -> str:
    """Compute SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def scan_directory(directory: str) -> Dict[str, Any]:
    """Scan directory and return statistics"""
    total_files = 0
    total_size = 0
    file_types = {}
    
    for root, dirs, files in os.walk(directory):
        # Skip hidden directories and common excludes
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                   ['node_modules', '__pycache__', 'venv', '.venv', '.git']]
        
        for file in files:
            if not file.startswith('.'):
                total_files += 1
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    total_size += size
                    
                    ext = os.path.splitext(file)[1]
                    file_types[ext] = file_types.get(ext, 0) + 1
                except:
                    pass
                    
    return {
        "total_files": total_files,
        "total_size": total_size,
        "file_types": file_types
    }

if __name__ == "__main__":
    # Test the logger
    logger = BackupLogger()
    logger.log_operation("TEST", "backup_system_logger.py", "INITIALIZED")
    print(f"Logger initialized. Session ID: {logger.session_id}")
    print(f"Log files created in: {logger.log_dir}")
    print(f"  - JSON log: {logger.log_file}")
    print(f"  - Text log: {logger.text_log}")
