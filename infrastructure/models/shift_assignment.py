from uuid import UUID

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base
from .custom_types import UUIDType

class ShiftAssignmentModel(Base):
    """SQLAlchemy model for shift assignments."""
    __tablename__ = "shift_assignments"

    # Column definitions
    id = Column(UUIDType, primary_key=True)
    schedule_id = Column(UUIDType, ForeignKey("schedules.id"), nullable=False)
    employee_id = Column(UUIDType, nullable=False)
    workstation_id = Column(UUIDType, nullable=False)
    period = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="scheduled")
    notes = Column(String)

    # Relationships
    schedule = relationship("ScheduleModel", back_populates="assignments")
