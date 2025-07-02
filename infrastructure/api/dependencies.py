# infrastructure/api/dependencies.py
from fastapi import Depends
from sqlalchemy.orm import Session

# Import repositories from the correct locations
from domain.repositories.employee_repository import EmployeeRepository
from domain.repositories.schedule_repository import ScheduleRepository
from domain.repositories.workstation_repository import WorkstationRepository
from domain.repositories.interfaces.refresh_token_repository import RefreshTokenRepositoryInterface
from domain.repositories.interfaces.user_repository import UserRepositoryInterface
from infrastructure.repositories.employee_repository import SQLAlchemyEmployeeRepository
from infrastructure.repositories.schedule_repository import SQLAlchemyScheduleRepository
from infrastructure.repositories.workstation_repository import SQLAlchemyWorkstationRepository
from infrastructure.repositories.refresh_token_repository import SQLAlchemyRefreshTokenRepository
from infrastructure.repositories.user_repository import SQLAlchemyUserRepository

# Import services
from domain.services.schedule_service import ScheduleService
from domain.services.user_service import UserService
from infrastructure.database import get_db

# These imports would be used in a more comprehensive implementation
# from infrastructure.repositories.api_key_repository import SQLAlchemyApiKeyRepository
# from infrastructure.repositories.role_repository import SQLAlchemyRoleRepository

def get_repositories(db: Session = Depends(get_db)):
    """Get all repositories with the given database session."""
    return {
        "employee_repository": SQLAlchemyEmployeeRepository(db),
        "workstation_repository": SQLAlchemyWorkstationRepository(db),
        "schedule_repository": SQLAlchemyScheduleRepository(db)
    }

def get_employee_repository(db: Session = Depends(get_db)) -> EmployeeRepository:
    """Get employee repository instance."""
    return SQLAlchemyEmployeeRepository(db)

def get_workstation_repository(db: Session = Depends(get_db)) -> WorkstationRepository:
    """Get workstation repository instance."""
    return SQLAlchemyWorkstationRepository(db)

def get_schedule_repository(db: Session = Depends(get_db)) -> ScheduleRepository:
    """Get schedule repository instance."""
    return SQLAlchemyScheduleRepository(db)

def get_schedule_service(
    employee_repository: EmployeeRepository = Depends(get_employee_repository),
    workstation_repository: WorkstationRepository = Depends(get_workstation_repository),
    schedule_repository: ScheduleRepository = Depends(get_schedule_repository),
) -> ScheduleService:
    """Get schedule service instance."""
    return ScheduleService(
        employee_repository=employee_repository,
        workstation_repository=workstation_repository,
        schedule_repository=schedule_repository,
    )

def get_refresh_token_repository(db: Session = Depends(get_db)) -> RefreshTokenRepositoryInterface:
    """Get the refresh token repository."""
    return SQLAlchemyRefreshTokenRepository(db)

def get_user_repository(db: Session = Depends(get_db)) -> UserRepositoryInterface:
    """Get the user repository."""
    return SQLAlchemyUserRepository(db)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Get the user service."""
    user_repository = get_user_repository(db)
    return UserService(user_repository)

# This function would be used in a more comprehensive implementation
# def get_api_key_repository(db: Session = Depends(get_db)):
#     """Get the API key repository."""
#     return SQLAlchemyApiKeyRepository(db)
