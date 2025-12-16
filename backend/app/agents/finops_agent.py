import subprocess
import tempfile
import shutil
import os
import json
from app.utils.logger import logger

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
        """Generate estimated costs based on resource detection"""
        # Parse resources from Terraform code
        content = "\n".join(iac_files.values())
        
        # Estimate costs based on detected resources
        estimated = {
            "summary": {
                "total_monthly_cost": "estimated",
                "resources_analyzed": len(iac_files),
                "note": "Estimated costs - Install infracost for accurate pricing"
            },
            "resources": []
        }
        
        # Detect and estimate common resources
        if "azurerm_windows_virtual_machine" in content or "azurerm_linux_virtual_machine" in content:
            estimated["resources"].append({
                "name": "Azure VM",
                "type": "Compute",
                "estimated_monthly_cost": "$30-200",
                "depends_on": "VM size and usage hours"
            })
        
        if "azurerm_network_interface" in content:
            estimated["resources"].append({
                "name": "Network Interface",
                "type": "Networking",
                "estimated_monthly_cost": "$0.40",
                "note": "Charged when VM is running"
            })
        
        if "azurerm_virtual_network" in content:
            estimated["resources"].append({
                "name": "Virtual Network",
                "type": "Networking",
                "estimated_monthly_cost": "$0",
                "note": "Free tier"
            })
        
        if "aws_instance" in content:
            estimated["resources"].append({
                "name": "EC2 Instance",
                "type": "Compute",
                "estimated_monthly_cost": "$20-150",
                "depends_on": "Instance type and usage hours"
            })
        
        logger.info(f"✓ Generated estimated costs for {len(estimated['resources'])} resources")
        return estimated

