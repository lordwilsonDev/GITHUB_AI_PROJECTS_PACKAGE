#!/usr/bin/env python3
"""
Tests for Tool Research System

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

from technical_learning.tool_research_system import (
    ToolResearchSystem,
    ToolCategory,
    MaturityLevel,
    ToolFeature,
    ToolProfile,
    ToolComparison
)


class TestToolResearchSystem(unittest.TestCase):
    """Test cases for ToolResearchSystem."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.research = ToolResearchSystem(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test research system initialization."""
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertIsInstance(self.research.tools, dict)
        self.assertIsInstance(self.research.comparisons, dict)
        
        # Should have common tools initialized
        self.assertGreater(len(self.research.tools), 0)
    
    def test_research_tool(self):
        """Test researching a new tool."""
        tool = self.research.research_tool(
            name="TestTool",
            category=ToolCategory.DEVELOPMENT.value,
            description="A test tool",
            maturity_level=MaturityLevel.STABLE.value,
            use_cases=['testing', 'development']
        )
        
        self.assertIsInstance(tool, ToolProfile)
        self.assertEqual(tool.name, "TestTool")
        self.assertIn(tool.tool_id, self.research.tools)
    
    def test_research_tool_with_features(self):
        """Test researching a tool with features."""
        features = [
            {'name': 'feature1', 'description': 'First feature', 'importance': 'critical'},
            {'name': 'feature2', 'description': 'Second feature', 'importance': 'important'}
        ]
        
        tool = self.research.research_tool(
            name="FeatureTool",
            category=ToolCategory.TESTING.value,
            description="Tool with features",
            features=features
        )
        
        self.assertEqual(len(tool.features), 2)
    
    def test_update_tool_info(self):
        """Test updating tool information."""
        tool = self.research.research_tool(
            name="UpdateTool",
            category=ToolCategory.DEVELOPMENT.value,
            description="Original description"
        )
        
        self.research.update_tool_info(
            tool.tool_id,
            {'description': 'Updated description', 'version': '2.0'}
        )
        
        updated = self.research.tools[tool.tool_id]
        self.assertEqual(updated['description'], 'Updated description')
        self.assertEqual(updated['version'], '2.0')
    
    def test_add_tool_feature(self):
        """Test adding a feature to a tool."""
        tool = self.research.research_tool(
            name="FeatureAddTool",
            category=ToolCategory.DEVELOPMENT.value,
            description="Test"
        )
        
        initial_features = len(tool.features)
        
        self.research.add_tool_feature(
            tool.tool_id,
            'new_feature',
            'A new feature',
            'important'
        )
        
        updated = self.research.tools[tool.tool_id]
        self.assertEqual(len(updated['features']), initial_features + 1)
    
    def test_compare_tools(self):
        """Test comparing tools."""
        tool1 = self.research.research_tool(
            name="Tool1",
            category=ToolCategory.DEVELOPMENT.value,
            description="First tool"
        )
        
        tool2 = self.research.research_tool(
            name="Tool2",
            category=ToolCategory.DEVELOPMENT.value,
            description="Second tool"
        )
        
        comparison = self.research.compare_tools([tool1.tool_id, tool2.tool_id])
        
        self.assertIsInstance(comparison, ToolComparison)
        self.assertEqual(len(comparison.tools), 2)
        self.assertIsNotNone(comparison.winner)
    
    def test_find_alternatives(self):
        """Test finding alternative tools."""
        # Create tools with similar use cases
        tool1 = self.research.research_tool(
            name="MainTool",
            category=ToolCategory.TESTING.value,
            description="Main tool",
            use_cases=['unit_testing', 'integration_testing']
        )
        
        tool2 = self.research.research_tool(
            name="Alternative1",
            category=ToolCategory.TESTING.value,
            description="Alternative",
            use_cases=['unit_testing', 'mocking']
        )
        
        alternatives = self.research.find_alternatives(tool1.tool_id)
        
        self.assertIsInstance(alternatives, list)
        if len(alternatives) > 0:
            self.assertIn('name', alternatives[0])
            self.assertIn('similarity', alternatives[0])
    
    def test_track_trend(self):
        """Test tracking technology trends."""
        self.research.track_trend(
            'AI Agents',
            ToolCategory.AI_ML.value
        )
        
        self.assertGreater(len(self.research.trends), 0)
        
        # Track again to increase mentions
        self.research.track_trend(
            'AI Agents',
            ToolCategory.AI_ML.value
        )
        
        # Find the trend
        trend = next(t for t in self.research.trends.values() 
                    if t['technology'] == 'AI Agents')
        
        self.assertEqual(trend['mentions'], 2)
    
    def test_recommend_tool(self):
        """Test tool recommendation."""
        # Create tools for testing
        self.research.research_tool(
            name="TestingTool1",
            category=ToolCategory.TESTING.value,
            description="Testing tool",
            use_cases=['unit_testing'],
            maturity_level=MaturityLevel.MATURE.value
        )
        
        recommendations = self.research.recommend_tool(
            use_case='unit_testing',
            category=ToolCategory.TESTING.value
        )
        
        self.assertIsInstance(recommendations, list)
        if len(recommendations) > 0:
            self.assertIn('name', recommendations[0])
            self.assertIn('recommendation_score', recommendations[0])
    
    def test_recommend_tool_with_constraints(self):
        """Test tool recommendation with constraints."""
        # Create tools with different maturity levels
        self.research.research_tool(
            name="MatureTool",
            category=ToolCategory.DEVELOPMENT.value,
            description="Mature tool",
            use_cases=['coding'],
            maturity_level=MaturityLevel.MATURE.value
        )
        
        self.research.research_tool(
            name="BetaTool",
            category=ToolCategory.DEVELOPMENT.value,
            description="Beta tool",
            use_cases=['coding'],
            maturity_level=MaturityLevel.BETA.value
        )
        
        # Recommend with maturity constraint
        recommendations = self.research.recommend_tool(
            use_case='coding',
            constraints={'min_maturity': MaturityLevel.STABLE.value}
        )
        
        # Should only include mature/stable tools
        for rec in recommendations:
            tool = self.research.tools[rec['tool_id']]
            self.assertIn(tool['maturity_level'], 
                         [MaturityLevel.MATURE.value, MaturityLevel.STABLE.value])
    
    def test_record_tool_usage(self):
        """Test recording tool usage."""
        tool = self.research.research_tool(
            name="UsageTool",
            category=ToolCategory.DEVELOPMENT.value,
            description="Test"
        )
        
        initial_usage = tool.usage_count
        initial_score = tool.recommendation_score
        
        self.research.record_tool_usage(tool.tool_id, success=True)
        
        updated = self.research.tools[tool.tool_id]
        self.assertEqual(updated['usage_count'], initial_usage + 1)
        self.assertGreater(updated['recommendation_score'], initial_score)
    
    def test_record_tool_usage_failure(self):
        """Test recording failed tool usage."""
        tool = self.research.research_tool(
            name="FailTool",
            category=ToolCategory.DEVELOPMENT.value,
            description="Test"
        )
        
        initial_score = tool.recommendation_score
        
        self.research.record_tool_usage(tool.tool_id, success=False)
        
        updated = self.research.tools[tool.tool_id]
        self.assertLess(updated['recommendation_score'], initial_score)
    
    def test_recommendation_score_calculation(self):
        """Test recommendation score calculation."""
        # Mature tool with good attributes
        good_tool = ToolProfile(
            tool_id="good",
            name="GoodTool",
            category=ToolCategory.DEVELOPMENT.value,
            description="Good tool",
            version="1.0",
            maturity_level=MaturityLevel.MATURE.value,
            learning_curve="easy",
            documentation_quality=0.9,
            performance_rating=0.9,
            community_size="large"
        )
        
        # Experimental tool with poor attributes
        poor_tool = ToolProfile(
            tool_id="poor",
            name="PoorTool",
            category=ToolCategory.DEVELOPMENT.value,
            description="Poor tool",
            version="0.1",
            maturity_level=MaturityLevel.EXPERIMENTAL.value,
            learning_curve="hard",
            documentation_quality=0.2,
            performance_rating=0.3,
            community_size="small"
        )
        
        good_score = self.research._calculate_recommendation_score(good_tool)
        poor_score = self.research._calculate_recommendation_score(poor_tool)
        
        self.assertGreater(good_score, poor_score)
    
    def test_get_tool_profile(self):
        """Test getting tool profile."""
        tool = self.research.research_tool(
            name="ProfileTool",
            category=ToolCategory.DEVELOPMENT.value,
            description="Test"
        )
        
        profile = self.research.get_tool_profile(tool.tool_id)
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile['name'], 'ProfileTool')
    
    def test_get_trending_technologies(self):
        """Test getting trending technologies."""
        # Track some trends
        for i in range(5):
            self.research.track_trend(
                'TrendingTech',
                ToolCategory.AI_ML.value
            )
        
        trending = self.research.get_trending_technologies(min_momentum=0.3)
        
        self.assertIsInstance(trending, list)
        if len(trending) > 0:
            self.assertIn('technology', trending[0])
            self.assertIn('momentum', trending[0])
    
    def test_get_research_summary(self):
        """Test getting research summary."""
        summary = self.research.get_research_summary()
        
        self.assertIn('total_tools', summary)
        self.assertIn('tools_by_category', summary)
        self.assertIn('tools_by_maturity', summary)
        self.assertIn('most_used_tools', summary)
        
        self.assertGreater(summary['total_tools'], 0)
    
    def test_persistence(self):
        """Test that data persists across instances."""
        tool = self.research.research_tool(
            name="PersistentTool",
            category=ToolCategory.DEVELOPMENT.value,
            description="Test"
        )
        
        # Create new instance
        research2 = ToolResearchSystem(data_dir=self.test_dir)
        
        # Should load saved data
        profile = research2.get_tool_profile(tool.tool_id)
        self.assertIsNotNone(profile)
        self.assertEqual(profile['name'], 'PersistentTool')
    
    def test_comparison_with_criteria(self):
        """Test tool comparison with specific criteria."""
        tool1 = self.research.research_tool(
            name="FastTool",
            category=ToolCategory.DEVELOPMENT.value,
            description="Fast tool"
        )
        
        tool2 = self.research.research_tool(
            name="SlowTool",
            category=ToolCategory.DEVELOPMENT.value,
            description="Slow tool"
        )
        
        # Update performance ratings
        self.research.update_tool_info(
            tool1.tool_id,
            {'performance_rating': 0.9}
        )
        self.research.update_tool_info(
            tool2.tool_id,
            {'performance_rating': 0.3}
        )
        
        comparison = self.research.compare_tools(
            [tool1.tool_id, tool2.tool_id],
            criteria=['performance_rating']
        )
        
        self.assertIn('performance_rating', comparison.criteria)
    
    def test_research_log(self):
        """Test that research activities are logged."""
        initial_log_length = len(self.research.research_log)
        
        self.research.research_tool(
            name="LoggedTool",
            category=ToolCategory.DEVELOPMENT.value,
            description="Test"
        )
        
        self.assertGreater(len(self.research.research_log), initial_log_length)


class TestToolFeature(unittest.TestCase):
    """Test cases for ToolFeature dataclass."""
    
    def test_feature_creation(self):
        """Test creating a tool feature."""
        feature = ToolFeature(
            feature_name="test_feature",
            description="A test feature",
            importance="critical"
        )
        
        self.assertEqual(feature.feature_name, "test_feature")
        self.assertEqual(feature.importance, "critical")
        self.assertTrue(feature.availability)


class TestToolProfile(unittest.TestCase):
    """Test cases for ToolProfile dataclass."""
    
    def test_profile_creation(self):
        """Test creating a tool profile."""
        profile = ToolProfile(
            tool_id="tool_001",
            name="TestTool",
            category=ToolCategory.DEVELOPMENT.value,
            description="A test tool",
            version="1.0",
            maturity_level=MaturityLevel.STABLE.value
        )
        
        self.assertEqual(profile.name, "TestTool")
        self.assertEqual(profile.category, ToolCategory.DEVELOPMENT.value)


if __name__ == '__main__':
    unittest.main()
