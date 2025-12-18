#!/usr/bin/env python3
"""
VY Coordination Translator - Blueprint Implementation
======================================================

This module implements the Coordinate Translation Matrix (CTM) for the Vy system
on Mac Mini M1 (Apple Silicon) with Retina displays.

The primary challenge: Retina displays create a "Coordinate Rift" between physical
pixels (what Computer Vision sees) and logical points (what macOS expects for input).

Author: NanoApex/MoIE Architecture Team
Platform: macOS (Monterey through Sequoia) on Apple Silicon M1
Dependencies: mss (screen capture), subprocess (for cliclick)
"""

import subprocess
import sys
from typing import Tuple, Dict, Optional
import json

try:
    import mss
except ImportError:
    print("ERROR: mss library not found. Install with: pip install mss")
    sys.exit(1)


class CoordinateTranslator:
    """
    Handles the translation between physical pixel coordinates and logical point coordinates
    for macOS Retina displays.
    
    This class implements the mathematical formulation from Section 3.1 of the Blueprint:
    - Calculates dynamic scaling factors (Sx, Sy) per monitor
    - Handles multi-monitor setups with global coordinate offsets
    - Supports "More Space" and virtual framebuffer configurations
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the Coordinate Translator.
        
        Args:
            verbose: If True, print diagnostic information
        """
        self.verbose = verbose
        self.sct = mss.mss()
        self.monitors = self.sct.monitors
        self.scaling_cache = {}
        
        if self.verbose:
            print("=== Coordinate Translator Initialized ===")
            print(f"Detected {len(self.monitors) - 1} monitor(s)")
            for i, mon in enumerate(self.monitors[1:], 1):
                print(f"Monitor {i}: Logical {mon['width']}x{mon['height']} at ({mon['left']}, {mon['top']})")
    
    def get_scaling_factors(self, monitor_index: int = 1) -> Tuple[float, float]:
        """
        Calculate the dynamic scaling factors for a specific monitor.
        
        This implements the formula from Section 3.1.1:
        Sx = W_img / L_width
        Sy = H_img / L_height
        
        Args:
            monitor_index: Monitor number (1-indexed, 0 is all monitors combined)
        
        Returns:
            Tuple of (Sx, Sy) scaling factors
        """
        if monitor_index in self.scaling_cache:
            return self.scaling_cache[monitor_index]
        
        if monitor_index >= len(self.monitors):
            raise ValueError(f"Monitor index {monitor_index} out of range (max: {len(self.monitors) - 1})")
        
        monitor = self.monitors[monitor_index]
        
        # Capture a 1x1 pixel to get the actual framebuffer dimensions
        # without the overhead of capturing the entire screen
        with mss.mss() as sct:
            # Grab the full monitor to get actual pixel dimensions
            screenshot = sct.grab(monitor)
            W_img = screenshot.width
            H_img = screenshot.height
        
        L_width = monitor['width']
        L_height = monitor['height']
        
        Sx = W_img / L_width
        Sy = H_img / L_height
        
        self.scaling_cache[monitor_index] = (Sx, Sy)
        
        if self.verbose:
            print(f"\n=== Scaling Factors for Monitor {monitor_index} ===")
            print(f"Physical Resolution: {W_img}x{H_img} pixels")
            print(f"Logical Resolution: {L_width}x{L_height} points")
            print(f"Scaling Factors: Sx={Sx:.2f}, Sy={Sy:.2f}")
            
            if Sx == 2.0 and Sy == 2.0:
                print("Display Mode: Standard Retina (2x)")
            elif Sx == 1.0 and Sy == 1.0:
                print("Display Mode: Non-Retina (1x)")
            else:
                print(f"Display Mode: Custom/More Space ({Sx:.2f}x)")
        
        return Sx, Sy
    
    def physical_to_logical(self, 
                           x_img: float, 
                           y_img: float, 
                           monitor_index: int = 1) -> Tuple[int, int]:
        """
        Convert physical pixel coordinates to logical point coordinates.
        
        This implements the complete transformation from Section 3.1.1:
        1. Calculate scaling factors
        2. Convert to local logical coordinates
        3. Apply global offset
        
        Args:
            x_img: X coordinate in the captured image (physical pixels)
            y_img: Y coordinate in the captured image (physical pixels)
            monitor_index: Monitor number (1-indexed)
        
        Returns:
            Tuple of (x_target, y_target) in global logical coordinates
        """
        if monitor_index >= len(self.monitors):
            raise ValueError(f"Monitor index {monitor_index} out of range")
        
        monitor = self.monitors[monitor_index]
        Sx, Sy = self.get_scaling_factors(monitor_index)
        
        # Step 1: Convert to local logical coordinates
        x_local = x_img / Sx
        y_local = y_img / Sy
        
        # Step 2: Apply global offset
        L_left = monitor['left']
        L_top = monitor['top']
        
        x_target = int(L_left + x_local)
        y_target = int(L_top + y_local)
        
        if self.verbose:
            print(f"\n=== Coordinate Translation ===")
            print(f"Input (physical): ({x_img}, {y_img})")
            print(f"Local (logical): ({x_local:.2f}, {y_local:.2f})")
            print(f"Global offset: ({L_left}, {L_top})")
            print(f"Output (global logical): ({x_target}, {y_target})")
        
        return x_target, y_target
    
    def logical_to_physical(self,
                           x_target: int,
                           y_target: int,
                           monitor_index: int = 1) -> Tuple[int, int]:
        """
        Convert logical point coordinates to physical pixel coordinates.
        
        This is the inverse transformation, useful for verification.
        
        Args:
            x_target: X coordinate in global logical space
            y_target: Y coordinate in global logical space
            monitor_index: Monitor number (1-indexed)
        
        Returns:
            Tuple of (x_img, y_img) in physical pixel coordinates
        """
        if monitor_index >= len(self.monitors):
            raise ValueError(f"Monitor index {monitor_index} out of range")
        
        monitor = self.monitors[monitor_index]
        Sx, Sy = self.get_scaling_factors(monitor_index)
        
        # Remove global offset
        L_left = monitor['left']
        L_top = monitor['top']
        
        x_local = x_target - L_left
        y_local = y_target - L_top
        
        # Convert to physical pixels
        x_img = int(x_local * Sx)
        y_img = int(y_local * Sy)
        
        return x_img, y_img
    
    def get_monitor_for_point(self, x: int, y: int) -> Optional[int]:
        """
        Determine which monitor contains a given logical point.
        
        Args:
            x: X coordinate in global logical space
            y: Y coordinate in global logical space
        
        Returns:
            Monitor index (1-indexed) or None if point is off-screen
        """
        for i, monitor in enumerate(self.monitors[1:], 1):
            left = monitor['left']
            top = monitor['top']
            right = left + monitor['width']
            bottom = top + monitor['height']
            
            if left <= x < right and top <= y < bottom:
                return i
        
        return None
    
    def verify_cliclick_available(self) -> bool:
        """
        Verify that cliclick is installed and accessible.
        
        Returns:
            True if cliclick is available, False otherwise
        """
        try:
            result = subprocess.run(['which', 'cliclick'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            available = result.returncode == 0
            
            if self.verbose:
                if available:
                    print(f"✓ cliclick found at: {result.stdout.strip()}")
                else:
                    print("✗ cliclick not found. Install with: brew install cliclick")
            
            return available
        except Exception as e:
            if self.verbose:
                print(f"✗ Error checking for cliclick: {e}")
            return False
    
    def click_at_physical(self, 
                         x_img: float, 
                         y_img: float, 
                         monitor_index: int = 1,
                         easing: int = 20,
                         wait_ms: int = 50) -> bool:
        """
        Click at a physical pixel coordinate using cliclick.
        
        This implements the actuation protocol from Section 4.2.
        
        Args:
            x_img: X coordinate in physical pixels
            y_img: Y coordinate in physical pixels
            monitor_index: Monitor number (1-indexed)
            easing: Easing factor for mouse movement (higher = slower/smoother)
            wait_ms: Milliseconds to wait before clicking
        
        Returns:
            True if successful, False otherwise
        """
        if not self.verify_cliclick_available():
            print("ERROR: cliclick not available")
            return False
        
        # Translate to logical coordinates
        x_target, y_target = self.physical_to_logical(x_img, y_img, monitor_index)
        
        # Build cliclick command
        # Format: cliclick -e <easing> m:<x>,<y> w:<wait> c:.
        cmd = f"cliclick -e {easing} m:{x_target},{y_target} w:{wait_ms} c:."
        
        if self.verbose:
            print(f"\n=== Executing Click ===")
            print(f"Command: {cmd}")
        
        try:
            result = subprocess.run(cmd, 
                                  shell=True, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            
            if result.returncode == 0:
                if self.verbose:
                    print("✓ Click executed successfully")
                return True
            else:
                print(f"✗ Click failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ Error executing click: {e}")
            return False
    
    def drag_physical(self,
                     x_start_img: float,
                     y_start_img: float,
                     x_end_img: float,
                     y_end_img: float,
                     monitor_index: int = 1,
                     easing: int = 20) -> bool:
        """
        Perform a drag operation using physical pixel coordinates.
        
        This implements the Drag-and-Drop Protocol from Section 4.2.1.
        
        Args:
            x_start_img: Start X in physical pixels
            y_start_img: Start Y in physical pixels
            x_end_img: End X in physical pixels
            y_end_img: End Y in physical pixels
            monitor_index: Monitor number (1-indexed)
            easing: Easing factor for mouse movement
        
        Returns:
            True if successful, False otherwise
        """
        if not self.verify_cliclick_available():
            print("ERROR: cliclick not available")
            return False
        
        # Translate coordinates
        x_start, y_start = self.physical_to_logical(x_start_img, y_start_img, monitor_index)
        x_end, y_end = self.physical_to_logical(x_end_img, y_end_img, monitor_index)
        
        # Build drag command following the protocol:
        # 1. Approach: Move to source
        # 2. Latch: Drag down and wait
        # 3. Transport: Drag move to destination
        # 4. Settle: Wait at destination
        # 5. Release: Drag up
        cmd = (f"cliclick -e {easing} "
               f"m:{x_start},{y_start} w:50 "  # Approach
               f"dd:. w:100 "                    # Latch
               f"dm:{x_end},{y_end} w:100 "     # Transport + Settle
               f"du:.")                          # Release
        
        if self.verbose:
            print(f"\n=== Executing Drag ===")
            print(f"Start (physical): ({x_start_img}, {y_start_img})")
            print(f"End (physical): ({x_end_img}, {y_end_img})")
            print(f"Start (logical): ({x_start}, {y_start})")
            print(f"End (logical): ({x_end}, {y_end})")
            print(f"Command: {cmd}")
        
        try:
            result = subprocess.run(cmd,
                                  shell=True,
                                  capture_output=True,
                                  text=True,
                                  timeout=15)
            
            if result.returncode == 0:
                if self.verbose:
                    print("✓ Drag executed successfully")
                return True
            else:
                print(f"✗ Drag failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ Error executing drag: {e}")
            return False
    
    def generate_diagnostic_report(self) -> Dict:
        """
        Generate a comprehensive diagnostic report of the display configuration.
        
        Returns:
            Dictionary containing diagnostic information
        """
        report = {
            "system": "VY Coordination Translator",
            "platform": "macOS Apple Silicon M1",
            "monitors": []
        }
        
        for i, monitor in enumerate(self.monitors[1:], 1):
            Sx, Sy = self.get_scaling_factors(i)
            
            # Capture to get physical dimensions
            with mss.mss() as sct:
                screenshot = sct.grab(monitor)
                W_img = screenshot.width
                H_img = screenshot.height
            
            mon_info = {
                "index": i,
                "logical": {
                    "width": monitor['width'],
                    "height": monitor['height'],
                    "left": monitor['left'],
                    "top": monitor['top']
                },
                "physical": {
                    "width": W_img,
                    "height": H_img
                },
                "scaling": {
                    "Sx": Sx,
                    "Sy": Sy,
                    "mode": self._get_display_mode(Sx, Sy)
                }
            }
            
            report["monitors"].append(mon_info)
        
        return report
    
    def _get_display_mode(self, Sx: float, Sy: float) -> str:
        """Determine the display mode based on scaling factors."""
        if Sx == 2.0 and Sy == 2.0:
            return "Standard Retina (2x)"
        elif Sx == 1.0 and Sy == 1.0:
            return "Non-Retina (1x)"
        elif Sx == 1.5 and Sy == 1.5:
            return "More Space (1.5x)"
        else:
            return f"Custom ({Sx:.2f}x)"


def run_loopback_test(translator: CoordinateTranslator) -> bool:
    """
    Perform the Loopback Test from Section 5.2.1 to verify TCC permissions.
    
    This test verifies that cliclick has the necessary Accessibility permissions
    to control the mouse.
    
    Args:
        translator: CoordinateTranslator instance
    
    Returns:
        True if permissions are granted, False otherwise
    """
    print("\n=== Running Loopback Test (TCC Verification) ===")
    
    if not translator.verify_cliclick_available():
        print("✗ cliclick not available - cannot perform loopback test")
        return False
    
    try:
        # Query current position
        result = subprocess.run(['cliclick', 'p'],
                              capture_output=True,
                              text=True,
                              timeout=5)
        
        if result.returncode != 0:
            print("✗ Failed to query mouse position")
            return False
        
        # Parse position (format: "X,Y")
        pos_str = result.stdout.strip()
        x0, y0 = map(int, pos_str.split(','))
        print(f"Initial position: ({x0}, {y0})")
        
        # Attempt minimal move
        new_x = x0 + 1
        subprocess.run(f'cliclick m:{new_x},{y0}',
                      shell=True,
                      capture_output=True,
                      timeout=5)
        
        # Query new position
        result = subprocess.run(['cliclick', 'p'],
                              capture_output=True,
                              text=True,
                              timeout=5)
        
        pos_str = result.stdout.strip()
        x1, y1 = map(int, pos_str.split(','))
        print(f"New position: ({x1}, {y1})")
        
        # Restore original position
        subprocess.run(f'cliclick m:{x0},{y0}',
                      shell=True,
                      capture_output=True,
                      timeout=5)
        
        if x1 == x0 and y1 == y0:
            print("✗ LOOPBACK TEST FAILED")
            print("   TCC is blocking event injection.")
            print("   Enable Accessibility permissions:")
            print("   System Settings → Privacy & Security → Accessibility")
            print("   Add Terminal (or your Python app) to the allowed list.")
            return False
        else:
            print("✓ LOOPBACK TEST PASSED")
            print("   Accessibility permissions are granted.")
            return True
    
    except Exception as e:
        print(f"✗ Loopback test error: {e}")
        return False


def main():
    """
    Main entry point for the Coordinate Translator.
    
    Demonstrates usage and runs diagnostic tests.
    """
    print("=" * 70)
    print("VY COORDINATION TRANSLATOR - Mac M1 Retina Display Handler")
    print("Blueprint Implementation: NanoApex/MoIE Architecture")
    print("=" * 70)
    
    # Initialize translator
    translator = CoordinateTranslator(verbose=True)
    
    # Run loopback test
    loopback_passed = run_loopback_test(translator)
    
    # Generate diagnostic report
    print("\n=== Diagnostic Report ===")
    report = translator.generate_diagnostic_report()
    print(json.dumps(report, indent=2))
    
    # Example usage
    print("\n=== Example Usage ===")
    print("# To click at physical pixel (1000, 500) on monitor 1:")
    print("translator.click_at_physical(1000, 500, monitor_index=1)")
    print()
    print("# To drag from (100, 100) to (500, 500):")
    print("translator.drag_physical(100, 100, 500, 500, monitor_index=1)")
    print()
    print("# To translate coordinates manually:")
    print("x_logical, y_logical = translator.physical_to_logical(1920, 1080, monitor_index=1)")
    
    # Safety check
    if not loopback_passed:
        print("\n" + "!" * 70)
        print("WARNING: Loopback test failed. Fix permissions before using Vy.")
        print("!" * 70)
        return 1
    
    print("\n" + "=" * 70)
    print("✓ Coordination Translator initialized successfully")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
