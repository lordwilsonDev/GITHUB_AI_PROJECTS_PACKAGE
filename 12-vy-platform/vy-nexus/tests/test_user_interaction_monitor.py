#!/usr/bin/env python3
"""
Test Suite for User Interaction Monitor

Author: VY-NEXUS Self-Evolving AI Ecosystem
Date: December 15, 2025
Version: 1.0.0
"""

import unittest
import time
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / "modules"))

from learning.user_interaction_monitor import (
    UserInteractionMonitor,
    Interaction,
    InteractionType,
    InteractionStatus,
    InteractionPattern,
    UserProfile
)

class TestUserInteractionMonitor(unittest.TestCase):
    """Test cases for User Interaction Monitor"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test data
        self.test_dir = Path(tempfile.mkdtemp())
        self.monitor = UserInteractionMonitor(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        self.monitor.stop()
        shutil.rmtree(self.test_dir)
    
    def test_record_interaction(self):
        """Test recording a single interaction"""
        timestamp = self.monitor.record_interaction(
            interaction_type=InteractionType.CLI_COMMAND,
            command="test_command",
            status=InteractionStatus.SUCCESS,
            duration_ms=100.0,
            user_id="test_user"
        )
        
        self.assertIsNotNone(timestamp)
        
        # Check statistics
        stats = self.monitor.get_statistics()
        self.assertEqual(stats["total_interactions"], 1)
        self.assertEqual(stats["successful_interactions"], 1)
        self.assertEqual(stats["failed_interactions"], 0)
    
    def test_record_multiple_interactions(self):
        """Test recording multiple interactions"""
        for i in range(10):
            status = InteractionStatus.SUCCESS if i % 2 == 0 else InteractionStatus.FAILURE
            self.monitor.record_interaction(
                interaction_type=InteractionType.CLI_COMMAND,
                command=f"command_{i}",
                status=status,
                duration_ms=100.0 + i,
                user_id="test_user"
            )
        
        stats = self.monitor.get_statistics()
        self.assertEqual(stats["total_interactions"], 10)
        self.assertEqual(stats["successful_interactions"], 5)
        self.assertEqual(stats["failed_interactions"], 5)
    
    def test_flush_to_disk(self):
        """Test flushing interactions to disk"""
        # Record interactions
        for i in range(5):
            self.monitor.record_interaction(
                interaction_type=InteractionType.CLI_COMMAND,
                command=f"command_{i}",
                status=InteractionStatus.SUCCESS,
                duration_ms=100.0,
                user_id="test_user"
            )
        
        # Flush to disk
        self.monitor._flush_to_disk()
        
        # Check file exists
        today = datetime.utcnow().date().isoformat()
        filepath = self.test_dir / f"interactions_{today}.jsonl"
        self.assertTrue(filepath.exists())
        
        # Check file contents
        with open(filepath, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 5)
    
    def test_analyze_recent_interactions(self):
        """Test analyzing recent interactions"""
        # Record various interactions
        for i in range(10):
            self.monitor.record_interaction(
                interaction_type=InteractionType.CLI_COMMAND,
                command="test_command" if i < 5 else "other_command",
                status=InteractionStatus.SUCCESS if i % 2 == 0 else InteractionStatus.FAILURE,
                duration_ms=100.0 + i * 10,
                user_id="test_user"
            )
        
        # Analyze
        analysis = self.monitor.analyze_recent_interactions(hours=24)
        
        self.assertEqual(analysis["total_count"], 10)
        self.assertEqual(analysis["success_rate"], 0.5)
        self.assertGreater(analysis["avg_duration_ms"], 0)
        self.assertIn("test_command", analysis["command_frequency"])
        self.assertEqual(analysis["command_frequency"]["test_command"], 5)
    
    def test_interaction_types(self):
        """Test different interaction types"""
        types = [
            InteractionType.CLI_COMMAND,
            InteractionType.API_REQUEST,
            InteractionType.TASK_SUBMISSION,
            InteractionType.EXPERT_QUERY
        ]
        
        for interaction_type in types:
            self.monitor.record_interaction(
                interaction_type=interaction_type,
                command="test",
                status=InteractionStatus.SUCCESS,
                duration_ms=100.0
            )
        
        analysis = self.monitor.analyze_recent_interactions(hours=24)
        self.assertEqual(len(analysis["interaction_types"]), 4)
    
    def test_error_tracking(self):
        """Test error message tracking"""
        self.monitor.record_interaction(
            interaction_type=InteractionType.CLI_COMMAND,
            command="failing_command",
            status=InteractionStatus.ERROR,
            duration_ms=50.0,
            error_message="Test error message"
        )
        
        analysis = self.monitor.analyze_recent_interactions(hours=24)
        self.assertIn("Test error message", analysis["error_frequency"])
    
    def test_metadata_storage(self):
        """Test metadata storage"""
        metadata = {"key1": "value1", "key2": 123}
        
        self.monitor.record_interaction(
            interaction_type=InteractionType.CLI_COMMAND,
            command="test",
            status=InteractionStatus.SUCCESS,
            duration_ms=100.0,
            metadata=metadata
        )
        
        # Flush and reload
        self.monitor._flush_to_disk()
        
        # Verify metadata is preserved
        today = datetime.utcnow().date().isoformat()
        filepath = self.test_dir / f"interactions_{today}.jsonl"
        
        with open(filepath, 'r') as f:
            data = json.loads(f.readline())
            self.assertEqual(data["metadata"], metadata)
    
    def test_anonymization(self):
        """Test user ID anonymization"""
        user_id = "sensitive_user_id"
        
        self.monitor.record_interaction(
            interaction_type=InteractionType.CLI_COMMAND,
            command="test",
            status=InteractionStatus.SUCCESS,
            duration_ms=100.0,
            user_id=user_id
        )
        
        # Flush and check
        self.monitor._flush_to_disk()
        
        today = datetime.utcnow().date().isoformat()
        filepath = self.test_dir / f"interactions_{today}.jsonl"
        
        with open(filepath, 'r') as f:
            data = json.loads(f.readline())
            # User hash should not equal original user_id
            self.assertNotEqual(data["user_hash"], user_id)
            # User hash should be consistent
            expected_hash = self.monitor._anonymize_user_id(user_id)
            self.assertEqual(data["user_hash"], expected_hash)
    
    def test_hourly_distribution(self):
        """Test hourly distribution tracking"""
        # Record interactions
        for i in range(24):
            self.monitor.record_interaction(
                interaction_type=InteractionType.CLI_COMMAND,
                command="test",
                status=InteractionStatus.SUCCESS,
                duration_ms=100.0
            )
        
        analysis = self.monitor.analyze_recent_interactions(hours=24)
        
        # Should have entries in hourly distribution
        self.assertGreater(len(analysis["hourly_distribution"]), 0)
    
    def test_concurrent_recording(self):
        """Test thread-safe concurrent recording"""
        import threading
        
        def record_interactions():
            for i in range(10):
                self.monitor.record_interaction(
                    interaction_type=InteractionType.CLI_COMMAND,
                    command="concurrent_test",
                    status=InteractionStatus.SUCCESS,
                    duration_ms=100.0
                )
        
        # Create multiple threads
        threads = [threading.Thread(target=record_interactions) for _ in range(5)]
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check total count
        stats = self.monitor.get_statistics()
        self.assertEqual(stats["total_interactions"], 50)

class TestInteractionDataModels(unittest.TestCase):
    """Test data model classes"""
    
    def test_interaction_to_dict(self):
        """Test Interaction to_dict method"""
        interaction = Interaction(
            timestamp="2025-12-15T10:00:00",
            interaction_type="cli_command",
            command="test",
            status="success",
            duration_ms=100.0
        )
        
        data = interaction.to_dict()
        self.assertEqual(data["command"], "test")
        self.assertEqual(data["status"], "success")
    
    def test_interaction_from_dict(self):
        """Test Interaction from_dict method"""
        data = {
            "timestamp": "2025-12-15T10:00:00",
            "interaction_type": "cli_command",
            "command": "test",
            "status": "success",
            "duration_ms": 100.0,
            "error_message": None,
            "metadata": {},
            "session_id": None,
            "user_hash": None
        }
        
        interaction = Interaction.from_dict(data)
        self.assertEqual(interaction.command, "test")
        self.assertEqual(interaction.status, "success")
    
    def test_interaction_pattern(self):
        """Test InteractionPattern model"""
        pattern = InteractionPattern(
            pattern_id="pattern_001",
            pattern_type="repetitive_command",
            frequency=10,
            first_seen="2025-12-15T10:00:00",
            last_seen="2025-12-15T11:00:00",
            confidence=0.95,
            description="User frequently runs status command"
        )
        
        data = pattern.to_dict()
        self.assertEqual(data["frequency"], 10)
        self.assertEqual(data["confidence"], 0.95)
    
    def test_user_profile(self):
        """Test UserProfile model"""
        profile = UserProfile(
            user_hash="abc123",
            total_interactions=100,
            success_rate=0.95,
            avg_session_duration_minutes=15.5,
            peak_usage_hours=[9, 10, 14, 15],
            common_commands=["status", "query"],
            common_errors=["timeout"],
            preferred_experts=["code_expert"],
            last_updated="2025-12-15T10:00:00"
        )
        
        data = profile.to_dict()
        self.assertEqual(data["total_interactions"], 100)
        self.assertEqual(data["success_rate"], 0.95)

if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
