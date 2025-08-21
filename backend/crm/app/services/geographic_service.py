"""
Service for database-driven geographic data (Countries, States, Cities)
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from ..models.geographic import Country, State, City


class GeographicService:
    """Service for managing geographic data from database"""
    
    @staticmethod
    def get_all_countries(db: Session) -> List[Dict]:
        """Get all countries from database"""
        countries = db.query(Country).order_by(Country.name).all()
        return [
            {
                "id": country.id,
                "name": country.name,
                "code": country.code
            }
            for country in countries
        ]
    
    @staticmethod
    def get_states_by_country(db: Session, country_id: int) -> List[Dict]:
        """Get all states for a specific country"""
        states = (
            db.query(State)
            .filter(State.country_id == country_id)
            .order_by(State.name)
            .all()
        )
        return [
            {
                "id": state.id,
                "name": state.name,
                "country_id": state.country_id
            }
            for state in states
        ]
    
    @staticmethod
    def get_states_by_country_name(db: Session, country_name: str) -> List[Dict]:
        """Get all states for a specific country by name"""
        country = db.query(Country).filter(Country.name == country_name).first()
        if not country:
            return []
        
        return GeographicService.get_states_by_country(db, country.id)
    
    @staticmethod
    def get_cities_by_state(db: Session, state_id: int) -> List[Dict]:
        """Get all cities for a specific state"""
        cities = (
            db.query(City)
            .filter(City.state_id == state_id)
            .order_by(City.name)
            .all()
        )
        return [
            {
                "id": city.id,
                "name": city.name,
                "state_id": city.state_id
            }
            for city in cities
        ]
    
    @staticmethod
    def get_cities_by_state_name(db: Session, country_name: str, state_name: str) -> List[Dict]:
        """Get all cities for a specific state by country and state names"""
        # Find the state by joining with country
        state = (
            db.query(State)
            .join(Country)
            .filter(Country.name == country_name, State.name == state_name)
            .first()
        )
        
        if not state:
            return []
        
        return GeographicService.get_cities_by_state(db, state.id)
    
    @staticmethod
    def get_geographic_ids(db: Session, country_name: str, state_name: str, city_name: str) -> Dict[str, Optional[int]]:
        """Get the IDs for country, state, and city names"""
        result = {"country_id": None, "state_id": None, "city_id": None}
        
        # Get country ID
        country = db.query(Country).filter(Country.name == country_name).first()
        if not country:
            return result
        result["country_id"] = country.id
        
        # Get state ID
        state = (
            db.query(State)
            .filter(State.name == state_name, State.country_id == country.id)
            .first()
        )
        if not state:
            return result
        result["state_id"] = state.id
        
        # Get city ID
        city = (
            db.query(City)
            .filter(City.name == city_name, City.state_id == state.id)
            .first()
        )
        if city:
            result["city_id"] = city.id
        
        return result
    
    @staticmethod
    def validate_geographic_selection(db: Session, country_id: Optional[int], 
                                     state_id: Optional[int], city_id: Optional[int]) -> Dict[str, bool]:
        """Validate that geographic selections are valid and related"""
        result = {"valid": True, "errors": []}
        
        if country_id:
            country = db.query(Country).filter(Country.id == country_id).first()
            if not country:
                result["valid"] = False
                result["errors"].append("Invalid country ID")
                return result
        
        if state_id:
            state = db.query(State).filter(State.id == state_id).first()
            if not state:
                result["valid"] = False
                result["errors"].append("Invalid state ID")
            elif country_id and state.country_id != country_id:
                result["valid"] = False
                result["errors"].append("State does not belong to selected country")
        
        if city_id:
            city = db.query(City).filter(City.id == city_id).first()
            if not city:
                result["valid"] = False
                result["errors"].append("Invalid city ID")
            elif state_id and city.state_id != state_id:
                result["valid"] = False
                result["errors"].append("City does not belong to selected state")
        
        return result