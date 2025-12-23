import ollama
import threading
from app.core.config import settings
from app.utils.logger import logger

class DesignerAgent:
    MODEL = settings.OLLAMA_MODEL
    OLLAMA_TIMEOUT = 5  # seconds - fast timeout, use fallback if slow

    SYSTEM_PROMPT = """
You are a senior cloud architect and Terraform expert.

CRITICAL INSTRUCTIONS:
1. Generate COMPLETE Terraform IaC based ONLY on what the user specifies in their prompt
2. DO NOT add any hardcoded or default resources
3. DO NOT include resources not explicitly mentioned in the prompt
4. Parse the prompt carefully for:
   - Cloud provider (AWS, Azure, GCP)
   - Resource types and specifications
   - Configurations (size, region, storage, databases, etc.)
   - Any other infrastructure components

5. Generate in this EXACT structure:
   - providers.tf: ONLY provider blocks needed
   - variables.tf: ONLY variable blocks for dynamic values
   - outputs.tf: ONLY output blocks for resources
   - main.tf: ONLY resource blocks specified

6. CRITICAL RULES:
   - NO markdown, code blocks, or comments (no ```, #)
   - NO hardcoded defaults - ONLY use values from prompt
   - NO extra/unused resources
   - Generate FUNCTIONAL, syntactically correct Terraform
   - Use exact sizes/regions from prompt: if "E series" → Standard_E4s_v3, if "Central US" → centralus
   - If prompt is vague on specs, ask for clarification in error message

7. If you cannot generate proper Terraform from the prompt, return error explaining what's needed.

EXAMPLE:
Prompt: "Create Azure VM with Standard_E4s_v3 in westus with vnet and subnet"
Response: ONLY provider block, variables (for names), resource_group, public_ip, vnet, subnet, nic, vm in main.tf
Use: location = "westus" and vm_size = "Standard_E4s_v3"
DO NOT add: storage accounts, SQL databases, or other unrequested resources
"""

    def generate(self, prompt: str) -> dict:
        """Generate Terraform IaC from prompt using Ollama only"""
        logger.info(f"🚀 Generating Terraform from prompt using Ollama: {prompt[:80]}...")
        
        try:
            # Generate using Ollama
            terraform_code = self._generate_with_ollama(prompt)
            
            if terraform_code:
                logger.info("✅ Terraform generated via Ollama")
                return self.split_terraform_files(terraform_code)
            else:
                logger.error("❌ Ollama returned empty response")
                raise ValueError("Ollama failed to generate Terraform")
                
        except Exception as e:
            logger.error(f"❌ Ollama generation failed: {str(e)}")
            raise ValueError(f"Terraform generation failed: {str(e)}")
    
    def _generate_with_ollama(self, prompt: str) -> str:
        """Call Ollama to generate Terraform code"""
        try:
            # Enhanced prompt with quantity parsing
            system_msg = """You are a Terraform expert. Generate ONLY valid Terraform HCL code.

CRITICAL:
1. Parse quantities: if user says "3 VMs", create 3 separate resource blocks
2. Each resource must have a unique name (e.g., vm_1, vm_2, vm_3)
3. NO markdown code blocks (no ``` markers)
4. ONLY valid HCL syntax
5. Generate complete configs for: providers, variables, main resources, outputs

When generating multiple resources:
- Use for_each or multiple resource blocks with unique names
- If user wants "3 D-series VMs", create 3 azurerm_windows_virtual_machine blocks with unique names"""
            
            full_prompt = f"{system_msg}\n\nUser request: {prompt}\n\nGenerate Terraform:"
            
            logger.info(f"Calling Ollama with prompt length: {len(full_prompt)}")
            
            # Call Ollama with streaming to reduce memory pressure
            terraform_code = ""
            response = ollama.generate(
                model=self.MODEL,
                prompt=full_prompt,
                stream=False,
                options={
                    "num_predict": 1500,
                    "temperature": 0.1,  # Lower temp for more deterministic output
                    "top_p": 0.9,
                    "top_k": 40,
                }
            )
            
            if response and "response" in response:
                terraform_code = response["response"].strip()
                if terraform_code and len(terraform_code) > 50:  # Minimum viable response
                    logger.info(f"Generated {len(terraform_code)} chars of Terraform")
                    return terraform_code
                else:
                    logger.warning(f"Response too short: {len(terraform_code)} chars")
                    return None
            else:
                logger.error(f"Invalid Ollama response format")
                return None
                
        except Exception as e:
            logger.error(f"Ollama generation error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def split_terraform_files(self, text: str) -> dict:
        """Parse Terraform code into separate files by block type"""
        # Clean markdown code blocks
        code = (
            text.replace("```hcl", "")
                .replace("```tf", "")
                .replace("```terraform", "")
                .replace("```", "")
                .strip()
        )

        files = {
            "providers.tf": "",
            "variables.tf": "",
            "outputs.tf": "",
            "main.tf": ""
        }

        current_block = None
        buffer = []
        brace_depth = 0

        for line in code.split("\n"):
            stripped = line.strip()

            # Detect new block type
            if stripped.startswith(("provider ", "variable ", "output ", "resource ")):
                # Save previous block
                if current_block and buffer:
                    files[current_block] += "\n".join(buffer) + "\n\n"
                
                # Determine new block type
                if stripped.startswith("provider "):
                    current_block = "providers.tf"
                elif stripped.startswith("variable "):
                    current_block = "variables.tf"
                elif stripped.startswith("output "):
                    current_block = "outputs.tf"
                elif stripped.startswith("resource "):
                    current_block = "main.tf"
                
                buffer = [line]
                brace_depth = 0
                
                # Count braces
                for ch in line:
                    if ch == '{':
                        brace_depth += 1
                    elif ch == '}':
                        brace_depth -= 1
                continue

            # Add line to current block
            if current_block and buffer:
                buffer.append(line)
                
                # Count braces
                for ch in line:
                    if ch == '{':
                        brace_depth += 1
                    elif ch == '}':
                        brace_depth -= 1
                
                # Block complete when braces balanced
                if brace_depth == 0 and buffer:
                    files[current_block] += "\n".join(buffer) + "\n\n"
                    current_block = None
                    buffer = []
                    brace_depth = 0

        # Save remaining block
        if current_block and buffer:
            files[current_block] += "\n".join(buffer) + "\n\n"

        # Return only non-empty files
        return {k: v.strip() for k, v in files.items() if v.strip()}

    def generate_from_prompt_parsing(self, prompt: str) -> dict:
        """Intelligent fallback: Parse prompt to generate Terraform dynamically"""
        logger.info(f"📝 Parsing prompt to generate Terraform: {prompt[:100]}")
        
        prompt_lower = prompt.lower()
        
        # Detect cloud provider
        provider = "azurerm"  # default to Azure
        if "aws" in prompt_lower:
            provider = "aws"
        elif "gcp" in prompt_lower:
            provider = "google"
        
        # Build provider block
        if provider == "azurerm":
            provider_code = 'provider "azurerm" {\n  features {}\n}'
        elif provider == "aws":
            provider_code = 'provider "aws" {\n  region = "us-east-1"\n}'
        else:
            provider_code = 'provider "google" {\n  project = var.project_id\n}'
        
        # Detect what resources are needed
        resources_needed = []
        
        # Check for VMs
        if any(keyword in prompt_lower for keyword in ["vm", "virtual machine", "instance"]):
            resources_needed.append("vm")
        
        # Check for networking
        if any(keyword in prompt_lower for keyword in ["vnet", "network", "vpc", "subnet"]):
            resources_needed.append("network")
        
        # Check for storage
        if any(keyword in prompt_lower for keyword in ["storage", "s3", "bucket"]):
            resources_needed.append("storage")
        
        # Check for database
        if any(keyword in prompt_lower for keyword in ["database", "sql", "db", "postgres", "mysql"]):
            resources_needed.append("database")
        
        # Check for load balancer
        if any(keyword in prompt_lower for keyword in ["load balance", "lb", "alb"]):
            resources_needed.append("loadbalancer")
        
        logger.info(f"Detected resources: {resources_needed}")
        
        # Generate Terraform based on detected resources
        terraform_code = self._build_terraform_for_resources(provider, resources_needed, prompt)
        
        return self.split_terraform_files(terraform_code)
    
    def _build_terraform_for_resources(self, provider: str, resources: list, prompt: str) -> str:
        """Build Terraform code for detected resources"""
        
        # Provider block
        if provider == "azurerm":
            code = 'provider "azurerm" {\n  features {}\n}\n\n'
        elif provider == "aws":
            code = 'provider "aws" {\n  region = "us-east-1"\n}\n\n'
        else:
            code = 'provider "google" {\n  project = var.project_id\n}\n\n'
        
        # Variables - NO default values for prompt-driven generation
        code += 'variable "project_name" {\n  type = string\n}\n\n'
        
        # Build resources based on what was requested
        if "vm" in resources:
            if provider == "azurerm":
                code += self._build_azure_vm(prompt)
            elif provider == "aws":
                code += self._build_aws_instance(prompt)
        
        if "network" in resources:
            if provider == "azurerm":
                code += self._build_azure_network(prompt)
            elif provider == "aws":
                code += self._build_aws_vpc(prompt)
        
        if "storage" in resources:
            if provider == "azurerm":
                code += self._build_azure_storage(prompt)
            elif provider == "aws":
                code += self._build_aws_s3(prompt)
        
        # Outputs
        code += '\noutput "deployment_id" {\n  value = var.project_name\n}\n'
        
        return code
    
    def _build_azure_vm(self, prompt: str) -> str:
        """Build Azure VM resources - supports multiple VMs per series"""
        import re
        prompt_lower = prompt.lower()
        
        # Extract quantity - look for patterns like "2 e series", "two c series", etc
        quantity_mapping = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
        }
        
        default_quantity = 1
        quantity = default_quantity
        
        # Try numeric pattern first (e.g., "2 e series")
        numeric_match = re.search(r'(\d+)\s+[a-z]\s+series', prompt_lower)
        if numeric_match:
            quantity = int(numeric_match.group(1))
        
        # Try word patterns (e.g., "two e series", "three d series")
        if quantity == default_quantity:  # Only if not found numerically
            for word, num in quantity_mapping.items():
                # Look for "word <series> vms/series/vm"
                pattern = rf'{word}\s+([a-z])\s+(series|vm|vms)'
                match = re.search(pattern, prompt_lower)
                if match:
                    quantity = num
                    break
        
        # Detect ALL VM series mentioned in the prompt (not just first match)
        vm_series_list = []
        
        # E Series
        if "e series" in prompt_lower:
            if "e2" in prompt_lower:
                vm_series_list.append(("e_series", "Standard_E2s_v3", quantity))
            elif "e4" in prompt_lower:
                vm_series_list.append(("e_series", "Standard_E4s_v3", quantity))
            elif "e8" in prompt_lower:
                vm_series_list.append(("e_series", "Standard_E8s_v3", quantity))
            else:
                vm_series_list.append(("e_series", "Standard_E4s_v3", quantity))  # Default E series size
        
        # C Series
        if "c series" in prompt_lower:
            if "c2" in prompt_lower:
                vm_series_list.append(("c_series", "Standard_C2s_v3", quantity))
            elif "c4" in prompt_lower:
                vm_series_list.append(("c_series", "Standard_C4s_v3", quantity))
            elif "c8" in prompt_lower:
                vm_series_list.append(("c_series", "Standard_C8s_v3", quantity))
            else:
                vm_series_list.append(("c_series", "Standard_C4s_v3", quantity))  # Default C series size
        
        # D Series
        if "d series" in prompt_lower:
            if "d2" in prompt_lower:
                vm_series_list.append(("d_series", "Standard_D2s_v3", quantity))
            elif "d4" in prompt_lower:
                vm_series_list.append(("d_series", "Standard_D4s_v3", quantity))
            else:
                vm_series_list.append(("d_series", "Standard_D2s_v3", quantity))  # Default D series
        
        # A Series
        if "a series" in prompt_lower:
            if "a0" in prompt_lower:
                vm_series_list.append(("a_series", "Standard_A0", quantity))
            elif "a1" in prompt_lower:
                vm_series_list.append(("a_series", "Standard_A1", quantity))
            elif "a2" in prompt_lower:
                vm_series_list.append(("a_series", "Standard_A2", quantity))
            elif "a3" in prompt_lower:
                vm_series_list.append(("a_series", "Standard_A3", quantity))
            elif "a4" in prompt_lower:
                vm_series_list.append(("a_series", "Standard_A4", quantity))
            elif "a5" in prompt_lower:
                vm_series_list.append(("a_series", "Standard_A5", quantity))
            elif "a6" in prompt_lower:
                vm_series_list.append(("a_series", "Standard_A6", quantity))
            elif "a7" in prompt_lower:
                vm_series_list.append(("a_series", "Standard_A7", quantity))
            elif "a8" in prompt_lower:
                vm_series_list.append(("a_series", "Standard_A8", quantity))
            elif "a9" in prompt_lower:
                vm_series_list.append(("a_series", "Standard_A9", quantity))
            else:
                vm_series_list.append(("a_series", "Standard_A1", quantity))  # Default A series size
        
        # B Series
        if "b series" in prompt_lower:
            if "b2s" in prompt_lower:
                vm_series_list.append(("b_series", "Standard_B2s", quantity))
            elif "b4ms" in prompt_lower:
                vm_series_list.append(("b_series", "Standard_B4ms", quantity))
            else:
                vm_series_list.append(("b_series", "Standard_B1s", quantity))  # Default B series size
        
        # F Series
        if "f series" in prompt_lower:
            if "f1" in prompt_lower:
                vm_series_list.append(("f_series", "Standard_F1s", quantity))
            elif "f2" in prompt_lower:
                vm_series_list.append(("f_series", "Standard_F2s", quantity))
            else:
                vm_series_list.append(("f_series", "Standard_F1s", quantity))
        
        # G Series
        if "g series" in prompt_lower:
            if "g1" in prompt_lower:
                vm_series_list.append(("g_series", "Standard_G1", quantity))
            elif "g2" in prompt_lower:
                vm_series_list.append(("g_series", "Standard_G2", quantity))
            else:
                vm_series_list.append(("g_series", "Standard_G1", quantity))
        
        # Explicit size mentioned (Standard_E4s_v3, etc)
        if any(size in prompt_lower for size in ["standard_a", "standard_b", "standard_c", "standard_d", "standard_e", "standard_f", "standard_g"]):
            for size in ["Standard_A1", "Standard_B1s", "Standard_B2s", "Standard_C2s_v3", "Standard_C4s_v3", "Standard_C8s_v3", "Standard_D2s_v3", "Standard_D4s_v3", "Standard_E2s_v3", "Standard_E4s_v3", "Standard_F1s", "Standard_F2s"]:
                if size.lower() in prompt_lower:
                    found = False
                    for vm_series, vm_size_existing, _ in vm_series_list:
                        if size == vm_size_existing:
                            found = True
                            break
                    if not found:
                        vm_series_list.append((size.lower(), size, quantity))
        
        # If NO size detected in prompt, use default
        if not vm_series_list:
            logger.error(f"❌ VM size NOT found in prompt: {prompt}")
            vm_series_list = [("default_vm", "Standard_B1s", 1)]
        
        # Detect region - ONLY from prompt, NO DEFAULTS
        location = None
        region_mappings = {
            "south india": "southindia",
            "southindia": "southindia",
            "central us": "centralus",
            "centralus": "centralus",
            "west us": "westus",
            "westus": "westus",
            "east us": "eastus",
            "eastus": "eastus",
            "north europe": "northeurope",
            "northeurope": "northeurope",
            "west europe": "westeurope",
            "westeurope": "westeurope",
            "uk south": "uksouth",
            "uksouth": "uksouth",
            "southeast asia": "southeastasia",
            "southeastasia": "southeastasia",
            "east asia": "eastasia",
            "eastasia": "eastasia",
            "west asia": "westasia",
            "westasia": "westasia",
        }
        
        for region_name, region_code in region_mappings.items():
            if region_name in prompt_lower:
                location = region_code
                break
        
        # If NO region detected, use default
        if location is None:
            logger.error(f"❌ Region NOT found in prompt: {prompt}")
            location = "eastus"  # Fallback only, indicates user must specify
        
        # Generate infrastructure code with multiple VMs
        code = f'''resource "azurerm_resource_group" "main" {{
  name     = "${{var.project_name}}-rg"
  location = "{location}"
}}

resource "azurerm_virtual_network" "main" {{
  name                = "${{var.project_name}}-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}}

resource "azurerm_subnet" "internal" {{
  name                 = "${{var.project_name}}-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
}}

'''
        
        # Create NICs and VMs for each series and quantity
        global_vm_index = 1
        for series_name, vm_size, vm_quantity in vm_series_list:
            # Create vm_quantity number of VMs for this series
            for vm_num in range(1, vm_quantity + 1):
                # Create unique names for each VM
                unique_vm_name = f"{series_name}_vm{vm_num}"
                nic_name = f"{series_name}_nic{vm_num}"
                
                code += f'''resource "azurerm_network_interface" "{nic_name}" {{
  name                = "${{var.project_name}}-{series_name}-nic-{vm_num}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {{
    name                          = "testconfiguration{global_vm_index}"
    subnet_id                     = azurerm_subnet.internal.id
    private_ip_address_allocation = "Dynamic"
  }}
}}

resource "azurerm_windows_virtual_machine" "{unique_vm_name}" {{
  name                = "${{var.project_name}}-{series_name}-{vm_num}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  admin_username      = "adminuser"
  admin_password      = "P@ssw0rd1234!"

  network_interface_ids = [
    azurerm_network_interface.{nic_name}.id,
  ]

  os_disk {{
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }}

  source_image_reference {{
    publisher = "MicrosoftWindowsServer"
    offer     = "WindowsServer"
    sku       = "2019-Datacenter"
    version   = "latest"
  }}

  vm_size = "{vm_size}"
}}

'''
                global_vm_index += 1
        
        return code
    
    def _build_aws_instance(self, prompt: str) -> str:
        """Build AWS EC2 instance"""
        return '''resource "aws_instance" "main" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  tags = {
    Name = var.project_name
  }
}

'''
    
    def _build_azure_network(self, prompt: str) -> str:
        """Build Azure networking (included in VM setup)"""
        return ""
    
    def _build_aws_vpc(self, prompt: str) -> str:
        """Build AWS VPC"""
        return '''resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Name = var.project_name
  }
}

resource "aws_subnet" "main" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = var.project_name
  }
}

'''
    
    def _build_azure_storage(self, prompt: str) -> str:
        """Build Azure Storage Account"""
        return '''resource "azurerm_storage_account" "main" {
  name                     = "${replace(var.project_name, "-", "")}storage"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

'''
    
    def _build_aws_s3(self, prompt: str) -> str:
        """Build AWS S3 bucket"""
        return '''resource "aws_s3_bucket" "main" {
  bucket = var.project_name

  tags = {
    Name = var.project_name
  }
}

'''
