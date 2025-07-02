"""
Custom Exception Classes for AttendanceAI API
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status

class AttendanceAIException(Exception):
    """Base exception class for AttendanceAI"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

class AuthenticationError(AttendanceAIException):
    """Authentication related errors"""
    pass

class AuthorizationError(AttendanceAIException):
    """Authorization/permission related errors"""
    pass

class ValidationError(AttendanceAIException):
    """Data validation errors"""
    pass

class UserNotFoundError(AttendanceAIException):
    """User not found error"""
    pass

class AttendanceError(AttendanceAIException):
    """Attendance operation errors"""
    pass

class FaceRecognitionError(AttendanceAIException):
    """Face recognition related errors"""
    pass

class DatabaseError(AttendanceAIException):
    """Database operation errors"""
    pass

class FileUploadError(AttendanceAIException):
    """File upload related errors"""
    pass

class EmailError(AttendanceAIException):
    """Email service errors"""
    pass

class ConfigurationError(AttendanceAIException):
    """Configuration related errors"""
    pass

# HTTP Exception mappers
def map_to_http_exception(exc: AttendanceAIException) -> HTTPException:
    """Map custom exceptions to HTTP exceptions"""
    
    error_mappings = {
        AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        AuthorizationError: status.HTTP_403_FORBIDDEN,
        UserNotFoundError: status.HTTP_404_NOT_FOUND,
        ValidationError: status.HTTP_400_BAD_REQUEST,
        AttendanceError: status.HTTP_400_BAD_REQUEST,
        FaceRecognitionError: status.HTTP_400_BAD_REQUEST,
        FileUploadError: status.HTTP_400_BAD_REQUEST,
        DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        EmailError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ConfigurationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    
    status_code = error_mappings.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return HTTPException(
        status_code=status_code,
        detail={
            "message": exc.message,
            "error_code": exc.error_code,
            "details": exc.details
        }
    )

# Specific exception classes with predefined messages
class InvalidCredentialsError(AuthenticationError):
    """Invalid login credentials"""
    
    def __init__(self):
        super().__init__(
            message="Invalid email or password",
            error_code="INVALID_CREDENTIALS"
        )

class TokenExpiredError(AuthenticationError):
    """Expired authentication token"""
    
    def __init__(self):
        super().__init__(
            message="Authentication token has expired",
            error_code="TOKEN_EXPIRED"
        )

class InsufficientPermissionsError(AuthorizationError):
    """Insufficient permissions for operation"""
    
    def __init__(self, required_permission: str = None):
        message = "Insufficient permissions to perform this action"
        if required_permission:
            message += f". Required permission: {required_permission}"
        
        super().__init__(
            message=message,
            error_code="INSUFFICIENT_PERMISSIONS",
            details={"required_permission": required_permission}
        )

class DuplicateEmailError(ValidationError):
    """Email already exists"""
    
    def __init__(self, email: str):
        super().__init__(
            message=f"Email address '{email}' is already registered",
            error_code="DUPLICATE_EMAIL",
            details={"email": email}
        )

class DuplicateEmployeeIdError(ValidationError):
    """Employee ID already exists"""
    
    def __init__(self, employee_id: str):
        super().__init__(
            message=f"Employee ID '{employee_id}' already exists",
            error_code="DUPLICATE_EMPLOYEE_ID",
            details={"employee_id": employee_id}
        )

class AlreadyCheckedInError(AttendanceError):
    """User already checked in today"""
    
    def __init__(self):
        super().__init__(
            message="You have already checked in today",
            error_code="ALREADY_CHECKED_IN"
        )

class NotCheckedInError(AttendanceError):
    """User not checked in"""
    
    def __init__(self):
        super().__init__(
            message="You must check in before you can check out",
            error_code="NOT_CHECKED_IN"
        )

class AlreadyCheckedOutError(AttendanceError):
    """User already checked out today"""
    
    def __init__(self):
        super().__init__(
            message="You have already checked out today",
            error_code="ALREADY_CHECKED_OUT"
        )

class FaceNotDetectedError(FaceRecognitionError):
    """No face detected in image"""
    
    def __init__(self):
        super().__init__(
            message="No face detected in the uploaded image",
            error_code="FACE_NOT_DETECTED"
        )

class MultipleFacesDetectedError(FaceRecognitionError):
    """Multiple faces detected in image"""
    
    def __init__(self, face_count: int):
        super().__init__(
            message=f"Multiple faces detected ({face_count}). Please ensure only one person is in the image",
            error_code="MULTIPLE_FACES_DETECTED",
            details={"face_count": face_count}
        )

class FaceNotRecognizedError(FaceRecognitionError):
    """Face not recognized"""
    
    def __init__(self, confidence: float = None):
        message = "Face not recognized. Please try again or contact administrator"
        details = {}
        
        if confidence is not None:
            details["confidence"] = confidence
            message += f" (Confidence: {confidence:.2f})"
        
        super().__init__(
            message=message,
            error_code="FACE_NOT_RECOGNIZED",
            details=details
        )

class LowFaceQualityError(FaceRecognitionError):
    """Face image quality too low"""
    
    def __init__(self, quality_score: float = None):
        message = "Face image quality is too low. Please provide a clearer image"
        details = {}
        
        if quality_score is not None:
            details["quality_score"] = quality_score
        
        super().__init__(
            message=message,
            error_code="LOW_FACE_QUALITY",
            details=details
        )

class InvalidFileTypeError(FileUploadError):
    """Invalid file type uploaded"""
    
    def __init__(self, file_type: str, allowed_types: list):
        super().__init__(
            message=f"Invalid file type '{file_type}'. Allowed types: {', '.join(allowed_types)}",
            error_code="INVALID_FILE_TYPE",
            details={
                "uploaded_type": file_type,
                "allowed_types": allowed_types
            }
        )

class FileSizeExceededError(FileUploadError):
    """File size exceeds limit"""
    
    def __init__(self, file_size: int, max_size: int):
        super().__init__(
            message=f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)",
            error_code="FILE_SIZE_EXCEEDED",
            details={
                "file_size": file_size,
                "max_size": max_size
            }
        )

class DatabaseConnectionError(DatabaseError):
    """Database connection failed"""
    
    def __init__(self):
        super().__init__(
            message="Unable to connect to database. Please try again later",
            error_code="DATABASE_CONNECTION_ERROR"
        )

class RecordNotFoundError(DatabaseError):
    """Database record not found"""
    
    def __init__(self, resource_type: str, resource_id: str = None):
        message = f"{resource_type} not found"
        if resource_id:
            message += f" with ID: {resource_id}"
        
        super().__init__(
            message=message,
            error_code="RECORD_NOT_FOUND",
            details={
                "resource_type": resource_type,
                "resource_id": resource_id
            }
        )

class LeaveRequestError(AttendanceAIException):
    """Leave request related errors"""
    pass

class InsufficientLeaveBalanceError(LeaveRequestError):
    """Insufficient leave balance"""
    
    def __init__(self, requested_days: int, available_days: int):
        super().__init__(
            message=f"Insufficient leave balance. Requested: {requested_days} days, Available: {available_days} days",
            error_code="INSUFFICIENT_LEAVE_BALANCE",
            details={
                "requested_days": requested_days,
                "available_days": available_days
            }
        )

class LeaveRequestNotFoundError(LeaveRequestError):
    """Leave request not found"""
    
    def __init__(self, request_id: int):
        super().__init__(
            message=f"Leave request with ID {request_id} not found",
            error_code="LEAVE_REQUEST_NOT_FOUND",
            details={"request_id": request_id}
        )

class LeaveRequestAlreadyProcessedError(LeaveRequestError):
    """Leave request already processed"""
    
    def __init__(self, current_status: str):
        super().__init__(
            message=f"Leave request has already been {current_status}",
            error_code="LEAVE_REQUEST_ALREADY_PROCESSED",
            details={"current_status": current_status}
        )

class InvalidLeaveDateError(LeaveRequestError):
    """Invalid leave dates"""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"Invalid leave dates: {reason}",
            error_code="INVALID_LEAVE_DATE",
            details={"reason": reason}
        )

# Rate limiting exceptions
class RateLimitExceededError(AttendanceAIException):
    """Rate limit exceeded"""
    
    def __init__(self, retry_after: int = None):
        message = "Rate limit exceeded. Please try again later"
        details = {}
        
        if retry_after:
            details["retry_after"] = retry_after
            message += f" (Retry after {retry_after} seconds)"
        
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details
        )

# External service exceptions
class ExternalServiceError(AttendanceAIException):
    """External service errors"""
    pass

class SMTPServiceError(ExternalServiceError):
    """SMTP service errors"""
    
    def __init__(self, details: str = None):
        message = "Email service is currently unavailable"
        if details:
            message += f": {details}"
        
        super().__init__(
            message=message,
            error_code="SMTP_SERVICE_ERROR",
            details={"service_details": details}
        )

class ModelNotLoadedError(FaceRecognitionError):
    """Face recognition model not loaded"""
    
    def __init__(self):
        super().__init__(
            message="Face recognition model is not loaded. Please contact administrator",
            error_code="MODEL_NOT_LOADED"
        )

# Convenience functions for raising common exceptions
def raise_authentication_error(message: str = None):
    """Raise authentication error"""
    if not message:
        raise InvalidCredentialsError()
    raise AuthenticationError(message)

def raise_authorization_error(required_permission: str = None):
    """Raise authorization error"""
    raise InsufficientPermissionsError(required_permission)

def raise_validation_error(message: str, field: str = None):
    """Raise validation error"""
    details = {"field": field} if field else {}
    raise ValidationError(message, details=details)

def raise_not_found_error(resource_type: str, resource_id: str = None):
    """Raise not found error"""
    raise RecordNotFoundError(resource_type, resource_id)