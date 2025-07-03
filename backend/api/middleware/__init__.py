"""
Middleware Package
"""

from .cors import setup_cors
from .auth import AuthMiddleware
from .logging import setup_logging

def setup_middleware(app):
    """Setup all middleware"""
    setup_cors(app)
    setup_logging(app)
    # Add auth middleware if needed
    
__all__ = ["setup_middleware", "setup_cors", "AuthMiddleware", "setup_logging"]
