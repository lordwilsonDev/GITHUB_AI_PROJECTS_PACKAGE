#!/usr/bin/env python3
"""Fix all remaining API mismatches in integration tests"""

import re

# Read the file
with open('tests/integration_tests.rs', 'r') as f:
    content = f.read()

# Fix 1: BasicHITLCollaborator::new() should use with_audit_logger()
content = re.sub(
    r'let hitl = BasicHITLCollaborator::new\(audit_logger\.clone\(\)\);',
    'let hitl = BasicHITLCollaborator::with_audit_logger(600, audit_logger.clone());',
    content
)

# Fix 2: query_history() API - it takes a Filter struct, not individual params
# The actual API is: query_history(&self, filter: &Filter)
# Tests are calling: query_history(None, None, None, None)
content = re.sub(
    r'logger\.query_history\(None, None, None, None\)',
    'logger.query_history(&audit_system::Filter { start_time: None, end_time: None, action_types: vec![], limit: None })',
    content
)

# Write back
with open('tests/integration_tests.rs', 'w') as f:
    f.write(content)

print('Fixed integration tests:')
print('- BasicHITLCollaborator::new() -> with_audit_logger()')
print('- query_history() API calls')
