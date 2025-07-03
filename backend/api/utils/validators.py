"""
Data Validators for University System
"""

import re
from typing import Optional, List
from email_validator import validate_email, EmailNotValidError
from config.settings import settings

class ValidationError(Exception):
    """Custom validation error"""
    pass

def validate_email_domain(email: str) -> bool:
    """Validate if email belongs to university domain"""
    try:
        # First validate email format
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError:
        return False
    
    # Check university domains
    university_domains = [
        f"@{settings.UNIVERSITY_EMAIL_DOMAIN}",
        f"@student.{settings.UNIVERSITY_EMAIL_DOMAIN}",
        "@gmail.com",  # Allow Gmail for testing
        "@yahoo.com",  # Allow Yahoo for testing
    ]
    
    return any(email.lower().endswith(domain.lower()) for domain in university_domains)

def validate_staff_id(staff_id: str) -> bool:
    """Validate staff ID format: BU/DEPT/XXX"""
    if not staff_id:
        return False
    
    # Pattern: BU/CSC/001 or BU/CSC/0001
    pattern = rf"^{settings.UNIVERSITY_SHORT_NAME}/[A-Z]{{2,5}}/\d{{3,4}}$"
    return bool(re.match(pattern, staff_id.upper()))

def validate_student_id(student_id: str) -> bool:
    """Validate student ID format: BU/DEPT/YY/XXX"""
    if not student_id:
        return False
    
    # Pattern: BU/CSC/18/001 or BU/CSC/2018/001
    pattern = rf"^{settings.UNIVERSITY_SHORT_NAME}/[A-Z]{{2,5}}/(\d{{2}}|\d{{4}})/\d{{3,4}}$"
    return bool(re.match(pattern, student_id.upper()))

def validate_course_code(course_code: str) -> bool:
    """Validate course code format: CSC 438"""
    if not course_code:
        return False
    
    # Pattern: ABC 123 or ABCD 1234
    pattern = r"^[A-Z]{2,4}\s\d{3,4}$"
    return bool(re.match(pattern, course_code.upper()))

def validate_phone_number(phone: str) -> bool:
    """Validate Nigerian phone number format"""
    if not phone:
        return False
    
    # Nigerian phone number patterns
    patterns = [
        r"^\+234[789]\d{9}$",  # +234XXXXXXXXX
        r"^0[789]\d{9}$",      # 0XXXXXXXXX
        r"^[789]\d{9}$",       # XXXXXXXXX
        r"^\+1\d{10}$",        # US format for testing
        r"^\d{10}$"            # 10 digits for testing
    ]
    
    return any(re.match(pattern, phone.strip()) for pattern in patterns)

def validate_matric_number(matric_number: str) -> bool:
    """Validate matriculation number format"""
    if not matric_number:
        return True  # Optional field
    
    # Pattern: 6 digits or alphanumeric
    patterns = [
        r"^\d{6}$",           # 123456
        r"^[A-Z]\d{5}$",      # A12345
        r"^\d{2}[A-Z]\d{3}$"  # 12A345
    ]
    
    return any(re.match(pattern, matric_number.upper()) for pattern in patterns)

def validate_academic_session(session: str) -> bool:
    """Validate academic session format: 2024/2025"""
    if not session:
        return False
    
    pattern = r"^\d{4}/\d{4}$"
    if not re.match(pattern, session):
        return False
    
    years = session.split("/")
    try:
        year1 = int(years[0])
        year2 = int(years[1])
        return year2 == year1 + 1 and 2020 <= year1 <= 2030
    except ValueError:
        return False

def validate_password_strength(password: str) -> tuple[bool, List[str]]:
    """Validate password strength and return errors"""
    errors = []
    
    if len(password) < 6:
        errors.append("Password must be at least 6 characters long")
    
    if len(password) > 128:
        errors.append("Password must be less than 128 characters")
    
    if not re.search(r"[a-zA-Z]", password):
        errors.append("Password must contain at least one letter")
    
    # Optional: Add more strict requirements
    # if not re.search(r"[A-Z]", password):
    #     errors.append("Password must contain at least one uppercase letter")
    
    # if not re.search(r"[0-9]", password):
    #     errors.append("Password must contain at least one number")
    
    return len(errors) == 0, errors

def validate_level(level: str) -> bool:
    """Validate student level"""
    valid_levels = ["100", "200", "300", "400", "500"]
    return level in valid_levels

def validate_semester(semester: str) -> bool:
    """Validate semester"""
    valid_semesters = ["First Semester", "Second Semester", "Rain Semester"]
    return semester in valid_semesters

def validate_course_unit(unit: int) -> bool:
    """Validate course unit"""
    return 1 <= unit <= 6

def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension"""
    if not filename or '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in [ext.lower() for ext in allowed_extensions]

def validate_image_file(filename: str) -> bool:
    """Validate image file extension"""
    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
    return validate_file_extension(filename, allowed_extensions)

def sanitize_input(input_str: str, max_length: int = 255) -> str:
    """Sanitize input string"""
    if not input_str:
        return ""
    
    # Remove potentially dangerous characters
    cleaned = re.sub(r'[<>"\']', '', input_str.strip())
    
    # Truncate if too long
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    return cleaned

def validate_user_data(data: dict, user_type: str) -> tuple[bool, List[str]]:
    """Validate complete user data"""
    errors = []
    
    # Common validations
    if not data.get('full_name'):
        errors.append("Full name is required")
    elif len(data['full_name'].strip()) < 2:
        errors.append("Full name must be at least 2 characters")
    
    if not data.get('email'):
        errors.append("Email is required")
    elif not validate_email_domain(data['email']):
        errors.append("Invalid email or email domain not allowed")
    
    if not data.get('password'):
        errors.append("Password is required")
    else:
        pwd_valid, pwd_errors = validate_password_strength(data['password'])
        if not pwd_valid:
            errors.extend(pwd_errors)
    
    # Phone validation (optional)
    if data.get('phone') and not validate_phone_number(data['phone']):
        errors.append("Invalid phone number format")
    
    # User type specific validations
    if user_type == 'lecturer':
        if not data.get('staff_id'):
            errors.append("Staff ID is required for lecturers")
        elif not validate_staff_id(data['staff_id']):
            errors.append("Invalid staff ID format")
    
    elif user_type == 'student':
        if not data.get('student_id'):
            errors.append("Student ID is required for students")
        elif not validate_student_id(data['student_id']):
            errors.append("Invalid student ID format")
        
        if not data.get('level'):
            errors.append("Level is required for students")
        elif not validate_level(data['level']):
            errors.append("Invalid level")
        
        if data.get('matric_number') and not validate_matric_number(data['matric_number']):
            errors.append("Invalid matriculation number format")
    
    return len(errors) == 0, errors
