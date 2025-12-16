#!/usr/bin/env python3
"""Test end-to-end pricing calculation"""
from pricing_calculator import calculate_terraform_pricing

# Test Terraform code
terraform_code = '''
resource "azurerm_windows_virtual_machine" "vm" {
  name                  = "myvm"
  location              = "East US"
  resource_group_name   = "myrg"
  size                  = "D2_v3"
  admin_username        = "azureuser"
  admin_password        = "Password1234!"
}
'''

print("=" * 60)
print("TESTING END-TO-END PRICING CALCULATION")
print("=" * 60)

try:
    result = calculate_terraform_pricing(terraform_code)
    print("\n✓ Pricing Calculation Result:")
    print(f"  Total Azure Cost: ${result['total_costs']['azure']:.2f}")
    print(f"  Breakdown:")
    for item in result['breakdown']['azure']:
        print(f"    - {item['name']:20s} {item['type']:30s} ${item['cost']:.2f}")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
