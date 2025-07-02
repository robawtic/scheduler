# Import dependencies from infrastructure/api/dependencies.py
from infrastructure.api.dependencies import (
    get_db,
    get_employee_repository,
    get_workstation_repository,
    get_schedule_repository,
    get_schedule_service,
    get_repositories,
    get_refresh_token_repository,
    get_user_repository,
    get_user_service
)

# Re-export dependencies for backward compatibility
__all__ = [
    'get_db',
    'get_employee_repository',
    'get_workstation_repository',
    'get_schedule_repository',
    'get_schedule_service',
    'get_repositories',
    'get_refresh_token_repository',
    'get_user_repository',
    'get_user_service'
]
