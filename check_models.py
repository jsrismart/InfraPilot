#!/usr/bin/env python3
import urllib.request
import json

try:
    response = urllib.request.urlopen('http://localhost:11434/api/tags', timeout=5)
    data = json.loads(response.read().decode())
    models = [m.get('name', 'unknown') for m in data.get('models', [])]
    print("Available models:", models)
    
    if not models:
        print("⚠️  No models installed!")
        print("Install with: ollama pull qwen2.5-coder")
    else:
        has_qwen = any('qwen' in m.lower() for m in models)
        print(f"✅ Has qwen2.5-coder: {has_qwen}")
        if has_qwen:
            print("✅ Model is ready to use")
except Exception as e:
    print(f"❌ Error checking models: {e}")
