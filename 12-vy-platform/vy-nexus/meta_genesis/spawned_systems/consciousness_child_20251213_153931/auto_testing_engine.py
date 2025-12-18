#!/usr/bin/env python3
"""
🧪 AUTO-TESTING ENGINE 🧪
The system tests itself

PURPOSE: Code should validate code
AXIOM: "Trust but verify - recursively"
"""

import os
import sys
import subprocess
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple
import glob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
HOME = os.path.expanduser("~")
NEXUS_DIR = os.path.join(HOME, "vy-nexus")
TEST_DIR = os.path.join(NEXUS_DIR, "auto_tests")
TEST_RESULTS = os.path.join(TEST_DIR, "test_results")


class AutoTestingEngine:
    """
    Automatically tests all tools for basic functionality
    
    INVERSION: Instead of humans writing tests,
    the system tests itself
    """
    
    def __init__(self):
        """Initialize testing engine"""
        try:
            os.makedirs(TEST_DIR, exist_ok=True)
            os.makedirs(TEST_RESULTS, exist_ok=True)
            
            logger.info("🧪 Auto-Testing Engine initialized")
            
        except OSError as e:
            logger.error(f"Testing engine initialization failed: {e}")
            raise
    
    def discover_tools(self) -> List[str]:
        """Discover all executable Python tools"""
        try:
            tool_patterns = [
                os.path.join(NEXUS_DIR, "*.py"),
                os.path.join(NEXUS_DIR, "genesis", "generated_tools", "*.py")
            ]
            
            tools = []
            for pattern in tool_patterns:
                found = glob.glob(pattern)
                tools.extend([t for t in found if os.access(t, os.X_OK) or t.endswith('.py')])
            
            # Filter out __pycache__, test files, and this file
            tools = [
                t for t in tools 
                if '__pycache__' not in t 
                and 'test_' not in t
                and 'auto_testing_engine.py' not in t
            ]
            
            logger.info(f"🔍 Discovered {len(tools)} tools to test")
            return tools
            
        except Exception as e:
            logger.error(f"Tool discovery failed: {e}")
            return []
    
    def generate_basic_test(self, tool_path: str) -> str:
        """Generate a basic smoke test for a tool"""
        try:
            tool_name = os.path.basename(tool_path).replace('.py', '')
            
            test_code = f'''#!/usr/bin/env python3
"""
Auto-generated test for {tool_name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_import():
    """Test that module can be imported"""
    try:
        import {tool_name}
        print("✅ Import successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {{e}}")
        return False

def test_module_attributes():
    """Test that module has expected structure"""
    try:
        import {tool_name}
        
        # Check for main function or class
        has_main = hasattr({tool_name}, 'main')
        has_class = any(
            hasattr({tool_name}, attr) and 
            type(getattr({tool_name}, attr)).__name__ == 'type'
            for attr in dir({tool_name})
            if not attr.startswith('_')
        )
        
        if has_main or has_class:
            print("✅ Module structure valid")
            return True
        else:
            print("⚠️  No main function or class found")
            return False
            
    except Exception as e:
        print(f"❌ Structure check failed: {{e}}")
        return False

if __name__ == "__main__":
    print("="*60)
    print(f"Testing: {tool_name}")
    print("="*60)
    
    results = []
    
    print("\\n1. Import Test")
    results.append(test_import())
    
    print("\\n2. Structure Test")
    results.append(test_module_attributes())
    
    print("\\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {{passed}}/{{total}} tests passed")
    print("="*60)
    
    sys.exit(0 if all(results) else 1)
'''
            
            return test_code
            
        except Exception as e:
            logger.error(f"Test generation failed: {e}")
            return ""
    
    def save_test(self, tool_path: str, test_code: str) -> str:
        """Save generated test file"""
        try:
            tool_name = os.path.basename(tool_path).replace('.py', '')
            test_file = os.path.join(TEST_DIR, f"test_{tool_name}.py")
            
            with open(test_file, 'w') as f:
                f.write(test_code)
            
            os.chmod(test_file, 0o755)
            
            return test_file
            
        except (OSError, IOError) as e:
            logger.error(f"Test save failed: {e}")
            return ""
    
    def run_test(self, test_file: str) -> Tuple[bool, str]:
        """Execute a test file and capture results"""
        try:
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            return success, output
            
        except subprocess.TimeoutExpired:
            return False, "❌ Test timed out (30s)"
        except Exception as e:
            return False, f"❌ Test execution failed: {e}"
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Execute testing suite"""
        try:
            logger.info("🧪 Running test suite...")
            
            # Discover tools
            tools = self.discover_tools()
            
            if not tools:
                logger.warning("No tools found to test")
                return {'tests_run': 0}
            
            test_results = {
                'timestamp': datetime.now().isoformat(),
                'total_tools': len(tools),
                'tests_passed': 0,
                'tests_failed': 0,
                'results': []
            }
            
            # Generate and run tests
            for tool_path in tools:
                tool_name = os.path.basename(tool_path)
                logger.info(f"🔬 Testing: {tool_name}")
                
                # Generate test
                test_code = self.generate_basic_test(tool_path)
                
                if not test_code:
                    test_results['results'].append({
                        'tool': tool_name,
                        'status': 'SKIP',
                        'reason': 'Test generation failed'
                    })
                    continue
                
                # Save test
                test_file = self.save_test(tool_path, test_code)
                
                if not test_file:
                    test_results['results'].append({
                        'tool': tool_name,
                        'status': 'SKIP',
                        'reason': 'Test save failed'
                    })
                    continue
                
                # Run test
                success, output = self.run_test(test_file)
                
                if success:
                    test_results['tests_passed'] += 1
                    test_results['results'].append({
                        'tool': tool_name,
                        'status': 'PASS',
                        'output': output
                    })
                else:
                    test_results['tests_failed'] += 1
                    test_results['results'].append({
                        'tool': tool_name,
                        'status': 'FAIL',
                        'output': output
                    })
            
            # Save results
            results_file = os.path.join(
                TEST_RESULTS,
                f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(results_file, 'w') as f:
                json.dump(test_results, f, indent=2)
            
            logger.info(f"📊 Results saved: {results_file}")
            
            return test_results
            
        except Exception as e:
            logger.error(f"Test suite execution failed: {e}")
            return {'tests_run': 0, 'error': str(e)}



def main():
    """Main execution"""
    try:
        print("=" * 80)
        print("🧪 AUTO-TESTING ENGINE 🧪")
        print("=" * 80)
        print("The system tests itself")
        print("=" * 80)
        print()
        
        engine = AutoTestingEngine()
        
        print("🔍 Discovering and testing tools...")
        results = engine.run_all_tests()
        
        print()
        print("=" * 80)
        print("📊 TEST RESULTS")
        print("=" * 80)
        
        total = results.get('total_tools', 0)
        passed = results.get('tests_passed', 0)
        failed = results.get('tests_failed', 0)
        
        if total > 0:
            print(f"✅ Passed: {passed}/{total}")
            print(f"❌ Failed: {failed}/{total}")
            
            success_rate = (passed / total) * 100 if total > 0 else 0
            print(f"📈 Success Rate: {success_rate:.1f}%")
            
            print()
            
            if failed > 0:
                print("Failed tools:")
                for result in results.get('results', []):
                    if result['status'] == 'FAIL':
                        print(f"  ❌ {result['tool']}")
            
            print()
            print(f"📁 Test files: ~/vy-nexus/auto_tests/")
            print(f"📊 Results: ~/vy-nexus/auto_tests/test_results/")
        else:
            if 'error' in results:
                print(f"❌ Testing failed: {results['error']}")
            else:
                print("❌ No tools found to test")
        
        print()
        print("=" * 80)
        print("💓 Self-Validating Intelligence")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
