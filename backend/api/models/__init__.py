# backend/api/models/__init__.py (Complete)
"""
Database Models Package
Contains SQLAlchemy model definitions for University Attendance System
"""

from .user import User, UserRole, StudentLevel
from .course import Course
from .enrollment import Enrollment
from .class_session import ClassSession
from .attendance import AttendanceRecord

# Import order matters for foreign key relationships
__all__ = [
    "User",
    "UserRole", 
    "StudentLevel",
    "Course",
    "Enrollment",
    "ClassSession",
    "AttendanceRecord"
]

