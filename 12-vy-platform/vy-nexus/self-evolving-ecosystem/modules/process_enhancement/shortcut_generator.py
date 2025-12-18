#!/usr/bin/env python3
"""
Shortcut Generator Module
Generates keyboard shortcuts, aliases, and quick actions for common tasks.
Part of the Self-Evolving AI Ecosystem for vy-nexus.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict

@dataclass
class Shortcut:
    """Represents a keyboard shortcut or quick action."""
    shortcut_id: str
    timestamp: str
    shortcut_type: str  # keyboard, alias, script, menu, gesture
    name: str
    description: str
    
    # Trigger
    trigger: str  # e.g., "cmd+shift+p", "alias:gs", "script:backup"
    
    # Action
    action_type: str  # command, script, application, workflow
    action_command: str
    action_parameters: Dict[str, Any]
    
    # Context
    application: Optional[str] = None  # Specific app or "global"
    context_conditions: Optional[Dict[str, Any]] = None
    
    # Usage tracking
    usage_count: int = 0
    last_used: Optional[str] = None
    avg_time_saved_seconds: float = 0.0
    
    # Metadata
    category: str = "general"
    tags: List[str] = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.context_conditions is None:
            self.context_conditions = {}

@dataclass
class ShortcutUsage:
    """Tracks usage of a shortcut."""
    usage_id: str
    shortcut_id: str
    timestamp: str
    time_saved_seconds: float
    context: Dict[str, Any]
    success: bool

class ShortcutGenerator:
    """Generates and manages shortcuts for common tasks."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_dir = Path("/Users/lordwilson/vy-nexus/self-evolving-ecosystem")
        self.data_dir = self.base_dir / "data" / "process_enhancement" / "shortcuts"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Data files
        self.shortcuts_file = self.data_dir / "shortcuts.jsonl"
        self.usage_file = self.data_dir / "usage.jsonl"
        
        # Generated shortcuts directory
        self.generated_dir = self.base_dir / "generated" / "shortcuts"
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory storage
        self.shortcuts: List[Shortcut] = []
        self.usage_history: List[ShortcutUsage] = []
        
        # Shortcut templates
        self.templates = self._initialize_templates()
        
        self._load_data()
        self._initialized = True
    
    def _initialize_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize common shortcut templates."""
        return {
            'git_status': {
                'type': 'alias',
                'name': 'Git Status',
                'trigger': 'gs',
                'command': 'git status',
                'category': 'development',
                'time_saved': 3.0
            },
            'git_commit': {
                'type': 'alias',
                'name': 'Git Commit',
                'trigger': 'gc',
                'command': 'git commit -m',
                'category': 'development',
                'time_saved': 5.0
            },
            'git_push': {
                'type': 'alias',
                'name': 'Git Push',
                'trigger': 'gp',
                'command': 'git push',
                'category': 'development',
                'time_saved': 3.0
            },
            'open_project': {
                'type': 'keyboard',
                'name': 'Open Project',
                'trigger': 'cmd+shift+o',
                'command': 'open_project_dialog',
                'category': 'navigation',
                'time_saved': 5.0
            },
            'quick_search': {
                'type': 'keyboard',
                'name': 'Quick Search',
                'trigger': 'cmd+p',
                'command': 'quick_search',
                'category': 'navigation',
                'time_saved': 4.0
            },
            'terminal_here': {
                'type': 'menu',
                'name': 'Open Terminal Here',
                'trigger': 'right_click_menu',
                'command': 'open -a Terminal .',
                'category': 'navigation',
                'time_saved': 8.0
            },
            'screenshot_area': {
                'type': 'keyboard',
                'name': 'Screenshot Area',
                'trigger': 'cmd+shift+4',
                'command': 'screenshot_area',
                'category': 'productivity',
                'time_saved': 3.0
            },
            'clipboard_history': {
                'type': 'keyboard',
                'name': 'Clipboard History',
                'trigger': 'cmd+shift+v',
                'command': 'show_clipboard_history',
                'category': 'productivity',
                'time_saved': 10.0
            }
        }
    
    def _load_data(self):
        """Load existing data from files."""
        # Load shortcuts
        if self.shortcuts_file.exists():
            with open(self.shortcuts_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    self.shortcuts.append(Shortcut(**data))
        
        # Load usage history
        if self.usage_file.exists():
            with open(self.usage_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    self.usage_history.append(ShortcutUsage(**data))
    
    def create_shortcut(
        self,
        shortcut_type: str,
        name: str,
        description: str,
        trigger: str,
        action_type: str,
        action_command: str,
        action_parameters: Optional[Dict[str, Any]] = None,
        application: Optional[str] = None,
        category: str = "general",
        tags: Optional[List[str]] = None,
        avg_time_saved_seconds: float = 5.0
    ) -> Shortcut:
        """Create a new shortcut."""
        shortcut_id = f"shortcut_{len(self.shortcuts) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        shortcut = Shortcut(
            shortcut_id=shortcut_id,
            timestamp=datetime.now().isoformat(),
            shortcut_type=shortcut_type,
            name=name,
            description=description,
            trigger=trigger,
            action_type=action_type,
            action_command=action_command,
            action_parameters=action_parameters or {},
            application=application or "global",
            category=category,
            tags=tags or [],
            avg_time_saved_seconds=avg_time_saved_seconds
        )
        
        self.shortcuts.append(shortcut)
        
        # Save to file
        with open(self.shortcuts_file, 'a') as f:
            f.write(json.dumps(asdict(shortcut)) + '
')
        
        # Generate implementation file
        self._generate_shortcut_file(shortcut)
        
        return shortcut
    
    def _generate_shortcut_file(self, shortcut: Shortcut):
        """Generate implementation file for shortcut."""
        if shortcut.shortcut_type == "alias":
            self._generate_alias_file(shortcut)
        elif shortcut.shortcut_type == "script":
            self._generate_script_file(shortcut)
        elif shortcut.shortcut_type == "keyboard":
            self._generate_keyboard_config(shortcut)
    
    def _generate_alias_file(self, shortcut: Shortcut):
        """Generate shell alias file."""
        alias_file = self.generated_dir / "aliases.sh"
        
        alias_line = f"alias {shortcut.trigger}='{shortcut.action_command}'\n"
        
        # Append to alias file
        with open(alias_file, 'a') as f:
            f.write(f"# {shortcut.name} - {shortcut.description}\n")
            f.write(alias_line)
            f.write("\n")
    
    def _generate_script_file(self, shortcut: Shortcut):
        """Generate executable script file."""
        script_file = self.generated_dir / f"{shortcut.trigger}.sh"
        
        script_content = f"""#!/bin/bash
# {shortcut.name}
# {shortcut.description}
# Generated: {shortcut.timestamp}

{shortcut.action_command}
"""
        
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(script_file, 0o755)
    
    def _generate_keyboard_config(self, shortcut: Shortcut):
        """Generate keyboard shortcut configuration."""
        config_file = self.generated_dir / "keyboard_shortcuts.json"
        
        # Load existing config
        config = []
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
        
        # Add new shortcut
        config.append({
            'id': shortcut.shortcut_id,
            'name': shortcut.name,
            'description': shortcut.description,
            'trigger': shortcut.trigger,
            'command': shortcut.action_command,
            'application': shortcut.application,
            'enabled': shortcut.enabled
        })
        
        # Save config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def generate_from_template(self, template_name: str) -> Optional[Shortcut]:
        """Generate a shortcut from a template."""
        if template_name not in self.templates:
            return None
        
        template = self.templates[template_name]
        
        return self.create_shortcut(
            shortcut_type=template['type'],
            name=template['name'],
            description=f"Auto-generated from template: {template_name}",
            trigger=template['trigger'],
            action_type='command',
            action_command=template['command'],
            category=template['category'],
            avg_time_saved_seconds=template['time_saved']
        )
    
    def record_usage(
        self,
        shortcut_id: str,
        time_saved_seconds: float,
        context: Optional[Dict[str, Any]] = None,
        success: bool = True
    ) -> ShortcutUsage:
        """Record usage of a shortcut."""
        usage_id = f"usage_{len(self.usage_history) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        usage = ShortcutUsage(
            usage_id=usage_id,
            shortcut_id=shortcut_id,
            timestamp=datetime.now().isoformat(),
            time_saved_seconds=time_saved_seconds,
            context=context or {},
            success=success
        )
        
        self.usage_history.append(usage)
        
        # Update shortcut statistics
        for shortcut in self.shortcuts:
            if shortcut.shortcut_id == shortcut_id:
                shortcut.usage_count += 1
                shortcut.last_used = usage.timestamp
                
                # Update average time saved
                total_time = shortcut.avg_time_saved_seconds * (shortcut.usage_count - 1)
                shortcut.avg_time_saved_seconds = (total_time + time_saved_seconds) / shortcut.usage_count
                
                # Rewrite shortcuts file
                with open(self.shortcuts_file, 'w') as f:
                    for s in self.shortcuts:
                        f.write(json.dumps(asdict(s)) + '\n')
                break
        
        # Save usage
        with open(self.usage_file, 'a') as f:
            f.write(json.dumps(asdict(usage)) + '\n')
        
        return usage
    
    def get_most_used_shortcuts(self, limit: int = 10) -> List[Shortcut]:
        """Get most frequently used shortcuts."""
        sorted_shortcuts = sorted(
            self.shortcuts,
            key=lambda s: s.usage_count,
            reverse=True
        )
        return sorted_shortcuts[:limit]
    
    def get_shortcuts_by_category(self, category: str) -> List[Shortcut]:
        """Get all shortcuts in a category."""
        return [s for s in self.shortcuts if s.category == category]
    
    def get_time_saved_total(self) -> float:
        """Calculate total time saved by all shortcuts."""
        return sum(u.time_saved_seconds for u in self.usage_history if u.success)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about shortcuts."""
        total_shortcuts = len(self.shortcuts)
        enabled_shortcuts = sum(1 for s in self.shortcuts if s.enabled)
        total_usage = len(self.usage_history)
        successful_usage = sum(1 for u in self.usage_history if u.success)
        
        # Time saved
        total_time_saved = self.get_time_saved_total()
        
        # By category
        by_category = defaultdict(int)
        for s in self.shortcuts:
            by_category[s.category] += 1
        
        # By type
        by_type = defaultdict(int)
        for s in self.shortcuts:
            by_type[s.shortcut_type] += 1
        
        return {
            'total_shortcuts': total_shortcuts,
            'enabled_shortcuts': enabled_shortcuts,
            'total_usage': total_usage,
            'successful_usage': successful_usage,
            'success_rate': (successful_usage / total_usage * 100) if total_usage > 0 else 0,
            'total_time_saved_seconds': total_time_saved,
            'total_time_saved_hours': total_time_saved / 3600,
            'shortcuts_by_category': dict(by_category),
            'shortcuts_by_type': dict(by_type),
            'most_used': [asdict(s) for s in self.get_most_used_shortcuts(5)]
        }
    
    def suggest_shortcuts_from_patterns(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Suggest new shortcuts based on usage patterns."""
        suggestions = []
        
        for pattern in patterns:
            # Check if pattern is repetitive enough
            if pattern.get('frequency', 0) < 3:
                continue
            
            # Check if we already have a shortcut for this
            existing = any(
                s.action_command == pattern.get('action', '')
                for s in self.shortcuts
            )
            
            if existing:
                continue
            
            # Generate suggestion
            suggestion = {
                'pattern': pattern,
                'suggested_type': 'keyboard' if pattern.get('type') == 'ui' else 'alias',
                'suggested_trigger': self._suggest_trigger(pattern),
                'estimated_time_saved': pattern.get('duration', 5.0),
                'priority': pattern.get('frequency', 0) * pattern.get('duration', 5.0)
            }
            
            suggestions.append(suggestion)
        
        # Sort by priority
        suggestions.sort(key=lambda s: s['priority'], reverse=True)
        
        return suggestions
    
    def _suggest_trigger(self, pattern: Dict[str, Any]) -> str:
        """Suggest a trigger for a pattern."""
        # Simple heuristic: use first letters of action words
        action = pattern.get('action', '')
        words = action.split()
        
        if len(words) >= 2:
            trigger = ''.join(w[0] for w in words[:2])
        elif len(words) == 1:
            trigger = words[0][:2]
        else:
            trigger = 'sc'
        
        # Check if trigger already exists
        existing_triggers = {s.trigger for s in self.shortcuts}
        if trigger in existing_triggers:
            # Add number suffix
            i = 1
            while f"{trigger}{i}" in existing_triggers:
                i += 1
            trigger = f"{trigger}{i}"
        
        return trigger
    
    def export_shortcuts(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Export all shortcuts to a file."""
        if output_file is None:
            output_file = self.data_dir / f"shortcuts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'shortcuts': [asdict(s) for s in self.shortcuts],
            'templates': self.templates
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return export_data

def get_generator() -> ShortcutGenerator:
    """Get the singleton ShortcutGenerator instance."""
    return ShortcutGenerator()

if __name__ == "__main__":
    # Test the shortcut generator
    generator = get_generator()
    
    print("⌨️  Shortcut Generator Test")
    print("=" * 60)
    
    # Generate from templates
    print("\n1. Generating shortcuts from templates...")
    generator.generate_from_template('git_status')
    generator.generate_from_template('git_commit')
    generator.generate_from_template('quick_search')
    
    # Create custom shortcut
    print("\n2. Creating custom shortcut...")
    custom = generator.create_shortcut(
        shortcut_type="keyboard",
        name="Quick Note",
        description="Create a quick note",
        trigger="cmd+shift+n",
        action_type="command",
        action_command="open_quick_note",
        category="productivity",
        tags=["notes", "quick"],
        avg_time_saved_seconds=15.0
    )
    print(f"   Created: {custom.name} ({custom.trigger})")
    
    # Record usage
    print("\n3. Recording usage...")
    generator.record_usage(custom.shortcut_id, 12.0, {'note_type': 'meeting'})
    generator.record_usage(custom.shortcut_id, 18.0, {'note_type': 'idea'})
    
    # Get statistics
    print("\n4. Statistics:")
    stats = generator.get_statistics()
    print(f"   Total Shortcuts: {stats['total_shortcuts']}")
    print(f"   Total Usage: {stats['total_usage']}")
    print(f"   Time Saved: {stats['total_time_saved_seconds']:.1f}s ({stats['total_time_saved_hours']:.2f}h)")
    print(f"   Success Rate: {stats['success_rate']:.1f}%")
    
    # Most used
    print("\n5. Most Used Shortcuts:")
    most_used = generator.get_most_used_shortcuts(3)
    for i, shortcut in enumerate(most_used, 1):
        print(f"   {i}. {shortcut.name} - {shortcut.usage_count} uses")
    
    print("\n✅ Shortcut Generator test complete!")
    print(f"📁 Data stored in: {generator.data_dir}")
    print(f"📁 Generated files in: {generator.generated_dir}")
