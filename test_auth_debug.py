#!/usr/bin/env python3
"""
Debug authentication issue
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/crm'))

from app.database.engine import engine
from sqlalchemy.orm import sessionmaker
from app.models import User
from app.utils.auth import verify_password
from app.services.user_service import UserService

def test_auth():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Test user service
        user_service = UserService(db)
        user = user_service.get_user_by_username("admin")
        
        if user:
            print(f"User found: {user.username}")
            print(f"Password hash: {user.password_hash}")
            
            # Test password verification
            try:
                result = verify_password("admin123", user.password_hash)
                print(f"Password verification: {result}")
            except Exception as e:
                print(f"Password verification error: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("User not found")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_auth()