#!/usr/bin/env python3
# Test script to verify all modules can be imported

modules = [
    "safety",
    "engine_core",
    "minimind.extract_dataset",
    "minimind.train_minimind",
    "tools.safety_stats",
]

for m in modules:
    try:
        __import__(m)
        print(f"✅ {m} import OK")
    except Exception as e:
        print(f"❌ {m} import FAILED: {e}")

# Test safety functionality specifically
try:
    import safety
    result = safety.safety_score('Hello world')
    print(f"🔒 Safety test: score={result.score}, blocked={result.blocked}")
except Exception as e:
    print(f"❌ Safety test failed: {e}")

print('\n🎯 Import test complete!')
