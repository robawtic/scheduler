from sqlalchemy import Column, Integer, String, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from domain.models.Base import Base


class RoleModel(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Add a unique constraint on the name column
    __table_args__ = (UniqueConstraint('name', name='_role_name_uc'),)

    # Back-reference to TeamMember
    team_members = relationship('TeamMemberModel', back_populates='role')
