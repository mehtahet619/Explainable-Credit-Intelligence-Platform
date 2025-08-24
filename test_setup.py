#!/usr/bin/env python3
"""
CredTech Platform Setup Test Script
"""

import os
import sys
import importlib.util

def test_python_imports():
    """Test if all required Python packages can be imported"""
    print("Testing Python imports...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'psycopg2',
        'redis',
        'pandas',
        'numpy',
        'sklearn',
        'yfinance',
        'requests',
        'schedule'
    ]
    
    optional_packages = [
        'xgboost',
        'shap'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            if package == 'sklearn':
                import sklearn
            else:
                __import__(package)
            print(f"✓ {package}")
        except ImportError as e:
            print(f"✗ {package}: {e}")
            failed_imports.append(package)
    
    # Test optional packages
    print("\nTesting optional packages...")
    for package in optional_packages:
        try:
            __import__(package)
            print(f"✓ {package} (optional)")
        except ImportError:
            print(f"- {package} (optional, not installed)")
    
    if failed_imports:
        print(f"\nFailed to import required packages: {', '.join(failed_imports)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✓ All required Python packages imported successfully")
    return True

def test_file_structure():
    """Test if all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        'docker-compose.yml',
        'requirements.txt',
        '.env',
        'database/init.sql',
        'api/main.py',
        'api/models.py',
        'api/database.py',
        'ml-pipeline/main.py',
        'data-ingestion/main.py',
        'frontend/package.json',
        'frontend/src/App.js'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\nMissing files: {', '.join(missing_files)}")
        return False
    
    print("✓ All required files exist")
    return True

def test_environment_variables():
    """Test if environment variables are set"""
    print("\nTesting environment variables...")
    
    # Load .env file
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    required_vars = [
        'DATABASE_URL',
        'REDIS_URL'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        if var in os.environ:
            print(f"✓ {var}")
        else:
            print(f"✗ {var}")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\nMissing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✓ All required environment variables are set")
    return True

def main():
    """Run all tests"""
    print("CredTech Platform Setup Test")
    print("=" * 35)
    
    tests = [
        test_file_structure,
        test_environment_variables,
        test_python_imports
    ]
    
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 35)
    if all_passed:
        print("✓ All tests passed! Setup is ready.")
        print("\nNext steps:")
        print("1. Run: python start.py")
        print("2. Or run: docker-compose up --build")
        sys.exit(0)
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()