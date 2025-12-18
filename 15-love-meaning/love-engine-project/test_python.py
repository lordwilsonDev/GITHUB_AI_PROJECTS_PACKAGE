import sys
print(f'Python version: {sys.version}')

try:
    import requests
    print('requests: available')
except ImportError:
    print('requests: NOT AVAILABLE - need to install')

try:
    import fastapi
    print('fastapi: available')
except ImportError:
    print('fastapi: NOT AVAILABLE - need to install')

try:
    import uvicorn
    print('uvicorn: available')
except ImportError:
    print('uvicorn: NOT AVAILABLE - need to install')
