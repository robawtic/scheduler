from sqlalchemy import Boolean, Column, Integer, String, JSON
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import relationship

from .base import Base

class WorkstationModel(Base):
    """SQLAlchemy model for workstations."""
    __tablename__ = "workstations"

    id = Column(PgUUID(as_uuid=True), primary_key=True)
    station_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    team_id = Column(Integer, nullable=False, index=True)
    line_type_id = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    required_qualifications = Column(JSON, nullable=False, default=list)  # List of qualification names
    capacity = Column(Integer, nullable=False, default=1)
    equipment_type = Column(String, nullable=True)
    location = Column(String, nullable=True)
    maintenance_schedule = Column(JSON, nullable=False, default=dict)  # Dict[str, int] 