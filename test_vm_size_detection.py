#!/usr/bin/env python
"""Test script to verify VM size detection from prompts"""

import sys
sys.path.insert(0, r'c:\Users\SridharJayaraman\Downloads\infrapilot 2\infrapilot\backend')

from app.agents.designer_agent import DesignerAgent

# Test cases
test_cases = [
    "Create a azure vm with B series at South India region",
    "Create Azure VM with E4 size in Central US",
    "Create azure vm with E series at westus",
    "I need a D2 VM in east us",
    "Standard_B2s VM in southindia please",
    "Setup a B1 instance at north europe",
]

print("\n" + "="*80)
print("VM SIZE DETECTION TEST")
print("="*80)

agent = DesignerAgent()

for i, prompt in enumerate(test_cases, 1):
    print(f"\n[Test {i}] Prompt: {prompt}")
    print("-" * 80)
    
    result = agent.generate_from_prompt_parsing(prompt)
    
    # Extract the main.tf which contains VM size
    if "main.tf" in result:
        main_content = result["main.tf"]
        # Find vm_size line
        for line in main_content.split("\n"):
            if "vm_size" in line:
                print(f"✓ Generated: {line.strip()}")
                break
        
        # Check for errors
        if "ERROR" in main_content:
            print(f"❌ Error detected: {main_content}")
    else:
        print("❌ main.tf not found in result")

print("\n" + "="*80)
print("Detection test complete!")
print("="*80)
