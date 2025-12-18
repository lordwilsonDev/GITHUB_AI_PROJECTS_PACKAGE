"""
Sovereign Keep Protocol - Backup & Export System
Implements pre-execution backup and restore functionality.
"""

import json
import datetime
from pathlib import Path
from typing import Dict, List


class BackupManager:
    """
    Handles backup and export of Google Keep notes to local storage.
    """
    
    def __init__(self, keep_client, export_dir="exports"):
        """
        Initialize backup manager.
        
        Args:
            keep_client: Authenticated gkeepapi.Keep instance
            export_dir: Directory for storing backups
        """
        self.keep = keep_client
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True)
    
    def export_all(self, format='json') -> Path:
        """
        Export all notes to JSON format.
        
        Args:
            format: Export format ('json' or 'markdown')
            
        Returns:
            Path: Path to the backup file
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == 'json':
            return self._export_json(timestamp)
        elif format == 'markdown':
            return self._export_markdown(timestamp)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_json(self, timestamp: str) -> Path:
        """
        Export notes to JSON format with full metadata.
        
        Args:
            timestamp: Timestamp string for filename
            
        Returns:
            Path: Path to the JSON backup file
        """
        print("[Backup] Exporting notes to JSON...")
        
        notes_data = []
        for note in self.keep.all():
            note_dict = {
                'id': note.id,
                'title': note.title,
                'text': note.text,
                'archived': note.archived,
                'trashed': note.trashed,
                'pinned': note.pinned,
                'color': str(note.color),
                'labels': [label.name for label in note.labels.all()],
                'timestamps': {
                    'created': note.timestamps.created.isoformat(),
                    'updated': note.timestamps.updated.isoformat(),
                },
            }
            notes_data.append(note_dict)
        
        backup_file = self.export_dir / f"keep_backup_{timestamp}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(notes_data, f, indent=2, ensure_ascii=False)
        
        print(f"[Backup] ✓ Exported {len(notes_data)} notes to {backup_file}")
        return backup_file
    
    def _export_markdown(self, timestamp: str) -> Path:
        """
        Export notes to individual Markdown files.
        
        Args:
            timestamp: Timestamp string for directory name
            
        Returns:
            Path: Path to the backup directory
        """
        print("[Backup] Exporting notes to Markdown...")
        
        backup_dir = self.export_dir / f"keep_markdown_{timestamp}"
        backup_dir.mkdir(exist_ok=True)
        
        count = 0
        for note in self.keep.all():
            if note.trashed:
                continue
            
            # Create safe filename from title
            safe_title = "".join(c for c in note.title if c.isalnum() or c in (' ', '-', '_')).strip()
            if not safe_title:
                safe_title = f"note_{note.id[:8]}"
            
            filename = backup_dir / f"{safe_title}.md"
            
            # Handle duplicate filenames
            counter = 1
            while filename.exists():
                filename = backup_dir / f"{safe_title}_{counter}.md"
                counter += 1
            
            # Write markdown file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# {note.title}\n\n")
                f.write(note.text)
                f.write("\n\n---\n")
                f.write(f"*Created: {note.timestamps.created}*\n")
                f.write(f"*Updated: {note.timestamps.updated}*\n")
                if note.labels.all():
                    labels = ", ".join(label.name for label in note.labels.all())
                    f.write(f"*Labels: {labels}*\n")
            
            count += 1
        
        print(f"[Backup] ✓ Exported {count} notes to {backup_dir}")
        return backup_dir
    
    def restore_from_json(self, backup_file: Path):
        """
        Restore notes from JSON backup (NOT IMPLEMENTED - requires careful handling).
        
        Args:
            backup_file: Path to JSON backup file
        """
        raise NotImplementedError(
            "Restore functionality requires careful implementation to avoid duplicates. "
            "Use manual import via Google Keep web interface for now."
        )


# Example usage
if __name__ == "__main__":
    import sys
    from auth import SovereignAuth
    
    if len(sys.argv) < 2:
        print("Usage: python backup.py <your-email@gmail.com> [json|markdown]")
        sys.exit(1)
    
    email = sys.argv[1]
    format_type = sys.argv[2] if len(sys.argv) > 2 else 'json'
    
    # Authenticate
    auth = SovereignAuth(email)
    keep = auth.login()
    auth.sync()
    
    # Backup
    backup_mgr = BackupManager(keep)
    backup_path = backup_mgr.export_all(format=format_type)
    
    print(f"\n✓ Backup complete: {backup_path}")
