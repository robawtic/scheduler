from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, List, Optional, Set
from uuid import UUID

from .base import Entity

@dataclass(frozen=True)  # Make immutable to be hashable
class Qualification:
    """Value object representing an employee qualification."""
    name: str
    level: int
    acquired_date: datetime
    expires_at: Optional[datetime] = None

@dataclass
class Employee(Entity):
    """Employee domain entity."""
    employee_id: str
    first_name: str
    last_name: str
    team_id: int
    is_active: bool = True
    qualifications: Set[Qualification] = field(default_factory=set)
    workstation_skills: Dict[int, int] = field(default_factory=dict)  # workstation_id -> skill_level
    availability_cache: Dict[date, bool] = field(default_factory=dict)  # Using date instead of datetime
    max_hours_per_day: float = 8.0
    preferred_shifts: List[int] = field(default_factory=list)

    def __post_init__(self):
        super().__init__()

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def add_qualification(self, qualification: Qualification) -> None:
        """Add a qualification to the employee."""
        self.qualifications.add(qualification)
        self.update()

    def remove_qualification(self, qualification_name: str) -> None:
        """Remove a qualification from the employee."""
        self.qualifications = {
            q for q in self.qualifications if q.name != qualification_name
        }
        self.update()

    def has_qualification(self, qualification_name: str, minimum_level: int = 1) -> bool:
        """Check if employee has a qualification at or above the specified level."""
        return any(
            q.name == qualification_name and q.level >= minimum_level
            for q in self.qualifications
            if not q.expires_at or q.expires_at > datetime.now()
        )

    def set_workstation_skill(self, workstation_id: int, skill_level: int) -> None:
        """Set the employee's skill level for a workstation."""
        self.workstation_skills[workstation_id] = skill_level
        self.update()

    def get_workstation_skill(self, workstation_id: int) -> int:
        """Get the employee's skill level for a workstation."""
        return self.workstation_skills.get(workstation_id, 0)

    def update_availability(self, target_date: datetime, is_available: bool) -> None:
        """Update the employee's availability for a specific date."""
        self.availability_cache[target_date.date()] = is_available
        self.update()

    def is_available(self, target_date: datetime) -> bool:
        """Check if the employee is available on a specific date."""
        return self.availability_cache.get(target_date.date(), True) and self.is_active

    def deactivate(self) -> None:
        """Deactivate the employee."""
        self.is_active = False
        self.update() 