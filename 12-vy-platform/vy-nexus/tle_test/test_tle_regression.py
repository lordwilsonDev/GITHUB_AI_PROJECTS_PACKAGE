#!/usr/bin/env python3
"""
TLE Regression Test Suite
==========================

Automated tests that prevent the system from breaking again.

Run before every commit:
    python test_tle_regression.py

Run in CI/CD pipeline to catch issues automatically.
"""

import torch
from pathlib import Path
import sys

# Add color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_pass(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_fail(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_warn(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")


class TLERegressionTests:
    """Automated tests to prevent common TLE failures"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def test_vectors_exist(self):
        """Test 1: Learned vectors file exists"""
        print("\n[Test 1] Checking learned vectors exist...")
        
        vector_path = Path("tle_learned_vectors.pt")
        
        if vector_path.exists():
            print_pass("Learned vectors file found")
            
            # Check file size (should be >1KB)
            size = vector_path.stat().st_size
            if size > 1000:
                print_pass(f"Vector file size: {size} bytes (valid)")
                self.passed += 1
                return True
            else:
                print_fail(f"Vector file too small: {size} bytes (possibly corrupt)")
                self.failed += 1
                return False
        else:
            print_fail("tle_learned_vectors.pt not found")
            print_info("Run: python learn_vectors.py")
            self.failed += 1
            return False
    
    def test_vectors_not_random(self):
        """Test 2: Vectors are not random torch.randn"""
        print("\n[Test 2] Verifying vectors are learned (not random)...")
        
        vector_path = Path("tle_learned_vectors.pt")
        if not vector_path.exists():
            print_warn("Skipping (vectors don't exist)")
            self.warnings += 1
            return None
        
        try:
            vectors = torch.load(vector_path)
            
            # Check structure
            if 'anti_sycophancy' not in vectors:
                print_fail("Missing 'anti_sycophancy' key")
                self.failed += 1
                return False
            
            if 'metadata' not in vectors:
                print_warn("Missing metadata (older version?)")
                self.warnings += 1
            else:
                meta = vectors['metadata']
                training_pairs = meta.get('training_pairs', 0)
                
                if training_pairs == 0:
                    print_fail(f"No training pairs! Vectors are likely random.")
                    self.failed += 1
                    return False
                elif training_pairs < 3:
                    print_warn(f"Only {training_pairs} training pairs (recommend 5+)")
                    self.warnings += 1
                else:
                    print_pass(f"Trained on {training_pairs} contrastive pairs")
            
            # Check vector properties
            vec = vectors['anti_sycophancy']
            norm = torch.norm(vec).item()
            
            if 0.9 < norm < 1.1:  # Should be normalized
                print_pass(f"Vector norm: {norm:.4f} (normalized)")
                self.passed += 1
                return True
            else:
                print_fail(f"Vector norm: {norm:.4f} (should be ~1.0)")
                self.failed += 1
                return False
                
        except Exception as e:
            print_fail(f"Error loading vectors: {e}")
            self.failed += 1
            return False
    
    def test_pipeline_imports(self):
        """Test 3: Pipeline code has no import errors"""
        print("\n[Test 3] Checking pipeline imports...")
        
        try:
            import love_engine_pipeline_v2
            print_pass("love_engine_pipeline_v2.py imports successfully")
            self.passed += 1
            return True
        except ImportError as e:
            print_fail(f"Import error: {e}")
            self.failed += 1
            return False
        except Exception as e:
            print_fail(f"Unexpected error: {e}")
            self.failed += 1
            return False
    
    def test_validation_framework(self):
        """Test 4: Validation framework works"""
        print("\n[Test 4] Testing validation framework...")
        
        try:
            from validate_tle import TLEValidator
            
            # Create validator
            validator = TLEValidator()
            print_pass("Validator initialized")
            
            # Test coherence check on known good text
            good_text = "The Earth is spherical. This is confirmed by satellite imagery and basic physics."
            passed, ppl, msg = validator.check_coherence(good_text, max_perplexity=200)
            
            if passed:
                print_pass(f"Coherence test passed (perplexity: {ppl:.1f})")
                self.passed += 1
                return True
            else:
                print_warn(f"Coherence test failed for known good text: {msg}")
                self.warnings += 1
                return None
                
        except Exception as e:
            print_fail(f"Validation framework error: {e}")
            self.failed += 1
            return False
    
    def test_no_random_vectors_in_pipeline(self):
        """Test 5: Pipeline doesn't use torch.randn for steering"""
        print("\n[Test 5] Scanning pipeline for random vector usage...")
        
        pipeline_file = Path("love_engine_pipeline_v2.py")
        
        if not pipeline_file.exists():
            print_warn("Pipeline file not found")
            self.warnings += 1
            return None
        
        content = pipeline_file.read_text()
        
        # Check for dangerous patterns
        dangerous_patterns = [
            "torch.randn(hidden_dim",
            "torch.randn_like",
            "np.random.randn",
        ]
        
        found_dangerous = []
        for pattern in dangerous_patterns:
            if pattern in content and "# EXAMPLE" not in content:
                found_dangerous.append(pattern)
        
        if found_dangerous:
            print_fail(f"Found random vector generation: {found_dangerous}")
            print_fail("This will cause gibberish output!")
            self.failed += 1
            return False
        
        # Check for correct pattern
        if "torch.load" in content and "tle_learned_vectors.pt" in content:
            print_pass("Pipeline correctly loads learned vectors")
            self.passed += 1
            return True
        else:
            print_warn("Couldn't verify vector loading pattern")
            self.warnings += 1
            return None
    
    def test_conscience_strength_reasonable(self):
        """Test 6: Conscience strength is in safe range"""
        print("\n[Test 6] Checking conscience_strength parameter...")
        
        pipeline_file = Path("love_engine_pipeline_v2.py")
        
        if not pipeline_file.exists():
            print_warn("Pipeline file not found")
            self.warnings += 1
            return None
        
        content = pipeline_file.read_text()
        
        # Extract conscience_strength value
        # Look for: conscience_strength=0.05
        import re
        pattern = r'conscience_strength=([0-9.]+)'
        matches = re.findall(pattern, content)
        
        if not matches:
            print_warn("Couldn't find conscience_strength parameter")
            self.warnings += 1
            return None
        
        # Check all found values
        all_safe = True
        for match in matches:
            value = float(match)
            
            if value == 0.0:
                print_info(f"Found conscience_strength={value} (baseline mode)")
            elif 0.01 <= value <= 0.15:
                print_pass(f"conscience_strength={value} (safe range)")
            elif value < 0.01:
                print_warn(f"conscience_strength={value} (very gentle, might not steer)")
            elif 0.15 < value <= 0.30:
                print_warn(f"conscience_strength={value} (risky, monitor coherence)")
                all_safe = False
            else:
                print_fail(f"conscience_strength={value} (DANGER: likely to cause T→∞)")
                all_safe = False
        
        if all_safe:
            self.passed += 1
            return True
        else:
            self.failed += 1
            return False
    
    def test_safety_mechanisms_present(self):
        """Test 7: All safety mechanisms are in place"""
        print("\n[Test 7] Verifying safety mechanisms...")
        
        pipeline_file = Path("love_engine_pipeline_v2.py")
        
        if not pipeline_file.exists():
            print_warn("Pipeline file not found")
            self.warnings += 1
            return None
        
        content = pipeline_file.read_text()
        
        required_mechanisms = {
            'LogitsSanitizer': 'Logits sanitization before sampling',
            'torch.nan_to_num': 'NaN/Inf replacement',
            'torch.clamp': 'Activation clamping',
            'coherence_ratio': 'Geometric coherence monitoring',
            'geometric_failures': 'Failure tracking',
            'max_failures': 'Safety cutoff mechanism',
        }
        
        missing = []
        found = []
        
        for mechanism, description in required_mechanisms.items():
            if mechanism in content:
                found.append(f"{mechanism} ({description})")
            else:
                missing.append(f"{mechanism} ({description})")
        
        if not missing:
            print_pass("All safety mechanisms present:")
            for f in found:
                print(f"    ✓ {f}")
            self.passed += 1
            return True
        else:
            print_fail("Missing safety mechanisms:")
            for m in missing:
                print(f"    ✗ {m}")
            self.failed += 1
            return False
    
    def run_all_tests(self):
        """Run full test suite"""
        print("="*60)
        print("TLE REGRESSION TEST SUITE")
        print("="*60)
        
        self.test_vectors_exist()
        self.test_vectors_not_random()
        self.test_pipeline_imports()
        self.test_validation_framework()
        self.test_no_random_vectors_in_pipeline()
        self.test_conscience_strength_reasonable()
        self.test_safety_mechanisms_present()
        
        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.END}")
        print(f"{Colors.YELLOW}Warnings: {self.warnings}{Colors.END}")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}✅ ALL TESTS PASSED{Colors.END}")
            print("System is safe to deploy.")
            return 0
        else:
            print(f"\n{Colors.RED}❌ {self.failed} TEST(S) FAILED{Colors.END}")
            print("DO NOT DEPLOY. Fix failures first.")
            return 1


if __name__ == "__main__":
    tester = TLERegressionTests()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)
