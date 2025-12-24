"""
Automated Lucidchart Diagram Import using Playwright
Handles automatic import of Mermaid diagrams to Lucidchart
"""

import asyncio
import os
import base64

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    PlaywrightTimeoutError = TimeoutError


async def import_mermaid_to_lucidchart(
    document_id: str,
    mermaid_code: str,
    api_key: str
) -> dict:
    """
    Automatically import Mermaid diagram to Lucidchart using Playwright
    
    Args:
        document_id: Lucidchart document ID
        mermaid_code: Mermaid diagram code to import
        api_key: Lucidchart API key for authentication
        
    Returns:
        Dictionary with import status and document info
    """
    if not PLAYWRIGHT_AVAILABLE:
        print("[PLAYWRIGHT] Playwright not available - returning false for automation")
        return {
            "imported": False,
            "error": "Playwright not installed. Install with: pip install playwright"
        }
    
    print(f"[PLAYWRIGHT] Starting automated import for document: {document_id}")
    
    try:
        async with async_playwright() as p:
            # Launch browser in headless mode
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
            context = await browser.new_context()
            page = await context.new_page()
            
            # Set viewport
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Navigate to Lucidchart edit page
            edit_url = f"https://lucid.app/lucidchart/{document_id}/edit"
            print(f"[PLAYWRIGHT] Opening document: {edit_url}")
            
            await page.goto(edit_url, wait_until="networkidle", timeout=60000)
            print("[PLAYWRIGHT] Document page loaded")
            
            # Wait for page to fully load
            await asyncio.sleep(5)
            
            # Try to find and click File menu
            print("[PLAYWRIGHT] Looking for File menu...")
            try:
                # Look for File menu button (varies based on UI)
                file_menu = page.locator("[data-testid='file-menu'], [aria-label*='File'], .file-menu, button:has-text('File')")
                
                # Wait for file menu to be available
                await file_menu.first.wait_for(timeout=10000)
                await file_menu.first.click()
                print("[PLAYWRIGHT] File menu clicked")
                
                # Wait for Import option to appear
                await asyncio.sleep(2)
                
                # Click Import option
                import_option = page.locator("[data-testid='import'], [aria-label*='Import'], button:has-text('Import')")
                await import_option.first.wait_for(timeout=5000)
                await import_option.first.click()
                print("[PLAYWRIGHT] Import option clicked")
                
                # Wait for import dialog
                await asyncio.sleep(2)
                
                # Look for Mermaid option in import dialog
                mermaid_option = page.locator("button:has-text('Mermaid'), [data-testid*='mermaid']")
                if await mermaid_option.first.is_visible(timeout=3000):
                    await mermaid_option.first.click()
                    print("[PLAYWRIGHT] Mermaid option selected")
                
                # Find text input area and paste mermaid code
                await asyncio.sleep(1)
                textarea = page.locator("textarea, [contenteditable='true'], input[type='text']").first
                await textarea.fill(mermaid_code, timeout=5000)
                print("[PLAYWRIGHT] Mermaid code pasted")
                
                # Click Import button in dialog
                import_btn = page.locator("button:has-text('Import'), [data-testid='import-button']").last
                await import_btn.click(timeout=5000)
                print("[PLAYWRIGHT] Import button clicked")
                
                # Wait for diagram to render
                await asyncio.sleep(5)
                
                # Take screenshot of the diagram
                screenshot = await page.screenshot(path=f"/tmp/lucidchart_{document_id}.png")
                print(f"[PLAYWRIGHT] Screenshot taken: {screenshot}")
                
                print("[PLAYWRIGHT] Import completed successfully!")
                
                await browser.close()
                
                return {
                    "success": True,
                    "message": "Mermaid diagram imported to Lucidchart successfully",
                    "document_id": document_id,
                    "edit_url": edit_url,
                    "view_url": f"https://app.lucidchart.com/documents/view/{document_id}",
                    "imported": True
                }
                
            except Exception as e:
                print(f"[PLAYWRIGHT] Error during import process: {e}")
                await browser.close()
                return {
                    "success": False,
                    "message": f"Automated import failed: {str(e)}. Please use manual import.",
                    "document_id": document_id,
                    "edit_url": edit_url,
                    "imported": False,
                    "error": str(e)
                }
                
    except Exception as e:
        print(f"[PLAYWRIGHT] Fatal error: {e}")
        return {
            "success": False,
            "message": f"Browser automation failed: {str(e)}",
            "error": str(e),
            "imported": False
        }


def import_mermaid_sync(document_id: str, mermaid_code: str, api_key: str) -> dict:
    """
    Synchronous wrapper for async import function
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            import_mermaid_to_lucidchart(document_id, mermaid_code, api_key)
        )
        return result
    finally:
        loop.close()
