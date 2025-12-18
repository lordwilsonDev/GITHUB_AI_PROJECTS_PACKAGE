import subprocess
import json
import os

# Configuration for JARVIS to find the tools
TOOLS = {
    "filesystem": {
        "cmd": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/Users/lordwilson"]
    },
    "desktop": {
        "cmd": ["npx", "-y", "@wonderwhy-er/desktop-commander@latest"]
    },
    "github": {
        "cmd": ["npx", "-y", "@modelcontextprotocol/server-github"],
        "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN", "")}
    }
}

def list_available_tools():
    """Returns the manual for the Brain"""
    return [
        "filesystem: Read/Write files (args: path, content)",
        "desktop: Control Mouse/Keyboard (args: x, y, text)",
        "github: Read Repos (args: repo_url)"
    ]

# This function effectively 'wakes up' a tool when JARVIS needs it
def get_tool_command(tool_name):
    return TOOLS.get(tool_name, {}).get("cmd")
