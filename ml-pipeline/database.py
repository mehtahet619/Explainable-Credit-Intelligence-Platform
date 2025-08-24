from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///data/credtech.db")
        
        if "sqlite" in self.database_url:
            # SQLite configuration
            self.engine = create_engine(self.database_url, connect_args={"check_same_thread": False})
        else:
            # PostgreSQL configuration
            self.engine = create_engine(self.database_url)
            
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self):
        return self.SessionLocal()
    
    def get_all_companies(self) -> List[Dict]:
        """Get all companies from database"""
        with self.get_session() as session:
            result = session.execute(text("SELECT id, symbol, name FROM companies"))
            return [{"id": row[0], "symbol": row[1], "name": row[2]} for row in result]
    
    def get_company_info(self, company_id: int) -> Optional[Dict]:
        """Get company information"""
        with self.get_session() as session:
            result = session.execute(
                text("SELECT id, symbol, name, sector, industry, market_cap FROM companies WHERE id = :company_id"),
                {"company_id": company_id}
            )
            row = result.fetchone()
            if row:
                return {
                    "id": row[0],
                    "symbol": row[1],
                    "name": row[2],
                    "sector": row[3],
                    "industry": row[4],
                    "market_cap": row[5]
                }
            return None
    
    def get_recent_financial_data(self, company_id: int, days: int = 30) -> List[Dict]:
        """Get recent financial data for a company"""
        with self.get_session() as session:
            result = session.execute(
                text("""
                    SELECT metric_name, value, time, source
                    FROM financial_data
                    WHERE company_id = :company_id
                    AND time >= :start_date
                    ORDER BY time DESC
                """),
                {
                    "company_id": company_id,
                    "start_date": datetime.utcnow() - timedelta(days=days)
                }
            )
            return [
                {
                    "metric_name": row[0],
                    "value": float(row[1]) if row[1] else None,
                    "time": row[2],
                    "source": row[3]
                }
                for row in result
            ]
    
    def get_recent_market_data(self, symbol: str, days: int = 30) -> List[Dict]:
        """Get recent market data for a symbol"""
        with self.get_session() as session:
            result = session.execute(
                text("""
                    SELECT time, open_price, high_price, low_price, close_price, volume
                    FROM market_data
                    WHERE symbol = :symbol
                    AND time >= :start_date
                    ORDER BY time ASC
                """),
                {
                    "symbol": symbol,
                    "start_date": datetime.utcnow() - timedelta(days=days)
                }
            )
            return [
                {
                    "time": row[0],
                    "open_price": float(row[1]) if row[1] else None,
                    "high_price": float(row[2]) if row[2] else None,
                    "low_price": float(row[3]) if row[3] else None,
                    "close_price": float(row[4]) if row[4] else None,
                    "volume": int(row[5]) if row[5] else None
                }
                for row in result
            ]
    
    def get_recent_news_events(self, company_id: int, days: int = 7) -> List[Dict]:
        """Get recent news events for a company"""
        with self.get_session() as session:
            result = session.execute(
                text("""
                    SELECT timestamp, headline, sentiment_score, impact_score, event_type, source
                    FROM news_events
                    WHERE company_id = :company_id
                    AND timestamp >= :start_date
                    ORDER BY timestamp DESC
                """),
                {
                    "company_id": company_id,
                    "start_date": datetime.utcnow() - timedelta(days=days)
                }
            )
            return [
                {
                    "timestamp": row[0],
                    "headline": row[1],
                    "sentiment_score": float(row[2]) if row[2] else 50.0,
                    "impact_score": float(row[3]) if row[3] else 30.0,
                    "event_type": row[4] or 'general',
                    "source": row[5]
                }
                for row in result
            ]
    
    def insert_credit_score(self, data: Dict):
        """Insert credit score"""
        try:
            with self.get_session() as session:
                # Check if record exists
                existing = session.execute(
                    text("SELECT id FROM credit_scores WHERE time = :time AND company_id = :company_id"),
                    {"time": data["time"], "company_id": data["company_id"]}
                ).fetchone()
                
                if existing:
                    # Update existing record
                    session.execute(
                        text("""
                            UPDATE credit_scores 
                            SET score = :score, confidence = :confidence, model_version = :model_version
                            WHERE time = :time AND company_id = :company_id
                        """),
                        data
                    )
                else:
                    # Insert new record
                    session.execute(
                        text("""
                            INSERT INTO credit_scores (time, company_id, score, confidence, model_version)
                            VALUES (:time, :company_id, :score, :confidence, :model_version)
                        """),
                        data
                    )
                session.commit()
        except Exception as e:
            logger.error(f"Error inserting credit score: {e}")
    
    def insert_feature_importance(self, data: Dict):
        """Insert feature importance"""
        try:
            with self.get_session() as session:
                session.execute(
                    text("""
                        INSERT INTO feature_importance 
                        (company_id, timestamp, feature_name, importance_value, shap_value, feature_value)
                        VALUES (:company_id, :timestamp, :feature_name, :importance_value, :shap_value, :feature_value)
                    """),
                    data
                )
                session.commit()
        except Exception as e:
            logger.error(f"Error inserting feature importance: {e}")
    
    def insert_model_performance(self, data: Dict):
        """Insert model performance metrics"""
        try:
            with self.get_session() as session:
                session.execute(
                    text("""
                        INSERT INTO model_performance 
                        (model_version, timestamp, accuracy, precision_score, recall, f1_score, training_samples, validation_samples)
                        VALUES (:model_version, :timestamp, :accuracy, :precision_score, :recall, :f1_score, :training_samples, :validation_samples)
                    """),
                    data
                )
                session.commit()
        except Exception as e:
            logger.error(f"Error inserting model performance: {e}")
    
    def get_latest_credit_scores(self) -> List[Dict]:
        """Get latest credit scores for all companies"""
        with self.get_session() as session:
            result = session.execute(
                text("""
                    SELECT cs.company_id, cs.score, cs.confidence, cs.time, cs.model_version,
                           c.symbol, c.name, c.sector
                    FROM credit_scores cs
                    JOIN companies c ON cs.company_id = c.id
                    WHERE cs.time = (
                        SELECT MAX(time) 
                        FROM credit_scores cs2 
                        WHERE cs2.company_id = cs.company_id
                    )
                    ORDER BY cs.company_id
                """)
            )
            return [
                {
                    "company_id": row[0],
                    "score": float(row[1]) if row[1] else None,
                    "confidence": float(row[2]) if row[2] else None,
                    "time": row[3],
                    "model_version": row[4],
                    "symbol": row[5],
                    "name": row[6],
                    "sector": row[7]
                }
                for row in result
            ]