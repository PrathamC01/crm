"""
Sales Process model for tracking opportunity stages
"""

from sqlalchemy import (
    Column,
    String,
    Text,
    ForeignKey,
    Date,
    Integer,
    Boolean,
    Enum as SQLEnum,
    DateTime,
    JSON,
)
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime
from .base import BaseModel


class SalesStage(str, Enum):
    L1_PROSPECT = "L1_Prospect"
    L2_NEED_ANALYSIS = "L2_Need_Analysis"
    L3_PROPOSAL = "L3_Proposal"
    WIN = "Win"
    LOSS = "Loss"


class StageStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    SKIPPED = "Skipped"


class SalesProcess(BaseModel):
    __tablename__ = "sales_processes"

    # Link to Opportunity
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False, index=True)
    
    # Stage Information
    stage = Column(SQLEnum(SalesStage), nullable=False, index=True)
    stage_order = Column(Integer, nullable=False)  # 1, 2, 3, 4, 5 for ordering
    status = Column(SQLEnum(StageStatus), default=StageStatus.OPEN, nullable=False)
    
    # Stage Details
    stage_completion_date = Column(Date)
    comments = Column(Text)
    notes = Column(Text)
    
    # File uploads for documentation
    documents = Column(JSON)  # Array of document objects
    
    # Stage-specific fields
    stage_data = Column(JSON)  # Flexible storage for stage-specific information
    
    # Completion tracking
    completed_by = Column(Integer, ForeignKey("users.id"))
    completion_notes = Column(Text)
    
    # Relationships
    opportunity = relationship("Opportunity", back_populates="sales_processes")
    completed_by_user = relationship("User", foreign_keys=[completed_by])
    
    creator = relationship(
        "User",
        foreign_keys="SalesProcess.created_by",
        overlaps="completed_by_user"
    )
    updater = relationship(
        "User",
        foreign_keys="SalesProcess.updated_by"
    )

    @property
    def stage_display_name(self):
        """Return user-friendly stage name"""
        stage_names = {
            SalesStage.L1_PROSPECT: "L1 - Prospect",
            SalesStage.L2_NEED_ANALYSIS: "L2 - Need Analysis",
            SalesStage.L3_PROPOSAL: "L3 - Proposal",
            SalesStage.WIN: "Win",
            SalesStage.LOSS: "Loss",
        }
        return stage_names.get(self.stage, self.stage.value)

    @property
    def can_proceed_to_next(self):
        """Check if can proceed to next stage"""
        return self.status == StageStatus.COMPLETED

    @property
    def is_final_stage(self):
        """Check if this is a final stage (Win/Loss)"""
        return self.stage in [SalesStage.WIN, SalesStage.LOSS]

    def __repr__(self):
        return f"<SalesProcess(opportunity_id={self.opportunity_id}, stage={self.stage}, status={self.status})>"