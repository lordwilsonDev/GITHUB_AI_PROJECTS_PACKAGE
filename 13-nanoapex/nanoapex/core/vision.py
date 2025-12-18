"""
NanoApex Vision Module - Moondream Screen Understanding
Captures screen, analyzes with Moondream, returns semantic description
"""

import subprocess
import base64
import json
import os
from datetime import datetime

class VisionModule:
    def __init__(self, model_name="moondream:latest", screenshots_dir="logs/screenshots"):
        self.model_name = model_name
        self.screenshots_dir = screenshots_dir
        os.makedirs(screenshots_dir, exist_ok=True)
        
    def capture_screen(self):
        """Capture current screen state using screencapture"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"{self.screenshots_dir}/screen_{timestamp}.png"
        
        # macOS screencapture - captures main display
        subprocess.run(['screencapture', '-x', filepath], check=True)
        
        return filepath
    
    def encode_image(self, filepath):
        """Encode image to base64 for Ollama"""
        with open(filepath, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def analyze_screen(self, query="Describe what you see on this screen in detail."):
        """
        Capture screen and analyze with Moondream
        Returns semantic description of screen content
        """
        # Capture current screen
        screenshot_path = self.capture_screen()
        
        # Encode for Ollama
        image_b64 = self.encode_image(screenshot_path)
        
        # Query Moondream via Ollama
        payload = {
            "model": self.model_name,
            "prompt": query,
            "images": [image_b64],
            "stream": False
        }
        
        result = subprocess.run(
            ['ollama', 'run', self.model_name],
            input=json.dumps(payload),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Moondream analysis failed: {result.stderr}")
        
        response = json.loads(result.stdout)
        description = response.get('response', '')
        
        return {
            'screenshot': screenshot_path,
            'description': description,
            'timestamp': datetime.now().isoformat()
        }
    
    def locate_element(self, element_description):
        """
        Specialized query to find UI elements
        Returns semantic description to help locate.py find coordinates
        """
        query = f"Where is the {element_description} located on this screen? Describe its position relative to other elements."
        return self.analyze_screen(query)

if __name__ == "__main__":
    # Test vision module
    vision = VisionModule()
    result = vision.analyze_screen()
    print(f"Screenshot saved: {result['screenshot']}")
    print(f"Description: {result['description']}")
