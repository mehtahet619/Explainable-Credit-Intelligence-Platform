import schedule
import time
import logging
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
                self.yahoo_collector.collect_stock_data(company['symbol'])
                time.sleep(1)  # Rate limiting
                
            logger.info("Market data collection completed")
        except Exception as e:
            logger.error(f"Error in market data collection: {e}")
    
    def collect_financial_data(self):
        """Collect financial data from Alpha Vantage"""
        try:
            logger.info("Starting financial data collection...")
            companies = self.db.get_all_companies()
            
            for company in companies:
                self.alpha_vantage_collector.collect_financial_data(company['symbol'])
                time.sleep(12)  # Alpha Vantage rate limit: 5 calls per minute
                
            logger.info("Financial data collection completed")
        except Exception as e:
            logger.error(f"Error in financial data collection: {e}")
    
    def collect_news_data(self):
        """Collect news and sentiment data"""
        try:
            logger.info("Starting news data collection...")
            companies = self.db.get_all_companies()
            
            for company in companies:
                self.news_collector.collect_company_news(company['symbol'], company['name'])
                time.sleep(2)  # Rate limiting
                
            logger.info("News data collection completed")
        except Exception as e:
            logger.error(f"Error in news data collection: {e}")
    
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