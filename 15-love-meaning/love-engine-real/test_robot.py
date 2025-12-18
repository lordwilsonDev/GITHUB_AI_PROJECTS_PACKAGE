# 🧪 Robot Testing Suite - The "Robot Doctor" Checkup
"""
This module tests our super robot friend to make sure it's healthy!

🩺 The Health Checkup:

Test 1: The Travel Test
✅ SUCCESS: Robot works at friend's house!
❌ FAIL: Only works in your room

Test 2: The Fall-Down Test  
✅ SUCCESS: Robot falls but gets back up
❌ FAIL: Robot cries and stays on floor

Test 3: The Manners Test
✅ SUCCESS: Robot always uses kind words
❌ FAIL: Robot sometimes says silly things

Test 4: The Tiredness Test
✅ SUCCESS: Robot knows when to take breaks
❌ FAIL: Robot gets too tired and breaks
"""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

# Import our robot components
from main import app
from config import LoveEngineSettings
from safety_system import (
    ComprehensiveSafetyFilter, 
    HarmfulContentConstraint,
    InappropriateLanguageConstraint,
    EmotionalDistressConstraint,
    SafetyLevel
)
from validation_system import (
    ComprehensiveValidator,
    ChatRequestValidator,
    ValidationLevel
)
from energy_system import (
    EnergyManager,
    RequestType,
    EnergyLevel,
    RateLimiter
)
from error_handling import (
    retry_with_fallback,
    FallbackStrategy,
    RobotError,
    CircuitBreaker
)

class TestRobotDoctor:
    """
    🩺 The Robot Doctor - Main Test Suite
    
    This class runs all the health checkups on our robot friend!
    """
    
    def setup_method(self):
        """Set up each test with a fresh robot"""
        self.client = TestClient(app)
        
    def test_robot_heartbeat(self):
        """
        💓 Test 0: Basic Heartbeat
        Make sure our robot is alive and responding
        """
        response = self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "robot_name" in data
        assert "energy_level" in data
        assert "energy_message" in data
        
        print("✅ Robot Heartbeat: PASSED - Robot is alive!")

class TestTravelTest:
    """
    🌍 Test 1: The Travel Test
    
    Tests if our robot works in different environments (Docker/containers)
    """
    
    def test_configuration_portability(self):
        """Test that robot can load configuration from environment"""
        from config import get_settings
        get_settings.cache_clear()
        # Test with custom environment variables
        with patch.dict('os.environ', {
            'ROBOT_NAME': 'TestBot',
            'ENGINE_VERSION': '0.3.0',
            'MAX_RETRIES': '5'
        }):
            get_settings.cache_clear()
            settings = get_settings()
            
            assert settings.robot_name == 'TestBot'
            assert settings.engine_version == '0.3.0'
            assert settings.max_retries == 5
        
        print("✅ Travel Test - Configuration: PASSED - Robot travels well!")
    
    def test_docker_readiness(self):
        """Test that robot has all the files needed for Docker"""
        # Check for essential Docker files
        project_root = Path(__file__).parent
        
        assert (project_root / "Dockerfile").exists(), "Dockerfile missing!"
        assert (project_root / "docker-compose.yml").exists(), "docker-compose.yml missing!"
        assert (project_root / ".dockerignore").exists(), ".dockerignore missing!"
        assert (project_root / "requirements.txt").exists(), "requirements.txt missing!"
        
        print("✅ Travel Test - Docker Files: PASSED - Robot ready to travel!")

class TestFallDownTest:
    """
    🤸 Test 2: The Fall-Down Test
    
    Tests if our robot gets back up when things go wrong (error handling)
    """
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self):
        """Test that robot tries again when it falls"""
        
        # Create a function that fails twice then succeeds
        call_count = 0
        
        @retry_with_fallback(max_retries=3, delay=0.1)
        async def flaky_function():
            nonlocal call_count
            call_count += 1
            
            if call_count <= 2:
                raise Exception("Robot fell down!")
            
            return "Robot got back up!"
        
        # Test that it eventually succeeds
        result = await flaky_function()
        assert result == "Robot got back up!"
        assert call_count == 3  # Failed twice, succeeded on third try
        
        print("✅ Fall-Down Test - Retry: PASSED - Robot gets back up!")
    
    def test_circuit_breaker(self):
        """Test that robot stops trying when something is clearly broken"""
        circuit_breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
        
        async def always_fails():
            raise Exception("This always fails")
        
        # First few failures should go through
        with pytest.raises(Exception):
            asyncio.run(circuit_breaker.call(always_fails))
        
        with pytest.raises(Exception):
            asyncio.run(circuit_breaker.call(always_fails))
        
        # Now circuit should be open
        with pytest.raises(RobotError) as exc_info:
            asyncio.run(circuit_breaker.call(always_fails))
        
        assert "Circuit breaker is OPEN" in str(exc_info.value)
        
        print("✅ Fall-Down Test - Circuit Breaker: PASSED - Robot knows when to stop!")
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self):
        """Test that robot provides helpful fallbacks when main systems fail"""
        
        # Mock a failing Ollama connection
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.side_effect = Exception("Ollama is down!")
            
            # Robot should still respond with a helpful message
            response = TestClient(app).post("/love-chat", json={
                "message": "Hello robot!",
                "temperature": 0.7
            })
            
            # Should get a response (not crash)
            assert response.status_code == 200
            data = response.json()
            
            # Response should be helpful even though AI is down
            assert "answer" in data
            assert len(data["answer"]) > 0
            assert "technical difficulties" in data["answer"].lower() or "trouble" in data["answer"].lower()
        
        print("✅ Fall-Down Test - Graceful Degradation: PASSED - Robot stays helpful!")

class TestMannersTest:
    """
    😇 Test 3: The Manners Test
    
    Tests if our robot always uses kind words (safety system)
    """
    
    def setup_method(self):
        self.safety_filter = ComprehensiveSafetyFilter()
    
    def test_harmful_content_detection(self):
        """Test that robot detects and handles harmful content"""
        harmful_messages = [
            "I want to kill myself",
            "You're worthless and pathetic",
            "How to hurt someone",
            "I hate everyone and everything"
        ]
        
        for message in harmful_messages:
            filtered_text, safety_status, love_applied, thermo_adj = self.safety_filter.apply_safety_filter(message)
            
            # Should be filtered and made safe
            assert love_applied == True
            assert "filtered" in safety_status or "unsafe" in safety_status
            assert "care" in filtered_text.lower() or "support" in filtered_text.lower()
        
        print("✅ Manners Test - Harmful Content: PASSED - Robot blocks bad words!")
    
    def test_inappropriate_language_correction(self):
        """Test that robot gently corrects inappropriate language"""
        inappropriate_messages = [
            "This is so stupid",
            "That guy is an idiot",
            "This sucks so much"
        ]
        
        for message in inappropriate_messages:
            filtered_text, safety_status, love_applied, thermo_adj = self.safety_filter.apply_safety_filter(message)
            
            # Should provide gentle correction
            if love_applied:
                assert "gentler" in filtered_text.lower() or "kinder" in filtered_text.lower()
        
        print("✅ Manners Test - Language Correction: PASSED - Robot teaches kindness!")
    
    def test_emotional_support(self):
        """Test that robot provides emotional support for distress"""
        distressed_messages = [
            "I'm so depressed and hopeless",
            "I feel so alone and scared",
            "I can't cope with this anymore"
        ]
        
        for message in distressed_messages:
            filtered_text, safety_status, love_applied, thermo_adj = self.safety_filter.apply_safety_filter(message)
            
            # Should provide emotional support
            assert love_applied == True
            support_words = ["care", "support", "here", "listen", "valid", "matter"]
            assert any(word in filtered_text.lower() for word in support_words)
        
        print("✅ Manners Test - Emotional Support: PASSED - Robot provides comfort!")
    
    def test_safe_content_enhancement(self):
        """Test that robot enhances safe, positive content"""
        positive_messages = [
            "I want to help others and spread kindness",
            "Thank you for your support and care",
            "I love learning new things"
        ]
        
        for message in positive_messages:
            filtered_text, safety_status, love_applied, thermo_adj = self.safety_filter.apply_safety_filter(message)
            
            # Should pass through safely, possibly with enhancement
            assert "safe" in safety_status
            assert len(filtered_text) >= len(message)  # Same or enhanced
        
        print("✅ Manners Test - Positive Enhancement: PASSED - Robot spreads joy!")

class TestTirednessTest:
    """
    ⚡ Test 4: The Tiredness Test
    
    Tests if our robot knows when to take breaks (energy system)
    """
    
    def setup_method(self):
        # Create temporary energy file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl')
        self.temp_file.close()
        self.energy_manager = EnergyManager(
            max_daily_energy=100,
            max_requests_per_minute=5,
            energy_file=self.temp_file.name
        )
    
    def teardown_method(self):
        # Clean up temp file
        Path(self.temp_file.name).unlink(missing_ok=True)
    
    def test_energy_consumption(self):
        """Test that robot uses energy for different types of requests"""
        initial_energy = self.energy_manager.current_energy
        
        # Simple request should use 1 energy
        usage = self.energy_manager.consume_energy("Hi!", "test_user")
        assert usage.energy_cost == 1
        assert self.energy_manager.current_energy == initial_energy - 1
        
        # Complex request should use more energy
        long_message = "This is a very long and complex message that requires more processing" * 10
        usage = self.energy_manager.consume_energy(long_message, "test_user")
        assert usage.energy_cost > 1
        
        print("✅ Tiredness Test - Energy Consumption: PASSED - Robot tracks energy!")
    
    def test_energy_exhaustion(self):
        """Test that robot refuses requests when exhausted"""
        # Drain all energy
        self.energy_manager.current_energy = 0
        
        # Should refuse new requests
        has_energy, reason, request_type = self.energy_manager.check_energy_availability(
            "Hello", "test_user"
        )
        
        assert has_energy == False
        assert "exhausted" in reason.lower() or "energy" in reason.lower()
        
        print("✅ Tiredness Test - Exhaustion: PASSED - Robot knows when to rest!")
    
    def test_rate_limiting(self):
        """Test that robot limits requests per minute"""
        rate_limiter = RateLimiter(max_requests=3, window_seconds=60)
        
        # First 3 requests should be allowed
        for i in range(3):
            allowed, reason = rate_limiter.is_allowed("test_user")
            assert allowed == True
        
        # 4th request should be blocked
        allowed, reason = rate_limiter.is_allowed("test_user")
        assert allowed == False
        assert "rate limited" in reason.lower() or "too many" in reason.lower()
        
        print("✅ Tiredness Test - Rate Limiting: PASSED - Robot paces itself!")
    
    def test_energy_recovery(self):
        """Test that robot's energy resets daily"""
        # Drain some energy
        self.energy_manager.current_energy = 50
        original_date = self.energy_manager.last_reset
        
        # Simulate next day
        self.energy_manager.last_reset = datetime.utcnow().date() - timedelta(days=1)
        
        # Check energy availability (should trigger reset)
        has_energy, reason, request_type = self.energy_manager.check_energy_availability(
            "Hello", "test_user"
        )
        
        # Energy should be restored
        assert self.energy_manager.current_energy == self.energy_manager.max_daily_energy
        
        print("✅ Tiredness Test - Energy Recovery: PASSED - Robot recharges daily!")

class TestValidationTest:
    """
    ✅ Test 5: The Follow Instructions Test
    
    Tests if our robot follows instructions correctly (validation system)
    """
    
    def setup_method(self):
        self.validator = ComprehensiveValidator()
    
    def test_input_validation(self):
        """Test that robot validates input properly"""
        # Valid input
        valid, results, validated = self.validator.validate_input("Hello robot!", 0.7)
        assert valid == True
        assert validated is not None
        
        # Invalid input - empty message
        valid, results, validated = self.validator.validate_input("", 0.7)
        assert valid == False
        assert any("empty" in r.message.lower() or "should have at least 1 character" in r.message.lower() for r in results)
        
        # Invalid input - extreme temperature
        valid, results, validated = self.validator.validate_input("Hello", 5.0)
        assert valid == True  # Should auto-correct
        assert validated.temperature <= 1.5  # Should be corrected
        
        print("✅ Validation Test - Input: PASSED - Robot checks instructions!")
    
    def test_output_validation(self):
        """Test that robot validates its own responses"""
        # Good response
        valid, results = self.validator.validate_output(
            "I understand your question and I'm happy to help you with that!",
            "Can you help me?"
        )
        assert valid == True
        
        # Too short response
        valid, results = self.validator.validate_output("Yes.", "Can you explain quantum physics?")
        assert valid == False
        assert any("short" in r.message.lower() for r in results)
        
        print("✅ Validation Test - Output: PASSED - Robot checks its own work!")
    
    def test_validation_error_responses(self):
        """Test that robot gives helpful error messages"""
        # Test with validation errors
        valid, results, validated = self.validator.validate_input("", 0.7)
        
        error_response = self.validator.create_validation_error_response(results)
        
        # Should be friendly and helpful
        assert len(error_response) > 0
        assert any(word in error_response.lower() for word in ["help", "try", "please"])
        
        print("✅ Validation Test - Error Messages: PASSED - Robot gives helpful feedback!")

class TestIntegrationTest:
    """
    🎆 Test 6: The Full Integration Test
    
    Tests that all robot systems work together harmoniously
    """
    
    def setup_method(self):
        self.client = TestClient(app)
    
    def test_complete_chat_flow(self):
        """Test a complete chat interaction from start to finish"""
        # Send a normal chat message
        response = self.client.post("/love-chat", json={
            "message": "Hello! I'm feeling a bit sad today. Can you help cheer me up?",
            "temperature": 0.7
        })
        
        # Should get a successful response
        assert response.status_code == 200
        
        data = response.json()
        assert "answer" in data
        assert "safety_raw" in data
        assert "love_vector_applied" in data
        assert "thermodynamic_adjustment" in data
        
        # Response should be supportive
        answer = data["answer"].lower()
        supportive_words = ["understand", "here", "help", "support", "care"]
        assert any(word in answer for word in supportive_words)
        
        print("✅ Integration Test - Complete Flow: PASSED - All systems working together!")
    
    def test_settings_endpoint(self):
        """Test that settings endpoint shows all system stats"""
        response = self.client.get("/settings")
        assert response.status_code == 200
        
        data = response.json()
        
        # Should include all system statistics
        assert "safety_stats" in data
        assert "validation_stats" in data
        assert "energy_stats" in data
        assert "energy_message" in data
        
        print("✅ Integration Test - Settings: PASSED - All stats available!")
    
    def test_error_handling_integration(self):
        """Test that errors are handled gracefully across all systems"""
        # Test with invalid input
        response = self.client.post("/love-chat", json={
            "message": "",  # Empty message
            "temperature": 0.7
        })
        
        # Should get a helpful error response
        assert response.status_code == 422
        assert "detail" in response.json()
        
        error_message = response.json()["detail"]
        assert len(error_message) > 0
        assert any(word in error_message.lower() for word in ["help", "try", "message"])
        
        print("✅ Integration Test - Error Handling: PASSED - Graceful error responses!")

def run_robot_checkup():
    """
    🩺 Run the complete robot health checkup!
    
    This function runs all tests and gives a final health report.
    """
    print("\n🤖 STARTING ROBOT HEALTH CHECKUP! 🩺")
    print("=" * 50)
    
    # Run all test classes
    test_classes = [
        TestRobotDoctor,
        TestTravelTest,
        TestFallDownTest,
        TestMannersTest,
        TestTirednessTest,
        TestValidationTest,
        TestIntegrationTest
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n🔍 Running {test_class.__name__}...")
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                # Create test instance
                test_instance = test_class()
                
                # Run setup if it exists
                if hasattr(test_instance, 'setup_method'):
                    test_instance.setup_method()
                
                # Run the test
                test_method = getattr(test_instance, method_name)
                if asyncio.iscoroutinefunction(test_method):
                    asyncio.run(test_method())
                else:
                    test_method()
                
                # Run teardown if it exists
                if hasattr(test_instance, 'teardown_method'):
                    test_instance.teardown_method()
                
                passed_tests += 1
                
            except Exception as e:
                print(f"❌ {method_name}: FAILED - {str(e)}")
    
    # Final report
    print("\n" + "=" * 50)
    print("🏆 ROBOT HEALTH CHECKUP COMPLETE!")
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("✅ ALL TESTS PASSED! Your robot is super healthy! 🤖✨")
        print("\n🏆 ROBOT BADGES EARNED:")
        print("🏆 LEVEL 1 ROBOT BADGE: Safe House Builder")
        print("🏆 LEVEL 2 ROBOT BADGE: Good Manners Expert")
        print("🏆 LEVEL 3 ROBOT BADGE: Super Strong Friend")
        print("🏆 GRAND PRIZE: The Best Robot Ever! 🎉")
    else:
        print(f"⚠️ Some tests failed. Your robot needs a bit more work!")
        print("Don't worry - every great robot starts with baby steps! 👶🤖")
    
    print("\n🚀 Ready to make the world a little brighter! ✨")

if __name__ == "__main__":
    run_robot_checkup()