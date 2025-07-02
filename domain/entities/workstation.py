from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from uuid import UUID

from .base import Entity

@dataclass(frozen=True)
class RequiredQualification:
    """Value object representing a required qualification for a workstation."""
    name: str
    minimum_level: int

@dataclass
class Workstation(Entity):
    """Workstation domain entity."""
    station_id: str
    name: str
    team_id: int
    line_type_id: Optional[int]
    is_active: bool = True
    required_qualifications: Set[RequiredQualification] = field(default_factory=set)
    capacity: int = 1
    equipment_type: Optional[str] = None
    location: Optional[str] = None
    maintenance_schedule: Dict[str, int] = field(default_factory=dict)  # day_of_week -> duration_minutes

    def __post_init__(self):
        super().__init__()

    def add_required_qualification(self, name: str, minimum_level: int = 1) -> None:
        """Add a required qualification for operating this workstation."""
        self.required_qualifications.add(RequiredQualification(name, minimum_level))
        self.update()

    def remove_required_qualification(self, qualification_name: str) -> None:
        """Remove a required qualification."""
        self.required_qualifications = {
            q for q in self.required_qualifications if q.name != qualification_name
        }
        self.update()

    def can_be_operated_by(self, employee_qualifications: Set[str]) -> bool:
        """Check if an employee with given qualifications can operate this workstation."""
        return all(
            any(eq == rq.name for eq in employee_qualifications)
            for rq in self.required_qualifications
        )

    def set_maintenance_schedule(self, day_of_week: str, duration_minutes: int) -> None:
        """Set maintenance duration for a specific day of the week."""
        day = day_of_week.lower()
        if day not in {'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'}:
            raise ValueError("Invalid day of week")
        self.maintenance_schedule[day] = duration_minutes
        self.update()

    def get_maintenance_duration(self, day_of_week: str) -> int:
        """Get maintenance duration for a specific day of week."""
        return self.maintenance_schedule.get(day_of_week.lower(), 0)

    def deactivate(self) -> None:
        """Deactivate the workstation."""
        self.is_active = False
        self.update() 