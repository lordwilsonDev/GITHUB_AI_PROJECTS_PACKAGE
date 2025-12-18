# tools/screen_tools.py
import subprocess
import os
from datetime import datetime

def get_screen_resolution():
    """
    Get the current screen resolution.
    Returns: tuple (width, height)
    """
    try:
        # Use system_profiler to get display info
        result = subprocess.run(
            ['system_profiler', 'SPDisplaysDataType'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse resolution from output
        for line in result.stdout.split('\n'):
            if 'Resolution' in line:
                # Extract numbers from line like "Resolution: 1920 x 1080"
                parts = line.split(':')
                if len(parts) > 1:
                    res_parts = parts[1].strip().split('x')
                    if len(res_parts) == 2:
                        width = int(res_parts[0].strip())
                        height = int(res_parts[1].strip())
                        return (width, height)
        
        # Default fallback
        return (1920, 1080)
    except Exception as e:
        print(f"Warning: Could not detect screen resolution: {e}")
        return (1920, 1080)

def capture_screen(filename=None):
    """
    Capture a screenshot of the current screen.
    Args:
        filename: Optional custom filename. If None, generates timestamp-based name.
    Returns:
        Path to the saved screenshot
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
    
    # Ensure screenshots directory exists
    screenshots_dir = os.path.expanduser("~/level33_sovereign/workspace/screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    
    filepath = os.path.join(screenshots_dir, filename)
    
    try:
        # Use screencapture command
        subprocess.run(['screencapture', filepath], check=True)
        return filepath
    except Exception as e:
        return f"Error capturing screen: {e}"

def validate_coordinates(x, y):
    """
    Validate that coordinates are within screen bounds.
    Args:
        x: X coordinate
        y: Y coordinate
    Returns:
        tuple: (is_valid, message)
    """
    if x < 0 or y < 0:
        return (False, "Coordinates cannot be negative")
    
    width, height = get_screen_resolution()
    
    if x > width:
        return (False, f"X coordinate {x} exceeds screen width {width}")
    
    if y > height:
        return (False, f"Y coordinate {y} exceeds screen height {height}")
    
    return (True, "Coordinates valid")

if __name__ == "__main__":
    print("Screen Tools for Level 33")
    print("="*50)
    
    # Test screen resolution
    width, height = get_screen_resolution()
    print(f"Screen Resolution: {width}x{height}")
    
    # Test coordinate validation
    test_coords = [(100, 100), (2000, 2000), (-10, 50), (500, 3000)]
    for x, y in test_coords:
        is_valid, message = validate_coordinates(x, y)
        status = "✓" if is_valid else "✗"
        print(f"{status} ({x}, {y}): {message}")
    
    # Test screenshot (commented out to avoid cluttering)
    # print("\nCapturing screenshot...")
    # filepath = capture_screen()
    # print(f"Screenshot saved to: {filepath}")
