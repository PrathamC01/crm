"""
Authentication dependencies using SQLAlchemy
"""
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..utils.auth import verify_token
from ..models import User
from ..services.auth_service import AuthService
from ..services.user_service import UserService
from .database import get_postgres_db, get_mongo_db

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_postgres_db)
) -> dict:
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        payload = verify_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database using SQLAlchemy
        user_service = UserService(db)
        user = user_service.get_user_by_id(int(user_id))
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "username": user.username,
            "role": user.role.name if user.role else None,
            "department": user.department.name if user.department else None
        }
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID format")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_auth_service(
    db: Session = Depends(get_postgres_db),
    mongo_db = Depends(get_mongo_db)
) -> AuthService:
    """Get authentication service"""
    return AuthService(db, mongo_db)

def get_user_service(
    db: Session = Depends(get_postgres_db)
) -> UserService:
    """Get user service"""
    return UserService(db)