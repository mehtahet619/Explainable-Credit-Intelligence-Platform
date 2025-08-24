#!/usr/bin/env python3
"""
Populate CredTech database with sample data for testing
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Add the api directory to the path
sys.path.append('api')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Company, CreditScore, FeatureImportance, NewsEvent, MarketData
from dotenv import load_dotenv

def create_sample_data():
    """Create sample data for testing"""
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://credtech_user:credtech_pass@localhost:5432/credtech")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_companies = db.query(Company).count()
        if existing_companies > 0:
            print(f"Database already has {existing_companies} companies. Skipping data creation.")
            return
        
        # Sample companies
        companies_data = [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "market_cap": 3000000000000
            },
            {
                "symbol": "MSFT", 
                "name": "Microsoft Corporation",
                "sector": "Technology",
                "industry": "Software",
                "market_cap": 2800000000000
            },
            {
                "symbol": "GOOGL",
                "name": "Alphabet Inc.",
                "sector": "Technology", 
                "industry": "Internet Services",
                "market_cap": 1700000000000
            },
            {
                "symbol": "TSLA",
                "name": "Tesla Inc.",
                "sector": "Consumer Cyclical",
                "industry": "Auto Manufacturers", 
                "market_cap": 800000000000
            },
            {
                "symbol": "JPM",
                "name": "JPMorgan Chase & Co.",
                "sector": "Financial Services",
                "industry": "Banks",
                "market_cap": 450000000000
            }
        ]
        
        # Create companies
        companies = []
        for company_data in companies_data:
            company = Company(**company_data)
            db.add(company)
            companies.append(company)
        
        db.commit()
        print(f"Created {len(companies)} companies")
        
        # Create sample credit scores
        base_date = datetime.utcnow() - timedelta(days=30)
        
        for company in companies:
            # Generate scores for the last 30 days
            base_score = random.uniform(600, 800)
            
            for i in range(30):
                score_date = base_date + timedelta(days=i)
                
                # Add some random variation
                daily_change = random.uniform(-10, 10)
                score = max(300, min(850, base_score + daily_change))
                base_score = score  # Carry forward for next day
                
                credit_score = CreditScore(
                    time=score_date,
                    company_id=company.id,
                    score=Decimal(str(round(score, 2))),
                    confidence=Decimal(str(round(random.uniform(70, 95), 2))),
                    model_version="v1.0.0"
                )
                db.add(credit_score)
        
        db.commit()
        print("Created sample credit scores")
        
        # Create sample feature importance data
        feature_names = [
            "debt_to_equity", "current_ratio", "pe_ratio", "roe", "revenue_growth",
            "market_cap", "volatility_30d", "price_change_30d", "avg_sentiment_7d"
        ]
        
        for company in companies:
            for feature_name in feature_names:
                feature_importance = FeatureImportance(
                    company_id=company.id,
                    timestamp=datetime.utcnow(),
                    feature_name=feature_name,
                    importance_value=Decimal(str(round(random.uniform(0.01, 0.3), 6))),
                    shap_value=Decimal(str(round(random.uniform(-0.1, 0.1), 6))),
                    feature_value=Decimal(str(round(random.uniform(0, 100), 6)))
                )
                db.add(feature_importance)
        
        db.commit()
        print("Created sample feature importance data")
        
        # Create sample news events
        sample_headlines = [
            "Company reports strong quarterly earnings",
            "New product launch announced",
            "CEO announces strategic partnership",
            "Quarterly revenue beats expectations",
            "Company expands into new markets",
            "Strong guidance for next quarter"
        ]
        
        for company in companies:
            for i in range(3):  # 3 news events per company
                news_date = datetime.utcnow() - timedelta(days=random.randint(1, 7))
                
                news_event = NewsEvent(
                    company_id=company.id,
                    timestamp=news_date,
                    headline=random.choice(sample_headlines),
                    content=f"Sample news content for {company.name}",
                    source="Sample News",
                    sentiment_score=Decimal(str(round(random.uniform(40, 80), 2))),
                    impact_score=Decimal(str(round(random.uniform(20, 60), 2))),
                    event_type="financial"
                )
                db.add(news_event)
        
        db.commit()
        print("Created sample news events")
        
        # Create sample market data
        for company in companies:
            base_price = random.uniform(50, 300)
            
            for i in range(30):
                market_date = base_date + timedelta(days=i)
                
                # Generate OHLC data
                daily_change = random.uniform(-0.05, 0.05)
                open_price = base_price * (1 + daily_change)
                high_price = open_price * (1 + random.uniform(0, 0.03))
                low_price = open_price * (1 - random.uniform(0, 0.03))
                close_price = open_price * (1 + random.uniform(-0.02, 0.02))
                
                base_price = close_price  # Carry forward
                
                market_data = MarketData(
                    time=market_date,
                    symbol=company.symbol,
                    open_price=Decimal(str(round(open_price, 2))),
                    high_price=Decimal(str(round(high_price, 2))),
                    low_price=Decimal(str(round(low_price, 2))),
                    close_price=Decimal(str(round(close_price, 2))),
                    volume=random.randint(1000000, 10000000)
                )
                db.add(market_data)
        
        db.commit()
        print("Created sample market data")
        
        print("\n✅ Sample data created successfully!")
        print(f"Created data for {len(companies)} companies")
        print("You can now start the API server and frontend")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()