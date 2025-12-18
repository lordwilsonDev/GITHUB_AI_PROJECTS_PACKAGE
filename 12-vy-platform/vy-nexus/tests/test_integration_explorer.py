#!/usr/bin/env python3
"""
Tests for Integration Explorer

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

from technical_learning.integration_explorer import (
    IntegrationExplorer,
    IntegrationType,
    AuthMethod,
    DataFormat,
    Endpoint,
    Integration,
    IntegrationPattern,
    IntegrationChain
)


class TestIntegrationExplorer(unittest.TestCase):
    """Test cases for IntegrationExplorer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.explorer = IntegrationExplorer(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test explorer initialization."""
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertIsInstance(self.explorer.integrations, dict)
        
        # Should have common integrations initialized
        self.assertGreater(len(self.explorer.integrations), 0)
    
    def test_explore_integration(self):
        """Test exploring a new integration."""
        integration = self.explorer.explore_integration(
            name="TestAPI",
            platform="TestPlatform",
            integration_type=IntegrationType.REST_API.value,
            description="A test API",
            base_url="https://api.test.com",
            auth_method=AuthMethod.API_KEY.value
        )
        
        self.assertIsInstance(integration, Integration)
        self.assertEqual(integration.name, "TestAPI")
        self.assertIn(integration.integration_id, self.explorer.integrations)
    
    def test_explore_integration_with_capabilities(self):
        """Test exploring integration with capabilities."""
        integration = self.explorer.explore_integration(
            name="CapabilityAPI",
            platform="TestPlatform",
            integration_type=IntegrationType.REST_API.value,
            description="API with capabilities",
            capabilities=['read', 'write', 'delete']
        )
        
        self.assertEqual(len(integration.capabilities), 3)
    
    def test_add_endpoint(self):
        """Test adding an endpoint to an integration."""
        integration = self.explorer.explore_integration(
            name="EndpointAPI",
            platform="TestPlatform",
            integration_type=IntegrationType.REST_API.value,
            description="API for endpoint testing"
        )
        
        endpoint = self.explorer.add_endpoint(
            integration.integration_id,
            path="/users",
            method="GET",
            description="Get users",
            parameters=[{'name': 'limit', 'type': 'integer'}]
        )
        
        self.assertIsInstance(endpoint, Endpoint)
        self.assertEqual(endpoint.path, "/users")
        self.assertIn(endpoint.endpoint_id, self.explorer.endpoints)
        self.assertIn(endpoint.endpoint_id, 
                     self.explorer.integrations[integration.integration_id]['endpoints'])
    
    def test_add_endpoint_invalid_integration(self):
        """Test adding endpoint to non-existent integration."""
        with self.assertRaises(ValueError):
            self.explorer.add_endpoint(
                "invalid_id",
                path="/test",
                method="GET",
                description="Test"
            )
    
    def test_discover_pattern(self):
        """Test discovering an integration pattern."""
        pattern = self.explorer.discover_pattern(
            name="Request-Response",
            description="Simple request-response pattern",
            use_cases=['API calls', 'Data retrieval'],
            advantages=['Simple', 'Widely supported'],
            disadvantages=['Not real-time']
        )
        
        self.assertIsInstance(pattern, IntegrationPattern)
        self.assertEqual(pattern.name, "Request-Response")
        self.assertIn(pattern.pattern_id, self.explorer.patterns)
    
    def test_create_integration_chain(self):
        """Test creating an integration chain."""
        # Create two integrations
        int1 = self.explorer.explore_integration(
            name="API1",
            platform="Platform1",
            integration_type=IntegrationType.REST_API.value,
            description="First API"
        )
        
        int2 = self.explorer.explore_integration(
            name="API2",
            platform="Platform2",
            integration_type=IntegrationType.REST_API.value,
            description="Second API"
        )
        
        # Create chain
        chain = self.explorer.create_integration_chain(
            name="TestChain",
            description="Chain of two APIs",
            integration_ids=[int1.integration_id, int2.integration_id],
            data_flow=[
                {'from': int1.integration_id, 'to': int2.integration_id, 'data': 'user_data'}
            ]
        )
        
        self.assertIsInstance(chain, IntegrationChain)
        self.assertEqual(len(chain.integrations), 2)
        self.assertIn(chain.chain_id, self.explorer.chains)
    
    def test_create_chain_invalid_integration(self):
        """Test creating chain with invalid integration."""
        with self.assertRaises(ValueError):
            self.explorer.create_integration_chain(
                name="InvalidChain",
                description="Test",
                integration_ids=["invalid_id"],
                data_flow=[]
            )
    
    def test_find_integrations_by_platform(self):
        """Test finding integrations by platform."""
        # Create integrations on different platforms
        self.explorer.explore_integration(
            name="GitHub Test",
            platform="GitHub",
            integration_type=IntegrationType.REST_API.value,
            description="Test"
        )
        
        results = self.explorer.find_integrations(platform="GitHub")
        
        self.assertGreater(len(results), 0)
        for result in results:
            self.assertEqual(result['platform'], "GitHub")
    
    def test_find_integrations_by_type(self):
        """Test finding integrations by type."""
        results = self.explorer.find_integrations(
            integration_type=IntegrationType.REST_API.value
        )
        
        self.assertGreater(len(results), 0)
        for result in results:
            self.assertEqual(result['integration_type'], IntegrationType.REST_API.value)
    
    def test_find_integrations_by_capability(self):
        """Test finding integrations by capability."""
        self.explorer.explore_integration(
            name="CapTest",
            platform="Test",
            integration_type=IntegrationType.REST_API.value,
            description="Test",
            capabilities=['special_feature']
        )
        
        results = self.explorer.find_integrations(capability='special_feature')
        
        self.assertGreater(len(results), 0)
        for result in results:
            self.assertIn('special_feature', result['capabilities'])
    
    def test_find_integrations_by_reliability(self):
        """Test finding integrations by minimum reliability."""
        results = self.explorer.find_integrations(min_reliability=0.7)
        
        for result in results:
            self.assertGreaterEqual(result['reliability_score'], 0.7)
    
    def test_recommend_integration(self):
        """Test integration recommendation."""
        # Create integration with specific capabilities
        self.explorer.explore_integration(
            name="RecommendTest",
            platform="Test",
            integration_type=IntegrationType.REST_API.value,
            description="Test",
            capabilities=['messaging', 'notifications'],
            reliability_score=0.9,
            ease_of_use=0.8
        )
        
        recommendations = self.explorer.recommend_integration(
            use_case="Send notifications",
            requirements=['messaging', 'notifications']
        )
        
        self.assertIsInstance(recommendations, list)
        if len(recommendations) > 0:
            self.assertIn('recommendation_score', recommendations[0])
            self.assertIn('matching_capabilities', recommendations[0])
    
    def test_analyze_integration(self):
        """Test integration analysis."""
        integration = self.explorer.explore_integration(
            name="AnalyzeTest",
            platform="Test",
            integration_type=IntegrationType.REST_API.value,
            description="Test",
            sdk_available=True,
            real_time_updates=True
        )
        
        # Add some endpoints
        for i in range(3):
            self.explorer.add_endpoint(
                integration.integration_id,
                path=f"/endpoint{i}",
                method="GET",
                description=f"Endpoint {i}"
            )
        
        analysis = self.explorer.analyze_integration(integration.integration_id)
        
        self.assertIn('complexity', analysis)
        self.assertIn('completeness', analysis)
        self.assertIn('endpoint_count', analysis)
        self.assertEqual(analysis['endpoint_count'], 3)
        self.assertTrue(analysis['has_sdk'])
        self.assertTrue(analysis['real_time_capable'])
    
    def test_assess_complexity(self):
        """Test complexity assessment."""
        # Simple integration
        simple_int = {
            'auth_method': AuthMethod.API_KEY.value,
            'webhooks_supported': False,
            'real_time_updates': False
        }
        complexity = self.explorer._assess_integration_complexity(simple_int, [])
        self.assertEqual(complexity, 'low')
        
        # Complex integration
        complex_int = {
            'auth_method': AuthMethod.OAUTH2.value,
            'webhooks_supported': True,
            'real_time_updates': True
        }
        endpoints = [{'id': i} for i in range(60)]
        complexity = self.explorer._assess_integration_complexity(complex_int, endpoints)
        self.assertIn(complexity, ['high', 'very_high'])
    
    def test_assess_completeness(self):
        """Test completeness assessment."""
        # Complete integration
        complete_int = {
            'base_url': 'https://api.test.com',
            'documentation_url': 'https://docs.test.com',
            'capabilities': ['read', 'write'],
            'endpoints': ['ep1', 'ep2'],
            'sdk_available': True,
            'rate_limits': {'per_hour': 1000}
        }
        completeness = self.explorer._assess_completeness(complete_int)
        self.assertGreater(completeness, 0.8)
        
        # Incomplete integration
        incomplete_int = {
            'base_url': None,
            'documentation_url': None,
            'capabilities': [],
            'endpoints': []
        }
        completeness = self.explorer._assess_completeness(incomplete_int)
        self.assertLess(completeness, 0.3)
    
    def test_test_integration_success(self):
        """Test recording successful integration test."""
        integration = self.explorer.explore_integration(
            name="TestSuccess",
            platform="Test",
            integration_type=IntegrationType.REST_API.value,
            description="Test"
        )
        
        initial_usage = integration.usage_count
        initial_reliability = integration.reliability_score
        
        self.explorer.test_integration(
            integration.integration_id,
            success=True,
            response_time=0.5
        )
        
        updated = self.explorer.integrations[integration.integration_id]
        self.assertEqual(updated['usage_count'], initial_usage + 1)
        self.assertIsNotNone(updated['last_used'])
    
    def test_test_integration_failure(self):
        """Test recording failed integration test."""
        integration = self.explorer.explore_integration(
            name="TestFailure",
            platform="Test",
            integration_type=IntegrationType.REST_API.value,
            description="Test"
        )
        
        # Record multiple successes first
        for _ in range(5):
            self.explorer.test_integration(integration.integration_id, success=True)
        
        success_rate_before = self.explorer.integrations[integration.integration_id]['success_rate']
        
        # Record failure
        self.explorer.test_integration(integration.integration_id, success=False)
        
        success_rate_after = self.explorer.integrations[integration.integration_id]['success_rate']
        self.assertLess(success_rate_after, success_rate_before)
    
    def test_get_integration_chains(self):
        """Test getting integration chains."""
        # Create integrations and chain
        int1 = self.explorer.explore_integration(
            name="ChainAPI1",
            platform="Test",
            integration_type=IntegrationType.REST_API.value,
            description="Test"
        )
        
        int2 = self.explorer.explore_integration(
            name="ChainAPI2",
            platform="Test",
            integration_type=IntegrationType.REST_API.value,
            description="Test"
        )
        
        self.explorer.create_integration_chain(
            name="TestChain",
            description="Test",
            integration_ids=[int1.integration_id, int2.integration_id],
            data_flow=[]
        )
        
        # Get all chains
        chains = self.explorer.get_integration_chains()
        self.assertGreater(len(chains), 0)
        
        # Get chains for specific integration
        chains_for_int1 = self.explorer.get_integration_chains(
            integration_id=int1.integration_id
        )
        self.assertGreater(len(chains_for_int1), 0)
    
    def test_get_exploration_summary(self):
        """Test getting exploration summary."""
        summary = self.explorer.get_exploration_summary()
        
        self.assertIn('total_integrations', summary)
        self.assertIn('total_endpoints', summary)
        self.assertIn('total_patterns', summary)
        self.assertIn('total_chains', summary)
        self.assertIn('integrations_by_type', summary)
        self.assertIn('integrations_by_platform', summary)
        
        self.assertGreater(summary['total_integrations'], 0)
    
    def test_persistence(self):
        """Test that data persists across instances."""
        integration = self.explorer.explore_integration(
            name="PersistTest",
            platform="Test",
            integration_type=IntegrationType.REST_API.value,
            description="Test persistence"
        )
        
        # Create new instance
        explorer2 = IntegrationExplorer(data_dir=self.test_dir)
        
        # Should load saved data
        self.assertIn(integration.integration_id, explorer2.integrations)
        loaded = explorer2.integrations[integration.integration_id]
        self.assertEqual(loaded['name'], 'PersistTest')
    
    def test_exploration_log(self):
        """Test that exploration activities are logged."""
        initial_log_length = len(self.explorer.exploration_log)
        
        self.explorer.explore_integration(
            name="LogTest",
            platform="Test",
            integration_type=IntegrationType.REST_API.value,
            description="Test"
        )
        
        self.assertGreater(len(self.explorer.exploration_log), initial_log_length)


if __name__ == '__main__':
    unittest.main()
