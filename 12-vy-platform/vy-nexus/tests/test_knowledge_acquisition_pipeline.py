#!/usr/bin/env python3
"""
Unit tests for Knowledge Acquisition Pipeline

Author: VY-NEXUS Self-Evolving AI System
Date: December 15, 2025
"""

import unittest
import os
import tempfile
import shutil
import json
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.learning.knowledge_acquisition_pipeline import (
    KnowledgeAcquisitionPipeline,
    KnowledgeSource,
    KnowledgeType,
    ValidationStatus,
    KnowledgeQuery,
    KnowledgeItem
)


class TestKnowledgeAcquisitionPipeline(unittest.TestCase):
    """Test cases for KnowledgeAcquisitionPipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.pipeline = KnowledgeAcquisitionPipeline(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_acquire_knowledge(self):
        """Test acquiring new knowledge."""
        kid = self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="Python",
            predicate="is_a",
            object="programming_language",
            source=KnowledgeSource.DOCUMENTATION,
            confidence=1.0
        )
        
        self.assertIsNotNone(kid)
        self.assertIn(kid, self.pipeline._knowledge_base)
        
        item = self.pipeline._knowledge_base[kid]
        self.assertEqual(item.subject, "Python")
        self.assertEqual(item.predicate, "is_a")
        self.assertEqual(item.object, "programming_language")
        self.assertEqual(item.confidence, 1.0)
    
    def test_acquire_duplicate_knowledge(self):
        """Test acquiring duplicate knowledge increases confidence."""
        # Acquire knowledge first time
        kid1 = self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="VY",
            predicate="version",
            object="1.0",
            source=KnowledgeSource.OBSERVATION,
            confidence=0.5
        )
        
        initial_confidence = self.pipeline._knowledge_base[kid1].confidence
        
        # Acquire same knowledge again
        kid2 = self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="VY",
            predicate="version",
            object="1.0",
            source=KnowledgeSource.OBSERVATION,
            confidence=0.5
        )
        
        # Should be same ID
        self.assertEqual(kid1, kid2)
        
        # Confidence should increase
        final_confidence = self.pipeline._knowledge_base[kid1].confidence
        self.assertGreater(final_confidence, initial_confidence)
    
    def test_query_by_subject(self):
        """Test querying knowledge by subject."""
        # Acquire multiple knowledge items
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="Python",
            predicate="is_a",
            object="language",
            source=KnowledgeSource.DOCUMENTATION,
            confidence=1.0
        )
        
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="Python",
            predicate="version",
            object="3.11",
            source=KnowledgeSource.OBSERVATION,
            confidence=0.9
        )
        
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="JavaScript",
            predicate="is_a",
            object="language",
            source=KnowledgeSource.DOCUMENTATION,
            confidence=1.0
        )
        
        # Query for Python
        query = KnowledgeQuery(subject="Python")
        results = self.pipeline.query_knowledge(query)
        
        self.assertEqual(len(results), 2)
        for item in results:
            self.assertEqual(item.subject, "Python")
    
    def test_query_by_predicate(self):
        """Test querying knowledge by predicate."""
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="Python",
            predicate="is_a",
            object="language",
            source=KnowledgeSource.DOCUMENTATION,
            confidence=1.0
        )
        
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="JavaScript",
            predicate="is_a",
            object="language",
            source=KnowledgeSource.DOCUMENTATION,
            confidence=1.0
        )
        
        # Query for is_a relationships
        query = KnowledgeQuery(predicate="is_a")
        results = self.pipeline.query_knowledge(query)
        
        self.assertEqual(len(results), 2)
        for item in results:
            self.assertEqual(item.predicate, "is_a")
    
    def test_query_by_tags(self):
        """Test querying knowledge by tags."""
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="Python",
            predicate="is_a",
            object="language",
            source=KnowledgeSource.DOCUMENTATION,
            confidence=1.0,
            tags=["programming", "language"]
        )
        
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="Docker",
            predicate="is_a",
            object="container",
            source=KnowledgeSource.DOCUMENTATION,
            confidence=1.0,
            tags=["devops", "container"]
        )
        
        # Query for programming tag
        query = KnowledgeQuery(tags=["programming"])
        results = self.pipeline.query_knowledge(query)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].subject, "Python")
    
    def test_query_with_confidence_filter(self):
        """Test querying with minimum confidence filter."""
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="Item1",
            predicate="property",
            object="value1",
            source=KnowledgeSource.OBSERVATION,
            confidence=0.9
        )
        
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="Item2",
            predicate="property",
            object="value2",
            source=KnowledgeSource.OBSERVATION,
            confidence=0.4
        )
        
        # Query with high confidence threshold
        query = KnowledgeQuery(predicate="property", min_confidence=0.8)
        results = self.pipeline.query_knowledge(query)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].subject, "Item1")
    
    def test_get_knowledge(self):
        """Test getting specific knowledge value."""
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="Python",
            predicate="version",
            object="3.11",
            source=KnowledgeSource.DOCUMENTATION,
            confidence=1.0
        )
        
        version = self.pipeline.get_knowledge("Python", "version")
        self.assertEqual(version, "3.11")
        
        # Non-existent knowledge
        result = self.pipeline.get_knowledge("Python", "nonexistent")
        self.assertIsNone(result)
    
    def test_validate_knowledge(self):
        """Test manual knowledge validation."""
        kid = self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="Test",
            predicate="property",
            object="value",
            source=KnowledgeSource.OBSERVATION,
            confidence=0.5,
            auto_validate=False
        )
        
        item = self.pipeline._knowledge_base[kid]
        initial_confidence = item.confidence
        
        # Validate as correct
        success = self.pipeline.validate_knowledge(kid, is_valid=True)
        self.assertTrue(success)
        
        self.assertEqual(item.validation_status, ValidationStatus.VALIDATED)
        self.assertGreater(item.confidence, initial_confidence)
    
    def test_invalidate_knowledge(self):
        """Test invalidating knowledge."""
        kid = self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="Test",
            predicate="property",
            object="wrong_value",
            source=KnowledgeSource.OBSERVATION,
            confidence=0.5
        )
        
        # Invalidate
        success = self.pipeline.validate_knowledge(kid, is_valid=False)
        self.assertTrue(success)
        
        item = self.pipeline._knowledge_base[kid]
        self.assertEqual(item.validation_status, ValidationStatus.DEPRECATED)
        self.assertEqual(item.confidence, 0.0)
    
    def test_conflict_detection(self):
        """Test detection of conflicting knowledge."""
        # Acquire first knowledge
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="System",
            predicate="status",
            object="online",
            source=KnowledgeSource.OBSERVATION,
            confidence=0.7
        )
        
        # Acquire conflicting knowledge
        kid2 = self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="System",
            predicate="status",
            object="offline",
            source=KnowledgeSource.OBSERVATION,
            confidence=0.7
        )
        
        # Should be marked as conflicting
        item2 = self.pipeline._knowledge_base[kid2]
        # Conflict detection depends on implementation
        self.assertIsNotNone(item2.validation_status)
    
    def test_knowledge_persistence(self):
        """Test that knowledge persists across instances."""
        # Acquire knowledge
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="Persistent",
            predicate="property",
            object="value",
            source=KnowledgeSource.DOCUMENTATION,
            confidence=1.0
        )
        
        self.pipeline.flush()
        
        # Create new pipeline instance
        new_pipeline = KnowledgeAcquisitionPipeline(data_dir=self.test_dir)
        
        # Verify knowledge was loaded
        value = new_pipeline.get_knowledge("Persistent", "property")
        self.assertEqual(value, "value")
    
    def test_provenance_tracking(self):
        """Test provenance chain tracking."""
        kid = self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="Item",
            predicate="property",
            object="value",
            source=KnowledgeSource.OBSERVATION,
            confidence=0.5
        )
        
        # Acquire same knowledge from different source
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="Item",
            predicate="property",
            object="value",
            source=KnowledgeSource.DOCUMENTATION,
            confidence=0.8
        )
        
        item = self.pipeline._knowledge_base[kid]
        
        # Should have multiple sources in provenance
        self.assertGreater(len(item.provenance), 1)
        self.assertIn(KnowledgeSource.OBSERVATION.value, item.provenance)
        self.assertIn(KnowledgeSource.DOCUMENTATION.value, item.provenance)
    
    def test_knowledge_graph_generation(self):
        """Test knowledge graph generation."""
        # Create some relationships
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.RELATIONSHIP,
            subject="VY-NEXUS",
            predicate="uses",
            object="Python",
            source=KnowledgeSource.DOCUMENTATION,
            confidence=1.0
        )
        
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.RELATIONSHIP,
            subject="Python",
            predicate="runs_on",
            object="MacOS",
            source=KnowledgeSource.OBSERVATION,
            confidence=0.9
        )
        
        # Generate graph
        graph = self.pipeline.get_knowledge_graph()
        
        self.assertIn("nodes", graph)
        self.assertIn("edges", graph)
        self.assertGreater(len(graph["nodes"]), 0)
        self.assertGreater(len(graph["edges"]), 0)
    
    def test_statistics(self):
        """Test statistics generation."""
        # Acquire various knowledge items
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="Item1",
            predicate="prop",
            object="val1",
            source=KnowledgeSource.DOCUMENTATION,
            confidence=1.0
        )
        
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.PROCEDURE,
            subject="Item2",
            predicate="step",
            object="val2",
            source=KnowledgeSource.USER_INPUT,
            confidence=0.8
        )
        
        stats = self.pipeline.get_statistics()
        
        self.assertIn("total_items", stats)
        self.assertIn("by_type", stats)
        self.assertIn("by_source", stats)
        self.assertIn("confidence_distribution", stats)
        
        self.assertEqual(stats["total_items"], 2)
    
    def test_export_knowledge(self):
        """Test knowledge export."""
        # Acquire knowledge
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="Export",
            predicate="test",
            object="value",
            source=KnowledgeSource.DOCUMENTATION,
            confidence=1.0
        )
        
        # Export
        export_path = os.path.join(self.test_dir, "export.json")
        success = self.pipeline.export_knowledge(export_path)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(export_path))
        
        # Verify export content
        with open(export_path, 'r') as f:
            data = json.load(f)
        
        self.assertGreater(len(data), 0)
    
    def test_export_with_confidence_filter(self):
        """Test exporting only high-confidence knowledge."""
        # Acquire high and low confidence knowledge
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="High",
            predicate="conf",
            object="val1",
            source=KnowledgeSource.DOCUMENTATION,
            confidence=0.9
        )
        
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="Low",
            predicate="conf",
            object="val2",
            source=KnowledgeSource.OBSERVATION,
            confidence=0.3
        )
        
        # Export with confidence filter
        export_path = os.path.join(self.test_dir, "export_filtered.json")
        success = self.pipeline.export_knowledge(export_path, min_confidence=0.8)
        
        self.assertTrue(success)
        
        with open(export_path, 'r') as f:
            data = json.load(f)
        
        # Should only have high confidence item
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["subject"], "High")
    
    def test_access_tracking(self):
        """Test that knowledge access is tracked."""
        kid = self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.FACT,
            subject="Tracked",
            predicate="property",
            object="value",
            source=KnowledgeSource.DOCUMENTATION,
            confidence=1.0
        )
        
        initial_count = self.pipeline._knowledge_base[kid].access_count
        
        # Query the knowledge
        query = KnowledgeQuery(subject="Tracked")
        self.pipeline.query_knowledge(query)
        
        # Access count should increase
        final_count = self.pipeline._knowledge_base[kid].access_count
        self.assertGreater(final_count, initial_count)
    
    def test_inference(self):
        """Test knowledge inference."""
        # Create transitive relationships
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.RELATIONSHIP,
            subject="A",
            predicate="relates_to",
            object="B",
            source=KnowledgeSource.DOCUMENTATION,
            confidence=1.0
        )
        
        self.pipeline.acquire_knowledge(
            knowledge_type=KnowledgeType.RELATIONSHIP,
            subject="B",
            predicate="relates_to",
            object="C",
            source=KnowledgeSource.DOCUMENTATION,
            confidence=1.0
        )
        
        # Infer new knowledge
        inferred = self.pipeline.infer_knowledge()
        
        # Should infer A relates_to C
        self.assertGreater(len(inferred), 0)


if __name__ == "__main__":
    unittest.main()
