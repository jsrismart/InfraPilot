"""
AZURE VM PRICING BUG - ROOT CAUSE ANALYSIS & FIX
================================================

Analyzed: December 10, 2025
Issue: Azure VM pricing returns $0.00 instead of $70.08 for Standard_D2s_v3

EXECUTION TRACE
===============

1. TERRAFORM PARSING ✓
   - TerraformParser correctly extracts: 
     * vm_size = "Standard_D2s_v3"
     * location = "East US"
   - Properties dict populated correctly

2. PRICING CALCULATION - FLOW CHECK
   pricing_calculator.py line 760-800:
   
   for resource in parser.resources:
       # Extract instance_type from resource.properties
       for prop_name in ['size', 'instance_type', 'machine_type', 'vm_size', 'instance_class', 'name']:
           if prop_name in resource.properties:
               instance_type = resource.properties[prop_name]
               # This SHOULD find 'vm_size' = 'Standard_D2s_v3'

3. REAL-TIME PRICING INITIALIZATION ✓
   pricing_calculator.py line 17-22:
   
   try:
       from real_time_pricing_fetcher import pricing_fetcher, USE_FALLBACK_PRICING
       REAL_TIME_PRICING_ENABLED = True
   except ImportError:
       REAL_TIME_PRICING_ENABLED = False

   Status: ✓ Module exists and can be imported
   Status: ✓ REAL_TIME_PRICING_ENABLED = True

4. AZURE PRICING FETCHER ✓
   real_time_pricing_fetcher.py - AzurePricingFetcher class:
   
   - Initialized with: self.enabled = AZURE_CONFIG["enabled"]
   - AZURE_CONFIG["enabled"] = True (from pricing_config.py)
   - Uses Azure Retail Prices API: https://prices.azure.com/api/retail/prices
   
   Method: get_vm_pricing(vm_size, region)
   - Input: vm_size='Standard_D2s_v3', region='eastus'
   - Expected output: float price in $/month
   - Returns: approximately $70.08

5. THE ACTUAL API CALL
   real_time_pricing_fetcher.py line 327-380:
   
   url = "https://prices.azure.com/api/retail/prices"
   filter_str = f"armSkuName eq '{vm_size}'"
   
   This calls Azure's public pricing API which returns:
   - armSkuName: "Standard_D2s_v3"
   - retailPrice: ~$0.096/hour (hourly)
   - Converts to: $0.096 * 730 = ~$70.08/month


KEY FINDINGS
============

✓ Terraform parser WORKS - vm_size is extracted
✓ Pricing calculator IMPORTS successfully
✓ REAL_TIME_PRICING_ENABLED = True
✓ pricing_fetcher object is initialized
✓ AzurePricingFetcher is initialized
✓ Azure Retail Prices API endpoint is correct
✓ VM size normalization is correct: "Standard_D2s_v3"
✓ Region normalization exists


MYSTERY: Why does pricing show $0.00 if all pieces are working?

HYPOTHESIS OPTIONS:
===================

OPTION 1: instance_type NOT being passed to pricing calculator
   - Problem: resource.properties might be empty dict
   - Evidence: Would fail at line 793-796 check
   - Fix: Ensure TerraformParser populates properties correctly

OPTION 2: Real-time API call is failing silently
   - Problem: Exception caught at line 523-524
   - Evidence: Would log error but return 0
   - Fix: Need backend logs to see actual error

OPTION 3: Instance_type is None despite vm_size existing
   - Problem: Wrong property name search
   - Evidence: Loop doesn't match property name
   - Fix: Verify search loop is correct (it looks good)

OPTION 4: Region normalization failing
   - Problem: normalize_azure_region() might not handle "East US"
   - Evidence: Would pass wrong region to API
   - Fix: Check region_map in AzurePricingFetcher

OPTION 5: pricing_fetcher.get_vm_pricing() returns None
   - Problem: API request fails or returns empty results
   - Evidence: Line 519 check fails - returns $0.00
   - Fix: Need to verify API is working


RECOMMENDED DEBUGGING STEPS
============================

1. START BACKEND WITH DEBUG LOGGING:
   cd backend
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8001

2. MAKE A TEST CALL:
   curl -X POST http://localhost:8001/api/v1/pricing \
     -H "Content-Type: application/json" \
     -d '{
       "terraform_code": "resource \"azurerm_virtual_machine\" \"example\" {\n  name = \"example-vm\"\n  location = \"East US\"\n  vm_size = \"Standard_D2s_v3\"\n}"
     }'

3. WATCH BACKEND LOGS FOR:
   [PRICING] Processing resource: type=azurerm_virtual_machine
   [PRICING] Properties dict: {...}
   [PRICING] Found instance_type 'Standard_D2s_v3' from property 'vm_size'
   [AZURE_PRICING] Normalized VM size: 'Standard_D2s_v3' → 'Standard_D2s_v3'
   [AZURE_PRICING] Normalized region: 'East US' → 'eastus'
   [AZURE_PRICING] Calling get_pricing('azure', 'vm', 'Standard_D2s_v3', region='eastus')
   [AZURE_PRICING] Got response: {...}


PROPOSED FIX LOCATIONS
======================

If instance_type is not being found:
   → Check diagram_generator.py TerraformParser._parse_properties()
   → Ensure it's extracting property values correctly
   → Look for: properties['vm_size'] = 'Standard_D2s_v3'

If region is wrong:
   → Check normalize_azure_region() in pricing_calculator.py around line 690
   → Ensure "East US" maps to "eastus"

If API returns no data:
   → Check Azure Retail Prices API is accessible
   → Verify network/firewall isn't blocking it
   → Test manually: https://prices.azure.com/api/retail/prices?$filter=armSkuName eq 'Standard_D2s_v3'

If get_vm_pricing returns None:
   → Check exception handling in real_time_pricing_fetcher.py line 523
   → Add more specific error logging


DEBUG LOGGING ADDED
===================

Modified pricing_calculator.py to add detailed logs:

✓ Line 768: Log resource type and name being processed
✓ Line 769: Log whether properties dict exists
✓ Line 770: Log properties content
✓ Line 771: Log properties keys
✓ Line 776-778: Log when instance_type found and from which property
✓ Line 511: Log REAL_TIME_PRICING_ENABLED and pricing_fetcher status
✓ Line 517: Log normalized VM size
✓ Line 520: Log normalized region
✓ Line 523: Log API call being made
✓ Line 524: Log API response received
✓ Line 526-527: Log when price found successfully
✓ Line 529-530: Log when API returns no data
✓ Line 532: Log exceptions with full traceback

These logs will provide visibility into where exactly the $0.00 is coming from.
"""

print(__doc__)
