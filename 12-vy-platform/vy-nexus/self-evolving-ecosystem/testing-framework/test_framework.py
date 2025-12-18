"""\nComprehensive Testing Framework for Self-Evolving AI Ecosystem\nProvides unified testing infrastructure for all features\n"""

import unittest
import json
import time
from typing import Dict, Any, List, Callable, Optional
from pathlib import Path
from datetime import datetime
import sys
import traceback

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.logging import get_logger
from shared.metrics import get_metrics_collector


class FeatureTestCase(unittest.TestCase):
    """\n    Base test case class for all feature tests.\n    Provides common testing utilities and setup/teardown.\n    """
    
    feature_name = "base-feature"  # Override in subclasses
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment for the feature"""
        cls.logger = get_logger(cls.feature_name)
        cls.metrics = get_metrics_collector()
        cls.test_results = []
        cls.logger.info(f"Starting tests for {cls.feature_name}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        cls.logger.info(f"Completed tests for {cls.feature_name}")
        cls._generate_test_report()
    
    def setUp(self):
        """Set up before each test"""
        self.start_time = time.time()
        self.test_name = self._testMethodName
        self.logger.info(f"Starting test: {self.test_name}")
    
    def tearDown(self):
        """Clean up after each test"""
        duration = time.time() - self.start_time
        self.logger.info(f"Completed test: {self.test_name} in {duration:.3f}s")
        
        # Record test metrics
        self.metrics.record_performance_metric(
            self.feature_name,
            f"test_{self.test_name}_duration_ms",
            duration * 1000,
            {'test_name': self.test_name}
        )
    
    @classmethod
    def _generate_test_report(cls):
        """Generate test report for the feature"""
        report_dir = Path(__file__).parent.parent / "reports" / "test-results"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"{cls.feature_name}_test_report.json"
        report = {
            'feature': cls.feature_name,
            'timestamp': datetime.now().isoformat(),
            'results': cls.test_results
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
    
    def assert_performance(self, operation: Callable, max_duration_ms: float, 
                          operation_name: str = "operation"):
        """\n        Assert that an operation completes within a time limit.\n        \n        Args:\n            operation: Callable to execute\n            max_duration_ms: Maximum allowed duration in milliseconds\n            operation_name: Name of the operation for logging\n        """
        start = time.time()
        result = operation()
        duration_ms = (time.time() - start) * 1000
        
        self.assertLess(
            duration_ms, 
            max_duration_ms,
            f"{operation_name} took {duration_ms:.2f}ms, expected < {max_duration_ms}ms"
        )
        
        # Record performance metric
        self.metrics.record_performance_metric(
            self.feature_name,
            f"{operation_name}_duration_ms",
            duration_ms
        )
        
        return result
    
    def assert_accuracy(self, predicted: Any, actual: Any, 
                       min_accuracy: float, metric_name: str = "accuracy"):
        """\n        Assert that prediction accuracy meets minimum threshold.\n        \n        Args:\n            predicted: Predicted values\n            actual: Actual values\n            min_accuracy: Minimum required accuracy (0.0 to 1.0)\n            metric_name: Name of the accuracy metric\n        """
        if isinstance(predicted, list) and isinstance(actual, list):
            correct = sum(1 for p, a in zip(predicted, actual) if p == a)
            accuracy = correct / len(actual) if actual else 0.0
        else:
            accuracy = 1.0 if predicted == actual else 0.0
        
        self.assertGreaterEqual(
            accuracy,
            min_accuracy,
            f"{metric_name} is {accuracy:.2%}, expected >= {min_accuracy:.2%}"
        )
        
        # Record accuracy metric
        self.metrics.record_learning_metric(
            self.feature_name,
            metric_name,
            accuracy
        )
        
        return accuracy


class IntegrationTestCase(unittest.TestCase):
    """\n    Base test case for integration tests between features.\n    """
    
    features = []  # List of features being tested together
    
    @classmethod
    def setUpClass(cls):
        """Set up integration test environment"""
        cls.logger = get_logger('integration-tests')
        cls.metrics = get_metrics_collector()
        cls.logger.info(f"Starting integration tests for: {', '.join(cls.features)}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after integration tests"""
        cls.logger.info(f"Completed integration tests for: {', '.join(cls.features)}")


class PerformanceTestCase(unittest.TestCase):
    """\n    Base test case for performance and stress tests.\n    """
    
    feature_name = "base-feature"
    
    @classmethod
    def setUpClass(cls):
        """Set up performance test environment"""
        cls.logger = get_logger(f'{cls.feature_name}-performance')
        cls.metrics = get_metrics_collector()
        cls.performance_results = []
    
    def run_load_test(self, operation: Callable, num_iterations: int,
                     max_avg_duration_ms: float) -> Dict[str, float]:
        """\n        Run a load test on an operation.\n        \n        Args:\n            operation: Callable to test\n            num_iterations: Number of times to run the operation\n            max_avg_duration_ms: Maximum allowed average duration\n        \n        Returns:\n            Dictionary with performance statistics\n        """
        durations = []
        
        for i in range(num_iterations):
            start = time.time()
            try:
                operation()
                duration_ms = (time.time() - start) * 1000
                durations.append(duration_ms)
            except Exception as e:
                self.logger.error(f"Load test iteration {i} failed: {e}")
                raise
        
        stats = {
            'avg': sum(durations) / len(durations),
            'min': min(durations),
            'max': max(durations),
            'iterations': num_iterations
        }
        
        self.assertLess(
            stats['avg'],
            max_avg_duration_ms,
            f"Average duration {stats['avg']:.2f}ms exceeds limit {max_avg_duration_ms}ms"
        )
        
        # Record performance metrics
        self.metrics.record_performance_metric(
            self.feature_name,
            'load_test_avg_duration_ms',
            stats['avg'],
            {'iterations': num_iterations}
        )
        
        return stats


class TestRunner:
    """\n    Custom test runner for the ecosystem.\n    Provides enhanced reporting and metrics collection.\n    """
    
    def __init__(self, test_dir: str = None):
        self.test_dir = Path(test_dir) if test_dir else Path(__file__).parent
        self.logger = get_logger('test-runner')
        self.metrics = get_metrics_collector()
        self.results = []
    
    def discover_tests(self, pattern: str = "test_*.py") -> unittest.TestSuite:
        """\n        Discover all tests matching the pattern.\n        \n        Args:\n            pattern: File pattern to match\n        \n        Returns:\n            Test suite containing discovered tests\n        """
        loader = unittest.TestLoader()
        suite = loader.discover(str(self.test_dir), pattern=pattern)
        return suite
    
    def run_tests(self, suite: unittest.TestSuite = None, 
                 verbosity: int = 2) -> unittest.TestResult:
        """\n        Run test suite and collect results.\n        \n        Args:\n            suite: Test suite to run (discovers if None)\n            verbosity: Verbosity level (0-2)\n        \n        Returns:\n            Test results\n        """
        if suite is None:
            suite = self.discover_tests()
        
        self.logger.info("Starting test run")
        start_time = time.time()
        
        runner = unittest.TextTestRunner(verbosity=verbosity)
        result = runner.run(suite)
        
        duration = time.time() - start_time
        
        # Log results
        self.logger.info(f"Test run completed in {duration:.2f}s")
        self.logger.info(f"Tests run: {result.testsRun}")
        self.logger.info(f"Failures: {len(result.failures)}")
        self.logger.info(f"Errors: {len(result.errors)}")
        self.logger.info(f"Skipped: {len(result.skipped)}")
        
        # Record metrics
        self.metrics.record_performance_metric(
            'test-runner',
            'total_test_duration_s',
            duration,
            {
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors)
            }
        )
        
        # Generate report
        self._generate_report(result, duration)
        
        return result
    
    def _generate_report(self, result: unittest.TestResult, duration: float):
        """Generate comprehensive test report"""
        report_dir = Path(__file__).parent.parent / "reports" / "test-results"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'summary': {
                'total_tests': result.testsRun,
                'passed': result.testsRun - len(result.failures) - len(result.errors),
                'failed': len(result.failures),
                'errors': len(result.errors),
                'skipped': len(result.skipped),
                'success_rate': (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun if result.testsRun > 0 else 0
            },
            'failures': [
                {
                    'test': str(test),
                    'traceback': traceback
                }
                for test, traceback in result.failures
            ],
            'errors': [
                {
                    'test': str(test),
                    'traceback': traceback
                }
                for test, traceback in result.errors
            ]
        }
        
        report_file = report_dir / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Test report saved to {report_file}")


if __name__ == "__main__":
    # Run all tests
    runner = TestRunner()
    result = runner.run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
