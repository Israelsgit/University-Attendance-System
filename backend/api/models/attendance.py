"""
Attendance Database Model
"""

from sqlalchemy import Column, Integer, String, Date, Time, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime, time

class AttendanceRecord(Base):
    """Attendance record model"""
    
    __tablename__ = "attendance_records"
    
    # Primary Fields
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    
    # Time Fields
    check_in_time = Column(Time, nullable=True)
    check_out_time = Column(Time, nullable=True)
    total_hours = Column(Float, nullable=True)
    
    # Status and Methods
    status = Column(String(50), nullable=False, default="absent", index=True)
    # Status options: present, absent, late, early_departure, overtime, leave, holiday
    check_in_method = Column(String(50), nullable=True)  # face_recognition, manual, card
    check_out_method = Column(String(50), nullable=True)
    
    # Location and Device Info
    location = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    device_info = Column(Text, nullable=True)
    
    # Face Recognition Data
    face_confidence = Column(Float, nullable=True)
    face_image_path = Column(String(255), nullable=True)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    approved_by = Column(Integer, nullable=True)  # For manual entries
    approval_date = Column(DateTime, nullable=True)
    
    # Break and Overtime
    break_duration = Column(Float, nullable=True)  # in hours
    overtime_approved = Column(Boolean, default=False)
    overtime_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="attendance_records")
    
    def __repr__(self):
        return f"<AttendanceRecord(id={self.id}, user_id={self.user_id}, date={self.date}, status='{self.status}')>"
    
    def to_dict(self):
        """Convert attendance record to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date.isoformat() if self.date else None,
            "check_in_time": self.check_in_time.isoformat() if self.check_in_time else None,
            "check_out_time": self.check_out_time.isoformat() if self.check_out_time else None,
            "total_hours": self.total_hours,
            "status": self.status,
            "check_in_method": self.check_in_method,
            "check_out_method": self.check_out_method,
            "location": self.location,
            "face_confidence": self.face_confidence,
            "notes": self.notes,
            "break_duration": self.break_duration,
            "overtime_approved": self.overtime_approved,
            "overtime_reason": self.overtime_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_late(self, work_start_time: time) -> bool:
        """Check if check-in was late"""
        if not self.check_in_time:
            return False
        return self.check_in_time > work_start_time
    
    def is_early_departure(self, work_end_time: time) -> bool:
        """Check if check-out was early"""
        if not self.check_out_time:
            return False
        return self.check_out_time < work_end_time
    
    def is_overtime(self, standard_hours: float = 8.0) -> bool:
        """Check if worked overtime"""
        if not self.total_hours:
            return False
        return self.total_hours > standard_hours
    
    def get_working_duration_str(self) -> str:
        """Get working duration as human-readable string"""
        if not self.total_hours:
            return "0h 0m"
        
        hours = int(self.total_hours)
        minutes = int((self.total_hours - hours) * 60)
        return f"{hours}h {minutes}m"

class AttendanceCorrection(Base):
    """Attendance correction requests"""
    
    __tablename__ = "attendance_corrections"
    
    id = Column(Integer, primary_key=True, index=True)
    attendance_id = Column(Integer, ForeignKey("attendance_records.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Correction Details
    field_name = Column(String(50), nullable=False)  # check_in_time, check_out_time, etc.
    original_value = Column(String(255), nullable=True)
    requested_value = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)
    
    # Status and Approval
    status = Column(String(50), default="pending")  # pending, approved, rejected
    reviewed_by = Column(Integer, nullable=True)
    review_date = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<AttendanceCorrection(id={self.id}, attendance_id={self.attendance_id}, status='{self.status}')>"

class Holiday(Base):
    """Holiday calendar"""
    
    __tablename__ = "holidays"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    date = Column(Date, nullable=False, index=True)
    is_mandatory = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Holiday(id={self.id}, name='{self.name}', date={self.date})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "date": self.date.isoformat(),
            "is_mandatory": self.is_mandatory,
            "description": self.description
        }

class WorkSchedule(Base):
    """Work schedule configuration"""
    
    __tablename__ = "work_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for default schedule
    name = Column(String(100), nullable=False)
    
    # Schedule Details
    monday_start = Column(Time, nullable=True)
    monday_end = Column(Time, nullable=True)
    tuesday_start = Column(Time, nullable=True)
    tuesday_end = Column(Time, nullable=True)
    wednesday_start = Column(Time, nullable=True)
    wednesday_end = Column(Time, nullable=True)
    thursday_start = Column(Time, nullable=True)
    thursday_end = Column(Time, nullable=True)
    friday_start = Column(Time, nullable=True)
    friday_end = Column(Time, nullable=True)
    saturday_start = Column(Time, nullable=True)
    saturday_end = Column(Time, nullable=True)
    sunday_start = Column(Time, nullable=True)
    sunday_end = Column(Time, nullable=True)
    
    # Settings
    break_duration = Column(Float, default=1.0)  # in hours
    overtime_threshold = Column(Float, default=8.0)  # in hours
    late_threshold = Column(Integer, default=15)  # in minutes
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<WorkSchedule(id={self.id}, name='{self.name}', user_id={self.user_id})>"
    
    def get_work_hours_for_day(self, day_name: str):
        """Get work hours for a specific day"""
        day_map = {
            'monday': (self.monday_start, self.monday_end),
            'tuesday': (self.tuesday_start, self.tuesday_end),
            'wednesday': (self.wednesday_start, self.wednesday_end),
            'thursday': (self.thursday_start, self.thursday_end),
            'friday': (self.friday_start, self.friday_end),
            'saturday': (self.saturday_start, self.saturday_end),
            'sunday': (self.sunday_start, self.sunday_end)
        }
        
        return day_map.get(day_name.lower(), (None, None))
    
    def is_working_day(self, day_name: str) -> bool:
        """Check if it's a working day"""
        start_time, end_time = self.get_work_hours_for_day(day_name)
        return start_time is not None and end_time is not None
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "schedule": {
                "monday": {
                    "start": self.monday_start.isoformat() if self.monday_start else None,
                    "end": self.monday_end.isoformat() if self.monday_end else None
                },
                "tuesday": {
                    "start": self.tuesday_start.isoformat() if self.tuesday_start else None,
                    "end": self.tuesday_end.isoformat() if self.tuesday_end else None
                },
                "wednesday": {
                    "start": self.wednesday_start.isoformat() if self.wednesday_start else None,
                    "end": self.wednesday_end.isoformat() if self.wednesday_end else None
                },
                "thursday": {
                    "start": self.thursday_start.isoformat() if self.thursday_start else None,
                    "end": self.thursday_end.isoformat() if self.thursday_end else None
                },
                "friday": {
                    "start": self.friday_start.isoformat() if self.friday_start else None,
                    "end": self.friday_end.isoformat() if self.friday_end else None
                },
                "saturday": {
                    "start": self.saturday_start.isoformat() if self.saturday_start else None,
                    "end": self.saturday_end.isoformat() if self.saturday_end else None
                },
                "sunday": {
                    "start": self.sunday_start.isoformat() if self.sunday_start else None,
                    "end": self.sunday_end.isoformat() if self.sunday_end else None
                }
            },
            "break_duration": self.break_duration,
            "overtime_threshold": self.overtime_threshold,
            "late_threshold": self.late_threshold,
            "is_active": self.is_active
        }