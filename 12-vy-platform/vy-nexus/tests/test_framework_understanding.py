#!/usr/bin/env python3
"""
Tests for Framework Understanding Module

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

from technical_learning.framework_understanding import (
    FrameworkUnderstanding,
    FrameworkType,
    ArchitecturePattern,
    DesignPattern,
    Component,
    BestPractice,
    MigrationPath,
    FrameworkProfile
)


class TestFrameworkUnderstanding(unittest.TestCase):
    """Test cases for FrameworkUnderstanding."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.understanding = FrameworkUnderstanding(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test framework understanding initialization."""
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertIsInstance(self.understanding.frameworks, dict)
        
        # Should have common frameworks initialized
        self.assertGreater(len(self.understanding.frameworks), 0)
    
    def test_learn_framework(self):
        """Test learning a new framework."""
        framework = self.understanding.learn_framework(
            name="TestFramework",
            framework_type=FrameworkType.WEB_FRONTEND.value,
            version="1.0",
            description="A test framework",
            architecture_pattern=ArchitecturePattern.MVC.value
        )
        
        self.assertIsInstance(framework, FrameworkProfile)
        self.assertEqual(framework.name, "TestFramework")
        self.assertIn(framework.framework_id, self.understanding.frameworks)
    
    def test_learn_framework_with_concepts(self):
        """Test learning framework with core concepts."""
        framework = self.understanding.learn_framework(
            name="ConceptFramework",
            framework_type=FrameworkType.WEB_BACKEND.value,
            version="2.0",
            description="Framework with concepts",
            architecture_pattern=ArchitecturePattern.LAYERED.value,
            core_concepts=['routing', 'middleware', 'controllers'],
            design_patterns=[DesignPattern.MIDDLEWARE.value, DesignPattern.REPOSITORY.value]
        )
        
        self.assertEqual(len(framework.core_concepts), 3)
        self.assertEqual(len(framework.design_patterns), 2)
    
    def test_add_component(self):
        """Test adding a component to a framework."""
        framework = self.understanding.learn_framework(
            name="ComponentFramework",
            framework_type=FrameworkType.WEB_FRONTEND.value,
            version="1.0",
            description="Test",
            architecture_pattern=ArchitecturePattern.MVC.value
        )
        
        component = self.understanding.add_component(
            framework.framework_id,
            name="Router",
            purpose="Handle routing",
            dependencies=['core'],
            patterns_used=[DesignPattern.STRATEGY.value]
        )
        
        self.assertIsInstance(component, Component)
        self.assertEqual(component.name, "Router")
        self.assertIn(component.component_id, self.understanding.components)
    
    def test_add_best_practice(self):
        """Test adding a best practice."""
        framework = self.understanding.learn_framework(
            name="BestPracticeFramework",
            framework_type=FrameworkType.WEB_BACKEND.value,
            version="1.0",
            description="Test",
            architecture_pattern=ArchitecturePattern.MVC.value
        )
        
        practice = self.understanding.add_best_practice(
            framework.framework_id,
            title="Use dependency injection",
            description="Inject dependencies instead of creating them",
            category="architecture",
            importance="critical"
        )
        
        self.assertIsInstance(practice, BestPractice)
        self.assertEqual(practice.importance, "critical")
    
    def test_create_migration_path(self):
        """Test creating a migration path."""
        path = self.understanding.create_migration_path(
            from_framework="React",
            to_framework="Vue",
            difficulty="moderate",
            estimated_effort="2-4 weeks",
            key_differences=['reactivity system', 'template syntax'],
            migration_steps=['Learn Vue basics', 'Convert components', 'Test thoroughly']
        )
        
        self.assertIsInstance(path, MigrationPath)
        self.assertEqual(path.difficulty, "moderate")
        self.assertEqual(len(path.migration_steps), 3)
    
    def test_analyze_architecture(self):
        """Test architecture analysis."""
        framework = self.understanding.learn_framework(
            name="ArchFramework",
            framework_type=FrameworkType.WEB_FRONTEND.value,
            version="1.0",
            description="Test",
            architecture_pattern=ArchitecturePattern.MVVM.value,
            design_patterns=[DesignPattern.OBSERVER.value, DesignPattern.DECORATOR.value]
        )
        
        # Add some components
        for i in range(3):
            self.understanding.add_component(
                framework.framework_id,
                name=f"Component{i}",
                purpose="Test component"
            )
        
        analysis = self.understanding.analyze_architecture(framework.framework_id)
        
        self.assertIn('framework', analysis)
        self.assertIn('architecture_pattern', analysis)
        self.assertIn('complexity', analysis)
        self.assertIn('modularity', analysis)
        self.assertEqual(analysis['component_count'], 3)
    
    def test_assess_complexity(self):
        """Test complexity assessment."""
        # Simple framework
        simple_fw = {
            'components': [],
            'design_patterns': [],
            'learning_curve': 'easy'
        }
        complexity = self.understanding._assess_complexity(simple_fw)
        self.assertEqual(complexity, 'low')
        
        # Complex framework
        complex_fw = {
            'components': [{'name': f'c{i}'} for i in range(25)],
            'design_patterns': [f'p{i}' for i in range(8)],
            'learning_curve': 'very_steep'
        }
        complexity = self.understanding._assess_complexity(complex_fw)
        self.assertEqual(complexity, 'very_high')
    
    def test_assess_modularity(self):
        """Test modularity assessment."""
        # Highly modular (few dependencies)
        modular_fw = {
            'components': [
                {'dependencies': []},
                {'dependencies': ['a']},
                {'dependencies': []}
            ]
        }
        modularity = self.understanding._assess_modularity(modular_fw)
        self.assertGreater(modularity, 0.6)
        
        # Low modularity (many dependencies)
        coupled_fw = {
            'components': [
                {'dependencies': ['a', 'b', 'c', 'd']},
                {'dependencies': ['a', 'b', 'c']},
                {'dependencies': ['a', 'b']}
            ]
        }
        modularity = self.understanding._assess_modularity(coupled_fw)
        self.assertLess(modularity, 0.5)
    
    def test_assess_extensibility(self):
        """Test extensibility assessment."""
        extensible_fw = {
            'design_patterns': [
                DesignPattern.PLUGIN.value,
                DesignPattern.DECORATOR.value,
                DesignPattern.STRATEGY.value
            ],
            'integrations': {f'int{i}': 'test' for i in range(15)}
        }
        
        extensibility = self.understanding._assess_extensibility(extensible_fw)
        self.assertGreater(extensibility, 0.7)
    
    def test_map_component_relationships(self):
        """Test component relationship mapping."""
        framework = self.understanding.learn_framework(
            name="RelFramework",
            framework_type=FrameworkType.WEB_FRONTEND.value,
            version="1.0",
            description="Test",
            architecture_pattern=ArchitecturePattern.MVC.value
        )
        
        # Add components with dependencies
        self.understanding.add_component(
            framework.framework_id,
            name="Core",
            purpose="Core functionality",
            dependencies=[]
        )
        
        self.understanding.add_component(
            framework.framework_id,
            name="Router",
            purpose="Routing",
            dependencies=['Core']
        )
        
        relationships = self.understanding._map_component_relationships(framework.framework_id)
        
        self.assertIn('Core', relationships)
        self.assertIn('Router', relationships)
        self.assertEqual(relationships['Router'], ['Core'])
    
    def test_identify_patterns(self):
        """Test pattern identification."""
        framework = self.understanding.learn_framework(
            name="PatternFramework",
            framework_type=FrameworkType.WEB_BACKEND.value,
            version="1.0",
            description="Test",
            architecture_pattern=ArchitecturePattern.MVC.value,
            design_patterns=[DesignPattern.REPOSITORY.value, DesignPattern.FACTORY.value]
        )
        
        # Add component with patterns
        self.understanding.add_component(
            framework.framework_id,
            name="DataLayer",
            purpose="Data access",
            patterns_used=[DesignPattern.SINGLETON.value]
        )
        
        patterns = self.understanding.identify_patterns(framework.framework_id)
        
        self.assertGreater(len(patterns), 0)
        # Should have framework-level and component-level patterns
        levels = [p['level'] for p in patterns]
        self.assertIn('framework', levels)
        self.assertIn('component', levels)
    
    def test_compare_frameworks(self):
        """Test framework comparison."""
        fw1 = self.understanding.learn_framework(
            name="Framework1",
            framework_type=FrameworkType.WEB_FRONTEND.value,
            version="1.0",
            description="First framework",
            architecture_pattern=ArchitecturePattern.MVC.value,
            learning_curve="easy",
            community_support=0.9,
            documentation_quality=0.8
        )
        
        fw2 = self.understanding.learn_framework(
            name="Framework2",
            framework_type=FrameworkType.WEB_FRONTEND.value,
            version="1.0",
            description="Second framework",
            architecture_pattern=ArchitecturePattern.MVVM.value,
            learning_curve="steep",
            community_support=0.5,
            documentation_quality=0.6
        )
        
        comparison = self.understanding.compare_frameworks(
            [fw1.framework_id, fw2.framework_id]
        )
        
        self.assertIn('frameworks', comparison)
        self.assertIn('criteria', comparison)
        self.assertIn('winner', comparison)
        self.assertEqual(len(comparison['frameworks']), 2)
    
    def test_find_integration_strategy(self):
        """Test finding integration strategy."""
        frontend = self.understanding.learn_framework(
            name="FrontendFW",
            framework_type=FrameworkType.WEB_FRONTEND.value,
            version="1.0",
            description="Frontend",
            architecture_pattern=ArchitecturePattern.MVC.value
        )
        
        backend = self.understanding.learn_framework(
            name="BackendFW",
            framework_type=FrameworkType.WEB_BACKEND.value,
            version="1.0",
            description="Backend",
            architecture_pattern=ArchitecturePattern.LAYERED.value
        )
        
        strategy = self.understanding.find_integration_strategy(
            frontend.framework_id,
            backend.framework_id
        )
        
        self.assertIn('compatibility', strategy)
        self.assertIn('integration_points', strategy)
        self.assertIn('recommended_approach', strategy)
        self.assertEqual(strategy['compatibility'], 'high')
    
    def test_assess_compatibility(self):
        """Test compatibility assessment."""
        frontend = {'framework_type': FrameworkType.WEB_FRONTEND.value}
        backend = {'framework_type': FrameworkType.WEB_BACKEND.value}
        
        compatibility = self.understanding._assess_compatibility(frontend, backend)
        self.assertEqual(compatibility, 'high')
        
        # Same type should have low compatibility
        same_type = self.understanding._assess_compatibility(frontend, frontend)
        self.assertEqual(same_type, 'low')
    
    def test_get_best_practices(self):
        """Test getting best practices."""
        framework = self.understanding.learn_framework(
            name="PracticeFramework",
            framework_type=FrameworkType.WEB_BACKEND.value,
            version="1.0",
            description="Test",
            architecture_pattern=ArchitecturePattern.MVC.value
        )
        
        # Add practices with different importance levels
        self.understanding.add_best_practice(
            framework.framework_id,
            title="Critical Practice",
            description="Very important",
            category="security",
            importance="critical"
        )
        
        self.understanding.add_best_practice(
            framework.framework_id,
            title="Recommended Practice",
            description="Good to have",
            category="performance",
            importance="recommended"
        )
        
        # Get all practices
        all_practices = self.understanding.get_best_practices(framework.framework_id)
        self.assertEqual(len(all_practices), 2)
        
        # Get only critical
        critical = self.understanding.get_best_practices(
            framework.framework_id,
            min_importance="critical"
        )
        self.assertEqual(len(critical), 1)
        
        # Get by category
        security = self.understanding.get_best_practices(
            framework.framework_id,
            category="security"
        )
        self.assertEqual(len(security), 1)
    
    def test_detect_anti_patterns(self):
        """Test anti-pattern detection."""
        framework = self.understanding.learn_framework(
            name="AntiPatternFramework",
            framework_type=FrameworkType.WEB_FRONTEND.value,
            version="1.0",
            description="Test",
            architecture_pattern=ArchitecturePattern.MVC.value
        )
        
        # Add practice with anti-patterns
        self.understanding.add_best_practice(
            framework.framework_id,
            title="Use proper state management",
            description="Manage state correctly",
            category="architecture",
            importance="critical",
            anti_patterns=['Global mutable state', 'Prop drilling']
        )
        
        anti_patterns = self.understanding.detect_anti_patterns(framework.framework_id)
        
        self.assertGreater(len(anti_patterns), 0)
        self.assertIn('anti_pattern', anti_patterns[0])
        self.assertIn('severity', anti_patterns[0])
    
    def test_get_learning_path(self):
        """Test getting learning path."""
        framework = self.understanding.learn_framework(
            name="LearnFramework",
            framework_type=FrameworkType.WEB_FRONTEND.value,
            version="1.0",
            description="Test",
            architecture_pattern=ArchitecturePattern.MVC.value,
            core_concepts=['components', 'routing', 'state', 'lifecycle'],
            learning_curve="moderate"
        )
        
        path = self.understanding.get_learning_path(framework.framework_id)
        
        self.assertIn('framework', path)
        self.assertIn('difficulty', path)
        self.assertIn('prerequisites', path)
        self.assertIn('learning_stages', path)
        self.assertGreater(len(path['learning_stages']), 0)
    
    def test_identify_prerequisites(self):
        """Test prerequisite identification."""
        frontend_fw = {'framework_type': FrameworkType.WEB_FRONTEND.value}
        prereqs = self.understanding._identify_prerequisites(frontend_fw)
        self.assertIn('JavaScript', prereqs)
        
        ml_fw = {'framework_type': FrameworkType.MACHINE_LEARNING.value}
        ml_prereqs = self.understanding._identify_prerequisites(ml_fw)
        self.assertIn('Python', ml_prereqs)
    
    def test_get_framework_summary(self):
        """Test getting framework summary."""
        framework = self.understanding.learn_framework(
            name="SummaryFramework",
            framework_type=FrameworkType.WEB_BACKEND.value,
            version="2.0",
            description="A comprehensive framework",
            architecture_pattern=ArchitecturePattern.LAYERED.value,
            core_concepts=['routing', 'middleware'],
            design_patterns=[DesignPattern.REPOSITORY.value],
            learning_curve="moderate",
            strengths=['Fast', 'Scalable'],
            weaknesses=['Complex setup']
        )
        
        summary = self.understanding.get_framework_summary(framework.framework_id)
        
        self.assertEqual(summary['name'], 'SummaryFramework')
        self.assertEqual(summary['version'], '2.0')
        self.assertIn('complexity', summary)
        self.assertIn('strengths', summary)
        self.assertIn('weaknesses', summary)
    
    def test_persistence(self):
        """Test that data persists across instances."""
        framework = self.understanding.learn_framework(
            name="PersistentFramework",
            framework_type=FrameworkType.WEB_FRONTEND.value,
            version="1.0",
            description="Test persistence",
            architecture_pattern=ArchitecturePattern.MVC.value
        )
        
        # Create new instance
        understanding2 = FrameworkUnderstanding(data_dir=self.test_dir)
        
        # Should load saved data
        self.assertIn(framework.framework_id, understanding2.frameworks)
        loaded = understanding2.frameworks[framework.framework_id]
        self.assertEqual(loaded['name'], 'PersistentFramework')
    
    def test_learning_log(self):
        """Test that learning activities are logged."""
        initial_log_length = len(self.understanding.learning_log)
        
        self.understanding.learn_framework(
            name="LoggedFramework",
            framework_type=FrameworkType.WEB_FRONTEND.value,
            version="1.0",
            description="Test",
            architecture_pattern=ArchitecturePattern.MVC.value
        )
        
        self.assertGreater(len(self.understanding.learning_log), initial_log_length)


if __name__ == '__main__':
    unittest.main()
