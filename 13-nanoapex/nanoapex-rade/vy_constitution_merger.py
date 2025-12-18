#!/usr/bin/env python3
"""
Constitution Merger - Safely applies approved proposals to constitution.md
with versioning and rollback capability.
"""

import os
import json
import shutil
from datetime import datetime

PULSE_DIR = os.path.expanduser("~/nano_memory/pulse")
CONSTITUTION_PATH = os.path.join(PULSE_DIR, "constitution.md")
PROPOSALS_PATH = os.path.join(PULSE_DIR, "constitution_proposals.jsonl")
BACKUP_DIR = os.path.join(PULSE_DIR, "constitution_backups")


def load_proposals():
    """Load all proposals from JSONL file."""
    if not os.path.exists(PROPOSALS_PATH):
        return []
    
    proposals = []
    with open(PROPOSALS_PATH, "r") as f:
        for line in f:
            try:
                proposals.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return proposals


def backup_constitution():
    """Create timestamped backup of current constitution."""
    if not os.path.exists(CONSTITUTION_PATH):
        return None
    
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"constitution_v{timestamp}.md")
    shutil.copy2(CONSTITUTION_PATH, backup_path)
    return backup_path


def get_version_number():
    """Extract current version from constitution header."""
    if not os.path.exists(CONSTITUTION_PATH):
        return "1.0"
    
    with open(CONSTITUTION_PATH, "r") as f:
        first_line = f.readline().strip()
    
    if "CONSTITUTION v" in first_line:
        try:
            return first_line.split("v")[1].strip()
        except:
            return "1.0"
    return "1.0"


def increment_version(version_str):
    """Increment version number (e.g., 1.2 -> 1.3)."""
    try:
        parts = version_str.split(".")
        major, minor = int(parts[0]), int(parts[1])
        return f"{major}.{minor + 1}"
    except:
        return "1.1"


def apply_proposal(proposal_id):
    """Apply a specific proposal to the constitution."""
    proposals = load_proposals()
    proposal = None
    
    for p in proposals:
        if p.get("id") == proposal_id:
            proposal = p
            break
    
    if not proposal:
        print(f"❌ Proposal {proposal_id} not found")
        return False
    
    # Parse the proposal if it's wrapped in raw text
    if "raw" in proposal:
        raw_text = proposal["raw"]
        # Extract JSON from markdown if present
        if "```" in raw_text:
            json_start = raw_text.find("{")
            json_end = raw_text.rfind("}") + 1
            if json_start != -1 and json_end != -1:
                try:
                    proposal = json.loads(raw_text[json_start:json_end])
                except json.JSONDecodeError:
                    print(f"❌ Could not parse proposal JSON")
                    return False
    
    # Backup current constitution
    backup_path = backup_constitution()
    print(f"📦 Backed up to: {backup_path}")
    
    # Read current constitution
    with open(CONSTITUTION_PATH, "r") as f:
        content = f.read()
    
    # Update version
    current_version = get_version_number()
    new_version = increment_version(current_version)
    
    # Apply the change
    change_type = proposal.get("change_type")
    new_rule_text = proposal.get("new_rule_text", "")
    target_match = proposal.get("target_rule_match", "")
    
    if change_type == "add_rule":
        # Add new rule at the end
        if not content.endswith("\n"):
            content += "\n"
        content += f"\n{new_rule_text}\n"
    
    elif change_type == "refine_rule" and target_match:
        # Replace existing rule
        content = content.replace(target_match, new_rule_text)
    
    elif change_type == "refine_rule":
        # Add as new rule if no target specified
        if not content.endswith("\n"):
            content += "\n"
        content += f"\n{new_rule_text}\n"
    
    # Update version header
    if "# CONSTITUTION v" in content:
        content = content.replace(f"# CONSTITUTION v{current_version}", f"# CONSTITUTION v{new_version}")
    else:
        content = f"# CONSTITUTION v{new_version}\n\n" + content
    
    # Write updated constitution
    with open(CONSTITUTION_PATH, "w") as f:
        f.write(content)
    
    print(f"✅ Applied proposal {proposal_id}")
    print(f"📈 Version: {current_version} → {new_version}")
    print(f"📝 Change: {proposal.get('summary', 'No summary')}")
    
    return True


def list_proposals():
    """List all available proposals."""
    proposals = load_proposals()
    if not proposals:
        print("No proposals found.")
        return
    
    print("Available proposals:")
    for i, p in enumerate(proposals):
        proposal_id = p.get("id", f"proposal_{i}")
        summary = p.get("summary", "No summary")
        change_type = p.get("change_type", "unknown")
        generated_at = p.get("generated_at", "unknown")
        
        print(f"  [{i}] {proposal_id}")
        print(f"      Type: {change_type}")
        print(f"      Summary: {summary}")
        print(f"      Generated: {generated_at}")
        print()


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 vy_constitution_merger.py list")
        print("  python3 vy_constitution_merger.py apply <proposal_id>")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        list_proposals()
    elif command == "apply" and len(sys.argv) > 2:
        proposal_id = sys.argv[2]
        apply_proposal(proposal_id)
    else:
        print("Invalid command. Use 'list' or 'apply <proposal_id>'")


if __name__ == "__main__":
    main()