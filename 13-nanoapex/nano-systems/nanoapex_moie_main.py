#!/usr/bin/env python3
"""
NanoApex/MoIE - Main Orchestration Script
Machine Optical & Intelligent Entity

This is the main entry point for the NanoApex autonomous vision system.
It integrates:
- Tesseract OCR (Vision)
- Ollama LLM (Cognition)
- Cliclick (Actuation)

Architecture: Vision → Cognition → Action
"""

import os
import sys
import time
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# Configure logging
log_file = '/tmp/nanoapex_moie_detailed.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('NanoApex')

# Configuration
CONFIG = {
    'tesseract_cmd': r'/opt/homebrew/bin/tesseract',
    'cliclick_cmd': '/opt/homebrew/bin/cliclick',
    'ollama_host': os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
    'ollama_model': 'llama3',
    'tessdata_prefix': '/opt/homebrew/share/tessdata',
    'loop_interval': 5,  # seconds between vision cycles
    'max_retries': 3,
}

class NanoApexMoIE:
    """Main orchestration class for NanoApex/MoIE system"""
    
    def __init__(self):
        self.logger = logging.getLogger('NanoApex.MoIE')
        self.running = False
        self.cycle_count = 0
        
    def check_dependencies(self):
        """Verify all required dependencies are available"""
        self.logger.info("Checking dependencies...")
        
        dependencies = {
            'Tesseract': CONFIG['tesseract_cmd'],
            'Cliclick': CONFIG['cliclick_cmd'],
            'Python PIL': None,  # Import check
            'Pytesseract': None,  # Import check
        }
        
        all_ok = True
        
        # Check binaries
        for name, path in dependencies.items():
            if path:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    self.logger.info(f"✓ {name} found at: {path}")
                else:
                    self.logger.error(f"✗ {name} NOT found at: {path}")
                    all_ok = False
        
        # Check Python imports
        try:
            from PIL import ImageGrab
            self.logger.info("✓ PIL/Pillow available")
        except ImportError as e:
            self.logger.error(f"✗ PIL/Pillow not available: {e}")
            all_ok = False
        
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = CONFIG['tesseract_cmd']
            self.logger.info("✓ Pytesseract available")
        except ImportError as e:
            self.logger.error(f"✗ Pytesseract not available: {e}")
            all_ok = False
        
        # Check Ollama
        try:
            import requests
            response = requests.get(f"{CONFIG['ollama_host']}/api/tags", timeout=5)
            if response.status_code == 200:
                self.logger.info(f"✓ Ollama API accessible at {CONFIG['ollama_host']}")
            else:
                self.logger.warning(f"⚠ Ollama API returned status {response.status_code}")
        except Exception as e:
            self.logger.error(f"✗ Ollama API not accessible: {e}")
            all_ok = False
        
        return all_ok
    
    def check_permissions(self):
        """Verify required macOS permissions are granted"""
        self.logger.info("Checking macOS permissions...")
        
        permissions_ok = True
        
        # Check Accessibility (via cliclick test)
        try:
            result = subprocess.run(
                [CONFIG['cliclick_cmd'], 'p'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.logger.info(f"✓ Accessibility permission granted (mouse at: {result.stdout.strip()})")
            else:
                self.logger.error("✗ Accessibility permission NOT granted")
                permissions_ok = False
        except Exception as e:
            self.logger.error(f"✗ Accessibility check failed: {e}")
            permissions_ok = False
        
        # Check Screen Recording (via screen capture test)
        try:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab(bbox=(0, 0, 100, 100))
            
            # Check if image is all black (permission denied)
            pixels = list(screenshot.getdata())
            black_pixels = sum(1 for p in pixels if p == (0, 0, 0) or (isinstance(p, int) and p == 0))
            black_ratio = black_pixels / len(pixels) if pixels else 1.0
            
            if black_ratio < 0.95:
                self.logger.info(f"✓ Screen Recording permission granted ({(1-black_ratio)*100:.1f}% content)")
            else:
                self.logger.error("✗ Screen Recording permission NOT granted (black screen)")
                permissions_ok = False
        except Exception as e:
            self.logger.error(f"✗ Screen Recording check failed: {e}")
            permissions_ok = False
        
        return permissions_ok
    
    def capture_screen(self):
        """Capture the current screen"""
        try:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
            self.logger.debug(f"Screen captured: {screenshot.size[0]}x{screenshot.size[1]}")
            return screenshot
        except Exception as e:
            self.logger.error(f"Screen capture failed: {e}")
            return None
    
    def extract_text(self, image):
        """Extract text from image using Tesseract OCR"""
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = CONFIG['tesseract_cmd']
            
            # Extract text with bounding boxes
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Filter out empty text
            results = []
            for i, text in enumerate(data['text']):
                if text.strip():
                    results.append({
                        'text': text,
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'confidence': data['conf'][i]
                    })
            
            self.logger.debug(f"OCR extracted {len(results)} text elements")
            return results
        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            return []
    
    def process_with_llm(self, ocr_data):
        """Process OCR data with Ollama LLM to decide action"""
        try:
            import requests
            
            # Build context from OCR data
            text_elements = [item['text'] for item in ocr_data[:50]]  # Limit to first 50
            context = "Screen contains: " + ", ".join(text_elements)
            
            # Query LLM
            prompt = f"{context}\n\nWhat action should I take? Respond with: WAIT, CLICK <text>, or TYPE <text>"
            
            response = requests.post(
                f"{CONFIG['ollama_host']}/api/generate",
                json={
                    'model': CONFIG['ollama_model'],
                    'prompt': prompt,
                    'stream': False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                action = result.get('response', 'WAIT').strip()
                self.logger.debug(f"LLM decision: {action}")
                return action
            else:
                self.logger.warning(f"LLM request failed: {response.status_code}")
                return 'WAIT'
        except Exception as e:
            self.logger.error(f"LLM processing failed: {e}")
            return 'WAIT'
    
    def execute_action(self, action, ocr_data):
        """Execute the decided action using cliclick"""
        try:
            if action.startswith('CLICK'):
                # Extract target text
                target = action.replace('CLICK', '').strip()
                
                # Find target in OCR data
                for item in ocr_data:
                    if target.lower() in item['text'].lower():
                        # Calculate center of bounding box
                        x = item['x'] + item['width'] // 2
                        y = item['y'] + item['height'] // 2
                        
                        # Execute click
                        subprocess.run(
                            [CONFIG['cliclick_cmd'], f'c:{x},{y}'],
                            timeout=5
                        )
                        self.logger.info(f"Clicked on '{target}' at ({x}, {y})")
                        return True
                
                self.logger.warning(f"Target '{target}' not found on screen")
                return False
            
            elif action.startswith('TYPE'):
                # Extract text to type
                text = action.replace('TYPE', '').strip()
                
                # Execute typing
                subprocess.run(
                    [CONFIG['cliclick_cmd'], f't:{text}'],
                    timeout=5
                )
                self.logger.info(f"Typed: {text}")
                return True
            
            else:
                # WAIT or unknown action
                self.logger.debug("Action: WAIT")
                return True
        except Exception as e:
            self.logger.error(f"Action execution failed: {e}")
            return False
    
    def run_cycle(self):
        """Run one complete vision-cognition-action cycle"""
        self.cycle_count += 1
        self.logger.info(f"=== Cycle {self.cycle_count} ===")
        
        # 1. Vision: Capture screen
        screenshot = self.capture_screen()
        if not screenshot:
            return False
        
        # 2. Vision: Extract text
        ocr_data = self.extract_text(screenshot)
        if not ocr_data:
            self.logger.debug("No text found on screen")
            return True
        
        # 3. Cognition: Process with LLM
        action = self.process_with_llm(ocr_data)
        
        # 4. Action: Execute decision
        success = self.execute_action(action, ocr_data)
        
        return success
    
    def run(self):
        """Main run loop"""
        self.logger.info("="*60)
        self.logger.info("NanoApex/MoIE Starting")
        self.logger.info(f"System: macOS {os.uname().release}")
        self.logger.info(f"User: {os.getenv('USER', 'unknown')}")
        self.logger.info(f"Time: {datetime.now().isoformat()}")
        self.logger.info("="*60)
        
        # Pre-flight checks
        if not self.check_dependencies():
            self.logger.error("Dependency check failed. Exiting.")
            return 1
        
        if not self.check_permissions():
            self.logger.error("Permission check failed. Exiting.")
            self.logger.error("Grant permissions:")
            self.logger.error("  Accessibility: System Settings → Privacy & Security → Accessibility")
            self.logger.error("  Screen Recording: System Settings → Privacy & Security → Screen Recording")
            return 1
        
        self.logger.info("All checks passed. Starting main loop...")
        self.running = True
        
        # Main loop
        try:
            while self.running:
                try:
                    self.run_cycle()
                except Exception as e:
                    self.logger.error(f"Cycle error: {e}", exc_info=True)
                
                # Wait before next cycle
                time.sleep(CONFIG['loop_interval'])
        
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}", exc_info=True)
            return 1
        finally:
            self.logger.info(f"Shutting down after {self.cycle_count} cycles")
            self.running = False
        
        return 0

def main():
    """Entry point"""
    moie = NanoApexMoIE()
    return moie.run()

if __name__ == '__main__':
    sys.exit(main())
