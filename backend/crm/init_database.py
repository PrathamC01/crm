#!/usr/bin/env python3
"""
Standalone database initialization script
Run this to set up the database with all tables and initial data
"""
import sys
import os

# Add the crm app to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.database.init_db import init_database

if __name__ == "__main__":
    print("🚀 Starting database initialization...")
    try:
        init_database()
        print("✅ Database initialization completed successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)