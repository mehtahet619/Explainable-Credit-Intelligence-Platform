#!/usr/bin/env python3
"""
Start CredTech Platform without Docker (using SQLite)
"""

import subprocess
import sys
import os
import time
import sqlite3
from dotenv import load_dotenv

def create_sqlite_database():
    """Create SQLite database with required tables"""
    print("Setting up SQLite database...")
    
    # Create database directory
    os.makedirs('data', exist_ok=True)
    
    # Connect to SQLite database
    conn = sqlite3.connect('data/credtech.db')
    cursor = conn.cursor()
    
    # Create tables (SQLite compatible)
    sql_commands = [
        """
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol VARCHAR(10) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            sector VARCHAR(100),
            industry VARCHAR(100),
            market_cap BIGINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS credit_scores (
            time TIMESTAMP NOT NULL,
            company_id INTEGER,
            score DECIMAL(5,2) NOT NULL,
            confidence DECIMAL(5,2),
            model_version VARCHAR(50),
            PRIMARY KEY (time, company_id),
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS feature_importance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            timestamp TIMESTAMP NOT NULL,
            feature_name VARCHAR(100) NOT NULL,
            importance_value DECIMAL(10,6) NOT NULL,
            shap_value DECIMAL(10,6),
            feature_value DECIMAL(15,6),
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS financial_data (
            time TIMESTAMP NOT NULL,
            company_id INTEGER,
            metric_name VARCHAR(100) NOT NULL,
            value DECIMAL(20,6),
            source VARCHAR(50),
            PRIMARY KEY (time, company_id, metric_name),
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS news_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            timestamp TIMESTAMP NOT NULL,
            headline TEXT NOT NULL,
            content TEXT,
            source VARCHAR(100),
            sentiment_score DECIMAL(5,2),
            impact_score DECIMAL(5,2),
            event_type VARCHAR(50),
            processed BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS market_data (
            time TIMESTAMP NOT NULL,
            symbol VARCHAR(10) NOT NULL,
            open_price DECIMAL(15,6),
            high_price DECIMAL(15,6),
            low_price DECIMAL(15,6),
            close_price DECIMAL(15,6),
            volume BIGINT,
            PRIMARY KEY (time, symbol)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS data_source_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name VARCHAR(100) NOT NULL UNIQUE,
            last_update TIMESTAMP,
            status VARCHAR(20) DEFAULT 'active',
            error_count INTEGER DEFAULT 0,
            last_error TEXT
        )
        """
    ]
    
    for sql in sql_commands:
        cursor.execute(sql)
    
    # Insert sample companies
    companies_data = [
        ('AAPL', 'Apple Inc.', 'Technology', 'Consumer Electronics', 3000000000000),
        ('MSFT', 'Microsoft Corporation', 'Technology', 'Software', 2800000000000),
        ('GOOGL', 'Alphabet Inc.', 'Technology', 'Internet Services', 1700000000000),
        ('TSLA', 'Tesla Inc.', 'Consumer Cyclical', 'Auto Manufacturers', 800000000000),
        ('JPM', 'JPMorgan Chase & Co.', 'Financial Services', 'Banks', 450000000000)
    ]
    
    cursor.execute("SELECT COUNT(*) FROM companies")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO companies (symbol, name, sector, industry, market_cap) VALUES (?, ?, ?, ?, ?)",
            companies_data
        )
        print("✅ Sample companies added to database")
    
    # Insert data source status
    cursor.execute("SELECT COUNT(*) FROM data_source_status")
    if cursor.fetchone()[0] == 0:
        sources = [
            ('yahoo_finance', 'active'),
            ('alpha_vantage', 'active'),
            ('news_api', 'active'),
            ('sec_edgar', 'active')
        ]
        cursor.executemany(
            "INSERT INTO data_source_status (source_name, status) VALUES (?, ?)",
            sources
        )
    
    conn.commit()
    conn.close()
    print("✅ SQLite database created successfully")

def update_database_config():
    """Update database configuration to use SQLite"""
    print("Updating database configuration...")
    
    # Update .env file
    with open('.env', 'r') as f:
        content = f.read()
    
    # Replace PostgreSQL URL with SQLite
    content = content.replace(
        'DATABASE_URL=postgresql://credtech_user:credtech_pass@localhost:5432/credtech',
        'DATABASE_URL=sqlite:///data/credtech.db'
    )
    
    # Remove Redis URL (not needed for basic functionality)
    content = content.replace('REDIS_URL=redis://localhost:6379', 'REDIS_URL=')
    
    with open('.env', 'w') as f:
        f.write(content)
    
    print("✅ Database configuration updated")

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
    print("CredTech Platform - No Docker Setup")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Test API keys
    print("Testing API keys...")
    alpha_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    news_key = os.getenv('NEWS_API_KEY')
    
    if alpha_key and alpha_key != 'demo':
        print("✅ Alpha Vantage API key configured")
    else:
        print("⚠️  Alpha Vantage API key not configured")
    
    if news_key and news_key != 'demo':
        print("✅ News API key configured")
    else:
        print("⚠️  News API key not configured")
    
    print()
    
    # Setup SQLite database
    create_sqlite_database()
    update_database_config()
    
    # Start services
    api_process = start_api()
    if not api_process:
        sys.exit(1)
    
    ingestion_process = start_data_ingestion()
    ml_process = start_ml_pipeline()
    frontend_process = start_frontend()
    
    print("\n" + "=" * 60)
    print("🚀 CredTech Platform is running (SQLite mode)!")
    print("=" * 60)
    print("Services:")
    print("- Database: SQLite (data/credtech.db)")
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
        
        print("✅ All services stopped")

if __name__ == "__main__":
    main()