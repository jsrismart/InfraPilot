#!/usr/bin/env python3
import http.server
import socketserver
import os
from pathlib import Path

PORTS = [5000, 9000, 9001, 9002]  # Try multiple ports
ROOT_DIR = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

# Change to root directory
os.chdir(ROOT_DIR)

# Try to bind to available port
httpd = None
port_used = None
for PORT in PORTS:
    try:
        httpd = socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler)
        port_used = PORT
        break
    except OSError as e:
        continue

if httpd:
    print(f"✓ Frontend server running at http://localhost:{port_used}")
    print(f"✓ Open http://localhost:{port_used}/simple_frontend.html in your browser")
    print(f"✓ Backend API at http://localhost:8000/api/v1")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Server stopped")
else:
    print("✗ Failed to bind to any available port")
    exit(1)
