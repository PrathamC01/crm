"""
Opportunity management service
"""
from typing import Optional, List
from ..models.opportunity import Opportunity
from ..schemas.opportunity import OpportunityCreate, OpportunityUpdate

class OpportunityService:
    def __init__(self, postgres_pool):
        self.postgres_pool = postgres_pool
    
    async def create_opportunity(self, opportunity_data: OpportunityCreate, created_by: Optional[str] = None) -> dict:
        """Create a new opportunity"""
        async with self.postgres_pool.acquire() as conn:
            opportunity = await Opportunity.create_opportunity(
                conn,
                **opportunity_data.dict(),
                created_by=created_by
            )
            return dict(opportunity)
    
    async def get_opportunity_by_id(self, opportunity_id: str) -> Optional[dict]:
        """Get opportunity by ID"""
        async with self.postgres_pool.acquire() as conn:
            opportunity = await Opportunity.find_by_id(conn, opportunity_id)
            return dict(opportunity) if opportunity else None
    
    async def get_opportunities(self, skip: int = 0, limit: int = 100, stage: str = None, 
                              status: str = None, search: str = None) -> List[dict]:
        """Get all opportunities with optional filtering"""
        async with self.postgres_pool.acquire() as conn:
            opportunities = await Opportunity.get_all(conn, skip, limit, stage, status, search)
            return [dict(opportunity) for opportunity in opportunities]
    
    async def get_opportunities_by_company(self, company_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get opportunities by company"""
        async with self.postgres_pool.acquire() as conn:
            opportunities = await Opportunity.get_by_company(conn, company_id, skip, limit)
            return [dict(opportunity) for opportunity in opportunities]
    
    async def get_opportunities_by_lead(self, lead_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get opportunities by lead"""
        async with self.postgres_pool.acquire() as conn:
            opportunities = await Opportunity.get_by_lead(conn, lead_id, skip, limit)
            return [dict(opportunity) for opportunity in opportunities]
    
    async def update_opportunity(self, opportunity_id: str, opportunity_data: OpportunityUpdate, updated_by: str) -> Optional[dict]:
        """Update opportunity information"""
        async with self.postgres_pool.acquire() as conn:
            opportunity = await Opportunity.update_opportunity(
                conn, 
                opportunity_id, 
                updated_by, 
                **opportunity_data.dict(exclude_unset=True)
            )
            return dict(opportunity) if opportunity else None
    
    async def delete_opportunity(self, opportunity_id: str, deleted_by: str) -> bool:
        """Soft delete opportunity"""
        async with self.postgres_pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE opportunities 
                SET is_active = false, deleted_on = CURRENT_TIMESTAMP, deleted_by = $1
                WHERE id = $2 AND is_active = true
            """, deleted_by, opportunity_id)
            return result == "UPDATE 1"
    
    async def update_stage(self, opportunity_id: str, stage: str, updated_by: str, notes: str = None) -> Optional[dict]:
        """Update opportunity stage"""
        async with self.postgres_pool.acquire() as conn:
            # Get current stage for validation
            current = await conn.fetchrow(
                "SELECT stage FROM opportunities WHERE id = $1 AND is_active = true",
                opportunity_id
            )
            
            if not current:
                return None
            
            # Validate stage transition
            from ..utils.validators import validate_opportunity_stage_transition
            is_valid, error_msg = validate_opportunity_stage_transition(current['stage'], stage)
            if not is_valid:
                raise ValueError(error_msg)
            
            # Update stage and notes
            update_data = {'stage': stage}
            if notes:
                current_notes = await conn.fetchval(
                    "SELECT notes FROM opportunities WHERE id = $1",
                    opportunity_id
                )
                new_notes = f"{current_notes}\n[Stage {stage}] {notes}" if current_notes else f"[Stage {stage}] {notes}"
                update_data['notes'] = new_notes
            
            opportunity = await Opportunity.update_opportunity(
                conn, opportunity_id, updated_by, **update_data
            )
            return dict(opportunity) if opportunity else None
    
    async def close_opportunity(self, opportunity_id: str, status: str, close_date: str, updated_by: str, notes: str = None) -> Optional[dict]:
        """Close opportunity"""
        async with self.postgres_pool.acquire() as conn:
            update_data = {
                'status': status,
                'close_date': close_date
            }
            
            if notes:
                current_notes = await conn.fetchval(
                    "SELECT notes FROM opportunities WHERE id = $1",
                    opportunity_id
                )
                new_notes = f"{current_notes}\n[Closed {status}] {notes}" if current_notes else f"[Closed {status}] {notes}"
                update_data['notes'] = new_notes
            
            opportunity = await Opportunity.update_opportunity(
                conn, opportunity_id, updated_by, **update_data
            )
            return dict(opportunity) if opportunity else None
    
    async def get_opportunity_count(self, stage: str = None, status: str = None, search: str = None) -> int:
        """Get total count of opportunities"""
        async with self.postgres_pool.acquire() as conn:
            base_query = """
                SELECT COUNT(*) FROM opportunities o
                LEFT JOIN companies c ON o.company_id = c.id
                LEFT JOIN contacts cont ON o.contact_id = cont.id
                WHERE o.is_active = true AND o.deleted_on IS NULL
            """
            
            conditions = []
            params = []
            
            if stage:
                conditions.append("o.stage = $" + str(len(params) + 1))
                params.append(stage)
            
            if status:
                conditions.append("o.status = $" + str(len(params) + 1))
                params.append(status)
            
            if search:
                conditions.append("(o.name ILIKE $" + str(len(params) + 1) + " OR c.name ILIKE $" + str(len(params) + 1) + " OR cont.full_name ILIKE $" + str(len(params) + 1) + ")")
                params.append(f"%{search}%")
            
            if conditions:
                base_query += " AND " + " AND ".join(conditions)
            
            result = await conn.fetchval(base_query, *params)
            return result or 0
    
    async def get_pipeline_summary(self, user_id: str = None) -> dict:
        """Get opportunity pipeline summary"""
        async with self.postgres_pool.acquire() as conn:
            return await Opportunity.get_pipeline_summary(conn, user_id)
    
    async def get_opportunity_metrics(self, user_id: str = None) -> dict:
        """Get opportunity metrics and analytics"""
        async with self.postgres_pool.acquire() as conn:
            where_clause = "WHERE o.is_active = true AND o.deleted_on IS NULL"
            params = []
            
            if user_id:
                where_clause += " AND o.created_by = $1"
                params.append(user_id)
            
            result = await conn.fetchrow(f"""
                SELECT 
                    COUNT(*) as total_opportunities,
                    COUNT(CASE WHEN o.status = 'Won' THEN 1 END) as won_opportunities,
                    COUNT(CASE WHEN o.status = 'Lost' THEN 1 END) as lost_opportunities,
                    CASE 
                        WHEN COUNT(CASE WHEN o.status IN ('Won', 'Lost') THEN 1 END) > 0 THEN 
                            ROUND(COUNT(CASE WHEN o.status = 'Won' THEN 1 END) * 100.0 / COUNT(CASE WHEN o.status IN ('Won', 'Lost') THEN 1 END), 2)
                        ELSE 0 
                    END as win_rate,
                    AVG(CASE WHEN o.amount IS NOT NULL AND o.status = 'Won' THEN o.amount ELSE NULL END) as avg_deal_size,
                    SUM(CASE WHEN o.status = 'Open' AND o.amount IS NOT NULL THEN o.amount ELSE 0 END) as pipeline_value,
                    SUM(CASE WHEN o.status = 'Open' AND o.amount IS NOT NULL THEN o.amount * o.probability / 100.0 ELSE 0 END) as forecasted_revenue
                FROM opportunities o
                {where_clause}
            """, *params)
            
            return dict(result)