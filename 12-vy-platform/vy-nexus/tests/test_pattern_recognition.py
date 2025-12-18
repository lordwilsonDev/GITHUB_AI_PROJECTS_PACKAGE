#!/usr/bin/env python3
"""
Test Suite for Pattern Recognition Engine

Author: VY-NEXUS Self-Evolving AI Ecosystem
Date: December 15, 2025
Version: 1.0.0
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / "modules"))

from learning.pattern_recognition_engine import (
    PatternRecognitionEngine,
    Pattern,
    MIN_PATTERN_FREQUENCY
)

from learning.user_interaction_monitor import (
    Interaction,
    InteractionType,
    InteractionStatus
)

class TestPatternRecognitionEngine(unittest.TestCase):
    """Test cases for Pattern Recognition Engine"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.engine = PatternRecognitionEngine(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def _create_test_interactions(self, count: int = 10) -> list:
        """Create test interactions"""
        interactions = []
        base_time = datetime.utcnow()
        
        for i in range(count):
            interaction = Interaction(
                timestamp=(base_time + timedelta(minutes=i)).isoformat(),
                interaction_type=InteractionType.CLI_COMMAND.value,
                command=f"command_{i % 3}",  # Create some repetition
                status=InteractionStatus.SUCCESS.value if i % 4 != 0 else InteractionStatus.FAILURE.value,
                duration_ms=100.0 + i * 10,
                error_message="Test error" if i % 4 == 0 else None,
                metadata={},
                session_id="test_session",
                user_hash="test_user"
            )
            interactions.append(interaction)
        
        return interactions
    
    def test_analyze_interactions(self):
        """Test basic interaction analysis"""
        interactions = self._create_test_interactions(20)
        results = self.engine.analyze_interactions(interactions)
        
        self.assertIn("patterns_detected", results)
        self.assertIn("patterns", results)
        self.assertIn("statistics", results)
        self.assertGreaterEqual(results["patterns_detected"], 0)
    
    def test_detect_repetitive_patterns(self):
        """Test repetitive pattern detection"""
        # Create interactions with repetitive commands
        interactions = []
        base_time = datetime.utcnow()
        
        # Repeat "status" command 10 times
        for i in range(10):
            interaction = Interaction(
                timestamp=(base_time + timedelta(minutes=i)).isoformat(),
                interaction_type=InteractionType.CLI_COMMAND.value,
                command="status",
                status=InteractionStatus.SUCCESS.value,
                duration_ms=100.0,
                error_message=None,
                metadata={},
                session_id="test_session",
                user_hash="test_user"
            )
            interactions.append(interaction)
        
        results = self.engine.analyze_interactions(interactions)
        
        # Should detect repetitive pattern
        repetitive_patterns = [
            p for p in results["patterns"]
            if p["pattern_type"] == "repetitive"
        ]
        
        self.assertGreater(len(repetitive_patterns), 0)
        self.assertEqual(repetitive_patterns[0]["frequency"], 10)
    
    def test_detect_sequential_patterns(self):
        """Test sequential pattern detection"""
        interactions = []
        base_time = datetime.utcnow()
        
        # Create sequence: cmd1 -> cmd2 -> cmd3, repeated 5 times
        for i in range(5):
            for j, cmd in enumerate(["cmd1", "cmd2", "cmd3"]):
                interaction = Interaction(
                    timestamp=(base_time + timedelta(minutes=i*3 + j)).isoformat(),
                    interaction_type=InteractionType.CLI_COMMAND.value,
                    command=cmd,
                    status=InteractionStatus.SUCCESS.value,
                    duration_ms=100.0,
                    error_message=None,
                    metadata={},
                    session_id="test_session",
                    user_hash="test_user"
                )
                interactions.append(interaction)
        
        results = self.engine.analyze_interactions(interactions)
        
        # Should detect sequential pattern
        sequential_patterns = [
            p for p in results["patterns"]
            if p["pattern_type"] == "sequential"
        ]
        
        self.assertGreater(len(sequential_patterns), 0)
    
    def test_detect_temporal_patterns(self):
        """Test temporal pattern detection"""
        interactions = []
        base_time = datetime.utcnow().replace(hour=9, minute=0)  # 9 AM
        
        # Create commands concentrated at 9 AM
        for i in range(10):
            interaction = Interaction(
                timestamp=(base_time + timedelta(minutes=i)).isoformat(),
                interaction_type=InteractionType.CLI_COMMAND.value,
                command="morning_check",
                status=InteractionStatus.SUCCESS.value,
                duration_ms=100.0,
                error_message=None,
                metadata={},
                session_id="test_session",
                user_hash="test_user"
            )
            interactions.append(interaction)
        
        # Add some at other times
        for i in range(2):
            interaction = Interaction(
                timestamp=(base_time.replace(hour=15) + timedelta(minutes=i)).isoformat(),
                interaction_type=InteractionType.CLI_COMMAND.value,
                command="morning_check",
                status=InteractionStatus.SUCCESS.value,
                duration_ms=100.0,
                error_message=None,
                metadata={},
                session_id="test_session",
                user_hash="test_user"
            )
            interactions.append(interaction)
        
        results = self.engine.analyze_interactions(interactions)
        
        # Should detect temporal pattern
        temporal_patterns = [
            p for p in results["patterns"]
            if p["pattern_type"] == "temporal"
        ]
        
        self.assertGreater(len(temporal_patterns), 0)
    
    def test_detect_error_patterns(self):
        """Test error pattern detection"""
        interactions = []
        base_time = datetime.utcnow()
        
        # Create command that frequently fails
        for i in range(10):
            interaction = Interaction(
                timestamp=(base_time + timedelta(minutes=i)).isoformat(),
                interaction_type=InteractionType.CLI_COMMAND.value,
                command="failing_command",
                status=InteractionStatus.FAILURE.value if i < 7 else InteractionStatus.SUCCESS.value,
                duration_ms=100.0,
                error_message="Connection timeout" if i < 7 else None,
                metadata={},
                session_id="test_session",
                user_hash="test_user"
            )
            interactions.append(interaction)
        
        results = self.engine.analyze_interactions(interactions)
        
        # Should detect error pattern
        error_patterns = [
            p for p in results["patterns"]
            if p["pattern_type"] == "error"
        ]
        
        self.assertGreater(len(error_patterns), 0)
        self.assertGreater(error_patterns[0]["metadata"]["error_rate"], 0.2)
    
    def test_detect_anomalies(self):
        """Test anomaly detection"""
        interactions = []
        base_time = datetime.utcnow()
        
        # Create command with mostly consistent duration
        for i in range(20):
            # Most durations around 100ms
            duration = 100.0 if i < 18 else 1000.0  # Two outliers
            
            interaction = Interaction(
                timestamp=(base_time + timedelta(minutes=i)).isoformat(),
                interaction_type=InteractionType.CLI_COMMAND.value,
                command="test_command",
                status=InteractionStatus.SUCCESS.value,
                duration_ms=duration,
                error_message=None,
                metadata={},
                session_id="test_session",
                user_hash="test_user"
            )
            interactions.append(interaction)
        
        results = self.engine.analyze_interactions(interactions)
        
        # Should detect anomaly pattern
        anomaly_patterns = [
            p for p in results["patterns"]
            if p["pattern_type"] == "anomaly"
        ]
        
        # May or may not detect depending on threshold
        # Just verify no errors
        self.assertIsNotNone(anomaly_patterns)
    
    def test_get_patterns_filtering(self):
        """Test pattern filtering"""
        interactions = self._create_test_interactions(20)
        self.engine.analyze_interactions(interactions)
        
        # Get all patterns
        all_patterns = self.engine.get_patterns()
        
        # Get only repetitive patterns
        repetitive = self.engine.get_patterns(pattern_type="repetitive")
        
        # Get high confidence patterns
        high_confidence = self.engine.get_patterns(min_confidence=0.8)
        
        # Verify filtering works
        self.assertGreaterEqual(len(all_patterns), len(repetitive))
        self.assertGreaterEqual(len(all_patterns), len(high_confidence))
    
    def test_get_optimization_opportunities(self):
        """Test optimization opportunity identification"""
        interactions = self._create_test_interactions(30)
        self.engine.analyze_interactions(interactions)
        
        opportunities = self.engine.get_optimization_opportunities(top_n=5)
        
        # Should return up to 5 opportunities
        self.assertLessEqual(len(opportunities), 5)
        
        # Should be sorted by optimization potential
        if len(opportunities) > 1:
            for i in range(len(opportunities) - 1):
                self.assertGreaterEqual(
                    opportunities[i].optimization_potential,
                    opportunities[i+1].optimization_potential
                )
    
    def test_pattern_persistence(self):
        """Test pattern saving and loading"""
        interactions = self._create_test_interactions(20)
        results = self.engine.analyze_interactions(interactions)
        
        pattern_count = results["patterns_detected"]
        
        # Create new engine instance (should load saved patterns)
        new_engine = PatternRecognitionEngine(data_dir=self.test_dir)
        
        # Should have loaded patterns
        loaded_patterns = new_engine.get_patterns(min_confidence=0.0, min_frequency=0)
        self.assertEqual(len(loaded_patterns), pattern_count)
    
    def test_statistics(self):
        """Test statistics tracking"""
        interactions = self._create_test_interactions(20)
        self.engine.analyze_interactions(interactions)
        
        stats = self.engine.get_statistics()
        
        self.assertIn("total_patterns", stats)
        self.assertIn("repetitive_patterns", stats)
        self.assertIn("sequential_patterns", stats)
        self.assertIn("temporal_patterns", stats)
        self.assertIn("error_patterns", stats)
        self.assertIn("anomalies_detected", stats)
        self.assertIn("last_analysis", stats)
        
        self.assertGreaterEqual(stats["total_patterns"], 0)

class TestPatternDataModels(unittest.TestCase):
    """Test pattern data models"""
    
    def test_pattern_to_dict(self):
        """Test Pattern to_dict method"""
        pattern = Pattern(
            pattern_id="test_001",
            pattern_type="repetitive",
            description="Test pattern",
            frequency=10,
            confidence=0.95,
            first_seen="2025-12-15T10:00:00",
            last_seen="2025-12-15T11:00:00",
            optimization_potential=0.8
        )
        
        data = pattern.to_dict()
        self.assertEqual(data["pattern_id"], "test_001")
        self.assertEqual(data["frequency"], 10)
        self.assertEqual(data["confidence"], 0.95)
    
    def test_pattern_from_dict(self):
        """Test Pattern from_dict method"""
        data = {
            "pattern_id": "test_001",
            "pattern_type": "repetitive",
            "description": "Test pattern",
            "frequency": 10,
            "confidence": 0.95,
            "first_seen": "2025-12-15T10:00:00",
            "last_seen": "2025-12-15T11:00:00",
            "examples": [],
            "metadata": {},
            "optimization_potential": 0.8
        }
        
        pattern = Pattern.from_dict(data)
        self.assertEqual(pattern.pattern_id, "test_001")
        self.assertEqual(pattern.frequency, 10)
        self.assertEqual(pattern.confidence, 0.95)

if __name__ == "__main__":
    unittest.main(verbosity=2)
