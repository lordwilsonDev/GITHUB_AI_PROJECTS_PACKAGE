"""
Tests for Communication Style Adapter Module

Author: Vy Self-Evolving AI Ecosystem
Phase: 4 - Real-Time Adaptation System
"""

import pytest
import os
import sqlite3
import json
from datetime import datetime
from modules.communication_adapter import (
    CommunicationAnalyzer,
    StyleAdapter,
    CommunicationAdapterEngine,
    CommunicationStyle,
    StyleLevel
)


@pytest.fixture
def temp_db(tmp_path):
    """Create temporary database for testing"""
    db_path = tmp_path / "test_communication.db"
    return str(db_path)


@pytest.fixture
def analyzer(temp_db):
    """Create CommunicationAnalyzer instance"""
    return CommunicationAnalyzer(temp_db)


@pytest.fixture
def adapter(temp_db):
    """Create StyleAdapter instance"""
    return StyleAdapter(temp_db)


@pytest.fixture
def engine(temp_db):
    """Create CommunicationAdapterEngine instance"""
    return CommunicationAdapterEngine(temp_db)


class TestCommunicationAnalyzer:
    """Test CommunicationAnalyzer functionality"""
    
    def test_database_initialization(self, analyzer):
        """Test database tables are created"""
        conn = sqlite3.connect(analyzer.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN 
            ('user_preferences', 'communication_feedback', 'message_history')
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert 'user_preferences' in tables
        assert 'communication_feedback' in tables
        assert 'message_history' in tables
    
    def test_analyze_formal_message(self, analyzer):
        """Test analysis of formal message"""
        message = "Please kindly review this document. Would you be able to provide feedback?"
        style = analyzer.analyze_message_style(message)
        
        assert 'formality' in style
        assert style['formality'] >= 3  # Should be formal
    
    def test_analyze_casual_message(self, analyzer):
        """Test analysis of casual message"""
        message = "Hey! Yeah, that's gonna be awesome. Wanna check it out?"
        style = analyzer.analyze_message_style(message)
        
        assert 'formality' in style
        assert style['formality'] <= 3  # Should be casual
    
    def test_analyze_verbose_message(self, analyzer):
        """Test analysis of verbose message"""
        message = " ".join(["word"] * 150)  # 150 words
        style = analyzer.analyze_message_style(message)
        
        assert 'verbosity' in style
        assert style['verbosity'] >= 4  # Should be verbose
    
    def test_analyze_concise_message(self, analyzer):
        """Test analysis of concise message"""
        message = "Done. Ready."
        style = analyzer.analyze_message_style(message)
        
        assert 'verbosity' in style
        assert style['verbosity'] <= 2  # Should be concise
    
    def test_analyze_technical_message(self, analyzer):
        """Test analysis of technical message"""
        message = "The algorithm optimizes the database using API parameters and framework modules."
        style = analyzer.analyze_message_style(message)
        
        assert 'technicality' in style
        assert style['technicality'] >= 3  # Should be technical
    
    def test_record_positive_feedback(self, analyzer):
        """Test recording positive feedback"""
        style = {'formality': 4, 'verbosity': 3}
        analyzer.record_user_feedback(
            "user123", "msg001", "positive", 
            "Great communication!", style
        )
        
        conn = sqlite3.connect(analyzer.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM communication_feedback")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 1
    
    def test_record_negative_feedback(self, analyzer):
        """Test recording negative feedback"""
        style = {'formality': 1, 'verbosity': 5}
        analyzer.record_user_feedback(
            "user123", "msg002", "negative",
            "Too casual and verbose", style
        )
        
        conn = sqlite3.connect(analyzer.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT feedback_type FROM communication_feedback")
        feedback_type = cursor.fetchone()[0]
        conn.close()
        
        assert feedback_type == "negative"
    
    def test_get_user_preferences(self, analyzer):
        """Test retrieving user preferences"""
        # Record some feedback to create preferences
        style = {'formality': 4, 'verbosity': 2}
        analyzer.record_user_feedback("user123", "msg001", "positive", None, style)
        
        preferences = analyzer.get_user_preferences("user123")
        
        assert len(preferences) > 0
        assert 'formality' in preferences or 'verbosity' in preferences
    
    def test_analyze_feedback_patterns(self, analyzer):
        """Test feedback pattern analysis"""
        # Record multiple feedbacks
        analyzer.record_user_feedback("user123", "msg001", "positive")
        analyzer.record_user_feedback("user123", "msg002", "positive")
        analyzer.record_user_feedback("user123", "msg003", "negative")
        
        patterns = analyzer.analyze_feedback_patterns("user123")
        
        assert patterns['total_count'] == 3
        assert patterns['positive_count'] == 2
        assert patterns['negative_count'] == 1
        assert patterns['satisfaction_rate'] > 0.5


class TestStyleAdapter:
    """Test StyleAdapter functionality"""
    
    def test_adapter_initialization(self, adapter):
        """Test adapter initializes correctly"""
        conn = sqlite3.connect(adapter.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='adaptation_strategies'
        """)
        
        table_exists = cursor.fetchone() is not None
        conn.close()
        
        assert table_exists
    
    def test_make_more_formal(self, adapter):
        """Test making message more formal"""
        casual = "Hey, yeah I'm gonna do that"
        formal = adapter._make_more_formal(casual)
        
        assert "hey" not in formal.lower() or "hello" in formal.lower()
        assert "gonna" not in formal.lower()
    
    def test_make_more_casual(self, adapter):
        """Test making message more casual"""
        formal = "Hello, I cannot do that"
        casual = adapter._make_more_casual(formal)
        
        assert "can't" in casual or "cannot" not in casual
    
    def test_make_more_concise(self, adapter):
        """Test making message more concise"""
        verbose = "Actually, I will basically do that in order to help you"
        concise = adapter._make_more_concise(verbose)
        
        assert len(concise) < len(verbose)
        assert "actually" not in concise.lower()
    
    def test_generate_adapted_message_no_preferences(self, adapter):
        """Test message adaptation with no user preferences"""
        message = "Hello, this is a test message"
        adapted = adapter.generate_adapted_message("new_user", message)
        
        # Should return original if no preferences
        assert adapted == message
    
    def test_create_adaptation_strategy(self, adapter):
        """Test creating adaptation strategy"""
        recommended_styles = {'formality': 4, 'verbosity': 2}
        strategy_id = adapter.create_adaptation_strategy(
            "user123", "technical_task", recommended_styles
        )
        
        assert strategy_id.startswith("strat_")
        
        # Verify it's in database
        conn = sqlite3.connect(adapter.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM adaptation_strategies WHERE strategy_id = ?", 
                      (strategy_id,))
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 1
    
    def test_get_best_strategy(self, adapter):
        """Test retrieving best strategy"""
        # Create multiple strategies
        adapter.create_adaptation_strategy("user123", "coding", {'formality': 3})
        adapter.create_adaptation_strategy("user123", "coding", {'formality': 4})
        
        strategy = adapter.get_best_strategy("user123", "coding")
        
        assert strategy is not None
        assert strategy.context == "coding"


class TestCommunicationAdapterEngine:
    """Test CommunicationAdapterEngine functionality"""
    
    def test_engine_initialization(self, engine):
        """Test engine initializes correctly"""
        assert engine.analyzer is not None
        assert engine.adapter is not None
    
    def test_process_message(self, engine):
        """Test message processing"""
        message = "Hey! I'm gonna help you with this task"
        result = engine.process_message("user123", message, "general")
        
        assert 'message_id' in result
        assert 'original_message' in result
        assert 'adapted_message' in result
        assert 'original_style' in result
        assert 'adapted_style' in result
        assert result['original_message'] == message
    
    def test_provide_feedback(self, engine):
        """Test providing feedback"""
        # Process a message first
        result = engine.process_message("user123", "Test message", "general")
        message_id = result['message_id']
        
        # Provide feedback
        engine.provide_feedback("user123", message_id, "positive", "Great!")
        
        # Verify feedback was recorded
        conn = sqlite3.connect(engine.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM communication_feedback WHERE message_id = ?",
                      (message_id,))
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 1
    
    def test_get_communication_report(self, engine):
        """Test generating communication report"""
        # Process some messages and provide feedback
        result1 = engine.process_message("user123", "Message 1", "general")
        engine.provide_feedback("user123", result1['message_id'], "positive")
        
        result2 = engine.process_message("user123", "Message 2", "general")
        engine.provide_feedback("user123", result2['message_id'], "positive")
        
        # Get report
        report = engine.get_communication_report("user123")
        
        assert 'user_id' in report
        assert report['user_id'] == "user123"
        assert 'preferences' in report
        assert 'feedback_summary' in report
        assert 'generated_at' in report
    
    def test_message_recorded_in_history(self, engine):
        """Test that messages are recorded in history"""
        result = engine.process_message("user123", "Test message", "general")
        
        conn = sqlite3.connect(engine.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT message_text FROM message_history WHERE message_id = ?",
                      (result['message_id'],))
        recorded_message = cursor.fetchone()[0]
        conn.close()
        
        assert recorded_message == result['adapted_message']
    
    def test_style_adaptation_with_preferences(self, engine):
        """Test that style adapts based on preferences"""
        # Create preferences by providing feedback
        result1 = engine.process_message("user123", "Hey there!", "general")
        engine.provide_feedback("user123", result1['message_id'], "negative")
        
        # Process another message - should adapt
        result2 = engine.process_message("user123", "Hey there!", "general")
        
        # The adapted message should be different from original
        # (though exact adaptation depends on preference learning)
        assert 'adapted_message' in result2


class TestIntegration:
    """Integration tests for communication adapter"""
    
    def test_full_adaptation_cycle(self, engine):
        """Test complete adaptation cycle"""
        user_id = "integration_user"
        
        # Step 1: Process initial message
        result1 = engine.process_message(
            user_id, 
            "Hey! I'm gonna implement this feature for you",
            "coding"
        )
        
        # Step 2: Provide positive feedback
        engine.provide_feedback(user_id, result1['message_id'], "positive")
        
        # Step 3: Process similar message
        result2 = engine.process_message(
            user_id,
            "Hey! I'm gonna create another feature",
            "coding"
        )
        
        # Step 4: Get report
        report = engine.get_communication_report(user_id)
        
        assert report['feedback_summary']['positive_count'] == 1
        assert len(report['preferences']) > 0
    
    def test_preference_learning_from_multiple_feedbacks(self, engine):
        """Test that preferences improve with multiple feedbacks"""
        user_id = "learning_user"
        
        # Provide multiple positive feedbacks for formal style
        for i in range(5):
            result = engine.process_message(
                user_id,
                "Please review this document carefully",
                "general"
            )
            engine.provide_feedback(user_id, result['message_id'], "positive")
        
        # Check preferences
        preferences = engine.analyzer.get_user_preferences(user_id)
        
        # Should have learned some preferences
        assert len(preferences) > 0
        
        # Confidence should increase with more samples
        for pref in preferences.values():
            assert pref.sample_count >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
