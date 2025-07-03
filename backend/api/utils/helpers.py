# backend/api/utils/helpers.py
"""
Helper utilities for University System
"""

import re
import hashlib
import secrets
import string
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Union
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

def generate_id(prefix: str = "", length: int = 6) -> str:
    """Generate a unique ID with optional prefix"""
    numbers = ''.join(secrets.choice(string.digits) for _ in range(length))
    return f"{prefix}{numbers}" if prefix else numbers

def generate_staff_id(department_code: str = "CSC") -> str:
    """Generate staff ID in university format: BU/CSC/001"""
    return f"{settings.UNIVERSITY_SHORT_NAME}/{department_code.upper()}/{generate_id('', 3)}"

def generate_student_id(department_code: str = "CSC", year: Optional[str] = None) -> str:
    """Generate student ID in university format: BU/CSC/24/001"""
    if not year:
        year = str(datetime.now().year)[2:]  # Last 2 digits of current year
    return f"{settings.UNIVERSITY_SHORT_NAME}/{department_code.upper()}/{year}/{generate_id('', 3)}"

def generate_matric_number() -> str:
    """Generate matriculation number: 6 digits"""
    return generate_id('', 6)

def format_phone_number(phone: str) -> str:
    """Format phone number to Nigerian standard"""
    if not phone:
        return ""
    
    # Remove all non-digits
    digits_only = re.sub(r'\D', '', phone)
    
    # Handle different input formats
    if digits_only.startswith('234'):
        return f"+{digits_only}"
    elif digits_only.startswith('0') and len(digits_only) == 11:
        return f"+234{digits_only[1:]}"
    elif len(digits_only) == 10:
        return f"+234{digits_only}"
    else:
        return phone  # Return original if can't format

def validate_nigerian_phone(phone: str) -> bool:
    """Validate Nigerian phone number"""
    if not phone:
        return False
    
    patterns = [
        r'^\+234[789]\d{9}$',  # +234XXXXXXXXX
        r'^0[789]\d{9}$',      # 0XXXXXXXXX  
        r'^[789]\d{9}$'        # XXXXXXXXX
    ]
    return any(re.match(pattern, phone.strip()) for pattern in patterns)

def calculate_age(date_of_birth: date) -> int:
    """Calculate age from date of birth"""
    if not date_of_birth:
        return 0
    
    today = date.today()
    return today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))

def get_academic_year(input_date: Optional[date] = None) -> str:
    """Get academic year for a given date"""
    if not input_date:
        input_date = date.today()
    
    # Academic year typically starts in September
    if input_date.month >= 9:
        start_year = input_date.year
        end_year = input_date.year + 1
    else:
        start_year = input_date.year - 1
        end_year = input_date.year
    
    return f"{start_year}/{end_year}"

def get_semester(input_date: Optional[date] = None) -> str:
    """Determine current semester"""
    if not input_date:
        input_date = date.today()
    
    month = input_date.month
    
    # First semester: September to January
    if month >= 9 or month == 1:
        return "First Semester"
    # Second semester: February to June  
    elif 2 <= month <= 6:
        return "Second Semester"
    # Rain semester: July to August
    else:
        return "Rain Semester"

def hash_file_content(content: bytes) -> str:
    """Generate hash of file content"""
    return hashlib.sha256(content).hexdigest()

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    if not filename:
        return "file"
    
    # Remove or replace unsafe characters
    safe_chars = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Limit length
    if len(safe_chars) > 100:
        name, ext = safe_chars.rsplit('.', 1) if '.' in safe_chars else (safe_chars, '')
        safe_chars = f"{name[:95]}.{ext}" if ext else name[:100]
    
    return safe_chars

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format"""
    if seconds < 0:
        return "0s"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def calculate_attendance_percentage(attended: int, total: int) -> float:
    """Calculate attendance percentage"""
    if total == 0:
        return 0.0
    return round((attended / total) * 100, 2)

def get_attendance_status(percentage: float) -> str:
    """Get attendance status based on percentage"""
    if percentage >= settings.MINIMUM_ATTENDANCE_PERCENTAGE:
        return "good"
    elif percentage >= 60:
        return "warning"
    else:
        return "poor"

def generate_attendance_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate attendance summary from records"""
    if not records:
        return {
            "total": 0,
            "present": 0,
            "late": 0,
            "absent": 0,
            "attended": 0,
            "percentage": 0.0,
            "status": "poor"
        }
    
    total = len(records)
    present = len([r for r in records if r.get('status') == 'present'])
    late = len([r for r in records if r.get('status') == 'late'])
    absent = len([r for r in records if r.get('status') == 'absent'])
    
    attended = present + late
    percentage = calculate_attendance_percentage(attended, total)
    
    return {
        "total": total,
        "present": present,
        "late": late,
        "absent": absent,
        "attended": attended,
        "percentage": percentage,
        "status": get_attendance_status(percentage)
    }

def get_week_dates(input_date: Optional[date] = None) -> Dict[str, date]:
    """Get start and end dates of week for given date"""
    if not input_date:
        input_date = date.today()
    
    # Monday as start of week
    days_since_monday = input_date.weekday()
    start_of_week = input_date - timedelta(days=days_since_monday)
    end_of_week = start_of_week + timedelta(days=6)
    
    return {
        "start": start_of_week,
        "end": end_of_week
    }

def get_month_dates(input_date: Optional[date] = None) -> Dict[str, date]:
    """Get start and end dates of month for given date"""
    if not input_date:
        input_date = date.today()
    
    start_of_month = input_date.replace(day=1)
    
    # Get last day of month
    if input_date.month == 12:
        end_of_month = input_date.replace(year=input_date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = input_date.replace(month=input_date.month + 1, day=1) - timedelta(days=1)
    
    return {
        "start": start_of_month,
        "end": end_of_month
    }

def paginate_results(items: List[Any], page: int = 1, size: int = 20) -> Dict[str, Any]:
    """Paginate a list of items"""
    total = len(items)
    start = (page - 1) * size
    end = start + size
    
    paginated_items = items[start:end]
    total_pages = (total + size - 1) // size  # Ceiling division
    
    return {
        "items": paginated_items,
        "total": total,
        "page": page,
        "size": size,
        "pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }

def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask sensitive data showing only last few characters"""
    if not data:
        return ""
    
    if len(data) <= visible_chars:
        return mask_char * len(data)
    
    masked_part = mask_char * (len(data) - visible_chars)
    visible_part = data[-visible_chars:]
    
    return masked_part + visible_part

def log_user_action(user_id: int, action: str, details: Optional[Dict[str, Any]] = None):
    """Log user action for audit trail"""
    log_data = {
        "user_id": user_id,
        "action": action,
        "timestamp": datetime.now().isoformat(),
        "details": details or {}
    }
    
    logger.info(f"User action: {log_data}")

def create_error_response(message: str, details: Optional[str] = None) -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        "success": False,
        "error": message,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }

def create_success_response(message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create standardized success response"""
    return {
        "success": True,
        "message": message,
        "data": data or {},
        "timestamp": datetime.now().isoformat()
    }

def is_business_day(check_date: date) -> bool:
    """Check if date is a business day (Monday-Friday)"""
    return check_date.weekday() < 5

def get_business_days_between(start_date: date, end_date: date) -> int:
    """Get number of business days between two dates"""
    if start_date > end_date:
        return 0
    
    current = start_date
    count = 0
    
    while current <= end_date:
        if is_business_day(current):
            count += 1
        current += timedelta(days=1)
    
    return count

def validate_course_code_format(course_code: str) -> bool:
    """Validate course code format (e.g., CSC 438)"""
    if not course_code:
        return False
    
    pattern = r'^[A-Z]{2,4}\s\d{3,4}$'
    return bool(re.match(pattern, course_code.upper()))

def parse_course_code(course_code: str) -> Dict[str, str]:
    """Parse course code into department and number"""
    if not validate_course_code_format(course_code):
        raise ValueError("Invalid course code format")
    
    parts = course_code.upper().split()
    return {
        "department": parts[0],
        "number": parts[1],
        "full_code": course_code.upper()
    }

def generate_backup_filename(prefix: str, extension: str = "sql") -> str:
    """Generate backup filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_backup_{timestamp}.{extension}"

def format_file_size(size_bytes: int) -> str:
    """Format file size in bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def get_client_ip(request) -> str:
    """Get client IP address from request"""
    # Try to get real IP from headers (in case of proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to client host
    if hasattr(request, 'client') and request.client:
        return request.client.host
    
    return "unknown"

def validate_json_data(data: Any, required_fields: List[str]) -> tuple[bool, List[str]]:
    """Validate JSON data has required fields"""
    errors = []
    
    if not isinstance(data, dict):
        errors.append("Data must be a JSON object")
        return False, errors
    
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            errors.append(f"Field '{field}' cannot be empty")
    
    return len(errors) == 0, errors

def convert_to_timezone(dt: datetime, timezone_str: str = "UTC") -> datetime:
    """Convert datetime to specified timezone"""
    try:
        import pytz
        if dt.tzinfo is None:
            # Assume UTC if no timezone info
            dt = pytz.UTC.localize(dt)
        
        target_tz = pytz.timezone(timezone_str)
        return dt.astimezone(target_tz)
    except ImportError:
        logger.warning("pytz not installed, returning original datetime")
        return dt
    except Exception as e:
        logger.error(f"Error converting timezone: {e}")
        return dt

def clean_dict(data: Dict[str, Any], remove_none: bool = True, remove_empty: bool = True) -> Dict[str, Any]:
    """Clean dictionary by removing None/empty values"""
    if not isinstance(data, dict):
        return data
    
    cleaned = {}
    for key, value in data.items():
        if remove_none and value is None:
            continue
        if remove_empty and isinstance(value, str) and not value.strip():
            continue
        
        # Recursively clean nested dictionaries
        if isinstance(value, dict):
            cleaned[key] = clean_dict(value, remove_none, remove_empty)
        else:
            cleaned[key] = value
    
    return cleaned

def generate_random_string(length: int = 32, include_symbols: bool = False) -> str:
    """Generate random string for tokens, passwords, etc."""
    characters = string.ascii_letters + string.digits
    if include_symbols:
        characters += "!@#$%^&*"
    
    return ''.join(secrets.choice(characters) for _ in range(length))

def is_valid_uuid(uuid_string: str) -> bool:
    """Check if string is a valid UUID"""
    try:
        import uuid
        uuid.UUID(uuid_string)
        return True
    except (ValueError, TypeError):
        return False

def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result

def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to integer"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def extract_numbers(text: str) -> List[int]:
    """Extract all numbers from text"""
    if not text:
        return []
    
    numbers = re.findall(r'\d+', text)
    return [int(num) for num in numbers]

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    if not text:
        return ""
    
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

# University-specific helper functions

def get_student_level_from_id(student_id: str) -> Optional[str]:
    """Extract student level from student ID"""
    try:
        # Pattern: BU/CSC/18/001 - year 18 means started in 2018
        parts = student_id.split('/')
        if len(parts) >= 3:
            year = parts[2]
            current_year = datetime.now().year
            
            # Convert 2-digit year to 4-digit
            if len(year) == 2:
                year_int = int(year)
                if year_int > 50:  # Assume 1900s
                    full_year = 1900 + year_int
                else:  # Assume 2000s
                    full_year = 2000 + year_int
            else:
                full_year = int(year)
            
            # Calculate level based on years passed
            years_passed = current_year - full_year
            level = min(100 + (years_passed * 100), 500)
            return str(level)
    except (ValueError, IndexError):
        pass
    
    return None

def format_academic_session(year: int) -> str:
    """Format academic session from year"""
    return f"{year}/{year + 1}"

def get_current_academic_session() -> str:
    """Get current academic session"""
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Academic year starts in September
    if current_month >= 9:
        return format_academic_session(current_year)
    else:
        return format_academic_session(current_year - 1)