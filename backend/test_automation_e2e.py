"""
End-to-end test for Lucidchart automation with Mermaid import
Tests the complete flow from Terraform → Diagram → Lucidchart → Automated Import
"""

import requests
import json
import os
import sys
import time

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
API_KEY = os.getenv("LUCIDCHART_API_KEY")

# Sample Terraform code
TERRAFORM_CODE = """
resource "azurerm_resource_group" "main" {
  name     = "rg-infrapilot"
  location = "East US"
}

resource "azurerm_virtual_network" "main" {
  name                = "vnet-main"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_subnet" "internal" {
  name                 = "subnet-internal"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
}

resource "azurerm_network_interface" "main" {
  name                = "nic-main"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "testconfiguration1"
    subnet_id                     = azurerm_subnet.internal.id
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_linux_virtual_machine" "main" {
  name                = "vm-main"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  admin_username      = "azureuser"

  network_interface_ids = [azurerm_network_interface.main.id]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts-gen2"
    version   = "latest"
  }
}
"""

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_api_status():
    """Test if the API is configured"""
    print_section("STEP 1: Check Lucidchart API Status")
    
    try:
        response = requests.get(f"{BASE_URL}/diagram/lucidchart/status")
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"API Configured: {data.get('configured', False)}")
        print(f"Message: {data.get('message', 'N/A')}")
        
        if not data.get('configured'):
            print("\n⚠️  WARNING: Lucidchart API not configured!")
            print(f"   Please set LUCIDCHART_API_KEY environment variable")
            return False
        
        print("\n✅ API is configured and ready!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking API status: {e}")
        return False

def test_export_to_lucidchart():
    """Test the complete export to Lucidchart with automation"""
    print_section("STEP 2: Export to Lucidchart with Automated Import")
    
    payload = {
        "terraform_code": TERRAFORM_CODE,
        "lucidchart_doc_title": "Automated E2E Test Diagram"
    }
    
    print(f"Sending request to: {BASE_URL}/diagram/lucidchart/export")
    print(f"Terraform code length: {len(TERRAFORM_CODE)} characters")
    print(f"Document title: {payload['lucidchart_doc_title']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/diagram/lucidchart/export",
            json=payload,
            timeout=120  # Extended timeout for automation
        )
        
        print(f"\nResponse Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        data = response.json()
        
        print("\n✅ Response received successfully!")
        print("\nResponse Details:")
        print(f"  Success: {data.get('success', False)}")
        print(f"  Automated Import: {data.get('automated_import', False)}")
        print(f"  Document ID: {data.get('lucidchart_document_id', 'N/A')}")
        print(f"  Message: {data.get('message', 'N/A')}")
        
        if data.get('automated_import'):
            print("\n🎉 AUTOMATED IMPORT SUCCESSFUL!")
            print("   The diagram has been automatically imported to Lucidchart")
        else:
            print("\n⚠️  Automated import not performed")
            if data.get('manual_import_available'):
                print("   Manual import instructions are available")
            if data.get('automation_error'):
                print(f"   Automation error: {data.get('automation_error')}")
        
        print(f"\nEdit URL: {data.get('edit_url', 'N/A')}")
        print(f"View URL: {data.get('view_url', 'N/A')}")
        print(f"Preview URL: {data.get('preview_url', 'N/A')}")
        
        if data.get('metadata'):
            print(f"\nInfrastructure Metadata:")
            print(f"  Provider: {data['metadata'].get('provider', 'N/A')}")
            print(f"  Resource Count: {data['metadata'].get('resources_count', 0)}")
            print(f"  Resource Types: {', '.join(data['metadata'].get('resource_types', []))}")
        
        print(f"\nMermaid Code Preview:")
        mermaid = data.get('mermaid_code', '')
        print(mermaid[:300] + "..." if len(mermaid) > 300 else mermaid)
        
        return data
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out (automation taking longer than expected)")
        return None
    except Exception as e:
        print(f"❌ Error during export: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_generate_diagram():
    """Test the diagram generation"""
    print_section("STEP 3: Generate Mermaid Diagram")
    
    payload = {
        "terraform_code": TERRAFORM_CODE,
        "diagram_type": "mermaid"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/diagram/generate-diagram",
            json=payload
        )
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            return None
        
        data = response.json()
        
        if data.get('success'):
            print("✅ Diagram generation successful!")
            content = data.get('data', {}).get('mermaid', '')
            if content:
                print(f"\nMermaid diagram preview ({len(content)} chars):")
                print(content[:400] + "..." if len(content) > 400 else content)
            return data
        else:
            print("❌ Diagram generation failed")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  LUCIDCHART AUTOMATION - END-TO-END TEST")
    print("=" * 70)
    print(f"\nBackend URL: {BASE_URL}")
    print(f"API Key configured: {bool(API_KEY)}")
    
    # Check prerequisites
    if not API_KEY:
        print("\n❌ LUCIDCHART_API_KEY environment variable not set!")
        print("   Please set it before running this test")
        sys.exit(1)
    
    # Run tests
    api_ready = test_api_status()
    if not api_ready:
        print("\n⚠️  Skipping export test - API not configured")
        return
    
    diagram_data = test_generate_diagram()
    if not diagram_data:
        print("\n⚠️  Skipping export test - diagram generation failed")
        return
    
    export_data = test_export_to_lucidchart()
    
    # Summary
    print_section("TEST SUMMARY")
    
    if export_data:
        print("✅ Export endpoint responded successfully")
        if export_data.get('automated_import'):
            print("✅ Automated import was performed")
            print(f"✅ Document ID: {export_data.get('lucidchart_document_id')}")
            print(f"\n🎉 FULL AUTOMATION WORKING!")
            print(f"\nOpen in Lucidchart: {export_data.get('edit_url')}")
        else:
            print("⚠️  Automated import not performed (manual import available)")
            print(f"   Reason: {export_data.get('automation_error', 'Unknown')}")
    else:
        print("❌ Export test failed")
    
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    main()
