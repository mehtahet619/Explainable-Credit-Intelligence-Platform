#!/usr/bin/env python3
"""
Monitor CredTech Platform data collection in real-time
"""

import os
import sys
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_dashboard_data():
    """Get dashboard data from API"""
    try:
        response = requests.get("http://localhost:8000/dashboard", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_companies_data():
    """Get companies data from API"""
    try:
        response = requests.get("http://localhost:8000/companies", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def display_status():
    """Display the current status"""
    clear_screen()
    
    print("🚀 CredTech Platform - Real-Time Data Collection Monitor")
    print("=" * 65)
    print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check API health
    api_healthy = check_api_health()
    status_icon = "✅" if api_healthy else "❌"
    print(f"{status_icon} API Server: {'Running' if api_healthy else 'Not responding'}")
    
    if not api_healthy:
        print("\n❌ API server is not running!")
        print("Please start the platform with: python start_with_real_data.py")
        return
    
    # Get data
    dashboard_data = get_dashboard_data()
    companies = get_companies_data()
    
    if dashboard_data:
        print(f"✅ Database: Connected")
        print(f"📊 Total Companies: {dashboard_data.get('total_companies', 0)}")
        print(f"🚨 Active Alerts: {len(dashboard_data.get('alerts', []))}")
        
        # Display companies and their latest scores
        print("\n📈 Company Credit Scores:")
        print("-" * 50)
        
        companies_data = dashboard_data.get('companies', [])
        if companies_data:
            for company in companies_data[:10]:  # Show first 10
                score = company.get('current_score', 0)
                confidence = company.get('confidence', 0)
                last_updated = company.get('last_updated', '')
                
                # Format last updated time
                try:
                    if last_updated:
                        dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                        time_str = dt.strftime('%H:%M:%S')
                    else:
                        time_str = 'N/A'
                except:
                    time_str = 'N/A'
                
                # Color code the score
                if score >= 750:
                    score_icon = "🟢"
                elif score >= 650:
                    score_icon = "🟡"
                else:
                    score_icon = "🔴"
                
                print(f"{score_icon} {company.get('symbol', 'N/A'):6} | {score:6.1f} | {confidence:5.1f}% | {time_str}")
        else:
            print("No company data available")
        
        # Display alerts
        alerts = dashboard_data.get('alerts', [])
        if alerts:
            print(f"\n🚨 Recent Alerts ({len(alerts)}):")
            print("-" * 40)
            for alert in alerts[:5]:  # Show first 5 alerts
                symbol = alert.get('company_symbol', 'N/A')
                change = alert.get('score_change', 0)
                severity = alert.get('severity', 'medium')
                
                severity_icon = "🔴" if severity == 'high' else "🟡"
                change_str = f"+{change:.1f}" if change > 0 else f"{change:.1f}"
                
                print(f"{severity_icon} {symbol:6} | {change_str:8} points | {severity.upper()}")
        
    else:
        print("❌ Database: No data available")
    
    # Display data source status
    print(f"\n🔌 Data Sources:")
    print("-" * 30)
    
    load_dotenv()
    alpha_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    news_key = os.getenv('NEWS_API_KEY')
    
    alpha_status = "✅ Active" if alpha_key and alpha_key != 'demo' else "⚠️  Not configured"
    news_status = "✅ Active" if news_key and news_key != 'demo' else "⚠️  Not configured"
    
    print(f"Alpha Vantage: {alpha_status}")
    print(f"News API:      {news_status}")
    print(f"Yahoo Finance: ✅ Active (Free)")
    print(f"SEC EDGAR:     ✅ Active (Free)")
    
    print(f"\n📊 System Status:")
    print("-" * 20)
    print("🔄 Data collection running every 5-15 minutes")
    print("🧠 ML pipeline generating scores every 10 minutes")
    print("📈 Real-time updates in dashboard")
    
    print(f"\n🌐 Access URLs:")
    print("-" * 20)
    print("Frontend:  http://localhost:3000")
    print("API:       http://localhost:8000")
    print("API Docs:  http://localhost:8000/docs")
    
    print(f"\nPress Ctrl+C to stop monitoring")

def main():
    """Main monitoring loop"""
    try:
        while True:
            display_status()
            time.sleep(10)  # Update every 10 seconds
    except KeyboardInterrupt:
        clear_screen()
        print("👋 Monitoring stopped")

if __name__ == "__main__":
    main()