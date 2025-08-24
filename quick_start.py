#!/usr/bin/env python3
"""
Quick start script for CredTech Platform
"""

import subprocess
import sys
import os
import time

def run_command(command, cwd=None, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"Error running command: {command}")
            print(f"Error output: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception running command {command}: {e}")
        return False

def start_database():
    """Start just the database services"""
    print("Starting database services...")
    
    if not run_command("docker-compose up -d postgres redis"):
        print("Failed to start database services")
        return False
    
    print("Waiting for database to be ready...")
    time.sleep(10)
    return True

def populate_data():
    """Populate the database with sample data"""
    print("Populating database with sample data...")
    
    if not run_command("python populate_sample_data.py"):
        print("Failed to populate sample data")
        return False
    
    return True

def start_api():
    """Start the API server"""
    print("Starting API server...")
    
    # Start API in background
    api_process = subprocess.Popen(
        ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd="api"
    )
    
    print("API server started (PID: {})".format(api_process.pid))
    time.sleep(5)
    
    return api_process

def start_frontend():
    """Start the frontend development server"""
    print("Installing frontend dependencies...")
    
    if not run_command("npm install", cwd="frontend"):
        print("Failed to install frontend dependencies")
        return None
    
    print("Starting frontend server...")
    
    # Start frontend in background
    frontend_process = subprocess.Popen(
        ["npm", "start"],
        cwd="frontend"
    )
    
    print("Frontend server started (PID: {})".format(frontend_process.pid))
    return frontend_process

def main():
    """Main function"""
    print("CredTech Platform Quick Start")
    print("=" * 35)
    
    # Start database services
    if not start_database():
        sys.exit(1)
    
    # Populate with sample data
    if not populate_data():
        print("Warning: Failed to populate sample data, continuing anyway...")
    
    # Start API server
    api_process = start_api()
    if not api_process:
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("Warning: Failed to start frontend")
    
    print("\n" + "=" * 50)
    print("🚀 CredTech Platform is starting up!")
    print("=" * 50)
    print("Services:")
    print("- Database: Running in Docker")
    print("- API Server: http://localhost:8000")
    print("- API Docs: http://localhost:8000/docs")
    if frontend_process:
        print("- Frontend: http://localhost:3000")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        
        if api_process:
            api_process.terminate()
            print("API server stopped")
        
        if frontend_process:
            frontend_process.terminate()
            print("Frontend server stopped")
        
        run_command("docker-compose down", check=False)
        print("Database services stopped")
        
        print("✅ All services stopped")

if __name__ == "__main__":
    main()