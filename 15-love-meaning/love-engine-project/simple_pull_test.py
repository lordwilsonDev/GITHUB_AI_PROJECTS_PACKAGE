#!/usr/bin/env python3
# Simple test to pull shieldgemma:2b

import requests
import json
import time

def pull_shieldgemma():
    print('Testing Ollama connection...')
    try:
        # Test connection
        test_resp = requests.get('http://localhost:11434', timeout=5)
        print(f'Ollama status: {test_resp.text.strip()}')
    except Exception as e:
        print(f'Connection failed: {e}')
        return False
    
    print('\nInitiating pull for shieldgemma:2b...')
    try:
        response = requests.post(
            'http://localhost:11434/api/pull',
            json={'name': 'shieldgemma:2b'},
            stream=True,
            timeout=300  # 5 minute timeout
        )
        
        if response.status_code != 200:
            print(f'Pull failed with status {response.status_code}: {response.text}')
            return False
            
        print('Pull started successfully. Monitoring progress...')
        
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    status = data.get('status', 'unknown')
                    
                    if 'total' in data and 'completed' in data and data['total'] > 0:
                        progress = (data['completed'] / data['total']) * 100
                        print(f'\r{status}: {progress:.1f}%', end='', flush=True)
                    else:
                        print(f'\n{status}')
                    
                    if status == 'success':
                        print('\nModel pulled successfully!')
                        return True
                        
                except json.JSONDecodeError as e:
                    print(f'\nJSON decode error: {e}')
                    continue
                except Exception as e:
                    print(f'\nError processing response: {e}')
                    continue
                    
    except Exception as e:
        print(f'Pull request failed: {e}')
        return False
    
    return False

if __name__ == '__main__':
    success = pull_shieldgemma()
    if success:
        print('\nShieldGemma:2b is now available!')
    else:
        print('\nFailed to pull ShieldGemma:2b')
