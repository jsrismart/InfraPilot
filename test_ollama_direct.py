#!/usr/bin/env python
import sys
import os
import time

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Test Ollama generation directly
from app.agents.designer_agent import DesignerAgent

agent = DesignerAgent()

# Test with updated prompt
test_prompt = "Create 3 D series Azure VMs in East US and one Express Route"

print(f"Testing Ollama generation with updated prompt...")
print(f"Input: {test_prompt}")
print(f"Waiting for generation...")

start = time.time()
result = agent.generate(test_prompt)
elapsed = time.time() - start

if result:
    print(f"\n✅ SUCCESS - Generated in {elapsed:.1f}s")
    print(f"Files generated: {list(result.keys())}")
    for filename, content in result.items():
        print(f"\n--- {filename} ({len(content)} chars) ---")
        print(content[:500] if len(content) > 500 else content)
else:
    print(f"\n❌ FAILED - No result after {elapsed:.1f}s")
