#!/usr/bin/env python3
"""
Agent-to-Documentation Interface
Simple API for agents to update documentation automatically
"""

from doc_automation_engine import DocumentationEngine, AgentDocBridge, DocumentationWatcher
import sys
import json


class AgentInterface:
    """Simple interface for agents to interact with documentation"""
    
    def __init__(self):
        self.engine = DocumentationEngine("/Users/lordwilson/PROJECT_DOCUMENTATION.md")
        self.bridge = AgentDocBridge(self.engine)
        self.watcher = DocumentationWatcher(self.bridge)
    
    def add_troubleshooting(self, issue_title, solution_text):
        """
        Add a new troubleshooting entry
        
        Args:
            issue_title: Brief title of the issue
            solution_text: Detailed solution
        """
        return self.bridge.handle_troubleshooting_event(issue_title, solution_text)
    
    def update_config(self, config_key, config_value, description):
        """
        Document a configuration change
        
        Args:
            config_key: Configuration parameter name
            config_value: New value
            description: What this config does
        """
        return self.bridge.handle_config_change(config_key, config_value, description)
    
    def create_release(self, version_type="patch", notes=None):
        """
        Create a new release and update version
        
        Args:
            version_type: 'major', 'minor', or 'patch'
            notes: Optional release notes
        """
        return self.bridge.handle_release(version_type, notes)
    
    def append_to_section(self, section_name, content):
        """
        Append content to any section
        
        Args:
            section_name: Full section name (e.g., 'Section 1: Introduction to Advanced Features')
            content: Content to append
        """
        return self.engine.append_to_section(section_name, content)
    
    def get_version(self):
        """Get current documentation version"""
        return self.engine.get_current_version()


def cli():
    """Command-line interface for quick updates"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python agent_doc_interface.py troubleshooting '<issue>' '<solution>'")
        print("  python agent_doc_interface.py config '<key>' '<value>' '<description>'")
        print("  python agent_doc_interface.py release [major|minor|patch] '<notes>'")
        print("  python agent_doc_interface.py version")
        sys.exit(1)
    
    interface = AgentInterface()
    command = sys.argv[1]
    
    if command == "troubleshooting":
        if len(sys.argv) < 4:
            print("Error: Need issue and solution")
            sys.exit(1)
        result = interface.add_troubleshooting(sys.argv[2], sys.argv[3])
        print(f"✅ Troubleshooting entry added: {sys.argv[2]}")
    
    elif command == "config":
        if len(sys.argv) < 5:
            print("Error: Need key, value, and description")
            sys.exit(1)
        result = interface.update_config(sys.argv[2], sys.argv[3], sys.argv[4])
        print(f"✅ Configuration documented: {sys.argv[2]}")
    
    elif command == "release":
        version_type = sys.argv[2] if len(sys.argv) > 2 else "patch"
        notes = sys.argv[3] if len(sys.argv) > 3 else None
        new_version = interface.create_release(version_type, notes)
        print(f"✅ Release created: v{new_version}")
    
    elif command == "version":
        version = interface.get_version()
        print(f"Current version: {version}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
