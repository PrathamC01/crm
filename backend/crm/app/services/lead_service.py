"""
Lead management service
"""
from typing import Optional, List
from ..models.lead import Lead
from ..schemas.lead import LeadCreate, LeadUpdate, LeadConversion
from ..services.opportunity_service import OpportunityService

class LeadService:
    def __init__(self, postgres_pool):
        self.postgres_pool = postgres_pool
    
    async def create_lead(self, lead_data: LeadCreate, created_by: Optional[str] = None) -> dict:
        """Create a new lead"""
        async with self.postgres_pool.acquire() as conn:
            lead = await Lead.create_lead(
                conn,
                **lead_data.dict(),
                created_by=created_by
            )
            return dict(lead)
    
    async def get_lead_by_id(self, lead_id: str) -> Optional[dict]:
        """Get lead by ID"""
        async with self.postgres_pool.acquire() as conn:
            lead = await Lead.find_by_id(conn, lead_id)
            return dict(lead) if lead else None
    
    async def get_leads(self, skip: int = 0, limit: int = 100, status: str = None, search: str = None) -> List[dict]:
        """Get all leads with optional filtering"""
        async with self.postgres_pool.acquire() as conn:
            leads = await Lead.get_all(conn, skip, limit, status, search)
            return [dict(lead) for lead in leads]
    
    async def get_leads_by_company(self, company_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get leads by company"""
        async with self.postgres_pool.acquire() as conn:
            leads = await Lead.get_by_company(conn, company_id, skip, limit)
            return [dict(lead) for lead in leads]
    
    async def get_leads_by_salesperson(self, sales_person_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get leads by salesperson"""
        async with self.postgres_pool.acquire() as conn:
            leads = await Lead.get_by_salesperson(conn, sales_person_id, skip, limit)
            return [dict(lead) for lead in leads]
    
    async def update_lead(self, lead_id: str, lead_data: LeadUpdate, updated_by: str) -> Optional[dict]:
        """Update lead information"""
        async with self.postgres_pool.acquire() as conn:
            lead = await Lead.update_lead(
                conn, 
                lead_id, 
                updated_by, 
                **lead_data.dict(exclude_unset=True)
            )
            return dict(lead) if lead else None
    
    async def delete_lead(self, lead_id: str, deleted_by: str) -> bool:
        """Soft delete lead"""
        async with self.postgres_pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE leads 
                SET is_active = false, deleted_on = CURRENT_TIMESTAMP, deleted_by = $1
                WHERE id = $2 AND is_active = true
            """, deleted_by, lead_id)
            return result == "UPDATE 1"
    
    async def convert_to_opportunity(self, lead_id: str, conversion_data: LeadConversion, created_by: str) -> dict:
        """Convert lead to opportunity"""
        async with self.postgres_pool.acquire() as conn:
            # Get lead details
            lead = await Lead.find_by_id(conn, lead_id)
            if not lead:
                raise ValueError("Lead not found")
            
            # Verify contact is a Decision Maker
            contact = await conn.fetchrow(
                "SELECT role_type FROM contacts WHERE id = $1 AND is_active = true",
                conversion_data.contact_id
            )
            if not contact or contact['role_type'] != 'Decision Maker':
                raise ValueError("Contact must be a Decision Maker to create opportunity")
            
            # Create opportunity
            opportunity_data = {
                'lead_id': lead_id,
                'company_id': lead['company_id'],
                'contact_id': conversion_data.contact_id,
                'name': conversion_data.opportunity_name,
                'stage': conversion_data.stage,
                'amount': conversion_data.amount,
                'justification': conversion_data.justification,
                'notes': conversion_data.notes,
                'created_by': created_by
            }
            
            from ..models.opportunity import Opportunity
            opportunity = await Opportunity.create_opportunity(conn, **opportunity_data)
            
            # Update lead status to Qualified
            await Lead.update_lead(conn, lead_id, created_by, status='Qualified')
            
            return dict(opportunity)
    
    async def get_lead_count(self, status: str = None, search: str = None) -> int:
        """Get total count of leads"""
        async with self.postgres_pool.acquire() as conn:
            base_query = """
                SELECT COUNT(*) FROM leads l
                LEFT JOIN companies c ON l.company_id = c.id
                WHERE l.is_active = true AND l.deleted_on IS NULL
            """
            
            conditions = []
            params = []
            
            if status:
                conditions.append("l.status = $" + str(len(params) + 1))
                params.append(status)
            
            if search:
                conditions.append("(c.name ILIKE $" + str(len(params) + 1) + " OR l.location ILIKE $" + str(len(params) + 1) + " OR l.notes ILIKE $" + str(len(params) + 1) + ")")
                params.append(f"%{search}%")
            
            if conditions:
                base_query += " AND " + " AND ".join(conditions)
            
            result = await conn.fetchval(base_query, *params)
            return result or 0
    
    async def auto_close_inactive_leads(self) -> int:
        """Auto-close leads inactive for 4 weeks"""
        async with self.postgres_pool.acquire() as conn:
            return await Lead.auto_close_inactive_leads(conn, weeks=4)
    
    async def get_lead_summary(self, sales_person_id: str = None) -> dict:
        """Get lead summary statistics"""
        async with self.postgres_pool.acquire() as conn:
            where_clause = "WHERE is_active = true AND deleted_on IS NULL"
            params = []
            
            if sales_person_id:
                where_clause += " AND sales_person_id = $1"
                params.append(sales_person_id)
            
            result = await conn.fetchrow(f"""
                SELECT 
                    COUNT(*) as total_leads,
                    COUNT(CASE WHEN status = 'New' THEN 1 END) as new_leads,
                    COUNT(CASE WHEN status = 'Qualified' THEN 1 END) as qualified_leads,
                    COUNT(CASE WHEN status = 'Closed Won' THEN 1 END) as closed_won,
                    COUNT(CASE WHEN status = 'Closed Lost' THEN 1 END) as closed_lost,
                    COUNT(CASE WHEN status = 'Dropped' THEN 1 END) as dropped,
                    CASE 
                        WHEN COUNT(*) > 0 THEN 
                            ROUND(COUNT(CASE WHEN status = 'Closed Won' THEN 1 END) * 100.0 / COUNT(*), 2)
                        ELSE 0 
                    END as conversion_rate
                FROM leads
                {where_clause}
            """, *params)
            
            return dict(result)