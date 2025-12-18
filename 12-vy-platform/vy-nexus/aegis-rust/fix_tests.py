#!/usr/bin/env python3
"""
Automated test fixer for aegis-rust integration tests.
Fixes common patterns:
1. Missing AuditSystem import
2. Wrong log_experience signature
3. Wrong learn_from_* signatures  
4. get_capability_metrics() is not async
"""

import re

# Read the test file
with open('/Users/lordwilson/vy-nexus/aegis-rust/tests/integration_tests.rs', 'r') as f:
    content = f.read()

# Fix 1: Add AuditSystem import if missing
if 'use audit_system::AuditSystem;' not in content:
    # Find the imports section and add it
    content = content.replace(
        'use audit_system::{BasicAuditLogger, AuditEntry};',
        'use audit_system::{BasicAuditLogger, AuditEntry, AuditSystem};'
    )

# Fix 2: Fix log_experience calls
# Pattern: log_experience(id, action_type, params, success)
# Should be: log_experience(action_type, params, Outcome{success, ...}, eth_score, safety_score)

# First, let's find all log_experience patterns and fix them
# This is complex, so we'll use a more sophisticated approach

lines = content.split('\n')
output_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # Check if this line starts a log_experience call
    if 'evolution.log_experience(' in line or '.log_experience(' in line:
        # Collect the full multi-line call
        call_lines = [line]
        paren_count = line.count('(') - line.count(')')
        j = i + 1
        while paren_count > 0 and j < len(lines):
            call_lines.append(lines[j])
            paren_count += lines[j].count('(') - lines[j].count(')')
            j += 1
        
        full_call = '\n'.join(call_lines)
        
        # Parse the arguments - this is a simple heuristic
        # If it has 4 args, it's the old format (id, action_type, params, success)
        # Count commas outside of parentheses/braces
        depth = 0
        arg_count = 1  # Start with 1 since there's at least one arg
        for c in full_call:
            if c in '({[':
                depth += 1
            elif c in ')}]':
                depth -= 1
            elif c == ',' and depth == 1:  # Only count commas at the argument level
                arg_count += 1
        
        # If it looks like the old 4-arg format, skip it and mark for manual fix
        # For now, let's just output as-is
        output_lines.extend(call_lines)
        i = j
        continue
    
    # Fix 3: Remove .await from get_capability_metrics()
    if '.get_capability_metrics().await' in line:
        line = line.replace('.get_capability_metrics().await', '.get_capability_metrics()')
    
    # Fix 4: Fix learn_from_safety/ethics - action_type should be &str not String
    # Change format!("...", x) to &format!("...", x) or just use a string literal
    if '.learn_from_safety(' in line or '.learn_from_ethics(' in line:
        # If next line has format!(), we need to look at the full call
        pass  # This is too complex for simple regex
    
    output_lines.append(line)
    i += 1

# Write back
with open('/Users/lordwilson/vy-nexus/aegis-rust/tests/integration_tests.rs', 'w') as f:
    f.write('\n'.join(output_lines))

print("Fixed basic patterns. Complex fixes require manual intervention.")
print("Fixed:")
print("✓ Added AuditSystem import")
print("✓ Removed .await from get_capability_metrics()")
print("✗ log_experience calls need manual fix (complex multi-line)")
print("✗ learn_from_* calls need manual fix (complex multi-line)")
