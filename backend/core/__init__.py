"""
Core Package
Contains core application components and utilities
"""

from .exceptions import (
    AttendanceAIException,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    FaceRecognitionError,
    AttendanceError
)

__all__ = [
    "AttendanceAIException",
    "AuthenticationError", 
    "AuthorizationError",
    "ValidationError",
    "FaceRecognitionError",
    "AttendanceError"
]
