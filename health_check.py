#!/usr/bin/env python
"""
Quick health check for InfraPilot
Verifies all components are working correctly
"""
import sys
import os
import time
import subprocess

print("\n" + "=" * 80)
print("INFRAPILOT HEALTH CHECK")
print("=" * 80)

# Check 1: Ollama availability
print("\n[1/4] Checking Ollama service...")
try:
    import requests
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        tags = response.json()
        models = [m['name'] for m in tags.get('models', [])]
        if models:
            print(f"      ✅ Ollama running - Models: {', '.join(models)}")
        else:
            print(f"      ⚠️  Ollama running but no models found")
    else:
        print(f"      ❌ Ollama not responding properly (status {response.status_code})")
except Exception as e:
    print(f"      ❌ Ollama not available: {e}")

# Check 2: Backend API availability
print("\n[2/4] Checking Backend API...")
try:
    response = requests.get("http://localhost:8000/", timeout=5)
    if response.status_code == 200:
        print(f"      ✅ Backend running - {response.json()['message']}")
    else:
        print(f"      ❌ Backend not responding properly (status {response.status_code})")
except Exception as e:
    print(f"      ❌ Backend not available: {e}")

# Check 3: Frontend availability  
print("\n[3/4] Checking Frontend Server...")
try:
    response = requests.get("http://localhost:3000/", timeout=5)
    if response.status_code == 200:
        if "simple_frontend" in response.text or "InfraPilot" in response.text:
            print(f"      ✅ Frontend running - UI ready")
        else:
            print(f"      ⚠️  Frontend responding but content unexpected")
    else:
        print(f"      ❌ Frontend not responding properly (status {response.status_code})")
except Exception as e:
    print(f"      ❌ Frontend not available: {e}")

# Check 4: Quick pricing test
print("\n[4/4] Checking Pricing Module...")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
try:
    from app.agents.finops_agent import FinOpsAgent
    
    # Simple test terraform
    test_tf = {
        'main.tf': '''resource "azurerm_windows_virtual_machine" "test" {
  size = "Standard_B2s"
  location = "eastus"
}'''
    }
    
    agent = FinOpsAgent()
    result = agent.analyze(test_tf)
    
    if result and 'resources' in result:
        print(f"      ✅ Pricing module working - Analyzed {len(result.get('resources', []))} resources")
    else:
        print(f"      ❌ Pricing module not responding correctly")
except Exception as e:
    print(f"      ❌ Pricing module error: {e}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
If all checks pass (✅), InfraPilot is ready to use:

1. Open http://localhost:3000 in your browser
2. Enter a prompt like "Create 3 D series Azure VMs in East US"
3. Click "Generate"
4. Wait 2-3 minutes for Terraform + Pricing calculation

For quick testing without full flow:
  python verify_architecture.py    # Full end-to-end test
  python test_pricing_only.py      # Quick pricing test only
  python test_ollama_direct.py     # Quick Ollama test
""")
print("=" * 80 + "\n")
