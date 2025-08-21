#!/usr/bin/env python3
"""
Populate geographic data for testing the new database-driven APIs
"""

import sys
import os
sys.path.append('/app/backend')

from sqlalchemy.orm import Session
from backend.crm.app.database.engine import SessionLocal
from backend.crm.app.models.geographic import Country, State, City

def populate_test_data():
    """Populate minimal test data for the review requirements"""
    db = SessionLocal()
    
    try:
        print("🔄 Populating geographic test data...")
        
        # Check if data already exists
        if db.query(Country).first():
            print("✅ Geographic data already exists, skipping...")
            return
        
        # Create the 3 required countries
        countries_data = [
            {"code": "US", "name": "United States"},
            {"code": "CA", "name": "Canada"}, 
            {"code": "IN", "name": "India"}
        ]
        
        countries = {}
        for country_data in countries_data:
            country = Country(**country_data)
            db.add(country)
            db.flush()  # Get ID
            countries[country.code] = country
            print(f"✅ Added country: {country.name}")
        
        # Create states for each country
        states_data = [
            # India states
            {"name": "Maharashtra", "country_id": countries["IN"].id},
            {"name": "Karnataka", "country_id": countries["IN"].id},
            {"name": "Delhi", "country_id": countries["IN"].id},
            
            # US states
            {"name": "California", "country_id": countries["US"].id},
            {"name": "New York", "country_id": countries["US"].id},
            {"name": "Texas", "country_id": countries["US"].id},
            
            # Canada provinces
            {"name": "Ontario", "country_id": countries["CA"].id},
            {"name": "Quebec", "country_id": countries["CA"].id},
            {"name": "British Columbia", "country_id": countries["CA"].id}
        ]
        
        states = {}
        for state_data in states_data:
            state = State(**state_data)
            db.add(state)
            db.flush()  # Get ID
            states[f"{state.name}"] = state
            print(f"✅ Added state: {state.name}")
        
        # Create cities for Maharashtra (19 cities as mentioned in requirements)
        maharashtra_cities = [
            "Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Solapur", "Amravati", 
            "Kolhapur", "Sangli", "Jalgaon", "Akola", "Latur", "Dhule", "Ahmednagar", 
            "Chandrapur", "Parbhani", "Ichalkaranji", "Jalna", "Bhusawal"
        ]
        
        for city_name in maharashtra_cities:
            city = City(name=city_name, state_id=states["Maharashtra"].id)
            db.add(city)
            print(f"✅ Added Maharashtra city: {city_name}")
        
        # Create cities for California
        california_cities = ["San Francisco", "Los Angeles", "San Diego", "Sacramento", "San Jose"]
        for city_name in california_cities:
            city = City(name=city_name, state_id=states["California"].id)
            db.add(city)
            print(f"✅ Added California city: {city_name}")
        
        # Create cities for Ontario
        ontario_cities = ["Toronto", "Ottawa", "Mississauga", "Hamilton", "London"]
        for city_name in ontario_cities:
            city = City(name=city_name, state_id=states["Ontario"].id)
            db.add(city)
            print(f"✅ Added Ontario city: {city_name}")
        
        # Add a few more cities for other states for completeness
        other_cities = [
            {"name": "Bangalore", "state_id": states["Karnataka"].id},
            {"name": "Mysore", "state_id": states["Karnataka"].id},
            {"name": "New Delhi", "state_id": states["Delhi"].id},
            {"name": "New York City", "state_id": states["New York"].id},
            {"name": "Buffalo", "state_id": states["New York"].id},
            {"name": "Houston", "state_id": states["Texas"].id},
            {"name": "Dallas", "state_id": states["Texas"].id},
            {"name": "Montreal", "state_id": states["Quebec"].id},
            {"name": "Vancouver", "state_id": states["British Columbia"].id}
        ]
        
        for city_data in other_cities:
            city = City(**city_data)
            db.add(city)
            print(f"✅ Added city: {city.name}")
        
        db.commit()
        print("🎉 Geographic test data populated successfully!")
        
        # Print summary
        total_countries = db.query(Country).count()
        total_states = db.query(State).count()
        total_cities = db.query(City).count()
        
        print(f"\n📊 Summary:")
        print(f"   Countries: {total_countries}")
        print(f"   States: {total_states}")
        print(f"   Cities: {total_cities}")
        
    except Exception as e:
        print(f"❌ Error populating data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    populate_test_data()