# 🧪 Testing Framework
## Self-Evolving AI Ecosystem

---

## Overview

Comprehensive testing framework for all ecosystem features. Provides unified testing infrastructure with performance monitoring, validation, and detailed reporting.

---

## Components

### 1. Test Framework (`test_framework.py`)

Core testing infrastructure with three base test case classes:

#### FeatureTestCase
Base class for feature-specific unit tests.

**Features:**
- Automatic logging and metrics collection
- Performance assertions
- Accuracy validation
- Test report generation

**Usage:**
```python
from testing_framework.test_framework import FeatureTestCase

class TestLearningEngine(FeatureTestCase):
    feature_name = "learning-engine"
    
    def test_pattern_recognition(self):
        # Test implementation
        result = self.assert_performance(
            lambda: recognize_pattern(data),
            max_duration_ms=100,
            operation_name="pattern_recognition"
        )
        self.assertIsNotNone(result)
```

#### IntegrationTestCase
Base class for testing feature interactions.

**Features:**
- Multi-feature testing support
- Integration logging
- Cross-feature validation

**Usage:**
```python
from testing_framework.test_framework import IntegrationTestCase

class TestLearningOptimizationIntegration(IntegrationTestCase):
    features = ['learning-engine', 'process-optimization']
    
    def test_learning_feeds_optimization(self):
        # Test feature interaction
        pass
```

#### PerformanceTestCase
Base class for performance and load testing.

**Features:**
- Load testing utilities
- Performance statistics
- Stress testing support

**Usage:**
```python
from testing_framework.test_framework import PerformanceTestCase

class TestLearningEnginePerformance(PerformanceTestCase):
    feature_name = "learning-engine"
    
    def test_load_handling(self):
        stats = self.run_load_test(
            operation=lambda: process_data(),
            num_iterations=1000,
            max_avg_duration_ms=50
        )
        self.assertLess(stats['max'], 200)
```

### 2. Validation Framework (`validation/validation_framework.py`)

Data and behavior validation utilities.

#### Validators Available:

1. **MetricsValidator** - Validate metric data
2. **LearningValidator** - Validate learning patterns and confidence
3. **OptimizationValidator** - Validate optimization results
4. **SystemValidator** - Validate system health and state

**Usage:**
```python
from testing_framework.validation.validation_framework import MetricsValidator

validator = MetricsValidator(strict=False)
if validator.validate_metric(metric_data):
    print("Valid metric")
else:
    print(f"Errors: {validator.get_errors()}")
```

### 3. Test Runner

Custom test runner with enhanced reporting.

**Usage:**
```python
from testing_framework.test_framework import TestRunner

runner = TestRunner()
result = runner.run_tests(verbosity=2)
```

---

## Directory Structure

```
testing-framework/
├── test_framework.py          # Core testing infrastructure
├── README.md                   # This file
├── unit-tests/                 # Unit tests for each feature
│   ├── test_learning_engine.py
│   ├── test_process_optimization.py
│   └── ...
├── integration-tests/          # Integration tests
│   ├── test_learning_optimization.py
│   └── ...
├── performance-tests/          # Performance tests
│   ├── test_learning_performance.py
│   └── ...
└── validation/                 # Validation utilities
    ├── validation_framework.py
    └── __init__.py
```

---

## Running Tests

### Run All Tests
```bash
python -m testing_framework.test_framework
```

### Run Specific Feature Tests
```bash
python -m unittest testing_framework.unit_tests.test_learning_engine
```

### Run Integration Tests
```bash
python -m unittest discover -s testing_framework/integration-tests
```

### Run Performance Tests
```bash
python -m unittest discover -s testing_framework/performance-tests
```

---

## Test Reports

Test reports are automatically generated in:
```
/vy-nexus/reports/test-results/
```

Report format:
```json
{
  "timestamp": "2025-12-15T00:15:00",
  "duration_seconds": 45.2,
  "summary": {
    "total_tests": 150,
    "passed": 148,
    "failed": 2,
    "errors": 0,
    "skipped": 0,
    "success_rate": 0.987
  },
  "failures": [...],
  "errors": [...]
}
```

---

## Best Practices

### 1. Test Organization
- One test file per feature
- Group related tests in test classes
- Use descriptive test names

### 2. Test Coverage
- Aim for 80%+ code coverage
- Test both success and failure cases
- Include edge cases

### 3. Performance Testing
- Set realistic performance thresholds
- Test under various load conditions
- Monitor resource usage

### 4. Integration Testing
- Test feature interactions
- Validate data flows
- Check error propagation

### 5. Validation
- Validate all inputs and outputs
- Use strict mode for critical validations
- Log validation errors for debugging

---

## Metrics Collection

All tests automatically collect metrics:
- Test duration
- Performance metrics
- Accuracy metrics
- Success/failure rates

Metrics are stored in the central metrics database and can be queried for analysis.

---

## Continuous Integration

The testing framework is designed to integrate with CI/CD pipelines:

1. **Pre-commit**: Run unit tests
2. **Pre-merge**: Run integration tests
3. **Pre-deployment**: Run full test suite including performance tests
4. **Post-deployment**: Run validation tests

---

## Troubleshooting

### Tests Failing
1. Check test logs in `/vy-nexus/logs/ecosystem/`
2. Review test reports in `/vy-nexus/reports/test-results/`
3. Verify test data and fixtures
4. Check feature dependencies

### Performance Issues
1. Review performance metrics
2. Check resource usage
3. Optimize slow operations
4. Adjust performance thresholds if needed

### Validation Errors
1. Check validation error messages
2. Verify data schemas
3. Update validators if requirements changed
4. Review data generation logic

---

**Created:** December 15, 2025
**Status:** Ready for Use
**Version:** 1.0.0
