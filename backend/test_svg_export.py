#!/usr/bin/env python3
"""
Test SVG generation and Lucidchart upload
"""

import requests
import json
import sys

def test_svg_export():
    """Test SVG generation and Lucidchart upload"""
    
    terraform_code = """
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "web" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}

resource "aws_security_group" "web" {
  vpc_id = aws_vpc.main.id
}

resource "aws_instance" "web_server" {
  ami = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  subnet_id = aws_subnet.web.id
  security_groups = [aws_security_group.web.id]
}

resource "aws_rds_instance" "database" {
  engine = "mysql"
  instance_class = "db.t2.micro"
}
"""
    
    print("🧪 Testing SVG Export to Lucidchart...")
    print("=" * 60)
    
    payload = {
        "terraform_code": terraform_code,
        "diagram_type": "lucidchart",
        "export_to_lucidchart": True,
        "lucidchart_doc_title": "Test SVG Architecture Diagram"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/diagram/lucidchart/export",
            json=payload,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in (200, 201):
            data = response.json()
            print("\n✅ SUCCESS!")
            print(f"Message: {data.get('message', 'No message')}")
            print(f"Document ID: {data.get('lucidchart_document_id', 'N/A')}")
            print(f"Automated Import: {data.get('automated_import', False)}")
            print(f"Edit URL: {data.get('edit_url', 'N/A')}")
            print(f"SVG Size: {len(data.get('svg_content', ''))} bytes")
            print(f"Mermaid Code Length: {len(data.get('mermaid_code', ''))} bytes")
            
            # Save SVG to file for inspection
            if data.get('svg_content'):
                svg_file = "test_output.svg"
                with open(svg_file, 'w') as f:
                    f.write(data['svg_content'])
                print(f"\n💾 SVG saved to: {svg_file}")
            
            return True
        else:
            print(f"\n❌ FAILED!")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_svg_export()
    sys.exit(0 if success else 1)
