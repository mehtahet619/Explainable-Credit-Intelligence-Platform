#!/usr/bin/env python3
"""
Smart startup script that automatically chooses Docker or SQLite mode
"""

import subprocess
import sys
import os

def check_docker_available():
    """Check if Docker is available and running"""
    try:
        result = subprocess.run(["docker", "ps"], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def main():
    """Main function"""
    print("🚀 CredTech Platform - Smart Startup")
    print("=" * 40)
    
    print("Checking Docker availability...")
    
    if check_docker_available():
        print("✅ Docker Desktop is running")
        print("🐳 Starting with Docker (PostgreSQL + Redis)")
        print("\nRunning: python start_with_real_data.py")
        print("=" * 40)
        
        # Run the Docker version
        os.system("python start_with_real_data.py")
    else:
        print("❌ Docker Desktop is not available")
        print("💾 Starting with SQLite (No Docker required)")
        print("\nRunning: python start_without_docker.py")
        print("=" * 40)
        
        # Run the SQLite version
        os.system("python start_without_docker.py")

if __name__ == "__main__":
    main()