#!/usr/bin/env python3
import http.server
import socketserver
import os
from pathlib import Path

PORT = 3001
ROOT_DIR = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

# Change to root directory
os.chdir(ROOT_DIR)

with socketserver.TCPServer(("127.0.0.1", PORT), MyHTTPRequestHandler) as httpd:
    print(f"✓ Frontend server running at http://localhost:{PORT}")
    print(f"✓ Open http://localhost:{PORT}/simple_frontend.html in your browser")
    print(f"✓ Backend API at http://localhost:8001")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Server stopped")
