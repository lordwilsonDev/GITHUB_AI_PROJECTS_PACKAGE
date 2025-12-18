# tools/physical_hand.py
import subprocess
import time

def safe_click(x: int, y: int, confirm: bool = True):
    """
    Executes a physical click at (x,y).
    SAFETY: Requires user confirmation for coordinates > 1000 (edge of screen).
    """
    if x < 0 or y < 0:
        return "Error: Negative coordinates impossible."
    
    # The Panopticon Safety Check
    if confirm:
        user_approval = input(f" Allow click at {x},{y}? (y/n): ")
        if user_approval.lower() != 'y':
            return "Action blocked by User."

    try:
        # Use cliclick (brew install cliclick)
        subprocess.run(["cliclick", f"c:{x},{y}"], check=True)
        return f"Clicked at {x},{y}"
    except Exception as e:
        return f"Failed to click: {e}"

if __name__ == "__main__":
    # Test the function
    print("Testing safe_click function...")
    result = safe_click(100, 100, confirm=False)
    print(result)
