from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from domain.entities.schedule import Schedule, ShiftStatus, ShiftAssignment
from domain.repositories.schedule_repository import ScheduleRepository
from infrastructure.models.schedule import ScheduleModel
from infrastructure.models.shift_assignment import ShiftAssignmentModel

class SQLAlchemyScheduleRepository(ScheduleRepository):
    """SQLAlchemy implementation of the schedule repository."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, schedule: Schedule) -> None:
        """Save or update a schedule."""
        # Convert domain entity to ORM model
        schedule_model = ScheduleModel()
        schedule_model.id = schedule.id
        schedule_model.team_id = schedule.team_id
        schedule_model.start_date = schedule.start_date
        schedule_model.periods_per_day = schedule.periods_per_day
        schedule_model.is_published = schedule.is_published
        schedule_model.version = schedule.version
        schedule_model.created_at = schedule.created_at
        schedule_model.updated_at = schedule.updated_at

        # Save or update assignments
        for assignment in schedule.assignments:
            assignment_model = ShiftAssignmentModel()
            assignment_model.id = assignment.id
            assignment_model.schedule_id = schedule.id
            assignment_model.employee_id = assignment.employee_id
            assignment_model.workstation_id = assignment.workstation_id
            assignment_model.period = assignment.period
            assignment_model.status = assignment.status.value
            assignment_model.notes = assignment.notes
            self.session.merge(assignment_model)

        self.session.merge(schedule_model)
        self.session.commit()

    def get_by_id(self, schedule_id: UUID) -> Optional[Schedule]:
        """Retrieve a schedule by its UUID."""
        model = self.session.query(ScheduleModel).get(schedule_id)
        if not model:
            return None
        return self._to_domain_entity(model)

    def get_by_team_and_date(self, team_id: int, date: datetime) -> Optional[Schedule]:
        """Retrieve a schedule for a specific team and date."""
        model = (
            self.session.query(ScheduleModel)
            .filter(ScheduleModel.team_id == team_id)
            .filter(ScheduleModel.start_date == date.date())
            .first()
        )
        if not model:
            return None
        return self._to_domain_entity(model)

    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Schedule]:
        """Retrieve all schedules within a date range."""
        models = (
            self.session.query(ScheduleModel)
            .filter(ScheduleModel.start_date >= start_date.date())
            .filter(ScheduleModel.start_date <= end_date.date())
            .all()
        )
        return [self._to_domain_entity(model) for model in models]

    def get_by_employee(
        self, employee_id: UUID, start_date: datetime, end_date: datetime
    ) -> List[Schedule]:
        """Retrieve all schedules containing assignments for a specific employee."""
        models = (
            self.session.query(ScheduleModel)
            .join(ShiftAssignmentModel)
            .filter(ShiftAssignmentModel.employee_id == employee_id)
            .filter(ScheduleModel.start_date >= start_date.date())
            .filter(ScheduleModel.start_date <= end_date.date())
            .all()
        )
        return [self._to_domain_entity(model) for model in models]

    def get_by_workstation(
        self, workstation_id: UUID, start_date: datetime, end_date: datetime
    ) -> List[Schedule]:
        """Retrieve all schedules containing assignments for a specific workstation."""
        models = (
            self.session.query(ScheduleModel)
            .join(ShiftAssignmentModel)
            .filter(ShiftAssignmentModel.workstation_id == workstation_id)
            .filter(ScheduleModel.start_date >= start_date.date())
            .filter(ScheduleModel.start_date <= end_date.date())
            .all()
        )
        return [self._to_domain_entity(model) for model in models]

    def get_published_schedules(self, start_date: datetime, end_date: datetime) -> List[Schedule]:
        """Retrieve all published schedules in the date range."""
        models = (
            self.session.query(ScheduleModel)
            .filter(ScheduleModel.start_date >= start_date.date())
            .filter(ScheduleModel.start_date <= end_date.date())
            .filter(ScheduleModel.is_published.is_(True))
            .all()
        )
        return [self._to_domain_entity(model) for model in models]

    def get_by_version(self, schedule_id: UUID, version: int) -> Optional[Schedule]:
        """Retrieve a specific version of a schedule."""
        model = (
            self.session.query(ScheduleModel)
            .filter(ScheduleModel.id == schedule_id)
            .filter(ScheduleModel.version == version)
            .first()
        )
        if not model:
            return None
        return self._to_domain_entity(model)

    def get_by_status(
        self, status: ShiftStatus, start_date: datetime, end_date: datetime
    ) -> List[Schedule]:
        """Retrieve all schedules containing assignments with a specific status."""
        models = (
            self.session.query(ScheduleModel)
            .join(ShiftAssignmentModel)
            .filter(ShiftAssignmentModel.status == status.value)
            .filter(ScheduleModel.start_date >= start_date.date())
            .filter(ScheduleModel.start_date <= end_date.date())
            .all()
        )
        return [self._to_domain_entity(model) for model in models]

    def _to_domain_entity(self, model: ScheduleModel) -> Schedule:
        """Convert ORM model to domain entity."""
        schedule = Schedule(
            team_id=model.team_id,
            start_date=model.start_date,
            periods_per_day=model.periods_per_day,
        )
        schedule.id = model.id
        schedule.is_published = model.is_published
        schedule.version = model.version
        schedule.created_at = model.created_at
        schedule.updated_at = model.updated_at

        # Add assignments
        for assignment_model in model.assignments:
            assignment = ShiftAssignment(
                id=assignment_model.id,
                employee_id=assignment_model.employee_id,
                workstation_id=assignment_model.workstation_id,
                period=assignment_model.period,
                status=ShiftStatus(assignment_model.status),
                notes=assignment_model.notes,
            )
            schedule.assignments.append(assignment)

        return schedule 