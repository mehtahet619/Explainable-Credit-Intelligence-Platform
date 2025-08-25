#!/usr/bin/env python3
"""
Quick fix startup for CredTech Platform
"""
import os
import sys
import subprocess
from pathlib import Path

def create_database():
    """Create SQLite database in root directory"""
    print("📊 Creating SQLite database...")
    
    # Create a simple database setup script
    db_script = """
import sqlite3
from datetime import datetime, timedelta
import random

# Create database
conn = sqlite3.connect('credit_scoring.db')
cursor = conn.cursor()

# Create companies table
cursor.execute('''
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY,
    symbol TEXT UNIQUE,
    name TEXT,
    sector TEXT,
    industry TEXT,
    market_cap INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
''')

# Create credit_scores table
cursor.execute('''
CREATE TABLE IF NOT EXISTS credit_scores (
    time TIMESTAMP,
    company_id INTEGER,
    score DECIMAL(5,2),
    confidence DECIMAL(5,2),
    model_version TEXT,
    PRIMARY KEY (time, company_id),
    FOREIGN KEY (company_id) REFERENCES companies(id)
)
''')

# Insert sample companies
companies = [
    (1, 'AAPL', 'Apple Inc.', 'Technology', 'Consumer Electronics', 3000000000000),
    (2, 'MSFT', 'Microsoft Corporation', 'Technology', 'Software', 2800000000000),
    (3, 'GOOGL', 'Alphabet Inc.', 'Technology', 'Internet Services', 1800000000000),
    (4, 'AMZN', 'Amazon.com Inc.', 'Consumer Discretionary', 'E-commerce', 1600000000000),
    (5, 'TSLA', 'Tesla Inc.', 'Consumer Discretionary', 'Electric Vehicles', 800000000000)
]

for company in companies:
    cursor.execute('''
    INSERT OR REPLACE INTO companies 
    (id, symbol, name, sector, industry, market_cap, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', company + (datetime.now(), datetime.now()))

# Insert sample credit scores
base_time = datetime.now() - timedelta(days=30)
for company_id in range(1, 6):
    for i in range(30):
        score_time = base_time + timedelta(days=i)
        score = round(random.uniform(650, 850), 2)
        confidence = round(random.uniform(0.7, 0.95), 4)
        
        cursor.execute('''
        INSERT OR REPLACE INTO credit_scores 
        (time, company_id, score, confidence, model_version)
        VALUES (?, ?, ?, ?, ?)
        ''', (score_time, company_id, score, confidence, 'v1.0'))

conn.commit()
conn.close()
print("Database created successfully")
"""
    
    with open('create_db.py', 'w', encoding='utf-8') as f:
        f.write(db_script)
    
    # Run the database creation script
    subprocess.run([sys.executable, 'create_db.py'])
    
    # Clean up
    os.remove('create_db.py')

def start_api():
    """Start API server"""
    print("🚀 Starting API server...")
    os.chdir('api')
    subprocess.run([
        'uvicorn', 'main:app',
        '--host', '0.0.0.0',
        '--port', '8000',
        '--reload'
    ])

def main():
    print("🚀 CredTech Platform - Quick Fix")
    print("=" * 35)
    
    create_database()
    start_api()

if __name__ == "__main__":
    main()