#!/usr/bin/env python3
"""Check Ollama status before starting application"""
import subprocess
import urllib.request
import json
import sys
import time

print("=" * 60)
print("OLLAMA PRE-FLIGHT CHECK")
print("=" * 60)
print()

# Step 1: Check if Ollama process is running
print("1️⃣  Checking Ollama process...")
try:
    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq ollama.exe'], 
                          capture_output=True, text=True, timeout=5)
    if 'ollama.exe' in result.stdout:
        print("   ✅ Ollama process is running")
    else:
        print("   ❌ Ollama process is NOT running")
        print("   → Start Ollama: ollama serve")
        sys.exit(1)
except Exception as e:
    print(f"   ⚠️  Could not check process: {e}")

# Step 2: Check Ollama API
print()
print("2️⃣  Checking Ollama API (http://localhost:11434)...")
try:
    response = urllib.request.urlopen('http://localhost:11434/api/tags', timeout=5)
    data = json.loads(response.read().decode())
    print("   ✅ Ollama API is responding")
except Exception as e:
    print(f"   ❌ Ollama API NOT responding: {e}")
    print("   → Start Ollama: ollama serve")
    sys.exit(1)

# Step 3: Check available models
print()
print("3️⃣  Checking available models...")
try:
    models = data.get('models', [])
    if not models:
        print("   ❌ No models installed!")
        print("   → Install: ollama pull mistral")
        sys.exit(1)
    
    print(f"   ✅ Found {len(models)} model(s):")
    for model in models:
        print(f"      • {model.get('name', 'unknown')}")
    
    # Check for required models
    model_names = [m.get('name', '').lower() for m in models]
    has_mistral = any('mistral' in name for name in model_names)
    
    if has_mistral:
        print("   ✅ Mistral model available (configured)")
    else:
        print("   ⚠️  Mistral not found, but other models available")
        
except Exception as e:
    print(f"   ❌ Error checking models: {e}")
    sys.exit(1)

# Step 4: Test Ollama generation
print()
print("4️⃣  Testing Ollama Terraform generation...")
try:
    test_prompt = "Create a simple Azure VM in Terraform"
    
    data_json = json.dumps({
        "model": "mistral",
        "prompt": test_prompt,
        "stream": False
    }).encode()
    
    req = urllib.request.Request(
        'http://localhost:11434/api/generate',
        data=data_json,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"   Sending prompt: '{test_prompt}'")
    print("   Waiting for Ollama response (this may take 30-60 seconds)...")
    
    start = time.time()
    response = urllib.request.urlopen(req, timeout=120)
    result = json.loads(response.read().decode())
    elapsed = time.time() - start
    
    if result.get('response'):
        print(f"   ✅ Ollama generated response ({elapsed:.1f}s)")
        print(f"   Response length: {len(result['response'])} chars")
    else:
        print("   ❌ No response from Ollama")
        sys.exit(1)
        
except urllib.error.HTTPError as e:
    print(f"   ❌ HTTP Error {e.code}: {e.reason}")
    sys.exit(1)
except socket.timeout:
    print(f"   ❌ Request timed out - Ollama is too slow or not responding")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("✅ ALL CHECKS PASSED - READY TO START APPLICATION")
print("=" * 60)
print()
print("Next steps:")
print("1. Start Backend:  cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001")
print("2. Start Frontend: python frontend_server.py")
print("3. Open browser:   http://localhost:5000")
print()
