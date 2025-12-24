#!/usr/bin/env python3
"""
Simple test of the Lucidchart export endpoint
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

TERRAFORM_CODE = """
resource "azurerm_resource_group" "main" {
  name     = "rg-test"
  location = "East US"
}

resource "azurerm_virtual_network" "main" {
  name                = "vnet-main"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}
"""

print("Testing Lucidchart Export Endpoint...")
print("=" * 70)

# Test 1: Check API status
print("\n1. Checking API Status...")
try:
    response = requests.get(f"{BASE_URL}/diagram/lucidchart/status", timeout=5)
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Configured: {data.get('configured', False)}")
    print(f"   Message: {data.get('message')}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Generate Diagram
print("\n2. Generating Diagram...")
try:
    payload = {
        "terraform_code": TERRAFORM_CODE,
        "diagram_type": "mermaid"
    }
    response = requests.post(f"{BASE_URL}/diagram/generate-diagram", json=payload, timeout=10)
    if response.status_code == 200:
        print(f"   ✅ Success")
    else:
        print(f"   ❌ Error {response.status_code}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Export to Lucidchart
print("\n3. Exporting to Lucidchart with Automation...")
try:
    payload = {
        "terraform_code": TERRAFORM_CODE,
        "lucidchart_doc_title": "Test Automation Diagram"
    }
    print(f"   Sending request...")
    response = requests.post(f"{BASE_URL}/diagram/lucidchart/export", json=payload, timeout=120)
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success")
        print(f"   Automated Import: {data.get('automated_import', False)}")
        print(f"   Document ID: {data.get('lucidchart_document_id', 'N/A')}")
        print(f"   Message: {data.get('message', 'N/A')}")
        
        if data.get('edit_url'):
            print(f"\n   Open in Lucidchart:")
            print(f"   {data.get('edit_url')}")
        
        # Show full response in JSON format (pretty printed)
        print("\n   Full Response:")
        print(json.dumps(data, indent=2))
    else:
        print(f"   ❌ Error")
        print(f"   Response: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    print(f"   ⚠️  Request timed out (automation may be running)")
except Exception as e:
    print(f"   Error: {type(e).__name__}: {e}")

print("\n" + "=" * 70)
print("Test Complete")
