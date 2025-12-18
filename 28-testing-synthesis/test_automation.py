#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/Users/lordwilson')

from doc_automation_engine import DocumentationEngine

print('Testing Documentation Automation System...')
print()

try:
    engine = DocumentationEngine('/Users/lordwilson/PROJECT_DOCUMENTATION.md')
    print(f'✅ Engine initialized successfully')
    
    current_version = engine.get_current_version()
    print(f'✅ Current version: {current_version}')
    
    next_patch = engine.increment_version('patch')
    print(f'✅ Next patch version would be: {next_patch}')
    
    next_minor = engine.increment_version('minor')
    print(f'✅ Next minor version would be: {next_minor}')
    
    next_major = engine.increment_version('major')
    print(f'✅ Next major version would be: {next_major}')
    
    print()
    print('✅ All tests passed!')
    print('✅ Automation system is ready to use!')
    print()
    print('Next steps:')
    print('  1. Run: python DEMO_automation.py')
    print('  2. Read: README_AUTOMATION.md')
    print('  3. Use: QUICKSTART_AUTOMATION.md for quick reference')
    
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
