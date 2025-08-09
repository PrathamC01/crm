"""
SQLAlchemy engine and session configuration
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Database URL from environment
DATABASE_URL = os.getenv('POSTGRES_URL')

if not DATABASE_URL:
    raise ValueError("POSTGRES_URL environment variable is required")

print(f"Using database: {DATABASE_URL}")

# Check if we're using SQLite or PostgreSQL
if DATABASE_URL.startswith('sqlite'):
    print("⚠️  Using SQLite database")
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Only for SQLite
        echo=False  # Set to True for SQL debugging
    )
else:
    print("✅ Using PostgreSQL database")
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