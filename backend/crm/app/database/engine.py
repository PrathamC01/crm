"""
SQLAlchemy engine and session configuration
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Database URL from environment with SQLite fallback for local development
DATABASE_URL = os.getenv('POSTGRES_URL')

# If PostgreSQL is not available, use SQLite for local development
if not DATABASE_URL or 'localhost:5432' in DATABASE_URL:
    # Use SQLite for local development
    DATABASE_URL = 'sqlite:///./crm_database.db'
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Only for SQLite
        echo=False  # Set to True for SQL debugging
    )
else:
    # Use PostgreSQL for production
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False  # Set to True for SQL debugging
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)