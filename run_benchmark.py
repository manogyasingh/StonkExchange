#!/usr/bin/env python3
"""
Simple wrapper to start the server and run load tests
"""

import subprocess
import sys
import time
import requests

def check_server_running():
    """Check if the Flask server is running"""
    try:
        response = requests.get("http://localhost:5001/login", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_server():
    """Start the Flask server in background if not running"""
    if check_server_running():
        print("✓ Server is already running")
        return True
    
    print("Starting StonkExchange server...")
    try:
        subprocess.Popen([sys.executable, "run_server.py"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        # Wait for server to start
        for i in range(10):
            time.sleep(1)
            if check_server_running():
                print("✓ Server started successfully")
                return True
            print(f"Waiting for server... ({i+1}/10)")
        
        print("❌ Server failed to start within 10 seconds")
        return False
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def main():
    print("StonkExchange Load Test Runner")
    print("=============================")
    
    # Start server if needed
    if not start_server():
        print("Cannot run load test without server")
        sys.exit(1)
    
    # Run the load test
    print("\nStarting load test...")
    try:
        subprocess.run([sys.executable, "benchmark_client.py"])
    except KeyboardInterrupt:
        print("\nLoad test interrupted")
    except Exception as e:
        print(f"Load test failed: {e}")

if __name__ == "__main__":
    main() 