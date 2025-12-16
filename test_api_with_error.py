import requests
import json
import traceback

try:
    prompt = 'Create a azure vm in A series size at South india location'
    print(f'Sending request: {prompt}')
    
    response = requests.post(
        'http://127.0.0.1:8001/api/v1/infra/generate-iac',
        json={'prompt': prompt},
        timeout=10
    )
    
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text[:500]}')
    
    if response.status_code == 200:
        data = response.json()
        print('SUCCESS!')
        print('Files:', list(data.get('iac', {}).keys()))
    
except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()
