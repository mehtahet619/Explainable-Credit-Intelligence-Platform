from sqlalchemy import Column, Integer, String, DateTime, Decimal, Boolean, ForeignKey, BigInteger, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://credtech_user:credtech_pass@localhost:5432/credtech")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
from datetime import datetime

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, index=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(100))
    industry = Column(String(100))
    market_cap = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    credit_scores = relationship("CreditScore", back_populates="company")
    feature_importance = relationship("FeatureImportance", back_populates="company")
    news_events = relationship("NewsEvent", back_populates="company")

class CreditScore(Base):
    __tablename__ = "credit_scores"
    
    time = Column(DateTime, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), primary_key=True)
    score = Column(Decimal(5,2), nullable=False)
    confidence = Column(Decimal(5,2))
    model_version = Column(String(50))
    
    # Relationships
    company = relationship("Company", back_populates="credit_scores")

class FeatureImportance(Base):
    __tablename__ = "feature_importance"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    timestamp = Column(DateTime, nullable=False)
    feature_name = Column(String(100), nullable=False)
    importance_value = Column(Decimal(10,6), nullable=False)
    shap_value = Column(Decimal(10,6))
    feature_value = Column(Decimal(15,6))
    
    # Relationships
    company = relationship("Company", back_populates="feature_importance")

class FinancialData(Base):
    __tablename__ = "financial_data"
    
    time = Column(DateTime, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), primary_key=True)
    metric_name = Column(String(100), primary_key=True)
    value = Column(Decimal(20,6))
    source = Column(String(50))

class NewsEvent(Base):
    __tablename__ = "news_events"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    timestamp = Column(DateTime, nullable=False)
    headline = Column(Text, nullable=False)
    content = Column(Text)
    source = Column(String(100))
    sentiment_score = Column(Decimal(5,2))
    impact_score = Column(Decimal(5,2))
    event_type = Column(String(50))
    processed = Column(Boolean, default=False)
    
    # Relationships
    company = relationship("Company", back_populates="news_events")

class MarketData(Base):
    __tablename__ = "market_data"
    
    time = Column(DateTime, primary_key=True)
    symbol = Column(String(10), primary_key=True)
    open_price = Column(Decimal(15,6))
    high_price = Column(Decimal(15,6))
    low_price = Column(Decimal(15,6))
    close_price = Column(Decimal(15,6))
    volume = Column(BigInteger)

class ModelPerformance(Base):
    __tablename__ = "model_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    model_version = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    accuracy = Column(Decimal(5,4))
    precision_score = Column(Decimal(5,4))
    recall = Column(Decimal(5,4))
    f1_score = Column(Decimal(5,4))
    training_samples = Column(Integer)
    validation_samples = Column(Integer)

class DataSourceStatus(Base):
    __tablename__ = "data_source_status"
    
    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(100), nullable=False)
    last_update = Column(DateTime)
    status = Column(String(20), default='active')
    error_count = Column(Integer, default=0)
    last_error = Column(Text)