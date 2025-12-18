#!/usr/bin/env python3
"""
Interactive Setup Wizard for Level 33 Sovereign Architecture

Guides users through initial system configuration.
"""

import os
import sys
import subprocess
from pathlib import Path
import yaml


class Colors:
    """ANSI color codes."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print colored header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.RESET}\n")


def print_step(step: int, total: int, text: str):
    """Print step indicator."""
    print(f"{Colors.CYAN}[Step {step}/{total}]{Colors.RESET} {Colors.BOLD}{text}{Colors.RESET}")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓{Colors.RESET} {text}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}✗{Colors.RESET} {text}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {text}")


def ask_yes_no(question: str, default: bool = True) -> bool:
    """Ask yes/no question."""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{question} [{default_str}]: ").strip().lower()
    
    if not response:
        return default
    
    return response in ('y', 'yes')


def ask_choice(question: str, choices: list, default: int = 0) -> str:
    """Ask multiple choice question."""
    print(f"\n{question}")
    for i, choice in enumerate(choices, 1):
        marker = "*" if i-1 == default else " "
        print(f"  {marker} {i}. {choice}")
    
    while True:
        response = input(f"\nChoice [1-{len(choices)}] (default: {default+1}): ").strip()
        
        if not response:
            return choices[default]
        
        try:
            idx = int(response) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except ValueError:
            pass
        
        print_error("Invalid choice. Please try again.")


def check_command(command: str) -> bool:
    """Check if command exists."""
    try:
        subprocess.run(["which", command], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def run_command(command: str, description: str) -> bool:
    """Run shell command with feedback."""
    print(f"  Running: {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print_success(f"{description} completed")
            return True
        else:
            print_error(f"{description} failed: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"{description} failed: {e}")
        return False


def check_dependencies():
    """Check system dependencies."""
    print_step(1, 6, "Checking Dependencies")
    
    dependencies = {
        'ollama': 'Ollama (LLM runtime)',
        'python3': 'Python 3',
        'pip3': 'pip (Python package manager)',
        'cliclick': 'cliclick (mouse/keyboard control)'
    }
    
    missing = []
    
    for cmd, desc in dependencies.items():
        if check_command(cmd):
            print_success(f"{desc} found")
        else:
            print_error(f"{desc} not found")
            missing.append((cmd, desc))
    
    if missing:
        print_warning("\nMissing dependencies detected!")
        print("\nInstallation instructions:")
        
        for cmd, desc in missing:
            if cmd == 'ollama':
                print(f"  • {desc}: Visit https://ollama.com")
            elif cmd == 'cliclick':
                print(f"  • {desc}: Run 'brew install cliclick'")
            elif cmd in ('python3', 'pip3'):
                print(f"  • {desc}: Visit https://python.org")
        
        if not ask_yes_no("\nContinue anyway?", default=False):
            sys.exit(1)
    
    return True


def install_python_packages():
    """Install Python packages."""
    print_step(2, 6, "Installing Python Packages")
    
    packages = [
        'pyautogen',
        'dspy-ai',
        'pyyaml',
        'fastapi',
        'uvicorn',
        'pillow',
        'requests'
    ]
    
    if ask_yes_no("Install Python packages?", default=True):
        for package in packages:
            run_command(f"pip3 install {package}", f"Installing {package}")
    else:
        print_warning("Skipped Python package installation")


def setup_ollama():
    """Setup Ollama and download model."""
    print_step(3, 6, "Setting Up Ollama")
    
    if not check_command('ollama'):
        print_warning("Ollama not found. Skipping.")
        return
    
    # Check if Ollama is running
    try:
        result = subprocess.run(
            ['curl', '-s', 'http://localhost:11434/api/tags'],
            capture_output=True,
            timeout=2
        )
        if result.returncode != 0:
            print_warning("Ollama is not running. Please start it with: ollama serve")
            return
    except:
        print_warning("Could not connect to Ollama")
        return
    
    print_success("Ollama is running")
    
    # Download Gemma 2 9B model
    if ask_yes_no("Download Gemma 2 9B model? (~6GB)", default=True):
        run_command("ollama pull gemma2:9b", "Downloading Gemma 2 9B")


def configure_system():
    """Configure system settings."""
    print_step(4, 6, "System Configuration")
    
    config_path = Path("config.yaml")
    
    if config_path.exists():
        if not ask_yes_no("Config file exists. Reconfigure?", default=False):
            print_warning("Skipped configuration")
            return
    
    print("\nConfiguring system settings...\n")
    
    # Safety mode
    safety_mode = ask_yes_no("Enable safety mode (require confirmation for actions)?", default=True)
    
    # Log level
    log_level = ask_choice(
        "Select log level:",
        ["DEBUG", "INFO", "WARNING", "ERROR"],
        default=1
    )
    
    # Environment
    environment = ask_choice(
        "Select environment:",
        ["development", "staging", "production"],
        default=2
    )
    
    print_success("Configuration complete")
    print(f"  • Safety mode: {safety_mode}")
    print(f"  • Log level: {log_level}")
    print(f"  • Environment: {environment}")


def create_directories():
    """Create necessary directories."""
    print_step(5, 6, "Creating Directories")
    
    directories = [
        'logs',
        'data',
        'workspace',
        'quick_notes',
        'documentation',
        'screenshots',
        'reports',
        'backups',
        'metrics',
        'plugins'
    ]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print_success(f"Created {directory}/")
        else:
            print(f"  {directory}/ already exists")


def run_tests():
    """Run system tests."""
    print_step(6, 6, "Running Tests")
    
    if ask_yes_no("Run system tests?", default=True):
        tests = [
            ('python3 core/config_manager.py', 'Configuration manager'),
            ('python3 core/logger.py', 'Logging system'),
            ('python3 tools/physical_hand.py', 'Physical hand tool')
        ]
        
        for command, description in tests:
            run_command(command, f"Testing {description}")
    else:
        print_warning("Skipped tests")


def show_next_steps():
    """Show next steps to user."""
    print_header("Setup Complete!")
    
    print(f"{Colors.GREEN}✓ Level 33 Sovereign Architecture is ready!{Colors.RESET}\n")
    
    print(f"{Colors.BOLD}Next Steps:{Colors.RESET}\n")
    print("1. Review configuration:")
    print(f"   {Colors.CYAN}cat config.yaml{Colors.RESET}\n")
    
    print("2. Try the automations:")
    print(f"   {Colors.CYAN}make automations{Colors.RESET}")
    print(f"   {Colors.CYAN}make workspace{Colors.RESET}")
    print(f"   {Colors.CYAN}make health{Colors.RESET}\n")
    
    print("3. Read the documentation:")
    print(f"   {Colors.CYAN}cat COMPLETE_PROJECT_SUMMARY.md{Colors.RESET}")
    print(f"   {Colors.CYAN}cat USAGE_GUIDE.md{Colors.RESET}\n")
    
    print("4. Test the AI agents:")
    print(f"   {Colors.CYAN}make ai-email{Colors.RESET}")
    print(f"   {Colors.CYAN}make ai-files{Colors.RESET}\n")
    
    print(f"{Colors.BOLD}Documentation:{Colors.RESET}")
    print(f"  • Quick Start: {Colors.CYAN}QUICK_START.md{Colors.RESET}")
    print(f"  • Complete Guide: {Colors.CYAN}COMPLETE_SETUP.md{Colors.RESET}")
    print(f"  • Usage Guide: {Colors.CYAN}USAGE_GUIDE.md{Colors.RESET}")
    print(f"  • Automations: {Colors.CYAN}automations/README.md{Colors.RESET}\n")
    
    print(f"{Colors.BOLD}Support:{Colors.RESET}")
    print(f"  • Issues: Check {Colors.CYAN}REMAINING_ISSUES.md{Colors.RESET}")
    print(f"  • Logs: {Colors.CYAN}logs/level33.log{Colors.RESET}\n")


def main():
    """Run setup wizard."""
    print_header("Level 33 Sovereign Architecture Setup Wizard")
    
    print(f"{Colors.BOLD}Welcome!{Colors.RESET}")
    print("This wizard will guide you through setting up the Level 33 system.\n")
    
    if not ask_yes_no("Continue with setup?", default=True):
        print("Setup cancelled.")
        sys.exit(0)
    
    try:
        # Run setup steps
        check_dependencies()
        install_python_packages()
        setup_ollama()
        configure_system()
        create_directories()
        run_tests()
        
        # Show completion
        show_next_steps()
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup interrupted by user.{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
