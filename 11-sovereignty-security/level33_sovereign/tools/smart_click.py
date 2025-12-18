#!/usr/bin/env python3
"""
Smart Click - Vision-Guided Clicking for Level 33
Combines vision tools with physical agency for intelligent UI interaction
"""

import subprocess
import time
from pathlib import Path
from vision_tools import VisionTools
from physical_hand import safe_click
from screen_tools import get_screen_resolution, validate_coordinates


class SmartClicker:
    """Intelligent clicking with visual feedback and retry logic"""
    
    def __init__(self):
        self.vision = VisionTools()
        self.max_retries = 3
        self.retry_delay = 1.0
        
    def click_with_verification(self, x, y, expected_change=True, confirm=True):
        """
        Click and verify the action had an effect
        
        Args:
            x, y: Coordinates to click
            expected_change: Whether to expect UI change
            confirm: Whether to ask for user confirmation
            
        Returns:
            True if successful, False otherwise
        """
        # Validate coordinates
        if not validate_coordinates(x, y):
            print(f"Invalid coordinates: ({x}, {y})")
            return False
        
        # Capture before state
        before_screenshot = self.vision.capture_screen("before_click.png")
        
        # Perform click
        result = safe_click(x, y, confirm=confirm)
        
        if "Error" in result or "blocked" in result.lower():
            print(f"Click failed: {result}")
            return False
        
        # Wait for UI to update
        time.sleep(0.5)
        
        # Verify change if expected
        if expected_change:
            after_screenshot = self.vision.capture_screen("after_click.png")
            similarity = self.vision.compare_screenshots(before_screenshot, after_screenshot)
            
            if similarity > 0.98:  # Less than 2% change
                print(f"Warning: Click may not have had effect (similarity: {similarity:.2%})")
                return False
            else:
                print(f"Click verified (change detected: {(1-similarity)*100:.1f}%)")
                return True
        
        return True
    
    def click_with_retry(self, x, y, max_retries=None, confirm=True):
        """
        Click with automatic retry on failure
        
        Args:
            x, y: Coordinates to click
            max_retries: Maximum retry attempts
            confirm: Whether to ask for user confirmation
            
        Returns:
            True if successful, False if all retries failed
        """
        if max_retries is None:
            max_retries = self.max_retries
        
        for attempt in range(max_retries):
            print(f"Attempt {attempt + 1}/{max_retries}...")
            
            if self.click_with_verification(x, y, confirm=confirm):
                return True
            
            if attempt < max_retries - 1:
                print(f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
        
        print(f"Failed after {max_retries} attempts")
        return False
    
    def click_color_target(self, target_color, tolerance=20, confirm=True):
        """
        Find and click on a UI element by color
        
        Args:
            target_color: RGB tuple of target color
            tolerance: Color matching tolerance
            confirm: Whether to ask for user confirmation
            
        Returns:
            True if found and clicked, False otherwise
        """
        print(f"Searching for color: RGB{target_color}...")
        
        # Find regions matching color
        regions = self.vision.find_color_region(target_color, tolerance)
        
        if not regions:
            print("No matching color found")
            return False
        
        print(f"Found {len(regions)} matching regions")
        
        # Click the first match (center of region)
        x, y, w, h = regions[0]
        click_x = x + w // 2
        click_y = y + h // 2
        
        print(f"Clicking at ({click_x}, {click_y})...")
        return self.click_with_verification(click_x, click_y, confirm=confirm)
    
    def click_and_wait_for_change(self, x, y, timeout=5, confirm=True):
        """
        Click and wait for UI to change
        
        Args:
            x, y: Coordinates to click
            timeout: Maximum wait time for change
            confirm: Whether to ask for user confirmation
            
        Returns:
            True if change detected, False if timeout
        """
        # Capture before state
        before = self.vision.capture_screen("before_wait.png")
        
        # Click
        result = safe_click(x, y, confirm=confirm)
        if "Error" in result or "blocked" in result.lower():
            return False
        
        # Wait for change
        start_time = time.time()
        while time.time() - start_time < timeout:
            time.sleep(0.2)
            after = self.vision.capture_screen("after_wait.png")
            similarity = self.vision.compare_screenshots(before, after)
            
            if similarity < 0.98:  # Change detected
                print(f"Change detected after {time.time() - start_time:.1f}s")
                return True
        
        print(f"No change detected after {timeout}s")
        return False
    
    def adaptive_click(self, approximate_x, approximate_y, search_radius=50, confirm=True):
        """
        Click with adaptive coordinate adjustment
        Useful when exact coordinates may vary
        
        Args:
            approximate_x, approximate_y: Approximate target coordinates
            search_radius: Radius to search for clickable elements
            confirm: Whether to ask for user confirmation
            
        Returns:
            True if successful, False otherwise
        """
        print(f"Adaptive click near ({approximate_x}, {approximate_y})...")
        
        # Try exact coordinates first
        if self.click_with_verification(approximate_x, approximate_y, confirm=confirm):
            return True
        
        # Try nearby coordinates in a spiral pattern
        offsets = [
            (0, 0),
            (10, 0), (-10, 0), (0, 10), (0, -10),
            (20, 0), (-20, 0), (0, 20), (0, -20),
            (10, 10), (-10, -10), (10, -10), (-10, 10)
        ]
        
        for dx, dy in offsets:
            if abs(dx) > search_radius or abs(dy) > search_radius:
                continue
            
            x = approximate_x + dx
            y = approximate_y + dy
            
            if validate_coordinates(x, y):
                print(f"Trying offset ({dx}, {dy})...")
                if self.click_with_verification(x, y, confirm=confirm):
                    print(f"Success with offset ({dx}, {dy})")
                    return True
        
        print("Adaptive click failed")
        return False


class ClickSequence:
    """Manage sequences of clicks with timing and verification"""
    
    def __init__(self):
        self.clicker = SmartClicker()
        self.sequence = []
        
    def add_click(self, x, y, delay_after=0.5, verify=True):
        """
        Add a click to the sequence
        
        Args:
            x, y: Coordinates
            delay_after: Delay after click (seconds)
            verify: Whether to verify the click
        """
        self.sequence.append({
            'x': x,
            'y': y,
            'delay': delay_after,
            'verify': verify
        })
    
    def execute(self, confirm=True):
        """
        Execute the click sequence
        
        Args:
            confirm: Whether to ask for confirmation
            
        Returns:
            True if all clicks successful, False otherwise
        """
        print(f"Executing sequence of {len(self.sequence)} clicks...")
        
        for i, click in enumerate(self.sequence):
            print(f"\nStep {i+1}/{len(self.sequence)}:")
            
            if click['verify']:
                success = self.clicker.click_with_verification(
                    click['x'], click['y'], confirm=confirm
                )
            else:
                result = safe_click(click['x'], click['y'], confirm=confirm)
                success = "Error" not in result and "blocked" not in result.lower()
            
            if not success:
                print(f"Sequence failed at step {i+1}")
                return False
            
            if click['delay'] > 0:
                time.sleep(click['delay'])
        
        print("\nSequence completed successfully")
        return True
    
    def clear(self):
        """Clear the sequence"""
        self.sequence = []


# Convenience functions
def smart_click(x, y, verify=True, confirm=True):
    """Quick smart click with verification"""
    clicker = SmartClicker()
    if verify:
        return clicker.click_with_verification(x, y, confirm=confirm)
    else:
        result = safe_click(x, y, confirm=confirm)
        return "Error" not in result and "blocked" not in result.lower()


def click_with_retry(x, y, retries=3, confirm=True):
    """Quick click with retry"""
    clicker = SmartClicker()
    return clicker.click_with_retry(x, y, max_retries=retries, confirm=confirm)


def click_color(color_rgb, tolerance=20, confirm=True):
    """Quick color-based click"""
    clicker = SmartClicker()
    return clicker.click_color_target(color_rgb, tolerance, confirm)


# Test functionality
if __name__ == "__main__":
    print("=== Smart Click Test ===")
    print("\nThis will test vision-guided clicking.")
    print("Make sure you have a visible UI element to click.\n")
    
    clicker = SmartClicker()
    
    # Test 1: Basic smart click
    print("Test 1: Smart click with verification")
    print("Will click at (100, 100) and verify change...")
    success = clicker.click_with_verification(100, 100, expected_change=False)
    print(f"Result: {'Success' if success else 'Failed'}\n")
    
    # Test 2: Click sequence
    print("Test 2: Click sequence")
    sequence = ClickSequence()
    sequence.add_click(100, 100, delay_after=1.0)
    sequence.add_click(200, 200, delay_after=1.0)
    print("Executing 2-click sequence...")
    success = sequence.execute(confirm=True)
    print(f"Result: {'Success' if success else 'Failed'}\n")
    
    print("=== Smart Click Test Complete ===")
