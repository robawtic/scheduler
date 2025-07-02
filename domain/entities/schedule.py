from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set
from uuid import UUID, uuid4

from .base import Entity

class ShiftStatus(Enum):
    """Status of a shift assignment."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass(frozen=True)
class ShiftAssignment:
    """Value object representing a shift assignment."""
    id: UUID
    employee_id: UUID
    workstation_id: UUID
    period: int
    status: ShiftStatus = ShiftStatus.SCHEDULED
    notes: str = ""

@dataclass
class Schedule(Entity):
    """Schedule domain entity."""
    team_id: int
    start_date: datetime
    periods_per_day: int
    assignments: List[ShiftAssignment] = field(default_factory=list)
    is_published: bool = False
    version: int = 1

    def __post_init__(self):
        super().__init__()

    def add_assignment(
        self,
        employee_id: UUID,
        workstation_id: UUID,
        period: int,
        notes: str = "",
    ) -> ShiftAssignment:
        """Add a new shift assignment to the schedule."""
        if period < 1 or period > self.periods_per_day:
            raise ValueError(f"Period must be between 1 and {self.periods_per_day}")

        assignment = ShiftAssignment(
            id=uuid4(),
            employee_id=employee_id,
            workstation_id=workstation_id,
            period=period,
            notes=notes
        )
        self.assignments.append(assignment)
        self.version += 1
        self.update()
        return assignment

    def remove_assignment(self, assignment_id: UUID) -> None:
        """Remove a shift assignment from the schedule."""
        self.assignments = [a for a in self.assignments if a.id != assignment_id]
        self.version += 1
        self.update()

    def get_employee_assignments(self, employee_id: UUID) -> List[ShiftAssignment]:
        """Get all assignments for a specific employee."""
        return [a for a in self.assignments if a.employee_id == employee_id]

    def get_workstation_assignments(self, workstation_id: UUID) -> List[ShiftAssignment]:
        """Get all assignments for a specific workstation."""
        return [a for a in self.assignments if a.workstation_id == workstation_id]

    def get_period_assignments(self, period: int) -> List[ShiftAssignment]:
        """Get all assignments for a specific period."""
        return [a for a in self.assignments if a.period == period]

    def update_assignment_status(self, assignment_id: UUID, status: ShiftStatus) -> None:
        """Update the status of an assignment."""
        # Since ShiftAssignment is immutable, we need to create a new list
        self.assignments = [
            ShiftAssignment(
                id=a.id,
                employee_id=a.employee_id,
                workstation_id=a.workstation_id,
                period=a.period,
                status=status if a.id == assignment_id else a.status,
                notes=a.notes
            )
            for a in self.assignments
        ]
        self.version += 1
        self.update()

    def publish(self) -> None:
        """Publish the schedule."""
        self.is_published = True
        self.version += 1
        self.update()

    def unpublish(self) -> None:
        """Unpublish the schedule."""
        self.is_published = False
        self.version += 1
        self.update() 