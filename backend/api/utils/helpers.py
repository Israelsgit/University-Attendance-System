"""
Helper Functions and Utilities
"""

import re
import uuid
import hashlib
import secrets
import string
from datetime import datetime, date, time, timedelta
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import mimetypes
import base64
import json

def generate_employee_id(department: str = "GEN") -> str:
    """Generate unique employee ID"""
    timestamp = datetime.now().strftime("%y%m")
    random_part = secrets.randbelow(999) + 1
    return f"{department.upper()[:3]}{timestamp}{random_part:03d}"

def generate_secure_filename(original_filename: str) -> str:
    """Generate secure filename for file uploads"""
    # Get file extension
    file_ext = Path(original_filename).suffix.lower()
    
    # Generate unique filename
    unique_id = uuid.uuid4().hex[:12]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return f"{timestamp}_{unique_id}{file_ext}"

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (10-15 digits)
    return 10 <= len(digits_only) <= 15

def format_phone(phone: str) -> str:
    """Format phone number consistently"""
    if not phone:
        return None
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Format as +1-XXX-XXX-XXXX for US numbers
    if len(digits_only) == 10:
        return f"+1-{digits_only[:3]}-{digits_only[3:6]}-{digits_only[6:]}"
    elif len(digits_only) == 11 and digits_only.startswith('1'):
        return f"+1-{digits_only[1:4]}-{digits_only[4:7]}-{digits_only[7:]}"
    else:
        # For international numbers, just add + and format with dashes
        return f"+{digits_only}"

def calculate_age(birth_date: date) -> int:
    """Calculate age from birth date"""
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def calculate_working_days(start_date: date, end_date: date, exclude_weekends: bool = True) -> int:
    """Calculate working days between two dates"""
    total_days = (end_date - start_date).days + 1
    
    if not exclude_weekends:
        return total_days
    
    working_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        # Monday = 0, Sunday = 6
        if current_date.weekday() < 5:  # Monday to Friday
            working_days += 1
        current_date += timedelta(days=1)
    
    return working_days

def calculate_overtime_hours(check_in: time, check_out: time, standard_hours: float = 8.0) -> float:
    """Calculate overtime hours"""
    if not check_in or not check_out:
        return 0.0
    
    # Convert to datetime for calculation
    today = date.today()
    checkin_dt = datetime.combine(today, check_in)
    checkout_dt = datetime.combine(today, check_out)
    
    # Handle overnight shifts
    if checkout_dt < checkin_dt:
        checkout_dt += timedelta(days=1)
    
    total_hours = (checkout_dt - checkin_dt).total_seconds() / 3600
    return max(0, total_hours - standard_hours)

def time_to_decimal(time_obj: time) -> float:
    """Convert time to decimal hours"""
    if not time_obj:
        return 0.0
    return time_obj.hour + time_obj.minute / 60 + time_obj.second / 3600

def decimal_to_time(decimal_hours: float) -> time:
    """Convert decimal hours to time"""
    hours = int(decimal_hours)
    minutes = int((decimal_hours - hours) * 60)
    seconds = int(((decimal_hours - hours) * 60 - minutes) * 60)
    return time(hours, minutes, seconds)

def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    try:
        size_bytes = Path(file_path).stat().st_size
        return round(size_bytes / (1024 * 1024), 2)
    except:
        return 0.0

def get_mime_type(filename: str) -> str:
    """Get MIME type from filename"""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing/replacing invalid characters"""
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = Path(sanitized).stem, Path(sanitized).suffix
        max_name_length = 255 - len(ext)
        sanitized = name[:max_name_length] + ext
    
    return sanitized

def hash_file(file_path: str) -> str:
    """Generate SHA-256 hash of file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except:
        return ""

def generate_password(length: int = 12) -> str:
    """Generate secure password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(characters) for _ in range(length))
    
    # Ensure at least one character from each category
    if not any(c.isupper() for c in password):
        password = password[:-1] + secrets.choice(string.ascii_uppercase)
    if not any(c.islower() for c in password):
        password = password[:-1] + secrets.choice(string.ascii_lowercase)
    if not any(c.isdigit() for c in password):
        password = password[:-1] + secrets.choice(string.digits)
    
    return password

def parse_date_string(date_string: str) -> Optional[date]:
    """Parse date string in various formats"""
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%m-%d-%Y",
        "%Y/%m/%d"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt).date()
        except ValueError:
            continue
    
    return None

def parse_time_string(time_string: str) -> Optional[time]:
    """Parse time string in various formats"""
    formats = [
        "%H:%M",
        "%H:%M:%S",
        "%I:%M %p",
        "%I:%M:%S %p"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(time_string, fmt).time()
        except ValueError:
            continue
    
    return None

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minutes"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"

def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to maximum length with suffix"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces and special characters with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    
    # Remove leading/trailing hyphens
    return text.strip('-')

def generate_api_key() -> str:
    """Generate secure API key"""
    return secrets.token_urlsafe(32)

def encode_base64(data: Union[str, bytes]) -> str:
    """Encode data to base64 string"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return base64.b64encode(data).decode('utf-8')

def decode_base64(encoded_data: str) -> bytes:
    """Decode base64 string to bytes"""
    return base64.b64decode(encoded_data)

def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """Flatten nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def is_working_day(check_date: date, exclude_weekends: bool = True) -> bool:
    """Check if date is a working day"""
    if exclude_weekends and check_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    # Add holiday checking logic here if needed
    # holidays = get_holidays(check_date.year)
    # if check_date in holidays:
    #     return False
    
    return True

def get_week_range(target_date: date) -> tuple[date, date]:
    """Get start and end date of the week containing target_date"""
    days_since_monday = target_date.weekday()
    week_start = target_date - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end

def get_month_range(target_date: date) -> tuple[date, date]:
    """Get start and end date of the month containing target_date"""
    month_start = target_date.replace(day=1)
    
    # Get last day of month
    if target_date.month == 12:
        next_month = target_date.replace(year=target_date.year + 1, month=1, day=1)
    else:
        next_month = target_date.replace(month=target_date.month + 1, day=1)
    
    month_end = next_month - timedelta(days=1)
    return month_start, month_end

def calculate_leave_days(start_date: date, end_date: date, exclude_weekends: bool = True) -> int:
    """Calculate number of leave days between dates"""
    return calculate_working_days(start_date, end_date, exclude_weekends)

def validate_date_range(start_date: date, end_date: date, max_range_days: int = 365) -> bool:
    """Validate date range"""
    if start_date > end_date:
        return False
    
    if (end_date - start_date).days > max_range_days:
        return False
    
    return True

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency"""
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    elif currency == "GBP":
        return f"£{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def calculate_percentage(part: float, total: float) -> float:
    """Calculate percentage with division by zero protection"""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division with default value for division by zero"""
    if denominator == 0:
        return default
    return numerator / denominator

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def remove_duplicates_preserve_order(lst: List) -> List:
    """Remove duplicates from list while preserving order"""
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]

def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """Safely parse JSON string with default fallback"""
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """Safely serialize object to JSON with default fallback"""
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return default

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask sensitive data like email, phone numbers"""
    if not data or len(data) <= visible_chars:
        return data
    
    if "@" in data:  # Email
        local, domain = data.split("@")
        if len(local) <= visible_chars:
            return data
        masked_local = local[:2] + mask_char * (len(local) - 4) + local[-2:]
        return f"{masked_local}@{domain}"
    else:  # Phone or other
        return data[:visible_chars] + mask_char * (len(data) - visible_chars)

def generate_qr_code_data(user_id: int, timestamp: str = None) -> str:
    """Generate QR code data for attendance"""
    if not timestamp:
        timestamp = datetime.now().isoformat()
    
    data = {
        "user_id": user_id,
        "timestamp": timestamp,
        "type": "attendance_checkin"
    }
    
    return encode_base64(json.dumps(data))

def validate_qr_code_data(qr_data: str, max_age_minutes: int = 5) -> Dict[str, Any]:
    """Validate QR code data for attendance"""
    try:
        decoded_data = decode_base64(qr_data)
        data = json.loads(decoded_data.decode('utf-8'))
        
        # Check required fields
        required_fields = ["user_id", "timestamp", "type"]
        if not all(field in data for field in required_fields):
            return {"valid": False, "error": "Missing required fields"}
        
        # Check type
        if data["type"] != "attendance_checkin":
            return {"valid": False, "error": "Invalid QR code type"}
        
        # Check timestamp age
        qr_timestamp = datetime.fromisoformat(data["timestamp"])
        age_minutes = (datetime.now() - qr_timestamp).total_seconds() / 60
        
        if age_minutes > max_age_minutes:
            return {"valid": False, "error": "QR code expired"}
        
        return {"valid": True, "data": data}
        
    except Exception as e:
        return {"valid": False, "error": f"Invalid QR code: {str(e)}"}

class DateTimeHelper:
    """Helper class for datetime operations"""
    
    @staticmethod
    def get_current_time_string() -> str:
        """Get current time as ISO string"""
        return datetime.now().isoformat()
    
    @staticmethod
    def get_today_date_string() -> str:
        """Get today's date as ISO string"""
        return date.today().isoformat()
    
    @staticmethod
    def days_between(date1: date, date2: date) -> int:
        """Calculate days between two dates"""
        return abs((date2 - date1).days)
    
    @staticmethod
    def is_future_date(check_date: date) -> bool:
        """Check if date is in the future"""
        return check_date > date.today()
    
    @staticmethod
    def is_past_date(check_date: date) -> bool:
        """Check if date is in the past"""
        return check_date < date.today()
    
    @staticmethod
    def add_business_days(start_date: date, business_days: int) -> date:
        """Add business days to a date (excluding weekends)"""
        current_date = start_date
        days_added = 0
        
        while days_added < business_days:
            current_date += timedelta(days=1)
            if current_date.weekday() < 5:  # Monday to Friday
                days_added += 1
        
        return current_date

class FileHelper:
    """Helper class for file operations"""
    
    @staticmethod
    def ensure_directory_exists(directory_path: str):
        """Create directory if it doesn't exist"""
        Path(directory_path).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def delete_file_if_exists(file_path: str) -> bool:
        """Delete file if it exists"""
        try:
            Path(file_path).unlink()
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension"""
        return Path(filename).suffix.lower()
    
    @staticmethod
    def is_image_file(filename: str) -> bool:
        """Check if file is an image"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        return FileHelper.get_file_extension(filename) in image_extensions