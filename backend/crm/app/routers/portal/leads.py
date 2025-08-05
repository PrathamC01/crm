"""
Lead Management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from ...schemas.lead import (
    LeadCreate,
    LeadUpdate,
    LeadListResponse,
    LeadResponse,
    LeadStatusUpdate,
    LeadConversion,
    LeadSummary,
    LeadStatus,
)
from ...schemas.auth import StandardResponse
from ...dependencies.rbac import require_leads_read, require_leads_write
from ...services.lead_service import LeadService
from ...dependencies.database import get_postgres_db

router = APIRouter(prefix="/api/leads", tags=["Lead Management"])


async def get_lead_service(postgres_pool=Depends(get_postgres_db)) -> LeadService:
    return LeadService(postgres_pool)


@router.get("/", response_model=StandardResponse)
async def get_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    company_id: Optional[str] = Query(None),
    sales_person_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_leads_read),
    lead_service: LeadService = Depends(get_lead_service),
):
    """Get all leads with pagination and filtering"""
    try:
        if company_id:
            leads = lead_service.get_leads_by_company(company_id, skip, limit)
        elif sales_person_id:
            leads = lead_service.get_leads_by_salesperson(sales_person_id, skip, limit)
        else:
            leads = lead_service.get_leads(skip, limit, status, search)

        total = lead_service.get_lead_count(status, search)

        return StandardResponse(
            status=True,
            message="Leads retrieved successfully",
            # data={
            #     "leads": leads,
            #     "total": total,
            #     "skip": skip,
            #     "limit": limit
            # }
            data=LeadListResponse(
                leads=[
                    LeadResponse(
                        **lead.__dict__,
                        company_name=lead.company.name if lead.company else None,
                    )
                    for lead in leads
                ],
                total=total,
                skip=skip,
                limit=limit,
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{lead_id}", response_model=StandardResponse)
async def get_lead(
    lead_id: str,
    current_user: dict = Depends(require_leads_read),
    lead_service: LeadService = Depends(get_lead_service),
):
    """Get lead by ID"""
    try:
        lead = lead_service.get_lead_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        return StandardResponse(
            status=True, message="Lead retrieved successfully", data=lead
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=StandardResponse)
async def create_lead(
    lead_data: LeadCreate,
    current_user: dict = Depends(require_leads_write),
    lead_service: LeadService = Depends(get_lead_service),
):
    """Create new lead"""
    try:
        lead = lead_service.create_lead(
            lead_data.dict(exclude_unset=True), current_user["id"]
        )

        return StandardResponse(status=True, message="Lead created successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{lead_id}", response_model=StandardResponse)
async def update_lead(
    lead_id: str,
    lead_data: LeadUpdate,
    current_user: dict = Depends(require_leads_write),
    lead_service: LeadService = Depends(get_lead_service),
):
    """Update lead information"""
    try:
        lead = lead_service.update_lead(
            lead_id, lead_data.dict(exclude_unset=True), current_user["id"]
        )
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        return StandardResponse(status=True, message="Lead updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{lead_id}/status", response_model=StandardResponse)
async def update_lead_status(
    lead_id: int,
    status_data: LeadStatusUpdate,
    current_user: dict = Depends(require_leads_write),
    lead_service: LeadService = Depends(get_lead_service),
):
    """Update lead status with notes"""
    try:
        from ...schemas.lead import LeadUpdate

        update_data = LeadUpdate(status=status_data.status, notes=status_data.notes)

        lead = lead_service.update_lead(lead_id, update_data, current_user["id"])
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        return StandardResponse(status=True, message="Lead status updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{lead_id}/convert", response_model=StandardResponse)
async def convert_lead_to_opportunity(
    lead_id: str,
    conversion_data: LeadConversion,
    current_user: dict = Depends(require_leads_write),
    lead_service: LeadService = Depends(get_lead_service),
):
    """Convert lead to opportunity"""
    try:
        opportunity = lead_service.convert_to_opportunity(
            lead_id, conversion_data, current_user["id"]
        )

        return StandardResponse(
            status=True,
            message="Lead converted to opportunity successfully",
            # data=opportunity,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{lead_id}", response_model=StandardResponse)
async def delete_lead(
    lead_id: str,
    current_user: dict = Depends(require_leads_write),
    lead_service: LeadService = Depends(get_lead_service),
):
    """Soft delete lead"""
    try:
        deleted = lead_service.delete_lead(lead_id, current_user["id"])
        if not deleted:
            raise HTTPException(status_code=404, detail="Lead not found")

        return StandardResponse(status=True, message="Lead deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/statistics", response_model=StandardResponse)
async def get_lead_summary(
    sales_person_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_leads_read),
    lead_service: LeadService = Depends(get_lead_service),
):
    """Get lead summary statistics"""
    try:
        summary = lead_service.get_lead_summary(sales_person_id)

        return StandardResponse(
            status=True, message="Lead summary retrieved successfully", data=summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/maintenance/auto-close", response_model=StandardResponse)
async def auto_close_inactive_leads(
    current_user: dict = Depends(require_leads_write),
    lead_service: LeadService = Depends(get_lead_service),
):
    """Auto-close leads inactive for 4 weeks"""
    try:
        count = lead_service.auto_close_inactive_leads()

        return StandardResponse(
            status=True,
            message=f"Auto-closed {count} inactive leads",
            data={"closed_count": count},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
