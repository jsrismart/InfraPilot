#!/usr/bin/env python
"""Debug what instance_type is being extracted from Terraform"""
import sys
sys.path.insert(0, '.')

from diagram_generator import TerraformParser
from pricing_calculator import calculate_terraform_pricing

# Test with the exact Terraform from the screenshot
terraform_code = '''
resource "azurerm_windows_virtual_machine" "example" {
  name                = "example-vm"
  location            = "East US"
  resource_group_name = "example"
  vm_size             = "Standard_D2s_v3"

  admin_username = "adminuser"

  admin_password = "P@ssw0rd1234!"

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "MicrosoftWindowsServer"
    offer     = "WindowsServer"
    sku       = "2019-Datacenter"
    version   = "latest"
  }
}
'''

print("=" * 80)
print("PARSING TERRAFORM AND EXTRACTING INSTANCE TYPES")
print("=" * 80)

try:
    parser = TerraformParser(terraform_code)
    print(f"\n[OK] Parser created successfully")
    print(f"[OK] Found {len(parser.resources)} resources\n")
    
    for resource in parser.resources:
        print(f"Resource: {resource.name}")
        print(f"Type: {resource.type}")
        print(f"Properties: {resource.properties if hasattr(resource, 'properties') else 'N/A'}")
        
        # Check what instance_type would be extracted
        instance_type = None
        if hasattr(resource, 'properties') and resource.properties:
            for prop_name in ['size', 'instance_type', 'machine_type', 'vm_size', 'instance_class', 'name']:
                if prop_name in resource.properties:
                    instance_type = resource.properties[prop_name]
                    print(f"\n[OK] Found instance_type via '{prop_name}': {instance_type}")
                    break
        
        if instance_type is None:
            print("\n[ERROR] No instance_type found!")
        else:
            print(f"\nTesting pricing lookup for: {instance_type}")
            from pricing_calculator import CloudPricingCalculator
            calc = CloudPricingCalculator()
            cost, desc = calc._calculate_azure_cost('azurerm_windows_virtual_machine', instance_type, 1, {'config': {'region': 'East US'}})
            print(f"Result: ${cost:.2f} - {desc}")
        
        print("\n" + "=" * 80)

except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

# Now test the full pricing calculation
print("\n\nTESTING FULL PRICING CALCULATION")
print("=" * 80)
try:
    results = calculate_terraform_pricing(terraform_code)
    print("Results:")
    import json
    print(json.dumps(results, indent=2, default=str))
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
