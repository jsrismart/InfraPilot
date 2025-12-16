#!/usr/bin/env python3
"""Debug the terraform parsing"""
import sys
sys.path.insert(0, '.')

from diagram_generator import TerraformParser

terraform_code = '''resource "azurerm_windows_virtual_machine" "main" {
  name                = "vm"
  location            = "eastus"
  resource_group_name = "rg"
  vm_size = "Standard_D2s_v3"
}'''

parser = TerraformParser(terraform_code)
parser.parse()

print(f"Found {len(parser.resources)} resources")
for res in parser.resources:
    print(f'\nType: {res.type}')
    print(f'Name: {res.name}')
    print(f'Properties: {res.properties}')
    print(f'vm_size: {res.properties.get("vm_size", "NOT FOUND")}')
