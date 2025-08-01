"""
User database model
"""
from typing import Optional
from datetime import datetime
import uuid

class User:
    """User model for database operations"""
    
    @staticmethod
    async def create_table(conn):
        """Create users table if it doesn't exist"""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(100) NOT NULL DEFAULT 'user',
                department VARCHAR(100),
                is_active BOOLEAN DEFAULT true,
                created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_on TIMESTAMP NULL,
                created_by UUID,
                updated_by UUID,
                deleted_by UUID
            )
        """)
    
    @staticmethod
    async def find_by_email(conn, email: str) -> Optional[dict]:
        """Find user by email"""
        return await conn.fetchrow(
            "SELECT * FROM users WHERE email = $1 AND is_active = true AND deleted_on IS NULL",
            email
        )
    
    @staticmethod
    async def find_by_username(conn, username: str) -> Optional[dict]:
        """Find user by username"""
        return await conn.fetchrow(
            "SELECT * FROM users WHERE username = $1 AND is_active = true AND deleted_on IS NULL",
            username
        )
    
    @staticmethod
    async def find_by_id(conn, user_id: str) -> Optional[dict]:
        """Find user by ID"""
        return await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1 AND is_active = true AND deleted_on IS NULL",
            uuid.UUID(user_id)
        )
    
    @staticmethod
    async def create_user(conn, name: str, email: str, username: str, password_hash: str, 
                         role: str = "user", department: str = None, created_by: str = None) -> dict:
        """Create a new user"""
        return await conn.fetchrow("""
            INSERT INTO users (name, email, username, password_hash, role, department, created_by)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """, name, email, username, password_hash, role, department, 
            uuid.UUID(created_by) if created_by else None)