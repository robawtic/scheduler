from abc import abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from ..entities.schedule import Schedule, ShiftStatus
from .base import BaseRepository

class ScheduleRepository(BaseRepository[Schedule]):
    """Repository interface for Schedule entity."""

    @abstractmethod
    def get_by_team_and_date(self, team_id: int, date: datetime) -> Optional[Schedule]:
        """Retrieve a schedule for a specific team and date."""
        pass

    @abstractmethod
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Schedule]:
        """Retrieve all schedules within a date range."""
        pass

    @abstractmethod
    def get_by_employee(self, employee_id: UUID, start_date: datetime, end_date: datetime) -> List[Schedule]:
        """Retrieve all schedules containing assignments for a specific employee in the date range."""
        pass

    @abstractmethod
    def get_by_workstation(self, workstation_id: UUID, start_date: datetime, end_date: datetime) -> List[Schedule]:
        """Retrieve all schedules containing assignments for a specific workstation in the date range."""
        pass

    @abstractmethod
    def get_published_schedules(self, start_date: datetime, end_date: datetime) -> List[Schedule]:
        """Retrieve all published schedules in the date range."""
        pass

    @abstractmethod
    def get_by_version(self, schedule_id: UUID, version: int) -> Optional[Schedule]:
        """Retrieve a specific version of a schedule."""
        pass

    @abstractmethod
    def get_by_status(self, status: ShiftStatus, start_date: datetime, end_date: datetime) -> List[Schedule]:
        """Retrieve all schedules containing assignments with a specific status in the date range."""
        pass 