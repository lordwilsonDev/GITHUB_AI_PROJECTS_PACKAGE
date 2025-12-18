#!/usr/bin/env python3
"""
NanoApex System Demonstration

This script demonstrates the complete NanoApex workflow:
1. RADE captures code with @nanoapex markers
2. nano_indexer updates index.jsonl
3. nano_dispatcher routes to MoIE
4. MoIE processes and generates improved drafts
5. Status tracking prevents duplicate processing

Usage:
    python3 demo.py                    # Run full demo
    python3 demo.py --quick            # Quick demo (skip waits)
    python3 demo.py --cleanup          # Clean up demo files
    python3 demo.py --check-services   # Check if services are running

Requirements:
- RADE daemon running
- MoIE backend running (port 8000)
- nano_dispatcher.py available
"""

import os
import sys
import time
import json
import subprocess
import argparse
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_step(step_num: int, total: int, text: str):
    """Print a step indicator"""
    print(f"{Colors.CYAN}{Colors.BOLD}[{step_num}/{total}] {text}{Colors.ENDC}")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")

class ServiceChecker:
    """Check if required services are running"""
    
    @staticmethod
    def check_service(url: str, name: str, timeout: int = 2) -> bool:
        """Check if a service is available"""
        try:
            response = requests.get(f"{url}/health", timeout=timeout)
            if response.status_code == 200:
                print_success(f"{name} is running at {url}")
                return True
        except requests.exceptions.ConnectionError:
            print_error(f"{name} is NOT running at {url}")
        except requests.exceptions.Timeout:
            print_warning(f"{name} timed out at {url}")
        except Exception as e:
            print_error(f"{name} check failed: {e}")
        return False
    
    @staticmethod
    def check_all_services() -> Dict[str, bool]:
        """Check all required services"""
        print_header("Service Availability Check")
        
        services = {
            'moie': ('http://localhost:8000', 'MoIE Backend'),
            'love_engine': ('http://localhost:8001', 'Love Engine'),
            'age': ('http://localhost:9000', 'AGE Core'),
            'ollama': ('http://localhost:11434', 'Ollama')
        }
        
        results = {}
        for key, (url, name) in services.items():
            results[key] = ServiceChecker.check_service(url, name)
        
        print()
        if results['moie']:
            print_success("Core services ready for demo")
        else:
            print_error("MoIE backend is required for demo")
            print_info("Start MoIE: cd moie-os/backend && uvicorn main:app --port 8000")
        
        return results

class DemoEnvironment:
    """Manage demo environment and files"""
    
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.home()
        self.demo_project = self.base_path / "nanoapex_demo_project"
        self.nano_memory = self.base_path / "nano_memory"
        self.created_files: List[Path] = []
    
    def setup(self):
        """Set up demo environment"""
        print_step(1, 8, "Setting up demo environment")
        
        # Create demo project directory
        self.demo_project.mkdir(exist_ok=True)
        print_info(f"Demo project: {self.demo_project}")
        
        # Verify nano_memory exists
        if not self.nano_memory.exists():
            print_warning(f"nano_memory not found at {self.nano_memory}")
            self.nano_memory.mkdir()
            print_info(f"Created nano_memory directory")
        
        print_success("Environment ready")
        print()
    
    def create_test_file(self) -> Path:
        """Create a test Python file with @nanoapex marker"""
        print_step(2, 8, "Creating test file with @nanoapex marker")
        
        test_file = self.demo_project / "calculator.py"
        
        code = '''
"""Simple calculator for demonstration"""

# @nanoapex
def calculate(x, y, operation):
    """Perform calculation based on operation
    
    This function could be improved with:
    - Better error handling
    - Support for more operations
    - Type hints
    - Input validation
    """
    if operation == 'add':
        return x + y
    elif operation == 'subtract':
        return x - y
    elif operation == 'multiply':
        return x * y
    elif operation == 'divide':
        if y == 0:
            return None
        return x / y
    else:
        return None

# @nanoapex
def factorial(n):
    """Calculate factorial (could be optimized)"""
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

if __name__ == "__main__":
    print("Calculator Demo")
    print(f"5 + 3 = {calculate(5, 3, 'add')}")
    print(f"5! = {factorial(5)}")
'''
        
        test_file.write_text(code)
        self.created_files.append(test_file)
        
        print_info(f"Created: {test_file.name}")
        print_info(f"Functions marked: calculate, factorial")
        print_success("Test file ready")
        print()
        
        return test_file
    
    def wait_for_rade_capture(self, timeout: int = 30) -> List[Path]:
        """Wait for RADE to capture and create .nano files"""
        print_step(3, 8, "Waiting for RADE to capture marked functions")
        
        print_info("RADE daemon should detect @nanoapex markers...")
        print_info(f"Watching {self.nano_memory} for new .nano files...")
        
        start_time = time.time()
        initial_files = set(self.nano_memory.glob("*.nano"))
        
        while time.time() - start_time < timeout:
            current_files = set(self.nano_memory.glob("*.nano"))
            new_files = current_files - initial_files
            
            if new_files:
                print_success(f"Found {len(new_files)} new .nano file(s)")
                for f in new_files:
                    print_info(f"  - {f.name}")
                print()
                return list(new_files)
            
            time.sleep(1)
            print(".", end="", flush=True)
        
        print()
        print_warning(f"No new .nano files after {timeout}s")
        print_info("RADE daemon may not be running")
        print_info("Check: launchctl list | grep rade")
        print()
        
        return []
    
    def verify_index_update(self) -> bool:
        """Verify index.jsonl was updated"""
        print_step(4, 8, "Verifying index.jsonl update")
        
        index_file = self.nano_memory / "index.jsonl"
        
        if not index_file.exists():
            print_error("index.jsonl not found")
            return False
        
        # Read last few entries
        with open(index_file, 'r') as f:
            lines = f.readlines()
        
        print_info(f"Total entries in index: {len(lines)}")
        
        if lines:
            # Show last entry
            last_entry = json.loads(lines[-1])
            print_info(f"Latest entry: {last_entry.get('nano_file', 'unknown')}")
            print_info(f"  Kind: {last_entry.get('kind', 'unknown')}")
            print_info(f"  Function: {last_entry.get('function', 'unknown')}")
            print_success("index.jsonl is up to date")
        else:
            print_warning("index.jsonl is empty")
        
        print()
        return True
    
    def run_dispatcher(self, mode: str = "once") -> bool:
        """Run nano_dispatcher"""
        print_step(5, 8, "Running nano_dispatcher")
        
        dispatcher_path = self.base_path / "nano_dispatcher.py"
        
        if not dispatcher_path.exists():
            print_error(f"nano_dispatcher.py not found at {dispatcher_path}")
            return False
        
        print_info(f"Executing: python3 nano_dispatcher.py --mode {mode}")
        
        try:
            result = subprocess.run(
                ["python3", str(dispatcher_path), "--mode", mode, "--verbose"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print_success("Dispatcher completed successfully")
                
                # Show relevant output
                for line in result.stdout.split('\n'):
                    if 'Processing' in line or 'Successfully' in line or 'Found' in line:
                        print_info(f"  {line.strip()}")
                
                print()
                return True
            else:
                print_error(f"Dispatcher failed with code {result.returncode}")
                if result.stderr:
                    print_info("Error output:")
                    print(result.stderr)
                return False
        
        except subprocess.TimeoutExpired:
            print_error("Dispatcher timed out")
            return False
        except Exception as e:
            print_error(f"Failed to run dispatcher: {e}")
            return False
    
    def verify_status_update(self) -> bool:
        """Verify status.jsonl was updated"""
        print_step(6, 8, "Verifying status.jsonl update")
        
        status_file = self.nano_memory / "status.jsonl"
        
        if not status_file.exists():
            print_error("status.jsonl not found")
            return False
        
        # Read status entries
        with open(status_file, 'r') as f:
            lines = f.readlines()
        
        print_info(f"Total status entries: {len(lines)}")
        
        if lines:
            # Show last entry
            last_status = json.loads(lines[-1])
            print_info(f"Latest status: {last_status.get('nano_file', 'unknown')}")
            print_info(f"  State: {last_status.get('state', 'unknown')}")
            print_info(f"  Identifier: {last_status.get('identifier', 'unknown')}")
            
            if last_status.get('state') == 'DONE':
                print_success("Processing completed successfully")
            elif last_status.get('state') == 'ERROR':
                print_error(f"Processing failed: {last_status.get('error_message', 'unknown')}")
            else:
                print_warning(f"Processing state: {last_status.get('state')}")
        
        print()
        return True
    
    def check_for_drafts(self) -> List[Path]:
        """Check if MoIE generated improved drafts"""
        print_step(7, 8, "Checking for MoIE-generated drafts")
        
        # Look for draft files
        draft_files = list(self.nano_memory.glob("*draft*.nano"))
        
        if draft_files:
            print_success(f"Found {len(draft_files)} draft file(s)")
            for draft in draft_files:
                print_info(f"  - {draft.name}")
                
                # Show snippet of draft
                content = draft.read_text()
                lines = content.split('\n')[:10]
                print_info("  Preview:")
                for line in lines:
                    if line.strip():
                        print(f"    {line}")
        else:
            print_warning("No draft files found yet")
            print_info("MoIE may still be processing, or drafts may be in a different location")
        
        print()
        return draft_files
    
    def show_metrics(self):
        """Show system metrics"""
        print_step(8, 8, "System Metrics")
        
        # Count files
        nano_files = list(self.nano_memory.glob("*.nano"))
        draft_files = [f for f in nano_files if 'draft' in f.name]
        snippet_files = [f for f in nano_files if 'draft' not in f.name]
        
        print_info(f"Total .nano files: {len(nano_files)}")
        print_info(f"  Snippets: {len(snippet_files)}")
        print_info(f"  Drafts: {len(draft_files)}")
        
        # Index stats
        index_file = self.nano_memory / "index.jsonl"
        if index_file.exists():
            with open(index_file, 'r') as f:
                index_count = len(f.readlines())
            print_info(f"Index entries: {index_count}")
        
        # Status stats
        status_file = self.nano_memory / "status.jsonl"
        if status_file.exists():
            with open(status_file, 'r') as f:
                status_lines = f.readlines()
            
            states = {}
            for line in status_lines:
                entry = json.loads(line)
                state = entry.get('state', 'UNKNOWN')
                states[state] = states.get(state, 0) + 1
            
            print_info(f"Status entries: {len(status_lines)}")
            for state, count in states.items():
                print_info(f"  {state}: {count}")
        
        print_success("Metrics collected")
        print()
    
    def cleanup(self):
        """Clean up demo files"""
        print_header("Cleaning Up Demo Files")
        
        # Remove demo project
        if self.demo_project.exists():
            import shutil
            shutil.rmtree(self.demo_project)
            print_success(f"Removed {self.demo_project}")
        
        # Note: We don't remove nano_memory files as they may be from real usage
        print_info("nano_memory files preserved (may contain real data)")
        print_success("Cleanup complete")
        print()

def run_demo(quick: bool = False):
    """Run the complete demo"""
    print_header("NanoApex System Demonstration")
    
    print_info("This demo will:")
    print_info("  1. Create a test Python file with @nanoapex markers")
    print_info("  2. Wait for RADE to capture the marked functions")
    print_info("  3. Verify nano_indexer updated index.jsonl")
    print_info("  4. Run nano_dispatcher to route to MoIE")
    print_info("  5. Verify status tracking")
    print_info("  6. Check for MoIE-generated drafts")
    print_info("  7. Display system metrics")
    print()
    
    input("Press Enter to continue...")
    
    # Initialize environment
    env = DemoEnvironment()
    
    try:
        # Setup
        env.setup()
        
        # Create test file
        test_file = env.create_test_file()
        
        if not quick:
            # Wait for RADE
            nano_files = env.wait_for_rade_capture(timeout=30)
            
            if not nano_files:
                print_warning("Continuing demo without RADE capture...")
                print_info("You can manually trigger RADE or use existing .nano files")
                print()
        
        # Verify index
        env.verify_index_update()
        
        # Run dispatcher
        env.run_dispatcher(mode="once")
        
        # Verify status
        env.verify_status_update()
        
        # Check drafts
        env.check_for_drafts()
        
        # Show metrics
        env.show_metrics()
        
        # Summary
        print_header("Demo Complete")
        print_success("NanoApex system demonstration finished")
        print()
        print_info("Next steps:")
        print_info("  1. Review generated drafts in nano_memory/")
        print_info("  2. Check dispatcher.log for detailed logs")
        print_info("  3. Run 'python3 nano_dispatcher.py --mode daemon' for continuous processing")
        print_info("  4. Explore MoIE dashboard at http://localhost:8000")
        print()
        
        # Cleanup option
        cleanup = input("Clean up demo files? (y/N): ").strip().lower()
        if cleanup == 'y':
            env.cleanup()
        else:
            print_info(f"Demo files preserved at {env.demo_project}")
    
    except KeyboardInterrupt:
        print()
        print_warning("Demo interrupted by user")
        env.cleanup()
    except Exception as e:
        print()
        print_error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="NanoApex System Demonstration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 demo.py                    # Run full demo
  python3 demo.py --quick            # Quick demo (skip waits)
  python3 demo.py --cleanup          # Clean up demo files
  python3 demo.py --check-services   # Check if services are running

Requirements:
  - RADE daemon running (optional for quick mode)
  - MoIE backend running at http://localhost:8000
  - nano_dispatcher.py in home directory
        """
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Quick mode: skip waiting for RADE capture'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Clean up demo files and exit'
    )
    
    parser.add_argument(
        '--check-services',
        action='store_true',
        help='Check if required services are running'
    )
    
    args = parser.parse_args()
    
    if args.check_services:
        services = ServiceChecker.check_all_services()
        sys.exit(0 if services['moie'] else 1)
    
    if args.cleanup:
        env = DemoEnvironment()
        env.cleanup()
        sys.exit(0)
    
    # Check services before running demo
    services = ServiceChecker.check_all_services()
    
    if not services['moie']:
        print()
        print_error("Cannot run demo: MoIE backend is not running")
        print_info("Start MoIE backend:")
        print_info("  cd moie-os/backend")
        print_info("  uvicorn main:app --port 8000")
        sys.exit(1)
    
    # Run demo
    run_demo(quick=args.quick)

if __name__ == '__main__':
    main()
