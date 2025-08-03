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
        
        # Create tables in proper order (dependencies first)
        from ..models.role import Role
        from ..models.department import Department
        from ..models.user import User
        
        async with postgres_pool.acquire() as conn:
            # Create base tables first
            await Role.create_table(conn)
            await Department.create_table(conn)
            await User.create_table(conn)
            
            # Create business tables
            from ..models.company import Company
            from ..models.contact import Contact
            from ..models.lead import Lead
            from ..models.opportunity import Opportunity
            
            await Company.create_table(conn)
            await Contact.create_table(conn)
            await Lead.create_table(conn)
            await Opportunity.create_table(conn)
            
            # Seed admin user with proper role
            await User.seed_admin_user(conn)
            
            print("✅ Database tables created and admin user seeded")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        import traceback
        traceback.print_exc()
    
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