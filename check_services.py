#!/usr/bin/env python3
import urllib.request
import json
import sys

services = {
    "Backend API": "http://localhost:8001/",
    "Frontend": "http://localhost:5000/",
    "Ollama": "http://localhost:11434/api/tags"
}

print("=" * 60)
print("SERVICE STATUS CHECK")
print("=" * 60)

all_ok = True
for name, url in services.items():
    try:
        response = urllib.request.urlopen(url, timeout=3)
        print(f"✅ {name:20} -> {response.status} OK")
    except urllib.error.URLError as e:
        print(f"❌ {name:20} -> FAILED: {e.reason}")
        all_ok = False
    except Exception as e:
        print(f"❌ {name:20} -> ERROR: {str(e)[:50]}")
        all_ok = False

print("=" * 60)
if all_ok:
    print("✅ ALL SERVICES RUNNING!")
    sys.exit(0)
else:
    print("⚠️  Some services are not responding")
    sys.exit(1)
