import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.agents.designer_agent import DesignerAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.security_agent import SecurityAgent
from app.agents.finops_agent import FinOpsAgent

designer = DesignerAgent()
planner = PlannerAgent()
security = SecurityAgent()
finops = FinOpsAgent()

executor = ThreadPoolExecutor(max_workers=3)

def _run_planner(iac_files: dict):
    """Wrapper for planner to run in executor"""
    try:
        return planner.plan(iac_files)
    except Exception as e:
        return {"error": str(e)}

def _run_security(iac_files: dict):
    """Wrapper for security to run in executor"""
    try:
        return security.scan(iac_files)
    except Exception as e:
        return {"error": str(e)}

def _run_finops(iac_files: dict):
    """Wrapper for finops to run in executor"""
    try:
        return finops.analyze(iac_files)
    except Exception as e:
        return {"error": str(e)}

def run_pipeline(prompt: str, skip_tools: bool = False):
    """
    Run the full infrastructure pipeline.
    
    Args:
        prompt: User's infrastructure description
        skip_tools: If True, skip expensive tools (Terraform, Checkov, Infracost)
                   for faster feedback. Useful for quick IaC generation.
    
    Returns:
        Dictionary with iac, plan, security, finops results
    """
    # Stage 1: Generate IaC (required, blocking)
    iac_files = designer.generate(prompt)
    
    if not iac_files:
        raise ValueError("Failed to generate IaC files")
    
    result = {
        "iac": iac_files
    }
    
    # Stage 2-4: Run optional tools in parallel if not skipped
    if not skip_tools:
        # Run FinOps analysis in executor (safe, cost-focused)
        finops_future = executor.submit(_run_finops, iac_files)
        
        # Try to get results with short timeout to prevent blocking
        try:
            result["finops"] = finops_future.result(timeout=5)
        except Exception as e:
            result["finops"] = {"error": f"FinOps analysis failed: {str(e)}"}
    
    return result
