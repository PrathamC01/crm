"""
Leads Module API Routes
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from ..schemas.common import StandardResponse, BaseFilter, ApprovalRequest
from ..schemas.leads import *
from ..dependencies.auth import get_current_user, require_permission
from ..services.leads_service import LeadsService

router = APIRouter(prefix="/api/leads", tags=["leads"])

# Contact Management
@router.get("/contacts", response_model=StandardResponse)
async def list_contacts(
    filters: BaseFilter = Depends(),
    company_id: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
    leads_service: LeadsService = Depends()
):
    """Get paginated list of contacts"""
    try:
        contacts = await leads_service.get_contacts(filters, company_id)
        return StandardResponse(
            status=True,
            message="Contacts retrieved successfully",
            data=contacts
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contacts", response_model=StandardResponse)
async def create_contact(
    contact_data: ContactCreate,
    current_user: dict = Depends(require_permission("leads", "write")),
    leads_service: LeadsService = Depends()
):
    """Create new contact"""
    try:
        contact = await leads_service.create_contact(contact_data, current_user["id"])
        return StandardResponse(
            status=True,
            message="Contact created successfully",
            data=contact
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contacts/{contact_id}", response_model=StandardResponse)
async def get_contact(
    contact_id: int,
    current_user: dict = Depends(get_current_user),
    leads_service: LeadsService = Depends()
):
    """Get contact by ID"""
    try:
        contact = await leads_service.get_contact_by_id(contact_id)
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        return StandardResponse(
            status=True,
            message="Contact retrieved successfully",
            data=contact
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/contacts/{contact_id}", response_model=StandardResponse)
async def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    current_user: dict = Depends(require_permission("leads", "write")),
    leads_service: LeadsService = Depends()
):
    """Update contact"""
    try:
        contact = await leads_service.update_contact(contact_id, contact_data, current_user["id"])
        return StandardResponse(
            status=True,
            message="Contact updated successfully",
            data=contact
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Company Management
@router.get("/companies", response_model=StandardResponse)
async def list_companies(
    filters: BaseFilter = Depends(),
    industry_id: Optional[int] = Query(None),
    city_id: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
    leads_service: LeadsService = Depends()
):
    """Get paginated list of companies"""
    try:
        companies = await leads_service.get_companies(filters, industry_id, city_id)
        return StandardResponse(
            status=True,
            message="Companies retrieved successfully",
            data=companies
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/companies", response_model=StandardResponse)
async def create_company(
    company_data: CompanyCreate,
    current_user: dict = Depends(require_permission("leads", "write")),
    leads_service: LeadsService = Depends()
):
    """Create new company"""
    try:
        company = await leads_service.create_company(company_data, current_user["id"])
        return StandardResponse(
            status=True,
            message="Company created successfully",
            data=company
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/companies/{company_id}", response_model=StandardResponse)
async def get_company(
    company_id: int,
    current_user: dict = Depends(get_current_user),
    leads_service: LeadsService = Depends()
):
    """Get company by ID with contacts"""
    try:
        company = await leads_service.get_company_with_contacts(company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return StandardResponse(
            status=True,
            message="Company retrieved successfully",
            data=company
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/companies/{company_id}", response_model=StandardResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    current_user: dict = Depends(require_permission("leads", "write")),
    leads_service: LeadsService = Depends()
):
    """Update company"""
    try:
        company = await leads_service.update_company(company_id, company_data, current_user["id"])
        return StandardResponse(
            status=True,
            message="Company updated successfully",
            data=company
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Lead Management
@router.get("/", response_model=StandardResponse)
async def list_leads(
    filters: BaseFilter = Depends(),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assigned_to: Optional[int] = Query(None),
    company_id: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
    leads_service: LeadsService = Depends()
):
    """Get paginated list of leads"""
    try:
        leads = await leads_service.get_leads(
            filters, status, priority, assigned_to, company_id, current_user["id"]
        )
        return StandardResponse(
            status=True,
            message="Leads retrieved successfully",
            data=leads
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=StandardResponse)
async def create_lead(
    lead_data: LeadCreate,
    current_user: dict = Depends(require_permission("leads", "write")),
    leads_service: LeadsService = Depends()
):
    """Create new lead"""
    try:
        lead = await leads_service.create_lead(lead_data, current_user["id"])
        return StandardResponse(
            status=True,
            message="Lead created successfully",
            data=lead
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{lead_id}", response_model=StandardResponse)
async def get_lead(
    lead_id: int,
    current_user: dict = Depends(get_current_user),
    leads_service: LeadsService = Depends()
):
    """Get lead by ID with full details"""
    try:
        lead = await leads_service.get_lead_with_details(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        return StandardResponse(
            status=True,
            message="Lead retrieved successfully",
            data=lead
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{lead_id}", response_model=StandardResponse)
async def update_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    current_user: dict = Depends(require_permission("leads", "write")),
    leads_service: LeadsService = Depends()
):
    """Update lead"""
    try:
        lead = await leads_service.update_lead(lead_id, lead_data, current_user["id"])
        return StandardResponse(
            status=True,
            message="Lead updated successfully",
            data=lead
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{lead_id}/status", response_model=StandardResponse)
async def update_lead_status(
    lead_id: int,
    status_data: LeadStatusUpdate,
    current_user: dict = Depends(require_permission("leads", "write")),
    leads_service: LeadsService = Depends()
):
    """Update lead status"""
    try:
        lead = await leads_service.update_lead_status(
            lead_id, status_data, current_user["id"]
        )
        return StandardResponse(
            status=True,
            message=f"Lead status updated to {status_data.status}",
            data=lead
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{lead_id}/assign", response_model=StandardResponse)
async def assign_lead(
    lead_id: int,
    assignment_data: LeadAssignment,
    current_user: dict = Depends(require_permission("leads", "write")),
    leads_service: LeadsService = Depends()
):
    """Assign lead to user"""
    try:
        lead = await leads_service.assign_lead(
            lead_id, assignment_data.assigned_to, current_user["id"]
        )
        return StandardResponse(
            status=True,
            message="Lead assigned successfully",
            data=lead
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{lead_id}/convert", response_model=StandardResponse)
async def convert_lead_to_opportunity(
    lead_id: int,
    conversion_data: LeadConversion,
    current_user: dict = Depends(require_permission("leads", "write")),
    leads_service: LeadsService = Depends()
):
    """Convert qualified lead to opportunity"""
    try:
        opportunity = await leads_service.convert_to_opportunity(
            lead_id, conversion_data, current_user["id"]
        )
        return StandardResponse(
            status=True,
            message="Lead converted to opportunity successfully",
            data=opportunity
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/overview", response_model=StandardResponse)
async def get_leads_stats(
    current_user: dict = Depends(get_current_user),
    leads_service: LeadsService = Depends()
):
    """Get lead statistics overview"""
    try:
        stats = await leads_service.get_lead_stats(current_user["id"])
        return StandardResponse(
            status=True,
            message="Lead statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))