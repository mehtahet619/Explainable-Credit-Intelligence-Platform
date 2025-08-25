#!/usr/bin/env python3
"""
Simple API server startup script for CredTech Platform
"""
import os
import sys
import subprocess
from pathlib import Path

def setup_sqlite_database():
    """Setup SQLite database"""
    print("🔧 Setting up SQLite database...")
    
    # Update database configuration to use SQLite
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Replace PostgreSQL URL with SQLite
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
    """Start the FastAPI server"""
    print("🚀 Starting API server...")
    
    try:
        # Change to api directory and start uvicorn
        os.chdir("api")
        subprocess.run([
            "uvicorn", "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 API server stopped")
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        print("Make sure uvicorn is installed: pip install uvicorn")

def main():
    print("🚀 CredTech Platform - API Server Only")
    print("=" * 40)
    
    # Setup database
    setup_sqlite_database()
    create_database()
    
    # Start API server
    start_api_server()

if __name__ == "__main__":
    main()