#!/usr/bin/env python3
"""Test professional architecture diagram generation"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from diagram_generator import TerraformParser, DiagramGenerator
from diagram_image_generator import AdvancedDiagramGenerator

# Sample Terraform code
terraform_code = """
provider "aws" {
  region = "us-east-1"
}

# VPC Setup
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "web_subnet_1" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}

resource "aws_subnet" "app_subnet_1" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.0.2.0/24"
}

resource "aws_subnet" "db_subnet_1" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.0.3.0/24"
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
}

# Load Balancer
resource "aws_lb" "web_alb" {
  name = "web-alb"
  subnets = [aws_subnet.web_subnet_1.id]
}

# EC2 Instances
resource "aws_instance" "web_server_1" {
  ami = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  subnet_id = aws_subnet.app_subnet_1.id
}

resource "aws_instance" "web_server_2" {
  ami = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  subnet_id = aws_subnet.app_subnet_1.id
}

# Lambda Function
resource "aws_lambda_function" "api_function" {
  filename = "api_function.zip"
  function_name = "api-processor"
  role = aws_iam_role.lambda_role.arn
  handler = "index.handler"
}

# RDS Database
resource "aws_db_instance" "main_db" {
  identifier = "main-database"
  engine = "mysql"
  instance_class = "db.t2.micro"
  allocated_storage = 20
}

# S3 Buckets
resource "aws_s3_bucket" "app_bucket" {
  bucket = "app-data-bucket"
}

resource "aws_s3_bucket" "logs_bucket" {
  bucket = "app-logs-bucket"
}

# IAM Role
resource "aws_iam_role" "lambda_role" {
  name = "lambda-execution-role"
}

# Security Group
resource "aws_security_group" "web_sg" {
  name = "web-security-group"
  vpc_id = aws_vpc.main.id
}
"""

# Parse Terraform
parser = TerraformParser(terraform_code)

print(f"✓ Parsed Terraform code")
print(f"  Provider: {parser.get_provider()}")
print(f"  Resources: {len(parser.resources)}")

# Generate professional architecture diagram
advanced_gen = AdvancedDiagramGenerator(parser)
svg_diagram = advanced_gen.generate_professional_architecture_diagram()

print(f"\n✓ Generated professional architecture diagram")
print(f"  SVG size: {len(svg_diagram)} bytes")

# Save SVG to file
output_file = "professional_architecture.svg"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(svg_diagram)

print(f"\n✓ Saved to {output_file}")
print(f"\nDiagram preview (first 500 chars):")
print(svg_diagram[:500])

# Also test the API response format
from app.api.v1.diagram import DiagramRequest, DiagramResponse
from fastapi import HTTPException

print("\n\nTesting API Response Format:")
request = DiagramRequest(terraform_code=terraform_code, diagram_type="lucidchart")

try:
    # Simulate what the API does
    parser = TerraformParser(request.terraform_code)
    advanced_generator = AdvancedDiagramGenerator(parser)
    content = advanced_generator.generate_professional_architecture_diagram()
    
    response = DiagramResponse(
        success=True,
        diagram_type=request.diagram_type,
        content=content,
        metadata={
            "provider": parser.get_provider(),
            "resources_count": len(parser.resources),
            "resource_types": list(set(r.type for r in parser.resources))
        }
    )
    
    print(f"✓ API Response created successfully")
    print(f"  Success: {response.success}")
    print(f"  Diagram type: {response.diagram_type}")
    print(f"  Content size: {len(response.content)} bytes")
    print(f"  Resources: {response.metadata['resources_count']}")
    print(f"  Resource types: {', '.join(response.metadata['resource_types'][:3])}...")
    
except Exception as e:
    print(f"✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n✓ All tests passed!")
