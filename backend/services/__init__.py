"""
Services Package
Contains business logic services for the university system
"""

from .face_recognition import face_recognition_service
from .attendance_service import attendance_service
from .analytics_service import analytics_service

# Import email service only if configured
try:
    from .email import email_service
except ImportError:
    email_service = None

__all__ = [
    "face_recognition_service",
    "attendance_service", 
    "analytics_service",
    "email_service"
]
