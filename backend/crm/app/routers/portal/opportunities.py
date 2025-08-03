"""
Opportunity Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from ...schemas.opportunity import (
    OpportunityCreate, OpportunityUpdate, OpportunityListResponse,
    OpportunityStageUpdate, OpportunityCloseRequest, OpportunityPipelineSummary
)
from ...schemas.auth import StandardResponse
from ...dependencies.rbac import require_opportunities_read, require_opportunities_write
from ...services.opportunity_service import OpportunityService
from ...dependencies.database import get_postgres_pool

router = APIRouter(prefix="/api/opportunities", tags=["Opportunity Management"])

async def get_opportunity_service(postgres_pool = Depends(get_postgres_pool)) -> OpportunityService:
    return OpportunityService(postgres_pool)

@router.get("/", response_model=StandardResponse)
async def get_opportunities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    company_id: Optional[str] = Query(None),
    lead_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_opportunities_read),
    opportunity_service: OpportunityService = Depends(get_opportunity_service)
):
    """Get all opportunities with pagination and filtering"""
    try:
        if company_id:
            opportunities = await opportunity_service.get_opportunities_by_company(company_id, skip, limit)
        elif lead_id:
            opportunities = await opportunity_service.get_opportunities_by_lead(lead_id, skip, limit)
        else:
            opportunities = await opportunity_service.get_opportunities(skip, limit, stage, status, search)
        
        total = await opportunity_service.get_opportunity_count(stage, status, search)
        
        return StandardResponse(
            status=True,
            message="Opportunities retrieved successfully",
            data={
                "opportunities": opportunities,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{opportunity_id}", response_model=StandardResponse)
async def get_opportunity(
    opportunity_id: str,
    current_user: dict = Depends(require_opportunities_read),
    opportunity_service: OpportunityService = Depends(get_opportunity_service)
):
    """Get opportunity by ID"""
    try:
        opportunity = await opportunity_service.get_opportunity_by_id(opportunity_id)
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

@router.post("/", response_model=StandardResponse)
async def create_opportunity(
    opportunity_data: OpportunityCreate,
    current_user: dict = Depends(require_opportunities_write),
    opportunity_service: OpportunityService = Depends(get_opportunity_service)
):
    """Create new opportunity"""
    try:
        opportunity = await opportunity_service.create_opportunity(opportunity_data, current_user["id"])
        
        return StandardResponse(
            status=True,
            message="Opportunity created successfully",
            data=opportunity
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{opportunity_id}", response_model=StandardResponse)
async def update_opportunity(
    opportunity_id: str,
    opportunity_data: OpportunityUpdate,
    current_user: dict = Depends(require_opportunities_write),
    opportunity_service: OpportunityService = Depends(get_opportunity_service)
):
    """Update opportunity information"""
    try:
        opportunity = await opportunity_service.update_opportunity(
            opportunity_id, opportunity_data, current_user["id"]
        )
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        return StandardResponse(
            status=True,
            message="Opportunity updated successfully",
            data=opportunity
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{opportunity_id}/stage", response_model=StandardResponse)
async def update_opportunity_stage(
    opportunity_id: str,
    stage_data: OpportunityStageUpdate,
    current_user: dict = Depends(require_opportunities_write),
    opportunity_service: OpportunityService = Depends(get_opportunity_service)
):
    """Update opportunity stage"""
    try:
        opportunity = await opportunity_service.update_stage(
            opportunity_id, 
            stage_data.stage.value, 
            current_user["id"], 
            stage_data.notes
        )
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        return StandardResponse(
            status=True,
            message="Opportunity stage updated successfully",
            data=opportunity
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{opportunity_id}/close", response_model=StandardResponse)
async def close_opportunity(
    opportunity_id: str,
    close_data: OpportunityCloseRequest,
    current_user: dict = Depends(require_opportunities_write),
    opportunity_service: OpportunityService = Depends(get_opportunity_service)
):
    """Close opportunity (Won/Lost/Dropped)"""
    try:
        opportunity = await opportunity_service.close_opportunity(
            opportunity_id,
            close_data.status,
            close_data.close_date.isoformat(),
            current_user["id"],
            close_data.notes
        )
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        return StandardResponse(
            status=True,
            message=f"Opportunity closed as {close_data.status}",
            data=opportunity
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{opportunity_id}", response_model=StandardResponse)
async def delete_opportunity(
    opportunity_id: str,
    current_user: dict = Depends(require_opportunities_write),
    opportunity_service: OpportunityService = Depends(get_opportunity_service)
):
    """Soft delete opportunity"""
    try:
        deleted = await opportunity_service.delete_opportunity(opportunity_id, current_user["id"])
        if not deleted:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        return StandardResponse(
            status=True,
            message="Opportunity deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pipeline/summary", response_model=StandardResponse)
async def get_pipeline_summary(
    user_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_opportunities_read),
    opportunity_service: OpportunityService = Depends(get_opportunity_service)
):
    """Get opportunity pipeline summary"""
    try:
        summary = await opportunity_service.get_pipeline_summary(user_id)
        
        return StandardResponse(
            status=True,
            message="Pipeline summary retrieved successfully",
            data=summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/metrics", response_model=StandardResponse)
async def get_opportunity_metrics(
    user_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_opportunities_read),
    opportunity_service: OpportunityService = Depends(get_opportunity_service)
):
    """Get opportunity metrics and analytics"""
    try:
        metrics = await opportunity_service.get_opportunity_metrics(user_id)
        
        return StandardResponse(
            status=True,
            message="Opportunity metrics retrieved successfully",
            data=metrics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))