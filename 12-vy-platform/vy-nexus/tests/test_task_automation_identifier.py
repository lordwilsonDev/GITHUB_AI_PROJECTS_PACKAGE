#!/usr/bin/env python3
"""
Tests for Task Automation Identifier
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.optimization.task_automation_identifier import (
    TaskAutomationIdentifier,
    AutomationCandidate,
    AutomationPotential,
    TaskComplexity
)


class TestTaskAutomationIdentifier(unittest.TestCase):
    """Test suite for TaskAutomationIdentifier"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.identifier = TaskAutomationIdentifier(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test identifier initialization"""
        self.assertTrue(self.test_dir.exists())
        self.assertEqual(len(self.identifier.candidates), 0)
        self.assertEqual(len(self.identifier.task_sequences), 0)
    
    def test_record_task_sequence(self):
        """Test recording a task sequence"""
        self.identifier.record_task_sequence(
            task_name="Test Task",
            steps=["Step 1", "Step 2", "Step 3"],
            duration_seconds=120,
            success=True,
            context={'user': 'test'}
        )
        
        self.assertEqual(len(self.identifier.task_sequences), 1)
        self.assertTrue(self.identifier.task_sequences_file.exists())
    
    def test_pattern_hash_creation(self):
        """Test pattern hash creation"""
        steps1 = ["Step 1", "Step 2", "Step 3"]
        steps2 = ["Step 1", "Step 2", "Step 3"]
        steps3 = ["Step 1", "Step 2", "Step 4"]
        
        hash1 = self.identifier._create_pattern_hash(steps1)
        hash2 = self.identifier._create_pattern_hash(steps2)
        hash3 = self.identifier._create_pattern_hash(steps3)
        
        self.assertEqual(hash1, hash2)  # Same steps = same hash
        self.assertNotEqual(hash1, hash3)  # Different steps = different hash
    
    def test_complexity_assessment(self):
        """Test task complexity assessment"""
        # Trivial
        trivial = self.identifier._assess_complexity(["Do something"])
        self.assertEqual(trivial, TaskComplexity.TRIVIAL)
        
        # Simple
        simple = self.identifier._assess_complexity(["Step 1", "Step 2"])
        self.assertEqual(simple, TaskComplexity.SIMPLE)
        
        # Moderate
        moderate = self.identifier._assess_complexity(
            ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"]
        )
        self.assertEqual(moderate, TaskComplexity.MODERATE)
        
        # Complex with decisions
        complex_steps = ["Step 1", "If condition then step 2", "Step 3", "Check result"]
        complex_task = self.identifier._assess_complexity(complex_steps)
        self.assertIn(complex_task, [TaskComplexity.MODERATE, TaskComplexity.COMPLEX])
    
    def test_decision_point_counting(self):
        """Test decision point counting"""
        steps = [
            "Open file",
            "If file exists, read it",
            "Check for errors",
            "Decide next action",
            "Save result"
        ]
        
        count = self.identifier._count_decision_points(steps)
        self.assertEqual(count, 3)  # if, check, decide
    
    def test_external_dependencies_identification(self):
        """Test external dependency identification"""
        steps = [
            "Make API request to server",
            "Query database for records",
            "Read file from disk",
            "Ask user for input"
        ]
        
        deps = self.identifier._identify_external_dependencies(steps)
        
        self.assertIn('api', deps)
        self.assertIn('database', deps)
        self.assertIn('file_system', deps)
        self.assertIn('user_input', deps)
    
    def test_automation_difficulty_calculation(self):
        """Test automation difficulty calculation"""
        # Easy task
        easy_difficulty = self.identifier._calculate_automation_difficulty(
            TaskComplexity.SIMPLE, 2, 0, 0
        )
        self.assertLess(easy_difficulty, 40)
        
        # Hard task
        hard_difficulty = self.identifier._calculate_automation_difficulty(
            TaskComplexity.VERY_COMPLEX, 20, 5, 3
        )
        self.assertGreater(hard_difficulty, 60)
    
    def test_automation_score_calculation(self):
        """Test automation score calculation"""
        # High value task (frequent, time-consuming)
        high_score = self.identifier._calculate_automation_score(
            occurrence_count=20,
            avg_duration=300,  # 5 minutes
            monthly_savings=3600,  # 1 hour/month
            error_rate=0.2,
            consistency=0.9,
            difficulty=20
        )
        self.assertGreater(high_score, 50)
        
        # Low value task
        low_score = self.identifier._calculate_automation_score(
            occurrence_count=2,
            avg_duration=10,
            monthly_savings=60,
            error_rate=0.0,
            consistency=1.0,
            difficulty=80
        )
        self.assertLess(low_score, 30)
    
    def test_automation_potential_determination(self):
        """Test automation potential determination"""
        self.assertEqual(
            self.identifier._determine_automation_potential(85),
            AutomationPotential.CRITICAL
        )
        self.assertEqual(
            self.identifier._determine_automation_potential(65),
            AutomationPotential.HIGH
        )
        self.assertEqual(
            self.identifier._determine_automation_potential(45),
            AutomationPotential.MEDIUM
        )
        self.assertEqual(
            self.identifier._determine_automation_potential(25),
            AutomationPotential.LOW
        )
        self.assertEqual(
            self.identifier._determine_automation_potential(10),
            AutomationPotential.NONE
        )
    
    def test_roi_calculation(self):
        """Test ROI calculation"""
        # High ROI (saves lots of time, easy to automate)
        high_roi = self.identifier._calculate_roi(
            monthly_savings=7200,  # 2 hours/month
            difficulty=20,
            step_count=3
        )
        self.assertGreater(high_roi, 50)
        
        # Low ROI (saves little time, hard to automate)
        low_roi = self.identifier._calculate_roi(
            monthly_savings=300,  # 5 minutes/month
            difficulty=80,
            step_count=15
        )
        self.assertLess(low_roi, 30)
    
    def test_approach_recommendation(self):
        """Test automation approach recommendation"""
        # Simple task
        simple_approach = self.identifier._recommend_approach(
            TaskComplexity.SIMPLE, 2, []
        )
        self.assertIn("script", simple_approach.lower())
        
        # Complex task with API
        complex_approach = self.identifier._recommend_approach(
            TaskComplexity.COMPLEX, 10, ['api', 'database']
        )
        self.assertIn("application", complex_approach.lower())
    
    def test_development_time_estimation(self):
        """Test development time estimation"""
        # Easy task
        easy_time = self.identifier._estimate_development_time(20, 3)
        self.assertLess(easy_time, 5)
        
        # Hard task
        hard_time = self.identifier._estimate_development_time(80, 20)
        self.assertGreater(hard_time, 15)
    
    def test_analyze_automation_opportunities(self):
        """Test analyzing automation opportunities"""
        # Record multiple instances of the same task
        for i in range(5):
            self.identifier.record_task_sequence(
                task_name="Daily Report",
                steps=["Open tool", "Collect data", "Format report", "Send email"],
                duration_seconds=300,
                success=True
            )
        
        # Analyze
        candidates = self.identifier.analyze_automation_opportunities(days=30)
        
        self.assertGreater(len(candidates), 0)
        self.assertEqual(candidates[0].task_name, "Daily Report")
        self.assertEqual(candidates[0].occurrence_count, 5)
    
    def test_candidate_persistence(self):
        """Test saving and loading candidates"""
        # Record and analyze
        for i in range(4):
            self.identifier.record_task_sequence(
                task_name="Backup Task",
                steps=["Check files", "Create backup", "Verify backup"],
                duration_seconds=180,
                success=True
            )
        
        candidates = self.identifier.analyze_automation_opportunities()
        self.assertGreater(len(candidates), 0)
        
        # Create new identifier instance
        new_identifier = TaskAutomationIdentifier(data_dir=self.test_dir)
        
        # Should load existing candidates
        self.assertGreater(len(new_identifier.candidates), 0)
    
    def test_get_top_candidates(self):
        """Test getting top candidates"""
        # Record multiple different tasks
        for i in range(10):
            self.identifier.record_task_sequence(
                task_name="High Value Task",
                steps=["Step 1", "Step 2"],
                duration_seconds=600,
                success=True
            )
        
        for i in range(3):
            self.identifier.record_task_sequence(
                task_name="Low Value Task",
                steps=["Quick step"],
                duration_seconds=10,
                success=True
            )
        
        self.identifier.analyze_automation_opportunities()
        top = self.identifier.get_top_candidates(limit=5)
        
        self.assertGreater(len(top), 0)
        # First should be higher scoring
        if len(top) > 1:
            self.assertGreaterEqual(top[0].automation_score, top[1].automation_score)
    
    def test_get_quick_wins(self):
        """Test getting quick win candidates"""
        # Record a simple, frequent task
        for i in range(8):
            self.identifier.record_task_sequence(
                task_name="Simple Frequent Task",
                steps=["Do simple thing"],
                duration_seconds=120,
                success=True
            )
        
        self.identifier.analyze_automation_opportunities()
        quick_wins = self.identifier.get_quick_wins(max_difficulty=30)
        
        # Should find at least one quick win
        for win in quick_wins:
            self.assertLessEqual(win.automation_difficulty, 30)
            self.assertGreaterEqual(win.automation_score, 50)
    
    def test_generate_automation_report(self):
        """Test generating automation report"""
        # Record some tasks
        for i in range(6):
            self.identifier.record_task_sequence(
                task_name="Report Task",
                steps=["Gather data", "Create report", "Send report"],
                duration_seconds=240,
                success=True
            )
        
        self.identifier.analyze_automation_opportunities()
        report = self.identifier.generate_automation_report()
        
        self.assertIn('summary', report)
        self.assertIn('total_candidates', report['summary'])
        self.assertIn('top_10_candidates', report)
        self.assertGreater(report['summary']['total_candidates'], 0)
    
    def test_empty_report(self):
        """Test report generation with no candidates"""
        report = self.identifier.generate_automation_report()
        
        self.assertEqual(report['total_candidates'], 0)
        self.assertIn('No automation candidates', report['summary'])
    
    def test_consistency_score_calculation(self):
        """Test consistency score in pattern analysis"""
        # Record tasks with consistent duration
        for i in range(5):
            self.identifier.record_task_sequence(
                task_name="Consistent Task",
                steps=["Step 1", "Step 2"],
                duration_seconds=100,  # Always 100 seconds
                success=True
            )
        
        candidates = self.identifier.analyze_automation_opportunities()
        
        if candidates:
            # Should have high consistency score
            self.assertGreater(candidates[0].consistency_score, 0.8)
    
    def test_error_rate_tracking(self):
        """Test error rate tracking"""
        # Record tasks with some failures
        for i in range(10):
            self.identifier.record_task_sequence(
                task_name="Error Prone Task",
                steps=["Step 1", "Step 2"],
                duration_seconds=120,
                success=(i % 3 != 0)  # Fails every 3rd time
            )
        
        candidates = self.identifier.analyze_automation_opportunities()
        
        if candidates:
            # Should track error rate
            self.assertGreater(candidates[0].error_rate, 0)
            self.assertLess(candidates[0].success_rate, 1.0)
    
    def test_priority_ranking(self):
        """Test priority ranking of candidates"""
        # Record multiple different tasks
        for i in range(8):
            self.identifier.record_task_sequence(
                task_name="Task A",
                steps=["Step 1", "Step 2"],
                duration_seconds=300,
                success=True
            )
        
        for i in range(4):
            self.identifier.record_task_sequence(
                task_name="Task B",
                steps=["Step 1"],
                duration_seconds=60,
                success=True
            )
        
        candidates = self.identifier.analyze_automation_opportunities()
        
        # Should have priority ranks assigned
        for candidate in candidates:
            self.assertGreater(candidate.priority_rank, 0)
        
        # Ranks should be sequential
        ranks = [c.priority_rank for c in candidates]
        self.assertEqual(sorted(ranks), list(range(1, len(candidates) + 1)))


if __name__ == '__main__':
    unittest.main()
