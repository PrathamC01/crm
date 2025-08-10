"""
Enhanced Lead Management API endpoints with conversion workflow
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from typing import Optional, List
from datetime import datetime
from ...schemas.lead import (
    LeadCreate,
    LeadUpdate,
    # LeadResponse,
    # LeadListResponse,
    # LeadStatsResponse,
    ConversionRequestSchema,
    ReviewDecisionSchema,
    ConvertToOpportunitySchema,
    # LeadStatus,
    ReviewStatus,
)
from ...schemas.auth import StandardResponse
from ...schemas.opportunity import OpportunityCreate
from ...dependencies.rbac import (
    require_leads_read,
    require_leads_write,
    require_admin_role,
)
from ...services.lead_service import LeadService
from ...services.opportunity_service import OpportunityService
from ...dependencies.database import get_postgres_db

router = APIRouter(prefix="/api/leads", tags=["Enhanced Lead Management"])


async def get_lead_service(
    postgres_pool=Depends(get_postgres_db),
) -> LeadService:
    return LeadService(postgres_pool)


async def get_opportunity_service(
    postgres_pool=Depends(get_postgres_db),
) -> OpportunityService:
    return OpportunityService(postgres_pool)


@router.get("/", response_model=StandardResponse)
async def get_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    company_id: Optional[str] = Query(None),
    review_status: Optional[str] = Query(None),
    current_user: dict = Depends(require_leads_read),
    lead_service: LeadService = Depends(get_lead_service),
):
    """Get all leads with pagination and filtering"""
    try:
        leads = lead_service.get_leads(
            skip, limit, search, status, company_id, review_status
        )
        total = lead_service.get_leads_count(search, status, company_id, review_status)

        # Transform to response models
        lead_responses = []
        for lead in leads:
            lead_dict = {
                "id": lead.id,
                "project_title": lead.project_title,
                "lead_source": lead.lead_source.value,
                "lead_sub_type": lead.lead_sub_type.value,
                "tender_sub_type": lead.tender_sub_type.value,
                "products_services": lead.products_services or [],
                "company_id": lead.company_id,
                "sub_business_type": lead.sub_business_type,
                "end_customer_id": lead.end_customer_id,
                "end_customer_region": lead.end_customer_region,
                "partner_involved": lead.partner_involved,
                "partners_data": lead.partners_data or [],
                "tender_fee": lead.tender_fee,
                "currency": lead.currency,
                "submission_type": (
                    lead.submission_type.value if lead.submission_type else None
                ),
                "tender_authority": lead.tender_authority,
                "tender_for": lead.tender_for,
                "emd_required": lead.emd_required,
                "emd_amount": lead.emd_amount,
                "emd_currency": lead.emd_currency,
                "bg_required": lead.bg_required,
                "bg_amount": lead.bg_amount,
                "bg_currency": lead.bg_currency,
                "important_dates": lead.important_dates or [],
                "clauses": lead.clauses or [],
                "expected_revenue": lead.expected_revenue,
                "revenue_currency": lead.revenue_currency,
                "convert_to_opportunity_date": lead.convert_to_opportunity_date,
                "competitors": lead.competitors or [],
                "documents": lead.documents or [],
                "status": lead.status.value,
                "priority": lead.priority.value,
                "qualification_notes": lead.qualification_notes,
                "lead_score": lead.lead_score,
                "contacts": lead.contacts or [],
                "company_name": lead.company_name,
                "end_customer_name": lead.end_customer_name,
                "creator_name": lead.creator_name,
                "conversion_requester_name": lead.conversion_requester_name,
                "reviewer_name": lead.reviewer_name,
                "ready_for_conversion": lead.ready_for_conversion,
                "conversion_requested": lead.conversion_requested,
                "conversion_request_date": lead.conversion_request_date,
                "reviewed": lead.reviewed,
                "review_status": lead.review_status.value,
                "review_date": lead.review_date,
                "review_comments": lead.review_comments,
                "converted": lead.converted,
                "converted_to_opportunity_id": lead.converted_to_opportunity_id,
                "conversion_date": lead.conversion_date,
                "conversion_notes": lead.conversion_notes,
                "can_request_conversion": lead.can_request_conversion,
                "can_convert_to_opportunity": lead.can_convert_to_opportunity,
                "needs_admin_review": lead.needs_admin_review,
                "is_active": lead.is_active,
                "created_on": lead.created_on,
                "updated_on": lead.updated_on,
            }
            lead_responses.append(lead_dict)

        return StandardResponse(
            status=True,
            message="Leads retrieved successfully",
            data={
                "leads": lead_responses,
                "total": total,
                "skip": skip,
                "limit": limit,
            },
        )
    except Exception as e:
        print(f"Error in get_leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=StandardResponse)
async def get_lead_stats(
    current_user: dict = Depends(require_leads_read),
    lead_service: LeadService = Depends(get_lead_service),
):
    """Get lead statistics"""
    stats = lead_service.get_lead_stats()
    return StandardResponse(
        status=True, message="Lead statistics retrieved successfully", data=stats
    )


@router.get("/pending-review", response_model=StandardResponse)
async def get_pending_review_leads(
    current_user: dict = Depends(require_admin_role),
    lead_service: LeadService = Depends(get_lead_service),
):
    """Get leads pending admin review (Admin only)"""
    try:
        leads = lead_service.get_leads_pending_review()

        lead_responses = []
        for lead in leads:
            lead_dict = {
                "id": lead.id,
                "project_title": lead.project_title,
                "company_name": lead.company_name,
                "expected_revenue": lead.expected_revenue,
                "conversion_request_date": lead.conversion_request_date,
                "conversion_requester_name": lead.conversion_requester_name,
                "status": lead.status.value,
                "review_status": lead.review_status.value,
            }
            lead_responses.append(lead_dict)

        return StandardResponse(
            status=True,
            message="Pending review leads retrieved successfully",
            data={"leads": lead_responses},
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
    lead = lead_service.get_lead_by_id(lead_id)
    if not lead:
        from ...exceptions.custom_exceptions import NotFoundError
        raise NotFoundError("Lead", lead_id)

    # Transform to response format (same as in get_leads)
    lead_dict = {
        "id": lead.id,
        "project_title": lead.project_title,
        "lead_source": lead.lead_source.value,
        "lead_sub_type": lead.lead_sub_type.value,
        "tender_sub_type": lead.tender_sub_type.value,
        "products_services": lead.products_services or [],
        "company_id": lead.company_id,
        "sub_business_type": lead.sub_business_type,
        "end_customer_id": lead.end_customer_id,
        "end_customer_region": lead.end_customer_region,
        "partner_involved": lead.partner_involved,
        "partners_data": lead.partners_data or [],
        "tender_fee": lead.tender_fee,
        "currency": lead.currency,
        "submission_type": (
            lead.submission_type.value if lead.submission_type else None
        ),
        "tender_authority": lead.tender_authority,
        "tender_for": lead.tender_for,
        "emd_required": lead.emd_required,
        "emd_amount": lead.emd_amount,
        "emd_currency": lead.emd_currency,
        "bg_required": lead.bg_required,
        "bg_amount": lead.bg_amount,
        "bg_currency": lead.bg_currency,
        "important_dates": lead.important_dates or [],
        "clauses": lead.clauses or [],
        "expected_revenue": lead.expected_revenue,
        "revenue_currency": lead.revenue_currency,
        "convert_to_opportunity_date": lead.convert_to_opportunity_date,
        "competitors": lead.competitors or [],
        "documents": lead.documents or [],
        "status": lead.status.value,
        "priority": lead.priority.value,
        "qualification_notes": lead.qualification_notes,
        "lead_score": lead.lead_score,
        "contacts": lead.contacts or [],
        "company_name": lead.company_name,
        "end_customer_name": lead.end_customer_name,
        "creator_name": lead.creator_name,
        "conversion_requester_name": lead.conversion_requester_name,
        "reviewer_name": lead.reviewer_name,
        "ready_for_conversion": lead.ready_for_conversion,
        "conversion_requested": lead.conversion_requested,
        "conversion_request_date": lead.conversion_request_date,
        "reviewed": lead.reviewed,
        "review_status": lead.review_status.value,
        "review_date": lead.review_date,
        "review_comments": lead.review_comments,
        "converted": lead.converted,
        "converted_to_opportunity_id": lead.converted_to_opportunity_id,
        "conversion_date": lead.conversion_date,
        "conversion_notes": lead.conversion_notes,
        "can_request_conversion": lead.can_request_conversion,
        "can_convert_to_opportunity": lead.can_convert_to_opportunity,
        "needs_admin_review": lead.needs_admin_review,
        "is_active": lead.is_active,
        "created_on": lead.created_on,
        "updated_on": lead.updated_on,
    }

    return StandardResponse(
        status=True,
        message="Lead retrieved successfully",
        data=lead_dict,
    )


@router.post("/", response_model=StandardResponse)
async def create_lead(
    lead_data: LeadCreate,
    current_user: dict = Depends(require_leads_write),
    lead_service: LeadService = Depends(get_lead_service),
):
    """Create new lead"""
    try:
        # Convert Pydantic model to dict with proper enum handling
        lead_dict = lead_data.dict()
        
        # Convert enum objects to their string values
        for key, value in lead_dict.items():
            if hasattr(value, 'value'):  # It's an enum
                lead_dict[key] = value.value
        
        lead = lead_service.create_lead(lead_dict, current_user["id"])

        return StandardResponse(
            status=True,
            message="Lead created successfully",
            data={
                "id": lead.id,
                "project_title": lead.project_title,
                "status": lead.status.value,
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(e)
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
            lead_id,
            lead_data.dict(exclude_unset=True),
            current_user["id"],
        )
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        return StandardResponse(
            status=True,
            message="Lead updated successfully",
            data={
                "id": lead.id,
                "project_title": lead.project_title,
                "status": lead.status.value,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Conversion Workflow Endpoints


@router.post("/{lead_id}/request-conversion", response_model=StandardResponse)
async def request_conversion(
    lead_id: str,
    request_data: ConversionRequestSchema,
    current_user: dict = Depends(require_leads_write),
    lead_service: LeadService = Depends(get_lead_service),
):
    """Request conversion of qualified lead to opportunity"""
    try:
        lead = lead_service.request_conversion(
            lead_id, current_user["id"], request_data.notes
        )
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        return StandardResponse(
            status=True,
            message="Conversion request submitted successfully. Waiting for admin review.",
            data={
                "id": lead.id,
                "project_title": lead.project_title,
                "conversion_requested": lead.conversion_requested,
                "review_status": lead.review_status.value,
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{lead_id}/review", response_model=StandardResponse)
async def review_conversion_request(
    lead_id: str,
    review_data: ReviewDecisionSchema,
    current_user: dict = Depends(require_admin_role),
    lead_service: LeadService = Depends(get_lead_service),
):
    """Review and approve/reject conversion request (Admin only)"""
    try:
        lead = lead_service.review_conversion_request(
            lead_id, current_user["id"], review_data.decision, review_data.comments
        )
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        message = (
            "Conversion request approved successfully"
            if review_data.decision == ReviewStatus.APPROVED
            else "Conversion request rejected"
        )

        return StandardResponse(
            status=True,
            message=message,
            data={
                "id": lead.id,
                "project_title": lead.project_title,
                "review_status": lead.review_status.value,
                "reviewed_by": lead.reviewer_name,
                "review_date": lead.review_date,
                "can_convert_to_opportunity": lead.can_convert_to_opportunity,
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{lead_id}/convert-to-opportunity", response_model=StandardResponse)
async def convert_to_opportunity(
    lead_id: str,
    conversion_data: ConvertToOpportunitySchema,
    current_user: dict = Depends(require_leads_write),
    lead_service: LeadService = Depends(get_lead_service),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    """Convert approved lead to opportunity"""
    try:
        # Get and validate lead
        lead = lead_service.get_lead_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        # Check permissions
        user_roles = current_user.get("roles", [])
        is_admin = "admin" in user_roles or "reviewer" in user_roles

        if not lead.can_convert_to_opportunity and not is_admin:
            raise HTTPException(
                status_code=400,
                detail="This opportunity needs to be reviewed by an Admin before it can be converted.",
            )

        # Create opportunity from lead
        opportunity_name = (
            conversion_data.opportunity_name or f"{lead.project_title} Opportunity"
        )

        # Get primary contact (decision maker or first contact)
        contacts = lead.contacts or []
        primary_contact = None
        for contact in contacts:
            if contact.get("decision_maker"):
                primary_contact = contact
                break
        if not primary_contact and contacts:
            primary_contact = contacts[0]

        if not primary_contact:
            raise HTTPException(
                status_code=400,
                detail="Lead must have at least one contact to convert to opportunity",
            )

        # Create opportunity data
        opportunity_data = {
            "lead_id": lead.id,
            "company_id": lead.company_id,
            "contact_id": (
                primary_contact.get("contact_id")
                if primary_contact.get("contact_id")
                else None
            ),  # This would need to be mapped
            "name": opportunity_name,
            "amount": lead.expected_revenue,
            "notes": f"Converted from lead: {lead.project_title}\n"
            + (conversion_data.notes or ""),
            "close_date": lead.convert_to_opportunity_date,
            "stage": "L1_Prospect",
            "status": "Open",
        }

        # Create the opportunity
        opportunity = opportunity_service.create_opportunity_from_lead(
            opportunity_data, current_user["id"]
        )

        # Update lead as converted
        lead_service.mark_as_converted(
            lead_id, opportunity.id, current_user["id"], conversion_data.notes
        )

        return StandardResponse(
            status=True,
            message="Lead converted to opportunity successfully",
            data={
                "lead_id": lead.id,
                "opportunity_id": opportunity.id,
                "opportunity_pot_id": opportunity.pot_id,
                "opportunity_name": opportunity.name,
            },
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error converting lead to opportunity: {e}")
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


# Document upload endpoint
@router.post("/{lead_id}/upload", response_model=StandardResponse)
async def upload_lead_document(
    lead_id: str,
    file: UploadFile = File(...),
    document_type: str = Query(..., description="Type of document"),
    quotation_name: str = Query("", description="Quotation name"),
    description: str = Query("", description="Document description"),
    current_user: dict = Depends(require_leads_write),
    lead_service: LeadService = Depends(get_lead_service),
):
    """Upload lead-related documents"""
    try:
        # Validate lead exists
        lead = lead_service.get_lead_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        # Save file (implement actual file storage logic here)
        file_path = f"/uploads/leads/{lead.id}/{document_type}_{file.filename}"

        # Add document to lead
        document_data = {
            "document_type": document_type,
            "quotation_name": quotation_name,
            "file_path": file_path,
            "description": description,
        }

        lead_service.add_document(lead_id, document_data, current_user["id"])

        return StandardResponse(
            status=True,
            message="Document uploaded successfully",
            data={"file_path": file_path, "document_type": document_type},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
