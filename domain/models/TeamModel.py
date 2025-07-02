from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from .Base import Base



class TeamModel(Base):
    __tablename__ = 'teams'
    __table_args__ = {'extend_existing': True}  # Add this to prevent table redefinition errors

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    group = relationship('GroupModel', back_populates='teams', lazy='joined')
    members = relationship('TeamMemberModel', back_populates='team', lazy='joined')
    workstations = relationship('WorkstationModel', back_populates='team', lazy='joined')
    employees = relationship('EmployeeModel', back_populates='team', lazy='joined')
    schedules = relationship('ScheduleModel', back_populates='team', lazy='joined')
