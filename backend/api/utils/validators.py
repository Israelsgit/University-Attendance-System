"""
Custom Validators for AttendanceAI API
"""

import re
from datetime import date, time, datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import validator, ValidationError
from email_validator import validate_email as email_validate, EmailNotValidError

class AttendanceValidators:
    """Validators for attendance-related data"""
    
    @staticmethod
    def validate_employee_id(employee_id: str) -> str:
        """Validate employee ID format"""
        if not employee_id:
            raise ValueError("Employee ID is required")
        
        # Remove whitespace and convert to uppercase
        employee_id = employee_id.strip().upper()
        
        # Check format: 3-20 alphanumeric characters
        if not re.match(r'^[A-Z0-9]{3,20}$', employee_id):
            raise ValueError("Employee ID must be 3-20 alphanumeric characters")
        
        return employee_id
    
    @staticmethod
    def validate_department(department: str) -> str:
        """Validate department name"""
        if not department:
            raise ValueError("Department is required")
        
        department = department.strip()
        
        # Check length
        if len(department) < 2 or len(department) > 50:
            raise ValueError("Department name must be 2-50 characters")
        
        # Check for valid characters (letters, numbers, spaces, hyphens)
        if not re.match(r'^[A-Za-z0-9\s\-&]+$', department):
            raise ValueError("Department name contains invalid characters")
        
        return department
    
    @staticmethod
    def validate_phone_number(phone: str) -> str:
        """Validate phone number format"""
        if not phone:
            return None
        
        # Remove all non-digit characters for validation
        digits_only = re.sub(r'\D', '', phone)
        
        # Check length (10-15 digits)
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError("Phone number must be 10-15 digits")
        
        # Format as international number
        if len(digits_only) == 10:
            # Assume US number
            return f"+1{digits_only}"
        elif len(digits_only) == 11 and digits_only.startswith('1'):
            # US number with country code
            return f"+{digits_only}"
        else:
            # International number
            return f"+{digits_only}"
    
    @staticmethod
    def validate_email_address(email: str) -> str:
        """Validate email address"""
        if not email:
            raise ValueError("Email is required")
        
        try:
            # Use email-validator library for comprehensive validation
            validated_email = email_validate(email.strip().lower())
            return validated_email.email
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email address: {str(e)}")
    
    @staticmethod
    def validate_password_strength(password: str) -> str:
        """Validate password strength"""
        if not password:
            raise ValueError("Password is required")
        
        # Length check
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if len(password) > 128:
            raise ValueError("Password must be less than 128 characters")
        
        # Character requirements
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if not has_upper:
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not has_lower:
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not has_digit:
            raise ValueError("Password must contain at least one digit")
        
        if not has_special:
            raise ValueError("Password must contain at least one special character")
        
        # Check for common weak passwords
        weak_passwords = [
            "password", "123456", "password123", "admin", "qwerty",
            "letmein", "welcome", "monkey", "dragon", "master"
        ]
        
        if password.lower() in weak_passwords:
            raise ValueError("Password is too common and easily guessable")
        
        return password
    
    @staticmethod
    def validate_work_hours(check_in: time, check_out: time) -> tuple[time, time]:
        """Validate work hours"""
        if not check_in or not check_out:
            return check_in, check_out
        
        # Convert to datetime for comparison
        today = date.today()
        checkin_dt = datetime.combine(today, check_in)
        checkout_dt = datetime.combine(today, check_out)
        
        # Handle overnight shifts
        if checkout_dt < checkin_dt:
            checkout_dt += timedelta(days=1)
        
        # Check maximum shift duration (24 hours)
        max_duration = timedelta(hours=24)
        if checkout_dt - checkin_dt > max_duration:
            raise ValueError("Shift duration cannot exceed 24 hours")
        
        # Check minimum shift duration (15 minutes)
        min_duration = timedelta(minutes=15)
        if checkout_dt - checkin_dt < min_duration:
            raise ValueError("Shift duration must be at least 15 minutes")
        
        return check_in, check_out
    
    @staticmethod
    def validate_date_range(start_date: date, end_date: date, max_range_days: int = 365) -> tuple[date, date]:
        """Validate date range"""
        if not start_date or not end_date:
            raise ValueError("Both start date and end date are required")
        
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date")
        
        # Check maximum range
        if (end_date - start_date).days > max_range_days:
            raise ValueError(f"Date range cannot exceed {max_range_days} days")
        
        # Check if dates are not too far in the future
        max_future_date = date.today() + timedelta(days=365)
        if start_date > max_future_date or end_date > max_future_date:
            raise ValueError("Dates cannot be more than 1 year in the future")
        
        return start_date, end_date
    
    @staticmethod
    def validate_leave_dates(start_date: date, end_date: date) -> tuple[date, date]:
        """Validate leave request dates"""
        # Basic date range validation
        start_date, end_date = AttendanceValidators.validate_date_range(start_date, end_date, 365)
        
        # Check if start date is not in the past (allow today)
        if start_date < date.today():
            raise ValueError("Leave start date cannot be in the past")
        
        # Check minimum advance notice (1 day)
        if start_date <= date.today():
            raise ValueError("Leave requests must be submitted at least 1 day in advance")
        
        return start_date, end_date

class FileValidators:
    """Validators for file uploads"""
    
    ALLOWED_IMAGE_TYPES = {
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'
    }
    
    ALLOWED_DOCUMENT_TYPES = {
        'application/pdf', 'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain'
    }
    
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    @staticmethod
    def validate_image_file(file_content: bytes, content_type: str, filename: str) -> bool:
        """Validate uploaded image file"""
        # Check content type
        if content_type not in FileValidators.ALLOWED_IMAGE_TYPES:
            raise ValueError(f"Invalid image type. Allowed types: {', '.join(FileValidators.ALLOWED_IMAGE_TYPES)}")
        
        # Check file size
        if len(file_content) > FileValidators.MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum limit of {FileValidators.MAX_FILE_SIZE / (1024*1024):.1f}MB")
        
        # Check filename
        if not filename or len(filename) > 255:
            raise ValueError("Invalid filename")
        
        # Check file signature (magic bytes)
        if content_type == 'image/jpeg' and not file_content.startswith(b'\xff\xd8\xff'):
            raise ValueError("File content doesn't match JPEG format")
        elif content_type == 'image/png' and not file_content.startswith(b'\x89\x50\x4e\x47'):
            raise ValueError("File content doesn't match PNG format")
        
        return True
    
    @staticmethod
    def validate_document_file(file_content: bytes, content_type: str, filename: str) -> bool:
        """Validate uploaded document file"""
        # Check content type
        if content_type not in FileValidators.ALLOWED_DOCUMENT_TYPES:
            raise ValueError(f"Invalid document type. Allowed types: {', '.join(FileValidators.ALLOWED_DOCUMENT_TYPES)}")
        
        # Check file size
        if len(file_content) > FileValidators.MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum limit of {FileValidators.MAX_FILE_SIZE / (1024*1024):.1f}MB")
        
        # Check filename
        if not filename or len(filename) > 255:
            raise ValueError("Invalid filename")
        
        return True

class BusinessRuleValidators:
    """Validators for business rules"""
    
    @staticmethod
    def validate_attendance_time(check_time: time, attendance_type: str = "check_in") -> time:
        """Validate attendance check-in/check-out time"""
        if not check_time:
            raise ValueError(f"{attendance_type.replace('_', ' ').title()} time is required")
        
        # Define business hours (can be configurable)
        business_start = time(6, 0)  # 6:00 AM
        business_end = time(23, 59)  # 11:59 PM
        
        # Allow flexible hours but warn about unusual times
        if check_time < business_start or check_time > business_end:
            # Don't raise error, but this could be logged as unusual
            pass
        
        return check_time
    
    @staticmethod
    def validate_overtime_request(regular_hours: float, overtime_hours: float) -> float:
        """Validate overtime hours"""
        if overtime_hours < 0:
            raise ValueError("Overtime hours cannot be negative")
        
        if overtime_hours > 12:
            raise ValueError("Overtime hours cannot exceed 12 hours per day")
        
        total_hours = regular_hours + overtime_hours
        if total_hours > 24:
            raise ValueError("Total working hours cannot exceed 24 hours")
        
        return overtime_hours
    
    @staticmethod
    def validate_leave_balance(requested_days: int, available_balance: int, leave_type: str = "annual") -> int:
        """Validate leave balance"""
        if requested_days <= 0:
            raise ValueError("Leave days must be greater than 0")
        
        if requested_days > available_balance and leave_type != "emergency":
            raise ValueError(f"Insufficient leave balance. Available: {available_balance} days")
        
        # Special rules for different leave types
        if leave_type == "sick" and requested_days > 30:
            raise ValueError("Sick leave cannot exceed 30 days without medical certificate")
        
        if leave_type == "annual" and requested_days > 21:
            raise ValueError("Annual leave cannot exceed 21 consecutive days")
        
        return requested_days
    
    @staticmethod
    def validate_manager_assignment(employee_id: str, manager_id: str) -> bool:
        """Validate manager assignment"""
        if employee_id == manager_id:
            raise ValueError("Employee cannot be their own manager")
        
        # Additional checks could be added here:
        # - Circular manager relationships
        # - Department hierarchy
        # - Manager permissions
        
        return True

class APIValidators:
    """Validators for API requests"""
    
    @staticmethod
    def validate_pagination_params(page: int, limit: int) -> tuple[int, int]:
        """Validate pagination parameters"""
        if page < 1:
            raise ValueError("Page number must be greater than 0")
        
        if limit < 1:
            raise ValueError("Limit must be greater than 0")
        
        if limit > 100:
            raise ValueError("Limit cannot exceed 100")
        
        return page, limit
    
    @staticmethod
    def validate_sort_params(sort_by: str, sort_order: str, allowed_fields: List[str]) -> tuple[str, str]:
        """Validate sorting parameters"""
        if sort_by and sort_by not in allowed_fields:
            raise ValueError(f"Invalid sort field. Allowed fields: {', '.join(allowed_fields)}")
        
        if sort_order not in ['asc', 'desc']:
            raise ValueError("Sort order must be 'asc' or 'desc'")
        
        return sort_by, sort_order
    
    @staticmethod
    def validate_search_query(query: str) -> str:
        """Validate search query"""
        if not query:
            return query
        
        query = query.strip()
        
        if len(query) < 2:
            raise ValueError("Search query must be at least 2 characters")
        
        if len(query) > 100:
            raise ValueError("Search query cannot exceed 100 characters")
        
        # Remove potentially dangerous characters for SQL injection prevention
        dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
        for char in dangerous_chars:
            if char in query.lower():
                raise ValueError("Search query contains invalid characters")
        
        return query

def create_custom_validator(validation_func, error_message: str = None):
    """Create a custom Pydantic validator"""
    def validator_wrapper(cls, v):
        try:
            return validation_func(v)
        except ValueError as e:
            raise ValueError(error_message or str(e))
    
    return validator_wrapper

# Example usage in Pydantic models:
"""
from pydantic import BaseModel, validator
from api.utils.validators import AttendanceValidators

class UserCreateSchema(BaseModel):
    email: str
    employee_id: str
    
    @validator('email')
    def validate_email(cls, v):
        return AttendanceValidators.validate_email_address(v)
    
    @validator('employee_id')
    def validate_emp_id(cls, v):
        return AttendanceValidators.validate_employee_id(v)
"""