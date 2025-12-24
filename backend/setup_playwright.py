"""
Initialize Playwright installation on backend startup
Ensures Chromium browser is available for diagram automation
"""

import subprocess
import sys
import os

def ensure_playwright_installed():
    """Check and install Playwright if needed"""
    try:
        import playwright
        print("[SETUP] Playwright is already installed")
        return True
    except ImportError:
        print("[SETUP] Playwright not found, installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright", "-q"])
            print("[SETUP] ✅ Playwright installed successfully")
            return True
        except Exception as e:
            print(f"[SETUP] ⚠️  Failed to install Playwright: {e}")
            return False

def ensure_chromium_installed():
    """Check and install Chromium browser if needed"""
    try:
        import platform
        
        # Skip on Windows due to download size and complexity
        if platform.system() == "Windows":
            print("[SETUP] ⚠️  Skipping Chromium on Windows (use manual import or Linux/macOS)")
            return False
        
        # Check if browsers are installed
        import playwright.sync_api
        browsers_path = os.path.expanduser("~/.cache/ms-playwright")
        
        if os.path.exists(browsers_path) and os.listdir(browsers_path):
            print("[SETUP] Chromium browser is already installed")
            return True
        
        print("[SETUP] Installing Chromium browser (this may take a few minutes)...")
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium", "--with-deps"])
        print("[SETUP] ✅ Chromium installed successfully")
        return True
        
    except Exception as e:
        print(f"[SETUP] ⚠️  Failed to install Chromium: {e}")
        print("[SETUP] Note: Falling back to manual import mode")
        return False

def setup_playwright():
    """Main setup function"""
    print("\n" + "="*70)
    print("  PLAYWRIGHT AUTOMATION SETUP")
    print("="*70 + "\n")
    
    # Install Playwright package
    if not ensure_playwright_installed():
        print("[SETUP] Skipping Chromium installation - Playwright not available")
        return False
    
    # Install Chromium browser
    if not ensure_chromium_installed():
        print("[SETUP] Chromium installation failed - will use manual import fallback")
        return False
    
    print("\n" + "="*70)
    print("  SETUP COMPLETE - AUTOMATIC DIAGRAM IMPORT ENABLED")
    print("="*70 + "\n")
    return True

if __name__ == "__main__":
    success = setup_playwright()
    sys.exit(0 if success else 1)
