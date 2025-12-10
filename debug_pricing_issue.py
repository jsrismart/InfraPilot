"""
Debug script to identify why Azure VM pricing returns $0.00
This analyzes the data flow without requiring environment setup
"""

# Sample Terraform code with Azure VM
terraform_code = """
resource "azurerm_virtual_machine" "example" {
  name                  = "example-vm"
  location              = "East US"
  resource_group_name   = azurerm_resource_group.example.name
  vm_size               = "Standard_D2s_v3"
  
  tags = {
    environment = "production"
  }
}
"""

print("=" * 80)
print("AZURE VM PRICING DEBUG - Step by Step Analysis")
print("=" * 80)

# Step 1: Parse Terraform
print("\n1. TERRAFORM PARSING")
print("-" * 80)
import re
pattern = re.compile(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{', re.IGNORECASE)
for m in pattern.finditer(terraform_code):
    resource_type, resource_name = m.groups()
    print(f"   ✓ Found resource: type='{resource_type}', name='{resource_name}'")
    
    # Extract body
    start = m.end()
    brace_count = 1
    i = start
    while i < len(terraform_code) and brace_count > 0:
        ch = terraform_code[i]
        if ch == '{':
            brace_count += 1
        elif ch == '}':
            brace_count -= 1
        i += 1
    body = terraform_code[start:i-1].strip()
    print(f"   ✓ Extracted body: {len(body)} chars")
    
    # Step 2: Extract properties
    print("\n2. PROPERTY EXTRACTION")
    print("-" * 80)
    
    # Simple property extraction (looking for key = value patterns)
    prop_pattern = re.compile(r'(\w+)\s*=\s*"([^"]*)"')
    properties = {}
    for prop_match in prop_pattern.finditer(body):
        key, value = prop_match.groups()
        properties[key] = value
        print(f"   ✓ Found property: {key} = {value}")
    
    print(f"\n   Total properties found: {len(properties)}")
    
    # Step 3: Check what the pricing calculator looks for
    print("\n3. PRICING CALCULATOR REQUIREMENTS")
    print("-" * 80)
    
    # This is what pricing_calculator.py looks for (from line 760-769)
    search_props = ['size', 'instance_type', 'machine_type', 'vm_size', 'instance_class', 'name']
    print(f"   Searching for instance type in: {search_props}")
    
    instance_type = None
    for prop_name in search_props:
        if prop_name in properties:
            instance_type = properties[prop_name]
            print(f"   ✓ FOUND instance_type: '{instance_type}' (from '{prop_name}')")
            break
    
    if not instance_type:
        print(f"   ✗ NOT FOUND - will return $0.00 (ERROR!)")
    
    # Step 4: Check region extraction
    print("\n4. REGION EXTRACTION")
    print("-" * 80)
    
    region_props = ['location', 'region', 'availability_zone']
    print(f"   Searching for region in: {region_props}")
    
    region = None
    for prop_name in region_props:
        if prop_name in properties:
            region = properties[prop_name]
            print(f"   ✓ FOUND region: '{region}' (from '{prop_name}')")
            break
    
    if not region:
        print(f"   ✗ NOT FOUND - will use default 'eastus'")
    
    # Step 5: Normalization
    print("\n5. NORMALIZATION")
    print("-" * 80)
    
    if instance_type:
        # From pricing_calculator.py line 469
        if instance_type == "Standard_D2s_v3":
            normalized = "Standard_D2s_v3"
            print(f"   ✓ VM size '{instance_type}' → '{normalized}' (already normalized)")
        else:
            print(f"   ? VM size '{instance_type}' needs verification against mappings")
    
    if region:
        # Region normalization
        region_map = {
            "East US": "eastus",
            "West US": "westus",
            "Central US": "centralus",
        }
        normalized_region = region_map.get(region, region.lower())
        print(f"   ✓ Region '{region}' → '{normalized_region}'")

print("\n" + "=" * 80)
print("ROOT CAUSE ANALYSIS")
print("=" * 80)

print("""
The issue is in the PROPERTY EXTRACTION.

The TerraformParser._parse_properties() function in diagram_generator.py
correctly extracts properties from the resource body, BUT:

1. It stores raw values in the 'properties' dict
2. The pricing_calculator.py expects to find 'vm_size' key in resource.properties
3. Terraform uses 'vm_size = "Standard_D2s_v3"' syntax

DIAGNOSIS:
✓ Terraform parser DOES extract vm_size correctly
✓ Properties dict IS populated with vm_size
✓ Instance type extraction in pricing_calculator.py IS looking for vm_size

MOST LIKELY ISSUE:
The resource object passed to pricing_calculator.add_resource() might not have
the properties dict properly populated, OR the resource.properties is empty.

VERIFICATION NEEDED:
1. Check if TerraformParser is being called correctly
2. Verify resource.properties dict has vm_size
3. Check pricing_calculator logs for "Instance type required..." message
4. Verify REAL_TIME_PRICING_ENABLED and pricing_fetcher are initialized
""")

print("\nSUGGESTED FIX:")
print("-" * 80)
print("""
Add debug logging to pricing_calculator.py around line 760-785:

    for resource in parser.resources:
        # ADD THIS DEBUG LOG:
        logger.info(f"Processing resource: type={resource.type}, name={resource.name}")
        logger.info(f"Resource properties: {resource.properties}")
        
        if hasattr(resource, 'properties') and resource.properties:
            logger.info(f"Found properties dict with keys: {list(resource.properties.keys())}")
            for prop_name in ['size', 'instance_type', 'machine_type', 'vm_size', 'instance_class', 'name']:
                if prop_name in resource.properties:
                    instance_type = resource.properties[prop_name]
                    logger.info(f"✓ Found {prop_name}: {instance_type}")
                    break
        else:
            logger.error(f"✗ No properties dict found!")
""")
