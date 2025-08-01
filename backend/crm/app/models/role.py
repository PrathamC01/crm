"""
Role model for RBAC system
"""
from typing import Optional
import uuid

class Role:
    """Role model for role-based access control"""
    
    @staticmethod
    async def create_table(conn):
        """Create roles table"""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                permissions JSONB DEFAULT '[]',
                is_active BOOLEAN DEFAULT true,
                created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_on TIMESTAMP NULL,
                created_by UUID,
                updated_by UUID,
                deleted_by UUID
            )
        """)
        
        # Insert default roles
        await conn.execute("""
            INSERT INTO roles (name, description, permissions) VALUES 
            ('super_admin', 'Super Administrator', '["all"]'),
            ('admin', 'Administrator', '["users:read", "users:write", "companies:all", "contacts:all", "leads:all", "opportunities:all"]'),
            ('sales_manager', 'Sales Manager', '["companies:read", "contacts:all", "leads:all", "opportunities:all", "users:read"]'),
            ('sales_executive', 'Sales Executive', '["companies:read", "contacts:read", "leads:all", "opportunities:read", "opportunities:write"]'),
            ('marketing', 'Marketing Team', '["companies:read", "contacts:read", "leads:all"]'),
            ('user', 'Regular User', '["companies:read", "contacts:read", "leads:read", "opportunities:read"]')
            ON CONFLICT (name) DO NOTHING
        """)
    
    @staticmethod
    async def find_by_id(conn, role_id: str) -> Optional[dict]:
        """Find role by ID"""
        return await conn.fetchrow(
            "SELECT * FROM roles WHERE id = $1 AND is_active = true AND deleted_on IS NULL",
            uuid.UUID(role_id)
        )
    
    @staticmethod
    async def find_by_name(conn, name: str) -> Optional[dict]:
        """Find role by name"""
        return await conn.fetchrow(
            "SELECT * FROM roles WHERE name = $1 AND is_active = true AND deleted_on IS NULL",
            name
        )
    
    @staticmethod
    async def get_all(conn, skip: int = 0, limit: int = 100) -> list:
        """Get all active roles"""
        return await conn.fetch(
            "SELECT * FROM roles WHERE is_active = true AND deleted_on IS NULL ORDER BY name LIMIT $1 OFFSET $2",
            limit, skip
        )