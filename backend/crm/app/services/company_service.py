"""
Company management service
"""
from typing import Optional, List
from ..models.company import Company
from ..schemas.company import CompanyCreate, CompanyUpdate

class CompanyService:
    def __init__(self, postgres_pool):
        self.postgres_pool = postgres_pool
    
    async def create_company(self, company_data: CompanyCreate, created_by: Optional[str] = None) -> dict:
        """Create a new company"""
        async with self.postgres_pool.acquire() as conn:
            company = await Company.create_company(
                conn,
                **company_data.dict(),
                created_by=created_by
            )
            return dict(company)
    
    async def get_company_by_id(self, company_id: str) -> Optional[dict]:
        """Get company by ID"""
        async with self.postgres_pool.acquire() as conn:
            company = await Company.find_by_id(conn, company_id)
            return dict(company) if company else None
    
    async def get_companies(self, skip: int = 0, limit: int = 100, search: str = None) -> List[dict]:
        """Get all companies with optional search"""
        async with self.postgres_pool.acquire() as conn:
            companies = await Company.get_all(conn, skip, limit, search)
            return [dict(company) for company in companies]
    
    async def update_company(self, company_id: str, company_data: CompanyUpdate, updated_by: str) -> Optional[dict]:
        """Update company information"""
        async with self.postgres_pool.acquire() as conn:
            company = await Company.update_company(
                conn, 
                company_id, 
                updated_by, 
                **company_data.dict(exclude_unset=True)
            )
            return dict(company) if company else None
    
    async def delete_company(self, company_id: str, deleted_by: str) -> bool:
        """Soft delete company"""
        async with self.postgres_pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE companies 
                SET is_active = false, deleted_on = CURRENT_TIMESTAMP, deleted_by = $1
                WHERE id = $2 AND is_active = true
            """, deleted_by, company_id)
            return result == "UPDATE 1"
    
    async def get_company_count(self, search: str = None) -> int:
        """Get total count of companies"""
        async with self.postgres_pool.acquire() as conn:
            if search:
                result = await conn.fetchval("""
                    SELECT COUNT(*) FROM companies 
                    WHERE is_active = true AND deleted_on IS NULL 
                    AND (name ILIKE $1 OR industry_category ILIKE $1 OR city ILIKE $1)
                """, f"%{search}%")
            else:
                result = await conn.fetchval(
                    "SELECT COUNT(*) FROM companies WHERE is_active = true AND deleted_on IS NULL"
                )
            return result or 0