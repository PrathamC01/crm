"""
Database dependencies using SQLAlchemy
"""
from fastapi import Depends
from sqlalchemy.orm import Session
from ..database import get_db
from pymongo import MongoClient
from ..config import settings

# MongoDB connection
mongo_client = None
mongo_db = None

def init_mongodb():
    """Initialize MongoDB connection"""
    global mongo_client, mongo_db
    
    try:
        mongo_client = MongoClient(settings.MONGO_URL)
        mongo_db = mongo_client.crm_logs
        # Test connection
        mongo_client.admin.command('ping')
        print("✅ MongoDB connected successfully")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")

def close_mongodb():
    """Close MongoDB connection"""
    global mongo_client
    
    if mongo_client:
        mongo_client.close()
        print("📴 MongoDB connection closed")

def get_mongo_db():
    """Get MongoDB database"""
    if mongo_db is None:
        raise Exception("MongoDB not initialized")
    return mongo_db

# PostgreSQL dependency
def get_postgres_db(db: Session = Depends(get_db)):
    """Get PostgreSQL database session"""
    return db