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
    
    def get_company_id(self, symbol: str) -> Optional[int]:
        """Get company ID by symbol"""
        with self.get_session() as session:
            result = session.execute(
                text("SELECT id FROM companies WHERE symbol = :symbol"),
                {"symbol": symbol}
            )
            row = result.fetchone()
            return row[0] if row else None
    
    def insert_market_data(self, data: Dict):
        """Insert market data"""
        try:
            with self.get_session() as session:
                # Check if record exists
                existing = session.execute(
                    text("SELECT id FROM market_data WHERE time = :time AND symbol = :symbol"),
                    {"time": data["time"], "symbol": data["symbol"]}
                ).fetchone()
                
                if existing:
                    # Update existing record
                    session.execute(
                        text("""
                            UPDATE market_data 
                            SET open_price = :open_price, high_price = :high_price, 
                                low_price = :low_price, close_price = :close_price, volume = :volume
                            WHERE time = :time AND symbol = :symbol
                        """),
                        data
                    )
                else:
                    # Insert new record
                    session.execute(
                        text("""
                            INSERT INTO market_data (time, symbol, open_price, high_price, low_price, close_price, volume)
                            VALUES (:time, :symbol, :open_price, :high_price, :low_price, :close_price, :volume)
                        """),
                        data
                    )
                session.commit()
        except Exception as e:
            logger.error(f"Error inserting market data: {e}")
    
    def insert_financial_data(self, data: Dict):
        """Insert financial data"""
        try:
            with self.get_session() as session:
                # Check if record exists
                existing = session.execute(
                    text("SELECT id FROM financial_data WHERE time = :time AND company_id = :company_id AND metric_name = :metric_name"),
                    {"time": data["time"], "company_id": data["company_id"], "metric_name": data["metric_name"]}
                ).fetchone()
                
                if existing:
                    # Update existing record
                    session.execute(
                        text("""
                            UPDATE financial_data 
                            SET value = :value, source = :source
                            WHERE time = :time AND company_id = :company_id AND metric_name = :metric_name
                        """),
                        data
                    )
                else:
                    # Insert new record
                    session.execute(
                        text("""
                            INSERT INTO financial_data (time, company_id, metric_name, value, source)
                            VALUES (:time, :company_id, :metric_name, :value, :source)
                        """),
                        data
                    )
                session.commit()
        except Exception as e:
            logger.error(f"Error inserting financial data: {e}")
    
    def insert_news_event(self, data: Dict):
        """Insert news event"""
        try:
            with self.get_session() as session:
                # Check if similar news already exists (avoid duplicates)
                existing = session.execute(
                    text("""
                        SELECT id FROM news_events 
                        WHERE company_id = :company_id 
                        AND headline = :headline 
                        AND date(timestamp) = date(:timestamp)
                    """),
                    {
                        "company_id": data["company_id"],
                        "headline": data["headline"],
                        "timestamp": data["timestamp"]
                    }
                ).fetchone()
                
                if not existing:
                    session.execute(
                        text("""
                            INSERT INTO news_events 
                            (company_id, timestamp, headline, content, source, sentiment_score, impact_score, event_type)
                            VALUES (:company_id, :timestamp, :headline, :content, :source, :sentiment_score, :impact_score, :event_type)
                        """),
                        data
                    )
                    session.commit()
        except Exception as e:
            logger.error(f"Error inserting news event: {e}")
    
    def update_source_status(self, source_name: str, status: str, error: str = None):
        """Update data source status"""
        try:
            with self.get_session() as session:
                # Check if record exists
                existing = session.execute(
                    text("SELECT id FROM data_source_status WHERE source_name = :source_name"),
                    {"source_name": source_name}
                ).fetchone()
                
                if existing:
                    # Update existing record
                    session.execute(
                        text("""
                            UPDATE data_source_status 
                            SET last_update = :last_update, status = :status, last_error = :last_error,
                                error_count = CASE WHEN :status = 'error' THEN error_count + 1 ELSE 0 END
                            WHERE source_name = :source_name
                        """),
                        {
                            "source_name": source_name,
                            "last_update": datetime.utcnow(),
                            "status": status,
                            "last_error": error
                        }
                    )
                else:
                    # Insert new record
                    session.execute(
                        text("""
                            INSERT INTO data_source_status (source_name, last_update, status, last_error, error_count)
                            VALUES (:source_name, :last_update, :status, :last_error, :error_count)
                        """),
                        {
                            "source_name": source_name,
                            "last_update": datetime.utcnow(),
                            "status": status,
                            "last_error": error,
                            "error_count": 1 if status == 'error' else 0
                        }
                    )
                session.commit()
        except Exception as e:
            logger.error(f"Error updating source status: {e}")
    
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
                {"company_id": company_id, "start_date": datetime.utcnow() - timedelta(days=days)}
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