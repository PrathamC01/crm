"""
Contact Management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from ...schemas.contact import (
    ContactCreate,
    ContactUpdate,
    ContactListResponse,
    ContactResponse,
)
from ...schemas.auth import StandardResponse
from ...dependencies.rbac import require_contacts_read, require_contacts_write
from ...services.contact_service import ContactService
from ...dependencies.database import get_postgres_db

router = APIRouter(prefix="/api/contacts", tags=["Contact Management"])


async def get_contact_service(postgres_pool=Depends(get_postgres_db)) -> ContactService:
    return ContactService(postgres_pool)


@router.get("/", response_model=StandardResponse)
async def get_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    company_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_contacts_read),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Get all contacts with pagination and search"""
    try:
        if company_id:
            contacts = contact_service.get_contacts_by_company(company_id, skip, limit)
        else:
            contacts = contact_service.get_contacts(skip, limit, search)
        total = contact_service.get_contact_count(search)

        contact_response_list = [
            ContactResponse(
                **contact.__dict__,
                company_name=contact.company.name if contact.company else None
            )
            for contact in contacts
        ]

        return StandardResponse(
            status=True,
            message="Contacts retrieved successfully",
            # data={"contacts": contacts, "total": total, "skip": skip, "limit": limit},
            data=ContactListResponse(
                contacts=contact_response_list, total=total, skip=skip, limit=limit
            ),
        )
    except Exception as e:
        print(e)


@router.get("/{contact_id}", response_model=StandardResponse)
async def get_contact(
    contact_id: str,
    current_user: dict = Depends(require_contacts_read),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Get contact by ID"""
    try:
        contact = contact_service.get_contact_by_id(contact_id)
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")

        return StandardResponse(
            status=True, message="Contact retrieved successfully", data=contact
        )
    except HTTPException:
        raise
    except Exception as e:
        print(e)


@router.post("/", response_model=StandardResponse)
async def create_contact(
    contact_data: ContactCreate,
    current_user: dict = Depends(require_contacts_write),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Create new contact"""
    try:
        contact = contact_service.create_contact(
            contact_data.dict(exclude_unset=True), current_user["id"]
        )

        return StandardResponse(
            status=True, message="Contact created successfully"
        )
    except Exception as e:
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Email already exists")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{contact_id}", response_model=StandardResponse)
async def update_contact(
    contact_id: str,
    contact_data: ContactUpdate,
    current_user: dict = Depends(require_contacts_write),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Update contact information"""
    try:
        contact = contact_service.update_contact(
            contact_id, contact_data.dict(exclude_unset=True), current_user["id"]
        )
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")

        return StandardResponse(status=True, message="Contact updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(e)


@router.delete("/{contact_id}", response_model=StandardResponse)
async def delete_contact(
    contact_id: str,
    current_user: dict = Depends(require_contacts_write),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Soft delete contact"""
    try:
        deleted = contact_service.delete_contact(contact_id, current_user["id"])
        if not deleted:
            raise HTTPException(status_code=404, detail="Contact not found")

        return StandardResponse(status=True, message="Contact deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(e)


@router.get("/company/{company_id}/decision-makers", response_model=StandardResponse)
async def get_decision_makers(
    company_id: str,
    current_user: dict = Depends(require_contacts_read),
    contact_service: ContactService = Depends(get_contact_service),
):
    """Get decision makers for a company (needed for opportunity creation)"""
    try:
        contacts = contact_service.get_decision_makers(company_id)

        return StandardResponse(
            status=True,
            message="Decision makers retrieved successfully",
            data={
                "decision_makers": [
                    ContactResponse.from_orm(contact) for contact in contacts
                ]
            },
        )
    except Exception as e:
        print(e)
