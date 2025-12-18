# tools/keyboard_tools.py
import subprocess

def safe_type(text: str, confirm: bool = True):
    """
    Types text using cliclick.
    SAFETY: Requires user confirmation before typing.
    Args:
        text: The text to type
        confirm: Whether to ask for user confirmation
    Returns:
        Status message
    """
    if confirm:
        user_approval = input(f" Allow typing '{text}'? (y/n): ")
        if user_approval.lower() != 'y':
            return "Action blocked by User."
    
    try:
        # Use cliclick to type text
        subprocess.run(["cliclick", f"t:{text}"], check=True)
        return f"Typed: {text}"
    except Exception as e:
        return f"Failed to type: {e}"

def safe_key_press(key: str, confirm: bool = True):
    """
    Presses a special key using cliclick.
    SAFETY: Requires user confirmation before key press.
    Args:
        key: The key to press (e.g., 'return', 'tab', 'esc')
        confirm: Whether to ask for user confirmation
    Returns:
        Status message
    """
    if confirm:
        user_approval = input(f" Allow pressing key '{key}'? (y/n): ")
        if user_approval.lower() != 'y':
            return "Action blocked by User."
    
    try:
        # Use cliclick to press key
        subprocess.run(["cliclick", f"kp:{key}"], check=True)
        return f"Pressed key: {key}"
    except Exception as e:
        return f"Failed to press key: {e}"

def safe_key_combo(keys: str, confirm: bool = True):
    """
    Presses a key combination using cliclick.
    SAFETY: Requires user confirmation before key combo.
    Args:
        keys: The key combination (e.g., 'cmd+c', 'cmd+v', 'cmd+shift+4')
        confirm: Whether to ask for user confirmation
    Returns:
        Status message
    """
    if confirm:
        user_approval = input(f" Allow key combination '{keys}'? (y/n): ")
        if user_approval.lower() != 'y':
            return "Action blocked by User."
    
    try:
        # Use cliclick to press key combination
        subprocess.run(["cliclick", f"kp:{keys}"], check=True)
        return f"Pressed key combo: {keys}"
    except Exception as e:
        return f"Failed to press key combo: {e}"

if __name__ == "__main__":
    print("Keyboard Tools for Level 33")
    print("="*50)
    
    # Test typing (with confirmation disabled for testing)
    print("\nTest 1: Typing text")
    result = safe_type("Hello, Level 33!", confirm=False)
    print(result)
    
    print("\nTest 2: Key press")
    result = safe_key_press("return", confirm=False)
    print(result)
    
    print("\nTest 3: Key combination")
    result = safe_key_combo("cmd+c", confirm=False)
    print(result)
    
    print("\nNote: All tests run with confirm=False for automation.")
    print("In production, confirm=True is the default for safety.")
