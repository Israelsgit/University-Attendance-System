"""
Course Schemas for University System
"""

from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime, time

class CourseCreate(BaseModel):
    course_code: str
    course_title: str
    course_unit: int = 3
    semester: str
    academic_session: str
    level: str
    class_days: Optional[List[str]] = []
    class_time_start: Optional[str] = None
    class_time_end: Optional[str] = None
    classroom: Optional[str] = None
    description: Optional[str] = None
    prerequisites: Optional[str] = None
    max_students: Optional[int] = 100
    
    @validator('course_code')
    def validate_course_code(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Course code must be at least 3 characters')
        return v.upper()
    
    @validator('course_unit')
    def validate_course_unit(cls, v):
        if v < 1 or v > 6:
            raise ValueError('Course unit must be between 1 and 6')
        return v
    
    @validator('level')
    def validate_level(cls, v):
        if v not in ["100", "200", "300", "400", "500"]:
            raise ValueError('Level must be one of: 100, 200, 300, 400, 500')
        return v
    
    @validator('class_days')
    def validate_class_days(cls, v):
        valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        if v:
            for day in v:
                if day not in valid_days:
                    raise ValueError(f'Invalid day: {day}')
        return v

class CourseUpdate(BaseModel):
    course_title: Optional[str] = None
    course_unit: Optional[int] = None
    class_days: Optional[List[str]] = None
    class_time_start: Optional[str] = None
    class_time_end: Optional[str] = None
    classroom: Optional[str] = None
    description: Optional[str] = None
    prerequisites: Optional[str] = None
    max_students: Optional[int] = None
    is_active: Optional[bool] = None

class CourseResponse(BaseModel):
    course: Optional[dict] = None
    message: str

class EnrollmentCreate(BaseModel):
    student_email: str
    course_id: int

class ClassSessionCreate(BaseModel):
    session_date: datetime
    session_topic: Optional[str] = None
    session_type: str = "lecture"
    duration_minutes: int = 60
    notes: Optional[str] = None
    
    @validator('session_type')
    def validate_session_type(cls, v):
        valid_types = ["lecture", "practical", "tutorial", "exam", "seminar"]
        if v not in valid_types:
            raise ValueError(f'Session type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('duration_minutes')
    def validate_duration(cls, v):
        if v < 30 or v > 240:  # 30 minutes to 4 hours
            raise ValueError('Duration must be between 30 and 240 minutes')
        return v
