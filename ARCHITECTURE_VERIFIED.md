# InfraPilot Architecture Verification

## Architecture Overview

The InfraPilot system now implements a clean, validated architecture:

```
User Prompt
    ↓
[OLLAMA] → Generates Terraform Code
    ↓
[Terraform Code] → Extracted Resources
    ↓
[Pricing Calculator] → Calculates Cost from Terraform Resources
    ↓
Cost Report (from actual cloud pricing APIs)
```

## Key Components

### 1. Terraform Generation: OLLAMA ONLY
**File:** `backend/app/agents/designer_agent.py`

**Implementation:**
- Uses Ollama qwen2.5-coder model exclusively
- No fallback to prompt parsing (disabled)
- Takes user natural language prompt as input
- Returns structured Terraform code (providers.tf, variables.tf, outputs.tf, main.tf)

**System Prompt Enforces:**
- NO hardcoded defaults
- Only resources explicitly mentioned in prompt
- Exact sizes/regions from user input
- Valid, syntactically correct Terraform
- No extra/unused resources

**Code Flow:**
```python
def generate(self, prompt: str) -> dict:
    # Calls Ollama only - NO fallback
    terraform_code = self._generate_with_ollama(prompt)
    return self.split_terraform_files(terraform_code)
```

### 2. Pricing Calculation: FROM TERRAFORM CODE ONLY
**File:** `backend/app/agents/finops_agent.py`

**Implementation:**
- Extracts all resources from generated Terraform code
- Calculates pricing for each extracted resource
- Uses live cloud pricing APIs:
  - Azure: Azure Retail Prices API
  - AWS: AWS Pricing API
  - GCP: Google Cloud Billing API
- Shows actual cost or error (no generic estimates)

**Resource Extraction:**
- Parses Terraform code using regex to find:
  - `azurerm_windows_virtual_machine` → Azure VM pricing
  - `azurerm_linux_virtual_machine` → Azure VM pricing
  - `aws_instance` → EC2 pricing
  - `google_compute_instance` → GCP Compute pricing
  - `azurerm_network_interface` → Network interface pricing

**Cost Calculation:**
```python
for resource in extracted_resources:
    cost = calculator.calculate_resource_cost(
        provider='azure',
        resource_type='Virtual Machine',
        instance_type='Standard_E4s_v3',
        region='eastus',
        quantity=2
    )
    # Returns actual cost from live API or error
```

## Data Flow Examples

### Example 1: Create 2 E-series VMs
**User Input:**
```
"Create 2 Standard_E4s_v3 VMs in East US with vnet and subnet"
```

**Ollama Output (Terraform Code):**
```hcl
resource "azurerm_windows_virtual_machine" "e_series_vm1" {
  vm_size = "Standard_E4s_v3"
  location = "eastus"
  ...
}

resource "azurerm_windows_virtual_machine" "e_series_vm2" {
  vm_size = "Standard_E4s_v3"
  location = "eastus"
  ...
}
```

**Pricing Calculation:**
1. Extract: 2 × Standard_E4s_v3 VMs in eastus
2. Query Azure Pricing API for Standard_E4s_v3 in eastus
3. Calculate: $X.XX per month per VM × 2 = Total Cost
4. Return actual cost (not estimate)

### Example 2: Multiple VM Series
**User Input:**
```
"Create 3 C-series and 2 E-series VMs"
```

**Terraform Generated:** 5 separate VM resources (3 C + 2 E)

**Pricing:** Calculated individually for each resource type:
- 3 × C-series VMs @ $Y.YY each
- 2 × E-series VMs @ $Z.ZZ each
- Total = 3Y.YY + 2Z.ZZ

## Guarantees

### ✅ NO Hardcoded Pricing
- Pricing dictionaries removed from `pricing_calculator.py`
- All pricing fetched from live APIs
- Comments show what was removed:
  ```python
  # AWS_PRICING, AZURE_PRICING, GCP_PRICING dictionaries removed
  # Now using real-time pricing from cloud provider APIs
  ```

### ✅ NO Generic Estimates
- No "$30-200" range estimates
- No "depends on" placeholder costs
- Only actual extracted resources are priced
- Unknown resources show $0.00 or error message

### ✅ OLLAMA ONLY for Terraform
- Prompt parsing fallback completely disabled
- Single source of truth: Ollama model
- System prompt ensures quality output
- User gets exactly what they ask for

### ✅ PRICING FROM TERRAFORM ONLY
- Pricing driven by actual resource extraction
- No additional resources added
- Cost reflects only what's in generated code
- Transparent calculation chain

## Configuration

### Ollama Settings
**File:** `backend/app/core/config.py`
```python
OLLAMA_MODEL = "qwen2.5-coder:latest"
OLLAMA_HOST = "http://localhost:11434"
```

### Pricing APIs
**File:** `backend/real_time_pricing_fetcher.py`
- Azure: https://prices.azure.com/api/retail/prices
- AWS: boto3 AWS Pricing API
- GCP: Google Cloud Billing API

## Testing

Run the architecture verification:
```bash
python test_architecture_verification.py
```

Expected output:
```
STEP 1: Terraform Generation (via Ollama)
OK: Ollama generated Terraform successfully

STEP 2: Pricing Calculation (from Terraform code only)
OK: Pricing calculated from Terraform code

STEP 3: Verification - NO Hardcoded/Generic Estimates
OK: No generic estimates found

ARCHITECTURE VERIFIED
- Terraform generation: Ollama ONLY
- Pricing calculation: From Terraform code ONLY
- No hardcoded pricing
- No generic estimates
```

## Summary

The InfraPilot system now provides a clean, validated architecture where:

1. **Terraform is generated by Ollama only** - User prompt → Ollama → Terraform code
2. **Pricing is calculated from Terraform only** - Extract resources → Query live APIs → Cost
3. **No hardcoded data** - All pricing from cloud provider APIs
4. **No generic estimates** - Real costs for real resources extracted from code

This ensures accuracy, transparency, and user control over infrastructure specification.
