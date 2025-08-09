"""
Quotation service for opportunity quotations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from datetime import datetime, date
from decimal import Decimal

from ..models import Quotation, Opportunity, User
from ..models.quotation import QuotationStatus
from ..models.opportunity import OpportunityStage


class QuotationService:
    def __init__(self, db: Session):
        self.db = db

    def create_quotation(
        self, 
        opportunity_id: int,
        quotation_data: Dict[str, Any],
        created_by: int
    ) -> Quotation:
        """Create new quotation for opportunity"""
        # Get the opportunity
        opportunity = self.db.query(Opportunity).filter(
            and_(
                Opportunity.id == opportunity_id,
                Opportunity.is_active == True,
                Opportunity.deleted_on.is_(None)
            )
        ).first()
        
        if not opportunity:
            raise ValueError(f"Opportunity {opportunity_id} not found")
        
        # Check if quotations can be created (L3 stage requirement)
        if not opportunity.can_create_quotations:
            raise ValueError(f"Quotations can only be created after L3 (Proposal) stage is completed")

        try:
            # Prepare customer info from opportunity
            customer_info = {
                "company_name": opportunity.company.name if opportunity.company else None,
                "company_address": opportunity.company.address if opportunity.company else None,
                "contact_name": opportunity.contact.full_name if opportunity.contact else None,
                "contact_email": opportunity.contact.email if opportunity.contact else None,
                "contact_phone": opportunity.contact.phone if opportunity.contact else None,
            }

            quotation = Quotation(
                opportunity_id=opportunity_id,
                quotation_name=quotation_data.get('quotation_name'),
                quotation_date=quotation_data.get('quotation_date', date.today()),
                valid_until=quotation_data.get('valid_until'),
                amount=Decimal(str(quotation_data.get('amount', 0))),
                currency=quotation_data.get('currency', opportunity.currency or 'INR'),
                description=quotation_data.get('description'),
                terms_conditions=quotation_data.get('terms_conditions'),
                line_items=quotation_data.get('line_items', []),
                subtotal=Decimal(str(quotation_data.get('subtotal', 0))),
                tax_amount=Decimal(str(quotation_data.get('tax_amount', 0))),
                tax_percentage=Decimal(str(quotation_data.get('tax_percentage', 0))),
                discount_amount=Decimal(str(quotation_data.get('discount_amount', 0))),
                discount_percentage=Decimal(str(quotation_data.get('discount_percentage', 0))),
                total_amount=Decimal(str(quotation_data.get('total_amount', quotation_data.get('amount', 0)))),
                customer_info=customer_info,
                created_by=created_by
            )

            self.db.add(quotation)
            self.db.commit()
            self.db.refresh(quotation)
            
            return quotation
            
        except Exception as e:
            self.db.rollback()
            raise e

    def get_quotation_by_id(self, quotation_id: int) -> Optional[Quotation]:
        """Get quotation by ID"""
        return self.db.query(Quotation).options(
            joinedload(Quotation.opportunity),
            joinedload(Quotation.submitted_by_user),
            joinedload(Quotation.approved_by_user),
            joinedload(Quotation.creator)
        ).filter(
            and_(
                Quotation.id == quotation_id,
                Quotation.is_active == True,
                Quotation.deleted_on.is_(None)
            )
        ).first()

    def get_quotation_by_quotation_id(self, quotation_id: str) -> Optional[Quotation]:
        """Get quotation by quotation ID (QUO-YYYY-XXXX)"""
        return self.db.query(Quotation).options(
            joinedload(Quotation.opportunity),
            joinedload(Quotation.submitted_by_user),
            joinedload(Quotation.approved_by_user)
        ).filter(
            and_(
                Quotation.quotation_id == quotation_id,
                Quotation.is_active == True,
                Quotation.deleted_on.is_(None)
            )
        ).first()

    def get_quotations_by_opportunity(self, opportunity_id: int) -> List[Quotation]:
        """Get all quotations for an opportunity"""
        return self.db.query(Quotation).options(
            joinedload(Quotation.submitted_by_user),
            joinedload(Quotation.approved_by_user)
        ).filter(
            and_(
                Quotation.opportunity_id == opportunity_id,
                Quotation.is_active == True,
                Quotation.deleted_on.is_(None)
            )
        ).order_by(desc(Quotation.created_on)).all()

    def update_quotation(
        self, 
        quotation_id: int, 
        quotation_data: Dict[str, Any],
        updated_by: int
    ) -> Quotation:
        """Update quotation"""
        quotation = self.get_quotation_by_id(quotation_id)
        if not quotation:
            raise ValueError(f"Quotation {quotation_id} not found")

        if not quotation.is_editable:
            raise ValueError(f"Quotation {quotation.quotation_id} cannot be edited in current status: {quotation.status}")

        try:
            # Update fields
            for field, value in quotation_data.items():
                if hasattr(quotation, field) and field not in ['id', 'quotation_id', 'created_on', 'created_by']:
                    if field in ['amount', 'subtotal', 'tax_amount', 'tax_percentage', 'discount_amount', 'discount_percentage', 'total_amount']:
                        setattr(quotation, field, Decimal(str(value)) if value is not None else None)
                    else:
                        setattr(quotation, field, value)

            quotation.updated_by = updated_by
            quotation.updated_on = datetime.utcnow()

            self.db.commit()
            self.db.refresh(quotation)
            
            return quotation
            
        except Exception as e:
            self.db.rollback()
            raise e

    def submit_quotation(self, quotation_id: int, submitted_by: int) -> Quotation:
        """Submit quotation for approval"""
        quotation = self.get_quotation_by_id(quotation_id)
        if not quotation:
            raise ValueError(f"Quotation {quotation_id} not found")

        if not quotation.can_submit:
            raise ValueError(f"Quotation {quotation.quotation_id} cannot be submitted. Status: {quotation.status}")

        quotation.status = QuotationStatus.SUBMITTED
        quotation.submitted_date = datetime.utcnow()
        quotation.submitted_by = submitted_by

        self.db.commit()
        self.db.refresh(quotation)
        
        return quotation

    def approve_quotation(
        self, 
        quotation_id: int, 
        approved_by: int,
        approval_notes: Optional[str] = None
    ) -> Quotation:
        """Approve quotation"""
        quotation = self.get_quotation_by_id(quotation_id)
        if not quotation:
            raise ValueError(f"Quotation {quotation_id} not found")

        if not quotation.can_approve:
            raise ValueError(f"Quotation {quotation.quotation_id} cannot be approved. Status: {quotation.status}")

        quotation.status = QuotationStatus.APPROVED
        quotation.approved_date = datetime.utcnow()
        quotation.approved_by = approved_by
        
        if approval_notes:
            quotation.notes = approval_notes

        self.db.commit()
        self.db.refresh(quotation)
        
        return quotation

    def reject_quotation(
        self, 
        quotation_id: int, 
        rejected_by: int,
        rejection_reason: str
    ) -> Quotation:
        """Reject quotation"""
        quotation = self.get_quotation_by_id(quotation_id)
        if not quotation:
            raise ValueError(f"Quotation {quotation_id} not found")

        if quotation.status != QuotationStatus.SUBMITTED:
            raise ValueError(f"Only submitted quotations can be rejected. Current status: {quotation.status}")

        quotation.status = QuotationStatus.REJECTED
        quotation.rejection_reason = rejection_reason
        quotation.updated_by = rejected_by
        quotation.updated_on = datetime.utcnow()

        self.db.commit()
        self.db.refresh(quotation)
        
        return quotation

    def create_quotation_revision(
        self, 
        parent_quotation_id: int, 
        quotation_data: Dict[str, Any],
        created_by: int,
        revision_notes: Optional[str] = None
    ) -> Quotation:
        """Create revision of existing quotation"""
        parent_quotation = self.get_quotation_by_id(parent_quotation_id)
        if not parent_quotation:
            raise ValueError(f"Parent quotation {parent_quotation_id} not found")

        try:
            # Create new quotation as revision
            revision_data = quotation_data.copy()
            revision_data.update({
                'opportunity_id': parent_quotation.opportunity_id,
                'parent_quotation_id': parent_quotation_id,
                'revision_number': parent_quotation.revision_number + 1,
                'revision_notes': revision_notes,
                'customer_info': parent_quotation.customer_info
            })

            revision = self.create_quotation(
                opportunity_id=parent_quotation.opportunity_id,
                quotation_data=revision_data,
                created_by=created_by
            )

            # Mark parent as revised
            parent_quotation.status = QuotationStatus.REVISED
            self.db.commit()
            
            return revision
            
        except Exception as e:
            self.db.rollback()
            raise e

    def get_quotations_list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status_filter: Optional[str] = None,
        opportunity_filter: Optional[int] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated list of quotations with filters"""
        query = self.db.query(Quotation).options(
            joinedload(Quotation.opportunity),
            joinedload(Quotation.submitted_by_user)
        ).filter(
            and_(
                Quotation.is_active == True,
                Quotation.deleted_on.is_(None)
            )
        )

        # Apply filters
        if status_filter:
            query = query.filter(Quotation.status == status_filter)
        
        if opportunity_filter:
            query = query.filter(Quotation.opportunity_id == opportunity_filter)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Quotation.quotation_id.ilike(search_term),
                    Quotation.quotation_name.ilike(search_term)
                )
            )

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        quotations = query.order_by(desc(Quotation.created_on)).offset(skip).limit(limit).all()

        return {
            "quotations": quotations,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    def delete_quotation(self, quotation_id: int, deleted_by: int) -> bool:
        """Soft delete quotation"""
        quotation = self.get_quotation_by_id(quotation_id)
        if not quotation:
            raise ValueError(f"Quotation {quotation_id} not found")

        if quotation.status in [QuotationStatus.SUBMITTED, QuotationStatus.APPROVED]:
            raise ValueError(f"Cannot delete quotation in status: {quotation.status}")

        quotation.is_active = False
        quotation.deleted_on = datetime.utcnow()
        quotation.updated_by = deleted_by

        self.db.commit()
        return True

    def get_quotation_statistics(self) -> Dict[str, Any]:
        """Get quotation statistics"""
        total_quotations = self.db.query(Quotation).filter(
            and_(
                Quotation.is_active == True,
                Quotation.deleted_on.is_(None)
            )
        ).count()

        # Status-wise breakdown
        status_counts = {}
        for status in QuotationStatus:
            count = self.db.query(Quotation).filter(
                and_(
                    Quotation.status == status,
                    Quotation.is_active == True,
                    Quotation.deleted_on.is_(None)
                )
            ).count()
            status_counts[status.value] = count

        # Calculate total value
        total_value = self.db.query(Quotation).filter(
            and_(
                Quotation.is_active == True,
                Quotation.deleted_on.is_(None)
            )
        ).with_entities(Quotation.total_amount).all()
        
        total_amount = sum([quot.total_amount for quot in total_value if quot.total_amount])

        return {
            "total_quotations": total_quotations,
            "status_breakdown": status_counts,
            "total_value": total_amount,
            "approval_rate": (status_counts.get("Approved", 0) / total_quotations * 100) if total_quotations > 0 else 0
        }