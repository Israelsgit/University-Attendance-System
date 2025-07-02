"""
API Routes Package
Contains all FastAPI route definitions
"""

from .auth import router as auth_router
from .attendance import router as attendance_router
from .users import router as users_router
from .analytics import router as analytics_router

__all__ = [
    "auth_router",
    "attendance_router", 
    "users_router",
    "analytics_router"
]