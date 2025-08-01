"""
Opportunity model
"""
from typing import Optional
import uuid
from decimal import Decimal

class Opportunity:
    """Opportunity model for managing sales opportunities"""
    
    @staticmethod
    async def create_table(conn):
        """Create opportunities table"""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS opportunities (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                lead_id UUID NOT NULL,
                company_id UUID NOT NULL,
                contact_id UUID NOT NULL,
                name VARCHAR(255) NOT NULL,
                stage VARCHAR(20) NOT NULL DEFAULT 'L1' CHECK (stage IN ('L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7')),
                amount DECIMAL(15,2),
                scoring INTEGER DEFAULT 0 CHECK (scoring BETWEEN 0 AND 100),
                bom_id UUID,
                costing DECIMAL(15,2),
                status VARCHAR(20) NOT NULL DEFAULT 'Open' CHECK (status IN ('Open', 'Won', 'Lost', 'Dropped')),
                justification TEXT,
                close_date DATE,
                probability INTEGER DEFAULT 10 CHECK (probability BETWEEN 0 AND 100),
                notes TEXT,
                is_active BOOLEAN DEFAULT true,
                created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_on TIMESTAMP NULL,
                created_by UUID,
                updated_by UUID,
                deleted_by UUID,
                FOREIGN KEY (lead_id) REFERENCES leads(id),
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (contact_id) REFERENCES contacts(id),
                FOREIGN KEY (created_by) REFERENCES users(id),
                FOREIGN KEY (updated_by) REFERENCES users(id),
                FOREIGN KEY (deleted_by) REFERENCES users(id)
            )
        """)
        
        # Add check constraint for amount justification
        await conn.execute("""
            ALTER TABLE opportunities ADD CONSTRAINT check_amount_justification 
            CHECK (
                (amount < 1000000 AND justification IS NULL) OR 
                (amount >= 1000000 AND justification IS NOT NULL AND length(trim(justification)) > 0)
            )
        """)
        
        # Create indexes
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_lead ON opportunities(lead_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_company ON opportunities(company_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_contact ON opportunities(contact_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_stage ON opportunities(stage)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_status ON opportunities(status)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_amount ON opportunities(amount)")
    
    @staticmethod
    async def find_by_id(conn, opportunity_id: str) -> Optional[dict]:
        """Find opportunity by ID with related details"""
        return await conn.fetchrow("""
            SELECT o.*, 
                   c.name as company_name,
                   cont.full_name as contact_name,
                   cont.email as contact_email,
                   l.lead_source,
                   u.name as created_by_name
            FROM opportunities o
            LEFT JOIN companies c ON o.company_id = c.id
            LEFT JOIN contacts cont ON o.contact_id = cont.id
            LEFT JOIN leads l ON o.lead_id = l.id
            LEFT JOIN users u ON o.created_by = u.id
            WHERE o.id = $1 AND o.is_active = true AND o.deleted_on IS NULL
        """, uuid.UUID(opportunity_id))
    
    @staticmethod
    async def get_by_company(conn, company_id: str, skip: int = 0, limit: int = 100) -> list:
        """Get opportunities by company"""
        return await conn.fetch("""
            SELECT o.*, c.name as company_name, cont.full_name as contact_name
            FROM opportunities o
            LEFT JOIN companies c ON o.company_id = c.id
            LEFT JOIN contacts cont ON o.contact_id = cont.id
            WHERE o.company_id = $1 AND o.is_active = true AND o.deleted_on IS NULL
            ORDER BY o.created_on DESC LIMIT $2 OFFSET $3
        """, uuid.UUID(company_id), limit, skip)
    
    @staticmethod
    async def get_by_lead(conn, lead_id: str, skip: int = 0, limit: int = 100) -> list:
        """Get opportunities by lead"""
        return await conn.fetch("""
            SELECT o.*, c.name as company_name, cont.full_name as contact_name
            FROM opportunities o
            LEFT JOIN companies c ON o.company_id = c.id
            LEFT JOIN contacts cont ON o.contact_id = cont.id
            WHERE o.lead_id = $1 AND o.is_active = true AND o.deleted_on IS NULL
            ORDER BY o.created_on DESC LIMIT $2 OFFSET $3
        """, uuid.UUID(lead_id), limit, skip)
    
    @staticmethod
    async def get_all(conn, skip: int = 0, limit: int = 100, stage: str = None, 
                     status: str = None, search: str = None) -> list:
        """Get all active opportunities with optional filtering"""
        base_query = """
            SELECT o.*, 
                   c.name as company_name,
                   cont.full_name as contact_name,
                   cont.email as contact_email,
                   u.name as created_by_name
            FROM opportunities o
            LEFT JOIN companies c ON o.company_id = c.id
            LEFT JOIN contacts cont ON o.contact_id = cont.id
            LEFT JOIN users u ON o.created_by = u.id
            WHERE o.is_active = true AND o.deleted_on IS NULL
        """
        
        conditions = []
        params = []
        param_count = 1
        
        if stage:
            conditions.append(f"o.stage = ${param_count}")
            params.append(stage)
            param_count += 1
        
        if status:
            conditions.append(f"o.status = ${param_count}")
            params.append(status)
            param_count += 1
        
        if search:
            conditions.append(f"(o.name ILIKE ${param_count} OR c.name ILIKE ${param_count} OR cont.full_name ILIKE ${param_count})")
            params.append(f"%{search}%")
            param_count += 1
        
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        base_query += f" ORDER BY o.updated_on DESC LIMIT ${param_count} OFFSET ${param_count + 1}"
        params.extend([limit, skip])
        
        return await conn.fetch(base_query, *params)
    
    @staticmethod
    async def create_opportunity(conn, **kwargs) -> dict:
        """Create a new opportunity"""
        # Validate that contact is a Decision Maker
        contact_check = await conn.fetchrow(
            "SELECT role_type FROM contacts WHERE id = $1 AND is_active = true",
            uuid.UUID(kwargs['contact_id'])
        )
        
        if not contact_check or contact_check['role_type'] != 'Decision Maker':
            raise ValueError("Opportunity can only be created with a Decision Maker contact")
        
        return await conn.fetchrow("""
            INSERT INTO opportunities (lead_id, company_id, contact_id, name, stage, 
                                     amount, scoring, bom_id, costing, status, 
                                     justification, close_date, probability, notes, created_by)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
            RETURNING *
        """, 
        uuid.UUID(kwargs['lead_id']),
        uuid.UUID(kwargs['company_id']),
        uuid.UUID(kwargs['contact_id']),
        kwargs.get('name'),
        kwargs.get('stage', 'L1'),
        kwargs.get('amount'),
        kwargs.get('scoring', 0),
        uuid.UUID(kwargs['bom_id']) if kwargs.get('bom_id') else None,
        kwargs.get('costing'),
        kwargs.get('status', 'Open'),
        kwargs.get('justification'),
        kwargs.get('close_date'),
        kwargs.get('probability', 10),
        kwargs.get('notes'),
        uuid.UUID(kwargs['created_by']) if kwargs.get('created_by') else None
        )
    
    @staticmethod
    async def update_opportunity(conn, opportunity_id: str, updated_by: str, **kwargs) -> Optional[dict]:
        """Update opportunity information"""
        # Build dynamic update query
        update_fields = []
        values = []
        param_count = 1
        
        for field, value in kwargs.items():
            if value is not None and field not in ['id', 'created_on', 'created_by']:
                if field in ['lead_id', 'company_id', 'contact_id', 'bom_id']:
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
            UPDATE opportunities 
            SET {', '.join(update_fields)}
            WHERE id = ${param_count} AND is_active = true AND deleted_on IS NULL
            RETURNING *
        """
        values.append(uuid.UUID(opportunity_id))
        
        return await conn.fetchrow(query, *values)
    
    @staticmethod
    async def get_pipeline_summary(conn, user_id: str = None) -> dict:
        """Get opportunity pipeline summary"""
        where_clause = "WHERE o.is_active = true AND o.deleted_on IS NULL AND o.status = 'Open'"
        params = []
        
        if user_id:
            where_clause += " AND o.created_by = $1"
            params.append(uuid.UUID(user_id))
        
        result = await conn.fetchrow(f"""
            SELECT 
                COUNT(*) as total_opportunities,
                SUM(CASE WHEN o.amount IS NOT NULL THEN o.amount ELSE 0 END) as total_value,
                AVG(CASE WHEN o.scoring > 0 THEN o.scoring ELSE NULL END) as avg_scoring,
                COUNT(CASE WHEN o.stage IN ('L6', 'L7') THEN 1 END) as closing_stage_count
            FROM opportunities o
            {where_clause}
        """, *params)
        
        # Get stage-wise breakdown
        stage_breakdown = await conn.fetch(f"""
            SELECT stage, COUNT(*) as count, 
                   SUM(CASE WHEN amount IS NOT NULL THEN amount ELSE 0 END) as value
            FROM opportunities o
            {where_clause}
            GROUP BY stage
            ORDER BY stage
        """, *params)
        
        return {
            "summary": dict(result),
            "stage_breakdown": [dict(row) for row in stage_breakdown]
        }