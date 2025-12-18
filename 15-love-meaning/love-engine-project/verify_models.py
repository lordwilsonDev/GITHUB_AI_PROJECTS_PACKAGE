#!/usr/bin/env python3
# Verify model availability and functionality

import requests
import json

def get_available_models():
    """Get list of available models"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model['name'] for model in data['models']]
        return []
    except Exception as e:
        print(f'Error getting models: {e}')
        return []

def test_model_chat(model_name, test_prompt="Hello"):
    """Test if a model can respond to chat"""
    try:
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": test_prompt}],
            "stream": False
        }
        
        response = requests.post(
            'http://localhost:11434/v1/chat/completions',
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            return True, content.strip()
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def main():
    print('=== Model Verification ===\n')
    
    # Get available models
    available_models = get_available_models()
    print(f'Available models: {available_models}')
    
    # Required models for Love Engine
    required_models = ['gemma2:9b', 'shieldgemma:2b']
    
    # Check each required model
    missing_models = []
    working_models = []
    
    for model in required_models:
        if model in available_models:
            print(f'\nTesting {model}...')
            success, result = test_model_chat(model, "Say hi")
            if success:
                print(f'  ✓ {model} is working: "{result}"')
                working_models.append(model)
            else:
                print(f'  ✗ {model} failed: {result}')
        else:
            print(f'\n✗ {model} is not installed')
            missing_models.append(model)
    
    # Test available models
    print('\nTesting available models...')
    for model in available_models:
        if model not in required_models:
            success, result = test_model_chat(model, "Hello")
            if success:
                print(f'  ✓ {model}: "{result}"')
            else:
                print(f'  ✗ {model} failed: {result}')
    
    # Summary
    print('\n=== Verification Summary ===')
    print(f'Required models working: {len(working_models)}/{len(required_models)}')
    print(f'Missing models: {missing_models}')
    
    if len(working_models) == len(required_models):
        print('✓ All required models are available and working!')
        print('  Ready to proceed with Love Engine testing')
    else:
        print('⚠️  Some required models are missing or not working')
        print('  Need to pull missing models before Love Engine will work')
        
        if missing_models:
            print('\nTo pull missing models, run:')
            for model in missing_models:
                print(f'  ollama pull {model}')

if __name__ == '__main__':
    main()
