#!/usr/bin/env python3
"""
Test API endpoint for professional architecture diagram
"""

import requests
import json

API_BASE = "http://localhost:8001/api/v1"

# Sample Terraform infrastructure
terraform_code = """
provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "main-vpc"
  }
}

# Public Subnets
resource "aws_subnet" "public_subnet_1" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-east-1a"
}

resource "aws_subnet" "public_subnet_2" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.0.2.0/24"
  availability_zone = "us-east-1b"
}

# Private Subnets
resource "aws_subnet" "private_subnet_1" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.0.10.0/24"
  availability_zone = "us-east-1a"
}

resource "aws_subnet" "private_subnet_2" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.0.11.0/24"
  availability_zone = "us-east-1b"
}

resource "aws_subnet" "database_subnet" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.0.20.0/24"
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
}

# NAT Gateway
resource "aws_nat_gateway" "main" {
  subnet_id = aws_subnet.public_subnet_1.id
}

# Application Load Balancer
resource "aws_lb" "main" {
  name = "main-alb"
  load_balancer_type = "application"
  subnets = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]
}

# Network Load Balancer
resource "aws_lb" "nlb" {
  name = "main-nlb"
  load_balancer_type = "network"
  subnets = [aws_subnet.private_subnet_1.id, aws_subnet.private_subnet_2.id]
}

# EC2 Instances
resource "aws_instance" "web_server_1" {
  ami = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.small"
  subnet_id = aws_subnet.private_subnet_1.id
  tags = {
    Name = "web-server-1"
  }
}

resource "aws_instance" "web_server_2" {
  ami = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.small"
  subnet_id = aws_subnet.private_subnet_2.id
  tags = {
    Name = "web-server-2"
  }
}

# Lambda Functions
resource "aws_lambda_function" "api_handler" {
  filename = "api.zip"
  function_name = "api-handler"
  role = aws_iam_role.lambda.arn
  handler = "index.handler"
}

resource "aws_lambda_function" "data_processor" {
  filename = "processor.zip"
  function_name = "data-processor"
  role = aws_iam_role.lambda.arn
  handler = "index.handler"
}

# RDS Database
resource "aws_db_instance" "main" {
  identifier = "main-db"
  engine = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  db_subnet_group_name = aws_db_subnet_group.main.name
}

resource "aws_db_subnet_group" "main" {
  name = "main-db-subnet-group"
  subnet_ids = [aws_subnet.database_subnet.id]
}

# DynamoDB Table
resource "aws_dynamodb_table" "sessions" {
  name = "sessions"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "session_id"
  attribute {
    name = "session_id"
    type = "S"
  }
}

# S3 Buckets
resource "aws_s3_bucket" "application_data" {
  bucket = "app-data-prod"
}

resource "aws_s3_bucket" "logs" {
  bucket = "app-logs-prod"
}

resource "aws_s3_bucket" "backup" {
  bucket = "app-backup-prod"
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "main" {
  enabled = true
  is_ipv6_enabled = true
  default_root_object = "index.html"
  origin {
    domain_name = aws_s3_bucket.application_data.bucket_regional_domain_name
    origin_id = "s3-app-data"
  }
  default_cache_behavior {
    allowed_methods = ["GET", "HEAD"]
    cached_methods = ["GET", "HEAD"]
    target_origin_id = "s3-app-data"
    viewer_protocol_policy = "redirect-to-https"
    forwarded_values {
      query_string = false
    }
  }
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

# API Gateway
resource "aws_api_gateway_rest_api" "main" {
  name = "main-api"
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda" {
  name = "lambda-execution-role"
}

# Security Groups
resource "aws_security_group" "alb" {
  name = "alb-sg"
  vpc_id = aws_vpc.main.id
}

resource "aws_security_group" "app" {
  name = "app-sg"
  vpc_id = aws_vpc.main.id
}

resource "aws_security_group" "db" {
  name = "db-sg"
  vpc_id = aws_vpc.main.id
}
"""

print("Testing Professional Architecture Diagram API\n")
print("=" * 60)

try:
    # Test the Lucidchart endpoint which now returns professional architecture SVG
    print("\n1. Requesting Professional Architecture Diagram...")
    response = requests.post(
        f"{API_BASE}/diagram/generate-diagram",
        json={
            "terraform_code": terraform_code,
            "diagram_type": "lucidchart"
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success!")
        print(f"   - Diagram type: {data['diagram_type']}")
        print(f"   - Resources found: {data['metadata']['resources_count']}")
        print(f"   - Provider: {data['metadata']['provider']}")
        print(f"   - Content size: {len(data['content'])} bytes")
        
        # Verify it's SVG
        if '<svg' in data['content']:
            print(f"   - Format: SVG ✓")
        else:
            print(f"   - Format: Unknown ✗")
        
        # Save to file for inspection
        svg_file = "output_professional_architecture.svg"
        with open(svg_file, 'w', encoding='utf-8') as f:
            f.write(data['content'])
        print(f"\n   SVG saved to: {svg_file}")
        
        # Show resource types
        print(f"\n   Resource types in diagram:")
        for res_type in sorted(data['metadata']['resource_types'])[:5]:
            print(f"     - {res_type}")
        if len(data['metadata']['resource_types']) > 5:
            print(f"     ... and {len(data['metadata']['resource_types']) - 5} more")
        
    else:
        print(f"   ✗ Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"   ✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("\n✓ Test complete!")
print("\nYou can now:")
print("  1. View the professional architecture SVG in a browser")
print("  2. Import it into visualization tools")
print("  3. Use it for infrastructure documentation")
