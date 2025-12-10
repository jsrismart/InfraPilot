"""
Direct test of pricing calculation without needing the server running
"""
import sys
sys.path.insert(0, 'c:\\Users\\SridharJayaraman\\Downloads\\infrapilot 2\\infrapilot\\backend')

from pricing_calculator import calculate_terraform_pricing

terraform_code = '''
resource "azurerm_virtual_machine" "example" {
  name                  = "example-vm"
  location              = "East US"
  resource_group_name   = "example-rg"
  vm_size               = "Standard_D2s_v3"
}
'''

print("=" * 80)
print("Testing Azure VM pricing calculation directly")
print("=" * 80)
print(f"\nTerraform Code:\n{terraform_code}")
print("\nCalling calculate_terraform_pricing()...")

try:
    result = calculate_terraform_pricing(terraform_code)
    print("\n" + "=" * 80)
    print("RESULT:")
    print("=" * 80)
    import json
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
