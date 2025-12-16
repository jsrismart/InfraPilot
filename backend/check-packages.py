#!/usr/bin/env python3
"""
InfraPilot Dependency Checker - Python Version
Checks and installs missing Python packages
"""

import subprocess
import sys
from pathlib import Path

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name.replace("-", "_")
    
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """Install a package using pip"""
    print(f"📦 Installing {package_name}...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", package_name],
        capture_output=True,
        text=True
    )
    return result.returncode == 0

def main():
    print("\n🔍 InfraPilot Python Dependency Checker")
    print("=" * 40)
    
    packages = [
        ("fastapi", "fastapi"),
        ("uvicorn[standard]", "uvicorn"),
        ("pydantic", "pydantic"),
        ("pydantic-settings", "pydantic_settings"),
        ("ollama", "ollama"),
        ("python-dotenv", "dotenv"),
    ]
    
    all_ok = True
    missing = []
    
    print("\nChecking packages...\n")
    
    for package, import_name in packages:
        if check_package(package, import_name):
            print(f"✅ {package:<30} Installed")
        else:
            print(f"❌ {package:<30} MISSING")
            missing.append(package)
            all_ok = False
    
    print("\n" + "=" * 40)
    
    if all_ok:
        print("✨ All packages are installed!")
        return 0
    
    print(f"\n⚠️  {len(missing)} package(s) missing")
    print("\nInstalling missing packages...\n")
    
    failed = []
    for package in missing:
        if not install_package(package):
            failed.append(package)
            print(f"❌ Failed to install {package}")
        else:
            print(f"✅ {package} installed")
    
    print("\n" + "=" * 40)
    
    if failed:
        print(f"❌ Failed to install {len(failed)} package(s):")
        for package in failed:
            print(f"   - {package}")
        print("\nPlease try installing manually:")
        print(f"   pip install {' '.join(failed)}")
        return 1
    else:
        print("✨ All packages installed successfully!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
