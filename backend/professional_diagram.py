"""
Professional Architecture Diagram Generator

Creates professional Azure-style architecture diagrams with official icons.
This is a wrapper that delegates to lucidchart_diagram.py.
"""

from lucidchart_diagram import LucidchartDiagramGenerator, generate_lucidchart_diagram


class ProfessionalArchitectureDiagram:
    """Professional architecture diagram wrapper."""
    
    def __init__(self, parser):
        """Initialize with a TerraformParser instance."""
        # Extract terraform code from parser
        self.terraform_code = ""
        if hasattr(parser, 'terraform_code'):
            self.terraform_code = parser.terraform_code
        elif hasattr(parser, 'resources'):
            # Reconstruct minimal terraform code from resources
            lines = []
            for r in parser.resources:
                props = " ".join([f'{k} = "{v}"' for k, v in (r.properties or {}).items()])
                lines.append(f'resource "{r.type}" "{r.name}" {{ {props} }}')
            self.terraform_code = "\n".join(lines)
        
        self._generator = LucidchartDiagramGenerator(self.terraform_code)
        self.nodes = self._generator.nodes
        self.connections = self._generator.connections
    
    def generate_svg(self) -> str:
        """Generate SVG diagram."""
        return self._generator.generate_svg()
    
    def generate_html(self) -> str:
        """Generate HTML diagram."""
        svg = self._generator.generate_svg()
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Architecture Diagram</title>
    <style>
        body {{ 
            margin: 0; 
            padding: 20px; 
            background: #f5f5f5; 
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        .diagram-container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
            overflow: auto;
        }}
    </style>
</head>
<body>
    <div class="diagram-container">
        {svg}
    </div>
</body>
</html>'''
    
    def generate_mermaid(self) -> str:
        """Generate Mermaid diagram."""
        return self._generator.generate_mermaid()


def generate_professional_diagram(terraform_code: str, output_format: str = 'svg') -> str:
    """
    Generate a professional architecture diagram.
    
    Args:
        terraform_code: The Terraform code to parse
        output_format: 'svg', 'html', or 'mermaid'
    
    Returns:
        Diagram content in the requested format
    """
    return generate_lucidchart_diagram(terraform_code, output_format)
