#!/usr/bin/env python3
"""
Create geographic tables manually
"""

import sys
import os
sys.path.append('/app/backend')

from backend.crm.app.database.engine import engine
from backend.crm.app.models.geographic import Country, State, City
from backend.crm.app.models.base import Base

def create_tables():
    """Create geographic tables"""
    try:
        print("🔄 Creating geographic tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Geographic tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    create_tables()