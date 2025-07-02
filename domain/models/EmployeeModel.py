# domain/models/EmployeeModel.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from domain.models.Base import Base


class EmployeeModel(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    employee_id = Column(String(100), nullable=False, unique=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    team = relationship('TeamModel', back_populates='employees')
    team_memberships = relationship('TeamMemberModel', back_populates='employee')

