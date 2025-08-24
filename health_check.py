#!/usr/bin/env python3
"""
CredTech Platform Health Check Script
"""

import requests
import psycopg2
import redis
import time
import sys

def check_api():
    """Check if the API is responding"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✓ API is healthy")
            return True
        else:
            print(f"✗ API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ API check failed: {e}")
        return False

def check_database():
    """Check if the database is accessible"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="credtech",
            user="credtech_user",
            password="credtech_pass"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        print("✓ Database is healthy")
        return True
    except Exception as e:
        print(f"✗ Database check failed: {e}")
        return False

def check_redis():
    """Check if Redis is accessible"""
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✓ Redis is healthy")
        return True
    except Exception as e:
        print(f"✗ Redis check failed: {e}")
        return False

def check_frontend():
    """Check if the frontend is accessible"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✓ Frontend is healthy")
            return True
        else:
            print(f"✗ Frontend returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Frontend check failed: {e}")
        return False

def main():
    """Run all health checks"""
    print("CredTech Platform Health Check")
    print("=" * 35)
    
    checks = [
        ("Database", check_database),
        ("Redis", check_redis),
        ("API", check_api),
        ("Frontend", check_frontend)
    ]
    
    all_healthy = True
    
    for name, check_func in checks:
        print(f"\nChecking {name}...")
        if not check_func():
            all_healthy = False
    
    print("\n" + "=" * 35)
    if all_healthy:
        print("✓ All services are healthy!")
        sys.exit(0)
    else:
        print("✗ Some services are not healthy")
        sys.exit(1)

if __name__ == "__main__":
    main()