#!/usr/bin/env python3
"""Test API endpoints and diagnose issues"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001/api/v1"

def test_endpoint(name, method, path, payload=None):
    """Test an API endpoint"""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    print(f"Method: {method}")
    print(f"URL: {BASE_URL}{path}")
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{path}", timeout=10)
        else:
            print(f"Payload: {json.dumps(payload, indent=2)[:200]}...")
            response = requests.post(f"{BASE_URL}{path}", json=payload, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)[:500]}...")
            return response.status_code == 200, data
        except:
            print(f"Response text: {response.text[:200]}")
            return False, None
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False, None

# Wait for server
time.sleep(2)

print("\n" + "=" * 60)
print("INFRAPILOT API DIAGNOSTIC TEST")
print("=" * 60)

# Test 1: Health Check
success, _ = test_endpoint(
    "Health Check",
    "GET",
    "/health/status"
)

# Test 2: Pricing Formats
success, _ = test_endpoint(
    "Get Pricing Formats",
    "GET",
    "/pricing/pricing-formats"
)

# Test 3: Pricing Calculation
pricing_payload = {
    "terraform_code": '''
resource "azurerm_windows_virtual_machine" "example" {
  name                = "vm"
  location            = "East US"
  resource_group_name = "rg"
  vm_size             = "D2_v3"
}
''',
    "include_breakdown": True,
    "include_comparison": True
}

success, pricing_result = test_endpoint(
    "Calculate Pricing",
    "POST",
    "/pricing/calculate-pricing",
    pricing_payload
)

if pricing_result:
    print(f"\n✓ Pricing Data Retrieved:")
    print(f"  - Total Costs: {pricing_result.get('total_costs')}")
    print(f"  - Breakdown: {pricing_result.get('breakdown')}")

# Test 4: IaC Generation
iac_payload = {
    "prompt": "Create an Azure VM with D2_v3 size in East US region"
}

success, iac_result = test_endpoint(
    "Generate IaC",
    "POST",
    "/infra/generate-iac",
    iac_payload
)

if iac_result:
    print(f"\n✓ IaC Generated:")
    if 'iac' in iac_result:
        for filename, content in iac_result.get('iac', {}).items():
            lines = len(str(content).split('\n'))
            print(f"  - {filename}: {lines} lines")

# Test 5: Diagram Generation
diagram_payload = {
    "terraform_code": '''
resource "azurerm_windows_virtual_machine" "example" {
  name                = "vm"
  location            = "East US"
  resource_group_name = "rg"
  vm_size             = "D2_v3"
}
''',
    "diagram_type": "ascii"
}

success, diagram_result = test_endpoint(
    "Generate Diagram (ASCII)",
    "POST",
    "/diagram/generate-diagram",
    diagram_payload
)

if diagram_result and diagram_result.get('content'):
    print(f"\n✓ Diagram Generated (Preview):")
    print(diagram_result['content'][:300])

print("\n" + "=" * 60)
print("DIAGNOSTIC TEST COMPLETE")
print("=" * 60)
