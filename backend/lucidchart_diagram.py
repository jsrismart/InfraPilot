"""
Lucidchart-Style Architecture Diagram Generator

Generates professional architecture diagrams compatible with Lucidchart:
1. Mermaid format (importable to Lucidchart)
2. CSV format (for Lucidchart data import)
3. Professional SVG with Azure icons from Icons folder
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


# Path to Icons folder
ICONS_PATH = Path(__file__).parent.parent / "Icons"


@dataclass
class ResourceNode:
    """Represents a resource in the architecture diagram"""
    id: str
    resource_type: str
    name: str
    display_name: str
    category: str
    icon_path: Optional[str] = None
    properties: Dict = field(default_factory=dict)
    x: float = 0
    y: float = 0
    width: float = 160
    height: float = 80


# Icon mappings to Icons folder
ICON_MAPPINGS = {
    # General
    'resource_group': 'general/10007-icon-service-Resource-Groups.svg',
    'subscription': 'general/10002-icon-service-Subscriptions.svg',
    
    # Compute
    'virtual_machine': 'compute/10021-icon-service-Virtual-Machine.svg',
    'vm': 'compute/10021-icon-service-Virtual-Machine.svg',
    'app_service': 'compute/10035-icon-service-App-Services.svg',
    'function_app': 'compute/10029-icon-service-Function-Apps.svg',
    'function': 'compute/10029-icon-service-Function-Apps.svg',
    'kubernetes': 'compute/10023-icon-service-Kubernetes-Services.svg',
    'aks': 'compute/10023-icon-service-Kubernetes-Services.svg',
    'container': 'compute/10104-icon-service-Container-Instances.svg',
    'batch': 'compute/10031-icon-service-Batch-Accounts.svg',
    'vmss': 'compute/10034-icon-service-VM-Scale-Sets.svg',
    'disk': 'compute/10032-icon-service-Disks.svg',
    
    # Networking
    'virtual_network': 'networking/10061-icon-service-Virtual-Networks.svg',
    'vnet': 'networking/10061-icon-service-Virtual-Networks.svg',
    'subnet': 'networking/02742-icon-service-Subnet.svg',
    'network_security_group': 'networking/10067-icon-service-Network-Security-Groups.svg',
    'nsg': 'networking/10067-icon-service-Network-Security-Groups.svg',
    'public_ip': 'networking/10069-icon-service-Public-IP-Addresses.svg',
    'load_balancer': 'networking/10062-icon-service-Load-Balancers.svg',
    'application_gateway': 'networking/10076-icon-service-Application-Gateways.svg',
    'firewall': 'networking/10084-icon-service-Firewalls.svg',
    'dns': 'networking/10064-icon-service-DNS-Zones.svg',
    'bastion': 'networking/02422-icon-service-Bastions.svg',
    'nat': 'networking/10310-icon-service-NAT.svg',
    'vpn': 'networking/10063-icon-service-Virtual-Network-Gateways.svg',
    'network_interface': 'networking/10080-icon-service-Network-Interfaces.svg',
    'route_table': 'networking/10082-icon-service-Route-Tables.svg',
    
    # Storage
    'storage_account': 'storage/10086-icon-service-Storage-Accounts.svg',
    'storage': 'storage/10086-icon-service-Storage-Accounts.svg',
    'blob': 'storage/10086-icon-service-Storage-Accounts.svg',
    'file_share': 'storage/10400-icon-service-Azure-Fileshares.svg',
    'data_lake': 'storage/10090-icon-service-Data-Lake-Storage-Gen1.svg',
    'backup': 'storage/00017-icon-service-Recovery-Services-Vaults.svg',
    
    # Databases
    'sql_server': 'databases/10132-icon-service-SQL-Server.svg',
    'sql_database': 'databases/10130-icon-service-SQL-Database.svg',
    'sql': 'databases/10130-icon-service-SQL-Database.svg',
    'cosmosdb': 'databases/10121-icon-service-Azure-Cosmos-DB.svg',
    'cosmos': 'databases/10121-icon-service-Azure-Cosmos-DB.svg',
    'mysql': 'databases/10122-icon-service-Azure-Database-MySQL-Server.svg',
    'postgresql': 'databases/10131-icon-service-Azure-Database-PostgreSQL-Server.svg',
    'redis': 'databases/10137-icon-service-Cache-Redis.svg',
    'cache': 'databases/10137-icon-service-Cache-Redis.svg',
    
    # Security
    'key_vault': 'security/10245-icon-service-Key-Vaults.svg',
    'keyvault': 'security/10245-icon-service-Key-Vaults.svg',
    
    # Monitoring
    'monitor': 'management + governance/00001-icon-service-Monitor.svg',
    'log_analytics': 'management + governance/00009-icon-service-Log-Analytics-Workspaces.svg',
    'application_insights': 'management + governance/00012-icon-service-Application-Insights.svg',
}

# Category colors (Lucidchart style)
CATEGORY_STYLES = {
    'compute': {'bg': '#E3F2FD', 'border': '#1565C0', 'icon_bg': '#BBDEFB'},
    'networking': {'bg': '#E8F5E9', 'border': '#2E7D32', 'icon_bg': '#C8E6C9'},
    'storage': {'bg': '#FFF3E0', 'border': '#E65100', 'icon_bg': '#FFE0B2'},
    'database': {'bg': '#F3E5F5', 'border': '#6A1B9A', 'icon_bg': '#E1BEE7'},
    'security': {'bg': '#FFEBEE', 'border': '#C62828', 'icon_bg': '#FFCDD2'},
    'management': {'bg': '#F5F5F5', 'border': '#424242', 'icon_bg': '#E0E0E0'},
    'identity': {'bg': '#FFF8E1', 'border': '#F57F17', 'icon_bg': '#FFECB3'},
    'integration': {'bg': '#E0F7FA', 'border': '#00838F', 'icon_bg': '#B2EBF2'},
}


def get_category(resource_type: str) -> str:
    """Determine category from resource type."""
    rt = resource_type.lower()
    
    if any(k in rt for k in ['virtual_machine', 'vm', 'app_service', 'function', 'container', 'kubernetes', 'aks', 'batch', 'vmss']):
        return 'compute'
    elif any(k in rt for k in ['virtual_network', 'vnet', 'subnet', 'nsg', 'network', 'firewall', 'gateway', 'ip', 'dns', 'load_balancer', 'bastion']):
        return 'networking'
    elif any(k in rt for k in ['storage', 'blob', 'disk', 'file', 'data_lake', 'backup']):
        return 'storage'
    elif any(k in rt for k in ['sql', 'database', 'cosmos', 'mysql', 'postgresql', 'redis', 'cache']):
        return 'database'
    elif any(k in rt for k in ['key_vault', 'security', 'defender']):
        return 'security'
    elif any(k in rt for k in ['resource_group', 'subscription', 'policy', 'blueprint']):
        return 'management'
    elif any(k in rt for k in ['active_directory', 'identity', 'b2c']):
        return 'identity'
    elif any(k in rt for k in ['service_bus', 'event', 'logic_app', 'api_management']):
        return 'integration'
    
    return 'compute'


def get_display_name(resource_type: str) -> str:
    """Get a human-readable display name."""
    # Remove provider prefix
    name = resource_type
    for prefix in ['azurerm_', 'aws_', 'google_']:
        name = name.replace(prefix, '')
    
    # Convert to title case
    return name.replace('_', ' ').title()


def get_icon_path(resource_type: str) -> Optional[str]:
    """Get the icon file path for a resource type."""
    rt = resource_type.lower()
    
    for keyword, path in ICON_MAPPINGS.items():
        if keyword in rt:
            full_path = ICONS_PATH / path
            if full_path.exists():
                return str(full_path)
    
    return None


def load_icon_svg(icon_path: str, size: int = 48) -> str:
    """Load and resize an SVG icon."""
    if not icon_path or not os.path.exists(icon_path):
        return get_default_icon(size)
    
    try:
        with open(icon_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        
        # Remove width/height and add new size
        svg_content = re.sub(r'width="[^"]*"', '', svg_content)
        svg_content = re.sub(r'height="[^"]*"', '', svg_content)
        svg_content = svg_content.replace('<svg', f'<svg width="{size}" height="{size}"', 1)
        
        return svg_content
    except Exception:
        return get_default_icon(size)


def get_default_icon(size: int = 48) -> str:
    """Return a default cloud icon."""
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path fill="#0078D4" d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z"/>
</svg>'''


class LucidchartDiagramGenerator:
    """Generate Lucidchart-compatible architecture diagrams."""
    
    def __init__(self, terraform_code: str):
        self.terraform_code = terraform_code
        self.nodes: List[ResourceNode] = []
        self.connections: List[Tuple[str, str, str]] = []
        self._parse_resources()
    
    def _parse_resources(self):
        """Parse Terraform code to extract resources."""
        # Pattern to match resource blocks
        pattern = re.compile(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{', re.IGNORECASE)
        
        for match in pattern.finditer(self.terraform_code):
            resource_type, resource_name = match.groups()
            
            # Extract properties
            start = match.end()
            brace_count = 1
            i = start
            while i < len(self.terraform_code) and brace_count > 0:
                if self.terraform_code[i] == '{':
                    brace_count += 1
                elif self.terraform_code[i] == '}':
                    brace_count -= 1
                i += 1
            
            body = self.terraform_code[start:i-1]
            properties = self._parse_properties(body)
            
            category = get_category(resource_type)
            display_name = get_display_name(resource_type)
            icon_path = get_icon_path(resource_type)
            
            node = ResourceNode(
                id=f"{resource_type}_{resource_name}".replace('.', '_'),
                resource_type=resource_type,
                name=resource_name,
                display_name=display_name,
                category=category,
                icon_path=icon_path,
                properties=properties
            )
            self.nodes.append(node)
        
        self._detect_connections()
    
    def _parse_properties(self, body: str) -> Dict[str, str]:
        """Parse properties from resource body."""
        properties = {}
        # Simple key = value pattern
        pattern = re.compile(r'(\w+)\s*=\s*([^\n]+)')
        for match in pattern.finditer(body):
            key, value = match.groups()
            properties[key.strip()] = value.strip().strip('"')
        return properties
    
    def _detect_connections(self):
        """Detect connections between resources."""
        for node in self.nodes:
            for prop_name, prop_value in node.properties.items():
                if isinstance(prop_value, str):
                    for other_node in self.nodes:
                        if other_node.id != node.id and other_node.name in prop_value:
                            self.connections.append((node.id, other_node.id, prop_name))
    
    def get_provider(self) -> str:
        """Detect the cloud provider."""
        code_lower = self.terraform_code.lower()
        if 'azurerm' in code_lower:
            return 'Azure'
        elif 'aws' in code_lower:
            return 'AWS'
        elif 'google' in code_lower:
            return 'GCP'
        return 'Cloud'
    
    def generate_mermaid(self) -> str:
        """Generate Mermaid diagram (importable to Lucidchart)."""
        if not self.nodes:
            return "graph TB\n  A[No resources found]"
        
        lines = ["graph TB"]
        lines.append("  %% Azure Architecture Diagram")
        lines.append("  %% Import this into Lucidchart via: File > Import > Mermaid")
        lines.append("")
        
        # Group nodes by category
        categories: Dict[str, List[ResourceNode]] = {}
        for node in self.nodes:
            if node.category not in categories:
                categories[node.category] = []
            categories[node.category].append(node)
        
        # Create subgraphs for each category
        for cat_name, cat_nodes in categories.items():
            style = CATEGORY_STYLES.get(cat_name, CATEGORY_STYLES['compute'])
            lines.append(f"  subgraph {cat_name}[{cat_name.title()}]")
            lines.append(f"    style {cat_name} fill:{style['bg']},stroke:{style['border']},stroke-width:2px")
            for node in cat_nodes:
                safe_id = node.name.replace('-', '_').replace('.', '_')
                lines.append(f"    {safe_id}[{node.display_name}<br/>{node.name}]")
            lines.append("  end")
            lines.append("")
        
        # Add connections
        if self.connections:
            lines.append("  %% Connections")
            for from_id, to_id, label in self.connections:
                from_node = next((n for n in self.nodes if n.id == from_id), None)
                to_node = next((n for n in self.nodes if n.id == to_id), None)
                if from_node and to_node:
                    f = from_node.name.replace('-', '_').replace('.', '_')
                    t = to_node.name.replace('-', '_').replace('.', '_')
                    lines.append(f"  {f} --> {t}")
        
        return "\n".join(lines)
    
    def generate_csv(self) -> str:
        """Generate CSV for Lucidchart data import."""
        lines = ["Id,Name,Type,Category,Shape Library,Shape,Container"]
        
        for node in self.nodes:
            lines.append(f'"{node.id}","{node.name}","{node.resource_type}","{node.category}","Azure 2019","Azure Resource",""')
        
        return "\n".join(lines)
    
    def generate_svg(self, width: int = 1400, height: int = 900) -> str:
        """Generate professional SVG diagram with Azure icons."""
        if not self.nodes:
            return self._empty_svg(width, height)
        
        # Layout calculation
        margin = 60
        title_height = 80
        node_width = 180
        node_height = 90
        h_spacing = 40
        v_spacing = 30
        group_padding = 25
        
        # Group by category
        categories: Dict[str, List[ResourceNode]] = {}
        for node in self.nodes:
            if node.category not in categories:
                categories[node.category] = []
            categories[node.category].append(node)
        
        # Sort categories
        cat_order = ['management', 'networking', 'compute', 'storage', 'database', 'security', 'identity', 'integration']
        sorted_cats = sorted(categories.keys(), key=lambda x: cat_order.index(x) if x in cat_order else 99)
        
        # Calculate positions - horizontal layout
        current_x = margin
        group_info = {}
        
        for cat in sorted_cats:
            cat_nodes = categories[cat]
            style = CATEGORY_STYLES.get(cat, CATEGORY_STYLES['compute'])
            
            # Stack nodes vertically within each category
            num_nodes = len(cat_nodes)
            group_width = node_width + group_padding * 2
            group_height = num_nodes * node_height + (num_nodes - 1) * v_spacing + group_padding * 2 + 35
            
            group_info[cat] = {
                'x': current_x,
                'y': title_height + margin,
                'width': group_width,
                'height': group_height,
                'style': style,
                'label': cat.title()
            }
            
            # Position nodes
            for idx, node in enumerate(cat_nodes):
                node.x = current_x + group_padding
                node.y = title_height + margin + group_padding + 35 + idx * (node_height + v_spacing)
                node.width = node_width
                node.height = node_height
            
            current_x += group_width + h_spacing
        
        # Normalize heights
        if group_info:
            max_height = max(g['height'] for g in group_info.values())
            for g in group_info.values():
                g['height'] = max_height
        
        # Calculate final dimensions
        actual_width = max(width, current_x + margin)
        actual_height = max(height, title_height + margin + (max_height if group_info else 300) + margin)
        
        provider = self.get_provider()
        
        # Build SVG
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{actual_width}" height="{actual_height}" viewBox="0 0 {actual_width} {actual_height}" 
     xmlns="http://www.w3.org/2000/svg" style="font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;">
  
  <defs>
    <style>
      .title {{ font-size: 28px; font-weight: 600; fill: #1a1a1a; }}
      .subtitle {{ font-size: 14px; fill: #666666; }}
      .group-label {{ font-size: 14px; font-weight: 600; fill: #333333; }}
      .node-name {{ font-size: 12px; font-weight: 600; fill: #1a1a1a; }}
      .node-type {{ font-size: 10px; fill: #666666; }}
      .connection {{ stroke: #0078D4; stroke-width: 2; fill: none; opacity: 0.7; }}
    </style>
    
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#0078D4"/>
    </marker>
    
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#000" flood-opacity="0.1"/>
    </filter>
    
    <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#0078D4;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#00BCF2;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Background -->
  <rect width="{actual_width}" height="{actual_height}" fill="#FAFAFA"/>
  
  <!-- Header bar -->
  <rect width="{actual_width}" height="4" fill="url(#headerGrad)"/>
  
  <!-- Title -->
  <text x="{actual_width/2}" y="45" class="title" text-anchor="middle">
    {provider} Architecture Diagram
  </text>
  <text x="{actual_width/2}" y="70" class="subtitle" text-anchor="middle">
    {len(self.nodes)} Resources • Generated by InfraPilot
  </text>
'''
        
        # Draw category groups
        for cat, info in group_info.items():
            style = info['style']
            svg += f'''
  <!-- {info['label']} Group -->
  <g class="category-group">
    <rect x="{info['x']}" y="{info['y']}" width="{info['width']}" height="{info['height']}" 
          rx="12" fill="{style['bg']}" stroke="{style['border']}" stroke-width="2"/>
    <text x="{info['x'] + info['width']/2}" y="{info['y'] + 22}" class="group-label" text-anchor="middle">
      {info['label']}
    </text>
  </g>
'''
        
        # Draw connections
        svg += '\n  <!-- Connections -->\n'
        for from_id, to_id, label in self.connections:
            from_node = next((n for n in self.nodes if n.id == from_id), None)
            to_node = next((n for n in self.nodes if n.id == to_id), None)
            
            if from_node and to_node:
                fx = from_node.x + from_node.width
                fy = from_node.y + from_node.height / 2
                tx = to_node.x
                ty = to_node.y + to_node.height / 2
                
                mid_x = (fx + tx) / 2
                svg += f'  <path d="M{fx},{fy} C{mid_x},{fy} {mid_x},{ty} {tx},{ty}" class="connection" marker-end="url(#arrowhead)"/>\n'
        
        # Draw nodes
        svg += '\n  <!-- Resource Nodes -->\n'
        for node in self.nodes:
            svg += self._render_node(node)
        
        svg += '\n</svg>'
        return svg
    
    def _render_node(self, node: ResourceNode) -> str:
        """Render a resource node."""
        x, y, w, h = node.x, node.y, node.width, node.height
        style = CATEGORY_STYLES.get(node.category, CATEGORY_STYLES['compute'])
        
        # Load icon
        icon_svg = load_icon_svg(node.icon_path, 40)
        
        # Truncate long names
        display_name = node.display_name[:20] + ('...' if len(node.display_name) > 20 else '')
        resource_name = node.name[:22] + ('...' if len(node.name) > 22 else '')
        
        return f'''
  <g class="resource-node" data-id="{node.id}">
    <!-- Card -->
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" 
          fill="white" stroke="{style['border']}" stroke-width="1.5" filter="url(#shadow)"/>
    
    <!-- Top accent -->
    <rect x="{x}" y="{y}" width="{w}" height="4" rx="8" fill="{style['border']}"/>
    <rect x="{x}" y="{y+3}" width="{w}" height="5" fill="{style['border']}"/>
    <rect x="{x}" y="{y+4}" width="{w}" height="4" fill="white"/>
    
    <!-- Icon background -->
    <rect x="{x + 10}" y="{y + 18}" width="50" height="50" rx="6" fill="{style['icon_bg']}"/>
    
    <!-- Icon -->
    <g transform="translate({x + 15}, {y + 23})">
      {icon_svg}
    </g>
    
    <!-- Text -->
    <text x="{x + 70}" y="{y + 38}" class="node-name">{display_name}</text>
    <text x="{x + 70}" y="{y + 55}" class="node-type">{resource_name}</text>
  </g>
'''
    
    def _empty_svg(self, width: int, height: int) -> str:
        """Return an empty diagram placeholder."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{width}" height="{height}" fill="#FAFAFA"/>
  <text x="{width/2}" y="{height/2}" text-anchor="middle" font-family="Segoe UI" font-size="18" fill="#666">
    No resources found in Terraform code
  </text>
</svg>'''
    
    def generate_json(self) -> str:
        """Generate JSON representation for data export."""
        return json.dumps({
            'provider': self.get_provider(),
            'resources': [
                {
                    'id': n.id,
                    'type': n.resource_type,
                    'name': n.name,
                    'display_name': n.display_name,
                    'category': n.category,
                    'properties': n.properties
                }
                for n in self.nodes
            ],
            'connections': [
                {'from': f, 'to': t, 'label': l}
                for f, t, l in self.connections
            ]
        }, indent=2)


def generate_lucidchart_diagram(terraform_code: str, output_format: str = 'svg') -> str:
    """
    Generate a Lucidchart-compatible architecture diagram.
    
    Args:
        terraform_code: The Terraform code to parse
        output_format: 'svg', 'mermaid', 'csv', or 'json'
    
    Returns:
        Diagram content in the requested format
    """
    generator = LucidchartDiagramGenerator(terraform_code)
    
    if output_format == 'mermaid':
        return generator.generate_mermaid()
    elif output_format == 'csv':
        return generator.generate_csv()
    elif output_format == 'json':
        return generator.generate_json()
    else:
        return generator.generate_svg()
