#!/usr/bin/env python3
import requests
import json
import time

def pull_model(model_name):
    print(f'Pulling {model_name}...')
    response = requests.post('http://localhost:11434/api/pull', 
                           json={'name': model_name},
                           stream=True)
    
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    if 'status' in data:
                        print(f'  {data["status"]}')
                    if data.get('status') == 'success':
                        print(f'Successfully pulled {model_name}')
                        return True
                except json.JSONDecodeError:
                    continue
    else:
        print(f'Error pulling {model_name}: {response.status_code}')
        return False

if __name__ == '__main__':
    models = ['gemma2:9b', 'shieldgemma:2b']
    
    for model in models:
        success = pull_model(model)
        if not success:
            print(f'Failed to pull {model}')
            break
        time.sleep(2)  # Brief pause between pulls
    
    print('Model pulling complete!')
