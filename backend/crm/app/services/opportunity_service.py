"""
Enhanced Opportunity management service with stage-specific functionality
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from ..models import (
    Opportunity,
    Lead,
    Company,
    Contact,
    User,
    RoleType,
    OpportunityStatus,
    OpportunityStage,
    QualificationStatus,
    GoNoGoStatus,
    QuotationStatus,
)
from decimal import Decimal


class OpportunityService:
    def __init__(self, db: Session):
        self.db = db

    def create_opportunity(
        self, opportunity_data: dict, created_by: Optional[int] = None
    ) -> Opportunity:
        """Create a new opportunity with POT-{4digit} ID"""
        # Validate that contact is a Decision Maker
        contact = (
            self.db.query(Contact)
            .filter(Contact.id == opportunity_data["contact_id"])
            .first()
        )

        if not contact or contact.role_type != RoleType.DECISION_MAKER:
            raise ValueError(
                "Opportunity can only be created with a Decision Maker contact"
            )

        # Generate unique POT ID
        pot_id = self._generate_unique_pot_id()

        db_opportunity = Opportunity(
            pot_id=pot_id,
            lead_id=opportunity_data.get("lead_id"),
            company_id=opportunity_data.get("company_id"),
            contact_id=opportunity_data.get("contact_id"),
            name=opportunity_data.get("name"),
            stage=opportunity_data.get("stage", OpportunityStage.L1_PROSPECT),
            amount=opportunity_data.get("amount"),
            scoring=opportunity_data.get("scoring", 0),
            bom_id=opportunity_data.get("bom_id"),
            costing=opportunity_data.get("costing"),
            status=opportunity_data.get("status", OpportunityStatus.OPEN),
            justification=opportunity_data.get("justification"),
            close_date=opportunity_data.get("close_date"),
            probability=opportunity_data.get("probability", 10),
            notes=opportunity_data.get("notes"),
            # L1 - Qualification Fields
            requirement_gathering_notes=opportunity_data.get(
                "requirement_gathering_notes"
            ),
            go_no_go_status=opportunity_data.get(
                "go_no_go_status", GoNoGoStatus.PENDING
            ),
            qualification_completed_by=opportunity_data.get(
                "qualification_completed_by"
            ),
            qualification_status=opportunity_data.get("qualification_status"),
            qualification_scorecard=opportunity_data.get("qualification_scorecard"),
            # L2 - Need Analysis / Demo Fields
            demo_completed=opportunity_data.get("demo_completed", False),
            demo_date=opportunity_data.get("demo_date"),
            demo_summary=opportunity_data.get("demo_summary"),
            presentation_materials=opportunity_data.get("presentation_materials"),
            qualification_meeting_completed=opportunity_data.get(
                "qualification_meeting_completed", False
            ),
            qualification_meeting_date=opportunity_data.get(
                "qualification_meeting_date"
            ),
            qualification_meeting_notes=opportunity_data.get(
                "qualification_meeting_notes"
            ),
            # L3 - Proposal / Bid Submission Fields
            quotation_created=opportunity_data.get("quotation_created", False),
            quotation_status=opportunity_data.get(
                "quotation_status", QuotationStatus.DRAFT
            ),
            quotation_file_path=opportunity_data.get("quotation_file_path"),
            quotation_version=opportunity_data.get("quotation_version", 1),
            proposal_prepared=opportunity_data.get("proposal_prepared", False),
            proposal_file_path=opportunity_data.get("proposal_file_path"),
            proposal_submitted=opportunity_data.get("proposal_submitted", False),
            proposal_submission_date=opportunity_data.get("proposal_submission_date"),
            poc_completed=opportunity_data.get("poc_completed", False),
            poc_notes=opportunity_data.get("poc_notes"),
            solutions_team_approval_notes=opportunity_data.get(
                "solutions_team_approval_notes"
            ),
            # L4 - Negotiation Fields
            customer_discussion_notes=opportunity_data.get("customer_discussion_notes"),
            proposal_updated=opportunity_data.get("proposal_updated", False),
            updated_proposal_file_path=opportunity_data.get(
                "updated_proposal_file_path"
            ),
            updated_proposal_submitted=opportunity_data.get(
                "updated_proposal_submitted", False
            ),
            negotiated_quotation_file_path=opportunity_data.get(
                "negotiated_quotation_file_path"
            ),
            negotiation_rounds=opportunity_data.get("negotiation_rounds", 0),
            commercial_approval_required=opportunity_data.get(
                "commercial_approval_required", False
            ),
            commercial_approval_status=opportunity_data.get(
                "commercial_approval_status"
            ),
            # L5 - Won Fields
            kickoff_meeting_scheduled=opportunity_data.get(
                "kickoff_meeting_scheduled", False
            ),
            kickoff_meeting_date=opportunity_data.get("kickoff_meeting_date"),
            loi_received=opportunity_data.get("loi_received", False),
            loi_file_path=opportunity_data.get("loi_file_path"),
            order_verified=opportunity_data.get("order_verified", False),
            handoff_to_delivery=opportunity_data.get("handoff_to_delivery", False),
            delivery_team_assigned=opportunity_data.get("delivery_team_assigned"),
            created_by=created_by,
        )

        self.db.add(db_opportunity)
        self.db.commit()
        self.db.refresh(db_opportunity)
        return db_opportunity

    def _generate_unique_pot_id(self) -> str:
        """Generate unique POT-{4digit} ID"""
        import random

        while True:
            pot_id = f"POT-{random.randint(1000, 9999)}"
            existing = (
                self.db.query(Opportunity).filter(Opportunity.pot_id == pot_id).first()
            )
            if not existing:
                return pot_id

    def get_opportunity_by_id(self, opportunity_id: int) -> Optional[Opportunity]:
        """Get opportunity by ID with related details"""
        return (
            self.db.query(Opportunity)
            .options(
                joinedload(Opportunity.company),
                joinedload(Opportunity.contact),
                joinedload(Opportunity.lead),
                joinedload(Opportunity.creator),
                joinedload(Opportunity.qualification_completer),
                joinedload(Opportunity.delivery_team_member),
            )
            .filter(
                and_(
                    Opportunity.id == opportunity_id,
                    Opportunity.is_active == True,
                    Opportunity.deleted_on.is_(None),
                )
            )
            .first()
        )

    def get_opportunity_by_pot_id(self, pot_id: str) -> Optional[Opportunity]:
        """Get opportunity by POT ID"""
        return (
            self.db.query(Opportunity)
            .options(
                joinedload(Opportunity.company),
                joinedload(Opportunity.contact),
                joinedload(Opportunity.lead),
                joinedload(Opportunity.creator),
                joinedload(Opportunity.qualification_completer),
                joinedload(Opportunity.delivery_team_member),
            )
            .filter(
                and_(
                    Opportunity.pot_id == pot_id,
                    Opportunity.is_active == True,
                    Opportunity.deleted_on.is_(None),
                )
            )
            .first()
        )

    def update_opportunity(
        self,
        opportunity_id: int,
        opportunity_data: dict,
        updated_by: Optional[int] = None,
    ) -> Optional[Opportunity]:
        """Update opportunity information"""
        db_opportunity = self.get_opportunity_by_id(opportunity_id)
        if not db_opportunity:
            return None

        for field, value in opportunity_data.items():
            if (
                field not in ["id", "pot_id", "created_on", "created_by"]
                and value is not None
            ):
                setattr(db_opportunity, field, value)

        if updated_by:
            db_opportunity.updated_by = updated_by

        self.db.commit()
        self.db.refresh(db_opportunity)
        return db_opportunity

    def update_stage(
        self,
        opportunity_id: int,
        stage: str,
        updated_by: int,
        notes: str = None,
        stage_specific_data: Dict[str, Any] = None,
    ) -> Optional[Opportunity]:
        """Update opportunity stage with stage-specific data"""
        db_opportunity = self.get_opportunity_by_id(opportunity_id)
        if not db_opportunity:
            return None

        # Update basic stage info
        db_opportunity.stage = stage
        db_opportunity.updated_by = updated_by

        # Update probability based on stage
        stage_probabilities = {
            OpportunityStage.L1_PROSPECT: 5,
            OpportunityStage.L1_QUALIFICATION: 15,
            OpportunityStage.L2_NEED_ANALYSIS: 40,
            OpportunityStage.L3_PROPOSAL: 60,
            OpportunityStage.L4_NEGOTIATION: 80,
            OpportunityStage.L5_WON: 100,
            OpportunityStage.L6_LOST: 0,
            OpportunityStage.L7_DROPPED: 0,
        }
        db_opportunity.probability = stage_probabilities.get(
            OpportunityStage(stage), db_opportunity.probability
        )

        # Update stage-specific data if provided
        if stage_specific_data:
            for field, value in stage_specific_data.items():
                if hasattr(db_opportunity, field) and value is not None:
                    setattr(db_opportunity, field, value)

        if notes:
            db_opportunity.notes = (
                db_opportunity.notes or ""
            ) + f"\n[Stage updated to {stage}]: {notes}"

        self.db.commit()
        self.db.refresh(db_opportunity)
        return db_opportunity

    def update_qualification(
        self, opportunity_id: int, qualification_data: Dict[str, Any], updated_by: int
    ) -> Optional[Opportunity]:
        """Update L1 qualification stage data"""
        db_opportunity = self.get_opportunity_by_id(opportunity_id)
        if not db_opportunity:
            return None

        # Update qualification fields
        for field in [
            "requirement_gathering_notes",
            "go_no_go_status",
            "qualification_status",
            "qualification_scorecard",
            "qualification_completed_by",
        ]:
            if field in qualification_data and qualification_data[field] is not None:
                setattr(db_opportunity, field, qualification_data[field])

        db_opportunity.updated_by = updated_by
        self.db.commit()
        self.db.refresh(db_opportunity)
        return db_opportunity

    def update_demo_tasks(
        self, opportunity_id: int, demo_data: Dict[str, Any], updated_by: int
    ) -> Optional[Opportunity]:
        """Update L2 demo and need analysis tasks"""
        db_opportunity = self.get_opportunity_by_id(opportunity_id)
        if not db_opportunity:
            return None

        # Update demo fields
        for field in [
            "demo_completed",
            "demo_date",
            "demo_summary",
            "presentation_materials",
            "qualification_meeting_completed",
            "qualification_meeting_date",
            "qualification_meeting_notes",
        ]:
            if field in demo_data and demo_data[field] is not None:
                setattr(db_opportunity, field, demo_data[field])

        db_opportunity.updated_by = updated_by
        self.db.commit()
        self.db.refresh(db_opportunity)
        return db_opportunity

    def update_proposal_tasks(
        self, opportunity_id: int, proposal_data: Dict[str, Any], updated_by: int
    ) -> Optional[Opportunity]:
        """Update L3 proposal and bid submission tasks"""
        db_opportunity = self.get_opportunity_by_id(opportunity_id)
        if not db_opportunity:
            return None

        # Update proposal fields
        for field in [
            "quotation_created",
            "quotation_status",
            "quotation_file_path",
            "quotation_version",
            "proposal_prepared",
            "proposal_file_path",
            "proposal_submitted",
            "proposal_submission_date",
            "poc_completed",
            "poc_notes",
            "solutions_team_approval_notes",
        ]:
            if field in proposal_data and proposal_data[field] is not None:
                setattr(db_opportunity, field, proposal_data[field])

        db_opportunity.updated_by = updated_by
        self.db.commit()
        self.db.refresh(db_opportunity)
        return db_opportunity

    def update_negotiation_tasks(
        self, opportunity_id: int, negotiation_data: Dict[str, Any], updated_by: int
    ) -> Optional[Opportunity]:
        """Update L4 negotiation tasks"""
        db_opportunity = self.get_opportunity_by_id(opportunity_id)
        if not db_opportunity:
            return None

        # Update negotiation fields
        for field in [
            "customer_discussion_notes",
            "proposal_updated",
            "updated_proposal_file_path",
            "updated_proposal_submitted",
            "negotiated_quotation_file_path",
            "negotiation_rounds",
            "commercial_approval_required",
            "commercial_approval_status",
        ]:
            if field in negotiation_data and negotiation_data[field] is not None:
                setattr(db_opportunity, field, negotiation_data[field])

        db_opportunity.updated_by = updated_by
        self.db.commit()
        self.db.refresh(db_opportunity)
        return db_opportunity

    def update_won_tasks(
        self, opportunity_id: int, won_data: Dict[str, Any], updated_by: int
    ) -> Optional[Opportunity]:
        """Update L5 won stage tasks"""
        db_opportunity = self.get_opportunity_by_id(opportunity_id)
        if not db_opportunity:
            return None

        # Update won fields
        for field in [
            "kickoff_meeting_scheduled",
            "kickoff_meeting_date",
            "loi_received",
            "loi_file_path",
            "order_verified",
            "handoff_to_delivery",
            "delivery_team_assigned",
        ]:
            if field in won_data and won_data[field] is not None:
                setattr(db_opportunity, field, won_data[field])

        # Auto-convert to customer if all tasks completed
        if (
            won_data.get("handoff_to_delivery")
            and db_opportunity.loi_received
            and db_opportunity.order_verified
        ):
            # TODO: Implement customer conversion logic
            pass

        db_opportunity.updated_by = updated_by
        self.db.commit()
        self.db.refresh(db_opportunity)
        return db_opportunity

    def close_opportunity(
        self,
        opportunity_id: int,
        status: str,
        close_date: str,
        updated_by: int,
        notes: str = None,
        lost_reason: str = None,
        competitor_name: str = None,
        drop_reason: str = None,
    ) -> Optional[Opportunity]:
        """Close opportunity with reason tracking"""
        db_opportunity = self.get_opportunity_by_id(opportunity_id)
        if not db_opportunity:
            return None

        db_opportunity.status = status
        db_opportunity.close_date = close_date
        db_opportunity.updated_by = updated_by

        # Update stage based on status
        if status == OpportunityStatus.WON:
            db_opportunity.stage = OpportunityStage.L5_WON
        elif status == OpportunityStatus.LOST:
            db_opportunity.stage = OpportunityStage.L6_LOST
            db_opportunity.lost_reason = lost_reason
            db_opportunity.competitor_name = competitor_name
        elif status == OpportunityStatus.DROPPED:
            db_opportunity.stage = OpportunityStage.L7_DROPPED
            db_opportunity.drop_reason = drop_reason

        if notes:
            db_opportunity.notes = (
                db_opportunity.notes or ""
            ) + f"\n[Closed as {status}]: {notes}"

        self.db.commit()
        self.db.refresh(db_opportunity)
        return db_opportunity

    def delete_opportunity(
        self, opportunity_id: int, deleted_by: Optional[int] = None
    ) -> bool:
        """Soft delete opportunity"""
        db_opportunity = self.get_opportunity_by_id(opportunity_id)
        if not db_opportunity:
            return False

        db_opportunity.is_active = False
        db_opportunity.deleted_on = datetime.utcnow()
        if deleted_by:
            db_opportunity.deleted_by = deleted_by

        self.db.commit()
        return True

    def get_opportunities(
        self,
        skip: int = 0,
        limit: int = 100,
        stage: str = None,
        status: str = None,
        search: str = None,
    ) -> List[Opportunity]:
        """Get all opportunities with pagination and filtering"""
        query = (
            self.db.query(Opportunity)
            .options(
                joinedload(Opportunity.company),
                joinedload(Opportunity.contact),
                joinedload(Opportunity.creator),
                joinedload(Opportunity.qualification_completer),
                joinedload(Opportunity.delivery_team_member),
            )
            .filter(
                and_(Opportunity.is_active == True, Opportunity.deleted_on.is_(None))
            )
        )

        if stage:
            query = query.filter(Opportunity.stage == stage)

        if status:
            query = query.filter(Opportunity.status == status)

        if search:
            search_term = f"%{search}%"
            query = (
                query.join(Company)
                .join(Contact)
                .filter(
                    or_(
                        Opportunity.name.ilike(search_term),
                        Opportunity.pot_id.ilike(search_term),
                        Company.name.ilike(search_term),
                        Contact.full_name.ilike(search_term),
                    )
                )
            )

        return (
            query.order_by(Opportunity.updated_on.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_opportunities_by_company(
        self, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[Opportunity]:
        """Get opportunities by company"""
        return (
            self.db.query(Opportunity)
            .options(joinedload(Opportunity.company), joinedload(Opportunity.contact))
            .filter(
                and_(
                    Opportunity.company_id == company_id,
                    Opportunity.is_active == True,
                    Opportunity.deleted_on.is_(None),
                )
            )
            .order_by(Opportunity.created_on.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_opportunities_by_lead(
        self, lead_id: int, skip: int = 0, limit: int = 100
    ) -> List[Opportunity]:
        """Get opportunities by lead"""
        return (
            self.db.query(Opportunity)
            .options(joinedload(Opportunity.company), joinedload(Opportunity.contact))
            .filter(
                and_(
                    Opportunity.lead_id == lead_id,
                    Opportunity.is_active == True,
                    Opportunity.deleted_on.is_(None),
                )
            )
            .order_by(Opportunity.created_on.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_opportunity_count(
        self, stage: str = None, status: str = None, search: str = None
    ) -> int:
        """Get total count of opportunities"""
        query = self.db.query(Opportunity).filter(
            and_(Opportunity.is_active == True, Opportunity.deleted_on.is_(None))
        )

        if stage:
            query = query.filter(Opportunity.stage == stage)

        if status:
            query = query.filter(Opportunity.status == status)

        if search:
            search_term = f"%{search}%"
            query = (
                query.join(Company)
                .join(Contact)
                .filter(
                    or_(
                        Opportunity.name.ilike(search_term),
                        Opportunity.pot_id.ilike(search_term),
                        Company.name.ilike(search_term),
                        Contact.full_name.ilike(search_term),
                    )
                )
            )

        return query.count()

    def get_pipeline_summary(self, user_id: int = None) -> dict:
        """Get enhanced opportunity pipeline summary"""
        query = self.db.query(Opportunity).filter(
            and_(
                Opportunity.is_active == True,
                Opportunity.deleted_on.is_(None),
                Opportunity.status == OpportunityStatus.OPEN,
            )
        )

        if user_id:
            query = query.filter(Opportunity.created_by == user_id)

        opportunities = query.all()

        total_opportunities = len(opportunities)
        total_value = sum(opp.amount or 0 for opp in opportunities)
        avg_scoring = (
            sum(opp.scoring for opp in opportunities) / total_opportunities
            if total_opportunities > 0
            else 0
        )
        closing_stage_count = len(
            [
                opp
                for opp in opportunities
                if opp.stage
                in [OpportunityStage.L4_NEGOTIATION, OpportunityStage.L5_WON]
            ]
        )

        # Enhanced stage-wise breakdown
        stage_breakdown = {}
        for opp in opportunities:
            stage = opp.stage.value
            stage_display = opp.stage_display_name
            if stage not in stage_breakdown:
                stage_breakdown[stage] = {
                    "stage": stage,
                    "stage_display": stage_display,
                    "count": 0,
                    "value": 0,
                    "percentage": opp.stage_percentage,
                }
            stage_breakdown[stage]["count"] += 1
            stage_breakdown[stage]["value"] += opp.amount or 0

        stage_breakdown_list = list(stage_breakdown.values())

        return {
            "summary": {
                "total_opportunities": total_opportunities,
                "total_value": total_value,
                "avg_scoring": round(avg_scoring, 2),
                "closing_stage_count": closing_stage_count,
            },
            "stage_breakdown": stage_breakdown_list,
        }

    def get_opportunity_metrics(self, user_id: int = None) -> dict:
        """Get enhanced opportunity metrics and analytics"""
        query = self.db.query(Opportunity).filter(
            and_(Opportunity.is_active == True, Opportunity.deleted_on.is_(None))
        )

        if user_id:
            query = query.filter(Opportunity.created_by == user_id)

        opportunities = query.all()

        total_opportunities = len(opportunities)
        won_opportunities = len(
            [opp for opp in opportunities if opp.status == OpportunityStatus.WON]
        )
        lost_opportunities = len(
            [opp for opp in opportunities if opp.status == OpportunityStatus.LOST]
        )

        win_rate = (
            (won_opportunities / total_opportunities * 100)
            if total_opportunities > 0
            else 0
        )

        won_opps = [opp for opp in opportunities if opp.status == OpportunityStatus.WON]
        avg_deal_size = (
            sum(opp.amount or Decimal(0) for opp in won_opps) / len(won_opps)
            if won_opps
            else Decimal(0)
        )

        pipeline_value = sum(
            opp.amount or Decimal(0)
            for opp in opportunities
            if opp.status == OpportunityStatus.OPEN
        )

        forecasted_revenue = sum(
            (opp.amount or Decimal(0)) * (Decimal(opp.probability) / Decimal(100))
            for opp in opportunities
            if opp.status == OpportunityStatus.OPEN
        )

        return {
            "total_opportunities": total_opportunities,
            "won_opportunities": won_opportunities,
            "lost_opportunities": lost_opportunities,
            "win_rate": round(win_rate, 2),
            "avg_deal_size": float(avg_deal_size),
            "pipeline_value": float(pipeline_value),
            "forecasted_revenue": float(forecasted_revenue),
        }
