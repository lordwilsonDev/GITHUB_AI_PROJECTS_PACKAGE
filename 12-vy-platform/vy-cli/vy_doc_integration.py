#!/usr/bin/env python3
"""
Vy Agent Integration for Documentation
Allows Vy to automatically update documentation during task execution
"""

from agent_doc_interface import AgentInterface
import json
from pathlib import Path
from datetime import datetime


class VyDocumentationHelper:
    """Helper class for Vy to maintain documentation"""
    
    def __init__(self):
        self.interface = AgentInterface()
        self.session_log = []
    
    def log_task_completion(self, task_name, outcome, learnings=None):
        """Log when Vy completes a task"""
        self.session_log.append({
            "timestamp": datetime.now().isoformat(),
            "task": task_name,
            "outcome": outcome,
            "learnings": learnings
        })
    
    def auto_document_error(self, error_type, solution):
        """
        Automatically add errors and solutions to troubleshooting
        
        Example:
            vy_doc.auto_document_error(
                "Connection Timeout to API",
                "Increase timeout value in config.json to 30 seconds"
            )
        """
        return self.interface.add_troubleshooting(error_type, solution)
    
    def auto_document_config(self, key, value, description):
        """
        Automatically document configuration changes
        
        Example:
            vy_doc.auto_document_config(
                "API_TIMEOUT",
                "30",
                "Maximum seconds to wait for API response"
            )
        """
        return self.interface.update_config(key, value, description)
    
    def auto_document_feature(self, feature_description):
        """
        Add new features to the advanced features section
        
        Example:
            vy_doc.auto_document_feature(
                "Added support for batch processing of documents"
            )
        """
        return self.interface.append_to_section(
            "Section 1: Introduction to Advanced Features",
            f"\n- {feature_description}"
        )
    
    def create_release_from_session(self, version_type="patch"):
        """
        Create a release based on session activities
        """
        if not self.session_log:
            return None
        
        # Generate release notes from session
        notes = "### Changes in this release:\n\n"
        for entry in self.session_log:
            if entry.get("learnings"):
                notes += f"- {entry['learnings']}\n"
        
        return self.interface.create_release(version_type, notes)
    
    def save_session_log(self, filepath="vy_session_log.json"):
        """Save session log to file"""
        with open(filepath, 'w') as f:
            json.dump(self.session_log, f, indent=2)


# Example usage patterns for Vy
if __name__ == "__main__":
    print("=== Vy Documentation Integration Examples ===")
    print()
    
    vy_doc = VyDocumentationHelper()
    
    print("Example 1: Document a troubleshooting solution")
    print("  vy_doc.auto_document_error(")
    print("      'Database Connection Failed',")
    print("      'Check DATABASE_URL environment variable is set correctly'")
    print("  )")
    print()
    
    print("Example 2: Document a configuration change")
    print("  vy_doc.auto_document_config(")
    print("      'MAX_WORKERS',")
    print("      '4',")
    print("      'Maximum number of concurrent worker threads'")
    print("  )")
    print()
    
    print("Example 3: Document a new feature")
    print("  vy_doc.auto_document_feature(")
    print("      'Added automatic retry logic for failed API calls'")
    print("  )")
    print()
    
    print("Example 4: Create a release")
    print("  vy_doc.log_task_completion('API Integration', 'success', 'Added retry logic')")
    print("  vy_doc.create_release_from_session('minor')")
    print()
    
    print("Current documentation version:", vy_doc.interface.get_version())
