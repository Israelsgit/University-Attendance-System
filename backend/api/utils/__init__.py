"""
Utilities Package
Contains security, validation, and helper utilities
"""

from .security import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    verify_token,
    get_current_user,
    get_current_active_user,
    get_current_lecturer,
    get_current_admin,
    get_current_student
)

from .validators import (
    validate_email_domain,
    validate_staff_id,
    validate_student_id,
    validate_course_code,
    validate_phone_number,
    validate_matric_number,
    validate_academic_session,
    validate_password_strength,
    validate_level,
    validate_semester,
    validate_course_unit,
    validate_file_extension,
    validate_image_file,
    sanitize_input,
    validate_user_data,
    ValidationError
)

from .helpers import (
    generate_id,
    generate_staff_id,
    generate_student_id,
    generate_matric_number,
    format_phone_number,
    validate_nigerian_phone,
    calculate_age,
    get_academic_year,
    get_semester,
    hash_file_content,
    sanitize_filename,
    format_duration,
    calculate_attendance_percentage,
    get_attendance_status,
    generate_attendance_summary,
    get_week_dates,
    get_month_dates,
    paginate_results,
    mask_sensitive_data,
    log_user_action,
    create_error_response,
    create_success_response,
    is_business_day,
    get_business_days_between,
    validate_course_code_format,
    parse_course_code,
    generate_backup_filename
)

__all__ = [
    # Security functions
    "get_password_hash",
    "verify_password", 
    "create_access_token",
    "verify_token",
    "get_current_user",
    "get_current_active_user",
    "get_current_lecturer",
    "get_current_admin",
    "get_current_student",
    
    # Validation functions
    "validate_email_domain",
    "validate_staff_id",
    "validate_student_id",
    "validate_course_code",
    "validate_phone_number",
    "validate_matric_number",
    "validate_academic_session",
    "validate_password_strength",
    "validate_level",
    "validate_semester",
    "validate_course_unit",
    "validate_file_extension",
    "validate_image_file",
    "sanitize_input",
    "validate_user_data",
    "ValidationError",
    
    # Helper functions
    "generate_id",
    "generate_staff_id",
    "generate_student_id",
    "generate_matric_number",
    "format_phone_number",
    "validate_nigerian_phone",
    "calculate_age",
    "get_academic_year",
    "get_semester",
    "hash_file_content",
    "sanitize_filename",
    "format_duration",
    "calculate_attendance_percentage",
    "get_attendance_status",
    "generate_attendance_summary",
    "get_week_dates",
    "get_month_dates",
    "paginate_results",
    "mask_sensitive_data",
    "log_user_action",
    "create_error_response",
    "create_success_response",
    "is_business_day",
    "get_business_days_between",
    "validate_course_code_format",
    "parse_course_code",
    "generate_backup_filename"
]