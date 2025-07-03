"""
Student Enrollment Model
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base

class Enrollment(Base):
    """Student enrollment in courses"""
    
    __tablename__ = "enrollments"
    
    # Primary Fields
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    
    # Enrollment Information
    enrollment_date = Column(DateTime, server_default=func.now())
    enrollment_status = Column(String(20), default="active")  # active, dropped, completed
    grade = Column(String(5), nullable=True)  # A, B, C, D, F
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    student = relationship("User", back_populates="enrolled_classes")
    course = relationship("Course", back_populates="enrollments")
    
    def __repr__(self):
        return f"<Enrollment(student_id={self.student_id}, course_id={self.course_id})>"