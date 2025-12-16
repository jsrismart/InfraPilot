#!/usr/bin/env python3
"""Debug pricing calculation"""

from pricing_calculator import calculate_terraform_pricing
import json

terraform_code = """
resource "azurerm_windows_virtual_machine" "example" {
  name                = "example-vm"
  location            = "East US"
  resource_group_name = "example-rg"
  size                = "Standard_D2s_v4"
}
"""

result = calculate_terraform_pricing(terraform_code)

print("Result:")
print(json.dumps(result, indent=2, default=str))
