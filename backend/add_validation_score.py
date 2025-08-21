#!/usr/bin/env python3
"""
Add validation_score column to companies table
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'crm'))

from sqlalchemy import text
from app.database.engine import engine

def add_validation_score_column():
    """Add validation_score column to companies table"""
    
    try:
        with engine.connect() as conn:
            # Check if column already exists (SQLite version)
            result = conn.execute(text("""
                PRAGMA table_info(companies)
            """))
            
            columns = [row[1] for row in result.fetchall()]
            if 'validation_score' in columns:
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