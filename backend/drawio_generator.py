"""
Draw.io (diagrams.net) XML format generator for infrastructure diagrams
Converts Terraform infrastructure to draw.io XML format
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple
from app.utils.logger import logger

class DrawIOGenerator:
    """Generate draw.io XML diagrams from Terraform infrastructure"""
    
    # draw.io cell/shape styling
    SHAPES = {
        "azure_resource_group": {
            "icon": "mxgraph.azure.resource_group",
            "color": "0078D4",
            "label": "Resource Group"
        },
        "azurerm_virtual_network": {
            "icon": "mxgraph.azure.virtual_network",
            "color": "0078D4",
            "label": "Virtual Network"
        },
        "azurerm_subnet": {
            "icon": "mxgraph.azure.subnet",
            "color": "50E6FF",
            "label": "Subnet"
        },
        "azurerm_public_ip": {
            "icon": "mxgraph.azure.public_ip",
            "color": "FFB900",
            "label": "Public IP"
        },
        "azurerm_network_interface": {
            "icon": "mxgraph.azure.nic",
            "color": "00BCF2",
            "label": "Network Interface"
        },
        "azurerm_windows_virtual_machine": {
            "icon": "mxgraph.azure.virtual_machine",
            "color": "7FBA00",
            "label": "Windows VM"
        },
        "azurerm_linux_virtual_machine": {
            "icon": "mxgraph.azure.virtual_machine",
            "color": "7FBA00",
            "label": "Linux VM"
        },
        "azurerm_storage_account": {
            "icon": "mxgraph.azure.storage",
            "color": "0078D4",
            "label": "Storage Account"
        },
        "azurerm_sql_database": {
            "icon": "mxgraph.azure.sql_database",
            "color": "0078D4",
            "label": "SQL Database"
        },
        "azurerm_cosmosdb_account": {
            "icon": "mxgraph.azure.cosmosdb",
            "color": "0078D4",
            "label": "Cosmos DB"
        },
        "azurerm_app_service": {
            "icon": "mxgraph.azure.app_service",
            "color": "0078D4",
            "label": "App Service"
        },
        "azurerm_network_security_group": {
            "icon": "mxgraph.azure.network_security_group",
            "color": "FFB900",
            "label": "NSG"
        }
    }
    
    def __init__(self):
        """Initialize draw.io generator"""
        self.canvas_width = 1200
        self.canvas_height = 800
        self.cell_id = 0
        self.cells = []
        self.edges = []
        
    def _next_cell_id(self) -> str:
        """Generate next cell ID"""
        self.cell_id += 1
        return str(self.cell_id)
    
    def _parse_terraform_resources(self, terraform_code: str) -> Dict[str, List[Dict]]:
        """Parse Terraform code to extract resources"""
        resources = {}
        
        # Simple parser to extract resource types and names
        lines = terraform_code.split('\n')
        current_resource_type = None
        current_resource_name = None
        
        for line in lines:
            line = line.strip()
            
            # Match: resource "type" "name"
            if line.startswith('resource'):
                parts = line.replace('resource', '').replace('"', '').strip().split()
                if len(parts) >= 2:
                    current_resource_type = parts[0]
                    current_resource_name = parts[1]
                    
                    if current_resource_type not in resources:
                        resources[current_resource_type] = []
                    
                    resources[current_resource_type].append({
                        'name': current_resource_name,
                        'type': current_resource_type
                    })
        
        return resources
    
    def _add_cell(self, x: int, y: int, width: int, height: int, 
                  label: str, shape: str = "rectangle", color: str = "0078D4") -> str:
        """Add a cell/node to the diagram"""
        cell_id = self._next_cell_id()
        
        cell = {
            'id': cell_id,
            'value': label,
            'style': f'shape={shape};fillColor=#{color};fontColor=ffffff;strokeColor=000000;',
            'vertex': '1',
            'parent': '1',
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }
        
        self.cells.append(cell)
        return cell_id
    
    def _add_edge(self, source_id: str, target_id: str, label: str = "") -> str:
        """Add a connection/edge between cells"""
        edge_id = self._next_cell_id()
        
        edge = {
            'id': edge_id,
            'value': label,
            'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;',
            'edge': '1',
            'parent': '1',
            'source': source_id,
            'target': target_id
        }
        
        self.edges.append(edge)
        return edge_id
    
    def _build_azure_architecture(self, resources: Dict) -> None:
        """Build Azure architecture diagram with proper layout"""
        
        x_pos = 50
        y_pos = 50
        col_width = 250
        row_height = 150
        
        # Group resources by type for better layout
        resource_groups = {}
        col = 0
        
        for resource_type, items in resources.items():
            if col > 3:  # Reset column position
                col = 0
                y_pos += row_height * 2
            
            x = 50 + (col * col_width)
            y = y_pos
            
            # Get shape info
            shape_info = self.SHAPES.get(resource_type, {
                'icon': 'rectangle',
                'color': '0078D4',
                'label': resource_type.replace('azurerm_', '').replace('_', ' ').title()
            })
            
            # Add resource nodes
            for item in items:
                cell_id = self._add_cell(
                    x, y, 200, 80,
                    f"{item['name']}\n({shape_info['label']})",
                    shape="rectangle",
                    color=shape_info['color']
                )
                item['cell_id'] = cell_id
                y += row_height
            
            col += 1
    
    def generate_drawio_xml(self, terraform_code: str) -> str:
        """Generate draw.io XML from Terraform code"""
        try:
            logger.info("Generating draw.io XML from Terraform...")
            
            # Parse resources
            resources = self._parse_terraform_resources(terraform_code)
            
            if not resources:
                logger.warning("No resources found in Terraform code")
                return self._create_empty_drawio()
            
            # Build architecture
            self._build_azure_architecture(resources)
            
            # Create draw.io document
            drawio_xml = self._create_drawio_document()
            
            logger.info(f"✓ Generated draw.io XML with {len(self.cells)} cells")
            return drawio_xml
            
        except Exception as e:
            logger.error(f"Error generating draw.io XML: {str(e)}")
            return self._create_empty_drawio()
    
    def _create_drawio_document(self) -> str:
        """Create complete draw.io XML document"""
        
        # Create XML structure
        mxFile = ET.Element('mxfile')
        mxFile.set('host', 'InfraPilot')
        mxFile.set('modified', '2024-12-24T00:00:00.000Z')
        mxFile.set('agent', 'InfraPilot/1.0')
        mxFile.set('etag', 'auto')
        mxFile.set('version', '20.8.0')
        
        diagram = ET.SubElement(mxFile, 'diagram')
        diagram.set('id', '0')
        diagram.set('name', 'Infrastructure')
        
        mxGraphModel = ET.SubElement(diagram, 'mxGraphModel')
        mxGraphModel.set('dx', '1200')
        mxGraphModel.set('dy', '800')
        mxGraphModel.set('grid', '1')
        mxGraphModel.set('gridSize', '10')
        mxGraphModel.set('guides', '1')
        mxGraphModel.set('tooltips', '1')
        mxGraphModel.set('connect', '1')
        mxGraphModel.set('arrows', '1')
        mxGraphModel.set('fold', '1')
        mxGraphModel.set('page', '1')
        mxGraphModel.set('pageScale', '1')
        mxGraphModel.set('pageWidth', '1200')
        mxGraphModel.set('pageHeight', '800')
        mxGraphModel.set('background', '#ffffff')
        mxGraphModel.set('math', '0')
        mxGraphModel.set('shadow', '0')
        
        root = ET.SubElement(mxGraphModel, 'root')
        
        # Add default cells (canvas)
        mxCell_0 = ET.SubElement(root, 'mxCell')
        mxCell_0.set('id', '0')
        
        mxCell_1 = ET.SubElement(root, 'mxCell')
        mxCell_1.set('id', '1')
        mxCell_1.set('parent', '0')
        
        # Add resource cells
        for cell in self.cells:
            mxCell = ET.SubElement(root, 'mxCell')
            mxCell.set('id', cell['id'])
            mxCell.set('value', cell['value'])
            mxCell.set('style', cell['style'])
            mxCell.set('vertex', cell['vertex'])
            mxCell.set('parent', cell['parent'])
            
            geometry = ET.SubElement(mxCell, 'mxGeometry')
            geometry.set('x', str(cell['x']))
            geometry.set('y', str(cell['y']))
            geometry.set('width', str(cell['width']))
            geometry.set('height', str(cell['height']))
            geometry.set('as', 'geometry')
        
        # Add edge cells
        for edge in self.edges:
            mxCell = ET.SubElement(root, 'mxCell')
            mxCell.set('id', edge['id'])
            mxCell.set('value', edge['value'])
            mxCell.set('style', edge['style'])
            mxCell.set('edge', edge['edge'])
            mxCell.set('parent', edge['parent'])
            mxCell.set('source', edge['source'])
            mxCell.set('target', edge['target'])
            
            geometry = ET.SubElement(mxCell, 'mxGeometry')
            geometry.set('relative', '1')
            geometry.set('as', 'geometry')
        
        # Convert to string
        return ET.tostring(mxFile, encoding='unicode')
    
    def _create_empty_drawio(self) -> str:
        """Create empty draw.io document"""
        mxFile = ET.Element('mxfile')
        mxFile.set('host', 'InfraPilot')
        mxFile.set('version', '20.8.0')
        
        diagram = ET.SubElement(mxFile, 'diagram')
        diagram.set('id', '0')
        diagram.set('name', 'Empty')
        
        mxGraphModel = ET.SubElement(diagram, 'mxGraphModel')
        root = ET.SubElement(mxGraphModel, 'root')
        
        ET.SubElement(root, 'mxCell').set('id', '0')
        ET.SubElement(root, 'mxCell').set('id', '1').set('parent', '0')
        
        return ET.tostring(mxFile, encoding='unicode')


def generate_drawio_from_terraform(terraform_code: str) -> str:
    """
    Generate draw.io XML from Terraform code
    
    Args:
        terraform_code: Terraform HCL code
        
    Returns:
        draw.io XML string
    """
    generator = DrawIOGenerator()
    return generator.generate_drawio_xml(terraform_code)
