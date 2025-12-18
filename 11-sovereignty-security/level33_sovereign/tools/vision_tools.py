#!/usr/bin/env python3
"""
Vision Tools for Level 33 Sovereign Architecture
Provides AI-powered visual analysis for intelligent clicking and UI interaction
"""

import subprocess
import os
import time
from datetime import datetime
from pathlib import Path

# Try to import PIL for image processing
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not available. Install with: pip install Pillow")


class VisionTools:
    """AI-powered vision tools for screen analysis"""
    
    def __init__(self, screenshots_dir="workspace/screenshots"):
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.last_screenshot = None
        
    def capture_screen(self, filename=None, region=None):
        """
        Capture screenshot of entire screen or specific region
        
        Args:
            filename: Optional custom filename
            region: Optional tuple (x, y, width, height) for partial capture
            
        Returns:
            Path to captured screenshot
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screen_{timestamp}.png"
            
        filepath = self.screenshots_dir / filename
        
        try:
            if region:
                x, y, w, h = region
                # Use screencapture with region
                cmd = ["screencapture", "-R", f"{x},{y},{w},{h}", str(filepath)]
            else:
                # Capture entire screen
                cmd = ["screencapture", str(filepath)]
                
            subprocess.run(cmd, check=True)
            self.last_screenshot = filepath
            return filepath
            
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None
    
    def get_screen_resolution(self):
        """
        Get current screen resolution
        
        Returns:
            Tuple (width, height) or None if detection fails
        """
        try:
            # Use system_profiler to get display info
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse output for resolution
            for line in result.stdout.split('\n'):
                if 'Resolution' in line:
                    # Extract resolution like "1920 x 1080"
                    parts = line.split(':')[1].strip().split('x')
                    if len(parts) == 2:
                        width = int(parts[0].strip())
                        height = int(parts[1].strip())
                        return (width, height)
                        
        except Exception as e:
            print(f"Error detecting resolution: {e}")
            
        # Fallback to common resolutions
        return (1920, 1080)
    
    def find_text_on_screen(self, text, capture_new=True):
        """
        Find text on screen using OCR
        
        Args:
            text: Text to search for
            capture_new: Whether to capture new screenshot
            
        Returns:
            List of (x, y, confidence) tuples where text was found
        """
        if capture_new:
            screenshot = self.capture_screen()
        else:
            screenshot = self.last_screenshot
            
        if not screenshot or not screenshot.exists():
            print("No screenshot available")
            return []
        
        try:
            # Use macOS built-in OCR via shortcuts
            # This is a placeholder - actual implementation would use Vision framework
            # or external OCR library
            print(f"Searching for text: '{text}'")
            print("Note: OCR integration requires additional setup")
            return []
            
        except Exception as e:
            print(f"Error in text detection: {e}")
            return []
    
    def find_color_region(self, color_rgb, tolerance=10, capture_new=True):
        """
        Find regions on screen matching a specific color
        
        Args:
            color_rgb: Tuple (r, g, b) of target color
            tolerance: Color matching tolerance (0-255)
            capture_new: Whether to capture new screenshot
            
        Returns:
            List of (x, y, width, height) regions
        """
        if not PIL_AVAILABLE:
            print("PIL required for color detection. Install: pip install Pillow")
            return []
            
        if capture_new:
            screenshot = self.capture_screen()
        else:
            screenshot = self.last_screenshot
            
        if not screenshot or not screenshot.exists():
            print("No screenshot available")
            return []
        
        try:
            img = Image.open(screenshot)
            pixels = img.load()
            width, height = img.size
            
            target_r, target_g, target_b = color_rgb
            regions = []
            
            # Simple color matching (can be optimized)
            for y in range(0, height, 10):  # Sample every 10 pixels
                for x in range(0, width, 10):
                    r, g, b = pixels[x, y][:3]  # Get RGB, ignore alpha
                    
                    # Check if color matches within tolerance
                    if (abs(r - target_r) <= tolerance and
                        abs(g - target_g) <= tolerance and
                        abs(b - target_b) <= tolerance):
                        regions.append((x, y, 10, 10))
            
            return regions
            
        except Exception as e:
            print(f"Error in color detection: {e}")
            return []
    
    def get_pixel_color(self, x, y, capture_new=True):
        """
        Get color of pixel at specific coordinates
        
        Args:
            x, y: Coordinates
            capture_new: Whether to capture new screenshot
            
        Returns:
            Tuple (r, g, b) or None
        """
        if not PIL_AVAILABLE:
            print("PIL required. Install: pip install Pillow")
            return None
            
        if capture_new:
            screenshot = self.capture_screen()
        else:
            screenshot = self.last_screenshot
            
        if not screenshot or not screenshot.exists():
            return None
        
        try:
            img = Image.open(screenshot)
            pixels = img.load()
            
            # Validate coordinates
            if 0 <= x < img.width and 0 <= y < img.height:
                return pixels[x, y][:3]  # Return RGB
            else:
                print(f"Coordinates ({x}, {y}) out of bounds")
                return None
                
        except Exception as e:
            print(f"Error getting pixel color: {e}")
            return None
    
    def compare_screenshots(self, screenshot1, screenshot2, threshold=0.95):
        """
        Compare two screenshots for similarity
        
        Args:
            screenshot1, screenshot2: Paths to screenshots
            threshold: Similarity threshold (0-1)
            
        Returns:
            Similarity score (0-1)
        """
        if not PIL_AVAILABLE:
            print("PIL required. Install: pip install Pillow")
            return 0.0
        
        try:
            img1 = Image.open(screenshot1)
            img2 = Image.open(screenshot2)
            
            # Resize to same size if different
            if img1.size != img2.size:
                img2 = img2.resize(img1.size)
            
            # Convert to RGB
            img1 = img1.convert('RGB')
            img2 = img2.convert('RGB')
            
            # Simple pixel-by-pixel comparison
            pixels1 = list(img1.getdata())
            pixels2 = list(img2.getdata())
            
            matches = sum(1 for p1, p2 in zip(pixels1, pixels2) if p1 == p2)
            total = len(pixels1)
            
            similarity = matches / total if total > 0 else 0.0
            return similarity
            
        except Exception as e:
            print(f"Error comparing screenshots: {e}")
            return 0.0
    
    def detect_ui_change(self, wait_time=1.0, threshold=0.95):
        """
        Detect if UI has changed by comparing screenshots
        
        Args:
            wait_time: Time to wait between screenshots
            threshold: Change detection threshold
            
        Returns:
            True if change detected, False otherwise
        """
        # Capture first screenshot
        screenshot1 = self.capture_screen("before.png")
        if not screenshot1:
            return False
        
        # Wait
        time.sleep(wait_time)
        
        # Capture second screenshot
        screenshot2 = self.capture_screen("after.png")
        if not screenshot2:
            return False
        
        # Compare
        similarity = self.compare_screenshots(screenshot1, screenshot2)
        changed = similarity < threshold
        
        print(f"Similarity: {similarity:.2%} - Changed: {changed}")
        return changed
    
    def find_button_by_color(self, button_color=(0, 122, 255), tolerance=20):
        """
        Find buttons on screen by their color (e.g., macOS blue buttons)
        
        Args:
            button_color: RGB tuple of button color
            tolerance: Color matching tolerance
            
        Returns:
            List of potential button locations (x, y)
        """
        regions = self.find_color_region(button_color, tolerance)
        
        # Convert regions to center points
        buttons = []
        for x, y, w, h in regions:
            center_x = x + w // 2
            center_y = y + h // 2
            buttons.append((center_x, center_y))
        
        return buttons
    
    def wait_for_element(self, check_function, timeout=10, interval=0.5):
        """
        Wait for a UI element to appear
        
        Args:
            check_function: Function that returns True when element found
            timeout: Maximum wait time in seconds
            interval: Check interval in seconds
            
        Returns:
            True if element found, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if check_function():
                return True
            time.sleep(interval)
        
        return False
    
    def create_visual_diff(self, screenshot1, screenshot2, output_path=None):
        """
        Create a visual diff showing differences between two screenshots
        
        Args:
            screenshot1, screenshot2: Paths to screenshots
            output_path: Where to save diff image
            
        Returns:
            Path to diff image
        """
        if not PIL_AVAILABLE:
            print("PIL required. Install: pip install Pillow")
            return None
        
        try:
            from PIL import ImageChops
            
            img1 = Image.open(screenshot1).convert('RGB')
            img2 = Image.open(screenshot2).convert('RGB')
            
            # Resize if needed
            if img1.size != img2.size:
                img2 = img2.resize(img1.size)
            
            # Create difference image
            diff = ImageChops.difference(img1, img2)
            
            # Save
            if output_path is None:
                output_path = self.screenshots_dir / "diff.png"
            
            diff.save(output_path)
            print(f"Visual diff saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error creating visual diff: {e}")
            return None


# Convenience functions
def capture_screen(filename=None):
    """Quick screenshot capture"""
    vt = VisionTools()
    return vt.capture_screen(filename)


def get_screen_resolution():
    """Quick resolution detection"""
    vt = VisionTools()
    return vt.get_screen_resolution()


def find_text(text):
    """Quick text search"""
    vt = VisionTools()
    return vt.find_text_on_screen(text)


def detect_change(wait_time=1.0):
    """Quick change detection"""
    vt = VisionTools()
    return vt.detect_ui_change(wait_time)


# Test functionality
if __name__ == "__main__":
    print("=== Vision Tools Test ===\n")
    
    vt = VisionTools()
    
    # Test 1: Screen resolution
    print("1. Testing screen resolution detection...")
    resolution = vt.get_screen_resolution()
    print(f"   Screen resolution: {resolution[0]}x{resolution[1]}")
    
    # Test 2: Screenshot capture
    print("\n2. Testing screenshot capture...")
    screenshot = vt.capture_screen("test_vision.png")
    if screenshot:
        print(f"   Screenshot saved: {screenshot}")
    
    # Test 3: Pixel color
    if PIL_AVAILABLE:
        print("\n3. Testing pixel color detection...")
        color = vt.get_pixel_color(100, 100, capture_new=False)
        if color:
            print(f"   Color at (100, 100): RGB{color}")
    
    # Test 4: Change detection
    print("\n4. Testing UI change detection...")
    print("   Move your mouse or switch windows in the next 2 seconds...")
    changed = vt.detect_ui_change(wait_time=2.0)
    print(f"   UI changed: {changed}")
    
    print("\n=== Vision Tools Test Complete ===")
    print(f"Screenshots saved in: {vt.screenshots_dir}")
