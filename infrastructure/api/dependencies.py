from fastapi import Depends
from sqlalchemy.orm import Session

from domain.repositories.schedule_repository import ScheduleRepository
from infrastructure.repositories.user_repository import SQLAlchemyUserRepository as UserRepository
from infrastructure.repositories.refresh_token_repository import RefreshTokenRepository
from domain.services.schedule_service import ScheduleService
from domain.services.user_service import UserService
from domain.models.db import Session as DBSession

def get_db() -> Session:
    db = DBSession()
    try:
        yield db
    finally:
        db.close()

def get_schedule_repository(db: Session = Depends(get_db)) -> ScheduleRepository:
    return ScheduleRepository(db)

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_schedule_service() -> ScheduleService:
    return ScheduleService()

def get_refresh_token_repository(db: Session = Depends(get_db)) -> RefreshTokenRepository:
    return RefreshTokenRepository(db)

def get_user_service(user_repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repository)
