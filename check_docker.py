#!/usr/bin/env python3
"""
Check Docker Desktop status and provide solutions
"""

import subprocess
import sys
import os

def check_docker_installed():
    """Check if Docker is installed"""
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_docker_running():
    """Check if Docker Desktop is running"""
    try:
        result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def main():
    """Main function"""
    print("Docker Desktop Status Check")
    print("=" * 30)
    
    docker_installed = check_docker_installed()
    docker_running = check_docker_running()
    
    print(f"Docker Installed: {'✅ Yes' if docker_installed else '❌ No'}")
    print(f"Docker Running:   {'✅ Yes' if docker_running else '❌ No'}")
    
    if not docker_installed:
        print("\n❌ Docker is not installed")
        print("\nSolutions:")
        print("1. Install Docker Desktop from: https://www.docker.com/products/docker-desktop")
        print("2. Or use SQLite mode: python start_without_docker.py")
        return 1
    
    if not docker_running:
        print("\n❌ Docker Desktop is not running")
        print("\nSolutions:")
        print("1. Start Docker Desktop application")
        print("2. Wait for Docker to fully start (may take 1-2 minutes)")
        print("3. Or use SQLite mode: python start_without_docker.py")
        return 1
    
    print("\n✅ Docker is ready!")
    print("You can run: python start_with_real_data.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())