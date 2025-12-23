#!/usr/bin/env python3
"""Test C-series VM pricing with fallback"""

import sys
sys.path.insert(0, '.')

from real_time_pricing_fetcher import AzurePricingFetcher
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

fetcher = AzurePricingFetcher()

print("=" * 80)
print("Testing C-series VM pricing with fallback mechanism")
print("=" * 80)

test_vms = [
    'Standard_C2s_v3',
    'Standard_C4s_v3',
    'Standard_C4c_v3',
    'Standard_C8s_v3',
    'Standard_D2s_v3',  # Control - should work directly
]

for vm in test_vms:
    print(f"\n[TEST] {vm}")
    print("-" * 80)
    price = fetcher.get_vm_pricing(vm, 'eastus')
    if price:
        print(f"✓ Price: ${price:.2f}/month")
    else:
        print(f"✗ No price available")
