from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from domain.entities.workstation import Workstation
from domain.repositories.workstation_repository import WorkstationRepository
from infrastructure.models.workstation import WorkstationModel

class SQLAlchemyWorkstationRepository(WorkstationRepository):
    """SQLAlchemy implementation of the workstation repository."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, workstation_id: UUID) -> Optional[Workstation]:
        """Get a workstation by ID."""
        model = self.session.query(WorkstationModel).filter_by(id=workstation_id).first()
        return self._to_domain_entity(model) if model else None

    def get_by_team(self, team_id: int) -> List[Workstation]:
        """Get all workstations in a team."""
        models = self.session.query(WorkstationModel).filter_by(team_id=team_id).all()
        return [self._to_domain_entity(model) for model in models]

    def save(self, workstation: Workstation) -> None:
        """Save or update a workstation."""
        model = self.session.query(WorkstationModel).filter_by(id=workstation.id).first()
        if not model:
            model = WorkstationModel()
        
        # Update model attributes
        for key, value in {
            'id': workstation.id,
            'station_id': workstation.station_id,
            'name': workstation.name,
            'team_id': workstation.team_id,
            'line_type_id': workstation.line_type_id,
            'is_active': workstation.is_active,
            'capacity': workstation.capacity,
            'equipment_type': workstation.equipment_type,
            'location': workstation.location,
            'maintenance_schedule': workstation.maintenance_schedule,
        }.items():
            setattr(model, key, value)
        
        self.session.add(model)
        self.session.commit()

    def get_all(self) -> List[Workstation]:
        """Get all workstations."""
        models = self.session.query(WorkstationModel).all()
        return [self._to_domain_entity(model) for model in models]

    def delete(self, workstation_id: UUID) -> None:
        """Delete a workstation."""
        self.session.query(WorkstationModel).filter_by(id=workstation_id).delete()
        self.session.commit()

    def _to_domain_entity(self, model: WorkstationModel) -> Workstation:
        """Convert ORM model to domain entity."""
        workstation = Workstation(
            station_id=getattr(model, 'station_id'),
            name=getattr(model, 'name'),
            team_id=getattr(model, 'team_id'),
            line_type_id=getattr(model, 'line_type_id'),
            is_active=getattr(model, 'is_active'),
            capacity=getattr(model, 'capacity'),
            equipment_type=getattr(model, 'equipment_type'),
            location=getattr(model, 'location'),
            maintenance_schedule=getattr(model, 'maintenance_schedule'),
        )
        workstation.id = getattr(model, 'id')
        return workstation 