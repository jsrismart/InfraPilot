#!/usr/bin/env python
"""Validation tests for VM and Region normalization fixes"""
from pricing_calculator import CloudPricingCalculator

calc = CloudPricingCalculator()

print('VALIDATION TEST SUITE')
print('=' * 70)

# Test 1: VM Size Normalization
print('\n[TEST 1] VM Size Normalization')
print('-' * 70)
test_sizes = ['D2_v3', 'Standard_D2s_v3', 'd4_v4', 'B1s', 'Standard_B2s']
for size in test_sizes:
    normalized = calc.normalize_azure_vm_size(size)
    print(f'  {size:25} -> {normalized}')

# Test 2: Region Normalization
print('\n[TEST 2] Region Normalization')
print('-' * 70)
test_regions = [
    ('East US', 'eastus'),
    ('eastus', 'eastus'),
    ('West US 2', 'westus2'),
    ('North Europe', 'northeurope'),
    ('Southeast Asia', 'southeastasia')
]
for region_in, region_expected in test_regions:
    normalized = calc.normalize_azure_region(region_in)
    status = 'PASS' if normalized == region_expected else 'FAIL'
    print(f'  {region_in:25} -> {normalized:20} [{status}]')

# Test 3: Full Pricing Calculation
print('\n[TEST 3] Full Pricing - VM in East US')
print('-' * 70)
resource = {
    'type': 'azurerm_windows_virtual_machine',
    'instance_type': 'Standard_D2s_v3',
    'quantity': 1,
    'provider': 'azure',
    'config': {'region': 'East US'}
}
cost, description = calc.calculate_resource_cost(resource)
print(f'  Resource Type:  {resource["type"]}')
print(f'  Instance Type:  {resource["instance_type"]}')
print(f'  Region:         {resource["config"]["region"]}')
print(f'  Monthly Cost:   ${cost:.2f}')
print(f'  Description:    {description}')
status = 'PASS' if cost > 0 and 'LIVE AZURE API' in description else 'FAIL'
print(f'  Status:         {status}')

# Test 4: Terraform parsing simulation
print('\n[TEST 4] Terraform Parsing Simulation (D2_v3 format)')
print('-' * 70)
from diagram_generator import TerraformParser
terraform_code = '''
resource "azurerm_windows_virtual_machine" "web" {
  name                = "web-vm"
  location            = "East US"
  resource_group_name = "rg"
  vm_size             = "Standard_D2s_v3"
}
'''
try:
    parser = TerraformParser(terraform_code)
    resource = parser.resources[0]
    print(f'  Parsed Resource: {resource.name}')
    print(f'  Resource Type:   {resource.type}')
    print(f'  VM Size:         {resource.properties.get("vm_size")}')
    print(f'  Location:        {resource.properties.get("location")}')
    
    # Calculate pricing
    instance_type = resource.properties.get('vm_size')
    region = resource.properties.get('location')
    normalized_vm = calc.normalize_azure_vm_size(instance_type)
    normalized_region = calc.normalize_azure_region(region)
    
    print(f'  Normalized VM:   {normalized_vm}')
    print(f'  Normalized Reg:  {normalized_region}')
    
    calc_resource = {
        'type': resource.type,
        'instance_type': instance_type,
        'quantity': 1,
        'provider': 'azure',
        'config': {'region': region}
    }
    cost, desc = calc.calculate_resource_cost(calc_resource)
    print(f'  Final Cost:      ${cost:.2f}')
    print(f'  Final Desc:      {desc}')
    print(f'  Status:          {"PASS" if cost > 0 else "FAIL"}')
except Exception as e:
    print(f'  ERROR: {e}')
    import traceback
    traceback.print_exc()

print('\n' + '=' * 70)
print('VALIDATION COMPLETE')
print('=' * 70)
