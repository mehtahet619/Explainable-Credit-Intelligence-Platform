#!/usr/bin/env python3
"""
Test real data collection with API keys
"""

import os
import sys
import requests
import yfinance as yf
from dotenv import load_dotenv
import json

def test_alpha_vantage():
    """Test Alpha Vantage API"""
    print("Testing Alpha Vantage API...")
    
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if not api_key or api_key == 'demo':
        print("❌ Alpha Vantage API key not configured")
        return False
    
    try:
        # Test company overview
        url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol=AAPL&apikey={api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'Symbol' in data:
                print("✅ Alpha Vantage API working")
                print(f"   Sample data: {data.get('Name', 'N/A')} - Market Cap: {data.get('MarketCapitalization', 'N/A')}")
                return True
            else:
                print(f"❌ Alpha Vantage API error: {data}")
                return False
        else:
            print(f"❌ Alpha Vantage API HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Alpha Vantage API exception: {e}")
        return False

def test_news_api():
    """Test News API"""
    print("Testing News API...")
    
    api_key = os.getenv('NEWS_API_KEY')
    if not api_key or api_key == 'demo':
        print("❌ News API key not configured")
        return False
    
    try:
        # Test news search
        url = f"https://newsapi.org/v2/everything?q=Apple&apiKey={api_key}&pageSize=3&sortBy=publishedAt"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok' and 'articles' in data:
                articles = data['articles']
                print("✅ News API working")
                print(f"   Found {len(articles)} articles")
                if articles:
                    print(f"   Latest: {articles[0].get('title', 'N/A')[:60]}...")
                return True
            else:
                print(f"❌ News API error: {data}")
                return False
        else:
            print(f"❌ News API HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ News API exception: {e}")
        return False

def test_yahoo_finance():
    """Test Yahoo Finance (free)"""
    print("Testing Yahoo Finance...")
    
    try:
        # Test stock data
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        hist = ticker.history(period="5d")
        
        if info and not hist.empty:
            print("✅ Yahoo Finance working")
            print(f"   Company: {info.get('longName', 'N/A')}")
            print(f"   Current Price: ${info.get('currentPrice', 'N/A')}")
            print(f"   Historical data points: {len(hist)}")
            return True
        else:
            print("❌ Yahoo Finance returned empty data")
            return False
    except Exception as e:
        print(f"❌ Yahoo Finance exception: {e}")
        return False

def test_data_collectors():
    """Test the data collector classes"""
    print("Testing data collector implementations...")
    
    # Add the data-ingestion directory to path
    sys.path.append('data-ingestion')
    
    try:
        from data_collectors import YahooFinanceCollector, AlphaVantageCollector, NewsCollector
        from database import DatabaseManager
        
        # Create a mock database manager for testing
        class MockDB:
            def get_company_id(self, symbol):
                return 1
            def insert_market_data(self, data):
                print(f"   Would insert market data: {data['symbol']} - ${data['close_price']}")
            def insert_financial_data(self, data):
                print(f"   Would insert financial data: {data['metric_name']} = {data['value']}")
            def insert_news_event(self, data):
                print(f"   Would insert news: {data['headline'][:50]}...")
        
        mock_db = MockDB()
        
        # Test Yahoo Finance collector
        print("\n📊 Testing Yahoo Finance Collector:")
        yahoo_collector = YahooFinanceCollector(mock_db)
        yahoo_collector.collect_stock_data("AAPL")
        
        # Test Alpha Vantage collector
        print("\n📈 Testing Alpha Vantage Collector:")
        alpha_collector = AlphaVantageCollector(mock_db)
        alpha_collector.collect_financial_data("AAPL")
        
        # Test News collector
        print("\n📰 Testing News Collector:")
        news_collector = NewsCollector(mock_db)
        news_collector.collect_company_news("AAPL", "Apple Inc.")
        
        print("✅ Data collectors working")
        return True
        
    except Exception as e:
        print(f"❌ Data collectors error: {e}")
        return False

def main():
    """Main test function"""
    print("CredTech Platform - Data Collection Test")
    print("=" * 45)
    
    # Load environment variables
    load_dotenv()
    
    tests = [
        ("Alpha Vantage API", test_alpha_vantage),
        ("News API", test_news_api),
        ("Yahoo Finance", test_yahoo_finance),
        ("Data Collectors", test_data_collectors)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1
        print()
    
    print("=" * 45)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All data sources are working!")
        print("\nYou can now run:")
        print("  python start_with_real_data.py")
        print("\nThis will start collecting real market data and news!")
        return 0
    else:
        print("⚠️  Some data sources have issues")
        print("The platform will still work with available data sources")
        return 1

if __name__ == "__main__":
    sys.exit(main())