"""
Enhanced Lead management service with conversion workflow
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from ..models import (
    Lead,
    Company,
    User,
    LeadStatus,
    ReviewStatus,
    LeadSource,
    LeadSubType,
    TenderSubType,
    SubmissionType,
    LeadPriority,
)
from .contact_service import ContactService


def parse_date_field(date_value):
    """Parse date field from string to date object"""
    if not date_value:
        return None
    if isinstance(date_value, date):
        return date_value
    if isinstance(date_value, str):
        try:
            return datetime.strptime(date_value, "%Y-%m-%d").date()
        except ValueError:
            try:
                return datetime.strptime(date_value, "%Y-%m-%dT%H:%M:%S").date()
            except ValueError:
                return None
    return None


class LeadService:
    def __init__(self, db: Session):
        self.db = db

    def create_lead(self, lead_data: dict, created_by: Optional[int] = None) -> Lead:
        """Create a new lead"""

        # Handle enum conversions safely
        def safe_enum_convert(value, enum_class):
            if value is None:
                return None
            if isinstance(value, enum_class):
                return value
            if isinstance(value, str):
                try:
                    return enum_class(value)
                except ValueError:
                    # If direct conversion fails, try to find by name
                    for enum_member in enum_class:
                        if enum_member.value == value:
                            return enum_member
                    raise ValueError(f"Invalid {enum_class.__name__} value: {value}")
            return value

        try:
            db_lead = Lead(
                project_title=lead_data.get("project_title"),
                lead_source=safe_enum_convert(lead_data.get("lead_source"), LeadSource),
                lead_sub_type=safe_enum_convert(
                    lead_data.get("lead_sub_type"), LeadSubType
                ),
                tender_sub_type=safe_enum_convert(
                    lead_data.get("tender_sub_type"), TenderSubType
                ),
                products_services=lead_data.get("products_services", []),
                company_id=lead_data.get("company_id"),
                sub_business_type=lead_data.get("sub_business_type"),
                end_customer_id=lead_data.get("end_customer_id"),
                end_customer_region=lead_data.get("end_customer_region"),
                partner_involved=lead_data.get("partner_involved", False),
                partners_data=lead_data.get("partners_data", []),
                tender_fee=lead_data.get("tender_fee"),
                currency=lead_data.get("currency", "INR"),
                submission_type=safe_enum_convert(
                    lead_data.get("submission_type"), SubmissionType
                ),
                tender_authority=lead_data.get("tender_authority"),
                tender_for=lead_data.get("tender_for"),
                # New tender details fields
                tender_id=lead_data.get("tender_details", {}).get("tender_id") if lead_data.get("tender_details") else None,
                tender_authority_name=lead_data.get("tender_details", {}).get("authority") if lead_data.get("tender_details") else None,
                bid_due_date=parse_date_field(lead_data.get("tender_details", {}).get("bid_due_date")) if lead_data.get("tender_details") else None,
                emd_required=lead_data.get("emd_required", False),
                emd_amount=lead_data.get("emd_amount"),
                emd_currency=lead_data.get("emd_currency", "INR"),
                bg_required=lead_data.get("bg_required", False),
                bg_amount=lead_data.get("bg_amount"),
                bg_currency=lead_data.get("bg_currency", "INR"),
                important_dates=lead_data.get("important_dates", []),
                clauses=lead_data.get("clauses", []),
                expected_revenue=lead_data.get("expected_revenue"),
                revenue_currency=lead_data.get("revenue_currency", "INR"),
                convert_to_opportunity_date=lead_data.get(
                    "convert_to_opportunity_date"
                ),
                competitors=lead_data.get("competitors", []),
                documents=lead_data.get("documents", []),
                status=safe_enum_convert(
                    lead_data.get("status") or LeadStatus.NEW, LeadStatus
                ),
                priority=safe_enum_convert(
                    lead_data.get("priority") or LeadPriority.MEDIUM, LeadPriority
                ),
                qualification_notes=lead_data.get("qualification_notes"),
                lead_score=lead_data.get("lead_score", 0),
                contacts=lead_data.get("contacts", []),
                created_by=created_by,
            )

            self.db.add(db_lead)
            self.db.commit()
            self.db.refresh(db_lead)
            for contact in lead_data.get("contacts", []):
                (ContactService(self.db)).create_contact(
                    contact_data={"company_id": lead_data.get("company_id"), **contact},
                    created_by=created_by,
                )
            return db_lead
        except Exception as e:
            self.db.rollback()
            print(f"Lead creation error: {e}")
            raise e

    def get_lead_by_id(self, lead_id: int) -> Optional[Lead]:
        """Get lead by ID with related details"""
        return (
            self.db.query(Lead)
            .options(
                joinedload(Lead.company),
                joinedload(Lead.end_customer),
                joinedload(Lead.creator),
                joinedload(Lead.conversion_requester),
                joinedload(Lead.reviewer),
            )
            .filter(
                and_(
                    Lead.id == lead_id,
                    Lead.is_active == True,
                    Lead.deleted_on.is_(None),
                )
            )
            .first()
        )

    def update_lead(
        self, lead_id: int, lead_data: dict, updated_by: Optional[int] = None
    ) -> Optional[Lead]:
        """Update lead information"""
        db_lead = self.get_lead_by_id(lead_id)
        if not db_lead:
            return None

        for field, value in lead_data.items():
            if field not in ["id", "created_on", "created_by"] and value is not None:
                if field == "lead_source" and value:
                    value = LeadSource(value)
                elif field == "lead_sub_type" and value:
                    value = LeadSubType(value)
                elif field == "tender_sub_type" and value:
                    value = TenderSubType(value)
                elif field == "submission_type" and value:
                    value = SubmissionType(value)
                elif field == "status" and value:
                    value = LeadStatus(value)
                elif field == "priority" and value:
                    value = LeadPriority(value)
                elif field == "tender_details" and value:
                    # Handle nested tender_details mapping
                    if isinstance(value, dict):
                        setattr(db_lead, "tender_id", value.get("tender_id"))
                        setattr(db_lead, "tender_authority_name", value.get("authority"))
                        setattr(db_lead, "bid_due_date", value.get("bid_due_date"))
                    continue  # Skip setattr for this field since we handled it above

                setattr(db_lead, field, value)

        if updated_by:
            db_lead.updated_by = updated_by

        self.db.commit()
        self.db.refresh(db_lead)
        return db_lead

    def get_leads(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str = None,
        status: str = None,
        company_id: str = None,
        review_status: str = None,
    ) -> List[Lead]:
        """Get all leads with pagination and filtering"""
        query = (
            self.db.query(Lead)
            .options(
                joinedload(Lead.company),
                joinedload(Lead.end_customer),
                joinedload(Lead.creator),
                joinedload(Lead.conversion_requester),
                joinedload(Lead.reviewer),
            )
            .filter(and_(Lead.is_active == True, Lead.deleted_on.is_(None)))
        )

        if status:
            query = query.filter(Lead.status == LeadStatus(status))

        if company_id:
            query = query.filter(Lead.company_id == company_id)

        if review_status:
            query = query.filter(Lead.review_status == ReviewStatus(review_status))

        if search:
            search_term = f"%{search}%"
            query = query.join(Company, Lead.company_id == Company.id).filter(
                or_(
                    Lead.project_title.ilike(search_term),
                    Company.name.ilike(search_term),
                    Lead.tender_authority.ilike(search_term),
                )
            )

        return query.order_by(Lead.updated_on.desc()).offset(skip).limit(limit).all()

    def get_leads_count(
        self,
        search: str = None,
        status: str = None,
        company_id: str = None,
        review_status: str = None,
    ) -> int:
        """Get total count of leads"""
        query = self.db.query(Lead).filter(
            and_(Lead.is_active == True, Lead.deleted_on.is_(None))
        )

        if status:
            query = query.filter(Lead.status == LeadStatus(status))

        if company_id:
            query = query.filter(Lead.company_id == company_id)

        if review_status:
            query = query.filter(Lead.review_status == ReviewStatus(review_status))

        if search:
            search_term = f"%{search}%"
            query = query.join(Company, Lead.company_id == Company.id).filter(
                or_(
                    Lead.project_title.ilike(search_term),
                    Company.name.ilike(search_term),
                    Lead.tender_authority.ilike(search_term),
                )
            )

        return query.count()

    def get_lead_stats(self) -> dict:
        """Get lead statistics"""
        total = (
            self.db.query(Lead)
            .filter(and_(Lead.is_active == True, Lead.deleted_on.is_(None)))
            .count()
        )

        new = (
            self.db.query(Lead)
            .filter(
                and_(
                    Lead.status == LeadStatus.NEW,
                    Lead.is_active == True,
                    Lead.deleted_on.is_(None),
                )
            )
            .count()
        )

        contacted = (
            self.db.query(Lead)
            .filter(
                and_(
                    Lead.status == LeadStatus.CONTACTED,
                    Lead.is_active == True,
                    Lead.deleted_on.is_(None),
                )
            )
            .count()
        )

        qualified = (
            self.db.query(Lead)
            .filter(
                and_(
                    Lead.status == LeadStatus.QUALIFIED,
                    Lead.is_active == True,
                    Lead.deleted_on.is_(None),
                )
            )
            .count()
        )

        converted = (
            self.db.query(Lead)
            .filter(
                and_(
                    Lead.converted == True,
                    Lead.is_active == True,
                    Lead.deleted_on.is_(None),
                )
            )
            .count()
        )

        pending_review = (
            self.db.query(Lead)
            .filter(
                and_(
                    Lead.conversion_requested == True,
                    Lead.reviewed == False,
                    Lead.is_active == True,
                    Lead.deleted_on.is_(None),
                )
            )
            .count()
        )

        approved_for_conversion = (
            self.db.query(Lead)
            .filter(
                and_(
                    Lead.review_status == ReviewStatus.APPROVED,
                    Lead.converted == False,
                    Lead.is_active == True,
                    Lead.deleted_on.is_(None),
                )
            )
            .count()
        )

        # Calculate total value
        total_value = (
            self.db.query(func.sum(Lead.expected_revenue))
            .filter(and_(Lead.is_active == True, Lead.deleted_on.is_(None)))
            .scalar()
            or 0
        )

        return {
            "total": total,
            "new": new,
            "contacted": contacted,
            "qualified": qualified,
            "converted": converted,
            "pending_review": pending_review,
            "approved_for_conversion": approved_for_conversion,
            "total_value": total_value,
        }

    def get_leads_pending_review(self) -> List[Lead]:
        """Get leads pending admin review"""
        return (
            self.db.query(Lead)
            .options(joinedload(Lead.company), joinedload(Lead.conversion_requester))
            .filter(
                and_(
                    Lead.conversion_requested == True,
                    Lead.reviewed == False,
                    Lead.is_active == True,
                    Lead.deleted_on.is_(None),
                )
            )
            .order_by(Lead.conversion_request_date.asc())
            .all()
        )

    # Conversion Workflow Methods

    def request_conversion(
        self, lead_id: int, requester_id: int, notes: str = None
    ) -> Optional[Lead]:
        """Request conversion of qualified lead to opportunity"""
        db_lead = self.get_lead_by_id(lead_id)
        if not db_lead:
            return None

        if not db_lead.can_request_conversion:
            raise ValueError("Lead cannot request conversion at this time")

        db_lead.conversion_requested = True
        db_lead.conversion_request_date = datetime.utcnow()
        db_lead.conversion_requested_by = requester_id
        db_lead.conversion_notes = notes
        db_lead.updated_by = requester_id

        self.db.commit()
        self.db.refresh(db_lead)
        return db_lead

    def review_conversion_request(
        self, lead_id: int, reviewer_id: int, decision: ReviewStatus, comments: str
    ) -> Optional[Lead]:
        """Review and approve/reject conversion request (Admin only)"""
        db_lead = self.get_lead_by_id(lead_id)
        if not db_lead:
            return None

        if not db_lead.needs_admin_review:
            raise ValueError("Lead does not need review at this time")

        db_lead.reviewed = True
        db_lead.review_status = decision
        db_lead.reviewed_by = reviewer_id
        db_lead.review_date = datetime.utcnow()
        db_lead.review_comments = comments
        db_lead.updated_by = reviewer_id

        # If approved, mark as ready for conversion
        if decision == ReviewStatus.APPROVED:
            db_lead.ready_for_conversion = True

        self.db.commit()
        self.db.refresh(db_lead)
        return db_lead

    def mark_as_converted(
        self, lead_id: int, opportunity_id: int, converted_by: int, notes: str = None
    ) -> Optional[Lead]:
        """Mark lead as converted to opportunity"""
        db_lead = self.get_lead_by_id(lead_id)
        if not db_lead:
            return None

        db_lead.converted = True
        db_lead.converted_to_opportunity_id = opportunity_id
        db_lead.conversion_date = datetime.utcnow()
        db_lead.conversion_notes = notes
        db_lead.status = LeadStatus.CONVERTED
        db_lead.updated_by = converted_by

        self.db.commit()
        self.db.refresh(db_lead)
        return db_lead

    def add_document(
        self, lead_id: int, document_data: dict, added_by: int
    ) -> Optional[Lead]:
        """Add document to lead"""
        db_lead = self.get_lead_by_id(lead_id)
        if not db_lead:
            return None

        documents = db_lead.documents or []
        documents.append(
            {
                **document_data,
                "uploaded_on": datetime.utcnow().isoformat(),
                "uploaded_by": added_by,
            }
        )

        db_lead.documents = documents
        db_lead.updated_by = added_by

        self.db.commit()
        self.db.refresh(db_lead)
        return db_lead

    def delete_lead(self, lead_id: int, deleted_by: Optional[int] = None) -> bool:
        """Soft delete lead"""
        db_lead = self.get_lead_by_id(lead_id)
        if not db_lead:
            return False

        db_lead.is_active = False
        db_lead.deleted_on = datetime.utcnow()
        if deleted_by:
            db_lead.deleted_by = deleted_by

        self.db.commit()
        return True
