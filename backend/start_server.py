#!/usr/bin/env python
"""
RAG Knowledge Base Server Starter
"""
import subprocess
import sys
import os

# Change to backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Activate virtual environment and start server
cmd = [
    "venv\\Scripts\\python.exe",
    "-m", "uvicorn", 
    "app.main:app", 
    "--host", "0.0.0.0", 
    "--port", "8000",
    "--reload"
]

print("=" * 50)
print("Starting RAG Knowledge Base Server...")
print("=" * 50)
print()
print("Server will be available at:")
print("  - API: http://localhost:8000")
print("  - Docs: http://localhost:8000/docs")
print()
print("Press Ctrl+C to stop the server")
print("=" * 50)
print()

# Start the server
try:
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Stream output
    for line in process.stdout:
        print(line, end='')
        
except KeyboardInterrupt:
    print("\n\nShutting down server...")
    process.terminate()
    process.wait()
    print("Server stopped.")
    sys.exit(0)
