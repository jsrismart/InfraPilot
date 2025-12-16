#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend')

from app.agents.designer_agent import DesignerAgent

# Test the exact prompt from the user's screenshot
prompt = "Create a azure vm with E series size at west asia region"
print(f"Testing prompt: {prompt}")
print()

agent = DesignerAgent()
result = agent.generate(prompt)

if result and 'main.tf' in result:
    main_tf = result['main.tf']
    print("✓ Response generated successfully")
    print()
    
    # Check for VM size
    vm_size_found = None
    location_found = None
    
    for line in main_tf.split('\n'):
        if 'vm_size' in line:
            vm_size_found = line.strip()
            print(f"VM Size: {vm_size_found}")
        if 'location = "westasia"' in line or 'location = "westasia"' in main_tf:
            location_found = True
    
    # Extract location from resource_group
    for i, line in enumerate(main_tf.split('\n')):
        if 'location = ' in line and i < 10:  # Should be near beginning
            print(f"Region: {line.strip()}")
            break
    
    print()
    print("Full main.tf:")
    print("=" * 60)
    print(main_tf)
else:
    print("❌ No response")
