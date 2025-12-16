#!/usr/bin/env python3
"""Test backend startup in detail"""
import sys
import os

os.chdir(r"c:\Users\SridharJayaraman\Downloads\infrapilot 2\infrapilot\backend")
sys.path.insert(0, os.getcwd())

print("=" * 60)
print("Testing Backend Startup")
print("=" * 60)

print("\n[1] Testing imports...")
try:
    from app.main import app
    print("✓ app.main imported successfully")
except Exception as e:
    print(f"✗ Failed to import app.main: {e}")
    sys.exit(1)

print("\n[2] Testing FastAPI app creation...")
try:
    print(f"✓ FastAPI app created: {app}")
    print(f"  - Routes count: {len(app.routes)}")
    print(f"  - Middleware count: {len(app.user_middleware)}")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

print("\n[3] Testing route initialization...")
try:
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  - {route.methods if hasattr(route, 'methods') else 'N/A'} {route.path}")
except Exception as e:
    print(f"✗ Failed: {e}")

print("\n[4] Testing main dependencies...")
try:
    from pricing_calculator import CloudPricingCalculator
    print("✓ pricing_calculator imported")
    
    from diagram_generator import TerraformParser
    print("✓ diagram_generator imported")
    
    from app.agents.designer_agent import DesignerAgent
    print("✓ designer_agent imported")
    
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("All startup tests passed!")
print("=" * 60)
