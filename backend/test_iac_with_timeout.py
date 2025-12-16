#!/usr/bin/env python3
"""Test IaC generation with timeout"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001/api/v1"

print("Testing IaC Generation (with timeout handling)...")
payload = {"prompt": "Create an Azure VM with D2_v3 size in East US"}

try:
    print("Sending request... (timeout set to 15 seconds)")
    response = requests.post(f"{BASE_URL}/infra/generate-iac", json=payload, timeout=15)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"IaC files: {list(data.get('iac', {}).keys())}")
    print(f"\nFull response:")
    print(json.dumps(data, indent=2)[:1000])
except requests.exceptions.Timeout:
    print("TIMEOUT: Request took too long. The Ollama LLM is probably unavailable.")
    print("The backend should fallback to template-based generation.")
except Exception as e:
    print(f"Error: {e}")
