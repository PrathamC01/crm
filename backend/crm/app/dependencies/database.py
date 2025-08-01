"""
Database dependencies
"""
from fastapi import HTTPException
import asyncpg
from pymongo import MongoClient
from ..config import settings

# Global database connections
postgres_pool = None
mongo_client = None
mongo_db = None

async def init_databases():
    """Initialize database connections"""
    global postgres_pool, mongo_client, mongo_db
    
    # PostgreSQL connection
    try:
        postgres_pool = await asyncpg.create_pool(settings.POSTGRES_URL)
        print("✅ PostgreSQL connected successfully")
        
        # Create tables
        from ..models.user import User
        async with postgres_pool.acquire() as conn:
            await User.create_table(conn)
            
            # Create a default admin user for testing
            from ..utils.auth import hash_password
            admin_password = hash_password("admin123")
            await conn.execute("""
                INSERT INTO users (name, email, username, password_hash, role, department)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (email) DO NOTHING
            """, "Admin User", "admin@crm.com", "admin", admin_password, "admin", "IT")
            
            print("✅ Database tables created and admin user seeded")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
    
    # MongoDB connection
    try:
        mongo_client = MongoClient(settings.MONGO_URL)
        mongo_db = mongo_client.crm_logs
        # Test connection
        mongo_client.admin.command('ping')
        print("✅ MongoDB connected successfully")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")

async def close_databases():
    """Close database connections"""
    global postgres_pool, mongo_client
    
    if postgres_pool:
        await postgres_pool.close()
        print("📴 PostgreSQL connection closed")
    
    if mongo_client:
        mongo_client.close()
        print("📴 MongoDB connection closed")

async def get_postgres_pool():
    """Get PostgreSQL connection pool"""
    if postgres_pool is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return postgres_pool

async def get_mongo_db():
    """Get MongoDB database"""
    if mongo_db is None:
        raise HTTPException(status_code=500, detail="MongoDB not initialized")
    return mongo_db