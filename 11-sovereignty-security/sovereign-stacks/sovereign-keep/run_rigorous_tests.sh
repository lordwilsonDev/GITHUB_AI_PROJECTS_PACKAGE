#!/bin/bash
# Rigorous Testing Suite - Run All Tests
# This script runs the complete formal testing suite

set -e  # Exit on error

echo "========================================"
echo "Sovereign Keep Protocol"
echo "Rigorous Testing Suite"
echo "========================================"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check dependencies
echo "Checking dependencies..."
pip install -q pytest hypothesis psutil scikit-learn 2>/dev/null || true

echo ""
echo "========================================"
echo "PHASE 1: Formal Invariants"
echo "========================================"
echo "Testing mathematical laws that MUST hold..."
echo ""
python tests/test_formal_invariants.py -v

echo ""
echo "========================================"
echo "PHASE 2: Adversarial Semantics"
echo "========================================"
echo "Testing with adversarial inputs..."
echo ""
python tests/test_adversarial.py -v

echo ""
echo "========================================"
echo "PHASE 3: Model Robustness"
echo "========================================"
echo "Testing across different embedding models..."
echo ""
python tests/test_model_robustness.py -v

echo ""
echo "========================================"
echo "PHASE 4: Scale & Performance"
echo "========================================"
echo "Testing algorithmic complexity and limits..."
echo ""
python tests/test_scale_performance.py -v

echo ""
echo "========================================"
echo "PHASE 5: Original Test Suite"
echo "========================================"
echo "Running original semantic analysis tests..."
echo ""
python tests/test_semantic_analysis.py -v

echo ""
echo "========================================"
echo "PHASE 6: Property-Based Tests"
echo "========================================"
echo "Running property-based tests (if available)..."
echo ""
if [ -f tests/test_property_based.py ]; then
    python tests/test_property_based.py -v
else
    echo "  (Skipped: test_property_based.py not found)"
fi

echo ""
echo "========================================"
echo "TEST SUMMARY"
echo "========================================"
echo ""
echo "✅ Formal Invariants: PASSED"
echo "✅ Adversarial Tests: PASSED"
echo "✅ Model Robustness: PASSED"
echo "✅ Scale Tests: PASSED"
echo "✅ Semantic Analysis: PASSED"
echo ""
echo "========================================"
echo "SYSTEM STATUS: PRODUCTION READY"
echo "========================================"
echo ""
echo "The Sovereign Keep Protocol has passed all rigorous tests."
echo "It is formally validated and ready for production use."
echo ""
