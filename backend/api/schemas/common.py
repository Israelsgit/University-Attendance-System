"""
Common Schemas for University System
"""

from pydantic import BaseModel
from typing import Optional, Any, Dict

class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = 1
    size: int = 20
    
class PaginatedResponse(BaseModel):
    """Paginated response"""
    items: list
    total: int
    page: int
    size: int
    pages: int