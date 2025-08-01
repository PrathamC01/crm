"""
Contact model
"""
from typing import Optional
import uuid

class Contact:
    """Contact model for managing company contacts"""
    
    @staticmethod
    async def create_table(conn):
        """Create contacts table"""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                full_name VARCHAR(255) NOT NULL,
                designation VARCHAR(100),
                email VARCHAR(255) UNIQUE NOT NULL,
                phone_number VARCHAR(20),
                company_id UUID NOT NULL,
                role_type VARCHAR(50) NOT NULL CHECK (role_type IN ('Admin', 'Influencer', 'Decision Maker')),
                business_card_path VARCHAR(500),
                is_active BOOLEAN DEFAULT true,
                created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_on TIMESTAMP NULL,
                created_by UUID,
                updated_by UUID,
                deleted_by UUID,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (created_by) REFERENCES users(id),
                FOREIGN KEY (updated_by) REFERENCES users(id),
                FOREIGN KEY (deleted_by) REFERENCES users(id)
            )
        """)
        
        # Create indexes
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_contacts_company ON contacts(company_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_contacts_role ON contacts(role_type)")
    
    @staticmethod
    async def find_by_id(conn, contact_id: str) -> Optional[dict]:
        """Find contact by ID with company details"""
        return await conn.fetchrow("""
            SELECT c.*, comp.name as company_name 
            FROM contacts c
            LEFT JOIN companies comp ON c.company_id = comp.id
            WHERE c.id = $1 AND c.is_active = true AND c.deleted_on IS NULL
        """, uuid.UUID(contact_id))
    
    @staticmethod
    async def find_by_email(conn, email: str) -> Optional[dict]:
        """Find contact by email"""
        return await conn.fetchrow(
            "SELECT * FROM contacts WHERE email = $1 AND is_active = true AND deleted_on IS NULL",
            email
        )
    
    @staticmethod
    async def get_by_company(conn, company_id: str, skip: int = 0, limit: int = 100) -> list:
        """Get contacts by company"""
        return await conn.fetch("""
            SELECT c.*, comp.name as company_name 
            FROM contacts c
            LEFT JOIN companies comp ON c.company_id = comp.id
            WHERE c.company_id = $1 AND c.is_active = true AND c.deleted_on IS NULL
            ORDER BY c.full_name LIMIT $2 OFFSET $3
        """, uuid.UUID(company_id), limit, skip)
    
    @staticmethod
    async def get_decision_makers_by_company(conn, company_id: str) -> list:
        """Get decision makers for a company"""
        return await conn.fetch("""
            SELECT * FROM contacts 
            WHERE company_id = $1 AND role_type = 'Decision Maker' 
            AND is_active = true AND deleted_on IS NULL
        """, uuid.UUID(company_id))
    
    @staticmethod
    async def get_all(conn, skip: int = 0, limit: int = 100, search: str = None) -> list:
        """Get all active contacts with optional search"""
        if search:
            return await conn.fetch("""
                SELECT c.*, comp.name as company_name 
                FROM contacts c
                LEFT JOIN companies comp ON c.company_id = comp.id
                WHERE c.is_active = true AND c.deleted_on IS NULL 
                AND (c.full_name ILIKE $1 OR c.email ILIKE $1 OR c.designation ILIKE $1 OR comp.name ILIKE $1)
                ORDER BY c.full_name LIMIT $2 OFFSET $3
            """, f"%{search}%", limit, skip)
        else:
            return await conn.fetch("""
                SELECT c.*, comp.name as company_name 
                FROM contacts c
                LEFT JOIN companies comp ON c.company_id = comp.id
                WHERE c.is_active = true AND c.deleted_on IS NULL 
                ORDER BY c.full_name LIMIT $1 OFFSET $2
            """, limit, skip)
    
    @staticmethod
    async def create_contact(conn, **kwargs) -> dict:
        """Create a new contact"""
        return await conn.fetchrow("""
            INSERT INTO contacts (full_name, designation, email, phone_number, 
                                company_id, role_type, business_card_path, created_by)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING *
        """, 
        kwargs.get('full_name'),
        kwargs.get('designation'),
        kwargs.get('email'),
        kwargs.get('phone_number'),
        uuid.UUID(kwargs['company_id']),
        kwargs.get('role_type'),
        kwargs.get('business_card_path'),
        uuid.UUID(kwargs['created_by']) if kwargs.get('created_by') else None
        )
    
    @staticmethod
    async def update_contact(conn, contact_id: str, updated_by: str, **kwargs) -> Optional[dict]:
        """Update contact information"""
        # Build dynamic update query
        update_fields = []
        values = []
        param_count = 1
        
        for field, value in kwargs.items():
            if value is not None and field not in ['id', 'created_on', 'created_by']:
                if field == 'company_id':
                    value = uuid.UUID(value)
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
            UPDATE contacts 
            SET {', '.join(update_fields)}
            WHERE id = ${param_count} AND is_active = true AND deleted_on IS NULL
            RETURNING *
        """
        values.append(uuid.UUID(contact_id))
        
        return await conn.fetchrow(query, *values)