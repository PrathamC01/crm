#!/usr/bin/env python3
"""
Database migration script to add validation columns for hot/cold lead classification
"""

import sqlite3
import os

def add_validation_columns():
    """Add employee_count and lead_status columns to companies table"""
    print("🔄 Adding validation columns to companies table...")
    
    db_path = "/app/backend/crm_database.db"
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(companies)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        # Add employee_count column if it doesn't exist
        if 'employee_count' not in existing_columns:
            cursor.execute("ALTER TABLE companies ADD COLUMN employee_count INTEGER")
            print("   ✅ Added employee_count column")
        else:
            print("   ℹ️  employee_count column already exists")
        
        # Add lead_status column if it doesn't exist
        if 'lead_status' not in existing_columns:
            cursor.execute("ALTER TABLE companies ADD COLUMN lead_status VARCHAR(4) DEFAULT 'COLD'")
            print("   ✅ Added lead_status column")
        else:
            print("   ℹ️  lead_status column already exists")
        
        # Update existing companies to have default lead_status if NULL
        cursor.execute("UPDATE companies SET lead_status = 'COLD' WHERE lead_status IS NULL")
        updated_count = cursor.rowcount
        if updated_count > 0:
            print(f"   ✅ Updated {updated_count} companies with default COLD status")
        
        conn.commit()
        conn.close()
        
        print("✅ Successfully added validation columns to companies table")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

def main():
    """Run the migration"""
    print("🚀 Starting database migration: Add Validation Columns")
    success = add_validation_columns()
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)