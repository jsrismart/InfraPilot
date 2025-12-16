#!/usr/bin/env python3
"""
Standalone server runner that keeps the backend alive and responsive
"""
import subprocess
import sys
import os
import time
import threading

os.chdir(r"c:\Users\SridharJayaraman\Downloads\infrapilot 2\infrapilot\backend")

# Start the Uvicorn server in a subprocess
print("Starting InfraPilot Backend Server...")
print("-" * 60)

proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", 
     "--host", "127.0.0.1", "--port", "8001"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines=True,
    bufsize=1
)

# Print output as it arrives
def print_output():
    try:
        for line in proc.stdout:
            if line:
                print(line.rstrip())
    except:
        pass

output_thread = threading.Thread(target=print_output, daemon=True)
output_thread.start()

# Keep the process alive
try:
    print("\nServer started successfully!")
    print("Press Ctrl+C to stop the server")
    print("-" * 60)
    
    while True:
        time.sleep(1)
        if proc.poll() is not None:
            print(f"Server process died with exit code {proc.returncode}")
            sys.exit(proc.returncode)
except KeyboardInterrupt:
    print("\nShutting down...")
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    print("Server stopped.")
    sys.exit(0)
