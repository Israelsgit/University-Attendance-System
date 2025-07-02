"""
Services Package
Contains business logic and service layer implementations
"""

from .face_recognition import face_recognition_service, FaceRecognitionService
from .attendance_service import attendance_service, AttendanceService  
from .notification_service import notification_service, NotificationService
from .analytics_service import analytics_service, AnalyticsService

__all__ = [
    "face_recognition_service",
    "FaceRecognitionService",
    "attendance_service", 
    "AttendanceService",
    "notification_service",
    "NotificationService",
    "analytics_service",
    "AnalyticsService"
]