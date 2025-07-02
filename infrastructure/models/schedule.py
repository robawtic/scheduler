from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base
from .custom_types import UUIDType, DateTimeType
from .shift_assignment import ShiftAssignmentModel

class ScheduleModel(Base):
    """SQLAlchemy model for schedules."""
    __tablename__ = "schedules"

    # Column definitions
    id = Column(UUIDType, primary_key=True)
    team_id = Column(Integer, nullable=False, index=True)
    start_date = Column(DateTimeType, nullable=False, index=True)
    periods_per_day = Column(Integer, nullable=False, default=4)
    is_published = Column(Boolean, default=False)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTimeType, nullable=False, default=datetime.now)
    updated_at = Column(DateTimeType, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relationships
    assignments = relationship("ShiftAssignmentModel", back_populates="schedule", cascade="all, delete-orphan")
