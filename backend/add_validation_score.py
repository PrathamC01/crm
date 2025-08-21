#!/usr/bin/env python3
"""
Add validation_score column to companies table
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'crm'))

from sqlalchemy import text
from app.database.init_db import get_engine

def add_validation_score_column():
    """Add validation_score column to companies table"""
    engine = get_engine()
    
    try:
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'companies' AND column_name = 'validation_score'
            """))
            
            if result.fetchone():
                print("✅ validation_score column already exists")
                return
            
            # Add the column
            conn.execute(text("""
                ALTER TABLE companies 
                ADD COLUMN validation_score INTEGER
            """))
            
            conn.commit()
            print("✅ Added validation_score column to companies table")
            
    except Exception as e:
        print(f"❌ Error adding validation_score column: {e}")
        raise

if __name__ == "__main__":
    add_validation_score_column()