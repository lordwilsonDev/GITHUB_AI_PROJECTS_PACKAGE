#!/usr/bin/env python3
"""
Shortcut Designer
Designs and creates keyboard shortcuts and quick actions for common workflows.

This module:
- Analyzes frequently used actions
- Suggests optimal keyboard shortcuts
- Creates automation shortcuts
- Manages shortcut conflicts
- Generates quick action scripts
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from collections import Counter, defaultdict
import string


class ShortcutDesigner:
    """Designs shortcuts and quick actions for workflows."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/optimization"):
        self.data_dir = os.path.expanduser(data_dir)
        self.shortcuts_dir = os.path.expanduser("~/vy-nexus/shortcuts")
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.shortcuts_dir, exist_ok=True)
        
        # Data files
        self.shortcuts_file = os.path.join(self.data_dir, "shortcuts.json")
        self.actions_file = os.path.join(self.data_dir, "quick_actions.json")
        self.usage_file = os.path.join(self.data_dir, "shortcut_usage.json")
        self.conflicts_file = os.path.join(self.data_dir, "shortcut_conflicts.json")
        self.statistics_file = os.path.join(self.data_dir, "designer_statistics.json")
        
        # Load existing data
        self.shortcuts = self._load_json(self.shortcuts_file, [])
        self.actions = self._load_json(self.actions_file, [])
        self.usage = self._load_json(self.usage_file, [])
        self.conflicts = self._load_json(self.conflicts_file, [])
        self.statistics = self._load_json(self.statistics_file, {
            "total_shortcuts_created": 0,
            "active_shortcuts": 0,
            "total_uses": 0,
            "time_saved": 0,
            "conflicts_resolved": 0
        })
        
        # Reserved system shortcuts (macOS)
        self.system_shortcuts = {
            "cmd+c", "cmd+v", "cmd+x", "cmd+z", "cmd+a", "cmd+s",
            "cmd+w", "cmd+q", "cmd+n", "cmd+o", "cmd+p", "cmd+f",
            "cmd+tab", "cmd+space", "cmd+shift+3", "cmd+shift+4"
        }
    
    def _load_json(self, filepath: str, default: Any) -> Any:
        """Load JSON data from file."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
        return default
    
    def _save_json(self, filepath: str, data: Any) -> None:
        """Save JSON data to file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")
    
    def analyze_action_frequency(self, actions: List[Dict]) -> List[Dict]:
        """Analyze action frequency to suggest shortcuts."""
        action_counts = Counter()
        action_details = defaultdict(lambda: {"count": 0, "total_time": 0, "examples": []})
        
        for action in actions:
            action_type = action.get("type", "unknown")
            action_counts[action_type] += 1
            
            action_details[action_type]["count"] += 1
            action_details[action_type]["total_time"] += action.get("duration", 0)
            
            if len(action_details[action_type]["examples"]) < 3:
                action_details[action_type]["examples"].append(action.get("description", ""))
        
        # Generate suggestions
        suggestions = []
        for action_type, count in action_counts.most_common(20):
            if count >= 5:  # Threshold for shortcut suggestion
                details = action_details[action_type]
                avg_time = details["total_time"] / details["count"] if details["count"] > 0 else 0
                
                suggestions.append({
                    "action_type": action_type,
                    "frequency": count,
                    "average_time": avg_time,
                    "total_time": details["total_time"],
                    "priority": self._calculate_priority(count, avg_time),
                    "suggested_shortcut": self._suggest_shortcut(action_type),
                    "examples": details["examples"]
                })
        
        return sorted(suggestions, key=lambda x: x["priority"], reverse=True)
    
    def _calculate_priority(self, frequency: int, avg_time: float) -> float:
        """Calculate priority score for shortcut creation."""
        # Higher frequency and longer time = higher priority
        return (frequency * 0.7) + (avg_time * 0.3)
    
    def _suggest_shortcut(self, action_type: str) -> str:
        """Suggest a keyboard shortcut based on action type."""
        # Extract first letters
        words = action_type.replace("_", " ").split()
        initials = "".join(word[0] for word in words if word)
        
        # Try different modifier combinations
        modifiers = [
            "cmd+shift",
            "cmd+opt",
            "cmd+ctrl",
            "cmd+shift+opt"
        ]
        
        for modifier in modifiers:
            for char in initials:
                shortcut = f"{modifier}+{char.lower()}"
                if not self._is_shortcut_taken(shortcut):
                    return shortcut
        
        # Fallback: try function keys
        for i in range(1, 13):
            shortcut = f"cmd+f{i}"
            if not self._is_shortcut_taken(shortcut):
                return shortcut
        
        return "custom"
    
    def _is_shortcut_taken(self, shortcut: str) -> bool:
        """Check if a shortcut is already taken."""
        if shortcut in self.system_shortcuts:
            return True
        
        for existing in self.shortcuts:
            if existing.get("shortcut") == shortcut and existing.get("status") == "active":
                return True
        
        return False
    
    def create_shortcut(self, name: str, description: str, 
                       action_type: str, shortcut: str,
                       script_path: str = None, command: str = None) -> str:
        """Create a new keyboard shortcut."""
        # Check for conflicts
        if self._is_shortcut_taken(shortcut):
            conflict = {
                "shortcut": shortcut,
                "new_action": name,
                "detected_at": datetime.now().isoformat()
            }
            self.conflicts.append(conflict)
            self._save_json(self.conflicts_file, self.conflicts)
            return None
        
        shortcut_id = f"shortcut_{len(self.shortcuts) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        shortcut_data = {
            "id": shortcut_id,
            "name": name,
            "description": description,
            "action_type": action_type,
            "shortcut": shortcut,
            "script_path": script_path,
            "command": command,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "uses": 0,
            "total_time_saved": 0
        }
        
        self.shortcuts.append(shortcut_data)
        self._save_json(self.shortcuts_file, self.shortcuts)
        
        self.statistics["total_shortcuts_created"] += 1
        self.statistics["active_shortcuts"] += 1
        self._save_json(self.statistics_file, self.statistics)
        
        # Generate script if needed
        if not script_path and command:
            script_path = self._generate_shortcut_script(shortcut_id, name, command)
            shortcut_data["script_path"] = script_path
            self._save_json(self.shortcuts_file, self.shortcuts)
        
        return shortcut_id
    
    def _generate_shortcut_script(self, shortcut_id: str, name: str, command: str) -> str:
        """Generate a script for the shortcut."""
        script_content = f'''#!/bin/bash
# Shortcut: {name}
# ID: {shortcut_id}
# Generated: {datetime.now().isoformat()}

# Log usage
echo "$(date -Iseconds),{shortcut_id},{name}" >> ~/vy-nexus/logs/shortcut_usage.log

# Execute command
{command}
'''
        
        script_path = os.path.join(self.shortcuts_dir, f"{shortcut_id}.sh")
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(script_path, 0o755)
        
        return script_path
    
    def create_quick_action(self, name: str, description: str,
                          action_type: str, steps: List[Dict],
                          icon: str = None) -> str:
        """Create a quick action (multi-step workflow)."""
        action_id = f"action_{len(self.actions) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        action = {
            "id": action_id,
            "name": name,
            "description": description,
            "action_type": action_type,
            "steps": steps,
            "icon": icon,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "uses": 0
        }
        
        self.actions.append(action)
        self._save_json(self.actions_file, self.actions)
        
        # Generate script
        script_path = self._generate_action_script(action_id, name, steps)
        action["script_path"] = script_path
        self._save_json(self.actions_file, self.actions)
        
        return action_id
    
    def _generate_action_script(self, action_id: str, name: str, steps: List[Dict]) -> str:
        """Generate a script for the quick action."""
        script_lines = [
            "#!/bin/bash",
            f"# Quick Action: {name}",
            f"# ID: {action_id}",
            f"# Generated: {datetime.now().isoformat()}",
            "",
            "# Log usage",
            f'echo "$(date -Iseconds),{action_id},{name}" >> ~/vy-nexus/logs/action_usage.log',
            "",
            "# Execute steps"
        ]
        
        for i, step in enumerate(steps, 1):
            script_lines.append(f"\n# Step {i}: {step.get('name', 'Unnamed step')}")
            
            if step.get("type") == "command":
                script_lines.append(step["command"])
            elif step.get("type") == "script":
                script_lines.append(f"bash {step['script_path']}")
            elif step.get("type") == "python":
                script_lines.append(f"python3 {step['script_path']}")
            
            if step.get("wait"):
                script_lines.append(f"sleep {step['wait']}")
        
        script_content = "\n".join(script_lines)
        script_path = os.path.join(self.shortcuts_dir, f"{action_id}.sh")
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        
        return script_path
    
    def record_usage(self, shortcut_id: str = None, action_id: str = None,
                    time_saved: float = 0) -> None:
        """Record shortcut or action usage."""
        usage_record = {
            "shortcut_id": shortcut_id,
            "action_id": action_id,
            "time_saved": time_saved,
            "timestamp": datetime.now().isoformat()
        }
        
        self.usage.append(usage_record)
        self._save_json(self.usage_file, self.usage)
        
        # Update statistics
        if shortcut_id:
            for shortcut in self.shortcuts:
                if shortcut["id"] == shortcut_id:
                    shortcut["uses"] += 1
                    shortcut["total_time_saved"] += time_saved
                    shortcut["last_used"] = datetime.now().isoformat()
                    break
            self._save_json(self.shortcuts_file, self.shortcuts)
        
        if action_id:
            for action in self.actions:
                if action["id"] == action_id:
                    action["uses"] += 1
                    action["last_used"] = datetime.now().isoformat()
                    break
            self._save_json(self.actions_file, self.actions)
        
        self.statistics["total_uses"] += 1
        self.statistics["time_saved"] += time_saved
        self._save_json(self.statistics_file, self.statistics)
    
    def detect_conflicts(self) -> List[Dict]:
        """Detect shortcut conflicts."""
        conflicts = []
        shortcut_map = defaultdict(list)
        
        # Map shortcuts to actions
        for shortcut in self.shortcuts:
            if shortcut.get("status") == "active":
                shortcut_map[shortcut["shortcut"]].append(shortcut)
        
        # Find conflicts
        for shortcut_key, actions in shortcut_map.items():
            if len(actions) > 1:
                conflicts.append({
                    "shortcut": shortcut_key,
                    "conflicting_actions": [
                        {"id": a["id"], "name": a["name"]}
                        for a in actions
                    ],
                    "detected_at": datetime.now().isoformat()
                })
        
        return conflicts
    
    def resolve_conflict(self, shortcut: str, keep_action_id: str) -> bool:
        """Resolve a shortcut conflict."""
        for sc in self.shortcuts:
            if sc["shortcut"] == shortcut and sc["id"] != keep_action_id:
                sc["status"] = "inactive"
                sc["deactivated_at"] = datetime.now().isoformat()
                sc["deactivation_reason"] = "conflict_resolution"
                self.statistics["active_shortcuts"] -= 1
        
        self._save_json(self.shortcuts_file, self.shortcuts)
        self.statistics["conflicts_resolved"] += 1
        self._save_json(self.statistics_file, self.statistics)
        
        return True
    
    def get_most_used_shortcuts(self, limit: int = 10) -> List[Dict]:
        """Get most frequently used shortcuts."""
        active_shortcuts = [s for s in self.shortcuts if s.get("status") == "active"]
        sorted_shortcuts = sorted(active_shortcuts, key=lambda x: x.get("uses", 0), reverse=True)
        return sorted_shortcuts[:limit]
    
    def get_time_saving_shortcuts(self, limit: int = 10) -> List[Dict]:
        """Get shortcuts that save the most time."""
        active_shortcuts = [s for s in self.shortcuts if s.get("status") == "active"]
        sorted_shortcuts = sorted(
            active_shortcuts,
            key=lambda x: x.get("total_time_saved", 0),
            reverse=True
        )
        return sorted_shortcuts[:limit]
    
    def generate_cheat_sheet(self) -> str:
        """Generate a cheat sheet of all active shortcuts."""
        active_shortcuts = [s for s in self.shortcuts if s.get("status") == "active"]
        
        # Group by action type
        grouped = defaultdict(list)
        for shortcut in active_shortcuts:
            grouped[shortcut.get("action_type", "other")].append(shortcut)
        
        cheat_sheet = "# Keyboard Shortcuts Cheat Sheet\n\n"
        cheat_sheet += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for action_type, shortcuts in sorted(grouped.items()):
            cheat_sheet += f"## {action_type.replace('_', ' ').title()}\n\n"
            
            for shortcut in sorted(shortcuts, key=lambda x: x["shortcut"]):
                cheat_sheet += f"- **{shortcut['shortcut']}**: {shortcut['name']}\n"
                cheat_sheet += f"  {shortcut['description']}\n"
                if shortcut.get("uses", 0) > 0:
                    cheat_sheet += f"  _(Used {shortcut['uses']} times)_\n"
                cheat_sheet += "\n"
        
        # Save cheat sheet
        cheat_sheet_path = os.path.join(self.shortcuts_dir, "CHEAT_SHEET.md")
        with open(cheat_sheet_path, 'w') as f:
            f.write(cheat_sheet)
        
        return cheat_sheet
    
    def generate_report(self) -> Dict:
        """Generate comprehensive shortcuts report."""
        active_shortcuts = [s for s in self.shortcuts if s.get("status") == "active"]
        active_actions = [a for a in self.actions if a.get("status") == "active"]
        
        return {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_shortcuts": len(self.shortcuts),
                "active_shortcuts": len(active_shortcuts),
                "total_actions": len(self.actions),
                "active_actions": len(active_actions),
                "total_uses": self.statistics["total_uses"],
                "time_saved_seconds": self.statistics["time_saved"],
                "time_saved_hours": self.statistics["time_saved"] / 3600,
                "conflicts_detected": len(self.conflicts),
                "conflicts_resolved": self.statistics["conflicts_resolved"]
            },
            "most_used_shortcuts": [
                {"name": s["name"], "shortcut": s["shortcut"], "uses": s["uses"]}
                for s in self.get_most_used_shortcuts(5)
            ],
            "time_saving_shortcuts": [
                {"name": s["name"], "shortcut": s["shortcut"], "time_saved": s["total_time_saved"]}
                for s in self.get_time_saving_shortcuts(5)
            ],
            "statistics": self.statistics
        }


if __name__ == "__main__":
    # Test the designer
    designer = ShortcutDesigner()
    
    print("Analyzing action frequency...")
    sample_actions = [
        {"type": "file_organization", "duration": 30, "description": "Organize downloads"},
        {"type": "file_organization", "duration": 25, "description": "Sort files"},
        {"type": "file_organization", "duration": 28, "description": "Clean desktop"},
        {"type": "file_organization", "duration": 32, "description": "Archive old files"},
        {"type": "file_organization", "duration": 27, "description": "Organize documents"},
        {"type": "file_organization", "duration": 30, "description": "Sort photos"},
        {"type": "screenshot", "duration": 5, "description": "Take screenshot"},
        {"type": "screenshot", "duration": 5, "description": "Capture window"},
        {"type": "screenshot", "duration": 5, "description": "Screen recording"},
        {"type": "screenshot", "duration": 5, "description": "Screenshot region"},
        {"type": "screenshot", "duration": 5, "description": "Capture screen"},
    ]
    
    suggestions = designer.analyze_action_frequency(sample_actions)
    print(f"\nFound {len(suggestions)} shortcut suggestions")
    
    # Create shortcuts
    print("\nCreating shortcuts...")
    shortcut1 = designer.create_shortcut(
        name="Quick File Organization",
        description="Organize files in current directory",
        action_type="file_organization",
        shortcut="cmd+shift+o",
        command="python3 ~/vy-nexus/modules/optimization/repetitive_tasks_scanner.py"
    )
    print(f"✓ Created shortcut: {shortcut1}")
    
    shortcut2 = designer.create_shortcut(
        name="Smart Screenshot",
        description="Take and organize screenshot",
        action_type="screenshot",
        shortcut="cmd+shift+s",
        command="screencapture -i ~/Desktop/screenshot_$(date +%Y%m%d_%H%M%S).png"
    )
    print(f"✓ Created shortcut: {shortcut2}")
    
    # Create quick action
    print("\nCreating quick action...")
    action1 = designer.create_quick_action(
        name="Daily Cleanup",
        description="Clean up workspace and organize files",
        action_type="maintenance",
        steps=[
            {"type": "command", "name": "Clean Downloads", "command": "echo 'Cleaning downloads...'"},
            {"type": "command", "name": "Organize Desktop", "command": "echo 'Organizing desktop...'", "wait": 1},
            {"type": "command", "name": "Empty Trash", "command": "echo 'Emptying trash...'"}
        ]
    )
    print(f"✓ Created action: {action1}")
    
    # Record usage
    print("\nRecording usage...")
    designer.record_usage(shortcut_id=shortcut1, time_saved=25)
    designer.record_usage(shortcut_id=shortcut1, time_saved=28)
    designer.record_usage(shortcut_id=shortcut2, time_saved=3)
    
    # Generate cheat sheet
    print("\nGenerating cheat sheet...")
    cheat_sheet = designer.generate_cheat_sheet()
    
    # Generate report
    report = designer.generate_report()
    
    print("\n" + "="*50)
    print("SHORTCUT DESIGNER REPORT")
    print("="*50)
    print(f"\nActive shortcuts: {report['summary']['active_shortcuts']}")
    print(f"Active actions: {report['summary']['active_actions']}")
    print(f"Total uses: {report['summary']['total_uses']}")
    print(f"Time saved: {report['summary']['time_saved_hours']:.2f} hours")
    
    print("\nMost Used Shortcuts:")
    for shortcut in report['most_used_shortcuts']:
        print(f"  - {shortcut['shortcut']}: {shortcut['name']} ({shortcut['uses']} uses)")
    
    print("\nSuggested Shortcuts:")
    for i, suggestion in enumerate(suggestions[:3], 1):
        print(f"  {i}. {suggestion['action_type']}: {suggestion['suggested_shortcut']}")
        print(f"     Frequency: {suggestion['frequency']}, Priority: {suggestion['priority']:.1f}")
    
    print("\n✅ Shortcut designer is operational!")
    print(f"\nCheat sheet saved to: {os.path.join(designer.shortcuts_dir, 'CHEAT_SHEET.md')}")
