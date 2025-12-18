#!/usr/bin/env python3
"""
Tests for Programming Language Learner

Author: Vy-Nexus Self-Evolving AI
Created: December 15, 2025
"""

import unittest
import os
import tempfile
import shutil
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from technical_learning.programming_language_learner import (
    ProgrammingLanguageLearner,
    LanguageCategory,
    PatternType,
    LanguageFeature,
    CodePattern
)


class TestProgrammingLanguageLearner(unittest.TestCase):
    """Test cases for ProgrammingLanguageLearner."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.learner = ProgrammingLanguageLearner(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test learner initialization."""
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertIsInstance(self.learner.knowledge, dict)
        self.assertIsInstance(self.learner.patterns, dict)
        
        # Should have base languages
        self.assertIn('python', self.learner.knowledge)
        self.assertIn('javascript', self.learner.knowledge)
    
    def test_learn_language_feature(self):
        """Test learning a language feature."""
        feature = self.learner.learn_language_feature(
            'python',
            'decorators',
            'syntax',
            'Function wrappers',
            syntax_examples=['@decorator\ndef func(): pass']
        )
        
        self.assertIsInstance(feature, LanguageFeature)
        self.assertEqual(feature.language, 'python')
        self.assertEqual(feature.feature_name, 'decorators')
    
    def test_learn_code_pattern(self):
        """Test learning a code pattern."""
        pattern = self.learner.learn_code_pattern(
            'python',
            'context_manager',
            PatternType.BEST_PRACTICE.value,
            'with open(file) as f:\n    pass',
            'Resource management pattern'
        )
        
        self.assertIsInstance(pattern, CodePattern)
        self.assertEqual(pattern.language, 'python')
        self.assertEqual(pattern.name, 'context_manager')
    
    def test_learn_best_practice(self):
        """Test learning a best practice."""
        self.learner.learn_best_practice(
            'python',
            'Use list comprehensions',
            'More Pythonic and readable'
        )
        
        practices = self.learner.knowledge['python']['best_practices']
        self.assertGreater(len(practices), 0)
        self.assertEqual(practices[-1]['practice'], 'Use list comprehensions')
    
    def test_learn_common_error(self):
        """Test learning a common error."""
        self.learner.learn_common_error(
            'python',
            'IndentationError',
            'Inconsistent indentation',
            'Use consistent spaces or tabs'
        )
        
        errors = self.learner.knowledge['python']['common_errors']
        self.assertGreater(len(errors), 0)
        self.assertEqual(errors[-1]['error_type'], 'IndentationError')
    
    def test_learn_library(self):
        """Test learning about a library."""
        self.learner.learn_library(
            'python',
            'requests',
            'HTTP library',
            common_functions=['get', 'post', 'put']
        )
        
        libraries = self.learner.knowledge['python']['libraries']
        self.assertIn('requests', libraries)
        self.assertEqual(libraries['requests']['purpose'], 'HTTP library')
    
    def test_analyze_python_code(self):
        """Test analyzing Python code."""
        code = """
with open('file.txt') as f:
    data = [line.strip() for line in f]
        """
        
        analysis = self.learner.analyze_code_sample('python', code)
        
        self.assertIn('patterns_found', analysis)
        self.assertIn('context_manager', analysis['patterns_found'])
        self.assertIn('list_comprehension', analysis['patterns_found'])
    
    def test_analyze_javascript_code(self):
        """Test analyzing JavaScript code."""
        code = """
const fetchData = async () => {
    const response = await fetch(url);
    return response.json();
};
        """
        
        analysis = self.learner.analyze_code_sample('javascript', code)
        
        self.assertIn('patterns_found', analysis)
        self.assertIn('arrow_function', analysis['patterns_found'])
        self.assertIn('async_await', analysis['patterns_found'])
    
    def test_analyze_java_code(self):
        """Test analyzing Java code."""
        code = """
public class Example implements Interface {
    @Override
    public void method() {
        // implementation
    }
}
        """
        
        analysis = self.learner.analyze_code_sample('java', code)
        
        self.assertIn('patterns_found', analysis)
        self.assertIn('interface_implementation', analysis['patterns_found'])
    
    def test_proficiency_update(self):
        """Test that proficiency updates as learning progresses."""
        initial_proficiency = self.learner.knowledge['python']['proficiency_level']
        
        # Learn multiple things
        for i in range(5):
            self.learner.learn_language_feature(
                'python',
                f'feature_{i}',
                'syntax',
                f'Feature {i}'
            )
        
        new_proficiency = self.learner.knowledge['python']['proficiency_level']
        
        self.assertGreater(new_proficiency, initial_proficiency)
    
    def test_get_language_knowledge(self):
        """Test getting language knowledge."""
        knowledge = self.learner.get_language_knowledge('python')
        
        self.assertIsNotNone(knowledge)
        self.assertEqual(knowledge['language'], 'python')
        self.assertIn('features', knowledge)
        self.assertIn('patterns', knowledge)
    
    def test_get_patterns_for_language(self):
        """Test getting patterns for a language."""
        # Add some patterns
        self.learner.learn_code_pattern(
            'python',
            'pattern1',
            PatternType.IDIOM.value,
            'code1',
            'desc1'
        )
        self.learner.learn_code_pattern(
            'python',
            'pattern2',
            PatternType.BEST_PRACTICE.value,
            'code2',
            'desc2'
        )
        
        patterns = self.learner.get_patterns_for_language('python')
        
        self.assertGreater(len(patterns), 0)
    
    def test_get_patterns_filtered_by_type(self):
        """Test getting patterns filtered by type."""
        self.learner.learn_code_pattern(
            'python',
            'idiom_pattern',
            PatternType.IDIOM.value,
            'code',
            'desc'
        )
        self.learner.learn_code_pattern(
            'python',
            'best_practice_pattern',
            PatternType.BEST_PRACTICE.value,
            'code',
            'desc'
        )
        
        idioms = self.learner.get_patterns_for_language(
            'python',
            pattern_type=PatternType.IDIOM.value
        )
        
        self.assertGreater(len(idioms), 0)
        for pattern in idioms:
            self.assertEqual(pattern['pattern_type'], PatternType.IDIOM.value)
    
    def test_compare_languages(self):
        """Test comparing two languages."""
        comparison = self.learner.compare_languages('python', 'javascript')
        
        self.assertIn('languages', comparison)
        self.assertIn('proficiency', comparison)
        self.assertIn('python', comparison['proficiency'])
        self.assertIn('javascript', comparison['proficiency'])
    
    def test_get_learning_summary(self):
        """Test getting learning summary."""
        summary = self.learner.get_learning_summary()
        
        self.assertIn('languages_learned', summary)
        self.assertIn('total_features', summary)
        self.assertIn('total_patterns', summary)
        self.assertIn('languages_by_proficiency', summary)
        
        self.assertGreater(summary['languages_learned'], 0)
    
    def test_pattern_frequency_tracking(self):
        """Test that pattern frequency is tracked."""
        # Learn same pattern multiple times
        for i in range(3):
            self.learner.learn_code_pattern(
                'python',
                'common_pattern',
                PatternType.IDIOM.value,
                'code',
                'desc'
            )
        
        patterns = self.learner.get_patterns_for_language('python')
        common_pattern = next(p for p in patterns if p['name'] == 'common_pattern')
        
        self.assertGreaterEqual(common_pattern['frequency'], 3)
    
    def test_learning_log(self):
        """Test that learning is logged."""
        initial_log_length = len(self.learner.learning_log)
        
        self.learner.learn_language_feature(
            'python',
            'new_feature',
            'syntax',
            'description'
        )
        
        self.assertEqual(len(self.learner.learning_log), initial_log_length + 1)
        self.assertEqual(self.learner.learning_log[-1]['item_name'], 'new_feature')
    
    def test_persistence(self):
        """Test that data persists across instances."""
        self.learner.learn_language_feature(
            'python',
            'persistent_feature',
            'syntax',
            'test'
        )
        
        # Create new instance
        learner2 = ProgrammingLanguageLearner(data_dir=self.test_dir)
        
        # Should load saved data
        knowledge = learner2.get_language_knowledge('python')
        feature_names = [f['feature_name'] for f in knowledge['features'].values()]
        
        self.assertIn('persistent_feature', feature_names)
    
    def test_new_language_creation(self):
        """Test creating knowledge for a new language."""
        self.learner.learn_language_feature(
            'rust',
            'ownership',
            'core',
            'Memory safety without garbage collection'
        )
        
        self.assertIn('rust', self.learner.knowledge)
        self.assertEqual(self.learner.knowledge['rust']['language'], 'rust')
    
    def test_code_quality_assessment(self):
        """Test code quality assessment."""
        good_code = """
with open('file.txt') as f:
    data = f.read()
        """
        
        bad_code = """
from module import *
x = 1
        """
        
        good_analysis = self.learner.analyze_code_sample('python', good_code)
        bad_analysis = self.learner.analyze_code_sample('python', bad_code)
        
        # Good code should have higher quality score
        self.assertGreater(
            good_analysis['quality_score'],
            bad_analysis['quality_score']
        )
    
    def test_javascript_quality_checks(self):
        """Test JavaScript-specific quality checks."""
        modern_code = "const x = 5; if (x === 5) { }"
        old_code = "var x = 5; if (x == 5) { }"
        
        modern_analysis = self.learner.analyze_code_sample('javascript', modern_code)
        old_analysis = self.learner.analyze_code_sample('javascript', old_code)
        
        # Modern code should have higher quality
        self.assertGreater(
            modern_analysis['quality_score'],
            old_analysis['quality_score']
        )
        
        # Old code should have improvement suggestions
        self.assertGreater(len(old_analysis['potential_improvements']), 0)


class TestLanguageFeature(unittest.TestCase):
    """Test cases for LanguageFeature dataclass."""
    
    def test_feature_creation(self):
        """Test creating a language feature."""
        feature = LanguageFeature(
            feature_id="feat_001",
            language="python",
            feature_name="decorators",
            feature_type="syntax",
            description="Function wrappers"
        )
        
        self.assertEqual(feature.language, "python")
        self.assertEqual(feature.feature_name, "decorators")


class TestCodePattern(unittest.TestCase):
    """Test cases for CodePattern dataclass."""
    
    def test_pattern_creation(self):
        """Test creating a code pattern."""
        pattern = CodePattern(
            pattern_id="pat_001",
            language="python",
            pattern_type=PatternType.IDIOM.value,
            name="list_comp",
            description="List comprehension",
            code_template="[x for x in range(10)]"
        )
        
        self.assertEqual(pattern.language, "python")
        self.assertEqual(pattern.name, "list_comp")


if __name__ == '__main__':
    unittest.main()
