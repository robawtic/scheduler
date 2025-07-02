from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import relationship

from .base import Base

class EmployeeModel(Base):
    """SQLAlchemy model for employees."""
    __tablename__ = "employees"

    id = Column(PgUUID(as_uuid=True), primary_key=True)
    employee_id = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    team_id = Column(Integer, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
