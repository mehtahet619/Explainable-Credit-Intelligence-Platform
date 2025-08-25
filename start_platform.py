#!/usr/bin/env python3
"""
Start both API server and frontend for CredTech Platform
"""
import os
import sys
import subprocess
import time
import signal
from pathlib import Path

# Global process references
api_process = None
frontend_process = None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Shutting down CredTech Platform...")
    
    if frontend_process:
        frontend_process.terminate()
        print("✅ Frontend stopped")
    
    if api_process:
        api_process.terminate()
        print("✅ API server stopped")
    
    sys.exit(0)

def setup_sqlite_database():
    """Setup SQLite database"""
    print("🔧 Setting up SQLite database...")
    
    # Update database configuration to use SQLite
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Replace PostgreSQL URL with SQLite
        if 'postgresql://' in content:
            content = content.replace(
                'DATABASE_URL=postgresql://credtech_user:credtech_pass@localhost:5432/credtech',
                'DATABASE_URL=sqlite:///./credit_scoring.db'
            )
            
            with open(env_path, 'w') as f:
                f.write(content)
    else:
        # Create .env file with SQLite configuration
        with open(env_path, 'w') as f:
            f.write("""DATABASE_URL=sqlite:///./credit_scoring.db
ALPHA_VANTAGE_API_KEY=V4A2QX47V83DDXIG
NEWS_API_KEY=c36e6c0f2267409c8e0d49c98c56a02c
""")
    
    print("✅ Database configuration updated to SQLite")

def create_database():
    """Create and populate SQLite database"""
    print("📊 Creating SQLite database...")
    
    try:
        # Run the database initialization
        result = subprocess.run([
            sys.executable, "api/init_database.py"
        ], capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            print("✅ SQLite database created successfully")
        else:
            print(f"⚠️  Database creation warning: {result.stderr}")
            print("Continuing anyway...")
    except Exception as e:
        print(f"⚠️  Database setup error: {e}")
        print("Continuing anyway...")

def start_api_server():
    """Start the FastAPI server in background"""
    global api_process
    print("🚀 Starting API server...")
    
    try:
        api_process = subprocess.Popen([
            "uvicorn", "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], cwd="api")
        
        # Wait a moment for the server to start
        time.sleep(3)
        print("✅ API server started on http://localhost:8000")
        return True
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        return False

def start_frontend():
    """Start the React frontend"""
    global frontend_process
    print("🌐 Starting frontend...")
    
    try:
        frontend_process = subprocess.Popen([
            "npm", "start"
        ], cwd="frontend")
        
        print("✅ Frontend starting on http://localhost:3000")
        return True
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return False

def main():
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🚀 CredTech Platform - Full Stack Startup")
    print("=" * 45)
    
    # Setup database
    setup_sqlite_database()
    create_database()
    
    # Start API server
    if not start_api_server():
        print("❌ Failed to start API server")
        return
    
    # Start frontend
    if not start_frontend():
        print("❌ Failed to start frontend")
        if api_process:
            api_process.terminate()
        return
    
    print("\n🎉 CredTech Platform is running!")
    print("📊 Frontend: http://localhost:3000")
    print("🔧 API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Wait for processes to complete
        while True:
            if api_process and api_process.poll() is not None:
                print("❌ API server stopped unexpectedly")
                break
            if frontend_process and frontend_process.poll() is not None:
                print("❌ Frontend stopped unexpectedly")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()