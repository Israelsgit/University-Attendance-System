"""
Enhanced Attendance Model for University System
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base

class AttendanceRecord(Base):
    """Enhanced attendance record for university system"""
    
    __tablename__ = "attendance_records"
    
    # Primary Fields
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("class_sessions.id"), nullable=False, index=True)
    
    # Attendance Information
    marked_at = Column(DateTime, server_default=func.now(), index=True)
    status = Column(String(20), nullable=False, default="present", index=True)
    # Status options: present, absent, late, excused
    
    # Face Recognition Data
    face_confidence = Column(Float, nullable=True)
    face_image_path = Column(String(255), nullable=True)
    recognition_method = Column(String(50), default="face_recognition")  # face_recognition, manual
    
    # Location and Device Info
    location = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    device_info = Column(Text, nullable=True)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    marked_by_lecturer = Column(Integer, ForeignKey("users.id"), nullable=True)  # For manual marking
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    student = relationship("User", back_populates="attendance_records", foreign_keys=[student_id])
    course = relationship("Course", back_populates="attendance_records")
    session = relationship("ClassSession", back_populates="attendance_records")
    lecturer = relationship("User", foreign_keys=[marked_by_lecturer])
    
    def __repr__(self):
        return f"<AttendanceRecord(student_id={self.student_id}, course_id={self.course_id}, status='{self.status}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "matric_number": self.student.matric_number if self.student else None,
            "course_id": self.course_id,
            "course_code": self.course.course_code if self.course else None,
            "course_title": self.course.course_title if self.course else None,
            "session_id": self.session_id,
            "session_date": self.session.session_date.isoformat() if self.session else None,
            "session_topic": self.session.session_topic if self.session else None,
            "marked_at": self.marked_at.isoformat() if self.marked_at else None,
            "status": self.status,
            "face_confidence": self.face_confidence,
            "recognition_method": self.recognition_method,
            "location": self.location,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }