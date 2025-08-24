#!/usr/bin/env python3
"""
Database initialization script that works with both PostgreSQL and SQLite
"""

import os
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with appropriate schema"""
    database_url = os.getenv("DATABASE_URL", "sqlite:///data/credtech.db")
    
    # Create data directory if using SQLite
    if "sqlite" in database_url:
        os.makedirs("data", exist_ok=True)
        schema_file = "database/init_sqlite.sql"
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
    else:
        schema_file = "database/init.sql"
        engine = create_engine(database_url)
    
    logger.info(f"Initializing database with {database_url}")
    logger.info(f"Using schema file: {schema_file}")
    
    try:
        # Read and execute schema
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        with engine.connect() as conn:
            for statement in statements:
                try:
                    conn.execute(text(statement))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Statement failed (might be expected): {e}")
                    continue
        
        logger.info("Database initialized successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    exit(0 if success else 1)