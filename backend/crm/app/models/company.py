"""
Company model
"""
from typing import Optional
import uuid

class Company:
    """Company model for managing company information"""
    
    @staticmethod
    async def create_table(conn):
        """Create companies table"""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) UNIQUE NOT NULL,
                gst_number VARCHAR(15),
                pan_number VARCHAR(10),
                parent_company_id UUID,
                industry_category VARCHAR(100),
                address TEXT,
                city VARCHAR(100),
                state VARCHAR(100),
                country VARCHAR(100) DEFAULT 'India',
                postal_code VARCHAR(10),
                website VARCHAR(255),
                description TEXT,
                is_active BOOLEAN DEFAULT true,
                created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_on TIMESTAMP NULL,
                created_by UUID,
                updated_by UUID,
                deleted_by UUID,
                FOREIGN KEY (parent_company_id) REFERENCES companies(id),
                FOREIGN KEY (created_by) REFERENCES users(id),
                FOREIGN KEY (updated_by) REFERENCES users(id),
                FOREIGN KEY (deleted_by) REFERENCES users(id)
            )
        """)
        
        # Create indexes
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_companies_gst ON companies(gst_number)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_companies_pan ON companies(pan_number)")
    
    @staticmethod
    async def find_by_id(conn, company_id: str) -> Optional[dict]:
        """Find company by ID"""
        return await conn.fetchrow(
            "SELECT * FROM companies WHERE id = $1 AND is_active = true AND deleted_on IS NULL",
            uuid.UUID(company_id)
        )
    
    @staticmethod
    async def find_by_name(conn, name: str) -> Optional[dict]:
        """Find company by name"""
        return await conn.fetchrow(
            "SELECT * FROM companies WHERE name = $1 AND is_active = true AND deleted_on IS NULL",
            name
        )
    
    @staticmethod
    async def get_all(conn, skip: int = 0, limit: int = 100, search: str = None) -> list:
        """Get all active companies with optional search"""
        if search:
            return await conn.fetch("""
                SELECT * FROM companies 
                WHERE is_active = true AND deleted_on IS NULL 
                AND (name ILIKE $1 OR industry_category ILIKE $1 OR city ILIKE $1)
                ORDER BY name LIMIT $2 OFFSET $3
            """, f"%{search}%", limit, skip)
        else:
            return await conn.fetch(
                "SELECT * FROM companies WHERE is_active = true AND deleted_on IS NULL ORDER BY name LIMIT $1 OFFSET $2",
                limit, skip
            )
    
    @staticmethod
    async def create_company(conn, **kwargs) -> dict:
        """Create a new company"""
        return await conn.fetchrow("""
            INSERT INTO companies (name, gst_number, pan_number, parent_company_id, 
                                 industry_category, address, city, state, country, 
                                 postal_code, website, description, created_by)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            RETURNING *
        """, 
        kwargs.get('name'),
        kwargs.get('gst_number'),
        kwargs.get('pan_number'),
        uuid.UUID(kwargs['parent_company_id']) if kwargs.get('parent_company_id') else None,
        kwargs.get('industry_category'),
        kwargs.get('address'),
        kwargs.get('city'),
        kwargs.get('state'),
        kwargs.get('country', 'India'),
        kwargs.get('postal_code'),
        kwargs.get('website'),
        kwargs.get('description'),
        uuid.UUID(kwargs['created_by']) if kwargs.get('created_by') else None
        )
    
    @staticmethod
    async def update_company(conn, company_id: str, updated_by: str, **kwargs) -> Optional[dict]:
        """Update company information"""
        # Build dynamic update query
        update_fields = []
        values = []
        param_count = 1
        
        for field, value in kwargs.items():
            if value is not None and field not in ['id', 'created_on', 'created_by']:
                if field == 'parent_company_id':
                    value = uuid.UUID(value) if value else None
                update_fields.append(f"{field} = ${param_count}")
                values.append(value)
                param_count += 1
        
        if not update_fields:
            return None
        
        # Add updated_on and updated_by
        update_fields.append(f"updated_on = CURRENT_TIMESTAMP")
        update_fields.append(f"updated_by = ${param_count}")
        values.append(uuid.UUID(updated_by))
        param_count += 1
        
        query = f"""
            UPDATE companies 
            SET {', '.join(update_fields)}
            WHERE id = ${param_count} AND is_active = true AND deleted_on IS NULL
            RETURNING *
        """
        values.append(uuid.UUID(company_id))
        
        return await conn.fetchrow(query, *values)