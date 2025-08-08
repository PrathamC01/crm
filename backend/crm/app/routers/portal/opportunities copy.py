"""
Enhanced Opportunity Management API endpoints with stage-specific functionality
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from typing import Optional, Dict, Any
from ...schemas.opportunity import (
    OpportunityCreate,
    OpportunityUpdate,
    OpportunityListResponse,
    OpportunityResponse,
    OpportunityStageUpdate,
    OpportunityCloseRequest,
    OpportunityPipelineSummary,
    QualificationTaskUpdate,
    DemoTaskUpdate,
    ProposalTaskUpdate,
    NegotiationTaskUpdate,
    WonTaskUpdate,
)
from ...schemas.auth import StandardResponse
from ...dependencies.rbac import require_opportunities_read, require_opportunities_write
from ...services.opportunity_service import OpportunityService
from ...dependencies.database import get_postgres_db

router = APIRouter(prefix="/api/opportunities", tags=["Enhanced Opportunity Management"])


async def get_opportunity_service(
    postgres_pool=Depends(get_postgres_db),
) -> OpportunityService:
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
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    """Get all opportunities with pagination and filtering"""
    try:
        if company_id:
            opportunities = opportunity_service.get_opportunities_by_company(
                company_id, skip, limit
            )
        elif lead_id:
            opportunities = opportunity_service.get_opportunities_by_lead(
                lead_id, skip, limit
            )
        else:
            opportunities = opportunity_service.get_opportunities(
                skip, limit, stage, status, search
            )

        total = opportunity_service.get_opportunity_count(stage, status, search)

        # Transform to response models
        opportunity_responses = []
        for opp in opportunities:
            opp_dict = {
                'id': opp.id,
                'pot_id': opp.pot_id,
                'lead_id': opp.lead_id,
                'company_id': opp.company_id,
                'contact_id': opp.contact_id,
                'name': opp.name,
                'stage': opp.stage.value,
                'amount': opp.amount,
                'scoring': opp.scoring,
                'bom_id': opp.bom_id,
                'costing': opp.costing,
                'status': opp.status.value,
                'justification': opp.justification,
                'close_date': opp.close_date,
                'probability': opp.probability,
                'notes': opp.notes,
                'company_name': opp.company_name,
                'contact_name': opp.contact_name,
                'contact_email': getattr(opp.contact, 'email', None),
                'lead_source': getattr(opp.lead, 'source', None),
                'created_by_name': opp.creator_name,
                'qualification_completer_name': getattr(opp.qualification_completer, 'full_name', None) if opp.qualification_completer else None,
                'delivery_team_member_name': getattr(opp.delivery_team_member, 'full_name', None) if opp.delivery_team_member else None,
                'is_active': opp.is_active,
                'created_on': opp.created_on,
                'updated_on': opp.updated_on,
                'stage_percentage': opp.stage_percentage,
                'stage_display_name': opp.stage_display_name,
                
                # Stage-specific fields
                'requirement_gathering_notes': opp.requirement_gathering_notes,
                'go_no_go_status': opp.go_no_go_status.value if opp.go_no_go_status else None,
                'qualification_completed_by': opp.qualification_completed_by,
                'qualification_status': opp.qualification_status.value if opp.qualification_status else None,
                'qualification_scorecard': opp.qualification_scorecard,
                
                'demo_completed': opp.demo_completed,
                'demo_date': opp.demo_date,
                'demo_summary': opp.demo_summary,
                'presentation_materials': opp.presentation_materials,
                'qualification_meeting_completed': opp.qualification_meeting_completed,
                'qualification_meeting_date': opp.qualification_meeting_date,
                'qualification_meeting_notes': opp.qualification_meeting_notes,
                
                'quotation_created': opp.quotation_created,
                'quotation_status': opp.quotation_status.value if opp.quotation_status else None,
                'quotation_file_path': opp.quotation_file_path,
                'quotation_version': opp.quotation_version,
                'proposal_prepared': opp.proposal_prepared,
                'proposal_file_path': opp.proposal_file_path,
                'proposal_submitted': opp.proposal_submitted,
                'proposal_submission_date': opp.proposal_submission_date,
                'poc_completed': opp.poc_completed,
                'poc_notes': opp.poc_notes,
                'solutions_team_approval_notes': opp.solutions_team_approval_notes,
                
                'customer_discussion_notes': opp.customer_discussion_notes,
                'proposal_updated': opp.proposal_updated,
                'updated_proposal_file_path': opp.updated_proposal_file_path,
                'updated_proposal_submitted': opp.updated_proposal_submitted,
                'negotiated_quotation_file_path': opp.negotiated_quotation_file_path,
                'negotiation_rounds': opp.negotiation_rounds,
                'commercial_approval_required': opp.commercial_approval_required,
                'commercial_approval_status': opp.commercial_approval_status,
                
                'kickoff_meeting_scheduled': opp.kickoff_meeting_scheduled,
                'kickoff_meeting_date': opp.kickoff_meeting_date,
                'loi_received': opp.loi_received,
                'loi_file_path': opp.loi_file_path,
                'order_verified': opp.order_verified,
                'handoff_to_delivery': opp.handoff_to_delivery,
                'delivery_team_assigned': opp.delivery_team_assigned,
                
                'lost_reason': opp.lost_reason,
                'competitor_name': opp.competitor_name,
                'follow_up_date': opp.follow_up_date,
                'drop_reason': opp.drop_reason,
                'reactivate_date': opp.reactivate_date,
            }
            opportunity_responses.append(opp_dict)

        return StandardResponse(
            status=True,
            message="Opportunities retrieved successfully",
            data={
                "opportunities": opportunity_responses,
                "total": total,
                "skip": skip,
                "limit": limit,
            },
        )
    except Exception as e:
        print(f"Error in get_opportunities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{opportunity_id}", response_model=StandardResponse)
async def get_opportunity(
    opportunity_id: str,
    current_user: dict = Depends(require_opportunities_read),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    """Get opportunity by ID"""
    try:
        opportunity = opportunity_service.get_opportunity_by_id(opportunity_id)
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        # Transform to response format
        opp_dict = {
            'id': opportunity.id,
            'pot_id': opportunity.pot_id,
            'lead_id': opportunity.lead_id,
            'company_id': opportunity.company_id,
            'contact_id': opportunity.contact_id,
            'name': opportunity.name,
            'stage': opportunity.stage.value,
            'amount': opportunity.amount,
            'scoring': opportunity.scoring,
            'bom_id': opportunity.bom_id,
            'costing': opportunity.costing,
            'status': opportunity.status.value,
            'justification': opportunity.justification,
            'close_date': opportunity.close_date,
            'probability': opportunity.probability,
            'notes': opportunity.notes,
            'company_name': opportunity.company_name,
            'contact_name': opportunity.contact_name,
            'contact_email': getattr(opportunity.contact, 'email', None),
            'lead_source': getattr(opportunity.lead, 'source', None),
            'created_by_name': opportunity.creator_name,
            'qualification_completer_name': getattr(opportunity.qualification_completer, 'full_name', None) if opportunity.qualification_completer else None,
            'delivery_team_member_name': getattr(opportunity.delivery_team_member, 'full_name', None) if opportunity.delivery_team_member else None,
            'is_active': opportunity.is_active,
            'created_on': opportunity.created_on,
            'updated_on': opportunity.updated_on,
            'stage_percentage': opportunity.stage_percentage,
            'stage_display_name': opportunity.stage_display_name,
            
            # All stage-specific fields...
            'requirement_gathering_notes': opportunity.requirement_gathering_notes,
            'go_no_go_status': opportunity.go_no_go_status.value if opportunity.go_no_go_status else None,
            'qualification_completed_by': opportunity.qualification_completed_by,
            'qualification_status': opportunity.qualification_status.value if opportunity.qualification_status else None,
            'qualification_scorecard': opportunity.qualification_scorecard,
            
            'demo_completed': opportunity.demo_completed,
            'demo_date': opportunity.demo_date,
            'demo_summary': opportunity.demo_summary,
            'presentation_materials': opportunity.presentation_materials,
            'qualification_meeting_completed': opportunity.qualification_meeting_completed,
            'qualification_meeting_date': opportunity.qualification_meeting_date,
            'qualification_meeting_notes': opportunity.qualification_meeting_notes,
            
            'quotation_created': opportunity.quotation_created,
            'quotation_status': opportunity.quotation_status.value if opportunity.quotation_status else None,
            'quotation_file_path': opportunity.quotation_file_path,
            'quotation_version': opportunity.quotation_version,
            'proposal_prepared': opportunity.proposal_prepared,
            'proposal_file_path': opportunity.proposal_file_path,
            'proposal_submitted': opportunity.proposal_submitted,
            'proposal_submission_date': opportunity.proposal_submission_date,
            'poc_completed': opportunity.poc_completed,
            'poc_notes': opportunity.poc_notes,
            'solutions_team_approval_notes': opportunity.solutions_team_approval_notes,
            
            'customer_discussion_notes': opportunity.customer_discussion_notes,
            'proposal_updated': opportunity.proposal_updated,
            'updated_proposal_file_path': opportunity.updated_proposal_file_path,
            'updated_proposal_submitted': opportunity.updated_proposal_submitted,
            'negotiated_quotation_file_path': opportunity.negotiated_quotation_file_path,
            'negotiation_rounds': opportunity.negotiation_rounds,
            'commercial_approval_required': opportunity.commercial_approval_required,
            'commercial_approval_status': opportunity.commercial_approval_status,
            
            'kickoff_meeting_scheduled': opportunity.kickoff_meeting_scheduled,
            'kickoff_meeting_date': opportunity.kickoff_meeting_date,
            'loi_received': opportunity.loi_received,
            'loi_file_path': opportunity.loi_file_path,
            'order_verified': opportunity.order_verified,
            'handoff_to_delivery': opportunity.handoff_to_delivery,
            'delivery_team_assigned': opportunity.delivery_team_assigned,
            
            'lost_reason': opportunity.lost_reason,
            'competitor_name': opportunity.competitor_name,
            'follow_up_date': opportunity.follow_up_date,
            'drop_reason': opportunity.drop_reason,
            'reactivate_date': opportunity.reactivate_date,
        }

        return StandardResponse(
            status=True,
            message="Opportunity retrieved successfully",
            data=opp_dict,
        )
    except HTTPException:
        raise
    except Exception as e:
        print(e)


@router.post("/", response_model=StandardResponse)
async def create_opportunity(
    opportunity_data: OpportunityCreate,
    current_user: dict = Depends(require_opportunities_write),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    """Create new opportunity with POT-{4digit} ID"""
    try:
        opportunity = opportunity_service.create_opportunity(
            opportunity_data.dict(exclude_unset=True), current_user["id"]
        )

        return StandardResponse(
            status=True, 
            message="Opportunity created successfully", 
            data={
                "id": opportunity.id,
                "pot_id": opportunity.pot_id,
                "name": opportunity.name,
                "stage": opportunity.stage.value,
                "stage_display_name": opportunity.stage_display_name
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(e)


@router.put("/{opportunity_id}", response_model=StandardResponse)
async def update_opportunity(
    opportunity_id: str,
    opportunity_data: OpportunityUpdate,
    current_user: dict = Depends(require_opportunities_write),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    """Update opportunity information"""
    try:
        opportunity = opportunity_service.update_opportunity(
            opportunity_id,
            opportunity_data.dict(exclude_unset=True),
            current_user["id"],
        )
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        return StandardResponse(
            status=True,
            message="Opportunity updated successfully",
            data={
                "id": opportunity.id,
                "pot_id": opportunity.pot_id,
                "name": opportunity.name,
                "stage": opportunity.stage.value,
                "stage_display_name": opportunity.stage_display_name
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        print(e)


@router.patch("/{opportunity_id}/stage", response_model=StandardResponse)
async def update_opportunity_stage(
    opportunity_id: str,
    stage_data: OpportunityStageUpdate,
    current_user: dict = Depends(require_opportunities_write),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    """Update opportunity stage with stage-specific data"""
    try:
        opportunity = opportunity_service.update_stage(
            opportunity_id, 
            stage_data.stage.value, 
            current_user["id"], 
            stage_data.notes,
            stage_data.stage_specific_data
        )
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        return StandardResponse(
            status=True,
            message="Opportunity stage updated successfully",
            data={
                "id": opportunity.id,
                "pot_id": opportunity.pot_id,
                "stage": opportunity.stage.value,
                "stage_display_name": opportunity.stage_display_name,
                "probability": opportunity.probability
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        print(e)


# Stage-specific task update endpoints
@router.patch("/{opportunity_id}/qualification", response_model=StandardResponse)
async def update_qualification_tasks(
    opportunity_id: str,
    qualification_data: QualificationTaskUpdate,
    current_user: dict = Depends(require_opportunities_write),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    """Update L1 qualification stage tasks"""
    try:
        opportunity = opportunity_service.update_qualification(
            opportunity_id, qualification_data.dict(exclude_unset=True), current_user["id"]
        )
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        return StandardResponse(
            status=True,
            message="Qualification tasks updated successfully",
            data={"pot_id": opportunity.pot_id, "stage": opportunity.stage.value},
        )
    except Exception as e:
        print(e)


@router.patch("/{opportunity_id}/demo", response_model=StandardResponse)
async def update_demo_tasks(
    opportunity_id: str,
    demo_data: DemoTaskUpdate,
    current_user: dict = Depends(require_opportunities_write),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    """Update L2 demo and need analysis tasks"""
    try:
        opportunity = opportunity_service.update_demo_tasks(
            opportunity_id, demo_data.dict(exclude_unset=True), current_user["id"]
        )
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        return StandardResponse(
            status=True,
            message="Demo tasks updated successfully",
            data={"pot_id": opportunity.pot_id, "stage": opportunity.stage.value},
        )
    except Exception as e:
        print(e)


@router.patch("/{opportunity_id}/proposal", response_model=StandardResponse)
async def update_proposal_tasks(
    opportunity_id: str,
    proposal_data: ProposalTaskUpdate,
    current_user: dict = Depends(require_opportunities_write),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    """Update L3 proposal and bid submission tasks"""
    try:
        opportunity = opportunity_service.update_proposal_tasks(
            opportunity_id, proposal_data.dict(exclude_unset=True), current_user["id"]
        )
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        return StandardResponse(
            status=True,
            message="Proposal tasks updated successfully",
            data={"pot_id": opportunity.pot_id, "stage": opportunity.stage.value},
        )
    except Exception as e:
        print(e)


@router.patch("/{opportunity_id}/negotiation", response_model=StandardResponse)
async def update_negotiation_tasks(
    opportunity_id: str,
    negotiation_data: NegotiationTaskUpdate,
    current_user: dict = Depends(require_opportunities_write),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    """Update L4 negotiation tasks"""
    try:
        opportunity = opportunity_service.update_negotiation_tasks(
            opportunity_id, negotiation_data.dict(exclude_unset=True), current_user["id"]
        )
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        return StandardResponse(
            status=True,
            message="Negotiation tasks updated successfully",
            data={"pot_id": opportunity.pot_id, "stage": opportunity.stage.value},
        )
    except Exception as e:
        print(e)


@router.patch("/{opportunity_id}/won-tasks", response_model=StandardResponse)
async def update_won_tasks(
    opportunity_id: str,
    won_data: WonTaskUpdate,
    current_user: dict = Depends(require_opportunities_write),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    """Update L5 won stage tasks"""
    try:
        opportunity = opportunity_service.update_won_tasks(
            opportunity_id, won_data.dict(exclude_unset=True), current_user["id"]
        )
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        return StandardResponse(
            status=True,
            message="Won tasks updated successfully",
            data={"pot_id": opportunity.pot_id, "stage": opportunity.stage.value},
        )
    except Exception as e:
        print(e)


@router.patch("/{opportunity_id}/close", response_model=StandardResponse)
async def close_opportunity(
    opportunity_id: str,
    close_data: OpportunityCloseRequest,
    current_user: dict = Depends(require_opportunities_write),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    """Close opportunity (Won/Lost/Dropped) with reason tracking"""
    try:
        opportunity = opportunity_service.close_opportunity(
            opportunity_id,
            close_data.status,
            close_data.close_date.isoformat(),
            current_user["id"],
            close_data.notes,
            close_data.lost_reason,
            close_data.competitor_name,
            close_data.drop_reason,
        )
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        return StandardResponse(
            status=True,
            message=f"Opportunity closed as {close_data.status}",
            data={
                "pot_id": opportunity.pot_id,
                "status": opportunity.status.value,
                "stage": opportunity.stage.value
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        print(e)


@router.delete("/{opportunity_id}", response_model=StandardResponse)
async def delete_opportunity(
    opportunity_id: str,
    current_user: dict = Depends(require_opportunities_write),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    """Soft delete opportunity"""
    try:
        deleted = opportunity_service.delete_opportunity(
            opportunity_id, current_user["id"]
        )
        if not deleted:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        return StandardResponse(status=True, message="Opportunity deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(e)


@router.get("/pipeline/summary", response_model=StandardResponse)
async def get_pipeline_summary(
    user_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_opportunities_read),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    """Get enhanced opportunity pipeline summary"""
    try:
        summary = opportunity_service.get_pipeline_summary(user_id)

        return StandardResponse(
            status=True, message="Pipeline summary retrieved successfully", data=summary
        )
    except Exception as e:
        print(e)


@router.get("/analytics/metrics", response_model=StandardResponse)
async def get_opportunity_metrics(
    user_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_opportunities_read),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    """Get enhanced opportunity metrics and analytics"""
    try:
        metrics = opportunity_service.get_opportunity_metrics(user_id)

        return StandardResponse(
            status=True,
            message="Opportunity metrics retrieved successfully",
            data=metrics,
        )
    except Exception as e:
        print(e)


# File upload endpoint for documents
@router.post("/{opportunity_id}/upload", response_model=StandardResponse)
async def upload_opportunity_document(
    opportunity_id: str,
    file: UploadFile = File(...),
    document_type: str = Query(..., description="Type of document: quotation, proposal, loi, etc."),
    current_user: dict = Depends(require_opportunities_write),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    """Upload opportunity-related documents"""
    try:
        # Validate opportunity exists
        opportunity = opportunity_service.get_opportunity_by_id(opportunity_id)
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        # Save file (implement actual file storage logic here)
        # For now, we'll just return a mock response
        file_path = f"/uploads/opportunities/{opportunity.pot_id}/{document_type}_{file.filename}"
        
        # Update appropriate field based on document type
        update_data = {}
        if document_type == "quotation":
            update_data["quotation_file_path"] = file_path
        elif document_type == "proposal":
            update_data["proposal_file_path"] = file_path
        elif document_type == "updated_proposal":
            update_data["updated_proposal_file_path"] = file_path
        elif document_type == "negotiated_quotation":
            update_data["negotiated_quotation_file_path"] = file_path
        elif document_type == "loi":
            update_data["loi_file_path"] = file_path
        
        if update_data:
            opportunity_service.update_opportunity(opportunity_id, update_data, current_user["id"])

        return StandardResponse(
            status=True,
            message="Document uploaded successfully",
            data={"file_path": file_path, "document_type": document_type}
        )
    except HTTPException:
        raise
    except Exception as e:
        print(e)