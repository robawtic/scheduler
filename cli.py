from datetime import datetime
from typing import List, Optional
from uuid import UUID

import typer
from rich import print as rprint

from domain.services.schedule_service import ScheduleService

app = typer.Typer()

@app.command()
def generate(
    team_id: int = typer.Argument(..., help="Team ID to generate schedule for"),
    start_date: datetime = typer.Option(None, help="Start date (YYYY-MM-DD)"),
    periods: int = typer.Option(4, help="Number of periods per day"),
    call_ins: Optional[List[str]] = typer.Option(None, help="List of employee IDs who called in"),
):
    """Generate a new schedule for a team."""
    try:
        # Convert string UUIDs to UUID objects
        call_in_uuids = [UUID(emp_id) for emp_id in (call_ins or [])]
        
        # Use current date if not specified
        schedule_date = start_date or datetime.now()

        # Initialize service (this would normally use dependency injection)
        service = ScheduleService(None, None, None)  # TODO: Add proper repository implementations
        
        schedule = service.generate_schedule(
            team_id=team_id,
            start_date=schedule_date,
            periods_per_day=periods,
            call_ins=call_in_uuids,
        )

        rprint("[green]Schedule generated successfully!")
        rprint(f"Schedule ID: {schedule.id}")
        rprint(f"Team ID: {schedule.team_id}")
        rprint(f"Start Date: {schedule.start_date}")
        rprint(f"Periods: {schedule.periods_per_day}")
        rprint("\nAssignments:")
        
        for period in range(1, schedule.periods_per_day + 1):
            rprint(f"\nPeriod {period}:")
            assignments = schedule.get_period_assignments(period)
            for assignment in assignments:
                rprint(f"  - Station {assignment.workstation_id}: Employee {assignment.employee_id}")

    except Exception as e:
        rprint(f"[red]Error: {str(e)}")

@app.command()
def publish(
    schedule_id: str = typer.Argument(..., help="Schedule ID to publish"),
):
    """Publish a schedule."""
    try:
        service = ScheduleService(None, None, None)  # TODO: Add proper repository implementations
        service.publish_schedule(UUID(schedule_id))
        rprint("[green]Schedule published successfully!")
    except Exception as e:
        rprint(f"[red]Error: {str(e)}")

@app.command()
def call_in(
    schedule_id: str = typer.Argument(..., help="Schedule ID"),
    employee_id: str = typer.Argument(..., help="Employee ID who called in"),
):
    """Handle an employee calling in."""
    try:
        service = ScheduleService(None, None, None)  # TODO: Add proper repository implementations
        service.handle_call_in(UUID(schedule_id), UUID(employee_id))
        rprint("[green]Call-in processed successfully!")
    except Exception as e:
        rprint(f"[red]Error: {str(e)}")

if __name__ == "__main__":
    app() 