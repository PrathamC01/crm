"""
Authentication service using SQLAlchemy
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
from ..models import User
from ..services.user_service import UserService
from ..utils.auth import verify_password, create_access_token
from ..utils.logger import log_activity
from ..schemas.auth import UserResponse

class AuthService:
    def __init__(self, db: Session, mongo_db):
        self.db = db
        self.mongo_db = mongo_db
        self.user_service = UserService(db)
    
    async def authenticate_user(self, email_or_username: str, password: str, request: Request) -> Dict[str, Any]:
        """Authenticate user and return token"""
        # Check if login is email or username
        if "@" in email_or_username:
            user = self.user_service.get_user_by_email(email_or_username)
        else:
            user = self.user_service.get_user_by_username(email_or_username)
        
        if not user:
            await log_activity(self.mongo_db, "unknown", "failed_login", 
                             {"email_or_username": email_or_username}, request)
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
        
        if not verify_password(password, user.password_hash):
            await log_activity(self.mongo_db, str(user.id), "failed_login", 
                             {"reason": "invalid_password"}, request)
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
        
        # Update last login
        self.user_service.update_last_login(user.id)
        
        # Create JWT token
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email
        }
        access_token = create_access_token(token_data)
        
        # Log successful login
        await log_activity(self.mongo_db, str(user.id), "successful_login", {}, request)
        
        return {"token": access_token}
    
    async def get_user_info(self, user_id: int, request: Request) -> UserResponse:
        """Get user information for dashboard"""
        user = self.user_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Log dashboard access
        await log_activity(self.mongo_db, str(user.id), "dashboard_access", {}, request)
        
        return UserResponse(
            id=str(user.id),
            name=user.name,
            email=user.email,
            username=user.username,
            role=user.role.name if user.role else "N/A",
            department=user.department.name if user.department else "N/A",
            is_active=user.is_active
        )