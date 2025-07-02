from abc import abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.workstation import Workstation
from .base import BaseRepository

class WorkstationRepository(BaseRepository[Workstation]):
    """Repository interface for Workstation entity."""

    @abstractmethod
    def get_by_station_id(self, station_id: str) -> Optional[Workstation]:
        """Retrieve a workstation by its station ID."""
        pass

    @abstractmethod
    def get_by_team(self, team_id: int) -> List[Workstation]:
        """Retrieve all workstations in a team."""
        pass

    @abstractmethod
    def get_by_line_type(self, line_type_id: int) -> List[Workstation]:
        """Retrieve all workstations of a specific line type."""
        pass

    @abstractmethod
    def get_by_required_qualification(self, qualification_name: str) -> List[Workstation]:
        """Retrieve all workstations requiring a specific qualification."""
        pass

    @abstractmethod
    def get_by_location(self, location: str) -> List[Workstation]:
        """Retrieve all workstations in a specific location."""
        pass 