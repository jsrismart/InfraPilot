#!/usr/bin/env python
from pricing_calculator import CloudPricingCalculator

calc = CloudPricingCalculator()

# Test D2_v3 normalization
vm_size = 'D2_v3'
normalized = calc.normalize_azure_vm_size(vm_size)
print(f'VM Normalization: {vm_size} -> {normalized}')

# Test a full pricing calculation with proper resource dict
resource = {
    'type': 'azurerm_virtual_machine',
    'instance_type': 'D2_v3',
    'quantity': 1,
    'provider': 'azure',
    'config': {'region': 'eastus'}
}

cost, description = calc.calculate_resource_cost(resource)
print(f'Cost: ${cost:.2f}')
print(f'Description: {description}')
