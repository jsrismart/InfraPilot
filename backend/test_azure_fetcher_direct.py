#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test real-time Azure pricing fetcher directly"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from real_time_pricing_fetcher import AzurePricingFetcher

print("=" * 80)
print("TESTING AZURE REAL-TIME PRICING FETCHER")
print("=" * 80)
print()

fetcher = AzurePricingFetcher()

test_vms = [
    ('Standard_D32a_v4', 'eastus'),
    ('Standard_B1s', 'eastus'),
    ('Standard_D2s_v4', 'eastus'),
    ('Standard_E4s_v3', 'eastus'),
]

for vm_size, region in test_vms:
    print(f"\n[TEST] {vm_size} in {region}")
    print("-" * 80)
    
    price = fetcher.get_vm_pricing(vm_size, region)
    
    if price:
        print(f"[SUCCESS] Monthly Price: ${price:.2f}")
    else:
        print(f"[FAIL] No price found from Azure API")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
