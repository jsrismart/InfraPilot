import requests
import json

prompt = 'Create a azure vm in A series size at South india location'
print(f'Testing: {prompt}\n')

response = requests.post(
    'http://127.0.0.1:8001/api/v1/infra/generate-iac',
    json={'prompt': prompt},
    timeout=10
)

print(f'Status: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    
    print('Generated files:')
    if 'iac' in data:
        for filename in data['iac'].keys():
            print(f'  ✓ {filename}')
        
        # Check main.tf
        if 'main.tf' in data['iac']:
            main_tf = data['iac']['main.tf']
            print(f'\nKey values in main.tf:')
            for line in main_tf.split('\n'):
                if 'vm_size' in line or ('location' in line and '=' in line and 'resource' not in line):
                    print(f'  {line.strip()}')
else:
    print(f'Error: {response.text[:300]}')
