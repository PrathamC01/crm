from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from typing import Optional
from ...schemas.opportunity import (
    OpportunityCreate,
    OpportunityUpdate,
    OpportunityStageUpdate,
    OpportunityCloseRequest,
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

router = APIRouter(
    prefix="/api/opportunities", tags=["Enhanced Opportunity Management"]
)


async def get_opportunity_service(
    postgres_pool=Depends(get_postgres_db),
) -> OpportunityService:
    return OpportunityService(postgres_pool)


# Utility for transforming opportunity objects to dict


def transform_opportunity(opp):
    return {
        "id": opp.id,
        "pot_id": opp.pot_id,
        "lead_id": opp.lead_id,
        "company_id": opp.company_id,
        "contact_id": opp.contact_id,
        "name": opp.name,
        "stage": opp.stage.value,
        "amount": opp.amount,
        "scoring": opp.scoring,
        "bom_id": opp.bom_id,
        "costing": opp.costing,
        "status": opp.status.value,
        "justification": opp.justification,
        "close_date": opp.close_date,
        "probability": opp.probability,
        "notes": opp.notes,
        "company_name": opp.company_name,
        "contact_name": opp.contact_name,
        "contact_email": getattr(opp.contact, "email", None),
        "lead_source": getattr(opp.lead, "source", None),
        "created_by_name": opp.creator_name,
        "qualification_completer_name": (
            getattr(opp.qualification_completer, "name", None)
            if opp.qualification_completer
            else None
        ),
        "delivery_team_member_name": (
            getattr(opp.delivery_team_member, "name", None)
            if opp.delivery_team_member
            else None
        ),
        "is_active": opp.is_active,
        "created_on": opp.created_on,
        "updated_on": opp.updated_on,
        "stage_percentage": opp.stage_percentage,
        "stage_display_name": opp.stage_display_name,
        # **opp.stage_specific_fields(),  # assuming all stage-specific fields are packed in one method
    }


@router.get("/", response_model=StandardResponse)
async def get_opportunities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    stage: Optional[str] = None,
    status: Optional[str] = None,
    company_id: Optional[str] = None,
    lead_id: Optional[str] = None,
    current_user: dict = Depends(require_opportunities_read),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
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
        return StandardResponse(
            status=True,
            message="Opportunities retrieved successfully",
            data={
                "opportunities": [transform_opportunity(opp) for opp in opportunities],
                "total": total,
                "skip": skip,
                "limit": limit,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{opportunity_id}", response_model=StandardResponse)
async def get_opportunity(
    opportunity_id: str,
    current_user: dict = Depends(require_opportunities_read),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    try:
        opportunity = opportunity_service.get_opportunity_by_id(opportunity_id)
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        return StandardResponse(
            status=True,
            message="Opportunity retrieved successfully",
            data=transform_opportunity(opportunity),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=StandardResponse)
async def create_opportunity(
    opportunity_data: OpportunityCreate,
    current_user: dict = Depends(require_opportunities_write),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
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
                "stage_display_name": opportunity.stage_display_name,
            },
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
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
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
                "stage_display_name": opportunity.stage_display_name,
            },
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
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    try:
        opportunity = opportunity_service.update_stage(
            opportunity_id,
            stage_data.stage.value,
            current_user["id"],
            stage_data.notes,
            stage_data.stage_specific_data,
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
                "probability": opportunity.probability,
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Dynamic stage-specific endpoint handler
def generate_stage_patch_handler(service_method, success_message):
    async def handler(
        opportunity_id: str,
        data: dict,
        current_user: dict = Depends(require_opportunities_write),
        opportunity_service: OpportunityService = Depends(get_opportunity_service),
    ):
        try:
            opportunity = service_method(
                opportunity_service,
                opportunity_id,
                data.dict(exclude_unset=True),
                current_user["id"],
            )
            if not opportunity:
                raise HTTPException(status_code=404, detail="Opportunity not found")
            return StandardResponse(
                status=True,
                message=success_message,
                data={"pot_id": opportunity.pot_id, "stage": opportunity.stage.value},
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return handler


router.add_api_route(
    "/{opportunity_id}/qualification",
    generate_stage_patch_handler(
        OpportunityService.update_qualification,
        "Qualification tasks updated successfully",
    ),
    methods=["PATCH"],
    response_model=StandardResponse,
)
router.add_api_route(
    "/{opportunity_id}/demo",
    generate_stage_patch_handler(
        OpportunityService.update_demo_tasks, "Demo tasks updated successfully"
    ),
    methods=["PATCH"],
    response_model=StandardResponse,
)
router.add_api_route(
    "/{opportunity_id}/proposal",
    generate_stage_patch_handler(
        OpportunityService.update_proposal_tasks, "Proposal tasks updated successfully"
    ),
    methods=["PATCH"],
    response_model=StandardResponse,
)
router.add_api_route(
    "/{opportunity_id}/negotiation",
    generate_stage_patch_handler(
        OpportunityService.update_negotiation_tasks,
        "Negotiation tasks updated successfully",
    ),
    methods=["PATCH"],
    response_model=StandardResponse,
)
router.add_api_route(
    "/{opportunity_id}/won-tasks",
    generate_stage_patch_handler(
        OpportunityService.update_won_tasks, "Won tasks updated successfully"
    ),
    methods=["PATCH"],
    response_model=StandardResponse,
)


@router.patch("/{opportunity_id}/close", response_model=StandardResponse)
async def close_opportunity(
    opportunity_id: str,
    close_data: OpportunityCloseRequest,
    current_user: dict = Depends(require_opportunities_write),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
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
                "stage": opportunity.stage.value,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{opportunity_id}", response_model=StandardResponse)
async def delete_opportunity(
    opportunity_id: str,
    current_user: dict = Depends(require_opportunities_write),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    try:
        deleted = opportunity_service.delete_opportunity(
            opportunity_id, current_user["id"]
        )
        if not deleted:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        return StandardResponse(status=True, message="Opportunity deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pipeline/summary", response_model=StandardResponse)
async def get_pipeline_summary(
    user_id: Optional[str] = None,
    current_user: dict = Depends(require_opportunities_read),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    try:
        summary = opportunity_service.get_pipeline_summary(user_id)
        return StandardResponse(
            status=True, message="Pipeline summary retrieved successfully", data=summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/metrics", response_model=StandardResponse)
async def get_opportunity_metrics(
    user_id: Optional[str] = None,
    current_user: dict = Depends(require_opportunities_read),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    try:
        metrics = opportunity_service.get_opportunity_metrics(user_id)
        return StandardResponse(
            status=True,
            message="Opportunity metrics retrieved successfully",
            data=metrics,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{opportunity_id}/upload", response_model=StandardResponse)
async def upload_opportunity_document(
    opportunity_id: str,
    file: UploadFile = File(...),
    document_type: str = Query(
        ..., description="Type of document: quotation, proposal, loi, etc."
    ),
    current_user: dict = Depends(require_opportunities_write),
    opportunity_service: OpportunityService = Depends(get_opportunity_service),
):
    try:
        opportunity = opportunity_service.get_opportunity_by_id(opportunity_id)
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        file_path = f"/uploads/opportunities/{opportunity.pot_id}/{document_type}_{file.filename}"

        doc_field_map = {
            "quotation": "quotation_file_path",
            "proposal": "proposal_file_path",
            "updated_proposal": "updated_proposal_file_path",
            "negotiated_quotation": "negotiated_quotation_file_path",
            "loi": "loi_file_path",
        }

        update_data = (
            {doc_field_map[document_type]: file_path}
            if document_type in doc_field_map
            else {}
        )

        if update_data:
            opportunity_service.update_opportunity(
                opportunity_id, update_data, current_user["id"]
            )

        return StandardResponse(
            status=True,
            message="Document uploaded successfully",
            data={"file_path": file_path, "document_type": document_type},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
