#!/usr/bin/env python3
"""
Google Takeout Parser for Sovereign Keep Protocol

Parses exported Google Keep data from Google Takeout and converts it
into a format compatible with the semantic analysis engine.

Google Takeout exports Keep notes as HTML files with JSON metadata.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import html
import re


@dataclass
class TakeoutNote:
    """Represents a note from Google Takeout export."""
    id: str
    title: str
    text: str
    labels: List[str]
    color: str
    archived: bool
    trashed: bool
    pinned: bool
    created: datetime
    updated: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'text': self.text,
            'labels': self.labels,
            'color': self.color,
            'archived': self.archived,
            'trashed': self.trashed,
            'pinned': self.pinned,
            'created': self.created.isoformat(),
            'updated': self.updated.isoformat()
        }


class TakeoutParser:
    """Parser for Google Takeout Keep exports."""
    
    def __init__(self, takeout_path: str):
        """
        Initialize parser with path to Takeout export.
        
        Args:
            takeout_path: Path to the 'Takeout/Keep' directory
        """
        self.takeout_path = Path(takeout_path)
        if not self.takeout_path.exists():
            raise FileNotFoundError(f"Takeout path not found: {takeout_path}")
    
    def parse_all_notes(self) -> List[TakeoutNote]:
        """
        Parse all notes from the Takeout export.
        
        Returns:
            List of TakeoutNote objects
        """
        notes = []
        
        # Google Takeout exports notes as .html files with .json metadata
        html_files = list(self.takeout_path.glob('*.html'))
        
        print(f"Found {len(html_files)} note files in Takeout export")
        
        for html_file in html_files:
            try:
                note = self._parse_note(html_file)
                if note:
                    notes.append(note)
            except Exception as e:
                print(f"Warning: Failed to parse {html_file.name}: {e}")
                continue
        
        print(f"Successfully parsed {len(notes)} notes")
        return notes
    
    def _parse_note(self, html_file: Path) -> Optional[TakeoutNote]:
        """
        Parse a single note from HTML and JSON files.
        
        Args:
            html_file: Path to the .html file
            
        Returns:
            TakeoutNote object or None if parsing fails
        """
        # Read HTML content
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Look for corresponding JSON file
        json_file = html_file.with_suffix('.json')
        metadata = {}
        
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        
        # Extract title and text from HTML
        title, text = self._extract_content_from_html(html_content)
        
        # Extract metadata
        note_id = html_file.stem  # Use filename as ID
        labels = metadata.get('labels', [])
        if isinstance(labels, list):
            labels = [label.get('name', '') for label in labels if isinstance(label, dict)]
        
        color = metadata.get('color', 'DEFAULT')
        archived = metadata.get('isArchived', False)
        trashed = metadata.get('isTrashed', False)
        pinned = metadata.get('isPinned', False)
        
        # Parse timestamps
        created = self._parse_timestamp(metadata.get('createdTimestampUsec', 0))
        updated = self._parse_timestamp(metadata.get('userEditedTimestampUsec', 0))
        
        return TakeoutNote(
            id=note_id,
            title=title,
            text=text,
            labels=labels,
            color=color,
            archived=archived,
            trashed=trashed,
            pinned=pinned,
            created=created,
            updated=updated
        )
    
    def _extract_content_from_html(self, html_content: str) -> tuple:
        """
        Extract title and text from HTML content.
        
        Args:
            html_content: Raw HTML string
            
        Returns:
            Tuple of (title, text)
        """
        # Extract title (usually in first heading)
        title_match = re.search(r'<div class="title">(.+?)</div>', html_content, re.DOTALL)
        title = ''
        if title_match:
            title = html.unescape(title_match.group(1).strip())
            title = re.sub(r'<[^>]+>', '', title)  # Remove any HTML tags
        
        # Extract text content (usually in content div)
        text_match = re.search(r'<div class="content">(.+?)</div>', html_content, re.DOTALL)
        text = ''
        if text_match:
            text = html.unescape(text_match.group(1).strip())
            # Convert <br> to newlines
            text = re.sub(r'<br\s*/?>', '\n', text)
            # Remove other HTML tags
            text = re.sub(r'<[^>]+>', '', text)
            # Clean up whitespace
            text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return title.strip(), text.strip()
    
    def _parse_timestamp(self, usec: int) -> datetime:
        """
        Parse timestamp from microseconds since epoch.
        
        Args:
            usec: Microseconds since Unix epoch
            
        Returns:
            datetime object
        """
        if usec == 0:
            return datetime.now()
        return datetime.fromtimestamp(usec / 1_000_000)
    
    def export_to_json(self, notes: List[TakeoutNote], output_path: str):
        """
        Export parsed notes to JSON file.
        
        Args:
            notes: List of TakeoutNote objects
            output_path: Path to output JSON file
        """
        data = [note.to_dict() for note in notes]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(notes)} notes to {output_path}")
    
    def filter_active_notes(self, notes: List[TakeoutNote]) -> List[TakeoutNote]:
        """
        Filter to only active (non-archived, non-trashed) notes.
        
        Args:
            notes: List of all notes
            
        Returns:
            List of active notes only
        """
        active = [n for n in notes if not n.archived and not n.trashed]
        print(f"Filtered to {len(active)} active notes (from {len(notes)} total)")
        return active


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python takeout_parser.py <path-to-takeout-keep-folder>")
        print("Example: python takeout_parser.py ~/Downloads/Takeout/Keep")
        sys.exit(1)
    
    takeout_path = sys.argv[1]
    
    try:
        parser = TakeoutParser(takeout_path)
        notes = parser.parse_all_notes()
        
        # Export to JSON
        output_path = '../data/takeout_notes.json'
        parser.export_to_json(notes, output_path)
        
        # Show statistics
        active_notes = parser.filter_active_notes(notes)
        archived = len([n for n in notes if n.archived])
        trashed = len([n for n in notes if n.trashed])
        
        print("\n=== Statistics ===")
        print(f"Total notes: {len(notes)}")
        print(f"Active notes: {len(active_notes)}")
        print(f"Archived notes: {archived}")
        print(f"Trashed notes: {trashed}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
