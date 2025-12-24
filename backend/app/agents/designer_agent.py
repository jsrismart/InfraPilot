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
            # Detect OS type from prompt BEFORE calling Ollama
            prompt_lower = prompt.lower()
            os_type = "unknown"
            
            # More robust OS detection - check for explicit OS keywords
            linux_keywords = ["linux", "ubuntu", "centos", "rhel", "debian", "alma", "rocky"]
            windows_keywords = ["windows", "server 2019", "server 2016", "server 2022", "sql server"]
            
            # Count keyword occurrences
            linux_count = sum(1 for keyword in linux_keywords if keyword in prompt_lower)
            windows_count = sum(1 for keyword in windows_keywords if keyword in prompt_lower)
            
            if linux_count > windows_count:
                os_type = "linux"
            elif windows_count > linux_count:
                os_type = "windows"
            elif "linux" in prompt_lower:
                os_type = "linux"
            elif "windows" in prompt_lower:
                os_type = "windows"
            
            logger.info(f"🔍 Detected OS type from prompt: {os_type} (linux_count={linux_count}, windows_count={windows_count})")
            
            # Enhanced prompt with quantity parsing and OS detection
            system_msg = f"""You are an expert Terraform code generator for Azure infrastructure.

CRITICAL: User explicitly requested {os_type.upper()} infrastructure.

RULES FOR {os_type.upper()}:
"""
            
            if os_type == "linux":
                system_msg += """- MUST use azurerm_linux_virtual_machine (NEVER azurerm_windows_virtual_machine)
- Publisher: "Canonical"
- Offer: "UbuntuServer"
- SKU: "18.04-LTS"
- NO provision_vm_agent or enable_automatic_updates
"""
            elif os_type == "windows":
                system_msg += """- MUST use azurerm_windows_virtual_machine (NEVER azurerm_linux_virtual_machine)
- Publisher: "MicrosoftWindowsServer"
- Offer: "WindowsServer"
- SKU: "2019-Datacenter"
"""
            
            system_msg += """
REQUIREMENTS:
- Generate complete, valid Terraform HCL
- NO markdown backticks or code blocks
- Parse quantities: if "10 VMs", create 10 separate resources (vm_1, vm_2, etc)
- Include all configuration files: providers.tf, variables.tf, main.tf, outputs.tf
- Output MUST be valid and deployable"""
            
            full_prompt = f"{system_msg}\n\nUser request: {prompt}\n\nGenerate Terraform ({os_type.upper()}):"
            
            logger.info(f"Calling Ollama with OS={os_type}, prompt length: {len(full_prompt)}")
            
            # Call Ollama with streaming to reduce memory pressure
            terraform_code = ""
            response = ollama.generate(
                model=self.MODEL,
                prompt=full_prompt,
                stream=False,
                options={
                    "num_predict": 800,  # Reduced from 1500 for faster generation
                    "temperature": 0.2,  # Slightly higher for better coherence
                    "top_p": 0.95,  # Increased for better diversity
                    "top_k": 50,
                }
            )
            
            if response and "response" in response:
                terraform_code = response["response"].strip()
                if terraform_code and len(terraform_code) > 50:  # Minimum viable response
                    logger.info(f"Generated {len(terraform_code)} chars of Terraform")
                    
                    # POST-PROCESSING: Fix OS type if Ollama generated wrong one
                    terraform_code = self._fix_os_type(terraform_code, os_type)
                    
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

    def _fix_os_type(self, terraform_code: str, os_type: str) -> str:
        """Post-process Terraform code to ensure correct OS type is used"""
        if not os_type or not terraform_code:
            return terraform_code
        
        os_type = os_type.lower()
        
        if os_type == "linux":
            # Convert Windows VMs to Linux
            terraform_code = terraform_code.replace(
                "azurerm_windows_virtual_machine",
                "azurerm_linux_virtual_machine"
            )
            
            # Fix publisher references from Windows to Linux distributions
            terraform_code = terraform_code.replace(
                'publisher = "MicrosoftWindowsServer"',
                'publisher = "Canonical"'
            )
            terraform_code = terraform_code.replace(
                'offer = "WindowsServer"',
                'offer = "UbuntuServer"'
            )
            terraform_code = terraform_code.replace(
                'sku = "2019-Datacenter"',
                'sku = "18.04-LTS"'
            )
            terraform_code = terraform_code.replace(
                'sku = "2016-Datacenter"',
                'sku = "18.04-LTS"'
            )
            
            # Remove Windows-specific configurations
            lines = terraform_code.split('\n')
            fixed_lines = []
            for line in lines:
                # Skip Windows-only config
                if any(skip in line.lower() for skip in ['enable_automatic_updates', 'provision_vm_agent']):
                    continue
                fixed_lines.append(line)
            terraform_code = '\n'.join(fixed_lines)
            
            logger.info(f"Fixed OS type to Linux")
        
        elif os_type == "windows":
            # Convert Linux VMs to Windows
            terraform_code = terraform_code.replace(
                "azurerm_linux_virtual_machine",
                "azurerm_windows_virtual_machine"
            )
            
            # Fix publisher references from Linux to Windows
            terraform_code = terraform_code.replace(
                'publisher = "Canonical"',
                'publisher = "MicrosoftWindowsServer"'
            )
            terraform_code = terraform_code.replace(
                'offer = "UbuntuServer"',
                'offer = "WindowsServer"'
            )
            terraform_code = terraform_code.replace(
                'sku = "18.04-LTS"',
                'sku = "2019-Datacenter"'
            )
            
            logger.info(f"Fixed OS type to Windows")
        
        return terraform_code

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
