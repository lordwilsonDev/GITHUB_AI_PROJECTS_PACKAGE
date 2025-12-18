#!/usr/bin/env python3
"""
Documentation Automation Engine
Automatically maintains PROJECT_DOCUMENTATION.md based on system events
"""

import os
import re
from datetime import datetime
from pathlib import Path
import json


class DocumentationEngine:
    """Core engine for automated documentation updates"""
    
    def __init__(self, doc_path="PROJECT_DOCUMENTATION.md"):
        self.doc_path = Path(doc_path)
        self.backup_dir = Path("doc_backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.version_pattern = r'\*\*Version:\*\* (\d+\.\d+\.\d+)'
        
    def backup_document(self):
        """Create timestamped backup before modifications"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"PROJECT_DOCUMENTATION_{timestamp}.md"
        
        if self.doc_path.exists():
            content = self.doc_path.read_text()
            backup_path.write_text(content)
            return backup_path
        return None
    
    def get_current_version(self):
        """Extract current version from document"""
        content = self.doc_path.read_text()
        match = re.search(self.version_pattern, content)
        if match:
            return match.group(1)
        return "1.0.0"
    
    def increment_version(self, version_type="patch"):
        """Increment version number (major.minor.patch)"""
        current = self.get_current_version()
        major, minor, patch = map(int, current.split('.'))
        
        if version_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif version_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        return f"{major}.{minor}.{patch}"
    
    def update_version(self, new_version=None, version_type="patch"):
        """Update version in document header"""
        self.backup_document()
        
        if new_version is None:
            new_version = self.increment_version(version_type)
        
        content = self.doc_path.read_text()
        content = re.sub(
            self.version_pattern,
            f"**Version:** {new_version}",
            content
        )
        
        # Update last modified date
        today = datetime.now().strftime("%B %d, %Y")
        content = re.sub(
            r'\*\*Last Updated:\*\* .+',
            f"**Last Updated:** {today}",
            content
        )
        content = re.sub(
            r'\*\*Last Modified:\*\* .+',
            f"**Last Modified:** {today}",
            content
        )
        
        self.doc_path.write_text(content)
        return new_version
    
    def append_to_section(self, section_name, new_content, auto_version=True):
        """Append content to a specific section"""
        self.backup_document()
        
        content = self.doc_path.read_text()
        
        # Find the section
        section_pattern = rf'(## {re.escape(section_name)}.*?)(\n---\n|\n## |$)'
        match = re.search(section_pattern, content, re.DOTALL)
        
        if not match:
            raise ValueError(f"Section '{section_name}' not found")
        
        # Insert new content before the section end
        section_content = match.group(1)
        section_end = match.group(2)
        
        # Add timestamp to new content
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        timestamped_content = f"\n\n**[Added {timestamp}]**\n{new_content}"
        
        updated_section = section_content + timestamped_content + section_end
        content = content.replace(match.group(0), updated_section)
        
        self.doc_path.write_text(content)
        
        if auto_version:
            self.update_version(version_type="patch")
        
        return True
    
    def update_section_content(self, section_name, new_content, auto_version=True):
        """Replace entire section content"""
        self.backup_document()
        
        content = self.doc_path.read_text()
        
        # Find section and replace content
        section_pattern = rf'(## {re.escape(section_name)}\n\n)(.+?)(\n\n\*\*Related Sections)'
        
        def replacer(match):
            return match.group(1) + new_content + match.group(3)
        
        content = re.sub(section_pattern, replacer, content, flags=re.DOTALL)
        self.doc_path.write_text(content)
        
        if auto_version:
            self.update_version(version_type="minor")
        
        return True


class AgentDocBridge:
    """Bridge between agents and documentation system"""
    
    def __init__(self, engine):
        self.engine = engine
        self.log_file = Path("agent_doc_updates.log")
    
    def log_update(self, action, section, details):
        """Log all documentation updates"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "action": action,
            "section": section,
            "details": details
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def handle_troubleshooting_event(self, issue, solution):
        """Auto-append troubleshooting entries"""
        content = f"\n### {issue}\n\n{solution}"
        self.engine.append_to_section("Section 6: Troubleshooting Guide", content)
        self.log_update("append", "Troubleshooting", {"issue": issue})
        return True
    
    def handle_config_change(self, config_key, config_value, description):
        """Auto-update configuration documentation"""
        content = f"\n- **{config_key}**: {config_value}\n  - {description}"
        self.engine.append_to_section("Section 2: Configuration Management", content)
        self.log_update("append", "Configuration", {"key": config_key})
        return True
    
    def handle_release(self, version_type="patch", release_notes=None):
        """Handle version releases"""
        new_version = self.engine.update_version(version_type=version_type)
        
        if release_notes:
            self.engine.append_to_section(
                "Section 10: Future Roadmap",
                f"\n### Release {new_version}\n{release_notes}"
            )
        
        self.log_update("release", "Version", {"version": new_version})
        return new_version


class DocumentationWatcher:
    """Watches for system events and triggers documentation updates"""
    
    def __init__(self, bridge):
        self.bridge = bridge
        self.event_queue = []
    
    def queue_event(self, event_type, data):
        """Queue an event for processing"""
        self.event_queue.append({
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    
    def process_events(self):
        """Process all queued events"""
        results = []
        
        for event in self.event_queue:
            try:
                if event["type"] == "troubleshooting":
                    self.bridge.handle_troubleshooting_event(
                        event["data"]["issue"],
                        event["data"]["solution"]
                    )
                elif event["type"] == "config_change":
                    self.bridge.handle_config_change(
                        event["data"]["key"],
                        event["data"]["value"],
                        event["data"]["description"]
                    )
                elif event["type"] == "release":
                    self.bridge.handle_release(
                        event["data"].get("version_type", "patch"),
                        event["data"].get("notes")
                    )
                
                results.append({"event": event, "status": "success"})
            except Exception as e:
                results.append({"event": event, "status": "failed", "error": str(e)})
        
        self.event_queue.clear()
        return results


if __name__ == "__main__":
    # Example usage
    engine = DocumentationEngine("/Users/lordwilson/PROJECT_DOCUMENTATION.md")
    bridge = AgentDocBridge(engine)
    watcher = DocumentationWatcher(bridge)
    
    print("Documentation Automation Engine initialized")
    print(f"Current version: {engine.get_current_version()}")
    print("\nReady to process automated updates...")
