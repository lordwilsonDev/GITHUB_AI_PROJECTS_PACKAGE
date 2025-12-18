"""
Tests for Knowledge Acquisition System
"""

import pytest
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/Users/lordwilson/vy-nexus/self-evolving-ecosystem/feature-07-knowledge-acquisition/src')

from knowledge_acquisition import (
    TechnicalLearningSystem,
    DomainExpertiseTracker,
    BehavioralLearningAnalyzer,
    CompetitiveResearchSystem,
    UseCaseOptimizer,
    KnowledgeAcquisitionEngine,
    KnowledgeItem,
    KnowledgeArea,
    ProficiencyLevel,
    LearningGoal,
    BehavioralPattern
)


class TestTechnicalLearningSystem:
    """Test technical learning system"""
    
    def test_add_knowledge(self):
        system = TechnicalLearningSystem()
        item = KnowledgeItem(
            topic="Python",
            area=KnowledgeArea.PROGRAMMING,
            proficiency=ProficiencyLevel.EXPERT,
            confidence=0.9,
            last_used=datetime.now()
        )
        system.add_knowledge(item)
        assert "Python" in system.knowledge_base
        assert len(system.learning_history) == 1
    
    def test_update_proficiency(self):
        system = TechnicalLearningSystem()
        item = KnowledgeItem(
            topic="JavaScript",
            area=KnowledgeArea.PROGRAMMING,
            proficiency=ProficiencyLevel.BEGINNER,
            confidence=0.5,
            last_used=datetime.now()
        )
        system.add_knowledge(item)
        system.update_proficiency("JavaScript", ProficiencyLevel.INTERMEDIATE, 0.7)
        assert system.knowledge_base["JavaScript"].proficiency == ProficiencyLevel.INTERMEDIATE
        assert system.knowledge_base["JavaScript"].confidence == 0.7
    
    def test_record_application(self):
        system = TechnicalLearningSystem()
        item = KnowledgeItem(
            topic="React",
            area=KnowledgeArea.FRAMEWORKS,
            proficiency=ProficiencyLevel.INTERMEDIATE,
            confidence=0.7,
            last_used=datetime.now()
        )
        system.add_knowledge(item)
        
        # Record successful applications
        system.record_application("React", True)
        system.record_application("React", True)
        system.record_application("React", False)
        
        assert system.knowledge_base["React"].times_applied == 3
        assert abs(system.knowledge_base["React"].success_rate - 0.667) < 0.01
    
    def test_create_learning_goal(self):
        system = TechnicalLearningSystem()
        goal = system.create_learning_goal(
            "Rust",
            KnowledgeArea.PROGRAMMING,
            ProficiencyLevel.INTERMEDIATE,
            0.8
        )
        assert len(system.learning_goals) == 1
        assert goal.topic == "Rust"
        assert goal.priority == 0.8
    
    def test_get_learning_priorities(self):
        system = TechnicalLearningSystem()
        system.create_learning_goal("Go", KnowledgeArea.PROGRAMMING, ProficiencyLevel.ADVANCED, 0.9)
        system.create_learning_goal("Kotlin", KnowledgeArea.PROGRAMMING, ProficiencyLevel.BEGINNER, 0.5)
        system.create_learning_goal("Swift", KnowledgeArea.PROGRAMMING, ProficiencyLevel.INTERMEDIATE, 0.7)
        
        priorities = system.get_learning_priorities()
        assert len(priorities) == 3
        assert priorities[0].topic == "Go"  # Highest priority
        assert priorities[2].topic == "Kotlin"  # Lowest priority
    
    def test_identify_knowledge_gaps(self):
        system = TechnicalLearningSystem()
        
        # Add item with low success rate
        item = KnowledgeItem(
            topic="C++",
            area=KnowledgeArea.PROGRAMMING,
            proficiency=ProficiencyLevel.BEGINNER,
            confidence=0.5,
            last_used=datetime.now(),
            times_applied=10,
            success_rate=0.4
        )
        system.add_knowledge(item)
        
        gaps = system.identify_knowledge_gaps()
        assert len(gaps) > 0
        assert any(g.get('topic') == 'C++' for g in gaps)
    
    def test_expertise_summary(self):
        system = TechnicalLearningSystem()
        
        for i in range(5):
            item = KnowledgeItem(
                topic=f"Topic{i}",
                area=KnowledgeArea.PROGRAMMING,
                proficiency=ProficiencyLevel.INTERMEDIATE,
                confidence=0.7,
                last_used=datetime.now(),
                times_applied=5,
                success_rate=0.8
            )
            system.add_knowledge(item)
        
        summary = system.get_expertise_summary()
        assert summary['total_topics'] == 5
        assert summary['avg_success_rate'] == 0.8
        assert summary['total_applications'] == 25


class TestDomainExpertiseTracker:
    """Test domain expertise tracker"""
    
    def test_add_domain(self):
        tracker = DomainExpertiseTracker()
        tracker.add_domain("AI/ML", "Artificial Intelligence", 0.9)
        assert "AI/ML" in tracker.domains
        assert tracker.domains["AI/ML"]['importance'] == 0.9
    
    def test_add_domain_knowledge(self):
        tracker = DomainExpertiseTracker()
        tracker.add_domain("Web Development", "Web dev", 0.7)
        
        item = KnowledgeItem(
            topic="REST APIs",
            area=KnowledgeArea.DOMAIN_SPECIFIC,
            proficiency=ProficiencyLevel.ADVANCED,
            confidence=0.85,
            last_used=datetime.now()
        )
        tracker.add_domain_knowledge("Web Development", item)
        
        assert len(tracker.domain_knowledge["Web Development"]) == 1
    
    def test_record_insight(self):
        tracker = DomainExpertiseTracker()
        tracker.add_domain("Finance", "Financial domain", 0.8)
        tracker.record_insight("Finance", "Market trends indicate growth", 0.75)
        
        assert len(tracker.insights) == 1
        assert tracker.domains["Finance"]['insights_count'] == 1
    
    def test_update_domain_proficiency(self):
        tracker = DomainExpertiseTracker()
        tracker.add_domain("Healthcare", "Healthcare domain", 0.85)
        tracker.update_domain_proficiency("Healthcare", ProficiencyLevel.EXPERT)
        
        assert tracker.domains["Healthcare"]['proficiency'] == ProficiencyLevel.EXPERT
    
    def test_get_domain_summary(self):
        tracker = DomainExpertiseTracker()
        tracker.add_domain("E-commerce", "Online retail", 0.75)
        tracker.record_insight("E-commerce", "Mobile shopping increasing", 0.8)
        
        summary = tracker.get_domain_summary("E-commerce")
        assert summary is not None
        assert summary['importance'] == 0.75
        assert len(summary['recent_insights']) == 1
    
    def test_get_top_domains(self):
        tracker = DomainExpertiseTracker()
        tracker.add_domain("AI", "AI domain", 0.9)
        tracker.update_domain_proficiency("AI", ProficiencyLevel.EXPERT)
        
        tracker.add_domain("Blockchain", "Blockchain domain", 0.5)
        tracker.update_domain_proficiency("Blockchain", ProficiencyLevel.BEGINNER)
        
        top = tracker.get_top_domains(2)
        assert len(top) <= 2
        assert top[0]['domain'] == "AI"  # Higher score


class TestBehavioralLearningAnalyzer:
    """Test behavioral learning analyzer"""
    
    def test_observe_behavior(self):
        analyzer = BehavioralLearningAnalyzer()
        analyzer.observe_behavior(
            "decision_making",
            "Prefers data-driven decisions",
            {"context": "planning"}
        )
        
        assert len(analyzer.observations) == 1
        assert len(analyzer.patterns) == 1
    
    def test_pattern_confidence_increase(self):
        analyzer = BehavioralLearningAnalyzer()
        
        # Observe same pattern multiple times
        for _ in range(5):
            analyzer.observe_behavior(
                "timing",
                "Works best in morning",
                {"time": "morning"}
            )
        
        pattern_key = "timing:Works best in morning"
        assert analyzer.patterns[pattern_key].observed_count == 5
        assert analyzer.patterns[pattern_key].confidence > 0.3
    
    def test_get_patterns_by_type(self):
        analyzer = BehavioralLearningAnalyzer()
        analyzer.observe_behavior("timing", "Morning person", {})
        analyzer.observe_behavior("timing", "Afternoon slump", {})
        analyzer.observe_behavior("communication", "Prefers brief updates", {})
        
        timing_patterns = analyzer.get_patterns_by_type("timing")
        assert len(timing_patterns) == 2
    
    def test_get_high_confidence_patterns(self):
        analyzer = BehavioralLearningAnalyzer()
        
        # Create high confidence pattern
        for _ in range(10):
            analyzer.observe_behavior("preference", "Likes automation", {})
        
        # Create low confidence pattern
        analyzer.observe_behavior("preference", "Uncertain preference", {})
        
        high_conf = analyzer.get_high_confidence_patterns(0.7)
        assert len(high_conf) >= 1
    
    def test_predict_behavior(self):
        analyzer = BehavioralLearningAnalyzer()
        
        # Build strong pattern
        for _ in range(15):
            analyzer.observe_behavior(
                "work_style",
                "Focused work sessions",
                {"duration": "90min"}
            )
        
        prediction = analyzer.predict_behavior("work_style", {})
        assert prediction == "Focused work sessions"
    
    def test_behavioral_summary(self):
        analyzer = BehavioralLearningAnalyzer()
        
        for i in range(5):
            analyzer.observe_behavior(f"type{i % 3}", f"Pattern {i}", {})
        
        summary = analyzer.get_behavioral_summary()
        assert summary['total_patterns'] == 5
        assert summary['total_observations'] == 5


class TestCompetitiveResearchSystem:
    """Test competitive research system"""
    
    def test_add_competitor(self):
        system = CompetitiveResearchSystem()
        system.add_competitor(
            "CompanyA",
            "AI Tools",
            ["Fast", "Accurate"],
            ["Expensive", "Complex"]
        )
        
        assert "CompanyA" in system.competitors
        assert len(system.competitors["CompanyA"]['strengths']) == 2
    
    def test_record_market_insight(self):
        system = CompetitiveResearchSystem()
        system.record_market_insight(
            "AI Tools",
            "Market growing 30% annually",
            0.8
        )
        
        assert len(system.market_insights) == 1
        assert system.market_insights[0]['impact'] == 0.8
    
    def test_record_trend(self):
        system = CompetitiveResearchSystem()
        system.record_trend(
            "AI automation",
            "Productivity",
            0.9
        )
        
        assert len(system.trends) == 1
        assert system.trends[0]['momentum'] == 0.9
    
    def test_get_competitive_analysis(self):
        system = CompetitiveResearchSystem()
        system.add_competitor("CompA", "AI", ["Fast"], ["Expensive"])
        system.add_competitor("CompB", "AI", ["Cheap"], ["Slow"])
        system.record_market_insight("AI", "Growing market", 0.8)
        
        analysis = system.get_competitive_analysis("AI")
        assert analysis['competitor_count'] == 2
        assert len(analysis['insights']) == 1
    
    def test_identify_opportunities(self):
        system = CompetitiveResearchSystem()
        
        # Multiple competitors with same weakness
        system.add_competitor("CompA", "AI", ["Fast"], ["Poor UX"])
        system.add_competitor("CompB", "AI", ["Cheap"], ["Poor UX"])
        system.add_competitor("CompC", "AI", ["Accurate"], ["Poor UX"])
        
        opportunities = system.identify_opportunities("AI")
        assert len(opportunities) > 0
        assert any(o['description'] == "Poor UX" for o in opportunities)


class TestUseCaseOptimizer:
    """Test use case optimizer"""
    
    def test_add_use_case(self):
        optimizer = UseCaseOptimizer()
        optimizer.add_use_case(
            "code_generation",
            "Generate Python code",
            frequency=5.0,
            importance=0.8
        )
        
        assert "code_generation" in optimizer.use_cases
        assert optimizer.use_cases["code_generation"]['frequency'] == 5.0
    
    def test_record_optimization(self):
        optimizer = UseCaseOptimizer()
        optimizer.add_use_case("data_analysis", "Analyze data", 3.0, 0.7)
        optimizer.record_optimization(
            "data_analysis",
            "Added caching",
            0.3  # 30% improvement
        )
        
        assert len(optimizer.optimizations) == 1
        assert optimizer.use_cases["data_analysis"]['optimizations_applied'] == 1
        assert optimizer.use_cases["data_analysis"]['performance_improvement'] == 0.3
    
    def test_get_optimization_priorities(self):
        optimizer = UseCaseOptimizer()
        
        # High frequency, high importance
        optimizer.add_use_case("uc1", "Use case 1", 10.0, 0.9)
        
        # Low frequency, low importance
        optimizer.add_use_case("uc2", "Use case 2", 1.0, 0.3)
        
        priorities = optimizer.get_optimization_priorities()
        assert len(priorities) == 2
        assert priorities[0]['use_case'] == "uc1"  # Higher priority
    
    def test_get_use_case_summary(self):
        optimizer = UseCaseOptimizer()
        optimizer.add_use_case("reporting", "Generate reports", 2.0, 0.6)
        optimizer.record_optimization("reporting", "Parallel processing", 0.5)
        
        summary = optimizer.get_use_case_summary("reporting")
        assert summary is not None
        assert len(summary['optimizations']) == 1
        assert summary['performance_improvement'] == 0.5


class TestKnowledgeAcquisitionEngine:
    """Test knowledge acquisition engine"""
    
    def test_engine_initialization(self):
        engine = KnowledgeAcquisitionEngine(cycle_interval_minutes=30)
        
        assert engine.technical_learning is not None
        assert engine.domain_expertise is not None
        assert engine.behavioral_learning is not None
        assert engine.competitive_research is not None
        assert engine.use_case_optimizer is not None
    
    @pytest.mark.asyncio
    async def test_run_acquisition_cycle(self):
        engine = KnowledgeAcquisitionEngine(cycle_interval_minutes=30)
        
        # Add some data
        item = KnowledgeItem(
            topic="Python",
            area=KnowledgeArea.PROGRAMMING,
            proficiency=ProficiencyLevel.EXPERT,
            confidence=0.9,
            last_used=datetime.now()
        )
        engine.technical_learning.add_knowledge(item)
        
        result = await engine.run_acquisition_cycle()
        
        assert 'cycle_time' in result
        assert 'learning_gaps' in result
        assert 'behavioral_patterns' in result
    
    def test_get_acquisition_report(self):
        engine = KnowledgeAcquisitionEngine()
        
        # Add some data
        item = KnowledgeItem(
            topic="JavaScript",
            area=KnowledgeArea.PROGRAMMING,
            proficiency=ProficiencyLevel.INTERMEDIATE,
            confidence=0.7,
            last_used=datetime.now()
        )
        engine.technical_learning.add_knowledge(item)
        
        engine.domain_expertise.add_domain("Web Dev", "Web development", 0.8)
        engine.behavioral_learning.observe_behavior("timing", "Morning person", {})
        engine.use_case_optimizer.add_use_case("testing", "Run tests", 5.0, 0.7)
        
        report = engine.get_acquisition_report()
        
        assert 'technical_expertise' in report
        assert 'domain_expertise' in report
        assert 'behavioral_learning' in report
        assert 'competitive_intelligence' in report
        assert 'use_case_optimization' in report
        assert report['technical_expertise']['total_topics'] == 1
        assert report['domain_expertise']['domains'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
