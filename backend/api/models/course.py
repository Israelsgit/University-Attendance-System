"""
Course/Class Model for University System
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, Time
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base

class Course(Base):
    """Course/Class model for university classes"""
    
    __tablename__ = "courses"
    
    # Primary Fields
    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(20), nullable=False, unique=True, index=True)  # e.g., "CSC 438"
    course_title = Column(String(200), nullable=False)
    course_unit = Column(Integer, nullable=False, default=3)
    
    # Academic Information
    semester = Column(String(20), nullable=False, index=True)  # e.g., "First Semester", "Second Semester"
    academic_session = Column(String(20), nullable=False, index=True)  # e.g., "2024/2025"
    level = Column(String(10), nullable=False, index=True)  # e.g., "100", "200", "300", "400", "500"
    
    # Class Schedule
    class_days = Column(String(100), nullable=True)  # e.g., "Monday,Wednesday,Friday"
    class_time_start = Column(Time, nullable=True)
    class_time_end = Column(Time, nullable=True)
    classroom = Column(String(100), nullable=True)  # e.g., "LT1", "Lab A"
    
    # Lecturer Information
    lecturer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Additional Information
    description = Column(Text, nullable=True)
    prerequisites = Column(Text, nullable=True)
    max_students = Column(Integer, nullable=True, default=100)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    lecturer = relationship("User", back_populates="taught_classes", foreign_keys=[lecturer_id])
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    attendance_records = relationship("AttendanceRecord", back_populates="course", cascade="all, delete-orphan")
    class_sessions = relationship("ClassSession", back_populates="course", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Course(code='{self.course_code}', title='{self.course_title}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "course_code": self.course_code,
            "course_title": self.course_title,
            "course_unit": self.course_unit,
            "semester": self.semester,
            "academic_session": self.academic_session,
            "level": self.level,
            "class_days": self.class_days.split(",") if self.class_days else [],
            "class_time_start": self.class_time_start.strftime("%H:%M") if self.class_time_start else None,
            "class_time_end": self.class_time_end.strftime("%H:%M") if self.class_time_end else None,
            "classroom": self.classroom,
            "lecturer_id": self.lecturer_id,
            "lecturer_name": self.lecturer.full_name if self.lecturer else None,
            "description": self.description,
            "prerequisites": self.prerequisites,
            "max_students": self.max_students,
            "enrolled_count": len(self.enrollments) if self.enrollments else 0,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }