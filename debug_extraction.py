#!/usr/bin/env python3
"""Debug terraform value extraction"""
import sys
import re

# Simulate the extraction function
def _extract_terraform_value(terraform_code: str, reference: str):
    """Extract actual value from Terraform code"""
    if not reference or not isinstance(reference, str):
        return None
    
    reference_str = str(reference).strip()
    print(f"\n🔍 Extracting: {reference_str}")
    
    # If it's a literal value (not a reference), return as-is
    if not any(c in reference_str for c in ['.', '$', '{', '}']):
        print(f"  ✓ Not a reference, returning as-is")
        return reference_str
    
    try:
        # Handle direct variable references like "azurerm_resource_group.main.location"
        if '.' in reference_str and not reference_str.startswith('$'):
            parts = reference_str.split('.')
            if len(parts) >= 3:
                resource_type = parts[0]
                resource_name = parts[1]
                property_name = '.'.join(parts[2:])
                
                print(f"  Type: {resource_type}, Name: {resource_name}, Property: {property_name}")
                
                # Find the resource block
                pattern = rf'resource\s+"{resource_type}"\s+"{resource_name}"\s*\{{([\s\S]*?)\n\}}'
                print(f"  Using pattern: {pattern}")
                
                match = re.search(pattern, terraform_code, re.DOTALL)
                if match:
                    resource_body = match.group(1)
                    print(f"  ✓ Found resource block")
                    print(f"  Resource body preview: {resource_body[:200]}...")
                    
                    # Extract the property value
                    prop_patterns = [
                        rf'{property_name}\s*=\s*"([^"]*)"',  # Quoted string
                        rf'{property_name}\s*=\s*\'([^\']*)\'',  # Single quoted
                        rf'{property_name}\s*=\s*([^,\n}}]+)',  # Unquoted
                    ]
                    
                    for i, prop_pattern in enumerate(prop_patterns):
                        print(f"  Trying pattern {i+1}: {prop_pattern}")
                        prop_match = re.search(prop_pattern, resource_body)
                        if prop_match:
                            value = prop_match.group(1).strip()
                            print(f"  ✓ MATCHED! Value: {value}")
                            return value
                    
                    print(f"  ✗ No patterns matched for property: {property_name}")
                else:
                    print(f"  ✗ Resource block NOT found")
                    # Try alternative pattern
                    alt_pattern = rf'resource\s+"{resource_type}"\s+"{resource_name}"\s*\{{'
                    alt_match = re.search(alt_pattern, terraform_code)
                    if alt_match:
                        print(f"  But found resource declaration at position {alt_match.start()}")
                        print(f"  Context: ...{terraform_code[max(0, alt_match.start()-50):alt_match.start()+100]}...")
    except Exception as e:
        print(f"  ✗ Exception: {e}")
    
    return None

# Test terraform code
terraform = '''resource "azurerm_resource_group" "main" {
  name     = "${var.project_name}-rg"
  location = "eastus"
}

resource "azurerm_virtual_network" "main" {
  name                = "${var.project_name}-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_subnet" "internal" {
  name                 = "${var.project_name}-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
}

resource "azurerm_network_interface" "main" {
  name                = "${var.project_name}-nic"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "testconfiguration1"
    subnet_id                     = azurerm_subnet.internal.id
    private_ip_address_allocation = "Dynamic"
  }
}'''

print("=" * 80)
print("TERRAFORM CODE:")
print("=" * 80)
print(terraform)

# Test extraction
print("\n" + "=" * 80)
print("TEST EXTRACTIONS:")
print("=" * 80)

reference = "azurerm_resource_group.main.location"
result = _extract_terraform_value(terraform, reference)
print(f"\n✅ FINAL RESULT: {result}")
