"""
Department model
"""
from typing import Optional
import uuid

class Department:
    """Department model"""
    
    @staticmethod
    async def create_table(conn):
        """Create departments table"""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                head_user_id UUID,
                is_active BOOLEAN DEFAULT true,
                created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_on TIMESTAMP NULL,
                created_by UUID,
                updated_by UUID,
                deleted_by UUID
            )
        """)
        
        # Insert default departments
        await conn.execute("""
            INSERT INTO departments (name, description) VALUES 
            ('IT', 'Information Technology'),
            ('Sales', 'Sales Department'),
            ('Marketing', 'Marketing Department'),
            ('Finance', 'Finance Department'),
            ('HR', 'Human Resources'),
            ('Operations', 'Operations Department')
            ON CONFLICT (name) DO NOTHING
        """)
    
    @staticmethod
    async def find_by_id(conn, dept_id: str) -> Optional[dict]:
        """Find department by ID"""
        return await conn.fetchrow(
            "SELECT * FROM departments WHERE id = $1 AND is_active = true AND deleted_on IS NULL",
            uuid.UUID(dept_id)
        )
    
    @staticmethod
    async def get_all(conn, skip: int = 0, limit: int = 100) -> list:
        """Get all active departments"""
        return await conn.fetch(
            "SELECT * FROM departments WHERE is_active = true AND deleted_on IS NULL ORDER BY name LIMIT $1 OFFSET $2",
            limit, skip
        )