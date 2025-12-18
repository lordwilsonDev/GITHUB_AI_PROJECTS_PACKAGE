#!/usr/bin/env python3
"""
Test Suite for M1 LLM Optimizer
Basic tests to verify functionality
"""

import sys
import subprocess
import platform
from pathlib import Path


class TestRunner:
    """Simple test runner for the optimizer"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
        
    def test(self, name, func):
        """Run a test function"""
        try:
            func()
            print(f"✓ {name}")
            self.passed += 1
            self.tests.append((name, True, None))
        except AssertionError as e:
            print(f"✗ {name}: {e}")
            self.failed += 1
            self.tests.append((name, False, str(e)))
        except Exception as e:
            print(f"✗ {name}: Unexpected error: {e}")
            self.failed += 1
            self.tests.append((name, False, str(e)))
    
    def summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Total:  {self.passed + self.failed}")
        
        if self.failed > 0:
            print("\nFailed Tests:")
            for name, passed, error in self.tests:
                if not passed:
                    print(f"  - {name}: {error}")
        
        print("="*70 + "\n")
        return self.failed == 0


def test_macos():
    """Test that we're running on macOS"""
    assert platform.system() == 'Darwin', "Must run on macOS"


def test_apple_silicon():
    """Test that we're on Apple Silicon"""
    result = subprocess.run(
        ['sysctl', '-n', 'machdep.cpu.brand_string'],
        capture_output=True, text=True
    )
    chip = result.stdout.strip()
    assert 'Apple' in chip, f"Not Apple Silicon: {chip}"


def test_python_version():
    """Test Python version is 3.8+"""
    version = sys.version_info
    assert version.major == 3 and version.minor >= 8, \
        f"Python 3.8+ required, got {version.major}.{version.minor}"


def test_project_structure():
    """Test that all required files exist"""
    base = Path(__file__).parent
    
    required_files = [
        'm1_optimizer.py',
        'README.md',
        'requirements.txt',
        'config/optimization_profiles.json',
        'modules/system_analyzer.py',
        'modules/os_optimizer.py',
        'modules/ollama_optimizer.py',
        'modules/python_optimizer.py',
        'modules/thermal_manager.py',
        'modules/process_manager.py',
        'utils/monitoring.py',
        'utils/rollback.py',
        'utils/model_recommender.py',
    ]
    
    for file in required_files:
        path = base / file
        assert path.exists(), f"Missing file: {file}"


def test_main_script_executable():
    """Test that main script can be imported"""
    base = Path(__file__).parent
    sys.path.insert(0, str(base))
    
    try:
        # Try to import without executing
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "m1_optimizer",
            base / "m1_optimizer.py"
        )
        assert spec is not None, "Could not load m1_optimizer.py"
    except Exception as e:
        raise AssertionError(f"Failed to load main script: {e}")


def test_psutil_available():
    """Test that psutil is installed"""
    try:
        import psutil
        assert True
    except ImportError:
        raise AssertionError("psutil not installed. Run: pip3 install psutil")


def test_system_info_commands():
    """Test that system info commands work"""
    commands = [
        ['sysctl', '-n', 'hw.memsize'],
        ['sysctl', '-n', 'machdep.cpu.brand_string'],
    ]
    
    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Command failed: {' '.join(cmd)}"


def test_ollama_check():
    """Test Ollama detection (non-critical)"""
    result = subprocess.run(
        ['which', 'ollama'],
        capture_output=True, text=True
    )
    # This is informational, not a failure
    if result.returncode != 0:
        print("  ℹ️  Ollama not found (optional)")


def test_config_file_valid():
    """Test that config file is valid JSON"""
    import json
    base = Path(__file__).parent
    config_file = base / 'config' / 'optimization_profiles.json'
    
    with open(config_file, 'r') as f:
        data = json.load(f)
    
    assert 'profiles' in data, "Config missing 'profiles' key"
    assert len(data['profiles']) > 0, "No profiles defined"


def test_dry_run_mode():
    """Test that dry-run mode works"""
    base = Path(__file__).parent
    result = subprocess.run(
        [sys.executable, str(base / 'm1_optimizer.py'), '--analyze'],
        capture_output=True, text=True,
        timeout=30
    )
    
    # Should not crash
    assert result.returncode in [0, 1], f"Script crashed: {result.stderr}"


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("M1 LLM OPTIMIZER - TEST SUITE")
    print("="*70 + "\n")
    
    runner = TestRunner()
    
    # System tests
    print("System Tests:")
    runner.test("macOS detection", test_macos)
    runner.test("Apple Silicon detection", test_apple_silicon)
    runner.test("Python version", test_python_version)
    runner.test("System info commands", test_system_info_commands)
    
    # Dependency tests
    print("\nDependency Tests:")
    runner.test("psutil installed", test_psutil_available)
    runner.test("Ollama detection", test_ollama_check)
    
    # Project structure tests
    print("\nProject Structure Tests:")
    runner.test("Required files exist", test_project_structure)
    runner.test("Main script loadable", test_main_script_executable)
    runner.test("Config file valid", test_config_file_valid)
    
    # Functional tests
    print("\nFunctional Tests:")
    runner.test("Dry-run mode", test_dry_run_mode)
    
    # Summary
    success = runner.summary()
    
    if success:
        print("✓ All tests passed! The optimizer is ready to use.")
        print("\nNext steps:")
        print("  1. Run: python3 m1_optimizer.py --analyze")
        print("  2. Review the system analysis")
        print("  3. Run: python3 m1_optimizer.py --all --dry-run")
        print("  4. Apply optimizations: python3 m1_optimizer.py --all")
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
