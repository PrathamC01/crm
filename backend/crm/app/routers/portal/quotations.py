"""
Quotation management API for opportunities
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date

from ...database.engine import SessionLocal
from ...models import User, Opportunity, Quotation
from ...services.quotation_service import QuotationService
from ...services.opportunity_service import OpportunityService
from ...schemas.quotation import (
    QuotationResponse, QuotationListResponse, QuotationCreate,
    QuotationUpdate, QuotationStats
)
from ...utils.auth import get_current_user
from ...utils.response import create_response


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/opportunity/{opportunity_id}/quotations", response_model=QuotationResponse)
async def create_quotation(
    opportunity_id: int,
    quotation_data: QuotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new quotation for opportunity"""
    try:
        quotation_service = QuotationService(db)
        opportunity_service = OpportunityService(db)
        
        # Check if opportunity exists and user has access
        opportunity = opportunity_service.get_opportunity_by_id(opportunity_id)
        if not opportunity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
        
        # Role-based access control
        if current_user.role.name == "Sales" and opportunity.converted_by != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        quotation = quotation_service.create_quotation(
            opportunity_id=opportunity_id,
            quotation_data=quotation_data.dict(),
            created_by=current_user.id
        )
        
        return create_response(
            success=True,
            message="Quotation created successfully",
            data={"quotation": quotation}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/opportunity/{opportunity_id}/quotations")
async def get_opportunity_quotations(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all quotations for an opportunity"""
    try:
        quotation_service = QuotationService(db)
        opportunity_service = OpportunityService(db)
        
        # Check access
        opportunity = opportunity_service.get_opportunity_by_id(opportunity_id)
        if not opportunity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
        
        if current_user.role.name == "Sales" and opportunity.converted_by != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        quotations = quotation_service.get_quotations_by_opportunity(opportunity_id)
        
        return create_response(
            success=True,
            message="Quotations retrieved successfully",
            data={"quotations": quotations}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/quotations", response_model=QuotationListResponse)
async def get_quotations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None),
    opportunity_filter: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paginated list of quotations with filters"""
    try:
        quotation_service = QuotationService(db)
        
        result = quotation_service.get_quotations_list(
            skip=skip,
            limit=limit,
            status_filter=status_filter,
            opportunity_filter=opportunity_filter,
            search=search
        )
        
        # Filter results based on user role
        if current_user.role.name == "Sales":
            # Filter to only show quotations from opportunities they converted
            filtered_quotations = []
            for quotation in result["quotations"]:
                if quotation.opportunity.converted_by == current_user.id:
                    filtered_quotations.append(quotation)
            result["quotations"] = filtered_quotations
            result["total"] = len(filtered_quotations)
        
        return create_response(
            success=True,
            message="Quotations retrieved successfully",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/quotations/{quotation_id}", response_model=QuotationResponse)
async def get_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get quotation by ID"""
    try:
        quotation_service = QuotationService(db)
        quotation = quotation_service.get_quotation_by_id(quotation_id)
        
        if not quotation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found")
        
        # Role-based access control
        if current_user.role.name == "Sales" and quotation.opportunity.converted_by != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        return create_response(
            success=True,
            message="Quotation retrieved successfully",
            data={"quotation": quotation}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/quotations/by-id/{quotation_id}", response_model=QuotationResponse)
async def get_quotation_by_quotation_id(
    quotation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get quotation by quotation ID (QUO-YYYY-XXXX)"""
    try:
        quotation_service = QuotationService(db)
        quotation = quotation_service.get_quotation_by_quotation_id(quotation_id)
        
        if not quotation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found")
        
        # Role-based access control
        if current_user.role.name == "Sales" and quotation.opportunity.converted_by != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        return create_response(
            success=True,
            message="Quotation retrieved successfully",
            data={"quotation": quotation}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/quotations/{quotation_id}", response_model=QuotationResponse)
async def update_quotation(
    quotation_id: int,
    quotation_data: QuotationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update quotation"""
    try:
        quotation_service = QuotationService(db)
        
        # Check access
        quotation = quotation_service.get_quotation_by_id(quotation_id)
        if not quotation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found")
        
        if current_user.role.name == "Sales" and quotation.opportunity.converted_by != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        updated_quotation = quotation_service.update_quotation(
            quotation_id=quotation_id,
            quotation_data=quotation_data.dict(exclude_unset=True),
            updated_by=current_user.id
        )
        
        return create_response(
            success=True,
            message="Quotation updated successfully",
            data={"quotation": updated_quotation}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/quotations/{quotation_id}/submit")
async def submit_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit quotation for approval"""
    try:
        quotation_service = QuotationService(db)
        
        # Check access
        quotation = quotation_service.get_quotation_by_id(quotation_id)
        if not quotation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found")
        
        if current_user.role.name == "Sales" and quotation.opportunity.converted_by != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        submitted_quotation = quotation_service.submit_quotation(
            quotation_id=quotation_id,
            submitted_by=current_user.id
        )
        
        return create_response(
            success=True,
            message="Quotation submitted successfully",
            data={"quotation": submitted_quotation}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/quotations/{quotation_id}/approve")
async def approve_quotation(
    quotation_id: int,
    approval_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve quotation (Admin/Reviewer only)"""
    try:
        if current_user.role.name not in ["Admin", "Reviewer"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin or Reviewer can approve quotations"
            )
        
        quotation_service = QuotationService(db)
        
        approved_quotation = quotation_service.approve_quotation(
            quotation_id=quotation_id,
            approved_by=current_user.id,
            approval_notes=approval_notes
        )
        
        return create_response(
            success=True,
            message="Quotation approved successfully",
            data={"quotation": approved_quotation}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/quotations/{quotation_id}/reject")
async def reject_quotation(
    quotation_id: int,
    rejection_reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reject quotation (Admin/Reviewer only)"""
    try:
        if current_user.role.name not in ["Admin", "Reviewer"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin or Reviewer can reject quotations"
            )
        
        quotation_service = QuotationService(db)
        
        rejected_quotation = quotation_service.reject_quotation(
            quotation_id=quotation_id,
            rejected_by=current_user.id,
            rejection_reason=rejection_reason
        )
        
        return create_response(
            success=True,
            message="Quotation rejected successfully",
            data={"quotation": rejected_quotation}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/quotations/{quotation_id}/revise")
async def create_quotation_revision(
    quotation_id: int,
    quotation_data: QuotationCreate,
    revision_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create revision of quotation"""
    try:
        quotation_service = QuotationService(db)
        
        # Check access
        quotation = quotation_service.get_quotation_by_id(quotation_id)
        if not quotation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found")
        
        if current_user.role.name == "Sales" and quotation.opportunity.converted_by != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        revision = quotation_service.create_quotation_revision(
            parent_quotation_id=quotation_id,
            quotation_data=quotation_data.dict(),
            created_by=current_user.id,
            revision_notes=revision_notes
        )
        
        return create_response(
            success=True,
            message="Quotation revision created successfully",
            data={"quotation": revision}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/quotations/{quotation_id}")
async def delete_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete quotation (soft delete)"""
    try:
        quotation_service = QuotationService(db)
        
        # Check access
        quotation = quotation_service.get_quotation_by_id(quotation_id)
        if not quotation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found")
        
        if current_user.role.name == "Sales" and quotation.opportunity.converted_by != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        success = quotation_service.delete_quotation(
            quotation_id=quotation_id,
            deleted_by=current_user.id
        )
        
        return create_response(
            success=success,
            message="Quotation deleted successfully",
            data=None
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/statistics/quotations", response_model=QuotationStats)
async def get_quotation_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get quotation statistics"""
    try:
        if current_user.role.name not in ["Admin", "Reviewer"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view statistics"
            )
        
        quotation_service = QuotationService(db)
        stats = quotation_service.get_quotation_statistics()
        
        return create_response(
            success=True,
            message="Quotation statistics retrieved successfully",
            data=stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))