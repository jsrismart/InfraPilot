from fastapi import APIRouter, HTTPException, Query
from app.api.v1.types import PromptRequest
from app.agents.designer_agent import DesignerAgent
from app.utils.logger import logger
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from pricing_calculator import calculate_terraform_pricing
import time

router = APIRouter()

@router.post("/generate-iac")
def generate_iac(data: PromptRequest, fast: bool = Query(False)):
    """
    Generate Infrastructure as Code ONLY via Ollama, then calculate pricing.
    
    This endpoint:
    1. Sends prompt ONLY to Ollama (DesignerAgent)
    2. Gets back Terraform code
    3. Calculates pricing from the Terraform code
    
    No other agents or processing involved.
    
    Args:
        data: PromptRequest with the infrastructure description
        fast: Not used (kept for API compatibility)
    
    Returns:
        Dictionary with iac (Terraform code) and pricing
    """
    # Validate input
    if not data.prompt or not data.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    if len(data.prompt) > 5000:
        raise HTTPException(status_code=400, detail="Prompt exceeds maximum length of 5000 characters")
    
    try:
        logger.info(f"🚀 Ollama-Only Pipeline: Generating Terraform from prompt")
        start_time = time.time()
        
        # STEP 1: Generate Terraform code ONLY via Ollama
        logger.info("Step 1/2: Generating Terraform via Ollama...")
        designer = DesignerAgent()
        terraform_result = designer.generate(data.prompt)
        
        # Extract the Terraform code
        iac_code = terraform_result.get("main.tf", "")
        
        if not iac_code or len(iac_code) < 10:
            logger.error("❌ Ollama generated invalid Terraform")
            raise ValueError("Failed to generate valid Terraform code from Ollama")
        
        logger.info(f"✅ Terraform generated ({len(iac_code)} chars)")
        
        # STEP 2: Calculate pricing from the generated Terraform
        logger.info("Step 2/2: Calculating pricing from Terraform...")
        pricing = calculate_terraform_pricing(iac_code)
        
        elapsed = time.time() - start_time
        logger.info(f"✅ Complete pipeline finished in {elapsed:.2f}s")
        
        return {
            "status": "success",
            "iac": iac_code,
            "terraform_files": terraform_result,
            "pricing": pricing,
            "generation_time_seconds": elapsed
        }
    
    except ValueError as e:
        logger.error(f"❌ Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
