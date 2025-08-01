"""
User management service
"""
from typing import Optional, List
from ..models.user import User
from ..utils.auth import hash_password
from ..schemas.user import UserCreate, UserUpdate, UserInDB

class UserService:
    def __init__(self, postgres_pool):
        self.postgres_pool = postgres_pool
    
    async def create_user(self, user_data: UserCreate, created_by: Optional[str] = None) -> UserInDB:
        """Create a new user"""
        async with self.postgres_pool.acquire() as conn:
            password_hash = hash_password(user_data.password)
            
            user = await User.create_user(
                conn,
                name=user_data.name,
                email=user_data.email,
                username=user_data.username,
                password_hash=password_hash,
                role=user_data.role,
                department=user_data.department,
                created_by=created_by
            )
            
            return UserInDB(**dict(user))
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID"""
        async with self.postgres_pool.acquire() as conn:
            user = await User.find_by_id(conn, user_id)
            if user:
                return UserInDB(**dict(user))
            return None
    
    async def update_user(self, user_id: str, user_data: UserUpdate, updated_by: Optional[str] = None) -> Optional[UserInDB]:
        """Update user information"""
        async with self.postgres_pool.acquire() as conn:
            # Build update query dynamically based on provided fields
            update_fields = []
            values = []
            param_count = 1
            
            for field, value in user_data.dict(exclude_unset=True).items():
                if value is not None:
                    update_fields.append(f"{field} = ${param_count}")
                    values.append(value)
                    param_count += 1
            
            if not update_fields:
                # No fields to update
                return await self.get_user_by_id(user_id)
            
            # Add updated_on and updated_by
            update_fields.append(f"updated_on = ${param_count}")
            values.append("CURRENT_TIMESTAMP")
            param_count += 1
            
            if updated_by:
                update_fields.append(f"updated_by = ${param_count}")
                values.append(updated_by)
                param_count += 1
            
            query = f"""
                UPDATE users 
                SET {', '.join(update_fields)}
                WHERE id = ${param_count} AND is_active = true AND deleted_on IS NULL
                RETURNING *
            """
            values.append(user_id)
            
            user = await conn.fetchrow(query, *values)
            if user:
                return UserInDB(**dict(user))
            return None