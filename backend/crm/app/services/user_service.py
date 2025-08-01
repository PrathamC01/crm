"""
User management service
"""
from typing import Optional, List
from ..models.user import User
from ..utils.auth import hash_password
from ..schemas.user import UserCreate, UserUpdate

class UserService:
    def __init__(self, postgres_pool):
        self.postgres_pool = postgres_pool
    
    async def create_user(self, user_data: UserCreate, created_by: Optional[str] = None) -> dict:
        """Create a new user"""
        async with self.postgres_pool.acquire() as conn:
            password_hash = hash_password(user_data.password)
            
            user = await User.create_user(
                conn,
                name=user_data.name,
                email=user_data.email,
                username=user_data.username,
                password_hash=password_hash,
                role_id=user_data.role_id,
                department_id=user_data.department_id,
                created_by=created_by
            )
            
            return dict(user)
    
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        async with self.postgres_pool.acquire() as conn:
            user = await User.find_by_id(conn, user_id)
            return dict(user) if user else None
    
    async def update_user(self, user_id: str, user_data: UserUpdate, updated_by: Optional[str] = None) -> Optional[dict]:
        """Update user information"""
        async with self.postgres_pool.acquire() as conn:
            user = await User.update_user(conn, user_id, updated_by, **user_data.dict(exclude_unset=True))
            return dict(user) if user else None
    
    async def get_all_users(self, skip: int = 0, limit: int = 100, search: str = None) -> List[dict]:
        """Get all users"""
        async with self.postgres_pool.acquire() as conn:
            users = await User.get_all(conn, skip, limit, search)
            return [dict(user) for user in users]