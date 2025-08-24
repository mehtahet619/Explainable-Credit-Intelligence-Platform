#!/usr/bin/env python3
"""
Database table creation script for CredTech API
"""

from sqlalchemy import create_engine
from models import Base
import os
from dotenv import load_dotenv

def create_tables():
    """Create all database tables"""
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://credtech_user:credtech_pass@localhost:5432/credtech")
    
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    create_tables()