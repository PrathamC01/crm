"""
SQLAlchemy engine and session configuration
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Database URL from environment with SQLite fallback for local development
DATABASE_URL = os.getenv('POSTGRES_URL')

# If no PostgreSQL URL provided, use SQLite for local development
if not DATABASE_URL:
    DATABASE_URL = 'sqlite:///./crm_database.db'
    print(f"No POSTGRES_URL found, using SQLite: {DATABASE_URL}")

# Check if we're using SQLite or PostgreSQL
if DATABASE_URL.startswith('sqlite'):
    print(f"Using SQLite database: {DATABASE_URL}")
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Only for SQLite
        echo=False  # Set to True for SQL debugging
    )
else:
    print(f"Using PostgreSQL database: {DATABASE_URL}")
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

print("✅ Database engine configured successfully")