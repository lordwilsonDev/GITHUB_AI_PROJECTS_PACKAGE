#!/usr/bin/env python3
from vy_doc_integration import VyDocumentationHelper
import time

def demo_automation():
    print('=' * 60)
    print('  DOCUMENTATION AUTOMATION SYSTEM - LIVE DEMO')
    print('=' * 60)
    vy_doc = VyDocumentationHelper()
    print(f'Current Documentation Version: {vy_doc.interface.get_version()}')
    print('-' * 60)
    print('DEMO 1: Auto-Documenting Troubleshooting Solution')
    vy_doc.auto_document_error(
        'Database Connection Pool Exhausted',
        'Increase pool size in database.yml: pool: 20 (default was 5)'
    )
    print('Troubleshooting section updated!')
    vy_doc.log_task_completion('Database Fix', 'success', 'Resolved pool exhaustion')
    time.sleep(1)
    print('-' * 60)
    print('DEMO 2: Auto-Documenting Configuration Change')
    vy_doc.auto_document_config(
        'DATABASE_POOL_SIZE', '20',
        'Maximum number of concurrent database connections'
    )
    print('Configuration section updated!')
    vy_doc.log_task_completion('Config Update', 'success', 'Updated pool config')
    time.sleep(1)
    print('-' * 60)
    print('DEMO 3: Auto-Documenting New Feature')
    vy_doc.auto_document_feature(
        'Automatic Database Connection Retry with exponential backoff'
    )
    print('Advanced Features section updated!')
    vy_doc.log_task_completion('Feature', 'success', 'Added retry logic')
    time.sleep(1)
    print('-' * 60)
    print('DEMO 4: Creating Release from Session Activity')
    new_version = vy_doc.create_release_from_session('minor')
    print(f'Release created: v{new_version}')
    vy_doc.save_session_log('demo_session_log.json')
    print('Session log saved!')
    print('=' * 60)
    print('DEMO COMPLETE - Documentation is now self-updating!')
    print('=' * 60)

if __name__ == '__main__':
    demo_automation()
