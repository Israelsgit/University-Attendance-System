"""
Common Pydantic Schemas used across the application
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from enum import Enum

class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class BaseResponse(BaseModel):
    """Base response schema"""
    success: bool
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class SuccessResponse(BaseResponse):
    """Success response schema"""
    success: bool = True
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseResponse):
    """Error response schema"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

class PaginatedResponse(BaseModel):
    """Paginated response schema"""
    items: List[Any]
    total: int
    page: int
    limit: int
    pages: int
    has_next: bool
    has_prev: bool
    
    @validator('pages', pre=True, always=True)
    def calculate_pages(cls, v, values):
        total = values.get('total', 0)
        limit = values.get('limit', 20)
        return (total + limit - 1) // limit
    
    @validator('has_next', pre=True, always=True)
    def calculate_has_next(cls, v, values):
        page = values.get('page', 1)
        pages = values.get('pages', 1)
        return page < pages
    
    @validator('has_prev', pre=True, always=True)
    def calculate_has_prev(cls, v, values):
        page = values.get('page', 1)
        return page > 1

class SortParams(BaseModel):
    """Sorting parameters"""
    sort_by: Optional[str] = None
    sort_order: SortOrder = SortOrder.ASC

class FilterParams(BaseModel):
    """Base filter parameters"""
    search: Optional[str] = Field(None, max_length=100)
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None

class FileUploadResponse(BaseModel):
    """File upload response schema"""
    success: bool
    filename: str
    file_url: str
    file_size: int
    mime_type: str
    upload_time: datetime

class BulkOperationResponse(BaseModel):
    """Bulk operation response schema"""
    success: bool
    total_processed: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]] = []
    warnings: List[str] = []

class HealthCheckResponse(BaseModel):
    """Health check response schema"""
    status: str = "healthy"
    timestamp: datetime
    version: str
    database: bool
    face_recognition: bool
    services: Dict[str, bool]

class SearchQuery(BaseModel):
    """Search query schema"""
    query: str = Field(..., min_length=1, max_length=100)
    filters: Optional[Dict[str, Any]] = None
    sort: Optional[SortParams] = None
    pagination: Optional[PaginationParams] = None

class ExportParams(BaseModel):
    """Export parameters"""
    format: str = Field(default="csv", pattern="^(csv|excel|pdf|json)$")
    include_headers: bool = True
    date_format: str = Field(default="YYYY-MM-DD", pattern="^(YYYY-MM-DD|DD/MM/YYYY|MM/DD/YYYY)$")
    fields: Optional[List[str]] = None

class NotificationPreferences(BaseModel):
    """Notification preferences schema"""
    email_notifications: bool = True
    sms_notifications: bool = False
    push_notifications: bool = True
    daily_summary: bool = True
    weekly_report: bool = True
    overtime_alerts: bool = True
    leave_reminders: bool = True

class SystemSettings(BaseModel):
    """System settings schema"""
    working_hours_start: str = Field(default="09:00", pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    working_hours_end: str = Field(default="17:00", pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    late_threshold_minutes: int = Field(default=15, ge=0, le=120)
    overtime_threshold_hours: int = Field(default=8, ge=1, le=24)
    auto_checkout_enabled: bool = False
    auto_checkout_time: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    face_confidence_threshold: float = Field(default=0.8, ge=0.1, le=1.0)

class APIKeyInfo(BaseModel):
    """API key information schema"""
    key_id: str
    name: str
    permissions: List[str]
    created_at: datetime
    last_used: Optional[datetime]
    expires_at: Optional[datetime]
    is_active: bool

class AuditLogEntry(BaseModel):
    """Audit log entry schema"""
    id: int
    user_id: Optional[int]
    action: str
    resource_type: str
    resource_id: Optional[str]
    details: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime

class ValidationError(BaseModel):
    """Validation error schema"""
    field: str
    message: str
    code: str

class ValidationErrorResponse(BaseModel):
    """Validation error response schema"""
    success: bool = False
    message: str = "Validation failed"
    errors: List[ValidationError]

class DatabaseStats(BaseModel):
    """Database statistics schema"""
    total_users: int
    active_users: int
    total_attendance_records: int
    total_leave_requests: int
    database_size: str
    last_backup: Optional[datetime]

class SystemInfo(BaseModel):
    """System information schema"""
    version: str
    python_version: str
    database_type: str
    uptime: str
    memory_usage: Dict[str, Union[int, float]]
    disk_usage: Dict[str, Union[int, float]]

class BackupInfo(BaseModel):
    """Backup information schema"""
    backup_id: str
    filename: str
    size: int
    created_at: datetime
    type: str  # full, incremental
    status: str  # success, failed, in_progress

class ConfigUpdate(BaseModel):
    """Configuration update schema"""
    section: str
    key: str
    value: Union[str, int, float, bool]
    description: Optional[str] = None

class ActivityLog(BaseModel):
    """Activity log schema"""
    user_id: int
    action: str
    description: str
    timestamp: datetime
    ip_address: Optional[str]
    success: bool