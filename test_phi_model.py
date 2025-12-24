#!/usr/bin/env python3
"""Test Ollama directly without backend"""

import requests
import json

def test_ollama_direct():
    """Test Ollama inference directly"""
    
    ollama_url = "http://localhost:11434/api/generate"
    
    # Simple prompt
    prompt = "Write a simple Terraform resource for an Azure VM"
    
    print("Testing Ollama Direct Inference")
    print("=" * 60)
    print(f"Model: mistral")
    print(f"Prompt: {prompt}")
    print(f"URL: {ollama_url}")
    print("-" * 60)
    
    try:
        payload = {
            "model": "mistral",
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 200,  # Limit output
                "temperature": 0.1,
                "top_p": 0.9,
            }
        }
        
        print("Sending request...")
        response = requests.post(ollama_url, json=payload, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response received!")
            print(f"Response text length: {len(data.get('response', ''))}")
            print(f"\nResponse preview:")
            print("-" * 60)
            print(data.get('response', '')[:500])
            print("-" * 60)
            return True
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (120 seconds)")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_ollama_direct()
