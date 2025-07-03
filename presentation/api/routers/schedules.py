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
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    days: Optional[int] = None,
    current_user: dict = Security(get_viewer_user),
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> List[ScheduleResponse]:
    """
    List all schedules.

    Query Parameters:
    - start_date: Optional start date in ISO format (YYYY-MM-DD)
    - end_date: Optional end date in ISO format (YYYY-MM-DD)
    - days: Optional number of days to include (default: 7)
    """
    from infrastructure.api.query_validation import validate_query_param

    # Set default end date to today
    current_end_date = datetime.now()

    # Validate and parse the end_date if provided
    if end_date:
        try:
            # Sanitize the end_date parameter
            sanitized_end_date = validate_query_param(
                end_date, 
                "end_date", 
                required=False, 
                pattern=r'^\d{4}-\d{2}-\d{2}$'
            )
            current_end_date = datetime.fromisoformat(sanitized_end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid end_date format. Use YYYY-MM-DD."
            )

    # Validate and parse the days parameter if provided
    days_value = 7  # Default
    if days:
        try:
            # Sanitize and convert to integer
            sanitized_days = validate_query_param(days, "days", required=False)
            days_value = int(sanitized_days)
            if days_value < 1 or days_value > 90:
                raise ValueError("Days must be between 1 and 90")
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )

    # Calculate the start date based on end_date and days if start_date not provided
    current_start_date = current_end_date - timedelta(days=days_value)

    # Validate and parse the start_date if provided
    if start_date:
        try:
            # Sanitize the start_date parameter
            sanitized_start_date = validate_query_param(
                start_date, 
                "start_date", 
                required=False, 
                pattern=r'^\d{4}-\d{2}-\d{2}$'
            )
            current_start_date = datetime.fromisoformat(sanitized_start_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid start_date format. Use YYYY-MM-DD."
            )

    # Get schedules for the specified date range
    schedules = schedule_service.schedule_repository.get_by_date_range(current_start_date, current_end_date)
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
        # Log the detailed error for debugging
        import logging
        logger = logging.getLogger("scheduler_api")
        logger.error(
            f"Error during schedule creation: {str(e)}",
            extra={
                "team_id": request.team_id,
                "start_date": request.start_date,
                "periods_per_day": request.periods_per_day,
                "error_type": type(e).__name__,
                "error_details": str(e)
            },
            exc_info=True
        )
        # Return a generic error message to the client
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create schedule. Please check your input and try again."
        )

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
        # This is likely a "not found" error, so we can keep it specific
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found or cannot be published")
    except Exception as e:
        # Log the detailed error for debugging
        import logging
        logger = logging.getLogger("scheduler_api")
        logger.error(
            f"Error during schedule publishing: {str(e)}",
            extra={
                "schedule_id": str(schedule_id),
                "user_id": current_user.get("id", "unknown"),
                "error_type": type(e).__name__,
                "error_details": str(e)
            },
            exc_info=True
        )
        # Return a generic error message to the client
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to publish schedule. Please try again later."
        )

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
        # This is likely a "not found" error, so we can keep it specific
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Schedule or assignment not found"
        )
    except Exception as e:
        # Log the detailed error for debugging
        import logging
        logger = logging.getLogger("scheduler_api")
        logger.error(
            f"Error updating assignment status: {str(e)}",
            extra={
                "schedule_id": str(schedule_id),
                "assignment_id": str(assignment_id),
                "status": status.value if hasattr(status, 'value') else str(status),
                "user_id": current_user.get("id", "unknown"),
                "error_type": type(e).__name__,
                "error_details": str(e)
            },
            exc_info=True
        )
        # Return a generic error message to the client
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update assignment status. Please try again later."
        )
