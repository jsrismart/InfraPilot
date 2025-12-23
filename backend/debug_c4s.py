#!/usr/bin/env python3
"""Debug C4s_v3 pricing issue"""

import sys
sys.path.insert(0, '.')

from real_time_pricing_fetcher import AzurePricingFetcher
import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

fetcher = AzurePricingFetcher()

print("Testing C4s_v3 direct fetch...")
price = fetcher.get_vm_pricing('Standard_C4s_v3', 'eastus')
print(f"Result: {price}")

if price:
    print(f"Success: ${price:.2f}/month")
else:
    print("Failed: No price returned")
