import requests
import json
import sys

def test_ollama_connection():
    try:
        response = requests.get('http://localhost:11434')
        print(f'Ollama connection: {response.text.strip()}')
        return True
    except Exception as e:
        print(f'Cannot connect to Ollama: {e}')
        return False

def pull_model(model_name):
    print(f'Pulling {model_name}...')
    try:
        response = requests.post('http://localhost:11434/api/pull', 
                               json={'name': model_name})
        
        if response.status_code == 200:
            print(f'Pull initiated for {model_name}')
            # Process streaming response
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if 'status' in data:
                            status = data['status']
                            if 'total' in data and 'completed' in data:
                                progress = (data['completed'] / data['total']) * 100
                                print(f'  {status}: {progress:.1f}%')
                            else:
                                print(f'  {status}')
                            
                            if status == 'success':
                                print(f'Successfully pulled {model_name}!')
                                return True
                    except json.JSONDecodeError:
                        continue
        else:
            print(f'Error: {response.status_code} - {response.text}')
            return False
    except Exception as e:
        print(f'Error pulling {model_name}: {e}')
        return False

if __name__ == '__main__':
    if test_ollama_connection():
        success = pull_model('shieldgemma:2b')
        if success:
            print('Model pull completed successfully!')
        else:
            print('Model pull failed!')
    else:
        print('Cannot proceed - Ollama not accessible')
