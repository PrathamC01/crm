"""
Lead model
"""
from typing import Optional
import uuid
from datetime import datetime, timedelta

class Lead:
    """Lead model for managing sales leads"""
    
    @staticmethod
    async def create_table(conn):
        """Create leads table"""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                company_id UUID NOT NULL,
                location VARCHAR(255),
                lead_source VARCHAR(50) NOT NULL CHECK (lead_source IN ('Web', 'Partner', 'Campaign', 'Referral', 'Cold Call', 'Event')),
                sales_person_id UUID NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'New' CHECK (status IN ('New', 'Contacted', 'Qualified', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost', 'Dropped')),
                notes TEXT,
                priority VARCHAR(10) DEFAULT 'Medium' CHECK (priority IN ('Low', 'Medium', 'High', 'Urgent')),
                expected_close_date DATE,
                last_activity_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT true,
                created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_on TIMESTAMP NULL,
                created_by UUID,
                updated_by UUID,
                deleted_by UUID,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (sales_person_id) REFERENCES users(id),
                FOREIGN KEY (created_by) REFERENCES users(id),
                FOREIGN KEY (updated_by) REFERENCES users(id),
                FOREIGN KEY (deleted_by) REFERENCES users(id)
            )
        """)
        
        # Create indexes
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_company ON leads(company_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_salesperson ON leads(sales_person_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_last_activity ON leads(last_activity_date)")
    
    @staticmethod
    async def find_by_id(conn, lead_id: str) -> Optional[dict]:
        """Find lead by ID with related details"""
        return await conn.fetchrow("""
            SELECT l.*, c.name as company_name, u.name as sales_person_name 
            FROM leads l
            LEFT JOIN companies c ON l.company_id = c.id
            LEFT JOIN users u ON l.sales_person_id = u.id
            WHERE l.id = $1 AND l.is_active = true AND l.deleted_on IS NULL
        """, uuid.UUID(lead_id))
    
    @staticmethod
    async def get_by_company(conn, company_id: str, skip: int = 0, limit: int = 100) -> list:
        """Get leads by company"""
        return await conn.fetch("""
            SELECT l.*, c.name as company_name, u.name as sales_person_name 
            FROM leads l
            LEFT JOIN companies c ON l.company_id = c.id
            LEFT JOIN users u ON l.sales_person_id = u.id
            WHERE l.company_id = $1 AND l.is_active = true AND l.deleted_on IS NULL
            ORDER BY l.created_on DESC LIMIT $2 OFFSET $3
        """, uuid.UUID(company_id), limit, skip)
    
    @staticmethod
    async def get_by_salesperson(conn, sales_person_id: str, skip: int = 0, limit: int = 100) -> list:
        """Get leads by salesperson"""
        return await conn.fetch("""
            SELECT l.*, c.name as company_name, u.name as sales_person_name 
            FROM leads l
            LEFT JOIN companies c ON l.company_id = c.id
            LEFT JOIN users u ON l.sales_person_id = u.id
            WHERE l.sales_person_id = $1 AND l.is_active = true AND l.deleted_on IS NULL
            ORDER BY l.last_activity_date DESC LIMIT $2 OFFSET $3
        """, uuid.UUID(sales_person_id), limit, skip)
    
    @staticmethod
    async def get_all(conn, skip: int = 0, limit: int = 100, status: str = None, search: str = None) -> list:
        """Get all active leads with optional filtering"""
        base_query = """
            SELECT l.*, c.name as company_name, u.name as sales_person_name 
            FROM leads l
            LEFT JOIN companies c ON l.company_id = c.id
            LEFT JOIN users u ON l.sales_person_id = u.id
            WHERE l.is_active = true AND l.deleted_on IS NULL
        """
        
        conditions = []
        params = []
        param_count = 1
        
        if status:
            conditions.append(f"l.status = ${param_count}")
            params.append(status)
            param_count += 1
        
        if search:
            conditions.append(f"(c.name ILIKE ${param_count} OR l.location ILIKE ${param_count} OR l.notes ILIKE ${param_count})")
            params.append(f"%{search}%")
            param_count += 1
        
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        base_query += f" ORDER BY l.last_activity_date DESC LIMIT ${param_count} OFFSET ${param_count + 1}"
        params.extend([limit, skip])
        
        return await conn.fetch(base_query, *params)
    
    @staticmethod
    async def get_inactive_leads(conn, weeks: int = 4) -> list:
        """Get leads that haven't been updated in specified weeks"""
        cutoff_date = datetime.utcnow() - timedelta(weeks=weeks)
        return await conn.fetch("""
            SELECT l.*, c.name as company_name 
            FROM leads l
            LEFT JOIN companies c ON l.company_id = c.id
            WHERE l.last_activity_date < $1 
            AND l.status NOT IN ('Closed Won', 'Closed Lost', 'Dropped')
            AND l.is_active = true AND l.deleted_on IS NULL
        """, cutoff_date)
    
    @staticmethod
    async def create_lead(conn, **kwargs) -> dict:
        """Create a new lead"""
        return await conn.fetchrow("""
            INSERT INTO leads (company_id, location, lead_source, sales_person_id, 
                             status, notes, priority, expected_close_date, created_by)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING *
        """, 
        uuid.UUID(kwargs['company_id']),
        kwargs.get('location'),
        kwargs.get('lead_source'),
        uuid.UUID(kwargs['sales_person_id']),
        kwargs.get('status', 'New'),
        kwargs.get('notes'),
        kwargs.get('priority', 'Medium'),
        kwargs.get('expected_close_date'),
        uuid.UUID(kwargs['created_by']) if kwargs.get('created_by') else None
        )
    
    @staticmethod
    async def update_lead(conn, lead_id: str, updated_by: str, **kwargs) -> Optional[dict]:
        """Update lead information"""
        # Build dynamic update query
        update_fields = []
        values = []
        param_count = 1
        
        for field, value in kwargs.items():
            if value is not None and field not in ['id', 'created_on', 'created_by']:
                if field in ['company_id', 'sales_person_id']:
                    value = uuid.UUID(value)
                update_fields.append(f"{field} = ${param_count}")
                values.append(value)
                param_count += 1
        
        if not update_fields:
            return None
        
        # Add updated_on, updated_by, and last_activity_date
        update_fields.extend([
            f"updated_on = CURRENT_TIMESTAMP",
            f"updated_by = ${param_count}",
            f"last_activity_date = CURRENT_TIMESTAMP"
        ])
        values.append(uuid.UUID(updated_by))
        param_count += 1
        
        query = f"""
            UPDATE leads 
            SET {', '.join(update_fields)}
            WHERE id = ${param_count} AND is_active = true AND deleted_on IS NULL
            RETURNING *
        """
        values.append(uuid.UUID(lead_id))
        
        return await conn.fetchrow(query, *values)
    
    @staticmethod
    async def auto_close_inactive_leads(conn, weeks: int = 4) -> int:
        """Auto-close leads inactive for specified weeks"""
        cutoff_date = datetime.utcnow() - timedelta(weeks=weeks)
        result = await conn.execute("""
            UPDATE leads 
            SET status = 'Dropped', 
                updated_on = CURRENT_TIMESTAMP,
                notes = COALESCE(notes, '') || ' [Auto-closed due to inactivity]'
            WHERE last_activity_date < $1 
            AND status NOT IN ('Closed Won', 'Closed Lost', 'Dropped')
            AND is_active = true AND deleted_on IS NULL
        """, cutoff_date)
        
        return int(result.split()[-1])  # Extract number of updated rows