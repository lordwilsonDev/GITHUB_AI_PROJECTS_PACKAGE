#!/usr/bin/env python3
# Test Ollama API endpoints

import requests
import json
import time

def test_basic_connection():
    """Test basic Ollama connection"""
    try:
        response = requests.get('http://localhost:11434', timeout=5)
        print(f'✓ Basic connection: {response.text.strip()}')
        return True
    except Exception as e:
        print(f'✗ Basic connection failed: {e}')
        return False

def test_models_endpoint():
    """Test OpenAI-compatible models endpoint"""
    try:
        response = requests.get('http://localhost:11434/v1/models', timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model['id'] for model in data['data']]
            print(f'✓ Models endpoint working. Available models: {models}')
            return models
        else:
            print(f'✗ Models endpoint failed: {response.status_code}')
            return []
    except Exception as e:
        print(f'✗ Models endpoint error: {e}')
        return []

def test_chat_completion(model_name):
    """Test chat completions endpoint"""
    try:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": "Say hello in exactly 3 words"}
            ],
            "stream": False,
            "max_tokens": 50
        }
        
        response = requests.post(
            'http://localhost:11434/v1/chat/completions',
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print(f'✓ Chat completion with {model_name}: "{content.strip()}"')
            return True
        else:
            print(f'✗ Chat completion failed for {model_name}: {response.status_code}')
            print(f'  Response: {response.text}')
            return False
    except Exception as e:
        print(f'✗ Chat completion error for {model_name}: {e}')
        return False

def test_native_api():
    """Test native Ollama API"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model['name'] for model in data['models']]
            print(f'✓ Native API working. Models: {models}')
            return models
        else:
            print(f'✗ Native API failed: {response.status_code}')
            return []
    except Exception as e:
        print(f'✗ Native API error: {e}')
        return []

def main():
    print('=== Ollama API Endpoint Tests ===\n')
    
    # Test 1: Basic connection
    if not test_basic_connection():
        print('Cannot proceed - Ollama not accessible')
        return
    
    # Test 2: Native API
    native_models = test_native_api()
    
    # Test 3: OpenAI-compatible API
    openai_models = test_models_endpoint()
    
    # Test 4: Chat completions
    if openai_models:
        print('\nTesting chat completions...')
        for model in openai_models:
            test_chat_completion(model)
    
    # Summary
    print('\n=== Test Summary ===')
    print(f'Native API models: {len(native_models)}')
    print(f'OpenAI API models: {len(openai_models)}')
    
    if len(openai_models) > 0:
        print('✓ Ollama API is ready for Love Engine integration')
    else:
        print('✗ No models available for testing')
        
    # Check for required models
    required_models = ['gemma2:9b', 'shieldgemma:2b']
    missing_models = []
    
    for model in required_models:
        if model not in native_models and model not in openai_models:
            missing_models.append(model)
    
    if missing_models:
        print(f'⚠️  Missing required models: {missing_models}')
        print('   Run model pull commands to download them')
    else:
        print('✓ All required models are available')

if __name__ == '__main__':
    main()
