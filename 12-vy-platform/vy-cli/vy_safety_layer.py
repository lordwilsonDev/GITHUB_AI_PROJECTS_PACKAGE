#!/usr/bin/env python3
"""
Vy Safety Layer Module

Forensic verification of TCC (Transparency, Consent, and Control) permissions
before executing the main control loop. Cannot grant permissions programmatically,
but can detect missing permissions and guide the user.

Architecture: NanoApex/MoIE on Mac Mini M1
Author: Vy Logic Injection Blueprint
Date: 2025-12-06
"""

import subprocess
import sys
import mss
import numpy as np
from typing import Tuple, Dict
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('VySafetyLayer')


class SafetyLayer:
    """
    Implements forensic verification of macOS TCC permissions.
    
    The Safety Layer performs "Loopback Tests" to empirically verify that:
    1. Accessibility permissions allow cliclick to control the mouse
    2. Screen Recording permissions allow MSS to capture the screen
    
    This is necessary because:
    - TCC database cannot be queried reliably without Full Disk Access
    - Permissions can be revoked at any time by the user or OS updates
    - Silent failures are common (black screenshots, ignored clicks)
    """
    
    def __init__(self, cliclick_path: str = '/opt/homebrew/bin/cliclick'):
        """Initialize the safety layer.
        
        Args:
            cliclick_path: Path to cliclick binary
        """
        self.cliclick_path = cliclick_path
        self.accessibility_verified = False
        self.screen_recording_verified = False
        
        logger.info("Initialized Vy Safety Layer")
    
    def verify_all(self) -> Tuple[bool, Dict[str, str]]:
        """
        Run all safety verifications.
        
        Returns:
            Tuple of (all_passed, results_dict)
        """
        results = {}
        
        # Check if cliclick exists
        cliclick_exists = self._check_cliclick_exists()
        results['cliclick_exists'] = 'PASS' if cliclick_exists else 'FAIL'
        
        if not cliclick_exists:
            logger.error(f"cliclick not found at {self.cliclick_path}")
            results['accessibility'] = 'SKIP'
            results['screen_recording'] = 'SKIP'
            return False, results
        
        # Run Accessibility Loopback Test
        accessibility_pass = self.verify_accessibility()
        results['accessibility'] = 'PASS' if accessibility_pass else 'FAIL'
        
        # Run Screen Recording Verification
        screen_recording_pass = self.verify_screen_recording()
        results['screen_recording'] = 'PASS' if screen_recording_pass else 'FAIL'
        
        all_passed = cliclick_exists and accessibility_pass and screen_recording_pass
        
        return all_passed, results
    
    def _check_cliclick_exists(self) -> bool:
        """Check if cliclick binary exists."""
        try:
            result = subprocess.run(
                [self.cliclick_path, '-V'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"cliclick found: {result.stdout.strip()}")
                return True
            else:
                logger.error(f"cliclick returned error: {result.stderr}")
                return False
        except FileNotFoundError:
            logger.error(f"cliclick not found at {self.cliclick_path}")
            return False
        except Exception as e:
            logger.error(f"Error checking cliclick: {e}")
            return False
    
    def verify_accessibility(self) -> bool:
        """
        Accessibility Loopback Test.
        
        Protocol:
        1. Query current mouse position (x0, y0)
        2. Attempt minimal move (+1 pixel in X)
        3. Query new position (x1, y1)
        4. Verify x1 = x0 + 1
        
        If the position doesn't change, TCC is blocking the event injection.
        
        Returns:
            True if accessibility is granted, False otherwise
        """
        logger.info("Running Accessibility Loopback Test...")
        
        try:
            # Step 1: Get initial position
            result = subprocess.run(
                [self.cliclick_path, 'p'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to query mouse position: {result.stderr}")
                return False
            
            # Parse position (format: "x,y")
            pos_str = result.stdout.strip()
            x0, y0 = map(int, pos_str.split(','))
            logger.info(f"Initial mouse position: ({x0}, {y0})")
            
            # Step 2: Attempt minimal move (+1 pixel)
            # Use relative move to avoid going off-screen
            move_cmd = f"m:+1,+0"
            result = subprocess.run(
                [self.cliclick_path, move_cmd],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to move mouse: {result.stderr}")
                return False
            
            # Small delay to ensure the move is processed
            time.sleep(0.1)
            
            # Step 3: Get new position
            result = subprocess.run(
                [self.cliclick_path, 'p'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to query mouse position after move: {result.stderr}")
                return False
            
            pos_str = result.stdout.strip()
            x1, y1 = map(int, pos_str.split(','))
            logger.info(f"New mouse position: ({x1}, {y1})")
            
            # Step 4: Verify the move succeeded
            if x1 == x0 + 1 and y1 == y0:
                logger.info("✅ Accessibility Loopback Test: PASS")
                logger.info("   Mouse moved successfully - Accessibility permission granted")
                self.accessibility_verified = True
                
                # Move back to original position
                subprocess.run(
                    [self.cliclick_path, f"m:{x0},{y0}"],
                    capture_output=True,
                    timeout=5
                )
                
                return True
            else:
                logger.error("❌ Accessibility Loopback Test: FAIL")
                logger.error(f"   Expected position: ({x0+1}, {y0})")
                logger.error(f"   Actual position: ({x1}, {y1})")
                logger.error("   TCC is blocking event injection")
                self._print_accessibility_fix()
                return False
                
        except Exception as e:
            logger.error(f"Accessibility test failed with exception: {e}")
            return False
    
    def verify_screen_recording(self) -> bool:
        """
        Screen Recording Verification Test.
        
        Protocol:
        1. Capture 10x10 pixel sample from screen center
        2. Calculate standard deviation of pixel colors
        3. Detect "black rectangle" or solid color substitution
        
        If std dev is 0 or very low, TCC is likely blocking the capture.
        
        Returns:
            True if screen recording is granted, False otherwise
        """
        logger.info("Running Screen Recording Verification Test...")
        
        try:
            with mss.mss() as sct:
                # Get main monitor
                monitor = sct.monitors[1]
                
                # Calculate center region (10x10 pixels)
                center_x = monitor['left'] + monitor['width'] // 2
                center_y = monitor['top'] + monitor['height'] // 2
                
                # Define capture region (logical coordinates)
                region = {
                    'left': center_x - 5,
                    'top': center_y - 5,
                    'width': 10,
                    'height': 10
                }
                
                logger.info(f"Capturing 10x10 sample from center: ({center_x}, {center_y})")
                
                # Capture the region
                screenshot = sct.grab(region)
                
                # Convert to numpy array
                img = np.array(screenshot)
                
                logger.info(f"Captured image shape: {img.shape}")
                logger.info(f"Captured image dtype: {img.dtype}")
                
                # Calculate statistics
                mean_color = np.mean(img)
                std_dev = np.std(img)
                
                logger.info(f"Image mean: {mean_color:.2f}")
                logger.info(f"Image std dev: {std_dev:.2f}")
                
                # Check for suspicious patterns
                # Pure black: mean ~0, std ~0
                # Pure white: mean ~255, std ~0
                # Solid color: std ~0
                
                if std_dev < 1.0:
                    logger.error("❌ Screen Recording Verification: FAIL")
                    logger.error(f"   Captured image has very low variance (std={std_dev:.2f})")
                    logger.error("   This indicates TCC is blocking screen capture")
                    logger.error("   macOS is substituting a solid color instead of actual content")
                    self._print_screen_recording_fix()
                    return False
                else:
                    logger.info("✅ Screen Recording Verification: PASS")
                    logger.info(f"   Captured image has normal variance (std={std_dev:.2f})")
                    logger.info("   Screen Recording permission granted")
                    self.screen_recording_verified = True
                    return True
                    
        except Exception as e:
            logger.error(f"Screen recording test failed with exception: {e}")
            return False
    
    def _print_accessibility_fix(self):
        """Print instructions for fixing Accessibility permissions."""
        print("\n" + "="*70)
        print("⚠️  ACCESSIBILITY PERMISSION REQUIRED")
        print("="*70)
        print("\nVy requires Accessibility permission to control the mouse and keyboard.")
        print("\nTo grant permission:")
        print("1. Open System Settings (System Preferences on older macOS)")
        print("2. Go to: Privacy & Security > Accessibility")
        print("3. Click the lock icon and authenticate")
        print("4. Find 'Terminal' (or your terminal app) in the list")
        print("5. Toggle it ON")
        print("6. Restart this script")
        print("\nDirect link (may not work on all macOS versions):")
        print("x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility")
        print("="*70 + "\n")
    
    def _print_screen_recording_fix(self):
        """Print instructions for fixing Screen Recording permissions."""
        print("\n" + "="*70)
        print("⚠️  SCREEN RECORDING PERMISSION REQUIRED")
        print("="*70)
        print("\nVy requires Screen Recording permission to capture the screen.")
        print("\nTo grant permission:")
        print("1. Open System Settings (System Preferences on older macOS)")
        print("2. Go to: Privacy & Security > Screen Recording")
        print("3. Click the lock icon and authenticate")
        print("4. Find 'Terminal' (or your terminal app) in the list")
        print("5. Toggle it ON")
        print("6. You may need to quit and restart Terminal completely")
        print("7. Restart this script")
        print("\nDirect link (may not work on all macOS versions):")
        print("x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture")
        print("="*70 + "\n")
    
    def print_status_report(self, results: Dict[str, str]):
        """Print a formatted status report."""
        print("\n" + "="*70)
        print("Vy Safety Layer - Status Report")
        print("="*70)
        
        for check, status in results.items():
            icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏭️"
            print(f"{icon} {check.replace('_', ' ').title()}: {status}")
        
        print("="*70 + "\n")


def main():
    """Test the safety layer."""
    print("=" * 70)
    print("Vy Safety Layer - TCC Verification Test")
    print("=" * 70)
    
    safety = SafetyLayer()
    
    print("\nRunning all safety checks...\n")
    all_passed, results = safety.verify_all()
    
    safety.print_status_report(results)
    
    if all_passed:
        print("✅ All safety checks passed! Vy is ready to operate.\n")
        return 0
    else:
        print("❌ Some safety checks failed. Please fix the issues above.\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
