#!/usr/bin/env python3
"""
Starter script for RAG Knowledge Base Server with Monitoring

This script starts the server with automatic recovery and monitoring.
"""

import os
import sys
import subprocess

# Change to backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Check if monitored server script exists
monitor_script = os.path.join(os.path.dirname(__file__), 'run_server_with_monitoring.py')

if not os.path.exists(monitor_script):
    print("Error: run_server_with_monitoring.py not found!")
    sys.exit(1)

print("=" * 60)
print("Starting RAG Knowledge Base Server with Monitoring...")
print("=" * 60)
print()
print("Features:")
print("• Automatic restart on failure")
print("• Health check monitoring")
print("• Exception detection and logging")
print("• Graceful shutdown handling")
print("• Reduced startup time")
print()
print("Server will be available at:")
print("  - API: http://localhost:8000")
print("  - Docs: http://localhost:8000/docs")
print()
print("Monitoring logs will be saved to:")
print("  - server_monitor.log")
print()
print("Press Ctrl+C to stop the server and monitoring")
print("=" * 60)
print()

# Start the monitored server
try:
    # Use the same Python interpreter
    cmd = [sys.executable, monitor_script]
    
    # Start the process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Stream output
    for line in iter(process.stdout.readline, ''):
        if line:
            print(line, end='')
            sys.stdout.flush()
            
except KeyboardInterrupt:
    print("\n\nShutting down server and monitoring...")
    if 'process' in locals():
        process.terminate()
        process.wait()
    print("Server and monitoring stopped.")
    sys.exit(0)
except Exception as e:
    print(f"Error starting monitored server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
