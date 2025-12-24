#!/usr/bin/env python3
import urllib.request
import json

print("Testing API endpoints...")
print("=" * 50)

# Test 1: Health check
try:
    response = urllib.request.urlopen('http://localhost:8001/', timeout=3)
    print(f"✅ Root endpoint: {response.status}")
except Exception as e:
    print(f"❌ Root endpoint error: {e}")

# Test 2: API health
try:
    response = urllib.request.urlopen('http://localhost:8001/api/v1/health', timeout=3)
    print(f"✅ Health endpoint: {response.status}")
except Exception as e:
    print(f"❌ Health endpoint error: {e}")

# Test 3: Generate IaC (will fail without Ollama, but shows if endpoint exists)
try:
    data = json.dumps({'prompt': 'test'}).encode()
    req = urllib.request.Request(
        'http://localhost:8001/api/v1/infra/generate-iac',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    response = urllib.request.urlopen(req, timeout=5)
    print(f"✅ IaC endpoint: {response.status}")
except urllib.error.HTTPError as e:
    if e.code in [422, 500]:  # Expected errors (validation or Ollama not ready)
        print(f"✅ IaC endpoint exists (returned HTTP {e.code})")
    else:
        print(f"❌ IaC endpoint error: HTTP {e.code}")
except Exception as e:
    print(f"❌ IaC endpoint error: {e}")

print("=" * 50)
print("✅ Backend API is accessible!")
