#!/usr/bin/env python3
"""
Screenshot Documentation Automation

Captures screenshots and organizes them into a documentation folder
with timestamps and optional annotations.

Usage: 
  python3 automations/screenshot_documenter.py
  python3 automations/screenshot_documenter.py --project "MyProject"
  python3 automations/screenshot_documenter.py --interval 5 --count 10
"""

import subprocess
import time
from datetime import datetime
from pathlib import Path
import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import capture_screen

class ScreenshotDocumenter:
    def __init__(self, project_name=None):
        self.home = Path.home()
        self.project_name = project_name or "General"
        
        # Create documentation directory
        self.docs_dir = self.home / "level33_sovereign" / "documentation" / self.project_name
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        self.screenshots = []
        
    def capture_single(self, description=None):
        """Capture a single screenshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if description:
            # Sanitize description for filename
            safe_desc = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in description)
            safe_desc = safe_desc.replace(' ', '_')[:50]  # Limit length
            filename = f"{timestamp}_{safe_desc}.png"
        else:
            filename = f"{timestamp}.png"
        
        filepath = self.docs_dir / filename
        
        print(f"📸 Capturing screenshot: {filename}")
        
        try:
            # Use macOS screencapture command
            subprocess.run(["screencapture", "-x", str(filepath)], check=True)
            self.screenshots.append(filepath)
            print(f"✅ Saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Failed to capture screenshot: {e}")
            return None
    
    def capture_series(self, interval=5, count=5, description_prefix=None):
        """Capture a series of screenshots at intervals"""
        print(f"\n🎬 Capturing {count} screenshots at {interval}s intervals...\n")
        
        for i in range(count):
            desc = f"{description_prefix}_{i+1}" if description_prefix else f"screenshot_{i+1}"
            self.capture_single(desc)
            
            if i < count - 1:  # Don't wait after last screenshot
                print(f"Waiting {interval} seconds...")
                time.sleep(interval)
        
        print(f"\n✅ Captured {len(self.screenshots)} screenshots")
    
    def capture_interactive(self):
        """Interactive mode - capture screenshots on demand"""
        print("\n📸 INTERACTIVE SCREENSHOT MODE")
        print("="*50)
        print("Commands:")
        print("  c - Capture screenshot")
        print("  d - Capture with description")
        print("  s - Capture series")
        print("  l - List captured screenshots")
        print("  q - Quit")
        print("="*50 + "\n")
        
        while True:
            try:
                cmd = input("\n> ").strip().lower()
                
                if cmd == 'q':
                    break
                elif cmd == 'c':
                    self.capture_single()
                elif cmd == 'd':
                    desc = input("Description: ").strip()
                    self.capture_single(desc)
                elif cmd == 's':
                    try:
                        count = int(input("Number of screenshots: ").strip())
                        interval = int(input("Interval (seconds): ").strip())
                        prefix = input("Description prefix (optional): ").strip() or None
                        self.capture_series(interval, count, prefix)
                    except ValueError:
                        print("❌ Invalid input")
                elif cmd == 'l':
                    self.list_screenshots()
                else:
                    print("❌ Unknown command")
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
        
        self.generate_index()
    
    def list_screenshots(self):
        """List all captured screenshots"""
        if not self.screenshots:
            print("No screenshots captured yet")
            return
        
        print(f"\n📷 Captured Screenshots ({len(self.screenshots)}):")
        for i, path in enumerate(self.screenshots, 1):
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"  {i}. {path.name} ({size_mb:.2f} MB)")
    
    def generate_index(self):
        """Generate an HTML index of all screenshots"""
        if not self.screenshots:
            return
        
        print("\n📝 Generating documentation index...")
        
        index_path = self.docs_dir / "index.html"
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Screenshot Documentation - {self.project_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #007AFF;
            padding-bottom: 10px;
        }}
        .screenshot {{
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .screenshot img {{
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .screenshot h3 {{
            margin-top: 0;
            color: #007AFF;
        }}
        .meta {{
            color: #666;
            font-size: 0.9em;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <h1>📸 Screenshot Documentation: {self.project_name}</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Total Screenshots: {len(self.screenshots)}</p>
    <hr>
"""
        
        for i, path in enumerate(self.screenshots, 1):
            size_mb = path.stat().st_size / (1024 * 1024)
            html += f"""
    <div class="screenshot">
        <h3>Screenshot {i}: {path.stem}</h3>
        <img src="{path.name}" alt="{path.name}">
        <div class="meta">
            <strong>File:</strong> {path.name}<br>
            <strong>Size:</strong> {size_mb:.2f} MB<br>
            <strong>Path:</strong> {path}
        </div>
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        with open(index_path, 'w') as f:
            f.write(html)
        
        print(f"✅ Index generated: {index_path}")
        print(f"\n🌐 Open in browser: file://{index_path}")
        
        # Optionally open in browser
        try:
            subprocess.run(["open", str(index_path)])
        except:
            pass

def main():
    parser = argparse.ArgumentParser(description='Screenshot Documentation Tool')
    parser.add_argument('--project', '-p', help='Project name', default='General')
    parser.add_argument('--interval', '-i', type=int, help='Interval between screenshots (seconds)', default=5)
    parser.add_argument('--count', '-c', type=int, help='Number of screenshots to capture', default=1)
    parser.add_argument('--description', '-d', help='Screenshot description')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--series', action='store_true', help='Capture series of screenshots')
    
    args = parser.parse_args()
    
    documenter = ScreenshotDocumenter(project_name=args.project)
    
    print(f"\n📸 Screenshot Documenter")
    print(f"Project: {args.project}")
    print(f"Output: {documenter.docs_dir}\n")
    
    if args.interactive:
        documenter.capture_interactive()
    elif args.series:
        documenter.capture_series(args.interval, args.count, args.description)
        documenter.generate_index()
    else:
        documenter.capture_single(args.description)
        documenter.generate_index()

if __name__ == "__main__":
    main()
