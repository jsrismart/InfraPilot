#!/usr/bin/env python3
"""Test complete InfraPilot pipeline"""
import urllib.request
import json
import time

print("=" * 60)
print("TESTING COMPLETE PIPELINE")
print("=" * 60)
print()

# Test 1: Backend health
print("1️⃣  Testing Backend API...")
try:
    response = urllib.request.urlopen('http://localhost:8001/', timeout=3)
    print(f"   ✅ Backend responding (HTTP {response.status})")
except Exception as e:
    print(f"   ❌ Backend error: {e}")
    exit(1)

# Test 2: Send prompt to generate Terraform
print()
print("2️⃣  Testing Terraform generation via Ollama...")
print("   Prompt: 'create Azure Linux VM with E series size at East US region'")
print("   Model: qwen2.5-coder")
print("   Mode: Fast (IaC only)")
print()

try:
    prompt_data = json.dumps({
        "prompt": "create Azure Linux VM with E series size at East US region"
    }).encode()
    
    req = urllib.request.Request(
        'http://localhost:8001/api/v1/infra/generate-iac?fast=true',
        data=prompt_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print("   Sending to backend... (waiting for Ollama response)")
    start = time.time()
    
    response = urllib.request.urlopen(req, timeout=180)  # 3 minute timeout
    result = json.loads(response.read().decode())
    elapsed = time.time() - start
    
    print(f"   ✅ Response received in {elapsed:.1f}s")
    print()
    
    # Check response structure
    if 'iac' in result:
        print("   ✅ Terraform code generated:")
        for filename, content in result['iac'].items():
            print(f"      • {filename}: {len(content)} characters")
    else:
        print("   ❌ No 'iac' in response")
        
except urllib.error.HTTPError as e:
    print(f"   ❌ HTTP Error {e.code}")
    try:
        error_data = json.loads(e.read().decode())
        print(f"   Details: {error_data.get('detail', 'Unknown error')}")
    except:
        pass
except Exception as e:
    print(f"   ❌ Error: {e}")
    
print()
print("=" * 60)
