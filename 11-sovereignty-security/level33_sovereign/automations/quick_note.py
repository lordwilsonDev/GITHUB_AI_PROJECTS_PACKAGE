#!/usr/bin/env python3
"""
Quick Note Automation

Rapidly create notes without opening apps manually.
Supports different note types and templates.

Usage:
  python3 automations/quick_note.py "My quick thought"
  python3 automations/quick_note.py --type todo "Buy groceries"
  python3 automations/quick_note.py --type meeting "Team sync notes"
"""

import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class QuickNote:
    def __init__(self):
        self.notes_dir = Path.home() / "level33_sovereign" / "quick_notes"
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        
        self.templates = {
            "general": self.general_template,
            "todo": self.todo_template,
            "meeting": self.meeting_template,
            "idea": self.idea_template,
            "bug": self.bug_template,
        }
    
    def general_template(self, content):
        """General note template"""
        return f"""{content}

---
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    def todo_template(self, content):
        """Todo list template"""
        items = content.split('\n')
        todo_items = '\n'.join([f"- [ ] {item.strip()}" for item in items if item.strip()])
        
        return f"""# Todo List

{todo_items}

---
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    def meeting_template(self, content):
        """Meeting notes template"""
        return f"""# Meeting Notes

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Topic:** {content}

## Attendees
- 

## Agenda
1. 

## Discussion
{content}

## Action Items
- [ ] 

## Next Steps
- 

---
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    def idea_template(self, content):
        """Idea capture template"""
        return f"""# 💡 Idea

## Core Concept
{content}

## Why This Matters
- 

## Potential Applications
- 

## Next Steps
- [ ] Research
- [ ] Prototype
- [ ] Validate

---
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    def bug_template(self, content):
        """Bug report template"""
        return f"""# 🐛 Bug Report

## Description
{content}

## Steps to Reproduce
1. 
2. 
3. 

## Expected Behavior


## Actual Behavior


## Environment
- OS: macOS
- Date: {datetime.now().strftime('%Y-%m-%d')}

## Status
- [ ] Reproduced
- [ ] Fixed
- [ ] Tested

---
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    def create_note(self, content, note_type="general", filename=None):
        """Create a new note"""
        # Get template
        template_func = self.templates.get(note_type, self.general_template)
        note_content = template_func(content)
        
        # Generate filename
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Create safe filename from content
            safe_content = "".join(c if c.isalnum() or c in (' ', '-') else '_' for c in content[:30])
            safe_content = safe_content.replace(' ', '_').strip('_')
            filename = f"{timestamp}_{note_type}_{safe_content}.md"
        
        filepath = self.notes_dir / filename
        
        # Write note
        with open(filepath, 'w') as f:
            f.write(note_content)
        
        print(f"✅ Note created: {filepath}")
        print(f"\nContent preview:")
        print("="*50)
        print(note_content[:200] + "..." if len(note_content) > 200 else note_content)
        print("="*50)
        
        return filepath
    
    def list_notes(self, limit=10):
        """List recent notes"""
        notes = sorted(self.notes_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not notes:
            print("No notes found")
            return
        
        print(f"\n📝 Recent Notes (showing {min(limit, len(notes))} of {len(notes)}):")
        print("="*70)
        
        for i, note in enumerate(notes[:limit], 1):
            mtime = datetime.fromtimestamp(note.stat().st_mtime)
            size = note.stat().st_size
            print(f"{i:2}. {note.name}")
            print(f"    Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')} | Size: {size} bytes")
        
        print("="*70)
    
    def search_notes(self, query):
        """Search notes for a query"""
        results = []
        
        for note_path in self.notes_dir.glob("*.md"):
            with open(note_path, 'r') as f:
                content = f.read()
                if query.lower() in content.lower():
                    results.append(note_path)
        
        if not results:
            print(f"No notes found matching '{query}'")
            return
        
        print(f"\n🔍 Found {len(results)} note(s) matching '{query}':")
        print("="*70)
        
        for i, note in enumerate(results, 1):
            print(f"{i}. {note.name}")
        
        print("="*70)

def main():
    parser = argparse.ArgumentParser(description='Quick Note Creator')
    parser.add_argument('content', nargs='?', help='Note content')
    parser.add_argument('--type', '-t', choices=['general', 'todo', 'meeting', 'idea', 'bug'],
                       default='general', help='Note type')
    parser.add_argument('--list', '-l', action='store_true', help='List recent notes')
    parser.add_argument('--search', '-s', help='Search notes')
    parser.add_argument('--filename', '-f', help='Custom filename')
    
    args = parser.parse_args()
    
    noter = QuickNote()
    
    if args.list:
        noter.list_notes()
    elif args.search:
        noter.search_notes(args.search)
    elif args.content:
        noter.create_note(args.content, args.type, args.filename)
    else:
        # Interactive mode
        print("\n📝 Quick Note Creator")
        print("="*50)
        print("Note Types: general, todo, meeting, idea, bug")
        print("="*50 + "\n")
        
        note_type = input("Note type [general]: ").strip() or "general"
        if note_type not in noter.templates:
            print(f"⚠️  Unknown type '{note_type}', using 'general'")
            note_type = "general"
        
        print("\nEnter note content (Ctrl+D when done):")
        print("-" * 50)
        
        try:
            lines = []
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
            
            content = '\n'.join(lines)
            if content.strip():
                noter.create_note(content, note_type)
            else:
                print("❌ No content provided")
        except KeyboardInterrupt:
            print("\n\nCancelled")

if __name__ == "__main__":
    main()
