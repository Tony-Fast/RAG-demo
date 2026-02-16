#!/usr/bin/env python3
"""
RAG Knowledge Base Server with Monitoring and Auto-Recovery

This script provides:
1. Service health monitoring
2. Automatic restart on failure
3. Exception detection and logging
4. Graceful shutdown handling
5. Reduced startup time
"""

import subprocess
import time
import json
import logging
import argparse
import signal
import sys
import os
from pathlib import Path
import http.client
import urllib.parse

# Constants
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
HEALTH_CHECK_INTERVAL = 30  # seconds
MAX_RESTART_ATTEMPTS = 10
RESTART_BACKOFF_FACTOR = 2  # Exponential backoff for restart attempts
MAX_RESTART_TIME = 3600  # Maximum time (seconds) for restart attempts
LOG_FILE = "server_monitor.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ServerMonitor:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.process = None
        self.restart_count = 0
        self.last_restart_time = 0
        self.running = True
        self.start_time = time.time()
        
        # Create log directory if it doesn't exist
        log_dir = Path(LOG_FILE).parent
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
    
    def start_server(self):
        """Start the RAG server process"""
        logger.info("Starting RAG Knowledge Base Server...")
        
        # Build the command
        cmd = [
            sys.executable,
            "-m", "uvicorn",
            "app.main:app",
            "--host", self.host,
            "--port", str(self.port),
            "--log-level", "info",
            "--timeout-keep-alive", "30",
            "--timeout-graceful-shutdown", "10"
        ]
        
        try:
            # Start the process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Start logging output
            self.log_process_output()
            
            logger.info(f"Server started successfully on http://{self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
    
    def log_process_output(self):
        """Log server process output in a separate thread"""
        def log_output():
            if self.process:
                for line in iter(self.process.stdout.readline, ''):
                    if line:
                        logger.info(f"SERVER: {line.strip()}")
        
        import threading
        thread = threading.Thread(target=log_output, daemon=True)
        thread.start()
    
    def check_health(self):
        """Check if the server is healthy"""
        try:
            conn = http.client.HTTPConnection(self.host, self.port, timeout=10)
            conn.request("GET", "/health")
            response = conn.getresponse()
            
            if response.status == 200:
                try:
                    data = json.loads(response.read().decode())
                    if data.get("status") == "healthy":
                        return True, "Server is healthy"
                except json.JSONDecodeError:
                    return False, "Invalid health check response format"
            
            return False, f"Health check failed with status code: {response.status}"
            
        except Exception as e:
            return False, f"Health check error: {str(e)}"
    
    def stop_server(self):
        """Stop the server gracefully"""
        if self.process:
            logger.info("Stopping server...")
            
            try:
                # Send SIGINT (Ctrl+C) for graceful shutdown
                if os.name == 'nt':  # Windows
                    self.process.terminate()
                else:  # Unix-like
                    os.kill(self.process.pid, signal.SIGINT)
                
                # Wait for process to exit
                timeout = 15
                start_time = time.time()
                while time.time() - start_time < timeout:
                    if self.process.poll() is not None:
                        break
                    time.sleep(0.5)
                
                # Force kill if not exited
                if self.process.poll() is None:
                    logger.warning("Server did not exit gracefully, forcing shutdown")
                    self.process.kill()
                
                exit_code = self.process.poll()
                logger.info(f"Server stopped with exit code: {exit_code}")
                
            except Exception as e:
                logger.error(f"Error stopping server: {e}")
            
            finally:
                self.process = None
    
    def restart_server(self):
        """Restart the server"""
        current_time = time.time()
        
        # Check if we've exceeded restart limits
        if self.restart_count >= MAX_RESTART_ATTEMPTS:
            logger.error(f"Maximum restart attempts ({MAX_RESTART_ATTEMPTS}) reached. Stopping monitoring.")
            return False
        
        # Check if we're restarting too frequently
        if current_time - self.last_restart_time < 60:  # Less than 1 minute
            backoff_time = min(60, (2 ** self.restart_count) * 5)
            logger.warning(f"Restarting too frequently. Waiting {backoff_time} seconds before next attempt.")
            time.sleep(backoff_time)
        
        # Stop current server
        self.stop_server()
        
        # Increment restart count
        self.restart_count += 1
        self.last_restart_time = current_time
        
        # Wait a bit before starting
        time.sleep(2)
        
        # Start new server
        logger.info(f"Attempting to restart server (attempt {self.restart_count}/{MAX_RESTART_ATTEMPTS})...")
        return self.start_server()
    
    def run(self):
        """Main monitoring loop"""
        logger.info("Starting server monitoring...")
        
        # Initial start
        if not self.start_server():
            logger.error("Failed to start server initially. Exiting.")
            return
        
        # Give server time to start up
        time.sleep(5)
        
        # Main loop
        while self.running:
            try:
                # Check if process is still running
                if self.process and self.process.poll() is not None:
                    exit_code = self.process.poll()
                    logger.error(f"Server process exited with code: {exit_code}")
                    if not self.restart_server():
                        break
                
                # Health check
                is_healthy, message = self.check_health()
                if not is_healthy:
                    logger.warning(f"Health check failed: {message}")
                    # Give server a chance to recover
                    time.sleep(10)
                    # Check again
                    is_healthy, message = self.check_health()
                    if not is_healthy:
                        logger.error(f"Server is unhealthy: {message}")
                        if not self.restart_server():
                            break
                else:
                    # Reset restart count if server is healthy
                    if self.restart_count > 0:
                        logger.info("Server recovered successfully. Resetting restart count.")
                        self.restart_count = 0
                
                # Sleep until next check
                time.sleep(HEALTH_CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt. Stopping...")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(5)
        
        # Cleanup
        self.stop_server()
        logger.info("Monitoring stopped.")

def signal_handler(signum, frame):
    """Handle termination signals"""
    logger.info("Received termination signal. Preparing to stop...")
    if 'monitor' in globals():
        monitor.running = False

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="RAG Knowledge Base Server with Monitoring")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Server host")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Server port")
    args = parser.parse_args()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run monitor
    monitor = ServerMonitor(host=args.host, port=args.port)
    monitor.run()
