"""
Attendance Schemas for University System
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class AttendanceMarkingResponse(BaseModel):
    success: bool
    message: str
    student_name: str
    matric_number: str
    status: str
    confidence: float
    marked_at: str

class AttendanceResponse(BaseModel):
    attendance: Optional[dict] = None
    message: Optional[str] = None

class AttendanceCreate(BaseModel):
    matric_number: str
    course_id: int
    session_id: int
    status: str = "present"
    recognition_method: str = "face_recognition"
    notes: Optional[str] = None

class AttendanceUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class StudentAttendanceStats(BaseModel):
    student: dict
    attendance_records: List[dict]
    course_statistics: List[dict]

class CourseAttendanceStats(BaseModel):
    course: dict
    summary: dict
    student_statistics: List[dict]
    session_statistics: List[dict]

class AttendanceAnalytics(BaseModel):
    overall_stats: dict
    course_breakdown: List[dict]
    trend_data: List[dict]
    performance_metrics: dict
