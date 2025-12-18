#!/usr/bin/env python3
"""
Tests for Competitive Intelligence System

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

from domain_expertise.competitive_intelligence import (
    CompetitiveIntelligence,
    CompetitorSize,
    MarketPosition,
    StrategicMove,
    ThreatLevel,
    CompetitorProfile,
    SWOTAnalysis,
    ProductComparison,
    StrategicMoveRecord,
    CompetitiveOpportunity
)


class TestCompetitiveIntelligence(unittest.TestCase):
    """Test cases for CompetitiveIntelligence."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.ci = CompetitiveIntelligence(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test competitive intelligence initialization."""
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertIsInstance(self.ci.competitors, dict)
        
        # Should have example competitors initialized
        self.assertGreater(len(self.ci.competitors), 0)
    
    def test_profile_competitor(self):
        """Test profiling a competitor."""
        competitor = self.ci.profile_competitor(
            name="TestCorp",
            industry="Technology",
            size=CompetitorSize.MEDIUM.value,
            market_position=MarketPosition.CHALLENGER.value,
            products=["Product A", "Product B"],
            strengths=["Innovation", "Agility"],
            weaknesses=["Limited resources"]
        )
        
        self.assertIsInstance(competitor, CompetitorProfile)
        self.assertEqual(competitor.name, "TestCorp")
        self.assertIn(competitor.competitor_id, self.ci.competitors)
    
    def test_update_competitor(self):
        """Test updating competitor information."""
        competitor = self.ci.profile_competitor(
            name="UpdateCorp",
            industry="Technology",
            size=CompetitorSize.SMALL.value,
            market_position=MarketPosition.FOLLOWER.value
        )
        
        self.ci.update_competitor(
            competitor.competitor_id,
            {'market_share': 0.15, 'threat_level': ThreatLevel.HIGH.value}
        )
        
        updated = self.ci.competitors[competitor.competitor_id]
        self.assertEqual(updated['market_share'], 0.15)
        self.assertEqual(updated['threat_level'], ThreatLevel.HIGH.value)
    
    def test_conduct_swot_analysis(self):
        """Test conducting SWOT analysis."""
        competitor = self.ci.profile_competitor(
            name="SWOTCorp",
            industry="Technology",
            size=CompetitorSize.LARGE.value,
            market_position=MarketPosition.LEADER.value
        )
        
        swot = self.ci.conduct_swot_analysis(
            competitor.competitor_id,
            strengths=["Market leader", "Strong brand"],
            weaknesses=["High costs", "Slow innovation"],
            opportunities=["New markets", "Technology trends"],
            threats=["Disruption", "New entrants"],
            overall_assessment="Strong but vulnerable",
            strategic_recommendations=["Invest in R&D", "Reduce costs"]
        )
        
        self.assertIsInstance(swot, SWOTAnalysis)
        self.assertEqual(len(swot.strengths), 2)
        self.assertEqual(len(swot.strategic_recommendations), 2)
        self.assertIn(swot.analysis_id, self.ci.swot_analyses)
    
    def test_compare_products(self):
        """Test product comparison."""
        competitor = self.ci.profile_competitor(
            name="ProductCorp",
            industry="Technology",
            size=CompetitorSize.MEDIUM.value,
            market_position=MarketPosition.CHALLENGER.value
        )
        
        comparison = self.ci.compare_products(
            our_product="Our Product",
            competitor_product="Their Product",
            competitor_id=competitor.competitor_id,
            features={
                'feature1': {'ours': 10, 'theirs': 8},
                'feature2': {'ours': 7, 'theirs': 9}
            },
            pricing={'ours': 99.99, 'theirs': 129.99},
            performance={'speed': {'ours': 0.9, 'theirs': 0.7}}
        )
        
        self.assertIsInstance(comparison, ProductComparison)
        self.assertIn(comparison.winner, ['ours', 'theirs', 'tie'])
        self.assertIn(comparison.comparison_id, self.ci.product_comparisons)
    
    def test_product_winner_determination(self):
        """Test product winner determination logic."""
        # Our product should win (better features, better price, better performance)
        winner = self.ci._determine_product_winner(
            features={'f1': {'ours': 10, 'theirs': 5}},
            pricing={'ours': 50, 'theirs': 100},
            performance={'speed': {'ours': 0.9, 'theirs': 0.5}}
        )
        self.assertEqual(winner, 'ours')
        
        # Their product should win
        winner = self.ci._determine_product_winner(
            features={'f1': {'ours': 5, 'theirs': 10}},
            pricing={'ours': 100, 'theirs': 50},
            performance={'speed': {'ours': 0.5, 'theirs': 0.9}}
        )
        self.assertEqual(winner, 'theirs')
    
    def test_analyze_product_differences(self):
        """Test product difference analysis."""
        gaps, advantages = self.ci._analyze_product_differences(
            features={'f1': {'ours': 5, 'theirs': 10}, 'f2': {'ours': 10, 'theirs': 5}},
            pricing={'ours': 100, 'theirs': 80},
            performance={'speed': {'ours': 0.9, 'theirs': 0.7}}
        )
        
        self.assertGreater(len(gaps), 0)
        self.assertGreater(len(advantages), 0)
    
    def test_track_strategic_move(self):
        """Test tracking strategic moves."""
        competitor = self.ci.profile_competitor(
            name="MoveCorp",
            industry="Technology",
            size=CompetitorSize.LARGE.value,
            market_position=MarketPosition.LEADER.value
        )
        
        move = self.ci.track_strategic_move(
            competitor.competitor_id,
            move_type=StrategicMove.PRODUCT_LAUNCH.value,
            description="Launched new AI product",
            impact_assessment="High impact on market",
            threat_level=ThreatLevel.HIGH.value,
            our_response="Accelerate our AI development"
        )
        
        self.assertIsInstance(move, StrategicMoveRecord)
        self.assertEqual(move.move_type, StrategicMove.PRODUCT_LAUNCH.value)
        self.assertIn(move.move_id, self.ci.strategic_moves)
        
        # Threat level should be updated
        updated_competitor = self.ci.competitors[competitor.competitor_id]
        self.assertEqual(updated_competitor['threat_level'], ThreatLevel.HIGH.value)
    
    def test_identify_opportunity(self):
        """Test opportunity identification."""
        opportunity = self.ci.identify_opportunity(
            title="Market Gap in AI Tools",
            description="Competitors lack user-friendly AI tools",
            opportunity_type="market_gap",
            potential_impact="high",
            required_resources=["Development team", "Marketing budget"],
            estimated_timeframe="6 months",
            competitors_affected=["comp_0001", "comp_0002"]
        )
        
        self.assertIsInstance(opportunity, CompetitiveOpportunity)
        self.assertEqual(opportunity.potential_impact, "high")
        self.assertIn(opportunity.opportunity_id, self.ci.opportunities)
    
    def test_analyze_market_position(self):
        """Test market position analysis."""
        # Add some competitors first
        self.ci.profile_competitor(
            name="Leader1",
            industry="Tech",
            size=CompetitorSize.LARGE.value,
            market_position=MarketPosition.LEADER.value,
            strengths=["Brand", "Resources"],
            weaknesses=["Slow"]
        )
        
        analysis = self.ci.analyze_market_position(
            our_market_share=0.15,
            our_strengths=["Innovation", "Agility"],
            our_weaknesses=["Limited resources"]
        )
        
        self.assertIn('our_market_share', analysis)
        self.assertIn('competitors_by_threat', analysis)
        self.assertIn('market_leaders', analysis)
        self.assertIn('strategic_recommendations', analysis)
        self.assertGreater(len(analysis['strategic_recommendations']), 0)
    
    def test_strategic_recommendations_generation(self):
        """Test strategic recommendations generation."""
        # Low market share
        recs = self.ci._generate_strategic_recommendations(
            market_share=0.05,
            strengths=["Innovation"],
            weaknesses=["Resources", "Brand"],
            gaps=["Gap1", "Gap2"]
        )
        self.assertGreater(len(recs), 0)
        
        # High market share
        recs = self.ci._generate_strategic_recommendations(
            market_share=0.35,
            strengths=["Brand", "Resources", "Innovation"],
            weaknesses=["Cost"],
            gaps=[]
        )
        self.assertGreater(len(recs), 0)
    
    def test_get_competitor_intelligence(self):
        """Test getting comprehensive competitor intelligence."""
        competitor = self.ci.profile_competitor(
            name="IntelCorp",
            industry="Technology",
            size=CompetitorSize.MEDIUM.value,
            market_position=MarketPosition.CHALLENGER.value
        )
        
        # Add SWOT
        self.ci.conduct_swot_analysis(
            competitor.competitor_id,
            strengths=["S1"],
            weaknesses=["W1"],
            opportunities=["O1"],
            threats=["T1"],
            overall_assessment="Test"
        )
        
        # Add strategic move
        self.ci.track_strategic_move(
            competitor.competitor_id,
            move_type=StrategicMove.ACQUISITION.value,
            description="Acquired startup",
            impact_assessment="Medium",
            threat_level=ThreatLevel.MEDIUM.value
        )
        
        intel = self.ci.get_competitor_intelligence(competitor.competitor_id)
        
        self.assertIn('profile', intel)
        self.assertIn('swot_analyses', intel)
        self.assertIn('product_comparisons', intel)
        self.assertIn('strategic_moves', intel)
        self.assertIn('threat_assessment', intel)
        
        self.assertEqual(len(intel['swot_analyses']), 1)
        self.assertEqual(len(intel['strategic_moves']), 1)
    
    def test_assess_overall_threat(self):
        """Test overall threat assessment."""
        competitor = {
            'market_position': MarketPosition.LEADER.value,
            'market_share': 0.4,
            'threat_level': ThreatLevel.HIGH.value,
            'competitive_advantages': ['A1', 'A2', 'A3', 'A4']
        }
        
        moves = [
            {'threat_level': ThreatLevel.HIGH.value},
            {'threat_level': ThreatLevel.CRITICAL.value}
        ]
        
        assessment = self.ci._assess_overall_threat(competitor, moves)
        
        self.assertIn('current_threat_level', assessment)
        self.assertIn('threat_factors', assessment)
        self.assertIn('recommendation', assessment)
        self.assertGreater(len(assessment['threat_factors']), 0)
    
    def test_threat_response_recommendation(self):
        """Test threat response recommendations."""
        critical_rec = self.ci._get_threat_response_recommendation(ThreatLevel.CRITICAL.value)
        self.assertIn('Immediate', critical_rec)
        
        low_rec = self.ci._get_threat_response_recommendation(ThreatLevel.LOW.value)
        self.assertIn('Periodic', low_rec)
    
    def test_find_competitors(self):
        """Test finding competitors with filters."""
        # Add test competitors
        self.ci.profile_competitor(
            name="TechCorp1",
            industry="Technology",
            size=CompetitorSize.LARGE.value,
            market_position=MarketPosition.LEADER.value,
            threat_level=ThreatLevel.HIGH.value
        )
        
        self.ci.profile_competitor(
            name="TechCorp2",
            industry="Technology",
            size=CompetitorSize.SMALL.value,
            market_position=MarketPosition.FOLLOWER.value,
            threat_level=ThreatLevel.LOW.value
        )
        
        # Find by industry
        results = self.ci.find_competitors(industry="Technology")
        self.assertGreater(len(results), 0)
        
        # Find by threat level
        high_threat = self.ci.find_competitors(min_threat_level=ThreatLevel.HIGH.value)
        for comp in high_threat:
            self.assertIn(comp['threat_level'], [ThreatLevel.HIGH.value, ThreatLevel.CRITICAL.value])
        
        # Find by market position
        leaders = self.ci.find_competitors(market_position=MarketPosition.LEADER.value)
        for comp in leaders:
            self.assertEqual(comp['market_position'], MarketPosition.LEADER.value)
    
    def test_get_intelligence_summary(self):
        """Test getting intelligence summary."""
        summary = self.ci.get_intelligence_summary()
        
        self.assertIn('total_competitors', summary)
        self.assertIn('competitors_by_position', summary)
        self.assertIn('competitors_by_threat', summary)
        self.assertIn('total_swot_analyses', summary)
        self.assertIn('total_product_comparisons', summary)
        self.assertIn('total_strategic_moves', summary)
        self.assertIn('total_opportunities', summary)
        self.assertIn('high_threat_competitors', summary)
        
        self.assertGreater(summary['total_competitors'], 0)
    
    def test_count_by_field(self):
        """Test counting competitors by field."""
        counts = self.ci._count_by_field('market_position')
        self.assertIsInstance(counts, dict)
    
    def test_persistence(self):
        """Test that data persists across instances."""
        competitor = self.ci.profile_competitor(
            name="PersistCorp",
            industry="Technology",
            size=CompetitorSize.MEDIUM.value,
            market_position=MarketPosition.CHALLENGER.value
        )
        
        # Create new instance
        ci2 = CompetitiveIntelligence(data_dir=self.test_dir)
        
        # Should load saved data
        self.assertIn(competitor.competitor_id, ci2.competitors)
        loaded = ci2.competitors[competitor.competitor_id]
        self.assertEqual(loaded['name'], 'PersistCorp')
    
    def test_intelligence_log(self):
        """Test that activities are logged."""
        initial_log_length = len(self.ci.intelligence_log)
        
        self.ci.profile_competitor(
            name="LogCorp",
            industry="Technology",
            size=CompetitorSize.SMALL.value,
            market_position=MarketPosition.FOLLOWER.value
        )
        
        self.assertGreater(len(self.ci.intelligence_log), initial_log_length)


if __name__ == '__main__':
    unittest.main()
