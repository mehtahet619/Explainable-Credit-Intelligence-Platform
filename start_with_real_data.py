#!/usr/bin/env python3
"""
Start CredTech Platform with real data collection
"""

import subprocess
import sys
import os
import time
import requests
from dotenv import load_dotenv

def test_api_keys():
    """Test if the API keys are working"""
    load_dotenv()
    
    print("Testing API keys...")
    
    # Test Alpha Vantage API
    alpha_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if alpha_key and alpha_key != 'demo':
        try:
            url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol=AAPL&apikey={alpha_key}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200 and 'Symbol' in response.text:
                print("✅ Alpha Vantage API key is working")
            else:
                print("⚠️  Alpha Vantage API key may have issues")
        except Exception as e:
            print(f"⚠️  Alpha Vantage API test failed: {e}")
    else:
        print("⚠️  Alpha Vantage API key not configured")
    
    # Test News API
    news_key = os.getenv('NEWS_API_KEY')
    if news_key and news_key != 'demo':
        try:
            url = f"https://newsapi.org/v2/everything?q=Apple&apiKey={news_key}&pageSize=1"
            response = requests.get(url, timeout=10)
            if response.status_code == 200 and 'articles' in response.text:
                print("✅ News API key is working")
            else:
                print("⚠️  News API key may have issues")
        except Exception as e:
            print(f"⚠️  News API test failed: {e}")
    else:
        print("⚠️  News API key not configured")

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
    """Start database services"""
    print("Starting database services...")
    
    if not run_command("docker-compose up -d postgres redis"):
        print("Failed to start database services")
        return False
    
    print("Waiting for database to be ready...")
    time.sleep(15)
    return True

def populate_initial_data():
    """Populate database with initial sample data"""
    print("Populating database with initial data...")
    
    if not run_command("python populate_sample_data.py"):
        print("Warning: Failed to populate sample data, continuing anyway...")
    
    return True

def start_data_ingestion():
    """Start data ingestion service"""
    print("Starting data ingestion service...")
    
    # Start data ingestion in background
    ingestion_process = subprocess.Popen(
        ["python", "main.py"],
        cwd="data-ingestion"
    )
    
    print(f"Data ingestion service started (PID: {ingestion_process.pid})")
    return ingestion_process

def start_ml_pipeline():
    """Start ML pipeline service"""
    print("Starting ML pipeline service...")
    
    # Start ML pipeline in background
    ml_process = subprocess.Popen(
        ["python", "main.py"],
        cwd="ml-pipeline"
    )
    
    print(f"ML pipeline service started (PID: {ml_process.pid})")
    return ml_process

def start_api():
    """Start API server"""
    print("Starting API server...")
    
    # Start API in background
    api_process = subprocess.Popen(
        ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd="api"
    )
    
    print(f"API server started (PID: {api_process.pid})")
    time.sleep(5)
    
    return api_process

def start_frontend():
    """Start frontend development server"""
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
    
    print(f"Frontend server started (PID: {frontend_process.pid})")
    return frontend_process

def main():
    """Main function"""
    print("CredTech Platform - Real Data Collection Mode")
    print("=" * 50)
    
    # Test API keys
    test_api_keys()
    print()
    
    # Start database services
    if not start_database():
        sys.exit(1)
    
    # Populate initial data
    populate_initial_data()
    
    # Start all services
    api_process = start_api()
    if not api_process:
        sys.exit(1)
    
    ingestion_process = start_data_ingestion()
    ml_process = start_ml_pipeline()
    frontend_process = start_frontend()
    
    print("\n" + "=" * 60)
    print("🚀 CredTech Platform is running with REAL DATA!")
    print("=" * 60)
    print("Services:")
    print("- Database: Running in Docker")
    print("- API Server: http://localhost:8000")
    print("- API Docs: http://localhost:8000/docs")
    print("- Data Ingestion: Collecting real market & news data")
    print("- ML Pipeline: Generating credit scores")
    if frontend_process:
        print("- Frontend: http://localhost:3000")
    
    print("\nData Sources:")
    print("- Alpha Vantage: Financial data")
    print("- News API: Real-time news sentiment")
    print("- Yahoo Finance: Market data")
    print("- SEC EDGAR: Regulatory filings")
    
    print("\nPress Ctrl+C to stop all services")
    
    processes = [p for p in [api_process, ingestion_process, ml_process, frontend_process] if p]
    
    try:
        # Keep the script running and monitor processes
        while True:
            # Check if any process has died
            for process in processes:
                if process.poll() is not None:
                    print(f"Warning: Process {process.pid} has stopped")
            
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nStopping services...")
        
        for process in processes:
            if process:
                process.terminate()
                print(f"Process {process.pid} stopped")
        
        run_command("docker-compose down", check=False)
        print("Database services stopped")
        
        print("✅ All services stopped")

if __name__ == "__main__":
    main()