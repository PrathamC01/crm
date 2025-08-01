"""
Enhanced User database model with role and department support
"""
from typing import Optional
from datetime import datetime
import uuid

class User:
    """Enhanced User model for database operations"""
    
    @staticmethod
    async def create_table(conn):
        """Create users table with enhanced fields"""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role_id UUID,
                department_id UUID,
                is_active BOOLEAN DEFAULT true,
                last_login TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP,
                created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_on TIMESTAMP NULL,
                created_by UUID,
                updated_by UUID,
                deleted_by UUID,
                FOREIGN KEY (role_id) REFERENCES roles(id),
                FOREIGN KEY (department_id) REFERENCES departments(id),
                FOREIGN KEY (created_by) REFERENCES users(id),
                FOREIGN KEY (updated_by) REFERENCES users(id),
                FOREIGN KEY (deleted_by) REFERENCES users(id)
            )
        """)
        
        # Create indexes
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users(role_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_department ON users(department_id)")
    
    @staticmethod
    async def seed_admin_user(conn):
        """Seed admin user with proper role"""
        from ..utils.auth import hash_password
        
        # Get admin role
        admin_role = await conn.fetchrow("SELECT id FROM roles WHERE name = 'admin'")
        it_dept = await conn.fetchrow("SELECT id FROM departments WHERE name = 'IT'")
        
        admin_password = hash_password("admin123")
        await conn.execute("""
            INSERT INTO users (name, email, username, password_hash, role_id, department_id)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (email) DO UPDATE SET
                role_id = EXCLUDED.role_id,
                department_id = EXCLUDED.department_id,
                updated_on = CURRENT_TIMESTAMP
        """, "Admin User", "admin@crm.com", "admin", admin_password, 
             admin_role['id'] if admin_role else None,
             it_dept['id'] if it_dept else None)
    
    @staticmethod
    async def find_by_email(conn, email: str) -> Optional[dict]:
        """Find user by email with role and department details"""
        return await conn.fetchrow("""
            SELECT u.*, r.name as role_name, r.permissions, d.name as department_name
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            LEFT JOIN departments d ON u.department_id = d.id
            WHERE u.email = $1 AND u.is_active = true AND u.deleted_on IS NULL
        """, email)
    
    @staticmethod
    async def find_by_username(conn, username: str) -> Optional[dict]:
        """Find user by username with role and department details"""
        return await conn.fetchrow("""
            SELECT u.*, r.name as role_name, r.permissions, d.name as department_name
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            LEFT JOIN departments d ON u.department_id = d.id
            WHERE u.username = $1 AND u.is_active = true AND u.deleted_on IS NULL
        """, username)
    
    @staticmethod
    async def find_by_id(conn, user_id: str) -> Optional[dict]:
        """Find user by ID with role and department details"""
        return await conn.fetchrow("""
            SELECT u.*, r.name as role_name, r.permissions, d.name as department_name
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            LEFT JOIN departments d ON u.department_id = d.id
            WHERE u.id = $1 AND u.is_active = true AND u.deleted_on IS NULL
        """, uuid.UUID(user_id))
    
    @staticmethod
    async def get_all(conn, skip: int = 0, limit: int = 100, search: str = None) -> list:
        """Get all active users with optional search"""
        if search:
            return await conn.fetch("""
                SELECT u.*, r.name as role_name, d.name as department_name
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.id
                LEFT JOIN departments d ON u.department_id = d.id
                WHERE u.is_active = true AND u.deleted_on IS NULL 
                AND (u.name ILIKE $1 OR u.email ILIKE $1 OR u.username ILIKE $1)
                ORDER BY u.name LIMIT $2 OFFSET $3
            """, f"%{search}%", limit, skip)
        else:
            return await conn.fetch("""
                SELECT u.*, r.name as role_name, d.name as department_name
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.id
                LEFT JOIN departments d ON u.department_id = d.id
                WHERE u.is_active = true AND u.deleted_on IS NULL 
                ORDER BY u.name LIMIT $1 OFFSET $2
            """, limit, skip)
    
    @staticmethod
    async def create_user(conn, name: str, email: str, username: str, password_hash: str, 
                         role_id: str = None, department_id: str = None, created_by: str = None) -> dict:
        """Create a new user"""
        return await conn.fetchrow("""
            INSERT INTO users (name, email, username, password_hash, role_id, department_id, created_by)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """, name, email, username, password_hash, 
            uuid.UUID(role_id) if role_id else None,
            uuid.UUID(department_id) if department_id else None,
            uuid.UUID(created_by) if created_by else None)
    
    @staticmethod
    async def update_user(conn, user_id: str, updated_by: str, **kwargs) -> Optional[dict]:
        """Update user information"""
        # Build dynamic update query
        update_fields = []
        values = []
        param_count = 1
        
        for field, value in kwargs.items():
            if value is not None and field not in ['id', 'created_on', 'created_by', 'password_hash']:
                if field in ['role_id', 'department_id']:
                    value = uuid.UUID(value) if value else None
                update_fields.append(f"{field} = ${param_count}")
                values.append(value)
                param_count += 1
        
        if not update_fields:
            return None
        
        # Add updated_on and updated_by
        update_fields.extend([
            f"updated_on = CURRENT_TIMESTAMP",
            f"updated_by = ${param_count}"
        ])
        values.append(uuid.UUID(updated_by))
        param_count += 1
        
        query = f"""
            UPDATE users 
            SET {', '.join(update_fields)}
            WHERE id = ${param_count} AND is_active = true AND deleted_on IS NULL
            RETURNING *
        """
        values.append(uuid.UUID(user_id))
        
        return await conn.fetchrow(query, *values)
    
    @staticmethod
    async def update_last_login(conn, user_id: str):
        """Update user's last login timestamp"""
        await conn.execute("""
            UPDATE users 
            SET last_login = CURRENT_TIMESTAMP, failed_login_attempts = 0
            WHERE id = $1
        """, uuid.UUID(user_id))
    
    @staticmethod
    async def increment_failed_login(conn, user_id: str):
        """Increment failed login attempts"""
        await conn.execute("""
            UPDATE users 
            SET failed_login_attempts = failed_login_attempts + 1
            WHERE id = $1
        """, uuid.UUID(user_id))
    
    @staticmethod
    async def get_sales_people(conn) -> list:
        """Get all users with sales roles"""
        return await conn.fetch("""
            SELECT u.id, u.name, u.email, r.name as role_name
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.is_active = true AND u.deleted_on IS NULL
            AND r.name IN ('sales_manager', 'sales_executive')
            ORDER BY u.name
        """)