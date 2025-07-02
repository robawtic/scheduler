from abc import abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from ..entities.employee import Employee
from .base import BaseRepository

class EmployeeRepository(BaseRepository[Employee]):
    """Repository interface for Employee entity."""

    @abstractmethod
    def get_by_employee_id(self, employee_id: str) -> Optional[Employee]:
        """Retrieve an employee by their employee ID."""
        pass

    @abstractmethod
    def get_by_team(self, team_id: int) -> List[Employee]:
        """Retrieve all employees in a team."""
        pass

    @abstractmethod
    def get_available_employees(self, date: datetime) -> List[Employee]:
        """Retrieve all employees available on a specific date."""
        pass

    @abstractmethod
    def get_by_qualification(self, qualification_name: str, minimum_level: int = 1) -> List[Employee]:
        """Retrieve all employees with a specific qualification at or above the minimum level."""
        pass

    @abstractmethod
    def get_by_workstation_skill(self, workstation_id: int, minimum_skill_level: int = 1) -> List[Employee]:
        """Retrieve all employees qualified for a specific workstation."""
        pass 