# backend/api/schemas/__init__.py (Complete)
"""
Schemas Package
Contains Pydantic schema definitions for API validation
"""

from .user import (
    UserCreate, 
    UserUpdate, 
    UserResponse, 
    UserLogin,
    LecturerCreate,
    StudentCreate,
    UserList,
    UserProfile,
    PasswordChange,
    FaceRegistration,
    UserStats
)
from .course import (
    CourseCreate,
    CourseUpdate, 
    CourseResponse,
    EnrollmentCreate,
    ClassSessionCreate
)
from .attendance import (
    AttendanceResponse,
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceMarkingResponse,
    StudentAttendanceStats,
    CourseAttendanceStats
)
from .auth import (
    Token,
    LecturerRegistration,
    StudentRegistration
)
from .common import (
    SuccessResponse,
    ErrorResponse,
    PaginationParams,
    PaginatedResponse
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserUpdate", 
    "UserResponse",
    "UserLogin",
    "LecturerCreate",
    "StudentCreate",
    "UserList",
    "UserProfile",
    "PasswordChange",
    "FaceRegistration",
    "UserStats",
    
    # Course schemas
    "CourseCreate",
    "CourseUpdate",
    "CourseResponse", 
    "EnrollmentCreate",
    "ClassSessionCreate",
    
    # Attendance schemas
    "AttendanceResponse",
    "AttendanceCreate",
    "AttendanceUpdate",
    "AttendanceMarkingResponse",
    "StudentAttendanceStats",
    "CourseAttendanceStats",
    
    # Auth schemas
    "Token",
    "LecturerRegistration", 
    "StudentRegistration",
    
    # Common schemas
    "SuccessResponse",
    "ErrorResponse",
    "PaginationParams",
    "PaginatedResponse"
]