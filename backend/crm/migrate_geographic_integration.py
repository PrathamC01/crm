"""
Migration to update company table with geographic foreign keys
"""

import sqlite3
import os
from pathlib import Path

# Database path
DB_PATH = "/app/backend/crm_database.db"

def migrate_company_table():
    """Update company table to use geographic foreign keys"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # First, check if the new columns already exist
    cursor.execute("PRAGMA table_info(companies)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Add new foreign key columns if they don't exist
    if 'country_id' not in columns:
        cursor.execute("ALTER TABLE companies ADD COLUMN country_id INTEGER REFERENCES countries(id)")
        print("✅ Added country_id column")
    
    if 'state_id' not in columns:
        cursor.execute("ALTER TABLE companies ADD COLUMN state_id INTEGER REFERENCES states(id)")
        print("✅ Added state_id column")
        
    if 'city_id' not in columns:
        cursor.execute("ALTER TABLE companies ADD COLUMN city_id INTEGER REFERENCES cities(id)")
        print("✅ Added city_id column")
    
    # Migrate existing text-based geographic data to foreign keys
    print("🔄 Migrating existing geographic data...")
    
    # Get companies with text-based geographic data
    cursor.execute("""
        SELECT id, country, state, city 
        FROM companies 
        WHERE country IS NOT NULL OR state IS NOT NULL OR city IS NOT NULL
    """)
    companies = cursor.fetchall()
    
    for company_id, country_name, state_name, city_name in companies:
        country_id = state_id = city_id = None
        
        # Get country_id
        if country_name:
            cursor.execute("SELECT id FROM countries WHERE name = ?", (country_name,))
            result = cursor.fetchone()
            if result:
                country_id = result[0]
        
        # Get state_id
        if state_name and country_id:
            cursor.execute("SELECT id FROM states WHERE name = ? AND country_id = ?", (state_name, country_id))
            result = cursor.fetchone()
            if result:
                state_id = result[0]
        
        # Get city_id
        if city_name and state_id:
            cursor.execute("SELECT id FROM cities WHERE name = ? AND state_id = ?", (city_name, state_id))
            result = cursor.fetchone()
            if result:
                city_id = result[0]
        
        # Update company with foreign keys
        cursor.execute("""
            UPDATE companies 
            SET country_id = ?, state_id = ?, city_id = ?
            WHERE id = ?
        """, (country_id, state_id, city_id, company_id))
        
        print(f"   Updated company {company_id}: country={country_name}→{country_id}, state={state_name}→{state_id}, city={city_name}→{city_id}")
    
    # Keep the old text columns for now (can be removed later after verification)
    print("📝 Keeping original text columns for verification")
    
    conn.commit()
    conn.close()
    print("✅ Company table migration completed!")

def verify_migration():
    """Verify the migration results"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check migrated data
    cursor.execute("""
        SELECT COUNT(*) 
        FROM companies 
        WHERE country_id IS NOT NULL OR state_id IS NOT NULL OR city_id IS NOT NULL
    """)
    migrated_count = cursor.fetchone()[0]
    
    # Show sample migrated company
    cursor.execute("""
        SELECT c.name, c.country, co.name as country_name, c.state, s.name as state_name, 
               c.city, ci.name as city_name
        FROM companies c
        LEFT JOIN countries co ON c.country_id = co.id
        LEFT JOIN states s ON c.state_id = s.id  
        LEFT JOIN cities ci ON c.city_id = ci.id
        WHERE c.country_id IS NOT NULL
        LIMIT 3
    """)
    samples = cursor.fetchall()
    
    print(f"📊 Migration verification:")
    print(f"   Companies with geographic IDs: {migrated_count}")
    print(f"   Sample migrations:")
    for company in samples:
        name, old_country, new_country, old_state, new_state, old_city, new_city = company
        print(f"     {name}: {old_country}→{new_country}, {old_state}→{new_state}, {old_city}→{new_city}")
    
    conn.close()

if __name__ == "__main__":
    print("🚀 Migrating company table for geographic integration...")
    migrate_company_table()
    verify_migration()
    print("✅ Geographic integration migration complete!")