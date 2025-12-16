from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from app.api.v1.types import PromptRequest
from app.services.pipeline import run_pipeline
from app.utils.logger import logger
import asyncio
from concurrent.futures import TimeoutError

router = APIRouter()

@router.post("/generate-iac")
def generate_iac(data: PromptRequest, fast: bool = Query(False)):
    """
    Generate Infrastructure as Code from a natural language prompt.
    
    Args:
        data: PromptRequest with the infrastructure description
        fast: If true, skip Terraform, Checkov, and Infracost for faster response
    
    Returns:
        Dictionary with iac, plan, security, and finops results
    """
    # Validate input
    if not data.prompt or not data.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    if len(data.prompt) > 5000:
        raise HTTPException(status_code=400, detail="Prompt exceeds maximum length of 5000 characters")
    
    try:
        logger.info(f"Processing request - Fast mode: {fast}, Prompt length: {len(data.prompt)}")
        result = run_pipeline(data.prompt, skip_tools=fast)
        logger.info("Request completed successfully")
        return result
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except TimeoutError as e:
        logger.error(f"Request timeout: {str(e)}")
        raise HTTPException(status_code=504, detail="Request took too long. Try using Fast Mode (?fast=true)")
    
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
