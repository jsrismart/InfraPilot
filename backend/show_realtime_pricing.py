#!/usr/bin/env python
"""Show real-time pricing in action"""

from pricing_calculator import calculate_terraform_pricing

tf_code = '''
resource "azurerm_windows_virtual_machine" "vm" { 
  vm_size = "Standard_D2s_v4"
}

resource "azurerm_sql_database" "db" {
  name = "testdb"
}

resource "azurerm_storage_account" "storage" {
  name = "teststorage"
}
'''

print("="*80)
print("REAL-TIME AZURE PRICING TEST")
print("="*80)

result = calculate_terraform_pricing(tf_code)

print("\n✓ AZURE COST BREAKDOWN (LIVE FROM API)")
print("-"*80)
for item in result['breakdown']['azure']:
    print(f"Resource:     {item['name']}")
    print(f"Type:         {item['type']}")
    print(f"Monthly Cost: ${item['cost']:.2f}")
    print(f"Source:       {item['description']}")
    print()

print("-"*80)
print(f"Total Azure: ${result['total_costs']['azure']:.2f}/month")
print("="*80)
