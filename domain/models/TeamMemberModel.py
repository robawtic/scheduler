from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .Base import Base


class TeamMemberModel(Base):
    __tablename__ = 'team_members'

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)

    # Relationships
    team = relationship('TeamModel', back_populates='members')
    employee = relationship('EmployeeModel', back_populates='team_memberships')
    role = relationship('RoleModel', back_populates='team_members')

    # Unique constraint to prevent duplicate team member entries
    __table_args__ = (
        UniqueConstraint('team_id', 'employee_id', name='_team_member_uc'),
    )