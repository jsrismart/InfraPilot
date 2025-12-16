#!/usr/bin/env python3
"""Debug script to test TerraformParser and pricing extraction"""

from diagram_generator import TerraformParser

# Test Terraform code with Azure VM
terraform_code = '''
provider "azurerm" {
  features {}
}

resource "azurerm_virtual_machine" "main" {
  name                  = "my-vm"
  location              = "East US"
  resource_group_name   = "my-rg"
  vm_size               = "Standard_D2s_v3"

  os_profile {
    computer_name  = "hostname"
    admin_username = "testadmin"
  }

  os_profile_linux_config {
    disable_password_authentication = true
  }

  storage_os_disk {
    name              = "myosdisk1"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Premium_LRS"
  }

  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }
}
'''

print("=" * 80)
print("TESTING TERRAFORM PARSER")
print("=" * 80)

try:
    parser = TerraformParser(terraform_code)
    parser.parse()
    
    print(f"\nTotal resources found: {len(parser.resources)}")
    
    for resource in parser.resources:
        print(f"\n--- Resource: {resource.name} ---")
        print(f"Type: {resource.type}")
        print(f"Properties: {resource.properties}")
        
        # Check for vm_size specifically
        if 'vm_size' in resource.properties:
            print(f"✓ vm_size found: {resource.properties['vm_size']}")
        else:
            print("✗ vm_size NOT found in properties")
            print(f"  Available keys: {list(resource.properties.keys())}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
