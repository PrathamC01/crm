#!/usr/bin/env python3
"""
Verify database setup and show table information
"""
import sys
import os

# Add the crm app to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.database.engine import engine
from sqlalchemy import inspect

if __name__ == "__main__":
    print("🔍 Verifying database setup...")
    
    try:
        # Get database inspector
        inspector = inspect(engine)
        
        # Get all table names
        table_names = inspector.get_table_names()
        print(f"\n📋 Found {len(table_names)} tables:")
        for table in sorted(table_names):
            print(f"  ✅ {table}")
        
        # Check if key tables exist
        required_tables = ['users', 'roles', 'departments', 'companies', 'contacts', 'leads', 'opportunities']
        missing_tables = [t for t in required_tables if t not in table_names]
        
        if missing_tables:
            print(f"\n❌ Missing required tables: {missing_tables}")
        else:
            print(f"\n✅ All required tables present!")
        
        # Check sample data
        from app.database.engine import SessionLocal
        from app.models import User, Role, Company, Lead, Opportunity
        
        db = SessionLocal()
        try:
            user_count = db.query(User).count()
            role_count = db.query(Role).count()
            company_count = db.query(Company).count()
            
            print(f"\n📊 Sample data counts:")
            print(f"  👤 Users: {user_count}")
            print(f"  👥 Roles: {role_count}")
            print(f"  🏢 Companies: {company_count}")
            
        finally:
            db.close()
            
        print(f"\n✅ Database verification completed successfully!")
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)