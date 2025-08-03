"""
Contact management service
"""
from typing import Optional, List
from ..models.contact import Contact
from ..schemas.contact import ContactCreate, ContactUpdate

class ContactService:
    def __init__(self, postgres_pool):
        self.postgres_pool = postgres_pool
    
    async def create_contact(self, contact_data: ContactCreate, created_by: Optional[str] = None) -> dict:
        """Create a new contact"""
        async with self.postgres_pool.acquire() as conn:
            contact = await Contact.create_contact(
                conn,
                **contact_data.dict(),
                created_by=created_by
            )
            return dict(contact)
    
    async def get_contact_by_id(self, contact_id: str) -> Optional[dict]:
        """Get contact by ID"""
        async with self.postgres_pool.acquire() as conn:
            contact = await Contact.find_by_id(conn, contact_id)
            return dict(contact) if contact else None
    
    async def get_contacts(self, skip: int = 0, limit: int = 100, search: str = None) -> List[dict]:
        """Get all contacts with optional search"""
        async with self.postgres_pool.acquire() as conn:
            contacts = await Contact.get_all(conn, skip, limit, search)
            return [dict(contact) for contact in contacts]
    
    async def get_contacts_by_company(self, company_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get contacts by company"""
        async with self.postgres_pool.acquire() as conn:
            contacts = await Contact.get_by_company(conn, company_id, skip, limit)
            return [dict(contact) for contact in contacts]
    
    async def get_decision_makers(self, company_id: str) -> List[dict]:
        """Get decision makers for a company"""
        async with self.postgres_pool.acquire() as conn:
            contacts = await Contact.get_decision_makers_by_company(conn, company_id)
            return [dict(contact) for contact in contacts]
    
    async def update_contact(self, contact_id: str, contact_data: ContactUpdate, updated_by: str) -> Optional[dict]:
        """Update contact information"""
        async with self.postgres_pool.acquire() as conn:
            contact = await Contact.update_contact(
                conn, 
                contact_id, 
                updated_by, 
                **contact_data.dict(exclude_unset=True)
            )
            return dict(contact) if contact else None
    
    async def delete_contact(self, contact_id: str, deleted_by: str) -> bool:
        """Soft delete contact"""
        async with self.postgres_pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE contacts 
                SET is_active = false, deleted_on = CURRENT_TIMESTAMP, deleted_by = $1
                WHERE id = $2 AND is_active = true
            """, deleted_by, contact_id)
            return result == "UPDATE 1"
    
    async def get_contact_count(self, search: str = None) -> int:
        """Get total count of contacts"""
        async with self.postgres_pool.acquire() as conn:
            if search:
                result = await conn.fetchval("""
                    SELECT COUNT(*) FROM contacts c
                    LEFT JOIN companies comp ON c.company_id = comp.id
                    WHERE c.is_active = true AND c.deleted_on IS NULL 
                    AND (c.full_name ILIKE $1 OR c.email ILIKE $1 OR c.designation ILIKE $1 OR comp.name ILIKE $1)
                """, f"%{search}%")
            else:
                result = await conn.fetchval(
                    "SELECT COUNT(*) FROM contacts WHERE is_active = true AND deleted_on IS NULL"
                )
            return result or 0
    
    async def upload_business_card(self, contact_id: str, file_path: str, updated_by: str) -> bool:
        """Upload business card for contact"""
        async with self.postgres_pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE contacts 
                SET business_card_path = $1, updated_on = CURRENT_TIMESTAMP, updated_by = $2
                WHERE id = $3 AND is_active = true
            """, file_path, updated_by, contact_id)
            return result == "UPDATE 1"