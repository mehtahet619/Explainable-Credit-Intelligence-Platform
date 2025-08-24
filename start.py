#!/usr/bin/env python3
"""
CredTech Platform Startup Script
"""

import subprocess
import sys
import os
import time

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running command: {command}")
            print(f"Error output: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception running command {command}: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    # Check Docker
    if not run_command("docker --version"):
        print("Docker is not installed or not in PATH")
        return False
    
    # Check Docker Compose
    if not run_command("docker-compose --version"):
        print("Docker Compose is not installed or not in PATH")
        return False
    
    print("✓ Dependencies check passed")
    return True

def start_services():
    """Start all services using Docker Compose"""
    print("Starting CredTech Platform services...")
    
    # Build and start services
    if not run_command("docker-compose up --build -d"):
        print("Failed to start services")
        return False
    
    print("✓ Services started successfully")
    
    # Wait for services to be ready
    print("Waiting for services to be ready...")
    time.sleep(30)
    
    # Check service health
    if run_command("docker-compose ps"):
        print("✓ Services are running")
        return True
    
    return False

def show_status():
    """Show the status of all services"""
    print("\n" + "="*50)
    print("CredTech Platform Status")
    print("="*50)
    
    run_command("docker-compose ps")
    
    print("\nAccess URLs:")
    print("- Frontend Dashboard: http://localhost:3000")
    print("- API Documentation: http://localhost:8000/docs")
    print("- Database: localhost:5432")
    print("- Redis: localhost:6379")

def main():
    """Main startup function"""
    print("CredTech Platform Startup")
    print("=" * 30)
    
    if not check_dependencies():
        sys.exit(1)
    
    if not start_services():
        sys.exit(1)
    
    show_status()
    
    print("\n✓ CredTech Platform is ready!")
    print("Press Ctrl+C to stop all services")
    
    try:
        # Keep the script running
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nStopping services...")
        run_command("docker-compose down")
        print("✓ Services stopped")

if __name__ == "__main__":
    main()