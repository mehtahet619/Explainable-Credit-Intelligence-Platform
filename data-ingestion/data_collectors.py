import yfinance as yf
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from textblob import TextBlob
import logging
import os
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class YahooFinanceCollector:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def collect_stock_data(self, symbol: str):
        """Collect stock price and volume data"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get recent data (last 5 days)
            hist = ticker.history(period="5d", interval="1d")
            
            for date, row in hist.iterrows():
                market_data = {
                    'time': date,
                    'symbol': symbol,
                    'open_price': float(row['Open']),
                    'high_price': float(row['High']),
                    'low_price': float(row['Low']),
                    'close_price': float(row['Close']),
                    'volume': int(row['Volume'])
                }
                self.db.insert_market_data(market_data)
            
            # Get financial metrics
            info = ticker.info
            financial_metrics = {
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'roe': info.get('returnOnEquity'),
                'revenue_growth': info.get('revenueGrowth')
            }
            
            company_id = self.db.get_company_id(symbol)
            timestamp = datetime.utcnow()
            
            for metric, value in financial_metrics.items():
                if value is not None:
                    self.db.insert_financial_data({
                        'time': timestamp,
                        'company_id': company_id,
                        'metric_name': metric,
                        'value': float(value),
                        'source': 'yahoo_finance'
                    })
                    
        except Exception as e:
            logger.error(f"Error collecting Yahoo Finance data for {symbol}: {e}")

class AlphaVantageCollector:
    def __init__(self, db_manager):
        self.db = db_manager
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.base_url = 'https://www.alphavantage.co/query'
    
    def collect_financial_data(self, symbol: str):
        """Collect fundamental financial data"""
        if not self.api_key:
            logger.warning("Alpha Vantage API key not found")
            return
            
        try:
            # Get company overview
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if 'Symbol' not in data:
                logger.warning(f"No data returned for {symbol}")
                return
            
            company_id = self.db.get_company_id(symbol)
            timestamp = datetime.utcnow()
            
            # Extract key financial metrics
            metrics = {
                'total_revenue': data.get('RevenueTTM'),
                'gross_profit': data.get('GrossProfitTTM'),
                'ebitda': data.get('EBITDA'),
                'net_income': data.get('NetIncomeTTM'),
                'total_debt': data.get('TotalDebt'),
                'total_assets': data.get('TotalAssets'),
                'book_value': data.get('BookValue'),
                'dividend_yield': data.get('DividendYield'),
                'beta': data.get('Beta')
            }
            
            for metric, value in metrics.items():
                if value and value != 'None':
                    try:
                        self.db.insert_financial_data({
                            'time': timestamp,
                            'company_id': company_id,
                            'metric_name': metric,
                            'value': float(value),
                            'source': 'alpha_vantage'
                        })
                    except ValueError:
                        continue
                        
        except Exception as e:
            logger.error(f"Error collecting Alpha Vantage data for {symbol}: {e}")

class NewsCollector:
    def __init__(self, db_manager):
        self.db = db_manager
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.base_url = 'https://newsapi.org/v2/everything'
    
    def collect_company_news(self, symbol: str, company_name: str):
        """Collect news articles and analyze sentiment"""
        try:
            # Collect from News API if available
            if self.news_api_key:
                self._collect_from_news_api(symbol, company_name)
            
            # Collect from RSS feeds (free alternative)
            self._collect_from_rss_feeds(symbol, company_name)
            
        except Exception as e:
            logger.error(f"Error collecting news for {symbol}: {e}")
    
    def _collect_from_news_api(self, symbol: str, company_name: str):
        """Collect from News API"""
        params = {
            'q': f'"{company_name}" OR "{symbol}"',
            'language': 'en',
            'sortBy': 'publishedAt',
            'from': (datetime.utcnow() - timedelta(days=1)).isoformat(),
            'apiKey': self.news_api_key
        }
        
        response = requests.get(self.base_url, params=params)
        data = response.json()
        
        if data.get('status') == 'ok':
            articles = data.get('articles', [])
            company_id = self.db.get_company_id(symbol)
            
            for article in articles[:10]:  # Limit to 10 articles
                sentiment_score = self._analyze_sentiment(article['title'] + ' ' + (article['description'] or ''))
                impact_score = self._calculate_impact_score(article['title'], sentiment_score)
                
                news_data = {
                    'company_id': company_id,
                    'timestamp': datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00')),
                    'headline': article['title'],
                    'content': article['description'],
                    'source': article['source']['name'],
                    'sentiment_score': sentiment_score,
                    'impact_score': impact_score,
                    'event_type': self._classify_event_type(article['title'])
                }
                
                self.db.insert_news_event(news_data)
    
    def _collect_from_rss_feeds(self, symbol: str, company_name: str):
        """Collect from free RSS feeds"""
        import feedparser
        
        # Google News RSS (URL encode the company name)
        import urllib.parse
        encoded_name = urllib.parse.quote(company_name)
        rss_url = f"https://news.google.com/rss/search?q={encoded_name}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            feed = feedparser.parse(rss_url)
            company_id = self.db.get_company_id(symbol)
            
            for entry in feed.entries[:5]:  # Limit to 5 articles
                sentiment_score = self._analyze_sentiment(entry.title + ' ' + entry.get('summary', ''))
                impact_score = self._calculate_impact_score(entry.title, sentiment_score)
                
                # Parse published date
                published = datetime.utcnow()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                
                news_data = {
                    'company_id': company_id,
                    'timestamp': published,
                    'headline': entry.title,
                    'content': entry.get('summary', ''),
                    'source': 'Google News',
                    'sentiment_score': sentiment_score,
                    'impact_score': impact_score,
                    'event_type': self._classify_event_type(entry.title)
                }
                
                self.db.insert_news_event(news_data)
                
        except Exception as e:
            logger.error(f"Error collecting RSS news for {symbol}: {e}")
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            # Convert polarity (-1 to 1) to score (0 to 100)
            return (blob.sentiment.polarity + 1) * 50
        except:
            return 50.0  # Neutral sentiment
    
    def _calculate_impact_score(self, headline: str, sentiment: float) -> float:
        """Calculate potential impact score based on keywords and sentiment"""
        high_impact_keywords = [
            'bankruptcy', 'acquisition', 'merger', 'lawsuit', 'investigation',
            'earnings', 'revenue', 'profit', 'loss', 'debt', 'restructuring',
            'ceo', 'resignation', 'appointed', 'partnership', 'contract'
        ]
        
        headline_lower = headline.lower()
        impact_score = 30.0  # Base impact
        
        for keyword in high_impact_keywords:
            if keyword in headline_lower:
                impact_score += 20.0
        
        # Adjust based on sentiment deviation from neutral
        sentiment_impact = abs(sentiment - 50) * 0.5
        impact_score += sentiment_impact
        
        return min(impact_score, 100.0)
    
    def _classify_event_type(self, headline: str) -> str:
        """Classify the type of event based on headline"""
        headline_lower = headline.lower()
        
        if any(word in headline_lower for word in ['earnings', 'revenue', 'profit', 'loss']):
            return 'financial'
        elif any(word in headline_lower for word in ['acquisition', 'merger', 'partnership']):
            return 'corporate_action'
        elif any(word in headline_lower for word in ['lawsuit', 'investigation', 'fine']):
            return 'legal'
        elif any(word in headline_lower for word in ['ceo', 'cfo', 'resignation', 'appointed']):
            return 'management'
        else:
            return 'general'

class SECEdgarCollector:
    def __init__(self, db_manager):
        self.db = db_manager
        self.base_url = 'https://data.sec.gov/submissions'
        self.headers = {
            'User-Agent': os.getenv('SEC_EDGAR_USER_AGENT', 'CredTech Platform contact@credtech.com')
        }
    
    def collect_filings(self, symbol: str):
        """Collect recent SEC filings"""
        try:
            # Get company CIK (Central Index Key)
            cik = self._get_company_cik(symbol)
            if not cik:
                return
            
            # Get recent filings
            url = f"{self.base_url}/CIK{cik:010d}.json"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                recent_filings = data.get('filings', {}).get('recent', {})
                
                company_id = self.db.get_company_id(symbol)
                
                # Process recent 10-K, 10-Q, 8-K filings
                forms = recent_filings.get('form', [])
                filing_dates = recent_filings.get('filingDate', [])
                
                for i, form in enumerate(forms[:10]):  # Limit to 10 recent filings
                    if form in ['10-K', '10-Q', '8-K']:
                        filing_date = datetime.strptime(filing_dates[i], '%Y-%m-%d')
                        
                        # Create a news event for the filing
                        news_data = {
                            'company_id': company_id,
                            'timestamp': filing_date,
                            'headline': f"{form} filing submitted",
                            'content': f"Company filed {form} with SEC",
                            'source': 'SEC EDGAR',
                            'sentiment_score': 50.0,  # Neutral
                            'impact_score': 60.0 if form == '10-K' else 40.0,
                            'event_type': 'regulatory'
                        }
                        
                        self.db.insert_news_event(news_data)
                        
        except Exception as e:
            logger.error(f"Error collecting SEC data for {symbol}: {e}")
    
    def _get_company_cik(self, symbol: str) -> Optional[int]:
        """Get company CIK from symbol"""
        # This is a simplified implementation
        # In practice, you'd maintain a mapping or use SEC's company tickers JSON
        cik_mapping = {
            'AAPL': 320193,
            'MSFT': 789019,
            'GOOGL': 1652044,
            'TSLA': 1318605,
            'JPM': 19617
        }
        return cik_mapping.get(symbol)