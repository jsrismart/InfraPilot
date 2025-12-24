#!/usr/bin/env python3
"""
Start the backend server for InfraPilot
"""
import os
import sys

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import and run uvicorn
import uvicorn

if __name__ == "__main__":
    # Run the Uvicorn server
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    )
