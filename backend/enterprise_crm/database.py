"""
Database configuration for Enterprise CRM
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings
from .models.base import Base

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=True if settings.DATABASE_URL.startswith("sqlite") else False
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()