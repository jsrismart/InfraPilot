"""
SVG generation from Mermaid diagrams
Converts Mermaid to SVG and uploads to Lucidchart as image
"""

import subprocess
import json
import os
import sys
import tempfile
import base64
import requests
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

def generate_svg_from_mermaid(mermaid_code: str) -> Optional[str]:
    """
    Generate SVG from Mermaid code using online service or local conversion
    Falls back to creating a simple SVG representation if mermaid-cli not available
    
    Args:
        mermaid_code: Mermaid diagram code
        
    Returns:
        SVG content as string, or None if conversion failed
    """
    
    # Method 1: Try using mermaid-cli if available
    svg_content = _try_mmdc_conversion(mermaid_code)
    if svg_content:
        print(f"✓ Successfully converted Mermaid to SVG using mmdc ({len(svg_content)} bytes)")
        return svg_content
    
    # Method 2: Try using mermaid.js via node
    svg_content = _try_node_conversion(mermaid_code)
    if svg_content:
        print(f"✓ Successfully converted Mermaid to SVG using Node.js ({len(svg_content)} bytes)")
        return svg_content
    
    # Method 3: Fallback to creating a basic SVG from mermaid structure
    svg_content = _create_fallback_svg_from_mermaid(mermaid_code)
    if svg_content:
        print(f"✓ Generated fallback SVG from Mermaid ({len(svg_content)} bytes)")
        return svg_content
    
    return None


def _try_mmdc_conversion(mermaid_code: str) -> Optional[str]:
    """Try to convert using mermaid-cli (mmdc)"""
    try:
        # Create temporary files for input and output
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f_in:
            f_in.write(mermaid_code)
            input_file = f_in.name
        
        output_file = input_file.replace('.mmd', '.svg')
        
        try:
            # Convert mermaid to SVG
            result = subprocess.run(
                ["mmdc", "-i", input_file, "-o", output_file, "-t", "default"],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0 and os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    return f.read()
            
        finally:
            # Cleanup temporary files
            try:
                if os.path.exists(input_file):
                    os.remove(input_file)
                if os.path.exists(output_file):
                    os.remove(output_file)
            except:
                pass
                
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    return None


def _try_node_conversion(mermaid_code: str) -> Optional[str]:
    """Try to convert using Node.js mermaid library"""
    try:
        import tempfile
        
        # Create a Node.js script to convert Mermaid to SVG
        node_script = f"""
const mermaid = require('mermaid');
mermaid.initialize({{ startOnLoad: true, theme: 'default' }});

const svg = mermaid.render('diagram', `{mermaid_code.replace(chr(96), chr(96) + chr(92))}`);
console.log(svg);
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(node_script)
            node_file = f.name
        
        try:
            result = subprocess.run(
                ["node", node_file],
                capture_output=True,
                timeout=15,
                text=True
            )
            
            if result.returncode == 0 and result.stdout:
                return result.stdout.strip()
        finally:
            try:
                os.remove(node_file)
            except:
                pass
                
    except:
        pass
    
    return None


def _create_fallback_svg_from_mermaid(mermaid_code: str) -> Optional[str]:
    """
    Create a basic SVG representation from Mermaid code
    Parses simple Mermaid syntax and creates visual boxes/connections
    """
    try:
        lines = mermaid_code.strip().split('\n')
        
        # Extract diagram type and nodes
        nodes = []
        connections = []
        
        for line in lines:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('%%') or line.startswith('--'):
                continue
            
            # Parse node definitions (simplified)
            if '[' in line and ']' in line:
                parts = line.split('[')
                if len(parts) > 1:
                    node_id = parts[0].strip()
                    node_text = parts[1].split(']')[0].strip()
                    nodes.append((node_id, node_text))
            
            # Parse connections (arrows)
            if '-->' in line or '-.->' in line:
                parts = line.split('-->' if '-->' in line else '-.->')
                if len(parts) == 2:
                    from_id = parts[0].strip()
                    to_id = parts[1].strip()
                    connections.append((from_id, to_id))
        
        if not nodes:
            return None
        
        # Create SVG with boxes and connections
        svg_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 800" width="1000" height="800">',
            '<defs>',
            '<style type="text/css">',
            '.node { fill: #4A90E2; stroke: #2E5C8A; stroke-width: 2; }',
            '.node-label { fill: white; font-family: Arial, sans-serif; font-size: 12px; text-anchor: middle; dominant-baseline: middle; }',
            '.connection { stroke: #333; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }',
            '.arrow { fill: #333; }',
            '</style>',
            '<marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">',
            '<polygon points="0 0, 10 3, 0 6" class="arrow"/>',
            '</marker>',
            '</defs>'
        ]
        
        # Position nodes in a grid
        cols_per_row = 3
        box_width = 150
        box_height = 60
        start_x = 50
        start_y = 50
        x_spacing = 250
        y_spacing = 150
        
        node_positions = {}
        for idx, (node_id, node_text) in enumerate(nodes):
            col = idx % cols_per_row
            row = idx // cols_per_row
            x = start_x + col * x_spacing
            y = start_y + row * y_spacing
            node_positions[node_id] = (x, y)
            
            # Draw node box
            svg_lines.append(f'<rect x="{x - box_width//2}" y="{y - box_height//2}" width="{box_width}" height="{box_height}" class="node" rx="5"/>')
            svg_lines.append(f'<text x="{x}" y="{y}" class="node-label">{node_text}</text>')
        
        # Draw connections
        for from_id, to_id in connections:
            if from_id in node_positions and to_id in node_positions:
                x1, y1 = node_positions[from_id]
                x2, y2 = node_positions[to_id]
                svg_lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="connection"/>')
        
        svg_lines.append('</svg>')
        
        return '\n'.join(svg_lines)
        
    except Exception as e:
        print(f"Error creating fallback SVG: {e}")
        return None


def mermaid_to_svg(mermaid_code: str) -> Optional[str]:
    """
    Convert Mermaid diagram code to SVG (legacy wrapper)
    
    Args:
        mermaid_code: Mermaid diagram code
        
    Returns:
        SVG content as string, or None if conversion failed
    """
    return generate_svg_from_mermaid(mermaid_code)


def svg_to_base64(svg_content: str) -> str:
    """
    Convert SVG content to base64 encoding
    
    Args:
        svg_content: SVG content as string
        
    Returns:
        Base64 encoded SVG
    """
    svg_bytes = svg_content.encode('utf-8')
    base64_bytes = base64.b64encode(svg_bytes)
    return base64_bytes.decode('utf-8')


def upload_svg_to_lucidchart(
    document_id: str,
    svg_content: str,
    api_key: str,
    title: str = "Architecture Diagram"
) -> Tuple[bool, Dict[str, Any]]:
    """
    Upload SVG as image to Lucidchart document using REST API
    
    Args:
        document_id: Lucidchart document ID
        svg_content: SVG content as string
        api_key: Lucidchart API key
        title: Title for the image
        
    Returns:
        Tuple of (success, response_data)
    """
    try:
        # Convert SVG to data URL
        svg_base64 = svg_to_base64(svg_content)
        svg_data_url = f"data:image/svg+xml;base64,{svg_base64}"
        
        # Lucidchart API endpoint for adding shapes/images
        url = f"https://api.lucidchart.com/v1/documents/{document_id}/shapes"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        # Create image shape in Lucidchart
        payload = {
            "type": "image",
            "x": 100,
            "y": 100,
            "width": 1000,
            "height": 800,
            "imageUrl": svg_data_url,
            "title": title,
            "name": title,
        }
        
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=15
        )
        
        if response.status_code in (200, 201):
            data = response.json()
            print(f"✓ SVG uploaded to Lucidchart successfully")
            return True, data
        else:
            # Try alternative endpoint for file import
            print(f"⚠ Image shape endpoint returned {response.status_code}, trying alternative...")
            
            # Alternative: Try direct document import
            import_url = f"https://api.lucidchart.com/v1/documents/{document_id}/import"
            import_payload = {
                "content": svg_content,
                "format": "svg"
            }
            
            import_response = requests.post(
                import_url,
                json=import_payload,
                headers=headers,
                timeout=15
            )
            
            if import_response.status_code in (200, 201):
                data = import_response.json()
                print(f"✓ SVG imported to Lucidchart successfully")
                return True, data
            else:
                error_msg = f"Failed to upload SVG (status: {response.status_code})"
                print(f"✗ {error_msg}")
                return False, {"error": error_msg, "status": response.status_code}
                
    except Exception as e:
        error_msg = f"Error uploading SVG to Lucidchart: {str(e)}"
        print(f"✗ {error_msg}")
        return False, {"error": error_msg}


def generate_and_upload_svg_diagram(
    mermaid_code: str,
    document_id: str,
    api_key: str,
    title: str = "Architecture Diagram"
) -> Dict[str, Any]:
    """
    Complete workflow: Generate SVG from Mermaid and upload to Lucidchart
    
    Args:
        mermaid_code: Mermaid diagram code
        document_id: Lucidchart document ID
        api_key: Lucidchart API key
        title: Title for the diagram
        
    Returns:
        Dictionary with status and results
    """
    result = {
        "success": False,
        "mermaid_to_svg": False,
        "svg_upload": False,
        "svg_content": None,
        "svg_size": 0,
        "error": None,
        "message": ""
    }
    
    # Step 1: Convert Mermaid to SVG
    svg_content = mermaid_to_svg(mermaid_code)
    if not svg_content:
        result["error"] = "Failed to convert Mermaid to SVG"
        result["message"] = "Mermaid diagram could not be converted to SVG format"
        return result
    
    result["mermaid_to_svg"] = True
    result["svg_content"] = svg_content
    result["svg_size"] = len(svg_content)
    result["message"] = f"✓ SVG generated ({result['svg_size']} bytes)"
    
    # Step 2: Upload SVG to Lucidchart
    success, upload_response = upload_svg_to_lucidchart(
        document_id,
        svg_content,
        api_key,
        title
    )
    
    if success:
        result["success"] = True
        result["svg_upload"] = True
        result["message"] = "✓ SVG uploaded to Lucidchart successfully"
        result["upload_response"] = upload_response
    else:
        result["svg_upload"] = False
        result["error"] = upload_response.get("error", "Unknown error during upload")
        result["message"] = f"SVG generated but upload failed: {result['error']}"
    
    return result
