#!/usr/bin/env python3
"""Debug what instance_type is being passed"""

from diagram_generator import TerraformParser
from pricing_calculator import CloudPricingCalculator

terraform_code = """
resource "azurerm_windows_virtual_machine" "example" {
  name                = "example-vm"
  location            = "East US"
  resource_group_name = "example-rg"
  size                = "Standard_D2s_v4"
}
"""

parser = TerraformParser(terraform_code)
print(f"Parsed {len(parser.resources)} resources\n")

for resource in parser.resources:
    print(f"Resource: {resource.name} ({resource.type})")
    print(f"Properties: {resource.properties}\n")
    
    # Simulate what the pricing calculator does
    instance_type = None
    if hasattr(resource, 'properties') and resource.properties:
        for prop_name in ['size', 'instance_type', 'machine_type', 'vm_size', 'instance_class', 'name']:
            if prop_name in resource.properties:
                instance_type = resource.properties[prop_name]
                print(f"[OK] Found instance_type via '{prop_name}': {instance_type}")
                break
    
    if instance_type is None:
        print("[ERROR] No instance_type found!")
    else:
        print(f"\nTesting pricing lookup for: {instance_type}")
        calc = CloudPricingCalculator()
        cost, desc = calc._calculate_azure_cost('azurerm_windows_virtual_machine', instance_type, 1, {'config': {}})
        print(f"Cost: ${cost:.2f}/month")
        print(f"Description: {desc}")
