#!/usr/bin/env python3
"""
Phase 7 Integration Tests - Technical Learning System

Tests the integration of all Phase 7 components:
- Programming Language Learner
- Tool Research System
- Framework Understanding Module
- Integration Explorer

Author: Vy-Nexus Self-Evolving AI
Created: December 15, 2025
"""

import unittest
import os
import tempfile
import shutil
import sys
import time

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from technical_learning.programming_language_learner import (
    ProgrammingLanguageLearner,
    ProgrammingLanguage
)
from technical_learning.tool_research_system import (
    ToolResearchSystem,
    ToolCategory,
    MaturityLevel
)
from technical_learning.framework_understanding import (
    FrameworkUnderstanding,
    FrameworkType,
    ArchitecturePattern,
    DesignPattern
)
from technical_learning.integration_explorer import (
    IntegrationExplorer,
    IntegrationType,
    AuthMethod
)


class TestPhase7Integration(unittest.TestCase):
    """Integration tests for Phase 7 Technical Learning System."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        
        # Initialize all Phase 7 components
        self.language_learner = ProgrammingLanguageLearner(
            data_dir=os.path.join(self.test_dir, 'languages')
        )
        self.tool_research = ToolResearchSystem(
            data_dir=os.path.join(self.test_dir, 'tools')
        )
        self.framework_understanding = FrameworkUnderstanding(
            data_dir=os.path.join(self.test_dir, 'frameworks')
        )
        self.integration_explorer = IntegrationExplorer(
            data_dir=os.path.join(self.test_dir, 'integrations')
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_all_components_initialized(self):
        """Test that all Phase 7 components initialize correctly."""
        self.assertIsNotNone(self.language_learner)
        self.assertIsNotNone(self.tool_research)
        self.assertIsNotNone(self.framework_understanding)
        self.assertIsNotNone(self.integration_explorer)
        
        # Verify data directories exist
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'languages')))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'tools')))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'frameworks')))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'integrations')))
    
    def test_web_development_learning_workflow(self):
        """Test complete workflow for learning web development stack."""
        # Step 1: Learn JavaScript
        js_lang = self.language_learner.learn_language(
            name="JavaScript",
            paradigms=["object-oriented", "functional"],
            typing="dynamic",
            use_cases=["web_frontend", "web_backend"],
            difficulty="moderate"
        )
        
        # Step 2: Research web development tools
        webpack_tool = self.tool_research.research_tool(
            name="Webpack",
            category=ToolCategory.BUILD_TOOLS.value,
            description="Module bundler",
            maturity_level=MaturityLevel.MATURE.value,
            use_cases=["bundling", "optimization"]
        )
        
        # Step 3: Learn React framework
        react_fw = self.framework_understanding.learn_framework(
            name="React",
            framework_type=FrameworkType.WEB_FRONTEND.value,
            version="18.0",
            description="UI library",
            architecture_pattern=ArchitecturePattern.COMPONENT_BASED.value,
            core_concepts=["components", "hooks", "state"],
            design_patterns=[DesignPattern.OBSERVER.value]
        )
        
        # Step 4: Explore integrations
        api_integration = self.integration_explorer.explore_integration(
            platform="REST API",
            integration_type=IntegrationType.REST_API.value,
            auth_method=AuthMethod.BEARER_TOKEN.value,
            capabilities=["data_fetch", "data_update"]
        )
        
        # Verify complete workflow
        self.assertEqual(js_lang.name, "JavaScript")
        self.assertEqual(webpack_tool.name, "Webpack")
        self.assertEqual(react_fw.name, "React")
        self.assertEqual(api_integration.platform, "REST API")
        
        # Verify relationships
        self.assertIn("web_frontend", js_lang.use_cases)
        self.assertEqual(react_fw.framework_type, FrameworkType.WEB_FRONTEND.value)
    
    def test_python_ml_stack_workflow(self):
        """Test learning Python ML/AI development stack."""
        # Learn Python
        python = self.language_learner.learn_language(
            name="Python",
            paradigms=["object-oriented", "functional"],
            typing="dynamic",
            use_cases=["data_science", "machine_learning"],
            difficulty="easy"
        )
        
        # Research ML tools
        jupyter = self.tool_research.research_tool(
            name="Jupyter",
            category=ToolCategory.DATA_SCIENCE.value,
            description="Interactive notebooks",
            maturity_level=MaturityLevel.MATURE.value
        )
        
        # Learn TensorFlow
        tensorflow = self.framework_understanding.learn_framework(
            name="TensorFlow",
            framework_type=FrameworkType.MACHINE_LEARNING.value,
            version="2.0",
            description="ML framework",
            architecture_pattern=ArchitecturePattern.LAYERED.value
        )
        
        # Explore cloud ML integrations
        aws_ml = self.integration_explorer.explore_integration(
            platform="AWS SageMaker",
            integration_type=IntegrationType.SDK.value,
            auth_method=AuthMethod.API_KEY.value,
            capabilities=["model_training", "deployment"]
        )
        
        # Verify stack coherence
        self.assertIn("machine_learning", python.use_cases)
        self.assertEqual(jupyter.category, ToolCategory.DATA_SCIENCE.value)
        self.assertEqual(tensorflow.framework_type, FrameworkType.MACHINE_LEARNING.value)
        self.assertIn("model_training", aws_ml.capabilities)
    
    def test_cross_component_data_flow(self):
        """Test data flows correctly between components."""
        # Learn TypeScript
        typescript = self.language_learner.learn_language(
            name="TypeScript",
            paradigms=["object-oriented"],
            typing="static",
            use_cases=["web_development"]
        )
        
        # Add code sample
        self.language_learner.add_code_sample(
            typescript.language_id,
            "interface User { name: string; }",
            "Type definition",
            "best_practice"
        )
        
        # Research TypeScript tools based on language
        ts_tools = self.tool_research.recommend_tool(
            use_case="web_development",
            category=ToolCategory.DEVELOPMENT.value
        )
        
        # Learn framework that uses TypeScript
        angular = self.framework_understanding.learn_framework(
            name="Angular",
            framework_type=FrameworkType.WEB_FRONTEND.value,
            version="15.0",
            description="TypeScript-based framework",
            architecture_pattern=ArchitecturePattern.MVC.value
        )
        
        # Verify data consistency
        self.assertEqual(typescript.typing, "static")
        self.assertIsInstance(ts_tools, list)
        self.assertEqual(angular.framework_type, FrameworkType.WEB_FRONTEND.value)
    
    def test_recommendation_pipeline(self):
        """Test recommendation pipeline across components."""
        # Scenario: User wants to build a web API
        
        # Step 1: Get language recommendations
        # (In real system, would query based on use case)
        python = self.language_learner.learn_language(
            name="Python",
            paradigms=["object-oriented"],
            typing="dynamic",
            use_cases=["web_backend"],
            difficulty="easy"
        )
        
        # Step 2: Get tool recommendations
        tools = self.tool_research.recommend_tool(
            use_case="web_backend",
            category=ToolCategory.DEVELOPMENT.value
        )
        
        # Step 3: Get framework recommendations
        # Learn some frameworks first
        flask = self.framework_understanding.learn_framework(
            name="Flask",
            framework_type=FrameworkType.WEB_BACKEND.value,
            version="2.0",
            description="Micro web framework",
            architecture_pattern=ArchitecturePattern.MVC.value,
            learning_curve="easy"
        )
        
        django = self.framework_understanding.learn_framework(
            name="Django",
            framework_type=FrameworkType.WEB_BACKEND.value,
            version="4.0",
            description="Full-stack framework",
            architecture_pattern=ArchitecturePattern.MVT.value,
            learning_curve="moderate"
        )
        
        # Compare frameworks
        comparison = self.framework_understanding.compare_frameworks(
            [flask.framework_id, django.framework_id]
        )
        
        # Step 4: Get integration recommendations
        integrations = self.integration_explorer.find_integrations(
            platform_filter="database"
        )
        
        # Verify recommendation pipeline
        self.assertIn("web_backend", python.use_cases)
        self.assertIsInstance(tools, list)
        self.assertIn('winner', comparison)
        self.assertIsInstance(integrations, list)
    
    def test_learning_progression(self):
        """Test learning progression from basics to advanced."""
        # Beginner: Learn JavaScript basics
        js = self.language_learner.learn_language(
            name="JavaScript",
            paradigms=["object-oriented"],
            typing="dynamic",
            use_cases=["web_frontend"],
            difficulty="moderate"
        )
        
        # Add beginner pattern
        self.language_learner.add_pattern(
            js.language_id,
            "Variables",
            "let x = 5;",
            "basic"
        )
        
        # Intermediate: Learn build tools
        npm = self.tool_research.research_tool(
            name="npm",
            category=ToolCategory.PACKAGE_MANAGER.value,
            description="Package manager",
            maturity_level=MaturityLevel.MATURE.value,
            learning_curve="easy"
        )
        
        # Advanced: Learn framework
        vue = self.framework_understanding.learn_framework(
            name="Vue",
            framework_type=FrameworkType.WEB_FRONTEND.value,
            version="3.0",
            description="Progressive framework",
            architecture_pattern=ArchitecturePattern.MVVM.value,
            learning_curve="moderate"
        )
        
        # Expert: Complex integrations
        graphql = self.integration_explorer.explore_integration(
            platform="GraphQL API",
            integration_type=IntegrationType.GRAPHQL.value,
            auth_method=AuthMethod.BEARER_TOKEN.value,
            capabilities=["query", "mutation", "subscription"]
        )
        
        # Verify progression
        self.assertEqual(js.difficulty, "moderate")
        self.assertEqual(npm.learning_curve, "easy")
        self.assertEqual(vue.learning_curve, "moderate")
        self.assertEqual(len(graphql.capabilities), 3)
    
    def test_migration_scenario(self):
        """Test framework migration scenario."""
        # Current stack: React
        react = self.framework_understanding.learn_framework(
            name="React",
            framework_type=FrameworkType.WEB_FRONTEND.value,
            version="18.0",
            description="UI library",
            architecture_pattern=ArchitecturePattern.COMPONENT_BASED.value
        )
        
        # Target stack: Vue
        vue = self.framework_understanding.learn_framework(
            name="Vue",
            framework_type=FrameworkType.WEB_FRONTEND.value,
            version="3.0",
            description="Progressive framework",
            architecture_pattern=ArchitecturePattern.MVVM.value
        )
        
        # Create migration path
        migration = self.framework_understanding.create_migration_path(
            from_framework="React",
            to_framework="Vue",
            difficulty="moderate",
            estimated_effort="2-4 weeks",
            key_differences=["reactivity", "templates"],
            migration_steps=["Learn Vue basics", "Convert components"]
        )
        
        # Research migration tools
        migration_tools = self.tool_research.recommend_tool(
            use_case="migration",
            category=ToolCategory.DEVELOPMENT.value
        )
        
        # Verify migration plan
        self.assertEqual(migration.from_framework, "React")
        self.assertEqual(migration.to_framework, "Vue")
        self.assertEqual(len(migration.migration_steps), 2)
    
    def test_performance_benchmarking(self):
        """Test performance of integrated system."""
        start_time = time.time()
        
        # Perform multiple operations
        for i in range(5):
            # Learn language
            lang = self.language_learner.learn_language(
                name=f"Lang{i}",
                paradigms=["object-oriented"],
                typing="static",
                use_cases=["general"]
            )
            
            # Research tool
            tool = self.tool_research.research_tool(
                name=f"Tool{i}",
                category=ToolCategory.DEVELOPMENT.value,
                description="Test tool"
            )
            
            # Learn framework
            fw = self.framework_understanding.learn_framework(
                name=f"Framework{i}",
                framework_type=FrameworkType.WEB_FRONTEND.value,
                version="1.0",
                description="Test",
                architecture_pattern=ArchitecturePattern.MVC.value
            )
            
            # Explore integration
            integration = self.integration_explorer.explore_integration(
                platform=f"Platform{i}",
                integration_type=IntegrationType.REST_API.value,
                auth_method=AuthMethod.API_KEY.value
            )
        
        elapsed_time = time.time() - start_time
        
        # Should complete reasonably fast (< 5 seconds for 5 iterations)
        self.assertLess(elapsed_time, 5.0)
        
        # Verify all data was stored
        self.assertEqual(len(self.language_learner.languages), 5)
        self.assertGreaterEqual(len(self.tool_research.tools), 5)
        self.assertGreaterEqual(len(self.framework_understanding.frameworks), 5)
        self.assertGreaterEqual(len(self.integration_explorer.integrations), 5)
    
    def test_error_handling_across_components(self):
        """Test error handling in integrated scenarios."""
        # Test invalid language ID
        with self.assertRaises(ValueError):
            self.language_learner.add_pattern(
                "invalid_id",
                "Pattern",
                "code",
                "basic"
            )
        
        # Test invalid tool ID
        with self.assertRaises(ValueError):
            self.tool_research.update_tool_info(
                "invalid_id",
                {"version": "2.0"}
            )
        
        # Test invalid framework ID
        with self.assertRaises(ValueError):
            self.framework_understanding.add_component(
                "invalid_id",
                name="Component",
                purpose="Test"
            )
        
        # Test invalid integration ID
        with self.assertRaises(ValueError):
            self.integration_explorer.add_endpoint(
                "invalid_id",
                path="/test",
                method="GET"
            )
    
    def test_data_persistence_across_components(self):
        """Test that all components persist data correctly."""
        # Create data in all components
        lang = self.language_learner.learn_language(
            name="PersistLang",
            paradigms=["functional"],
            typing="static",
            use_cases=["general"]
        )
        
        tool = self.tool_research.research_tool(
            name="PersistTool",
            category=ToolCategory.DEVELOPMENT.value,
            description="Test"
        )
        
        fw = self.framework_understanding.learn_framework(
            name="PersistFramework",
            framework_type=FrameworkType.WEB_BACKEND.value,
            version="1.0",
            description="Test",
            architecture_pattern=ArchitecturePattern.MVC.value
        )
        
        integration = self.integration_explorer.explore_integration(
            platform="PersistPlatform",
            integration_type=IntegrationType.SDK.value,
            auth_method=AuthMethod.OAUTH2.value
        )
        
        # Create new instances (simulating restart)
        new_lang_learner = ProgrammingLanguageLearner(
            data_dir=os.path.join(self.test_dir, 'languages')
        )
        new_tool_research = ToolResearchSystem(
            data_dir=os.path.join(self.test_dir, 'tools')
        )
        new_fw_understanding = FrameworkUnderstanding(
            data_dir=os.path.join(self.test_dir, 'frameworks')
        )
        new_integration_explorer = IntegrationExplorer(
            data_dir=os.path.join(self.test_dir, 'integrations')
        )
        
        # Verify data was loaded
        self.assertIn(lang.language_id, new_lang_learner.languages)
        self.assertIn(tool.tool_id, new_tool_research.tools)
        self.assertIn(fw.framework_id, new_fw_understanding.frameworks)
        self.assertIn(integration.integration_id, new_integration_explorer.integrations)
    
    def test_real_world_fullstack_scenario(self):
        """Test complete real-world full-stack development scenario."""
        # Frontend: TypeScript + React
        typescript = self.language_learner.learn_language(
            name="TypeScript",
            paradigms=["object-oriented"],
            typing="static",
            use_cases=["web_frontend"]
        )
        
        react = self.framework_understanding.learn_framework(
            name="React",
            framework_type=FrameworkType.WEB_FRONTEND.value,
            version="18.0",
            description="UI library",
            architecture_pattern=ArchitecturePattern.COMPONENT_BASED.value
        )
        
        # Backend: Python + FastAPI
        python = self.language_learner.learn_language(
            name="Python",
            paradigms=["object-oriented"],
            typing="dynamic",
            use_cases=["web_backend"]
        )
        
        fastapi = self.framework_understanding.learn_framework(
            name="FastAPI",
            framework_type=FrameworkType.WEB_BACKEND.value,
            version="0.100",
            description="Modern API framework",
            architecture_pattern=ArchitecturePattern.LAYERED.value
        )
        
        # Database integration
        postgres = self.integration_explorer.explore_integration(
            platform="PostgreSQL",
            integration_type=IntegrationType.DATABASE.value,
            auth_method=AuthMethod.USERNAME_PASSWORD.value,
            capabilities=["read", "write", "transactions"]
        )
        
        # API integration between frontend and backend
        rest_api = self.integration_explorer.explore_integration(
            platform="REST API",
            integration_type=IntegrationType.REST_API.value,
            auth_method=AuthMethod.BEARER_TOKEN.value,
            capabilities=["CRUD"]
        )
        
        # Build tools
        vite = self.tool_research.research_tool(
            name="Vite",
            category=ToolCategory.BUILD_TOOLS.value,
            description="Frontend build tool",
            maturity_level=MaturityLevel.STABLE.value
        )
        
        # Create integration chain
        chain = self.integration_explorer.create_integration_chain(
            name="Full Stack App",
            description="React frontend -> FastAPI backend -> PostgreSQL",
            integrations=[
                rest_api.integration_id,
                postgres.integration_id
            ]
        )
        
        # Verify complete stack
        self.assertEqual(typescript.typing, "static")
        self.assertEqual(react.framework_type, FrameworkType.WEB_FRONTEND.value)
        self.assertEqual(python.typing, "dynamic")
        self.assertEqual(fastapi.framework_type, FrameworkType.WEB_BACKEND.value)
        self.assertIn("transactions", postgres.capabilities)
        self.assertEqual(len(chain.integrations), 2)
        self.assertEqual(vite.category, ToolCategory.BUILD_TOOLS.value)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
