#!/usr/bin/env python3
from pathlib import Path

p = Path("tests/test_micro_automation.py")
s = p.read_text()

# Replace all references to the old function names
replacements = [
    ("execute_func=test_success_func", "execute_func=success_func"),
    ("execute_func=test_failure_func", "execute_func=failure_func"),
    ("execute_func=test_retry_func", "execute_func=retry_func"),
    ("validation_func=test_validation_func", "validation_func=validation_func"),
    ("rollback_func=test_rollback_func", "rollback_func=rollback_func"),
    ("hasattr(test_retry_func", "hasattr(retry_func"),
    ("test_retry_func.call_count", "retry_func.call_count"),
    ("hasattr(test_rollback_func", "hasattr(rollback_func"),
    ("test_rollback_func.called", "rollback_func.called"),
]

for old, new in replacements:
    s = s.replace(old, new)

p.write_text(s)
print(f"✅ Fixed all references in {p}")
print(f"Total replacements made: {len(replacements)}")
