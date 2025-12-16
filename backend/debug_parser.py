#!/usr/bin/env python3
"""Debug Terraform parser to see what properties are extracted"""

from diagram_generator import TerraformParser

terraform_code = """
resource "azurerm_windows_virtual_machine" "example" {
  name                = "example-vm"
  location            = "East US"
  resource_group_name = "example-rg"
  size                = "Standard_D2s_v4"
}
"""

parser = TerraformParser(terraform_code)
print(f"Found {len(parser.resources)} resources\n")

for resource in parser.resources:
    print(f"Resource Type: {resource.type}")
    print(f"Resource Name: {resource.name}")
    
    if hasattr(resource, 'properties'):
        print(f"Properties: {resource.properties}")
    else:
        print("No properties attribute")
    
    if hasattr(resource, 'arguments'):
        print(f"Arguments: {resource.arguments}")
    else:
        print("No arguments attribute")
    
    # Check all attributes
    print(f"\nAll attributes: {dir(resource)}")
    print("\n" + "="*60 + "\n")
