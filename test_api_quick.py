#!/usr/bin/env python3
"""Quick test of the backend API"""
import requests
import json
import time

time.sleep(2)  # Give server time to start

BASE_URL = "http://localhost:8000/api/v1"

def test_api():
    # Test root endpoint
    print("Testing root endpoint...")
    response = requests.get("http://localhost:8000/", timeout=5)
    print(f"Root: {response.status_code} - {response.text}")
    
    # Test generate-iac endpoint
    print("\nTesting /generate-iac endpoint...")
    payload = {
        "prompt": "Create 2 E series VMs in East US"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate-iac",
            json=payload,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"Keys: {list(data.keys())}")
            
            if "iac_files" in data:
                iac = data["iac_files"]
                print(f"\nGenerated Files:")
                for filename, content in iac.items():
                    vm_count = content.count("azurerm_windows_virtual_machine")
                    print(f"  - {filename}: {vm_count} VMs")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_api()
