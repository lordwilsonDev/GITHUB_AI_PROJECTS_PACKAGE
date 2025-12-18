#!/usr/bin/env python3
"""
Intelligent File Organizer Automation

Organizes files in Downloads folder by type:
- Images -> ~/Pictures/Downloads
- Documents -> ~/Documents/Downloads
- Archives -> ~/Documents/Archives
- Videos -> ~/Movies/Downloads

Usage: python3 automations/file_organizer.py
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import sys

class FileOrganizer:
    def __init__(self):
        self.home = Path.home()
        self.downloads = self.home / "Downloads"
        
        # Define categories and their extensions
        self.categories = {
            "Images": {
                "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".heic"],
                "destination": self.home / "Pictures" / "Downloads"
            },
            "Documents": {
                "extensions": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".pages"],
                "destination": self.home / "Documents" / "Downloads"
            },
            "Spreadsheets": {
                "extensions": [".xls", ".xlsx", ".csv", ".numbers"],
                "destination": self.home / "Documents" / "Spreadsheets"
            },
            "Archives": {
                "extensions": [".zip", ".tar", ".gz", ".rar", ".7z", ".dmg"],
                "destination": self.home / "Documents" / "Archives"
            },
            "Videos": {
                "extensions": [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv"],
                "destination": self.home / "Movies" / "Downloads"
            },
            "Audio": {
                "extensions": [".mp3", ".wav", ".aac", ".flac", ".m4a"],
                "destination": self.home / "Music" / "Downloads"
            },
            "Code": {
                "extensions": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".sh", ".json"],
                "destination": self.home / "Documents" / "Code"
            }
        }
        
        self.stats = {
            "total_files": 0,
            "organized": 0,
            "skipped": 0,
            "errors": 0
        }
    
    def create_directories(self):
        """Create destination directories if they don't exist"""
        print("📁 Creating destination directories...")
        for category, info in self.categories.items():
            info["destination"].mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {category}: {info['destination']}")
    
    def get_category(self, file_path):
        """Determine the category of a file based on extension"""
        extension = file_path.suffix.lower()
        for category, info in self.categories.items():
            if extension in info["extensions"]:
                return category
        return None
    
    def organize_file(self, file_path, dry_run=False):
        """Move a file to its appropriate category folder"""
        category = self.get_category(file_path)
        
        if category is None:
            self.stats["skipped"] += 1
            return False
        
        destination_dir = self.categories[category]["destination"]
        destination_path = destination_dir / file_path.name
        
        # Handle duplicate filenames
        if destination_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name_parts = file_path.stem, timestamp, file_path.suffix
            new_name = f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
            destination_path = destination_dir / new_name
        
        try:
            if dry_run:
                print(f"  [DRY RUN] Would move: {file_path.name} -> {category}/")
            else:
                shutil.move(str(file_path), str(destination_path))
                print(f"  ✅ Moved: {file_path.name} -> {category}/")
            
            self.stats["organized"] += 1
            return True
        except Exception as e:
            print(f"  ❌ Error moving {file_path.name}: {e}")
            self.stats["errors"] += 1
            return False
    
    def organize_downloads(self, dry_run=False):
        """Organize all files in Downloads folder"""
        print(f"\n📦 Scanning Downloads folder: {self.downloads}\n")
        
        if not self.downloads.exists():
            print("❌ Downloads folder not found!")
            return
        
        # Get all files (not directories)
        files = [f for f in self.downloads.iterdir() if f.is_file()]
        self.stats["total_files"] = len(files)
        
        if len(files) == 0:
            print("✅ Downloads folder is already clean!")
            return
        
        print(f"Found {len(files)} files to organize\n")
        
        # Create destination directories
        self.create_directories()
        
        print(f"\n📦 {'[DRY RUN] ' if dry_run else ''}Organizing files...\n")
        
        # Organize each file
        for file_path in files:
            self.organize_file(file_path, dry_run=dry_run)
        
        # Print summary
        self.print_summary(dry_run)
    
    def print_summary(self, dry_run=False):
        """Print organization summary"""
        print("\n" + "="*50)
        print(f"{'DRY RUN ' if dry_run else ''}ORGANIZATION SUMMARY")
        print("="*50)
        print(f"Total files scanned: {self.stats['total_files']}")
        print(f"Files organized: {self.stats['organized']}")
        print(f"Files skipped: {self.stats['skipped']}")
        print(f"Errors: {self.stats['errors']}")
        print("="*50 + "\n")

if __name__ == "__main__":
    organizer = FileOrganizer()
    
    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv
    
    if dry_run:
        print("👁️  DRY RUN MODE - No files will be moved\n")
    
    organizer.organize_downloads(dry_run=dry_run)
    
    if dry_run:
        print("\n💡 To actually organize files, run without --dry-run flag")
