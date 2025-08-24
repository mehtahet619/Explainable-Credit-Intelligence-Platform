import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class FeatureEngineer:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def extract_features(self, company_id: int) -> Optional[pd.DataFrame]:
        """Extract features for a specific company"""
        try:
            # Get financial data
            financial_features = self._extract_financial_features(company_id)
            
            # Get market data features
            market_features = self._extract_market_features(company_id)
            
            # Get news sentiment features
            sentiment_features = self._extract_sentiment_features(company_id)
            
            # Get technical indicators
            technical_features = self._extract_technical_features(company_id)
            
            # Combine all features
            all_features = {**financial_features, **market_features, **sentiment_features, **technical_features}
            
            if not all_features:
                return None
            
            # Convert to DataFrame
            features_df = pd.DataFrame([all_features])
            
            # Handle missing values
            features_df = features_df.fillna(0)
            
            return features_df
            
        except Exception as e:
            logger.error(f"Error extracting features for company {company_id}: {e}")
            return None
    
    def _extract_financial_features(self, company_id: int) -> Dict:
        """Extract financial ratio and fundamental features"""
        features = {}
        
        try:
            # Get recent financial data (last 90 days)
            financial_data = self.db.get_recent_financial_data(company_id, days=90)
            
            if not financial_data:
                return self._get_default_financial_features()
            
            # Convert to DataFrame for easier processing
            df = pd.DataFrame(financial_data)
            
            # Get latest values for each metric
            latest_metrics = df.groupby('metric_name')['value'].last()
            
            # Financial ratios
            features['debt_to_equity'] = latest_metrics.get('debt_to_equity', 0)
            features['current_ratio'] = latest_metrics.get('current_ratio', 1)
            features['pe_ratio'] = latest_metrics.get('pe_ratio', 15)
            features['roe'] = latest_metrics.get('roe', 0.1)
            features['revenue_growth'] = latest_metrics.get('revenue_growth', 0)
            
            # Size metrics
            features['market_cap'] = latest_metrics.get('market_cap', 1000000000)
            features['total_revenue'] = latest_metrics.get('total_revenue', 1000000000)
            features['total_assets'] = latest_metrics.get('total_assets', 1000000000)
            
            # Profitability metrics
            features['gross_profit'] = latest_metrics.get('gross_profit', 100000000)
            features['net_income'] = latest_metrics.get('net_income', 50000000)
            features['ebitda'] = latest_metrics.get('ebitda', 100000000)
            
            # Calculate derived ratios
            if features['total_revenue'] > 0:
                features['profit_margin'] = features['net_income'] / features['total_revenue']
                features['gross_margin'] = features['gross_profit'] / features['total_revenue']
            else:
                features['profit_margin'] = 0
                features['gross_margin'] = 0
            
            if features['total_assets'] > 0:
                features['asset_turnover'] = features['total_revenue'] / features['total_assets']
            else:
                features['asset_turnover'] = 0
            
            # Normalize large values (log transformation)
            for metric in ['market_cap', 'total_revenue', 'total_assets', 'gross_profit', 'net_income', 'ebitda']:
                if features[metric] > 0:
                    features[f'log_{metric}'] = np.log(features[metric])
                else:
                    features[f'log_{metric}'] = 0
            
        except Exception as e:
            logger.error(f"Error extracting financial features: {e}")
            features = self._get_default_financial_features()
        
        return features
    
    def _extract_market_features(self, company_id: int) -> Dict:
        """Extract market-based features"""
        features = {}
        
        try:
            # Get company symbol
            company_info = self.db.get_company_info(company_id)
            if not company_info:
                return self._get_default_market_features()
            
            symbol = company_info['symbol']
            
            # Get recent market data
            market_data = self.db.get_recent_market_data(symbol, days=30)
            
            if not market_data:
                return self._get_default_market_features()
            
            df = pd.DataFrame(market_data)
            df['time'] = pd.to_datetime(df['time'])
            df = df.sort_values('time')
            
            # Price features
            features['current_price'] = df['close_price'].iloc[-1]
            features['price_change_1d'] = (df['close_price'].iloc[-1] - df['close_price'].iloc[-2]) / df['close_price'].iloc[-2] if len(df) > 1 else 0
            features['price_change_7d'] = (df['close_price'].iloc[-1] - df['close_price'].iloc[-7]) / df['close_price'].iloc[-7] if len(df) > 7 else 0
            features['price_change_30d'] = (df['close_price'].iloc[-1] - df['close_price'].iloc[0]) / df['close_price'].iloc[0] if len(df) > 1 else 0
            
            # Volatility features
            df['returns'] = df['close_price'].pct_change()
            features['volatility_7d'] = df['returns'].tail(7).std() if len(df) > 7 else 0
            features['volatility_30d'] = df['returns'].std() if len(df) > 1 else 0
            
            # Volume features
            features['avg_volume_7d'] = df['volume'].tail(7).mean() if len(df) > 7 else 0
            features['avg_volume_30d'] = df['volume'].mean() if len(df) > 1 else 0
            features['volume_trend'] = (df['volume'].tail(7).mean() / df['volume'].head(7).mean()) - 1 if len(df) > 14 else 0
            
            # Technical indicators
            features['rsi'] = self._calculate_rsi(df['close_price'])
            features['moving_avg_ratio'] = df['close_price'].iloc[-1] / df['close_price'].tail(20).mean() if len(df) > 20 else 1
            
        except Exception as e:
            logger.error(f"Error extracting market features: {e}")
            features = self._get_default_market_features()
        
        return features
    
    def _extract_sentiment_features(self, company_id: int) -> Dict:
        """Extract news sentiment and event-based features"""
        features = {}
        
        try:
            # Get recent news events
            news_events = self.db.get_recent_news_events(company_id, days=7)
            
            if not news_events:
                return self._get_default_sentiment_features()
            
            df = pd.DataFrame(news_events)
            
            # Sentiment features
            features['avg_sentiment_7d'] = df['sentiment_score'].mean()
            features['sentiment_trend'] = df['sentiment_score'].tail(3).mean() - df['sentiment_score'].head(3).mean() if len(df) > 6 else 0
            features['sentiment_volatility'] = df['sentiment_score'].std()
            
            # Impact features
            features['avg_impact_7d'] = df['impact_score'].mean()
            features['max_impact_7d'] = df['impact_score'].max()
            features['high_impact_events'] = len(df[df['impact_score'] > 70])
            
            # Event type features
            event_types = df['event_type'].value_counts()
            features['financial_events'] = event_types.get('financial', 0)
            features['legal_events'] = event_types.get('legal', 0)
            features['management_events'] = event_types.get('management', 0)
            features['corporate_action_events'] = event_types.get('corporate_action', 0)
            
            # News frequency
            features['news_frequency_7d'] = len(df)
            
        except Exception as e:
            logger.error(f"Error extracting sentiment features: {e}")
            features = self._get_default_sentiment_features()
        
        return features
    
    def _extract_technical_features(self, company_id: int) -> Dict:
        """Extract technical analysis features"""
        features = {}
        
        try:
            # Get company info for sector/industry
            company_info = self.db.get_company_info(company_id)
            
            if company_info:
                # Sector encoding (simplified)
                sector_mapping = {
                    'Technology': 1,
                    'Financial Services': 2,
                    'Healthcare': 3,
                    'Consumer Cyclical': 4,
                    'Consumer Defensive': 5,
                    'Energy': 6,
                    'Utilities': 7,
                    'Real Estate': 8,
                    'Materials': 9,
                    'Industrials': 10
                }
                
                features['sector_code'] = sector_mapping.get(company_info.get('sector', ''), 0)
                features['market_cap_log'] = np.log(company_info.get('market_cap', 1000000000))
            else:
                features['sector_code'] = 0
                features['market_cap_log'] = 20  # Default log value
            
            # Time-based features
            now = datetime.utcnow()
            features['day_of_week'] = now.weekday()
            features['month'] = now.month
            features['quarter'] = (now.month - 1) // 3 + 1
            
        except Exception as e:
            logger.error(f"Error extracting technical features: {e}")
            features = {'sector_code': 0, 'market_cap_log': 20, 'day_of_week': 0, 'month': 1, 'quarter': 1}
        
        return features
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> float:
        """Calculate Relative Strength Index"""
        try:
            if len(prices) < window + 1:
                return 50.0  # Neutral RSI
            
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0
        except:
            return 50.0
    
    def _get_default_financial_features(self) -> Dict:
        """Return default financial features when data is not available"""
        return {
            'debt_to_equity': 0.5,
            'current_ratio': 1.2,
            'pe_ratio': 15.0,
            'roe': 0.1,
            'revenue_growth': 0.05,
            'market_cap': 1000000000,
            'total_revenue': 1000000000,
            'total_assets': 1000000000,
            'gross_profit': 200000000,
            'net_income': 50000000,
            'ebitda': 150000000,
            'profit_margin': 0.05,
            'gross_margin': 0.2,
            'asset_turnover': 1.0,
            'log_market_cap': 20.7,
            'log_total_revenue': 20.7,
            'log_total_assets': 20.7,
            'log_gross_profit': 19.1,
            'log_net_income': 17.7,
            'log_ebitda': 18.8
        }
    
    def _get_default_market_features(self) -> Dict:
        """Return default market features when data is not available"""
        return {
            'current_price': 100.0,
            'price_change_1d': 0.0,
            'price_change_7d': 0.0,
            'price_change_30d': 0.0,
            'volatility_7d': 0.02,
            'volatility_30d': 0.02,
            'avg_volume_7d': 1000000,
            'avg_volume_30d': 1000000,
            'volume_trend': 0.0,
            'rsi': 50.0,
            'moving_avg_ratio': 1.0
        }
    
    def _get_default_sentiment_features(self) -> Dict:
        """Return default sentiment features when data is not available"""
        return {
            'avg_sentiment_7d': 50.0,
            'sentiment_trend': 0.0,
            'sentiment_volatility': 5.0,
            'avg_impact_7d': 30.0,
            'max_impact_7d': 50.0,
            'high_impact_events': 0,
            'financial_events': 0,
            'legal_events': 0,
            'management_events': 0,
            'corporate_action_events': 0,
            'news_frequency_7d': 0
        }
    
    def prepare_training_data(self) -> Optional[pd.DataFrame]:
        """Prepare training data for model retraining"""
        try:
            # Get all companies
            companies = self.db.get_all_companies()
            
            training_data = []
            
            for company in companies:
                company_id = company['id']
                
                # Extract features
                features = self.extract_features(company_id)
                
                if features is not None:
                    # Generate synthetic target score for training
                    # In a real scenario, you'd have historical credit ratings or default data
                    target_score = self._generate_synthetic_target(features.iloc[0])
                    
                    feature_row = features.iloc[0].to_dict()
                    feature_row['target_score'] = target_score
                    
                    training_data.append(feature_row)
            
            if training_data:
                return pd.DataFrame(training_data)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            return None
    
    def _generate_synthetic_target(self, features: pd.Series) -> float:
        """Generate synthetic target score for training (placeholder)"""
        # This is a simplified synthetic target generation
        # In practice, you'd use historical credit ratings or default probabilities
        
        base_score = 0.6  # Base creditworthiness
        
        # Adjust based on financial health
        if features.get('debt_to_equity', 0) > 1.0:
            base_score -= 0.1
        if features.get('current_ratio', 1) < 1.0:
            base_score -= 0.1
        if features.get('roe', 0) > 0.15:
            base_score += 0.1
        
        # Adjust based on market performance
        if features.get('price_change_30d', 0) < -0.2:
            base_score -= 0.1
        if features.get('volatility_30d', 0) > 0.05:
            base_score -= 0.05
        
        # Adjust based on sentiment
        sentiment = features.get('avg_sentiment_7d', 50)
        if sentiment < 40:
            base_score -= 0.1
        elif sentiment > 60:
            base_score += 0.05
        
        # Add some noise
        noise = np.random.normal(0, 0.05)
        base_score += noise
        
        # Ensure score is between 0 and 1
        return max(0.1, min(0.9, base_score))