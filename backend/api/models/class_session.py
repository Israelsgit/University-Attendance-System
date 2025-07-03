"""
Class Session Model for tracking individual class meetings
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base

class ClassSession(Base):
    """Individual class session/meeting"""
    
    __tablename__ = "class_sessions"
    
    # Primary Fields
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    
    # Session Information
    session_date = Column(DateTime, nullable=False, index=True)
    session_topic = Column(String(200), nullable=True)
    session_type = Column(String(50), default="lecture")  # lecture, practical, tutorial, exam
    duration_minutes = Column(Integer, default=60)
    
    # Status
    is_active = Column(Boolean, default=True)  # Whether attendance is being taken
    is_completed = Column(Boolean, default=False)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    attendance_marked_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="class_sessions")
    attendance_records = relationship("AttendanceRecord", back_populates="session")
    marked_by = relationship("User", foreign_keys=[attendance_marked_by])
    
    def __repr__(self):
        return f"<ClassSession(id={self.id}, course='{self.course.course_code}', date='{self.session_date}')>"