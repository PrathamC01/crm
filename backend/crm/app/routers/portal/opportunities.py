"""
Enhanced Opportunity management API with Lead-based creation workflow
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date

from ...database.engine import SessionLocal
from ...models import User, Opportunity, SalesProcess
from ...models.opportunity import OpportunityStage, OpportunityStatus
from ...models.sales_process import SalesStage, StageStatus
from ...services.opportunity_service import OpportunityService
from ...schemas.opportunity import (
    OpportunityResponse,
    OpportunityListResponse,
    OpportunityCreate,
    SalesProcessUpdate,
    OpportunityStats,
)
from ...schemas.auth import StandardResponse
from ...utils.auth import get_current_user
from ...utils.response import create_response
from ...dependencies.rbac import require_opportunities_read


router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/convert-from-lead/{lead_id}", response_model=OpportunityResponse)
async def convert_lead_to_opportunity(
    lead_id: int,
    conversion_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Convert a qualified and approved lead to opportunity.
    This is the ONLY way to create opportunities.
    """
    try:
        opportunity_service = OpportunityService(db)

        # Check if user can convert this lead
        permission_check = opportunity_service.can_user_convert_lead(
            current_user.id, lead_id
        )
        if not permission_check.get("can_convert", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=permission_check.get("reason", "Cannot convert lead"),
            )

        # Determine who approved (Admin/Reviewer can self-approve)
        approved_by = None
        if current_user.role.name in ["Admin", "Reviewer"]:
            approved_by = current_user.id

        opportunity = opportunity_service.create_opportunity_from_lead(
            lead_id=lead_id,
            converted_by_user_id=current_user.id,
            approved_by_user_id=approved_by,
            conversion_notes=conversion_notes,
        )

        return create_response(
            success=True,
            message="Lead successfully converted to opportunity",
            data={"opportunity": opportunity},
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/check-conversion-eligibility/{lead_id}")
async def check_lead_conversion_eligibility(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check if user can convert specific lead to opportunity"""
    try:
        opportunity_service = OpportunityService(db)
        eligibility = opportunity_service.can_user_convert_lead(
            current_user.id, lead_id
        )

        return create_response(
            success=True, message="Conversion eligibility checked", data=eligibility
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/", response_model=StandardResponse)
async def get_opportunities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None),
    stage_filter: Optional[str] = Query(None),
    user_filter: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_opportunities_read),
):
    """Get paginated list of opportunities with filters"""
    try:
        opportunity_service = OpportunityService(db)

        # Role-based filtering - simplified for session-based auth
        result = opportunity_service.get_opportunities_list(
            skip=skip,
            limit=limit,
            status_filter=status_filter,
            stage_filter=stage_filter,
            user_filter=user_filter,
            search=search,
        )
        oppt = [
            OpportunityResponse.from_orm(opportunity)
            for opportunity in result.get("opportunities")
        ]
        # print({"opportunities": oppt, **result})
        return create_response(
            success=True,
            message="Opportunities retrieved successfully",
            data={
                "opportunities": [
                    OpportunityResponse.from_orm(o) for o in result.get("opportunities")
                ],
                "total": result["total"],
                "skip": skip,
                "limit": limit,
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{opportunity_id}", response_model=StandardResponse)
async def get_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get opportunity by ID with all related data"""
    try:
        opportunity_service = OpportunityService(db)
        opportunity = opportunity_service.get_opportunity_by_id(opportunity_id)
        print(opportunity)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found"
            )

        # Role-based access control
        if (
            current_user.role.name == "Sales"
            and opportunity.converted_by != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this opportunity",
            )

        return create_response(
            success=True,
            message="Opportunity retrieved successfully",
            data={"opportunity": OpportunityResponse.from_orm(opportunity)},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/pot/{pot_id}", response_model=OpportunityResponse)
async def get_opportunity_by_pot_id(
    pot_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get opportunity by POT ID"""
    try:
        opportunity_service = OpportunityService(db)
        opportunity = opportunity_service.get_opportunity_by_pot_id(pot_id)

        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found"
            )

        # Role-based access control
        if (
            current_user.role.name == "Sales"
            and opportunity.converted_by != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this opportunity",
            )

        return create_response(
            success=True,
            message="Opportunity retrieved successfully",
            data={"opportunity": opportunity},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/{opportunity_id}/sales-process/stage/{stage}")
async def update_sales_stage(
    opportunity_id: int,
    stage: str,
    stage_data: SalesProcessUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update sales process stage"""
    try:
        opportunity_service = OpportunityService(db)

        # Get opportunity and check access
        opportunity = opportunity_service.get_opportunity_by_id(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found"
            )

        # Role-based access control
        if (
            current_user.role.name == "Sales"
            and opportunity.converted_by != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

        # Convert string stage to enum
        try:
            sales_stage = SalesStage(stage)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid stage"
            )

        # Convert string status to enum
        try:
            stage_status = StageStatus(stage_data.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status"
            )

        sales_process = opportunity_service.update_sales_stage(
            opportunity_id=opportunity_id,
            stage=sales_stage,
            status=stage_status,
            completion_date=stage_data.completion_date,
            comments=stage_data.comments,
            documents=stage_data.documents,
            updated_by=current_user.id,
        )

        return create_response(
            success=True,
            message="Sales stage updated successfully",
            data={"sales_process": sales_process},
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{opportunity_id}/sales-processes")
async def get_sales_processes(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all sales processes for an opportunity"""
    try:
        opportunity_service = OpportunityService(db)

        # Check access
        opportunity = opportunity_service.get_opportunity_by_id(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found"
            )

        if (
            current_user.role.name == "Sales"
            and opportunity.converted_by != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

        sales_processes = opportunity_service.get_sales_processes(opportunity_id)

        return create_response(
            success=True,
            message="Sales processes retrieved successfully",
            data={"sales_processes": sales_processes},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/statistics/overview", response_model=OpportunityStats)
async def get_opportunity_statistics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_opportunities_read),
):
    """Get opportunity statistics"""
    try:
        opportunity_service = OpportunityService(db)
        stats = opportunity_service.get_opportunity_statistics()

        return create_response(
            success=True,
            message="Opportunity statistics retrieved successfully",
            data=stats,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# Note: No direct opportunity creation endpoint - opportunities can only be created by converting leads
