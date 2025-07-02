from fastapi import APIRouter
from presentation.api.routers import auth, schedules, users

router = APIRouter()

router.include_router(auth.router, tags=["authentication"])
router.include_router(schedules.router, tags=["schedules"])
router.include_router(users.router, tags=["users"])
