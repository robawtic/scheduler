from sqlalchemy import Column, Integer, Date, String, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .Base import Base

class ScheduleModel(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False, index=True)
    start_date = Column(Date, nullable=False, index=True)
    periods_per_day = Column(Integer, nullable=False, default=4)
    is_published = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Add composite index for common query patterns
    __table_args__ = (
        Index('idx_team_date', 'team_id', 'start_date'),
    )

    # Relationships
    team = relationship('TeamModel', back_populates='schedules')
