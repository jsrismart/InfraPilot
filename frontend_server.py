#!/usr/bin/env python3
import http.server
import socketserver
import os
from pathlib import Path

PORT = 5000  # Changed from 3000 to avoid permission issues
ROOT_DIR = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve simple_frontend.html as the default index
        if self.path in ['/', '/index.html']:
            self.path = '/simple_frontend.html'
        return super().do_GET()
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

# Change to root directory
os.chdir(ROOT_DIR)

try:
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"✓ Frontend server running at http://localhost:{PORT}")
        print(f"✓ Frontend: http://localhost:{PORT}")
        print(f"✓ Backend API at http://localhost:8000/api/v1")
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\n✓ Server stopped")
except OSError as e:
    print(f"Error: {e}")
    print("Trying alternate port...")
    PORT = 9000
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"✓ Frontend server running at http://localhost:{PORT}")
        httpd.serve_forever()

