#!/usr/bin/env python3
"""
Test suite for Knowledge Base Updater

Tests all functionality of the dynamic knowledge base update system.
"""

import unittest
import os
import shutil
import tempfile
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.adaptation.knowledge_base_updater import KnowledgeBaseUpdater


class TestKnowledgeBaseUpdater(unittest.TestCase):
    """Test cases for KnowledgeBaseUpdater."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.updater = KnowledgeBaseUpdater(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test updater initialization."""
        self.assertIsNotNone(self.updater)
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertIsInstance(self.updater.knowledge_base, dict)
        self.assertIsInstance(self.updater.categories, dict)
        self.assertIsInstance(self.updater.tags, dict)
    
    def test_add_knowledge(self):
        """Test adding knowledge."""
        kid = self.updater.add_knowledge(
            content="Python is great for automation",
            category="programming",
            tags=["python", "automation"],
            confidence=0.9
        )
        
        self.assertIsNotNone(kid)
        self.assertIn(kid, self.updater.knowledge_base)
        
        entry = self.updater.knowledge_base[kid]
        self.assertEqual(entry["content"], "Python is great for automation")
        self.assertEqual(entry["category"], "programming")
        self.assertIn("python", entry["tags"])
        self.assertEqual(entry["confidence"], 0.9)
    
    def test_duplicate_detection(self):
        """Test duplicate knowledge detection."""
        content = "Test knowledge content"
        
        kid1 = self.updater.add_knowledge(
            content=content,
            category="test",
            confidence=0.8
        )
        
        kid2 = self.updater.add_knowledge(
            content=content,
            category="test",
            confidence=0.9
        )
        
        # Should return same ID
        self.assertEqual(kid1, kid2)
        
        # Confidence should be updated
        entry = self.updater.knowledge_base[kid1]
        self.assertGreater(entry["confidence"], 0.8)
        self.assertGreater(entry["validation_count"], 0)
    
    def test_category_indexing(self):
        """Test category indexing."""
        kid = self.updater.add_knowledge(
            content="Test content",
            category="test_category",
            confidence=0.8
        )
        
        self.assertIn("test_category", self.updater.categories)
        self.assertIn(kid, self.updater.categories["test_category"]["knowledge_ids"])
        self.assertEqual(self.updater.categories["test_category"]["count"], 1)
    
    def test_tag_indexing(self):
        """Test tag indexing."""
        kid = self.updater.add_knowledge(
            content="Test content",
            category="test",
            tags=["tag1", "tag2"],
            confidence=0.8
        )
        
        self.assertIn("tag1", self.updater.tags)
        self.assertIn("tag2", self.updater.tags)
        self.assertIn(kid, self.updater.tags["tag1"]["knowledge_ids"])
        self.assertIn(kid, self.updater.tags["tag2"]["knowledge_ids"])
    
    def test_search_knowledge(self):
        """Test knowledge search."""
        # Add some knowledge
        self.updater.add_knowledge(
            content="Python is great for automation tasks",
            category="programming",
            tags=["python", "automation"],
            confidence=0.9
        )
        
        self.updater.add_knowledge(
            content="JavaScript is used for web development",
            category="programming",
            tags=["javascript", "web"],
            confidence=0.85
        )
        
        # Search for Python
        results = self.updater.search_knowledge("python automation")
        self.assertGreater(len(results), 0)
        self.assertIn("python", results[0]["content"].lower())
    
    def test_search_with_category_filter(self):
        """Test search with category filter."""
        self.updater.add_knowledge(
            content="Python automation",
            category="programming",
            confidence=0.9
        )
        
        self.updater.add_knowledge(
            content="Python data science",
            category="data_science",
            confidence=0.85
        )
        
        results = self.updater.search_knowledge(
            "python",
            category="programming"
        )
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["category"], "programming")
    
    def test_search_with_tag_filter(self):
        """Test search with tag filter."""
        self.updater.add_knowledge(
            content="Python automation",
            category="programming",
            tags=["python", "automation"],
            confidence=0.9
        )
        
        self.updater.add_knowledge(
            content="Python web development",
            category="programming",
            tags=["python", "web"],
            confidence=0.85
        )
        
        results = self.updater.search_knowledge(
            "python",
            tags=["automation"]
        )
        
        self.assertEqual(len(results), 1)
        self.assertIn("automation", results[0]["tags"])
    
    def test_update_from_interaction_task_completion(self):
        """Test updating from task completion interaction."""
        interaction = {
            "id": "test_1",
            "task_completed": True,
            "task": "file processing",
            "method": "using pandas"
        }
        
        kids = self.updater.update_from_interaction(interaction)
        self.assertGreater(len(kids), 0)
        
        # Check that knowledge was added
        entry = self.updater.knowledge_base[kids[0]]
        self.assertIn("file processing", entry["content"])
        self.assertIn("pandas", entry["content"])
    
    def test_update_from_interaction_errors(self):
        """Test updating from error resolution interaction."""
        interaction = {
            "id": "test_2",
            "errors": [
                {
                    "type": "ValueError",
                    "solution": "validate input data"
                }
            ]
        }
        
        kids = self.updater.update_from_interaction(interaction)
        self.assertGreater(len(kids), 0)
        
        entry = self.updater.knowledge_base[kids[0]]
        self.assertIn("ValueError", entry["content"])
        self.assertIn("validate input data", entry["content"])
        self.assertEqual(entry["category"], "error_solutions")
    
    def test_update_from_interaction_feedback(self):
        """Test updating from user feedback."""
        interaction = {
            "id": "test_3",
            "feedback": {
                "positive": "fast processing"
            }
        }
        
        kids = self.updater.update_from_interaction(interaction)
        self.assertGreater(len(kids), 0)
        
        entry = self.updater.knowledge_base[kids[0]]
        self.assertIn("fast processing", entry["content"])
        self.assertEqual(entry["category"], "user_preferences")
    
    def test_update_from_interaction_discoveries(self):
        """Test updating from discoveries."""
        interaction = {
            "id": "test_4",
            "discoveries": [
                {
                    "content": "New optimization technique",
                    "category": "optimization",
                    "tags": ["performance"],
                    "confidence": 0.75
                }
            ]
        }
        
        kids = self.updater.update_from_interaction(interaction)
        self.assertGreater(len(kids), 0)
        
        entry = self.updater.knowledge_base[kids[0]]
        self.assertEqual(entry["content"], "New optimization technique")
        self.assertEqual(entry["category"], "optimization")
    
    def test_knowledge_graph_creation(self):
        """Test knowledge graph creation."""
        kid1 = self.updater.add_knowledge(
            content="Python automation",
            category="programming",
            tags=["python"],
            confidence=0.9
        )
        
        kid2 = self.updater.add_knowledge(
            content="Python testing",
            category="programming",
            tags=["python"],
            confidence=0.85
        )
        
        # Check graph nodes
        self.assertIn(kid1, self.updater.knowledge_graph["nodes"])
        self.assertIn(kid2, self.updater.knowledge_graph["nodes"])
        
        # Check for edges (related knowledge)
        edges = self.updater.knowledge_graph["edges"]
        self.assertGreater(len(edges), 0)
    
    def test_relationship_strength_calculation(self):
        """Test relationship strength calculation."""
        entry1 = {
            "category": "programming",
            "tags": ["python", "automation"],
            "content": "Python automation tasks"
        }
        
        entry2 = {
            "category": "programming",
            "tags": ["python", "testing"],
            "content": "Python testing frameworks"
        }
        
        strength = self.updater._calculate_relationship_strength(entry1, entry2)
        
        # Should have some relationship (same category, shared tag, word overlap)
        self.assertGreater(strength, 0.3)
    
    def test_validate_knowledge_positive(self):
        """Test positive knowledge validation."""
        kid = self.updater.add_knowledge(
            content="Test content",
            category="test",
            confidence=0.7
        )
        
        initial_confidence = self.updater.knowledge_base[kid]["confidence"]
        
        self.updater.validate_knowledge(kid, is_valid=True)
        
        new_confidence = self.updater.knowledge_base[kid]["confidence"]
        self.assertGreater(new_confidence, initial_confidence)
        self.assertGreater(self.updater.knowledge_base[kid]["validation_count"], 0)
    
    def test_validate_knowledge_negative(self):
        """Test negative knowledge validation."""
        kid = self.updater.add_knowledge(
            content="Test content",
            category="test",
            confidence=0.7
        )
        
        initial_confidence = self.updater.knowledge_base[kid]["confidence"]
        
        self.updater.validate_knowledge(kid, is_valid=False)
        
        new_confidence = self.updater.knowledge_base[kid]["confidence"]
        self.assertLess(new_confidence, initial_confidence)
    
    def test_merge_duplicate_knowledge(self):
        """Test merging duplicate knowledge."""
        kid1 = self.updater.add_knowledge(
            content="Content 1",
            category="test",
            tags=["tag1"],
            confidence=0.8
        )
        
        kid2 = self.updater.add_knowledge(
            content="Content 2",
            category="test",
            tags=["tag2"],
            confidence=0.9
        )
        
        # Manually add to knowledge base (bypass duplicate detection)
        self.updater.knowledge_base[kid2] = {
            "id": kid2,
            "content": "Content 2",
            "category": "test",
            "tags": ["tag2"],
            "confidence": 0.9,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "access_count": 5,
            "validation_count": 2,
            "metadata": {}
        }
        
        primary = self.updater.merge_duplicate_knowledge(kid1, kid2)
        
        self.assertIsNotNone(primary)
        self.assertIn(primary, self.updater.knowledge_base)
        
        # Check merged tags
        merged_entry = self.updater.knowledge_base[primary]
        self.assertTrue(
            "tag1" in merged_entry["tags"] or "tag2" in merged_entry["tags"]
        )
    
    def test_statistics(self):
        """Test statistics generation."""
        # Add some knowledge
        for i in range(5):
            self.updater.add_knowledge(
                content=f"Content {i}",
                category="test",
                tags=[f"tag{i}"],
                confidence=0.8
            )
        
        stats = self.updater.get_statistics()
        
        self.assertEqual(stats["total_knowledge"], 5)
        self.assertGreater(stats["total_categories"], 0)
        self.assertGreater(stats["total_tags"], 0)
        self.assertGreater(stats["avg_confidence"], 0)
    
    def test_data_persistence(self):
        """Test data persistence across instances."""
        kid = self.updater.add_knowledge(
            content="Persistent content",
            category="test",
            confidence=0.9
        )
        
        # Create new instance with same data directory
        new_updater = KnowledgeBaseUpdater(data_dir=self.test_dir)
        
        # Check that knowledge persisted
        self.assertIn(kid, new_updater.knowledge_base)
        self.assertEqual(
            new_updater.knowledge_base[kid]["content"],
            "Persistent content"
        )
    
    def test_access_count_tracking(self):
        """Test access count tracking during search."""
        kid = self.updater.add_knowledge(
            content="Searchable content",
            category="test",
            confidence=0.9
        )
        
        initial_count = self.updater.knowledge_base[kid]["access_count"]
        
        # Perform search
        self.updater.search_knowledge("searchable")
        
        new_count = self.updater.knowledge_base[kid]["access_count"]
        self.assertGreater(new_count, initial_count)
    
    def test_update_history_recording(self):
        """Test update history recording."""
        initial_history_len = len(self.updater.update_history)
        
        self.updater.add_knowledge(
            content="Test content",
            category="test",
            confidence=0.8
        )
        
        new_history_len = len(self.updater.update_history)
        self.assertGreater(new_history_len, initial_history_len)
        
        # Check last update
        last_update = self.updater.update_history[-1]
        self.assertEqual(last_update["action"], "add")
        self.assertEqual(last_update["category"], "test")
    
    def test_metadata_storage(self):
        """Test metadata storage."""
        metadata = {
            "source_url": "https://example.com",
            "author": "test_user"
        }
        
        kid = self.updater.add_knowledge(
            content="Test content",
            category="test",
            confidence=0.8,
            metadata=metadata
        )
        
        entry = self.updater.knowledge_base[kid]
        self.assertEqual(entry["metadata"]["source_url"], "https://example.com")
        self.assertEqual(entry["metadata"]["author"], "test_user")
    
    def test_confidence_bounds(self):
        """Test confidence score bounds."""
        kid = self.updater.add_knowledge(
            content="Test content",
            category="test",
            confidence=0.95
        )
        
        # Validate multiple times to try to exceed 1.0
        for _ in range(10):
            self.updater.validate_knowledge(kid, is_valid=True)
        
        entry = self.updater.knowledge_base[kid]
        self.assertLessEqual(entry["confidence"], 1.0)
        
        # Invalidate multiple times to try to go below 0.0
        for _ in range(10):
            self.updater.validate_knowledge(kid, is_valid=False)
        
        entry = self.updater.knowledge_base[kid]
        self.assertGreaterEqual(entry["confidence"], 0.0)
    
    def test_empty_search(self):
        """Test search with no results."""
        results = self.updater.search_knowledge("nonexistent query")
        self.assertEqual(len(results), 0)
    
    def test_search_limit(self):
        """Test search result limiting."""
        # Add many knowledge entries
        for i in range(20):
            self.updater.add_knowledge(
                content=f"Python content {i}",
                category="test",
                confidence=0.8
            )
        
        results = self.updater.search_knowledge("python", limit=5)
        self.assertEqual(len(results), 5)
    
    def test_relevance_scoring(self):
        """Test relevance scoring in search."""
        # Add knowledge with varying relevance
        self.updater.add_knowledge(
            content="Python automation tasks",
            category="programming",
            tags=["python", "automation"],
            confidence=0.9
        )
        
        self.updater.add_knowledge(
            content="General automation",
            category="general",
            tags=["automation"],
            confidence=0.7
        )
        
        results = self.updater.search_knowledge("python automation")
        
        # First result should have higher relevance
        self.assertGreater(len(results), 0)
        if len(results) > 1:
            self.assertGreater(
                results[0]["relevance_score"],
                results[1]["relevance_score"]
            )


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == "__main__":
    run_tests()
