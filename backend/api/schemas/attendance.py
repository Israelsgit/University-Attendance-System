"""
Attendance Pydantic Schemas for Request/Response Validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, time, datetime
from enum import Enum

class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EARLY_DEPARTURE = "early_departure"
    OVERTIME = "overtime"
    HALF_DAY = "half_day"
    SICK = "sick"
    LEAVE = "leave"

class CheckInMethod(str, Enum):
    FACE_RECOGNITION = "face_recognition"
    MANUAL = "manual"
    BIOMETRIC = "biometric"
    CARD = "card"

class AttendanceBase(BaseModel):
    """Base attendance schema"""
    date: date
    status: AttendanceStatus = AttendanceStatus.PRESENT
    location: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)

class AttendanceCreate(AttendanceBase):
    """Schema for creating attendance record"""
    user_id: int
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    check_in_method: Optional[CheckInMethod] = CheckInMethod.MANUAL
    check_out_method: Optional[CheckInMethod] = CheckInMethod.MANUAL

class AttendanceUpdate(BaseModel):
    """Schema for updating attendance record"""
    status: Optional[AttendanceStatus] = None
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    total_hours: Optional[float] = Field(None, ge=0, le=24)
    location: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    admin_notes: Optional[str] = Field(None, max_length=500)
    
    @validator('total_hours')
    def validate_hours(cls, v):
        if v is not None and v > 24:
            raise ValueError('Total hours cannot exceed 24')
        return v

class AttendanceResponse(BaseModel):
    """Schema for attendance response"""
    id: int
    user_id: int
    user_name: Optional[str]
    employee_id: Optional[str]
    date: date
    check_in_time: Optional[time]
    check_out_time: Optional[time]
    total_hours: Optional[float]
    status: AttendanceStatus
    check_in_method: Optional[CheckInMethod]
    check_out_method: Optional[CheckInMethod]
    location: Optional[str]
    face_confidence: Optional[float]
    notes: Optional[str]
    admin_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AttendanceHistory(BaseModel):
    """Schema for attendance history"""
    id: int
    date: date
    check_in_time: Optional[time]
    check_out_time: Optional[time]
    total_hours: Optional[float]
    status: AttendanceStatus
    location: Optional[str]
    notes: Optional[str]
    
    class Config:
        from_attributes = True

class AttendanceStats(BaseModel):
    """Schema for attendance statistics"""
    present_days: int
    total_days: int
    avg_hours: float
    total_hours: float
    attendance_rate: float
    week_start: str
    week_end: str

class MonthlyStats(BaseModel):
    """Schema for monthly attendance statistics"""
    total_days: int
    present_days: int
    absent_days: int
    late_days: int
    overtime_days: int
    total_hours: float
    avg_hours: float
    overtime_hours: float
    attendance_rate: float
    month: str

class CheckInOut(BaseModel):
    """Schema for check-in/check-out response"""
    success: bool
    message: str
    timestamp: str
    status: AttendanceStatus
    confidence: Optional[float] = None
    total_hours: Optional[float] = None
    location: Optional[str] = None

class AttendanceFilter(BaseModel):
    """Schema for attendance filtering"""
    user_id: Optional[int] = None
    department: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[AttendanceStatus] = None
    location: Optional[str] = None
    limit: int = Field(default=50, le=100)
    offset: int = Field(default=0, ge=0)

class AttendanceReport(BaseModel):
    """Schema for attendance report generation"""
    start_date: date
    end_date: date
    user_ids: Optional[List[int]] = None
    departments: Optional[List[str]] = None
    format: str = Field(default="pdf", pattern="^(pdf|excel|csv)$")
    include_summary: bool = True

class BulkAttendanceUpdate(BaseModel):
    """Schema for bulk attendance updates"""
    attendance_updates: List[dict]
    reason: str = Field(..., max_length=200)

class AttendanceCorrection(BaseModel):
    """Schema for attendance correction requests"""
    attendance_id: int
    corrected_check_in: Optional[time] = None
    corrected_check_out: Optional[time] = None
    reason: str = Field(..., max_length=500)
    supporting_documents: Optional[List[str]] = None

class DepartmentAttendance(BaseModel):
    """Schema for department-wise attendance"""
    department: str
    total_employees: int
    present_today: int
    absent_today: int
    late_today: int
    attendance_rate: float

class LiveAttendance(BaseModel):
    """Schema for live attendance dashboard"""
    total_employees: int
    checked_in: int
    not_checked_in: int
    late_arrivals: int
    early_departures: int
    current_time: str
    departments: List[DepartmentAttendance]

class AttendanceAnalytics(BaseModel):
    """Schema for attendance analytics"""
    period: str  # weekly, monthly, yearly
    attendance_trend: List[dict]
    department_comparison: List[dict]
    punctuality_stats: dict
    overtime_analysis: dict
    leave_patterns: dict

class AttendanceExport(BaseModel):
    """Schema for attendance data export"""
    format: str = Field(default="excel", pattern="^(excel|csv|pdf)$")
    start_date: date
    end_date: date
    include_summary: bool = True
    group_by: str = Field(default="user", pattern="^(user|department|date)$")

class AttendanceNotification(BaseModel):
    """Schema for attendance notifications"""
    type: str  # reminder, warning, summary
    title: str
    message: str
    recipients: List[int]  # user IDs
    send_email: bool = True
    send_sms: bool = False

class AttendanceValidation(BaseModel):
    """Schema for attendance validation"""
    attendance_id: int
    is_valid: bool
    validation_notes: Optional[str] = None
    validated_by: int
    validation_date: datetime

class QuickCheckIn(BaseModel):
    """Schema for quick check-in without face recognition"""
    employee_id: str
    location: Optional[str] = "Main Office"
    notes: Optional[str] = None

class AttendanceOverride(BaseModel):
    """Schema for attendance override by admin"""
    attendance_id: int
    new_status: AttendanceStatus
    new_check_in: Optional[time] = None
    new_check_out: Optional[time] = None
    override_reason: str = Field(..., max_length=500)
    approved_by: int