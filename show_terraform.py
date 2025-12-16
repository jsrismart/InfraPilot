import requests

prompt = 'Create a azure vm in A series size at South india location'
response = requests.post(
    'http://127.0.0.1:8001/api/v1/infra/generate-iac',
    json={'prompt': prompt},
    timeout=15
)

if response.status_code == 200:
    data = response.json()
    main_tf = data['iac']['main.tf']
    
    print('✓ Generated Terraform for:', prompt)
    print('\nKey Values:')
    for line in main_tf.split('\n'):
        if 'vm_size' in line or ('location' in line and '=' in line and 'resource' not in line.lower()):
            print(f'  {line.strip()}')
    
    print('\nFull main.tf:')
    print(main_tf[:800])
