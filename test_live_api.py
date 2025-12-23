import requests
import json

prompt = 'Create a azure vm with B series at South India region'
print(f'Testing: {prompt}\n')

response = requests.post(
    'http://127.0.0.1:8000/api/v1/infra/generate-iac',
    json={'prompt': prompt},
    timeout=60
)

if response.status_code == 200:
    data = response.json()
    
    # Extract Terraform code
    if 'terraform' in data and 'main_tf' in data['terraform']:
        main_tf = data['terraform']['main_tf']
        
        print('Generated Terraform (main.tf):')
        print('-' * 60)
        print(main_tf[:800])
        print('...')
        
        # Highlight key values
        print('\nKey Values Detected:')
        for line in main_tf.split('\n'):
            if 'vm_size' in line:
                print(f'  ✓ VM Size: {line.strip()}')
            if 'location =' in line and '"' in line:
                print(f'  ✓ Region: {line.strip()}')
    else:
        print(json.dumps(data, indent=2)[:500])
else:
    print(f'Error: {response.status_code}')
    print(response.text[:500])
