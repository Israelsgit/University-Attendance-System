"""
Pydantic Schemas Package
Contains request/response validation schemas
"""

from .auth import (
    UserLogin, 
    UserRegister
)
from .user import (
    UserCreate,
    UserUpdate, 
    UserResponse,
    UserProfile,
    UserPasswordUpdate
)
from .attendance import (
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse,
    AttendanceHistory,
    CheckInOut
)
from .common import (
    BaseResponse,
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse
)

__all__ = [
    # Auth schemas
    "UserLogin",
    "UserRegister",
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse", 
    "UserProfile",
    "UserPasswordUpdate",
    # Attendance schemas
    "AttendanceCreate",
    "AttendanceUpdate",
    "AttendanceResponse",
    "AttendanceHistory", 
    "CheckInOut",
    # Common schemas
    "BaseResponse",
    "SuccessResponse",
    "ErrorResponse",
    "PaginatedResponse"
]