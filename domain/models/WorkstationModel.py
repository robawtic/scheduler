from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from .Base import Base

class WorkstationModel(Base):
    __tablename__ = 'workstations'
    __table_args__ = (
        UniqueConstraint('station_id', 'team_id', name='uq_workstations_station_id_team_id'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True)
    station_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    line_type_id = Column(Integer, ForeignKey('line_types.id'), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    capacity = Column(Integer, nullable=False, default=1)
    equipment_type = Column(String, nullable=True)
    location = Column(String, nullable=True)

    # Relationships
    team = relationship('TeamModel', back_populates='workstations')
    line_type = relationship('LineTypeModel', back_populates='workstations')
