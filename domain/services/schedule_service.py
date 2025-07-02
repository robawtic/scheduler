from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from uuid import UUID, uuid4

# Import OR-Tools conditionally to handle import error gracefully
try:
    from ortools.sat.python import cp_model
    HAS_ORTOOLS = True
except ImportError:
    HAS_ORTOOLS = False

from domain.entities.employee import Employee
from domain.entities.schedule import Schedule, ShiftStatus
from domain.entities.workstation import Workstation
from domain.repositories.employee_repository import EmployeeRepository
from domain.repositories.schedule_repository import ScheduleRepository
from domain.repositories.workstation_repository import WorkstationRepository

class ScheduleService:
    """Service for managing schedules and assignments."""

    def __init__(
        self,
        employee_repository: EmployeeRepository,
        workstation_repository: WorkstationRepository,
        schedule_repository: ScheduleRepository,
    ):
        self.employee_repository = employee_repository
        self.workstation_repository = workstation_repository
        self.schedule_repository = schedule_repository

    def generate_schedule(
        self,
        team_id: int,
        schedule_date: datetime,
        periods_per_day: int = 4,
    ) -> Schedule:
        """
        Generate a daily shift schedule for a manufacturing team.
        
        Args:
            team_id: ID of the team to generate schedule for
            schedule_date: The date for this shift schedule
            periods_per_day: Number of periods in the shift (default 4)
            
        Returns:
            Schedule: Generated schedule with optimal assignments
            
        Raises:
            ImportError: If OR-Tools is not installed
            ValueError: If insufficient staff available or no feasible schedule found
        """
        if not HAS_ORTOOLS:
            raise ImportError("Please install ortools package: pip install ortools")

        # Create initial schedule
        schedule = Schedule(
            team_id=team_id,
            start_date=schedule_date,
            periods_per_day=periods_per_day
        )

        try:
            # Get team's employees and workstations
            employees = self.employee_repository.get_by_team(team_id)
            workstations = self.workstation_repository.get_by_team(team_id)
            
            if not employees or not workstations:
                raise ValueError(f"No employees or workstations found for team {team_id}")
                
            # Get available employees for the date
            available_employees = self.employee_repository.get_available_employees(schedule_date)
            available_employee_ids = {e.id for e in available_employees}
            
            # Filter out unavailable employees
            employees = [e for e in employees if e.id in available_employee_ids]
            
            if not employees:
                raise ValueError(f"No available employees found for date {schedule_date}")
                
            # Create the CP-SAT model
            model = cp_model.CpModel()
            
            # Create variables
            # shifts[e][w][p] = 1 if employee e is assigned to workstation w in period p
            shifts = {}
            for e in range(len(employees)):
                shifts[e] = {}
                for w in range(len(workstations)):
                    shifts[e][w] = {}
                    for p in range(periods_per_day):
                        shifts[e][w][p] = model.NewBoolVar(f'shift_e{e}w{w}p{p}')
            
            # Constraints
            
            # 1. Each employee can only be assigned to one workstation per period
            for e in range(len(employees)):
                for p in range(periods_per_day):
                    model.Add(sum(shifts[e][w][p] for w in range(len(workstations))) <= 1)
            
            # 2. Each workstation needs exactly one employee per period
            for w in range(len(workstations)):
                for p in range(periods_per_day):
                    model.Add(sum(shifts[e][w][p] for e in range(len(employees))) == 1)
            
            # 3. Employee workstation training constraints
            for e in range(len(employees)):
                for w in range(len(workstations)):
                    # Get employee qualification names
                    employee_quals = {q.name for q in employees[e].qualifications}
                    if not workstations[w].can_be_operated_by(employee_quals):
                        for p in range(periods_per_day):
                            model.Add(shifts[e][w][p] == 0)
            
            # 4. Workstation continuity - employees stay at same workstation
            for e in range(len(employees)):
                for w in range(len(workstations)):
                    for p in range(periods_per_day - 1):
                        model.Add(shifts[e][w][p] == shifts[e][w][p + 1])
            
            # Create solver and solve
            solver = cp_model.CpSolver()
            status = solver.Solve(model)
            
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                # Add assignments to schedule
                for p in range(periods_per_day):
                    period = p + 1  # Convert to 1-based period numbers
                    
                    for e in range(len(employees)):
                        for w in range(len(workstations)):
                            if solver.Value(shifts[e][w][p]) == 1:
                                schedule.add_assignment(
                                    employee_id=employees[e].id,
                                    workstation_id=workstations[w].id,
                                    period=period
                                )
                
                self.schedule_repository.save(schedule)
                return schedule
            else:
                raise ValueError("No feasible schedule found. Check staff availability and training.")

        except Exception as e:
            raise ValueError(f"Failed to generate schedule: {str(e)}")

    def get_employee_schedule(
        self,
        employee_id: UUID,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Schedule]:
        """Get all schedules for an employee in a date range."""
        return self.schedule_repository.get_by_employee(employee_id, start_date, end_date)

    def get_workstation_schedule(
        self,
        workstation_id: UUID,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Schedule]:
        """Get all schedules for a workstation in a date range."""
        return self.schedule_repository.get_by_workstation(workstation_id, start_date, end_date)

    def publish_schedule(self, schedule_id: UUID) -> None:
        """Publish a schedule, making it visible to employees."""
        schedule = self.schedule_repository.get_by_id(schedule_id)
        if not schedule:
            raise ValueError(f"Schedule {schedule_id} not found")
        
        schedule.is_published = True
        self.schedule_repository.save(schedule)

    def update_assignment_status(
        self,
        schedule_id: UUID,
        assignment_id: UUID,
        status: ShiftStatus
    ) -> None:
        """Update the status of a shift assignment."""
        schedule = self.schedule_repository.get_by_id(schedule_id)
        if not schedule:
            raise ValueError(f"Schedule {schedule_id} not found")
        
        # Use the Schedule's update_assignment_status method
        schedule.update_assignment_status(assignment_id, status)
        self.schedule_repository.save(schedule) 