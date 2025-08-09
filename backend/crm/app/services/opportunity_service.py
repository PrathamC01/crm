"""
Opportunity service with Lead-based creation workflow
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from datetime import datetime, date

from ..models import Opportunity, Lead, SalesProcess, Quotation, User
from ..models.opportunity import OpportunityStatus, OpportunityStage
from ..models.sales_process import SalesStage, StageStatus
from ..models.lead import LeadStatus, ReviewStatus


class OpportunityService:
    def __init__(self, db: Session):
        self.db = db

    def create_opportunity_from_lead(
        self, 
        lead_id: int, 
        converted_by_user_id: int, 
        approved_by_user_id: Optional[int] = None,
        conversion_notes: Optional[str] = None
    ) -> Opportunity:
        """
        Create opportunity from lead with complete data preservation
        This is the ONLY way opportunities should be created
        """
        # Get the lead with all related data
        lead = self.db.query(Lead).options(
            joinedload(Lead.company),
            joinedload(Lead.end_customer),
            joinedload(Lead.contacts)
        ).filter(
            and_(
                Lead.id == lead_id,
                Lead.is_active == True,
                Lead.deleted_on.is_(None)
            )
        ).first()
        
        if not lead:
            raise ValueError(f"Lead with ID {lead_id} not found")
        
        # Check if lead is already converted
        if lead.converted:
            raise ValueError(f"Lead {lead_id} has already been converted to an opportunity")
        
        # Check if lead is qualified and approved for conversion
        if lead.status != LeadStatus.QUALIFIED:
            raise ValueError(f"Lead must be Qualified before conversion. Current status: {lead.status}")
        
        if not lead.reviewed or lead.review_status != ReviewStatus.APPROVED:
            raise ValueError(f"Lead must be reviewed and approved before conversion")
        
        # Check if opportunity already exists for this lead
        existing_opportunity = self.db.query(Opportunity).filter(
            Opportunity.lead_id == lead_id
        ).first()
        
        if existing_opportunity:
            raise ValueError(f"Opportunity already exists for Lead {lead_id}: {existing_opportunity.pot_id}")

        try:
            # Create opportunity from lead
            opportunity = Opportunity.create_from_lead(
                lead=lead,
                converted_by_user_id=converted_by_user_id,
                approved_by_user_id=approved_by_user_id
            )
            
            # Add conversion notes if provided
            if conversion_notes:
                opportunity.notes = conversion_notes
            
            self.db.add(opportunity)
            self.db.flush()  # Get the opportunity ID
            
            # Create initial sales process stages
            self._initialize_sales_processes(opportunity.id, converted_by_user_id)
            
            # Update lead status
            lead.converted = True
            lead.converted_to_opportunity_id = opportunity.pot_id
            lead.conversion_date = datetime.utcnow()
            lead.conversion_notes = conversion_notes
            lead.status = LeadStatus.CONVERTED
            
            self.db.commit()
            self.db.refresh(opportunity)
            
            return opportunity
            
        except Exception as e:
            self.db.rollback()
            raise e

    def _initialize_sales_processes(self, opportunity_id: int, created_by: int):
        """Initialize all sales process stages for new opportunity"""
        stages = [
            (SalesStage.L1_PROSPECT, 1),
            (SalesStage.L2_NEED_ANALYSIS, 2),
            (SalesStage.L3_PROPOSAL, 3),
            (SalesStage.WIN, 4),
            (SalesStage.LOSS, 5)
        ]
        
        for stage, order in stages:
            # First stage (L1) starts as In Progress, others as Open
            status = StageStatus.IN_PROGRESS if stage == SalesStage.L1_PROSPECT else StageStatus.OPEN
            
            sales_process = SalesProcess(
                opportunity_id=opportunity_id,
                stage=stage,
                stage_order=order,
                status=status,
                created_by=created_by
            )
            self.db.add(sales_process)

    def get_opportunity_by_id(self, opportunity_id: int) -> Optional[Opportunity]:
        """Get opportunity by ID with all related data"""
        return self.db.query(Opportunity).options(
            joinedload(Opportunity.lead),
            joinedload(Opportunity.company),
            joinedload(Opportunity.contact),
            joinedload(Opportunity.converted_by_user),
            joinedload(Opportunity.approved_by_user),
            joinedload(Opportunity.sales_processes),
            joinedload(Opportunity.quotations)
        ).filter(
            and_(
                Opportunity.id == opportunity_id,
                Opportunity.is_active == True,
                Opportunity.deleted_on.is_(None)
            )
        ).first()

    def get_opportunity_by_pot_id(self, pot_id: str) -> Optional[Opportunity]:
        """Get opportunity by POT ID"""
        return self.db.query(Opportunity).options(
            joinedload(Opportunity.lead),
            joinedload(Opportunity.company),
            joinedload(Opportunity.contact),
            joinedload(Opportunity.sales_processes),
            joinedload(Opportunity.quotations)
        ).filter(
            and_(
                Opportunity.pot_id == pot_id,
                Opportunity.is_active == True,
                Opportunity.deleted_on.is_(None)
            )
        ).first()

    def get_opportunities_list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status_filter: Optional[str] = None,
        stage_filter: Optional[str] = None,
        user_filter: Optional[int] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated list of opportunities with filters"""
        query = self.db.query(Opportunity).options(
            joinedload(Opportunity.lead),
            joinedload(Opportunity.company),
            joinedload(Opportunity.converted_by_user)
        ).filter(
            and_(
                Opportunity.is_active == True,
                Opportunity.deleted_on.is_(None)
            )
        )

        # Apply filters
        if status_filter:
            query = query.filter(Opportunity.status == status_filter)
        
        if stage_filter:
            query = query.filter(Opportunity.current_stage == stage_filter)
        
        if user_filter:
            query = query.filter(Opportunity.converted_by == user_filter)
        
        if search:
            search_term = f"%{search}%"
            query = query.join(Opportunity.company).filter(
                or_(
                    Opportunity.name.ilike(search_term),
                    Opportunity.pot_id.ilike(search_term),
                    Opportunity.company.name.ilike(search_term)
                )
            )

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        opportunities = query.order_by(desc(Opportunity.created_on)).offset(skip).limit(limit).all()

        return {
            "opportunities": opportunities,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    def update_sales_stage(
        self, 
        opportunity_id: int, 
        stage: SalesStage, 
        status: StageStatus,
        completion_date: Optional[date] = None,
        comments: Optional[str] = None,
        documents: Optional[List[Dict]] = None,
        updated_by: Optional[int] = None
    ) -> SalesProcess:
        """Update sales process stage"""
        # Get the opportunity
        opportunity = self.get_opportunity_by_id(opportunity_id)
        if not opportunity:
            raise ValueError(f"Opportunity {opportunity_id} not found")

        # Get the sales process for this stage
        sales_process = self.db.query(SalesProcess).filter(
            and_(
                SalesProcess.opportunity_id == opportunity_id,
                SalesProcess.stage == stage
            )
        ).first()

        if not sales_process:
            raise ValueError(f"Sales process stage {stage} not found for opportunity {opportunity_id}")

        # Check if previous stages are completed (except for Win/Loss which can be set anytime)
        if stage not in [SalesStage.WIN, SalesStage.LOSS]:
            self._validate_stage_progression(opportunity_id, stage)

        # Update sales process
        sales_process.status = status
        sales_process.completion_date = completion_date
        sales_process.comments = comments
        sales_process.updated_by = updated_by

        if documents:
            sales_process.documents = documents

        if status == StageStatus.COMPLETED:
            sales_process.completed_by = updated_by
            sales_process.stage_completion_date = completion_date or date.today()
            
            # Update opportunity stage and completion flags
            opportunity.current_stage = stage
            
            if stage == SalesStage.L1_PROSPECT:
                opportunity.l1_completed = True
                opportunity.l1_completion_date = sales_process.stage_completion_date
            elif stage == SalesStage.L2_NEED_ANALYSIS:
                opportunity.l2_completed = True
                opportunity.l2_completion_date = sales_process.stage_completion_date
            elif stage == SalesStage.L3_PROPOSAL:
                opportunity.l3_completed = True
                opportunity.l3_completion_date = sales_process.stage_completion_date
            elif stage == SalesStage.WIN:
                opportunity.status = OpportunityStatus.WON
                opportunity.won_date = sales_process.stage_completion_date
                opportunity.probability = 100
            elif stage == SalesStage.LOSS:
                opportunity.status = OpportunityStatus.LOST
                opportunity.lost_date = sales_process.stage_completion_date
                opportunity.probability = 0

        self.db.commit()
        self.db.refresh(sales_process)
        
        return sales_process

    def _validate_stage_progression(self, opportunity_id: int, target_stage: SalesStage):
        """Validate that previous stages are completed before moving to target stage"""
        stage_order = {
            SalesStage.L1_PROSPECT: 1,
            SalesStage.L2_NEED_ANALYSIS: 2,
            SalesStage.L3_PROPOSAL: 3,
        }
        
        if target_stage not in stage_order:
            return  # Win/Loss can be set anytime
        
        target_order = stage_order[target_stage]
        
        # Check that all previous stages are completed
        for stage, order in stage_order.items():
            if order < target_order:
                process = self.db.query(SalesProcess).filter(
                    and_(
                        SalesProcess.opportunity_id == opportunity_id,
                        SalesProcess.stage == stage
                    )
                ).first()
                
                if not process or process.status != StageStatus.COMPLETED:
                    raise ValueError(f"Cannot move to {target_stage.value}. Previous stage {stage.value} must be completed first.")

    def get_sales_processes(self, opportunity_id: int) -> List[SalesProcess]:
        """Get all sales processes for an opportunity"""
        return self.db.query(SalesProcess).filter(
            SalesProcess.opportunity_id == opportunity_id
        ).order_by(SalesProcess.stage_order).all()

    def can_user_convert_lead(self, user_id: int, lead_id: int) -> Dict[str, Any]:
        """Check if user can convert lead to opportunity"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"can_convert": False, "reason": "User not found"}

        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return {"can_convert": False, "reason": "Lead not found"}

        # Check if already converted
        if lead.converted:
            return {"can_convert": False, "reason": "Lead already converted"}

        # Check lead status
        if lead.status != LeadStatus.QUALIFIED:
            return {"can_convert": False, "reason": "Lead must be Qualified"}

        # Check approval status
        if not lead.reviewed or lead.review_status != ReviewStatus.APPROVED:
            return {"can_convert": False, "reason": "Lead must be approved by Admin/Reviewer"}

        # Role-based checks
        user_role = user.role.name if user.role else "Unknown"
        
        if user_role in ["Admin", "Reviewer"]:
            # Admin and Reviewers can convert directly
            return {"can_convert": True, "requires_approval": False}
        elif user_role == "Sales":
            # Sales users can convert only if already approved
            if lead.review_status == ReviewStatus.APPROVED:
                return {"can_convert": True, "requires_approval": False}
            else:
                return {"can_convert": False, "reason": "Requires Admin/Reviewer approval"}
        else:
            return {"can_convert": False, "reason": "Insufficient permissions"}

    def get_opportunity_statistics(self) -> Dict[str, Any]:
        """Get opportunity statistics"""
        total_opportunities = self.db.query(Opportunity).filter(
            and_(
                Opportunity.is_active == True,
                Opportunity.deleted_on.is_(None)
            )
        ).count()

        won_opportunities = self.db.query(Opportunity).filter(
            and_(
                Opportunity.status == OpportunityStatus.WON,
                Opportunity.is_active == True,
                Opportunity.deleted_on.is_(None)
            )
        ).count()

        lost_opportunities = self.db.query(Opportunity).filter(
            and_(
                Opportunity.status == OpportunityStatus.LOST,
                Opportunity.is_active == True,
                Opportunity.deleted_on.is_(None)
            )
        ).count()

        # Stage-wise breakdown
        stage_counts = {}
        for stage in OpportunityStage:
            count = self.db.query(Opportunity).filter(
                and_(
                    Opportunity.current_stage == stage,
                    Opportunity.is_active == True,
                    Opportunity.deleted_on.is_(None)
                )
            ).count()
            stage_counts[stage.value] = count

        # Calculate total value
        total_value = self.db.query(Opportunity).filter(
            and_(
                Opportunity.is_active == True,
                Opportunity.deleted_on.is_(None)
            )
        ).with_entities(Opportunity.amount).all()
        
        total_amount = sum([opp.amount for opp in total_value if opp.amount])

        return {
            "total_opportunities": total_opportunities,
            "won_opportunities": won_opportunities,
            "lost_opportunities": lost_opportunities,
            "open_opportunities": total_opportunities - won_opportunities - lost_opportunities,
            "stage_breakdown": stage_counts,
            "total_value": total_amount,
            "win_rate": (won_opportunities / total_opportunities * 100) if total_opportunities > 0 else 0
        }