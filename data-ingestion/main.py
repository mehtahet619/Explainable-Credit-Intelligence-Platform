import schedule
import time
import logging
import os
from datetime import datetime
from data_collectors import (
    YahooFinanceCollector,
    AlphaVantageCollector,
    NewsCollector,
    SECEdgarCollector
)
from database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngestionService:
    def __init__(self):
        self.db = DatabaseManager()
        self.yahoo_collector = YahooFinanceCollector(self.db)
        self.alpha_vantage_collector = AlphaVantageCollector(self.db)
        self.news_collector = NewsCollector(self.db)
        self.sec_collector = SECEdgarCollector(self.db)
        
    def collect_market_data(self):
        """Collect market data from Yahoo Finance"""
        try:
            logger.info("Starting market data collection...")
            companies = self.db.get_all_companies()
            
            for company in companies:
                try:
                    self.yahoo_collector.collect_stock_data(company['symbol'])
                    logger.info(f"Collected market data for {company['symbol']}")
                    time.sleep(1)  # Rate limiting
                except Exception as e:
                    logger.error(f"Error collecting market data for {company['symbol']}: {e}")
                    continue
                
            logger.info("Market data collection completed")
            self.update_data_source_status("yahoo_finance", "active")
        except Exception as e:
            logger.error(f"Error in market data collection: {e}")
            self.update_data_source_status("yahoo_finance", "error", str(e))
    
    def collect_financial_data(self):
        """Collect financial data from Alpha Vantage"""
        try:
            logger.info("Starting financial data collection...")
            companies = self.db.get_all_companies()
            
            # Check if Alpha Vantage API key is configured
            alpha_key = os.getenv('ALPHA_VANTAGE_API_KEY')
            if not alpha_key or alpha_key == 'demo':
                logger.warning("Alpha Vantage API key not configured, skipping financial data collection")
                return
            
            for company in companies:
                try:
                    self.alpha_vantage_collector.collect_financial_data(company['symbol'])
                    logger.info(f"Collected financial data for {company['symbol']}")
                    time.sleep(12)  # Alpha Vantage rate limit: 5 calls per minute
                except Exception as e:
                    logger.error(f"Error collecting financial data for {company['symbol']}: {e}")
                    continue
                
            logger.info("Financial data collection completed")
            self.update_data_source_status("alpha_vantage", "active")
        except Exception as e:
            logger.error(f"Error in financial data collection: {e}")
            self.update_data_source_status("alpha_vantage", "error", str(e))
    
    def collect_news_data(self):
        """Collect news and sentiment data"""
        try:
            logger.info("Starting news data collection...")
            companies = self.db.get_all_companies()
            
            # Check if News API key is configured
            news_key = os.getenv('NEWS_API_KEY')
            if not news_key or news_key == 'demo':
                logger.warning("News API key not configured, using RSS feeds only")
            
            for company in companies:
                try:
                    self.news_collector.collect_company_news(company['symbol'], company['name'])
                    logger.info(f"Collected news data for {company['symbol']}")
                    time.sleep(2)  # Rate limiting
                except Exception as e:
                    logger.error(f"Error collecting news data for {company['symbol']}: {e}")
                    continue
                
            logger.info("News data collection completed")
            self.update_data_source_status("news_api", "active")
        except Exception as e:
            logger.error(f"Error in news data collection: {e}")
            self.update_data_source_status("news_api", "error", str(e))
    
    def collect_sec_data(self):
        """Collect SEC filing data"""
        try:
            logger.info("Starting SEC data collection...")
            companies = self.db.get_all_companies()
            
            for company in companies:
                self.sec_collector.collect_filings(company['symbol'])
                time.sleep(5)  # SEC rate limiting
                
            logger.info("SEC data collection completed")
        except Exception as e:
            logger.error(f"Error in SEC data collection: {e}")
    
    def update_data_source_status(self, source_name: str, status: str, error: str = None):
        """Update data source status"""
        self.db.update_source_status(source_name, status, error)

def main():
    service = DataIngestionService()
    
    # Schedule data collection jobs
    schedule.every(5).minutes.do(service.collect_market_data)
    schedule.every(15).minutes.do(service.collect_financial_data)
    schedule.every(10).minutes.do(service.collect_news_data)
    schedule.every(1).hours.do(service.collect_sec_data)
    
    logger.info("Data ingestion service started")
    
    # Run initial collection
    service.collect_market_data()
    service.collect_news_data()
    
    # Keep the service running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()