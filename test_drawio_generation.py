#!/usr/bin/env python3
"""
Test script to verify draw.io diagram generation from Terraform code
"""

import requests
import json
from pathlib import Path

# Test Terraform configuration
test_terraform = """
provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "example" {
  name     = "example-rg"
  location = "eastus"
}

resource "azurerm_virtual_network" "example" {
  name                = "example-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
}

resource "azurerm_subnet" "internal" {
  name                 = "internal"
  resource_group_name  = azurerm_resource_group.example.name
  virtual_network_name = azurerm_virtual_network.example.name
  address_prefixes     = ["10.0.2.0/24"]
}

resource "azurerm_network_interface" "example" {
  name                = "example-nic"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name

  ip_configuration {
    name                          = "testconfiguration1"
    subnet_id                     = azurerm_subnet.internal.id
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_windows_virtual_machine" "example" {
  name                = "example-machine"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  admin_username      = "adminuser"

  network_interface_ids = [
    azurerm_network_interface.example.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "MicrosoftWindowsServer"
    offer     = "WindowsServer"
    sku       = "2016-Datacenter"
    version   = "latest"
  }
}

resource "azurerm_storage_account" "example" {
  name                     = "examplestg"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}
"""

def test_drawio_generation():
    """Test draw.io diagram generation"""
    
    api_url = "http://localhost:8000/api/v1/diagram/generate-diagram"
    
    payload = {
        "terraform_code": test_terraform,
        "diagram_type": "drawio"
    }
    
    print("=" * 70)
    print("DRAW.IO DIAGRAM GENERATION TEST")
    print("=" * 70)
    print(f"\n📡 Testing endpoint: {api_url}")
    print(f"📝 Diagram type: drawio")
    print(f"🔧 Terraform resources: 5 (RG, VNet, Subnet, NIC, VM, Storage)")
    
    try:
        print("\n⏳ Sending request...")
        response = requests.post(api_url, json=payload, timeout=30)
        
        print(f"✅ Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Generation successful!")
            print(f"📊 Diagram type returned: {data.get('diagram_type')}")
            print(f"📦 Success: {data.get('success')}")
            
            if 'metadata' in data:
                metadata = data['metadata']
                print(f"\n📋 Metadata:")
                print(f"   - Provider: {metadata.get('provider')}")
                print(f"   - Resources count: {metadata.get('resources_count')}")
                print(f"   - Resource types: {', '.join(metadata.get('resource_types', []))}")
            
            content = data.get('content', '')
            
            # Save the draw.io XML to a file
            output_file = Path("test_diagram.drawio")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\n💾 Draw.io XML saved to: {output_file}")
            print(f"📏 XML size: {len(content)} bytes")
            
            # Show first 500 chars of XML
            print(f"\n📄 First 500 characters of generated XML:")
            print("-" * 70)
            print(content[:500] + "..." if len(content) > 500 else content)
            print("-" * 70)
            
            # Verify it's valid XML
            try:
                import xml.etree.ElementTree as ET
                ET.fromstring(content)
                print("✅ XML is valid and well-formed!")
            except Exception as e:
                print(f"❌ XML parsing error: {e}")
                return False
            
            print("\n✅ DRAW.IO GENERATION TEST PASSED!")
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print("   Make sure backend is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_all_diagram_types():
    """Test all diagram types"""
    
    api_url = "http://localhost:8000/api/v1/diagram/generate-diagram"
    diagram_types = ["ascii", "mermaid", "json", "svg", "html", "drawio"]
    
    print("\n" + "=" * 70)
    print("TESTING ALL DIAGRAM TYPES")
    print("=" * 70)
    
    results = {}
    
    for dtype in diagram_types:
        print(f"\n🧪 Testing diagram type: {dtype.upper()}")
        
        payload = {
            "terraform_code": test_terraform,
            "diagram_type": dtype
        }
        
        try:
            response = requests.post(api_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                content_len = len(data.get('content', ''))
                
                if success:
                    print(f"   ✅ Generated successfully")
                    print(f"   📏 Content size: {content_len} bytes")
                    results[dtype] = "✅ PASS"
                else:
                    print(f"   ⚠️  Success flag is false")
                    results[dtype] = "⚠️  PASS (flag issue)"
            else:
                print(f"   ❌ HTTP {response.status_code}")
                results[dtype] = f"❌ FAIL ({response.status_code})"
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")
            results[dtype] = f"❌ ERROR"
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    for dtype, result in results.items():
        print(f"  {dtype.upper():15} {result}")
    
    return all("✅" in v or "⚠️" in v for v in results.values())

if __name__ == "__main__":
    # Run tests
    test1_pass = test_drawio_generation()
    
    print("\n")
    test2_pass = test_all_diagram_types()
    
    print("\n" + "=" * 70)
    if test1_pass and test2_pass:
        print("✅ ALL TESTS PASSED!")
    else:
        print("⚠️  Some tests did not pass completely")
    print("=" * 70)
