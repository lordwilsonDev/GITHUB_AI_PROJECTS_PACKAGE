#!/usr/bin/env python3
"""
Workspace Launcher Automation

Automatically opens your daily workspace:
- Terminal
- Browser with specific tabs
- Notes app
- Calendar

Usage: python3 automations/workspace_launcher.py
"""

import subprocess
import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import safe_click, safe_type, safe_key_combo, get_screen_resolution

class WorkspaceLauncher:
    def __init__(self):
        self.width, self.height = get_screen_resolution()
        print(f"🖥️  Screen Resolution: {self.width}x{self.height}")
    
    def open_app(self, app_name):
        """Open a macOS application"""
        print(f"📱 Opening {app_name}...")
        try:
            subprocess.run(["open", "-a", app_name], check=True)
            time.sleep(2)  # Wait for app to open
            return True
        except Exception as e:
            print(f"❌ Failed to open {app_name}: {e}")
            return False
    
    def open_terminal(self):
        """Open Terminal app"""
        return self.open_app("Terminal")
    
    def open_browser_with_tabs(self, urls):
        """Open browser with multiple tabs"""
        print(f"🌐 Opening browser with {len(urls)} tabs...")
        for i, url in enumerate(urls):
            if i == 0:
                subprocess.run(["open", "-a", "Google Chrome", url])
            else:
                subprocess.run(["open", url])
            time.sleep(1)
        return True
    
    def open_notes(self):
        """Open Notes app"""
        return self.open_app("Notes")
    
    def open_calendar(self):
        """Open Calendar app"""
        return self.open_app("Calendar")
    
    def create_daily_note(self):
        """Create a daily note with today's date"""
        from datetime import datetime
        today = datetime.now().strftime("%A, %B %d, %Y")
        
        print("📝 Creating daily note...")
        self.open_notes()
        time.sleep(2)
        
        # Create new note (Cmd+N)
        safe_key_combo(["cmd", "n"], confirm=False)
        time.sleep(1)
        
        # Type the title
        title = f"Daily Note - {today}"
        safe_type(title, confirm=False)
        time.sleep(0.5)
        
        # Press Enter to go to body
        safe_key_combo(["return"], confirm=False)
        time.sleep(0.5)
        
        # Type template
        template = f"""\n## Goals for Today\n- \n- \n- \n\n## Notes\n\n\n## Completed\n- """
        safe_type(template, confirm=False)
        
        print(f"✅ Created note: {title}")
        return True
    
    def launch_full_workspace(self):
        """Launch complete workspace"""
        print("\n🚀 LAUNCHING WORKSPACE...\n")
        
        # 1. Open Terminal
        self.open_terminal()
        
        # 2. Open Browser with useful tabs
        urls = [
            "https://github.com",
            "https://gmail.com",
            "https://calendar.google.com"
        ]
        self.open_browser_with_tabs(urls)
        
        # 3. Open Notes and create daily note
        self.create_daily_note()
        
        # 4. Open Calendar
        self.open_calendar()
        
        print("\n✅ WORKSPACE READY!\n")
        print("Opened:")
        print("  - Terminal")
        print("  - Browser (GitHub, Gmail, Calendar)")
        print("  - Notes (with daily template)")
        print("  - Calendar")

if __name__ == "__main__":
    launcher = WorkspaceLauncher()
    launcher.launch_full_workspace()
