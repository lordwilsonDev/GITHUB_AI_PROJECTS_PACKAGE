#!/usr/bin/env python3
"""
Phase 2 Integration Tests - Self-Evolving AI Ecosystem

Comprehensive integration testing for all Phase 2 modules:
- User Interaction Monitor
- Pattern Recognition Engine
- Success/Failure Tracker
- User Preference Learner
- Knowledge Acquisition Pipeline
- Productivity Metrics Analyzer

Tests module-to-module communication, data flow, and end-to-end workflows.
"""

import unittest
import tempfile
import shutil
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.learning.user_interaction_monitor import UserInteractionMonitor
from modules.learning.pattern_recognition_engine import PatternRecognitionEngine
from modules.learning.success_failure_tracker import SuccessFailureTracker
from modules.learning.user_preference_learner import UserPreferenceLearner
from modules.learning.knowledge_acquisition_pipeline import KnowledgeAcquisitionPipeline, KnowledgeSource
from modules.learning.productivity_metrics_analyzer import ProductivityMetricsAnalyzer, TaskCategory


class TestPhase2Integration(unittest.TestCase):
    """Integration tests for Phase 2 modules."""
    
    def setUp(self):
        """Set up test environment with temporary directories."""
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.test_dir, 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize all modules with test directories
        self.interaction_monitor = UserInteractionMonitor(
            data_dir=os.path.join(self.data_dir, 'interactions')
        )
        self.pattern_engine = PatternRecognitionEngine(
            data_dir=os.path.join(self.data_dir, 'patterns')
        )
        self.success_tracker = SuccessFailureTracker(
            data_dir=os.path.join(self.data_dir, 'success')
        )
        self.preference_learner = UserPreferenceLearner(
            data_dir=os.path.join(self.data_dir, 'preferences')
        )
        self.knowledge_pipeline = KnowledgeAcquisitionPipeline(
            data_dir=os.path.join(self.data_dir, 'knowledge')
        )
        self.productivity_analyzer = ProductivityMetricsAnalyzer(
            data_dir=os.path.join(self.data_dir, 'productivity')
        )
    
    def tearDown(self):
        """Clean up test environment."""
        # Flush all buffers
        self.interaction_monitor.flush()
        self.success_tracker.flush()
        self.productivity_analyzer.flush()
        
        # Clean up temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    # ========================================================================
    # Test 1: User Interaction Monitor -> Pattern Recognition Engine
    # ========================================================================
    
    def test_interaction_to_pattern_flow(self):
        """Test data flow from interaction monitoring to pattern recognition."""
        # Record repetitive interactions
        for i in range(10):
            self.interaction_monitor.record_interaction(
                user_id="test_user",
                command="git status",
                context={"iteration": i}
            )
        
        # Flush to disk
        self.interaction_monitor.flush()
        
        # Get interactions and analyze patterns
        interactions = self.interaction_monitor.get_interactions(days=1)
        self.assertEqual(len(interactions), 10)
        
        # Detect patterns
        patterns = self.pattern_engine.detect_patterns(interactions)
        
        # Should detect repetitive pattern
        repetitive_patterns = [p for p in patterns if p.pattern_type == 'repetitive']
        self.assertGreater(len(repetitive_patterns), 0)
        
        # Verify pattern details
        git_pattern = next((p for p in repetitive_patterns if 'git status' in str(p.pattern_data)), None)
        self.assertIsNotNone(git_pattern)
        self.assertGreater(git_pattern.confidence, 0.5)
    
    # ========================================================================
    # Test 2: Complete Learning Cycle
    # ========================================================================
    
    def test_complete_learning_cycle(self):
        """Test complete learning cycle from interaction to optimization."""
        user_id = "test_user"
        
        # Step 1: User performs repetitive task
        for i in range(15):
            # Record interaction
            self.interaction_monitor.record_interaction(
                user_id=user_id,
                command="npm test",
                context={"iteration": i, "project": "vy-nexus"}
            )
            
            # Track task
            task_id = f"test_run_{i}"
            entry_id = self.productivity_analyzer.start_task(
                task_name="Run Tests",
                task_category=TaskCategory.DEVELOPMENT,
                context={"iteration": i}
            )
            
            # Simulate task execution
            time.sleep(0.01)
            success = i < 12  # First 12 succeed, last 3 fail
            
            # Record success/failure
            self.success_tracker.record_task(
                task_id=task_id,
                task_type="testing",
                success=success,
                duration=0.01,
                error_type="test_failure" if not success else None,
                context={"iteration": i}
            )
            
            # End productivity tracking
            self.productivity_analyzer.end_task(
                entry_id,
                completed=success,
                interruptions=0 if success else 1
            )
        
        # Flush all buffers
        self.interaction_monitor.flush()
        self.success_tracker.flush()
        self.productivity_analyzer.flush()
        
        # Step 2: Analyze patterns
        interactions = self.interaction_monitor.get_interactions(days=1)
        patterns = self.pattern_engine.detect_patterns(interactions)
        
        # Should detect repetitive pattern
        repetitive = [p for p in patterns if p.pattern_type == 'repetitive']
        self.assertGreater(len(repetitive), 0)
        
        # Step 3: Analyze success/failure
        metrics = self.success_tracker.get_metrics(task_type="testing")
        self.assertEqual(metrics['total_tasks'], 15)
        self.assertEqual(metrics['successful_tasks'], 12)
        self.assertEqual(metrics['failed_tasks'], 3)
        
        # Step 4: Get productivity insights
        insights = self.productivity_analyzer.generate_insights(days=1)
        self.assertGreater(len(insights), 0)
        
        # Step 5: Store learned knowledge
        # Pattern knowledge
        for pattern in repetitive:
            if 'npm test' in str(pattern.pattern_data):
                self.knowledge_pipeline.add_knowledge(
                    subject="npm_test",
                    predicate="is_repetitive",
                    obj="true",
                    source=KnowledgeSource.SYSTEM_ANALYSIS,
                    confidence=pattern.confidence,
                    metadata={"frequency": pattern.pattern_data.get('frequency', 0)}
                )
        
        # Success rate knowledge
        self.knowledge_pipeline.add_knowledge(
            subject="npm_test",
            predicate="has_success_rate",
            obj=str(metrics['success_rate']),
            source=KnowledgeSource.SYSTEM_ANALYSIS,
            confidence=0.9,
            metadata=metrics
        )
        
        # Step 6: Verify knowledge was stored
        npm_knowledge = self.knowledge_pipeline.query(subject="npm_test")
        self.assertGreater(len(npm_knowledge), 0)
    
    # ========================================================================
    # Test 3: Data Persistence
    # ========================================================================
    
    def test_data_persistence_across_instances(self):
        """Test that data persists when modules are reinitialized."""
        # Record data
        self.interaction_monitor.record_interaction(
            user_id="persist_user",
            command="persist_test",
            context={"test": "persistence"}
        )
        self.interaction_monitor.flush()
        
        self.success_tracker.record_task(
            task_id="persist_task",
            task_type="persistence_test",
            success=True,
            duration=1.0
        )
        self.success_tracker.flush()
        
        self.knowledge_pipeline.add_knowledge(
            subject="persistence",
            predicate="is_tested",
            obj="true",
            source=KnowledgeSource.SYSTEM_ANALYSIS,
            confidence=1.0
        )
        
        # Create new instances with same data directories
        new_monitor = UserInteractionMonitor(
            data_dir=os.path.join(self.data_dir, 'interactions')
        )
        new_tracker = SuccessFailureTracker(
            data_dir=os.path.join(self.data_dir, 'success')
        )
        new_pipeline = KnowledgeAcquisitionPipeline(
            data_dir=os.path.join(self.data_dir, 'knowledge')
        )
        
        # Verify data persisted
        interactions = new_monitor.get_interactions(days=1)
        self.assertGreater(len(interactions), 0)
        
        metrics = new_tracker.get_metrics(task_type="persistence_test")
        self.assertEqual(metrics['total_tasks'], 1)
        
        knowledge = new_pipeline.query(subject="persistence")
        self.assertGreater(len(knowledge), 0)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
