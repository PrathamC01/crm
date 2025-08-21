"""
Create database tables for countries, states, and cities with proper relationships
"""

import sqlite3
import os
from pathlib import Path

# Database path
DB_PATH = "/app/backend/crm_database.db"

def create_geographic_tables():
    """Create countries, states, and cities tables with proper relationships"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create countries table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL UNIQUE,
            code VARCHAR(3) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create states table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            country_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (country_id) REFERENCES countries (id),
            UNIQUE(name, country_id)
        )
    """)
    
    # Create cities table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            state_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (state_id) REFERENCES states (id),
            UNIQUE(name, state_id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Geographic tables created successfully!")

def seed_geographic_data():
    """Seed the tables with predefined data as specified"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Countries data
    countries_data = [
        ("United States", "US"),
        ("Canada", "CA"), 
        ("India", "IN")
    ]
    
    # Insert countries
    cursor.executemany("INSERT OR IGNORE INTO countries (name, code) VALUES (?, ?)", countries_data)
    
    # Get country IDs
    cursor.execute("SELECT id, name FROM countries")
    country_mapping = {name: id for id, name in cursor.fetchall()}
    
    # States data
    states_data = [
        # United States
        ("California", country_mapping["United States"]),
        ("New York", country_mapping["United States"]),
        ("Texas", country_mapping["United States"]),
        
        # Canada
        ("Ontario", country_mapping["Canada"]),
        ("Quebec", country_mapping["Canada"]),
        ("British Columbia", country_mapping["Canada"]),
        
        # India
        ("Maharashtra", country_mapping["India"]),
        ("Karnataka", country_mapping["India"]),
        ("Delhi", country_mapping["India"])
    ]
    
    # Insert states
    cursor.executemany("INSERT OR IGNORE INTO states (name, country_id) VALUES (?, ?)", states_data)
    
    # Get state IDs
    cursor.execute("SELECT id, name FROM states")
    state_mapping = {name: id for id, name in cursor.fetchall()}
    
    # Cities data as specified
    cities_data = [
        # California cities
        ("San Francisco", state_mapping["California"]),
        ("Los Angeles", state_mapping["California"]),
        ("San Diego", state_mapping["California"]),
        
        # New York cities
        ("New York City", state_mapping["New York"]),
        ("Buffalo", state_mapping["New York"]),
        ("Albany", state_mapping["New York"]),
        
        # Texas cities
        ("Austin", state_mapping["Texas"]),
        ("Houston", state_mapping["Texas"]),
        ("Dallas", state_mapping["Texas"]),
        
        # Ontario cities
        ("Toronto", state_mapping["Ontario"]),
        ("Ottawa", state_mapping["Ontario"]),
        ("Mississauga", state_mapping["Ontario"]),
        
        # Quebec cities
        ("Montreal", state_mapping["Quebec"]),
        ("Quebec City", state_mapping["Quebec"]),
        ("Laval", state_mapping["Quebec"]),
        
        # British Columbia cities
        ("Vancouver", state_mapping["British Columbia"]),
        ("Victoria", state_mapping["British Columbia"]),
        ("Kelowna", state_mapping["British Columbia"]),
        
        # Maharashtra cities (as specified - 19 cities)
        ("Ahmednagar", state_mapping["Maharashtra"]),
        ("Akola", state_mapping["Maharashtra"]),
        ("Ambajogai", state_mapping["Maharashtra"]),
        ("Aurangabad", state_mapping["Maharashtra"]),
        ("Beed", state_mapping["Maharashtra"]),
        ("Bhiwandi", state_mapping["Maharashtra"]),
        ("Dhule", state_mapping["Maharashtra"]),
        ("Jalgaon", state_mapping["Maharashtra"]),
        ("Kolhapur", state_mapping["Maharashtra"]),
        ("Latur", state_mapping["Maharashtra"]),
        ("Mumbai", state_mapping["Maharashtra"]),
        ("Nagpur", state_mapping["Maharashtra"]),
        ("Nanded", state_mapping["Maharashtra"]),
        ("Nashik", state_mapping["Maharashtra"]),
        ("Osmanabad", state_mapping["Maharashtra"]),
        ("Pune", state_mapping["Maharashtra"]),
        ("Sangli", state_mapping["Maharashtra"]),
        ("Satara", state_mapping["Maharashtra"]),
        ("Solapur", state_mapping["Maharashtra"]),
        
        # Karnataka cities
        ("Bangalore", state_mapping["Karnataka"]),
        ("Mysore", state_mapping["Karnataka"]),
        ("Mangalore", state_mapping["Karnataka"]),
        
        # Delhi cities
        ("New Delhi", state_mapping["Delhi"]),
        ("Noida", state_mapping["Delhi"]),
        ("Gurgaon", state_mapping["Delhi"])
    ]
    
    # Insert cities
    cursor.executemany("INSERT OR IGNORE INTO cities (name, state_id) VALUES (?, ?)", cities_data)
    
    conn.commit()
    conn.close()
    print("✅ Geographic data seeded successfully!")

def verify_data():
    """Verify the seeded data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Count data
    cursor.execute("SELECT COUNT(*) FROM countries")
    countries_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM states")
    states_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM cities")
    cities_count = cursor.fetchone()[0]
    
    print(f"📊 Data verification:")
    print(f"   Countries: {countries_count}")
    print(f"   States: {states_count}")
    print(f"   Cities: {cities_count}")
    
    # Verify Maharashtra cities specifically
    cursor.execute("""
        SELECT c.name 
        FROM cities c
        JOIN states s ON c.state_id = s.id
        WHERE s.name = 'Maharashtra'
        ORDER BY c.name
    """)
    maharashtra_cities = cursor.fetchall()
    print(f"   Maharashtra cities: {len(maharashtra_cities)}")
    print(f"   Sample cities: {[city[0] for city in maharashtra_cities[:5]]}")
    
    conn.close()

if __name__ == "__main__":
    print("🚀 Creating geographic database tables...")
    create_geographic_tables()
    seed_geographic_data()
    verify_data()
    print("✅ Geographic database setup complete!")