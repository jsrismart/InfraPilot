"""
API routes for diagram generation
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from diagram_generator import TerraformParser, DiagramGenerator
from diagram_image_generator import AdvancedDiagramGenerator, generate_all_diagram_formats
from drawio_generator import generate_drawio_from_terraform
import json

router = APIRouter()

class DiagramRequest(BaseModel):
    """Request model for diagram generation"""
    terraform_code: str
    diagram_type: str = "ascii"  # ascii, mermaid, lucidchart, json, svg, png, html, drawio

class DiagramResponse(BaseModel):
    """Response model for diagram generation"""
    success: bool
    diagram_type: str
    content: str
    metadata: dict = {}

@router.post("/generate-diagram")
def generate_diagram(request: DiagramRequest) -> DiagramResponse:
    """
    Generate infrastructure diagram from Terraform code
    
    Supported diagram types:
    - ascii: ASCII art representation
    - mermaid: Mermaid diagram (can be rendered)
    - json: JSON structured representation
    - svg: SVG vector diagram
    - png: PNG image (base64 encoded)
    - html: Interactive HTML diagram
    """
    if not request.terraform_code or not request.terraform_code.strip():
        raise HTTPException(status_code=400, detail="Terraform code cannot be empty")
    
    if request.diagram_type not in ["ascii", "mermaid", "lucidchart", "json", "svg", "png", "html", "drawio"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid diagram_type. Must be one of: ascii, mermaid, lucidchart, json, svg, png, html, drawio"
        )
    
    try:
        # Parse Terraform code
        parser = TerraformParser(request.terraform_code)
        
        # Generate requested diagram type
        if request.diagram_type == "ascii":
            generator = DiagramGenerator(parser)
            content = generator.generate_ascii_diagram()
        elif request.diagram_type == "mermaid":
            generator = DiagramGenerator(parser)
            content = generator.generate_mermaid_diagram()
        elif request.diagram_type == "lucidchart":
            # Return professional architecture diagram in Mermaid format for Lucidchart
            # Lucidchart uses Mermaid's import feature for importing diagrams
            generator = DiagramGenerator(parser)
            content = generator.generate_mermaid_diagram()
        elif request.diagram_type == "json":
            generator = DiagramGenerator(parser)
            content = json.dumps(generator.generate_json_diagram(), indent=2)
        elif request.diagram_type == "svg":
            advanced_generator = AdvancedDiagramGenerator(parser)
            content = advanced_generator.generate_enhanced_svg_diagram()
        elif request.diagram_type == "png":
            advanced_generator = AdvancedDiagramGenerator(parser)
            png_base64 = advanced_generator.generate_png_diagram()
            if not png_base64:
                raise HTTPException(
                    status_code=500,
                    detail="PNG generation requires PIL library. Install with: pip install pillow"
                )
            content = png_base64
        elif request.diagram_type == "html":
            advanced_generator = AdvancedDiagramGenerator(parser)
            content = advanced_generator.generate_html_diagram()
        elif request.diagram_type == "drawio":
            content = generate_drawio_from_terraform(request.terraform_code)
        
        return DiagramResponse(
            success=True,
            diagram_type=request.diagram_type,
            content=content,
            metadata={
                "provider": parser.get_provider(),
                "resources_count": len(parser.resources),
                "resource_types": list(set(r.type for r in parser.resources))
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate diagram: {str(e)}"
        )

@router.get("/diagram-formats")
def get_supported_formats() -> dict:
    """Get list of supported diagram formats"""
    return {
        "formats": [
            {
                "type": "ascii",
                "description": "ASCII art infrastructure diagram",
                "best_for": "Terminal viewing, documentation",
                "example": "Tree structure with resource details"
            },
            {
                "type": "mermaid",
                "description": "Mermaid diagram",
                "best_for": "Visual representation, web rendering",
                "example": "Can be rendered in markdown, GitLab, GitHub"
            },
            {
                "type": "lucidchart",
                "description": "Lucidchart-compatible Mermaid diagram",
                "best_for": "Import into Lucidchart, simplified format",
                "example": "Copy-paste into Lucidchart for professional diagrams"
            },
            {
                "type": "json",
                "description": "JSON structured data",
                "best_for": "Programmatic access, custom rendering",
                "example": "Machine-readable resource definitions"
            },
            {
                "type": "svg",
                "description": "SVG vector diagram",
                "best_for": "Web display, printing, scalable graphics",
                "example": "Interactive diagrams with tooltips"
            },
            {
                "type": "png",
                "description": "PNG raster image",
                "best_for": "Email sharing, presentations, quick viewing",
                "example": "Base64 encoded image data"
            },
            {
                "type": "html",
                "description": "Interactive HTML diagram",
                "best_for": "Detailed exploration, sharing with team",
                "example": "Canvas-based interactive diagram with hover and click features"
            },
            {
                "type": "drawio",
                "description": "Draw.io (diagrams.net) XML format",
                "best_for": "Import into draw.io or diagrams.net, professional diagrams",
                "example": "XML format compatible with draw.io editor"
            }
        ]
    }

@router.post("/generate-all-diagrams")
def generate_all_diagrams(request: DiagramRequest) -> dict:
    """Generate all diagram formats at once"""
    if not request.terraform_code or not request.terraform_code.strip():
        raise HTTPException(status_code=400, detail="Terraform code cannot be empty")
    
    try:
        all_diagrams = generate_all_diagram_formats(request.terraform_code)
        return {
            "success": True,
            "data": all_diagrams
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate diagrams: {str(e)}"
        )

@router.post("/preview-html")
def preview_html_diagram(request: DiagramRequest) -> HTMLResponse:
    """Get interactive HTML diagram for preview in iframe"""
    if not request.terraform_code or not request.terraform_code.strip():
        raise HTTPException(status_code=400, detail="Terraform code cannot be empty")
    
    try:
        parser = TerraformParser(request.terraform_code)
        advanced_generator = AdvancedDiagramGenerator(parser)
        html_content = advanced_generator.generate_html_diagram()
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate HTML preview: {str(e)}"
        )
