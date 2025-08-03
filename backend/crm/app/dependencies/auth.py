"""
Authentication dependencies
"""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..utils.auth import verify_token
from ..models.user import User
from ..services.auth_service import AuthService
from ..services.user_service import UserService
from .database import get_postgres_db, get_mongo_db
import uuid

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    postgres_pool=Depends(get_postgres_db),
) -> dict:
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        payload = verify_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Get user from database
        async with postgres_pool.acquire() as conn:
            user = await User.find_by_id(conn, user_id)
            if not user:
                raise HTTPException(status_code=401, detail="User not found")

        return dict(user)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_auth_service(
    postgres_pool=Depends(get_postgres_db), mongo_db=Depends(get_mongo_db)
) -> AuthService:
    """Get authentication service"""
    return AuthService(postgres_pool, mongo_db)


async def get_user_service(postgres_pool=Depends(get_postgres_db)) -> UserService:
    """Get user service"""
    return UserService(postgres_pool)
