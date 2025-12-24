import subprocess
import tempfile
import shutil
import os
import json
import re
import sys
from app.utils.logger import logger

# Import pricing calculator from backend directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
try:
    from pricing_calculator import CloudPricingCalculator
except ImportError:
    CloudPricingCalculator = None
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from pricing_calculator import CloudPricingCalculator

class FinOpsAgent:
    def analyze(self, iac_files: dict):
        """Analyze cost using infracost with fallback to estimated pricing"""
        temp = tempfile.mkdtemp(prefix="infracost-")

        try:
            # write files
            for name, content in iac_files.items():
                with open(os.path.join(temp, name), "w") as f:
                    f.write(content)

            # try to run infracost
            cmd = [
                "infracost", "breakdown",
                "--path", temp,
                "--format", "json"
            ]

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout:
                    output = json.loads(result.stdout)
                    logger.info("✓ FinOps analysis completed via Infracost")
                    return output
                else:
                    logger.warning(f"⚠️ Infracost error: {result.stderr}")
                    return self._generate_estimated_costs(iac_files)
                    
            except (FileNotFoundError, subprocess.TimeoutExpired) as e:
                logger.warning(f"⚠️ Infracost not available, using estimated costs: {e}")
                return self._generate_estimated_costs(iac_files)

        except Exception as e:
            logger.error(f"❌ FinOps analysis failed: {str(e)}")
            return {"error": f"Cost analysis failed: {str(e)}"}
        finally:
            shutil.rmtree(temp, ignore_errors=True)

    def _generate_estimated_costs(self, iac_files: dict) -> dict:
        """Generate costs using live pricing APIs based on detected resources"""
        content = "\n".join(iac_files.values())
        
        # Initialize pricing calculator
        calculator = None
        if CloudPricingCalculator:
            try:
                calculator = CloudPricingCalculator()
            except Exception as e:
                logger.error(f"Failed to initialize pricing calculator: {e}")
        else:
            logger.warning("CloudPricingCalculator not available")
        
        # If calculator not available, use fallback
        if not calculator:
            return self._fallback_estimated_costs()
        
        # Parse and categorize resources
        azure_resources = self._extract_azure_resources(content)
        aws_resources = self._extract_aws_resources(content)
        gcp_resources = self._extract_gcp_resources(content)
        
        resources = []
        total_monthly = 0
        
        # Process Azure resources
        for resource in azure_resources:
            try:
                # Build resource dict for calculator
                calc_resource = {
                    'provider': 'azure',
                    'type': resource['type'],
                    'instance_type': resource['size'],
                    'region': resource['region'],
                    'quantity': resource['quantity']
                }
                
                cost, description = calculator.calculate_resource_cost(calc_resource)
                if cost and cost > 0:
                    resources.append({
                        "name": resource['name'],
                        "type": resource['type'],
                        "size": resource['size'],
                        "region": resource['region'],
                        "quantity": resource['quantity'],
                        "monthly_cost": f"${cost:.2f}",
                        "annual_cost": f"${cost * 12:.2f}",
                        "provider": "Azure",
                        "cost_description": description
                    })
                    total_monthly += cost
                else:
                    resources.append({
                        "name": resource['name'],
                        "type": resource['type'],
                        "size": resource['size'],
                        "region": resource['region'],
                        "quantity": resource['quantity'],
                        "monthly_cost": "$0.00",
                        "annual_cost": "$0.00",
                        "provider": "Azure",
                        "note": "Pricing not available"
                    })
            except Exception as e:
                logger.warning(f"Failed to calculate cost for {resource['name']}: {e}")
                resources.append({
                    "name": resource['name'],
                    "type": resource['type'],
                    "size": resource['size'],
                    "region": resource['region'],
                    "quantity": resource['quantity'],
                    "monthly_cost": "$0.00",
                    "annual_cost": "$0.00",
                    "provider": "Azure",
                    "note": f"Error: {str(e)}"
                })
        
        # Process AWS resources
        for resource in aws_resources:
            try:
                # Build resource dict for calculator
                calc_resource = {
                    'provider': 'aws',
                    'type': resource['type'],
                    'instance_type': resource['size'],
                    'region': resource['region'],
                    'quantity': resource['quantity']
                }
                
                cost, description = calculator.calculate_resource_cost(calc_resource)
                if cost and cost > 0:
                    resources.append({
                        "name": resource['name'],
                        "type": resource['type'],
                        "size": resource['size'],
                        "region": resource['region'],
                        "quantity": resource['quantity'],
                        "monthly_cost": f"${cost:.2f}",
                        "annual_cost": f"${cost * 12:.2f}",
                        "provider": "AWS",
                        "cost_description": description
                    })
                    total_monthly += cost
                else:
                    resources.append({
                        "name": resource['name'],
                        "type": resource['type'],
                        "size": resource['size'],
                        "region": resource['region'],
                        "quantity": resource['quantity'],
                        "monthly_cost": "$0.00",
                        "annual_cost": "$0.00",
                        "provider": "AWS",
                        "note": "Pricing not available"
                    })
            except Exception as e:
                logger.warning(f"Failed to calculate cost for {resource['name']}: {e}")
                resources.append({
                    "name": resource['name'],
                    "type": resource['type'],
                    "size": resource['size'],
                    "region": resource['region'],
                    "quantity": resource['quantity'],
                    "monthly_cost": "$0.00",
                    "annual_cost": "$0.00",
                    "provider": "AWS",
                    "note": f"Error: {str(e)}"
                })
        
        # Process GCP resources
        for resource in gcp_resources:
            try:
                # Build resource dict for calculator
                calc_resource = {
                    'provider': 'gcp',
                    'type': resource['type'],
                    'instance_type': resource['size'],
                    'region': resource['region'],
                    'quantity': resource['quantity']
                }
                
                cost, description = calculator.calculate_resource_cost(calc_resource)
                if cost and cost > 0:
                    resources.append({
                        "name": resource['name'],
                        "type": resource['type'],
                        "size": resource['size'],
                        "region": resource['region'],
                        "quantity": resource['quantity'],
                        "monthly_cost": f"${cost:.2f}",
                        "annual_cost": f"${cost * 12:.2f}",
                        "provider": "GCP",
                        "cost_description": description
                    })
                    total_monthly += cost
                else:
                    resources.append({
                        "name": resource['name'],
                        "type": resource['type'],
                        "size": resource['size'],
                        "region": resource['region'],
                        "quantity": resource['quantity'],
                        "monthly_cost": "$0.00",
                        "annual_cost": "$0.00",
                        "provider": "GCP",
                        "note": "Pricing not available"
                    })
            except Exception as e:
                logger.warning(f"Failed to calculate cost for {resource['name']}: {e}")
                resources.append({
                    "name": resource['name'],
                    "type": resource['type'],
                    "size": resource['size'],
                    "region": resource['region'],
                    "quantity": resource['quantity'],
                    "monthly_cost": "$0.00",
                    "annual_cost": "$0.00",
                    "provider": "GCP",
                    "note": f"Error: {str(e)}"
                })
                logger.warning(f"Failed to calculate cost for {resource['name']}: {e}")
                resources.append({
                    "name": resource['name'],
                    "type": resource['type'],
                    "size": resource['size'],
                    "region": resource['region'],
                    "quantity": resource['quantity'],
                    "monthly_cost": "$0.00",
                    "annual_cost": "$0.00",
                    "provider": "GCP",
                    "note": f"Error: {str(e)}"
                })
        
        # Add network interfaces
        if "azurerm_network_interface" in content:
            # Count network interfaces - typically one per VM
            nic_count = content.count("azurerm_network_interface")
            resources.append({
                "name": f"Network Interfaces ({nic_count})",
                "type": "Networking",
                "quantity": nic_count,
                "monthly_cost": f"${0.40 * nic_count:.2f}",
                "annual_cost": f"${0.40 * 12 * nic_count:.2f}",
                "provider": "Azure"
            })
            total_monthly += (0.40 * nic_count)
        
        return {
            "summary": {
                "total_monthly_cost": f"${total_monthly:.2f}",
                "total_annual_cost": f"${total_monthly * 12:.2f}",
                "resources_analyzed": len(resources),
                "calculation_method": "Live API pricing"
            },
            "resources": resources
        }
    
    def _fallback_estimated_costs(self) -> dict:
        """Fallback to simple estimates when pricing calculator unavailable"""
        return {
            "summary": {
                "total_monthly_cost": "estimated",
                "resources_analyzed": 0,
                "note": "Estimated costs - Pricing service unavailable"
            },
            "resources": []
        }
    
    def _extract_azure_resources(self, content: str) -> list:
        """Extract Azure resources from Terraform code"""
        resources = []
        
        # Find VMs
        vm_pattern = r'resource\s+"(azurerm_\w*virtual_machine)"\s+"([^"]+)"'
        vm_matches = re.finditer(vm_pattern, content)
        
        for match in vm_matches:
            resource_type = match.group(1)
            resource_name = match.group(2)
            
            # Try to find vm_size or image ID in the resource block
            # Look for vm_size = "..."
            size_match = re.search(rf'{resource_type}"\s+"{resource_name}"[^{{]*{{[^}}]*vm_size\s*=\s*"([^"]+)"', content)
            size = size_match.group(1) if size_match else "Standard_D2s_v3"
            
            # Try to find region/location
            region_match = re.search(rf'{resource_type}"\s+"{resource_name}"[^{{]*{{[^}}]*location\s*=\s*"([^"]+)"', content)
            region = region_match.group(1) if region_match else "eastus"
            
            resources.append({
                'name': resource_name,
                'type': 'azurerm_windows_virtual_machine',
                'size': size,
                'region': region,
                'quantity': 1
            })
        
        return resources
    
    def _extract_aws_resources(self, content: str) -> list:
        """Extract AWS resources from Terraform code"""
        resources = []
        
        # Find EC2 instances
        instance_pattern = r'resource\s+"aws_instance"\s+"([^"]+)"'
        instance_matches = re.finditer(instance_pattern, content)
        
        for match in instance_matches:
            resource_name = match.group(1)
            
            # Try to find instance_type
            type_match = re.search(rf'aws_instance"\s+"{resource_name}"[^{{]*{{[^}}]*instance_type\s*=\s*"([^"]+)"', content)
            instance_type = type_match.group(1) if type_match else "t2.micro"
            
            # Try to find region
            region_match = re.search(rf'aws_instance"\s+"{resource_name}"[^{{]*{{[^}}]*availability_zone\s*=\s*"([^"]+)"', content)
            region = region_match.group(1)[:-1] if region_match else "us-east-1"  # Remove AZ suffix
            
            resources.append({
                'name': resource_name,
                'type': 'EC2 Instance',
                'size': instance_type,
                'region': region,
                'quantity': 1
            })
        
        return resources
    
    def _extract_gcp_resources(self, content: str) -> list:
        """Extract GCP resources from Terraform code"""
        resources = []
        
        # Find GCP compute instances
        instance_pattern = r'resource\s+"google_compute_instance"\s+"([^"]+)"'
        instance_matches = re.finditer(instance_pattern, content)
        
        for match in instance_matches:
            resource_name = match.group(1)
            
            # Try to find machine_type
            type_match = re.search(rf'google_compute_instance"\s+"{resource_name}"[^{{]*{{[^}}]*machine_type\s*=\s*"([^"]+)"', content)
            machine_type = type_match.group(1) if type_match else "n1-standard-1"
            
            # Try to find zone
            zone_match = re.search(rf'google_compute_instance"\s+"{resource_name}"[^{{]*{{[^}}]*zone\s*=\s*"([^"]+)"', content)
            zone = zone_match.group(1) if zone_match else "us-central1-a"
            
            resources.append({
                'name': resource_name,
                'type': 'Compute Instance',
                'size': machine_type,
                'region': zone,
                'quantity': 1
            })
        
        return resources

