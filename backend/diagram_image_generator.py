"""
Infrastructure Diagram Image Generator
Generates professional visual diagrams as images (PNG/SVG)
"""

import json
import base64
import io
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from diagram_generator import TerraformParser, DiagramGenerator

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


@dataclass
class ResourceBox:
    """Represents a resource box in the diagram"""
    x: int
    y: int
    width: int
    height: int
    type: str
    name: str
    icon: str
    color: str


class AdvancedDiagramGenerator:
    """Generate professional visual diagrams as images"""
    
    # Color schemes for different providers
    PROVIDER_COLORS = {
        'aws': {'primary': '#FF9900', 'secondary': '#232F3E', 'background': '#F5F5F5'},
        'azure': {'primary': '#0078D4', 'secondary': '#106EBE', 'background': '#F5F5F5'},
        'gcp': {'primary': '#4285F4', 'secondary': '#1A73E8', 'background': '#F5F5F5'},
        'kubernetes': {'primary': '#326CE5', 'secondary': '#1D3A5D', 'background': '#F5F5F5'},
        'unknown': {'primary': '#4A90E2', 'secondary': '#2E5C8A', 'background': '#F5F5F5'},
    }
    
    # Resource type colors
    RESOURCE_COLORS = {
        'instance': '#4CAF50',        # Green
        'vpc': '#2196F3',              # Blue
        'subnet': '#03A9F4',           # Light Blue
        'security_group': '#F44336',   # Red
        'alb': '#FF9800',              # Orange
        'rds': '#9C27B0',              # Purple
        'bucket': '#FFC107',           # Amber
        'lambda': '#FF5722',           # Deep Orange
        'api_gateway': '#009688',      # Teal
        'dynamodb': '#00BCD4',         # Cyan
        'iam_role': '#673AB7',         # Deep Purple
        'route': '#CDDC39',            # Lime
        'nat_gateway': '#8BC34A',      # Light Green
        'load_balancer': '#FF9800',    # Orange
    }
    
    def __init__(self, parser: TerraformParser):
        self.parser = parser
        self.generator = DiagramGenerator(parser)
        self.provider = parser.get_provider()
        self.colors = self.PROVIDER_COLORS.get(self.provider, self.PROVIDER_COLORS['unknown'])
    
    def get_resource_color(self, resource_type: str) -> str:
        """Get color for resource type"""
        for key, color in self.RESOURCE_COLORS.items():
            if key in resource_type:
                return color
        return '#9E9E9E'  # Gray for unknown
    
    def generate_png_diagram(self) -> Optional[str]:
        """Generate PNG diagram and return as base64"""
        if not PIL_AVAILABLE:
            return None
        
        resources = self.parser.resources
        if not resources:
            return None
        
        # Layout calculation
        cols = max(3, (len(resources) + 2) // 3)
        rows = (len(resources) + cols - 1) // cols
        
        box_width = 200
        box_height = 150
        padding = 40
        margin = 20
        
        width = cols * (box_width + margin) + padding * 2
        height = rows * (box_height + margin) + padding * 3 + 60  # Extra space for title
        
        # Create image
        img = Image.new('RGB', (width, height), color=self.colors['background'])
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 20)
            text_font = ImageFont.truetype("arial.ttf", 10)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # Draw title
        title = f"{self.provider.upper()} Infrastructure Diagram"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        draw.text((title_x, 15), title, fill=self.colors['secondary'], font=title_font)
        
        # Draw resources
        for idx, resource in enumerate(resources):
            row = idx // cols
            col = idx % cols
            
            x = padding + col * (box_width + margin)
            y = padding + 60 + row * (box_height + margin)
            
            color = self.get_resource_color(resource.type)
            icon = self.generator.get_resource_icon(resource.type)
            
            # Draw box
            draw.rectangle(
                [(x, y), (x + box_width, y + box_height)],
                fill=color,
                outline=self.colors['secondary'],
                width=2
            )
            
            # Draw icon and text
            draw.text((x + 10, y + 10), icon, fill='white', font=text_font)
            
            # Draw resource type
            draw.text(
                (x + 10, y + 30),
                resource.type[:20],
                fill='white',
                font=text_font
            )
            
            # Draw resource name
            draw.text(
                (x + 10, y + 50),
                resource.name[:20],
                fill='white',
                font=text_font
            )
            
            # Draw resource count badge
            prop_count = len(resource.properties)
            badge_text = f"Props: {prop_count}"
            draw.text(
                (x + 10, y + 70),
                badge_text,
                fill='white',
                font=text_font
            )
        
        # Convert to base64 with proper error handling
        try:
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            png_data = buffer.getvalue()
            base64_image = base64.b64encode(png_data).decode('utf-8')
            return base64_image
        except Exception as e:
            print(f"Error encoding PNG to base64: {e}")
            return None
    
    def generate_enhanced_svg_diagram(self) -> str:
        """Generate enhanced SVG with professional styling"""
        resources = self.parser.resources
        if not resources:
            return '<svg></svg>'
        
        cols = max(3, (len(resources) + 2) // 3)
        rows = (len(resources) + cols - 1) // cols
        
        box_width = 200
        box_height = 150
        margin = 30
        padding = 40
        
        width = cols * (box_width + margin) + padding * 2
        height = rows * (box_height + margin) + padding * 3 + 60
        
        svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <style>
      .resource-box {{ stroke-width: 2; rx: 8; }}
      .resource-title {{ font-size: 14px; font-weight: bold; fill: white; }}
      .resource-name {{ font-size: 11px; fill: white; }}
      .resource-props {{ font-size: 9px; fill: white; opacity: 0.9; }}
      .diagram-title {{ font-size: 20px; font-weight: bold; fill: {self.colors['secondary']}; text-anchor: middle; }}
      .provider-label {{ font-size: 12px; fill: white; text-anchor: middle; }}
      .connection-line {{ stroke: {self.colors['secondary']}; stroke-width: 1.5; fill: none; }}
    </style>
    <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
      <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3"/>
    </filter>
  </defs>
  
  <!-- Background -->
  <rect width="{width}" height="{height}" fill="{self.colors['background']}"/>
  
  <!-- Title -->
  <text x="{width/2}" y="35" class="diagram-title">{self.provider.upper()} Infrastructure Diagram</text>
'''
        
        # Draw resources
        resource_positions = {}
        for idx, resource in enumerate(resources):
            row = idx // cols
            col = idx % cols
            
            x = padding + col * (box_width + margin)
            y = padding + 60 + row * (box_height + margin)
            
            resource_positions[f"{resource.type}:{resource.name}"] = (x + box_width/2, y + box_height/2)
            
            color = self.get_resource_color(resource.type)
            icon = self.generator.get_resource_icon(resource.type)
            
            svg += f'''  <!-- {resource.name} -->
  <g filter="url(#shadow)">
    <rect x="{x}" y="{y}" width="{box_width}" height="{box_height}" class="resource-box" fill="{color}" stroke="{self.colors['secondary']}"/>
    <text x="{x + 10}" y="{y + 25}" class="resource-title">{icon} {resource.type[:18]}</text>
    <text x="{x + 10}" y="{y + 45}" class="resource-name">{resource.name[:20]}</text>
    <text x="{x + 10}" y="{y + 65}" class="resource-props">ID: {resource.name[:12]}</text>
    <text x="{x + 10}" y="{y + 85}" class="resource-props">Props: {len(resource.properties)}</text>
  </g>
'''
        
        # Add connections
        connections = self._generate_svg_connections(resource_positions)
        svg += connections
        
        svg += '</svg>'
        return svg
    
    def _generate_svg_connections(self, positions: Dict[str, Tuple[float, float]]) -> str:
        """Generate SVG connection lines between related resources"""
        lines = ''
        
        relationships = [
            ('aws_instance', 'aws_security_group'),
            ('aws_subnet', 'aws_vpc'),
            ('aws_security_group', 'aws_vpc'),
            ('aws_db_instance', 'aws_security_group'),
            ('aws_alb', 'aws_security_group'),
        ]
        
        for source_type, target_type in relationships:
            source_nodes = [k for k in positions.keys() if k.startswith(source_type)]
            target_nodes = [k for k in positions.keys() if k.startswith(target_type)]
            
            for source in source_nodes:
                for target in target_nodes:
                    if source in positions and target in positions:
                        x1, y1 = positions[source]
                        x2, y2 = positions[target]
                        lines += f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="connection-line"/>\n'
        
        return lines
    
    def generate_interactive_json_diagram(self) -> Dict:
        """Generate enhanced JSON with visual positioning"""
        resources = self.parser.resources
        
        cols = max(3, (len(resources) + 2) // 3)
        rows = (len(resources) + cols - 1) // cols
        
        box_width = 200
        box_height = 150
        margin = 30
        padding = 40
        
        diagram_data = {
            "provider": self.provider,
            "title": f"{self.provider.upper()} Infrastructure Diagram",
            "layout": {
                "cols": cols,
                "rows": rows,
                "box_width": box_width,
                "box_height": box_height,
                "padding": padding,
                "margin": margin
            },
            "colors": {
                "provider": self.colors,
                "resources": {}
            },
            "resources": []
        }
        
        for idx, resource in enumerate(resources):
            row = idx // cols
            col = idx % cols
            
            x = padding + col * (box_width + margin)
            y = padding + 60 + row * (box_height + margin)
            
            color = self.get_resource_color(resource.type)
            icon = self.generator.get_resource_icon(resource.type)
            
            diagram_data["colors"]["resources"][resource.type] = color
            
            diagram_data["resources"].append({
                "id": f"{resource.type}:{resource.name}",
                "type": resource.type,
                "name": resource.name,
                "icon": icon,
                "color": color,
                "position": {
                    "x": x,
                    "y": y,
                    "width": box_width,
                    "height": box_height
                },
                "properties": resource.properties,
                "property_count": len(resource.properties)
            })
        
        return diagram_data
    
    def generate_html_diagram(self) -> str:
        """Generate interactive HTML diagram with Canvas rendering"""
        diagram_json = self.generate_interactive_json_diagram()
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{diagram_json['title']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            color: {self.colors['secondary']};
            margin-bottom: 5px;
        }}
        
        .header p {{
            color: #666;
            font-size: 14px;
        }}
        
        .diagram-wrapper {{
            background: {self.colors['background']};
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            overflow: auto;
        }}
        
        canvas {{
            display: block;
            margin: 0 auto;
            background: white;
            border-radius: 4px;
        }}
        
        .legend {{
            margin-top: 20px;
            padding: 15px;
            background: white;
            border-radius: 4px;
            font-size: 12px;
        }}
        
        .legend-item {{
            display: inline-block;
            margin-right: 20px;
            margin-bottom: 10px;
        }}
        
        .legend-color {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 3px;
            margin-right: 5px;
            vertical-align: middle;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ {diagram_json['title']}</h1>
            <p>Interactive Infrastructure Diagram • Total Resources: {len(diagram_json['resources'])}</p>
        </div>
        
        <div class="diagram-wrapper">
            <canvas id="diagramCanvas"></canvas>
            <div class="legend">
                <strong>Resource Types:</strong><br>
'''
        
        # Add legend
        for idx, resource in enumerate(diagram_json["resources"]):
            if idx < 5:  # Show first 5 in legend
                html += f'''                <div class="legend-item">
                    <span class="legend-color" style="background: {resource['color']};"></span>
                    <span>{resource['type']} {resource['icon']}</span>
                </div>
'''
        
        html += f'''            </div>
        </div>
    </div>
    
    <script>
        const diagramData = {json.dumps(diagram_json)};
        const canvas = document.getElementById('diagramCanvas');
        const ctx = canvas.getContext('2d');
        
        // Calculate canvas size
        const layout = diagramData.layout;
        const totalWidth = layout.cols * (layout.box_width + layout.margin) + layout.padding * 2;
        const totalHeight = layout.rows * (layout.box_height + layout.margin) + layout.padding * 3 + 60;
        
        canvas.width = totalWidth;
        canvas.height = totalHeight;
        
        // Fill background
        ctx.fillStyle = diagramData.colors.provider.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw title
        ctx.fillStyle = diagramData.colors.provider.secondary;
        ctx.font = 'bold 20px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(diagramData.title, totalWidth / 2, 35);
        
        // Draw resources
        diagramData.resources.forEach(resource => {{
            const pos = resource.position;
            const color = resource.color;
            
            // Draw box
            ctx.fillStyle = color;
            ctx.fillRect(pos.x, pos.y, pos.width, pos.height);
            
            // Draw border
            ctx.strokeStyle = diagramData.colors.provider.secondary;
            ctx.lineWidth = 2;
            ctx.strokeRect(pos.x, pos.y, pos.width, pos.height);
            
            // Draw text
            ctx.fillStyle = 'white';
            ctx.font = 'bold 12px Arial';
            ctx.textAlign = 'left';
            ctx.fillText(resource.icon + ' ' + resource.type.substring(0, 18), pos.x + 10, pos.y + 25);
            
            ctx.font = '11px Arial';
            ctx.fillText(resource.name.substring(0, 20), pos.x + 10, pos.y + 45);
            
            ctx.font = '9px Arial';
            ctx.fillText('ID: ' + resource.name.substring(0, 12), pos.x + 10, pos.y + 65);
            ctx.fillText('Props: ' + resource.property_count, pos.x + 10, pos.y + 85);
        }});
        
        // Add hover effect
        canvas.addEventListener('mousemove', (e) => {{
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            let hoverResource = null;
            diagramData.resources.forEach(resource => {{
                const pos = resource.position;
                if (x >= pos.x && x <= pos.x + pos.width &&
                    y >= pos.y && y <= pos.y + pos.height) {{
                    hoverResource = resource;
                }}
            }});
            
            canvas.style.cursor = hoverResource ? 'pointer' : 'default';
        }});
        
        // Click to show details
        canvas.addEventListener('click', (e) => {{
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            diagramData.resources.forEach(resource => {{
                const pos = resource.position;
                if (x >= pos.x && x <= pos.x + pos.width &&
                    y >= pos.y && y <= pos.y + pos.height) {{
                    console.log('Resource Details:', resource);
                    alert(JSON.stringify(resource, null, 2));
                }}
            }});
        }});
    </script>
</body>
</html>'''
        
        return html
    
    def generate_professional_architecture_diagram(self) -> str:
        """Generate professional infrastructure architecture diagram as SVG"""
        resources = self.parser.resources
        if not resources:
            return '<svg width="400" height="200"><text x="200" y="100" text-anchor="middle">No resources found</text></svg>'
        
        # Simple tier-based ASCII art representation
        tiers = {
            'Internet': ['internet_gateway', 'cloudfront', 'api_gateway', 'cdn'],
            'Web Tier': ['alb', 'nlb', 'load_balancer', 'elb', 'application_gateway'],
            'Compute': ['ec2', 'instance', 'lambda', 'ecs', 'eks', 'app_service', 'virtual_machine', 'function'],
            'Database': ['rds', 'dynamodb', 'sql_server', 'cosmosdb', 'cloud_sql', 'database'],
            'Storage': ['s3', 'bucket', 'storage_account', 'ebs', 'efs', 'cloud_storage'],
            'Network': ['vpc', 'virtual_network', 'subnet', 'security_group', 'network_interface', 'nat_gateway']
        }
        
        # Categorize resources
        tier_resources = {tier: [] for tier in tiers.keys()}
        for resource in resources:
            resource_lower = resource.type.lower()
            placed = False
            for tier, keywords in tiers.items():
                if any(kw in resource_lower for kw in keywords):
                    tier_resources[tier].append(resource)
                    placed = True
                    break
            if not placed:
                tier_resources['Network'].append(resource)
        
        # Build simple ASCII diagram as SVG text
        diagram_lines = []
        diagram_lines.append(f"{self.provider.upper()} Infrastructure Architecture")
        diagram_lines.append("=" * 60)
        
        y_offset = 0
        for tier_name in ['Internet', 'Web Tier', 'Compute', 'Database', 'Storage', 'Network']:
            tier_res = tier_resources.get(tier_name, [])
            if tier_res:
                diagram_lines.append("")
                diagram_lines.append(f"[{tier_name.upper()}]")
                for resource in tier_res:
                    res_short = resource.name[:20]
                    res_type = resource.type.replace('aws_', '').replace('azurerm_', '')[:15]
                    diagram_lines.append(f"  - {res_short} ({res_type})")
        
        # Create SVG with text
        svg_content = f'''<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <style>
    text {{ font-family: monospace; white-space: pre; }}
    .title {{ font-size: 18px; font-weight: bold; }}
    .tier {{ font-size: 14px; font-weight: bold; fill: #2196F3; }}
    .resource {{ font-size: 12px; fill: #333; }}
  </style>
  <rect width="800" height="600" fill="#f5f5f5" stroke="#999" stroke-width="1"/>'''
        
        y_pos = 20
        for line in diagram_lines:
            # Escape all special XML characters
            escaped_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
            if line.startswith(self.provider.upper()):
                svg_content += f'\n  <text x="20" y="{y_pos}" class="title">{escaped_line}</text>'
            elif line.startswith('['):
                svg_content += f'\n  <text x="20" y="{y_pos}" class="tier">{escaped_line}</text>'
            else:
                svg_content += f'\n  <text x="40" y="{y_pos}" class="resource">{escaped_line}</text>'
            y_pos += 18
        
        svg_content += '\n</svg>'
        return svg_content


def generate_all_diagram_formats(terraform_code: str) -> Dict:
    """Generate all diagram formats at once"""
    parser = TerraformParser(terraform_code)
    basic_generator = DiagramGenerator(parser)
    advanced_generator = AdvancedDiagramGenerator(parser)
    
    return {
        "ascii": basic_generator.generate_ascii_diagram(),
        "mermaid": basic_generator.generate_mermaid_diagram(),
        "json": basic_generator.generate_json_diagram(),
        "svg": advanced_generator.generate_enhanced_svg_diagram(),
        "png": advanced_generator.generate_png_diagram(),
        "html": advanced_generator.generate_html_diagram(),
        "interactive_json": advanced_generator.generate_interactive_json_diagram(),
        "metadata": {
            "provider": parser.get_provider(),
            "resources_count": len(parser.resources),
            "resource_types": list(set(r.type for r in parser.resources))
        }
    }
