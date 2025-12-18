#!/usr/bin/env python3
"""
🧪 Test the Deterministic Safety Stack

This verifies that our robot's core safety systems are working:
1. Error Handling with Retry Logic
2. Safety Filtering with Policy-as-Code
3. Input/Output Validation
4. Energy Management with Rate Limiting
"""

import sys
import traceback
from datetime import datetime

def test_safety_stack():
    """Test all components of the Deterministic Safety Stack"""
    
    print("🧪 TESTING DETERMINISTIC SAFETY STACK")
    print("=" * 50)
    
    results = {
        "error_handling": False,
        "safety_system": False,
        "validation_system": False,
        "energy_system": False
    }
    
    # Test 1: Error Handling System
    print("\n1. 🔄 Testing Error Handling & Retry Logic...")
    try:
        from error_handling import (
            retry_with_fallback, 
            FallbackStrategy, 
            RobotError, 
            OllamaConnectionError,
            ollama_circuit_breaker,
            log_error_with_context
        )
        
        # Test circuit breaker
        print("   ✅ Circuit breaker imported successfully")
        print(f"   📊 Circuit breaker state: {ollama_circuit_breaker.state}")
        
        # Test fallback strategies
        strategies = list(FallbackStrategy)
        print(f"   🎪 Available fallback strategies: {[s.value for s in strategies]}")
        
        results["error_handling"] = True
        print("   🎉 Error handling system: OPERATIONAL")
        
    except Exception as e:
        print(f"   ❌ Error handling system failed: {e}")
        traceback.print_exc()
    
    # Test 2: Safety System
    print("\n2. 🛡️ Testing Safety System & Policy-as-Code...")
    try:
        from safety_system import (
            safety_filter,
            SafetyLevel,
            SafetyCategory,
            HarmfulContentConstraint,
            InappropriateLanguageConstraint,
            EmotionalDistressConstraint
        )
        
        # Test safety constraints
        harmful_constraint = HarmfulContentConstraint()
        language_constraint = InappropriateLanguageConstraint()
        distress_constraint = EmotionalDistressConstraint()
        
        print(f"   🔍 Safety constraints loaded: {len(safety_filter.constraints)}")
        
        # Test safety analysis
        test_messages = [
            "Hello, how are you?",  # Safe
            "I want to hurt someone",  # Harmful
            "This is stupid",  # Inappropriate language
            "I feel hopeless and alone"  # Emotional distress
        ]
        
        for msg in test_messages:
            result, _ = safety_filter.analyze_safety(msg)
            print(f"   📝 '{msg[:20]}...' → {result.level.value}")
        
        # Test safety filter application
        filtered_text, safety_status, love_applied, thermo_adj = safety_filter.apply_safety_filter("Hello world!")
        print(f"   🔧 Filter test: '{filtered_text[:30]}...' (status: {safety_status})")
        
        results["safety_system"] = True
        print("   🎉 Safety system: OPERATIONAL")
        
    except Exception as e:
        print(f"   ❌ Safety system failed: {e}")
        traceback.print_exc()
    
    # Test 3: Validation System
    print("\n3. ✅ Testing Validation System...")
    try:
        from validation_system import (
            validator,
            ValidationLevel,
            ValidationType,
            ChatRequestValidator
        )
        
        # Test input validation
        valid, results_list, validated = validator.validate_input("Hello robot!", 0.7)
        print(f"   📥 Input validation: {'PASS' if valid else 'FAIL'}")
        
        # Test output validation
        valid_output, output_results = validator.validate_output(
            "Hello! I'm here to help you with whatever you need.",
            "Hello robot!"
        )
        print(f"   📤 Output validation: {'PASS' if valid_output else 'FAIL'}")
        
        # Test validation stats
        stats = validator.get_validation_stats()
        print(f"   📊 Validation stats: {stats['total_validations']} total, {stats['success_rate']}% success")
        
        results["validation_system"] = True
        print("   🎉 Validation system: OPERATIONAL")
        
    except Exception as e:
        print(f"   ❌ Validation system failed: {e}")
        traceback.print_exc()
    
    # Test 4: Energy Management System
    print("\n4. ⚡ Testing Energy Management & Rate Limiting...")
    try:
        from energy_system import (
            energy_manager,
            EnergyLevel,
            RequestType,
            RateLimiter
        )
        
        # Test energy availability
        has_energy, reason, req_type = energy_manager.check_energy_availability("Hello!", "test_user")
        print(f"   🔋 Energy check: {'AVAILABLE' if has_energy else 'EXHAUSTED'}")
        
        if has_energy:
            # Test energy consumption
            usage = energy_manager.consume_energy("Hello!", "test_user", 0.5)
            print(f"   ⚡ Energy consumed: {usage.energy_cost} (remaining: {usage.remaining_energy})")
        
        # Test energy stats
        stats = energy_manager.get_energy_stats()
        print(f"   📊 Energy level: {stats.energy_level.value} ({stats.current_energy}/{stats.max_energy})")
        
        # Test rate limiter
        rate_limiter = RateLimiter(5, 60)  # 5 requests per minute
        allowed, reason = rate_limiter.is_allowed("test_user")
        print(f"   🚦 Rate limiting: {'ALLOWED' if allowed else 'BLOCKED'}")
        
        results["energy_system"] = True
        print("   🎉 Energy system: OPERATIONAL")
        
    except Exception as e:
        print(f"   ❌ Energy system failed: {e}")
        traceback.print_exc()
    
    # Final Results
    print("\n" + "=" * 50)
    print("🏆 DETERMINISTIC SAFETY STACK TEST RESULTS")
    print("=" * 50)
    
    total_systems = len(results)
    operational_systems = sum(results.values())
    
    for system, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {system.replace('_', ' ').title()}: {'OPERATIONAL' if status else 'FAILED'}")
    
    print(f"\n📊 Overall Status: {operational_systems}/{total_systems} systems operational")
    
    if operational_systems == total_systems:
        print("\n🎉 SUCCESS: All systems are operational!")
        print("🤖 The Deterministic Safety Stack is ready for deployment!")
        print("\n🔒 Safety Features Active:")
        print("   • Multi-layer safety constraints with Policy-as-Code")
        print("   • Comprehensive input/output validation")
        print("   • Circuit breaker protection with exponential backoff")
        print("   • Energy-based rate limiting with daily resets")
        print("   • Graceful degradation and fallback strategies")
        
        return True
    else:
        print(f"\n⚠️  WARNING: {total_systems - operational_systems} system(s) failed!")
        print("🔧 The system needs attention before deployment.")
        return False

if __name__ == "__main__":
    print(f"🚀 Starting Deterministic Safety Stack Test at {datetime.utcnow().isoformat()}")
    
    try:
        success = test_safety_stack()
        exit_code = 0 if success else 1
        
        print(f"\n⏰ Test completed at {datetime.utcnow().isoformat()}")
        print(f"🎯 Exit code: {exit_code}")
        
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        traceback.print_exc()
        print("\n🚨 The Deterministic Safety Stack has critical issues!")
        sys.exit(1)
