"""
Updated export_to_lucidchart endpoint with automatic import
"""

# Add to the existing diagram.py file after line 9 (imports section):

# from lucidchart_automation import import_mermaid_sync

# Replace the export_to_lucidchart function starting at line 213:

@router.post("/lucidchart/export")
def export_to_lucidchart(request: DiagramRequest) -> dict:
    """Export diagram directly to Lucidchart account with automatic import
    
    Workflow:
    1. Generate Mermaid diagram from Terraform
    2. Create empty Lucidchart document via API
    3. Automatically import Mermaid diagram using browser automation
    4. Return rendered diagram and Lucidchart document link
    """
    if not request.terraform_code or not request.terraform_code.strip():
        raise HTTPException(status_code=400, detail="Terraform code cannot be empty")
    
    try:
        # Generate Mermaid diagram
        parser = TerraformParser(request.terraform_code)
        generator = DiagramGenerator(parser)
        mermaid_code = generator.generate_mermaid_diagram()
        
        # Try to export to Lucidchart
        lucidchart_api = LucidchartAPI()
        
        if not lucidchart_api.is_configured():
            print("[INFO] Lucidchart API not configured")
            return {
                "success": False,
                "message": "Lucidchart API not configured. Set LUCIDCHART_API_KEY environment variable.",
                "api_configured": False,
                "mermaid_code": mermaid_code,
                "preview_url": create_mermaid_live_link(mermaid_code),
                "instructions": "Copy the Mermaid code and manually import to Lucidchart via File > Import",
                "lucidchart_url": "https://app.lucidchart.com"
            }
        
        print(f"[INFO] Creating Lucidchart document: {request.lucidchart_doc_title}")
        # Create document in Lucidchart
        doc_data = lucidchart_api.create_document(request.lucidchart_doc_title)
        
        if not doc_data:
            print("[ERROR] Failed to create Lucidchart document")
            return {
                "success": False,
                "message": "Failed to create Lucidchart document. Please check API key and try again.",
                "mermaid_code": mermaid_code,
                "fallback_url": "https://app.lucidchart.com"
            }
        
        doc_id = doc_data.get("documentId") or doc_data.get("id")
        if not doc_id:
            print("[ERROR] No document ID in response")
            return {
                "success": False,
                "message": "Document creation returned no ID",
                "mermaid_code": mermaid_code
            }
        
        print(f"[OK] Document created: {doc_id}")
        
        # AUTOMATED IMPORT - Use browser automation
        print(f"[INFO] Starting automated import for document {doc_id}...")
        try:
            from lucidchart_automation import import_mermaid_sync
            
            import_result = import_mermaid_sync(
                document_id=doc_id,
                mermaid_code=mermaid_code,
                api_key=lucidchart_api.config.api_key
            )
            
            if import_result.get("imported"):
                print(f"[SUCCESS] Diagram automatically imported to Lucidchart!")
                
                return {
                    "success": True,
                    "message": f"✅ Diagram created and automatically imported to Lucidchart!",
                    "automated_import": True,
                    "lucidchart_document_id": doc_id,
                    "edit_url": f"https://lucid.app/lucidchart/{doc_id}/edit",
                    "view_url": f"https://app.lucidchart.com/documents/view/{doc_id}",
                    "open_url": f"https://lucid.app/lucidchart/{doc_id}/edit?view_items={doc_id}",
                    "mermaid_code": mermaid_code,
                    "preview_url": create_mermaid_live_link(mermaid_code),
                    "metadata": {
                        "provider": parser.get_provider(),
                        "resources_count": len(parser.resources),
                        "resource_types": list(set(r.type for r in parser.resources))
                    }
                }
            else:
                print(f"[WARNING] Automated import failed, falling back to manual import")
                # Fall back to manual import instructions
                import_instructions = generate_lucidchart_import_instructions(doc_id, mermaid_code)
                
                return {
                    "success": True,
                    "message": f"Document created but automated import failed. Please import manually.",
                    "automated_import": False,
                    "manual_import_needed": True,
                    "lucidchart_document_id": doc_id,
                    "edit_url": f"https://lucid.app/lucidchart/{doc_id}/edit",
                    "view_url": f"https://app.lucidchart.com/documents/view/{doc_id}",
                    "import_instructions": import_instructions,
                    "mermaid_code": mermaid_code,
                    "preview_url": create_mermaid_live_link(mermaid_code),
                    "metadata": {
                        "provider": parser.get_provider(),
                        "resources_count": len(parser.resources),
                        "resource_types": list(set(r.type for r in parser.resources))
                    }
                }
                
        except ImportError:
            print("[WARNING] Playwright not available, using manual import fallback")
            
            edit_url = f"https://lucid.app/lucidchart/{doc_id}/edit"
            import_instructions = generate_lucidchart_import_instructions(doc_id, mermaid_code)
            
            return {
                "success": True,
                "message": f"Document created. Import diagram manually.",
                "automated_import": False,
                "lucidchart_document_id": doc_id,
                "edit_url": edit_url,
                "view_url": f"https://app.lucidchart.com/documents/view/{doc_id}",
                "import_instructions": import_instructions,
                "mermaid_code": mermaid_code,
                "preview_url": create_mermaid_live_link(mermaid_code),
                "metadata": {
                    "provider": parser.get_provider(),
                    "resources_count": len(parser.resources),
                    "resource_types": list(set(r.type for r in parser.resources))
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] During Lucidchart export: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export to Lucidchart: {str(e)}"
        )
