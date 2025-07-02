from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security
from pydantic import BaseModel

from domain.entities.schedule import Schedule, ShiftStatus
from domain.services.schedule_service import ScheduleService
from presentation.api.dependencies import get_schedule_service
from infrastructure.api.auth import get_viewer_user, get_scheduler_user
from infrastructure.api.dependencies_csrf import csrf_protection

router = APIRouter(prefix="/schedules", tags=["schedules"])

class EmployeeAssignment(BaseModel):
    """API model for shift assignments."""
    period: int
    station_id: UUID
    employee_id: UUID
    status: str

class ScheduleRequest(BaseModel):
    """API model for schedule generation requests."""
    team_id: int
    start_date: datetime
    periods_per_day: int = 4

class ScheduleResponse(BaseModel):
    """API model for schedule responses."""
    id: UUID
    team_id: int
    start_date: datetime
    periods_per_day: int
    assignments: List[EmployeeAssignment]
    is_published: bool
    version: int
    created_at: datetime
    updated_at: datetime

def map_schedule_to_response(schedule: Schedule) -> ScheduleResponse:
    """Map domain Schedule entity to API response model."""
    assignments = [
        EmployeeAssignment(
            period=assignment.period,
            station_id=assignment.workstation_id,
            employee_id=assignment.employee_id,
            status=assignment.status.value
        )
        for assignment in schedule.assignments
    ]

    return ScheduleResponse(
        id=schedule.id,
        team_id=schedule.team_id,
        start_date=schedule.start_date,
        periods_per_day=schedule.periods_per_day,
        assignments=assignments,
        is_published=schedule.is_published,
        version=schedule.version,
        created_at=schedule.created_at,
        updated_at=schedule.updated_at
    )

@router.get("/", response_model=List[ScheduleResponse])
@router.get("", response_model=List[ScheduleResponse])  # Also handle path without trailing slash
async def list_schedules(
    current_user: dict = Security(get_viewer_user),
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> List[ScheduleResponse]:
    """List all schedules."""
    # Get schedules for the last 7 days by default
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    schedules = schedule_service.schedule_repository.get_by_date_range(start_date, end_date)
    return [map_schedule_to_response(schedule) for schedule in schedules]

@router.post("/", response_model=ScheduleResponse, dependencies=[csrf_protection])
@router.post("", response_model=ScheduleResponse, dependencies=[csrf_protection])  # Also handle path without trailing slash
async def create_schedule(
    request: ScheduleRequest,
    current_user: dict = Security(get_scheduler_user),
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> ScheduleResponse:
    """Generate a new schedule."""
    try:
        schedule = schedule_service.generate_schedule(
            team_id=request.team_id,
            schedule_date=request.start_date,
            periods_per_day=request.periods_per_day,
        )
        return map_schedule_to_response(schedule)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: UUID,
    current_user: dict = Security(get_viewer_user),
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> ScheduleResponse:
    """Get a schedule by ID."""
    schedule = schedule_service.schedule_repository.get_by_id(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return map_schedule_to_response(schedule)

@router.post("/{schedule_id}/publish", dependencies=[csrf_protection])
async def publish_schedule(
    schedule_id: UUID,
    current_user: dict = Security(get_scheduler_user),
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> Dict[str, str]:
    """Publish a schedule."""
    try:
        schedule_service.publish_schedule(schedule_id)
        return {"status": "Schedule published successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{schedule_id}/assignments/{assignment_id}/status", dependencies=[csrf_protection])
async def update_assignment_status(
    schedule_id: UUID,
    assignment_id: UUID,
    status: ShiftStatus,
    current_user: dict = Security(get_scheduler_user),
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> Dict[str, str]:
    """Update the status of a shift assignment."""
    try:
        schedule_service.update_assignment_status(schedule_id, assignment_id, status)
        return {"status": "Assignment status updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 
