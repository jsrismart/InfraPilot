#!/usr/bin/env python3
"""Simple backend startup without extra features"""
import sys
import os

# Change to backend directory
os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, '.')

# Direct import and run
from app.main import app
import uvicorn

if __name__ == "__main__":
    print("Starting InfraPilot Backend...")
    print("Backend: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
