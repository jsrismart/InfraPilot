import requests
import json

try:
    prompt = 'Create a azure vm in A series size at South india location'
    print(f'Testing: {prompt}\n')
    
    response = requests.post(
        'http://127.0.0.1:8001/api/v1/infra/generate-iac',
        json={'prompt': prompt},
        timeout=15
    )
    
    print(f'Status Code: {response.status_code}')
    print(f'Response Length: {len(response.text)}')
    
    if response.status_code == 200:
        data = response.json()
        print('✓ SUCCESS!')
        print('Files generated:')
        for filename in data.get('iac', {}).keys():
            print(f'  - {filename}')
    else:
        print(f'Error Response:')
        print(response.text[:1000])
        
except Exception as e:
    print(f'Exception: {e}')
    import traceback
    traceback.print_exc()
