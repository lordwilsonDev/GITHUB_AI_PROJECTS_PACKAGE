#!/usr/bin/env python3
# demo_agent.py - Interactive demo of Level 33 Sovereign Architecture

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from architecture.brain_core import solver, user_proxy
from tools.screen_tools import get_screen_resolution, validate_coordinates

def print_banner():
    print("\n" + "="*60)
    print("  🦁 LEVEL 33 SOVEREIGN ARCHITECTURE - DEMO")
    print("="*60)
    print("\nThis demo showcases the self-healing Ouroboros Loop:")
    print("  1. PLAN   - Agent analyzes the task")
    print("  2. ACT    - Agent executes physical actions")
    print("  3. REFLECT - Agent checks success/failure")
    print("  4. OPTIMIZE - DSPy corrects the plan")
    print("\n" + "="*60 + "\n")

def print_system_info():
    print("System Information:")
    print("-" * 60)
    
    # Screen resolution
    width, height = get_screen_resolution()
    print(f"  Screen Resolution: {width}x{height}")
    
    # Model info
    print(f"  AI Model: Gemma 2 9B (via Ollama)")
    print(f"  Endpoint: http://localhost:11434/v1")
    
    # Safety settings
    print(f"  Safety Mode: ALWAYS (human-in-the-loop)")
    print(f"  Max Auto-Replies: 5")
    
    print("-" * 60 + "\n")

def demo_coordinate_validation():
    print("Demo 1: Coordinate Validation")
    print("-" * 60)
    
    test_coords = [
        (100, 100, "Valid coordinates"),
        (3000, 3000, "Out of bounds - will trigger self-correction"),
        (-50, 100, "Negative coordinates - invalid"),
    ]
    
    for x, y, description in test_coords:
        is_valid, message = validate_coordinates(x, y)
        status = "✓" if is_valid else "✗"
        print(f"  {status} ({x:4d}, {y:4d}): {description}")
        print(f"      → {message}")
    
    print("-" * 60 + "\n")

def demo_simple_task():
    print("Demo 2: Simple Click Task")
    print("-" * 60)
    print("This will ask the agent to click at coordinates (100, 100).")
    print("The agent will:")
    print("  1. Validate the coordinates")
    print("  2. Ask for your confirmation")
    print("  3. Execute the click if approved")
    print("-" * 60)
    
    proceed = input("\nProceed with demo? (y/n): ")
    if proceed.lower() != 'y':
        print("Demo skipped.\n")
        return
    
    try:
        user_proxy.initiate_chat(
            solver,
            message="Click at coordinates 100, 100"
        )
    except Exception as e:
        print(f"Error during demo: {e}")
    
    print("\n" + "-" * 60 + "\n")

def demo_self_correction():
    print("Demo 3: Self-Correction (Ouroboros Loop)")
    print("-" * 60)
    print("This will ask the agent to click at invalid coordinates.")
    print("The DSPy optimizer should correct the plan automatically.")
    print("-" * 60)
    
    proceed = input("\nProceed with demo? (y/n): ")
    if proceed.lower() != 'y':
        print("Demo skipped.\n")
        return
    
    try:
        user_proxy.initiate_chat(
            solver,
            message="Click at coordinates 5000, 5000"
        )
    except Exception as e:
        print(f"Error during demo: {e}")
    
    print("\n" + "-" * 60 + "\n")

def interactive_mode():
    print("Interactive Mode")
    print("-" * 60)
    print("Enter your own task for the agent.")
    print("Examples:")
    print("  - Click at coordinates 500, 300")
    print("  - Type 'Hello World'")
    print("  - Press the return key")
    print("-" * 60)
    
    task = input("\nEnter task (or 'quit' to exit): ")
    if task.lower() == 'quit':
        return False
    
    try:
        user_proxy.initiate_chat(solver, message=task)
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "-" * 60 + "\n")
    return True

def main():
    print_banner()
    print_system_info()
    
    while True:
        print("\nAvailable Demos:")
        print("  1. Coordinate Validation")
        print("  2. Simple Click Task")
        print("  3. Self-Correction Demo")
        print("  4. Interactive Mode")
        print("  5. Exit")
        
        choice = input("\nSelect demo (1-5): ")
        
        if choice == '1':
            demo_coordinate_validation()
        elif choice == '2':
            demo_simple_task()
        elif choice == '3':
            demo_self_correction()
        elif choice == '4':
            if not interactive_mode():
                break
        elif choice == '5':
            print("\nExiting Level 33 Demo. Goodbye! 🦁\n")
            break
        else:
            print("Invalid choice. Please select 1-5.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye! 🦁\n")
        sys.exit(0)
