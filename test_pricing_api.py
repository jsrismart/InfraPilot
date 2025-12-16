"""
Direct test of the full pricing API response
"""
import sys
sys.path.insert(0, 'c:\\Users\\SridharJayaraman\\Downloads\\infrapilot 2\\infrapilot\\backend')

from app.api.v1.pricing import calculate_pricing, PricingRequest

terraform_code = '''
resource "azurerm_virtual_machine" "example" {
  name = "test-vm"
  location = "East US"
  vm_size = "Standard_D2s_v3"
}
'''

print("=" * 80)
print("Testing Pricing API Response Directly")
print("=" * 80)

request = PricingRequest(
    terraform_code=terraform_code,
    include_breakdown=True,
    include_comparison=True
)

try:
    response = calculate_pricing(request)
    print("\nAPI Response:")
    print("-" * 80)
    
    import json
    response_dict = response.model_dump() if hasattr(response, 'model_dump') else response.__dict__
    print(json.dumps(response_dict, indent=2, default=str))
    
    print("\n" + "=" * 80)
    print("VERIFICATION:")
    print("=" * 80)
    print(f"Azure Total Cost: ${response.total_costs['azure']:.2f}")
    print(f"Azure Breakdown: {response.breakdown['azure']}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
