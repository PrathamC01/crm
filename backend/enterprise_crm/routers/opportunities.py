"""
Opportunities Module API Routes
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from ..schemas.common import StandardResponse, BaseFilter, ApprovalRequest
from ..schemas.opportunities import *
from ..dependencies.auth import get_current_user, require_permission
from ..services.opportunities_service import OpportunitiesService

router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])

# Opportunity Management
@router.get("/", response_model=StandardResponse)
async def list_opportunities(
    filters: BaseFilter = Depends(),
    status: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    assigned_to: Optional[int] = Query(None),
    company_id: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
    opportunities_service: OpportunitiesService = Depends()
):
    """Get paginated list of opportunities"""
    try:
        opportunities = await opportunities_service.get_opportunities(
            filters, status, stage, assigned_to, company_id, current_user["id"]
        )
        return StandardResponse(
            status=True,
            message="Opportunities retrieved successfully",
            data=opportunities
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=StandardResponse)
async def create_opportunity(
    opportunity_data: OpportunityCreate,
    current_user: dict = Depends(require_permission("opportunities", "write")),
    opportunities_service: OpportunitiesService = Depends()
):
    """Create new opportunity"""
    try:
        opportunity = await opportunities_service.create_opportunity(
            opportunity_data, current_user["id"]
        )
        return StandardResponse(
            status=True,
            message="Opportunity created successfully",
            data=opportunity
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{opportunity_id}", response_model=StandardResponse)
async def get_opportunity(
    opportunity_id: int,
    current_user: dict = Depends(get_current_user),
    opportunities_service: OpportunitiesService = Depends()
):
    """Get opportunity by ID with full details"""
    try:
        opportunity = await opportunities_service.get_opportunity_with_details(opportunity_id)
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        return StandardResponse(
            status=True,
            message="Opportunity retrieved successfully",
            data=opportunity
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{opportunity_id}", response_model=StandardResponse)
async def update_opportunity(
    opportunity_id: int,
    opportunity_data: OpportunityUpdate,
    current_user: dict = Depends(require_permission("opportunities", "write")),
    opportunities_service: OpportunitiesService = Depends()
):
    """Update opportunity"""
    try:
        opportunity = await opportunities_service.update_opportunity(
            opportunity_id, opportunity_data, current_user["id"]
        )
        return StandardResponse(
            status=True,
            message="Opportunity updated successfully",
            data=opportunity
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{opportunity_id}/status", response_model=StandardResponse)
async def update_opportunity_status(
    opportunity_id: int,
    status_data: OpportunityStatusUpdate,
    current_user: dict = Depends(require_permission("opportunities", "write")),
    opportunities_service: OpportunitiesService = Depends()
):
    """Update opportunity status"""
    try:
        opportunity = await opportunities_service.update_opportunity_status(
            opportunity_id, status_data, current_user["id"]
        )
        return StandardResponse(
            status=True,
            message=f"Opportunity status updated to {status_data.status}",
            data=opportunity
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{opportunity_id}/stage", response_model=StandardResponse)
async def update_opportunity_stage(
    opportunity_id: int,
    stage_data: OpportunityStageUpdate,
    current_user: dict = Depends(require_permission("opportunities", "write")),
    opportunities_service: OpportunitiesService = Depends()
):
    """Update opportunity stage"""
    try:
        opportunity = await opportunities_service.update_opportunity_stage(
            opportunity_id, stage_data, current_user["id"]
        )
        return StandardResponse(
            status=True,
            message=f"Opportunity stage updated to {stage_data.stage}",
            data=opportunity
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Quotation Management
@router.get("/{opportunity_id}/quotations", response_model=StandardResponse)
async def list_quotations(
    opportunity_id: int,
    filters: BaseFilter = Depends(),
    current_user: dict = Depends(get_current_user),
    opportunities_service: OpportunitiesService = Depends()
):
    """Get quotations for opportunity"""
    try:
        quotations = await opportunities_service.get_opportunity_quotations(
            opportunity_id, filters
        )
        return StandardResponse(
            status=True,
            message="Quotations retrieved successfully",
            data=quotations
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{opportunity_id}/quotations", response_model=StandardResponse)
async def create_quotation(
    opportunity_id: int,
    quotation_data: QuotationCreate,
    current_user: dict = Depends(require_permission("opportunities", "write")),
    opportunities_service: OpportunitiesService = Depends()
):
    """Create quotation for opportunity"""
    try:
        quotation = await opportunities_service.create_quotation(
            opportunity_id, quotation_data, current_user["id"]
        )
        return StandardResponse(
            status=True,
            message="Quotation created successfully",
            data=quotation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quotations/{quotation_id}", response_model=StandardResponse)
async def get_quotation(
    quotation_id: int,
    current_user: dict = Depends(get_current_user),
    opportunities_service: OpportunitiesService = Depends()
):
    """Get quotation by ID with line items"""
    try:
        quotation = await opportunities_service.get_quotation_with_details(quotation_id)
        if not quotation:
            raise HTTPException(status_code=404, detail="Quotation not found")
        return StandardResponse(
            status=True,
            message="Quotation retrieved successfully",
            data=quotation
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/quotations/{quotation_id}", response_model=StandardResponse)
async def update_quotation(
    quotation_id: int,
    quotation_data: QuotationUpdate,
    current_user: dict = Depends(require_permission("opportunities", "write")),
    opportunities_service: OpportunitiesService = Depends()
):
    """Update quotation"""
    try:
        quotation = await opportunities_service.update_quotation(
            quotation_id, quotation_data, current_user["id"]
        )
        return StandardResponse(
            status=True,
            message="Quotation updated successfully",
            data=quotation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quotations/{quotation_id}/submit", response_model=StandardResponse)
async def submit_quotation(
    quotation_id: int,
    current_user: dict = Depends(require_permission("opportunities", "write")),
    opportunities_service: OpportunitiesService = Depends()
):
    """Submit quotation for approval"""
    try:
        quotation = await opportunities_service.submit_quotation(
            quotation_id, current_user["id"]
        )
        return StandardResponse(
            status=True,
            message="Quotation submitted for approval",
            data=quotation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quotations/{quotation_id}/approve", response_model=StandardResponse)
async def approve_quotation(
    quotation_id: int,
    approval_data: ApprovalRequest,
    current_user: dict = Depends(require_permission("opportunities", "approve")),
    opportunities_service: OpportunitiesService = Depends()
):
    """Approve or reject quotation"""
    try:
        quotation = await opportunities_service.approve_quotation(
            quotation_id, approval_data, current_user["id"]
        )
        return StandardResponse(
            status=True,
            message=f"Quotation {approval_data.decision} successfully",
            data=quotation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Quotation Line Items
@router.post("/quotations/{quotation_id}/items", response_model=StandardResponse)
async def add_quotation_item(
    quotation_id: int,
    item_data: QuotationLineItemCreate,
    current_user: dict = Depends(require_permission("opportunities", "write")),
    opportunities_service: OpportunitiesService = Depends()
):
    """Add line item to quotation"""
    try:
        item = await opportunities_service.add_quotation_line_item(
            quotation_id, item_data, current_user["id"]
        )
        return StandardResponse(
            status=True,
            message="Line item added to quotation",
            data=item
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/quotations/items/{item_id}", response_model=StandardResponse)
async def update_quotation_item(
    item_id: int,
    item_data: QuotationLineItemUpdate,
    current_user: dict = Depends(require_permission("opportunities", "write")),
    opportunities_service: OpportunitiesService = Depends()
):
    """Update quotation line item"""
    try:
        item = await opportunities_service.update_quotation_line_item(
            item_id, item_data, current_user["id"]
        )
        return StandardResponse(
            status=True,
            message="Line item updated successfully",
            data=item
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/quotations/items/{item_id}", response_model=StandardResponse)
async def delete_quotation_item(
    item_id: int,
    current_user: dict = Depends(require_permission("opportunities", "write")),
    opportunities_service: OpportunitiesService = Depends()
):
    """Delete quotation line item"""
    try:
        await opportunities_service.delete_quotation_line_item(item_id, current_user["id"])
        return StandardResponse(
            status=True,
            message="Line item deleted successfully",
            data=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics and Reports
@router.get("/stats/overview", response_model=StandardResponse)
async def get_opportunities_stats(
    current_user: dict = Depends(get_current_user),
    opportunities_service: OpportunitiesService = Depends()
):
    """Get opportunities statistics overview"""
    try:
        stats = await opportunities_service.get_opportunity_stats(current_user["id"])
        return StandardResponse(
            status=True,
            message="Opportunity statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/pipeline", response_model=StandardResponse)
async def get_pipeline_report(
    period: Optional[str] = Query("month"),  # month, quarter, year
    current_user: dict = Depends(get_current_user),
    opportunities_service: OpportunitiesService = Depends()
):
    """Get opportunity pipeline report"""
    try:
        pipeline_data = await opportunities_service.get_pipeline_report(
            period, current_user["id"]
        )
        return StandardResponse(
            status=True,
            message="Pipeline report retrieved successfully",
            data=pipeline_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))