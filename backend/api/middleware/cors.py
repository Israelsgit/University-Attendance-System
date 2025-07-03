"""
CORS Middleware Configuration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings

def setup_cors(app: FastAPI):
    """Setup CORS middleware"""
    
    print("CORS ALLOWED_ORIGINS:", settings.ALLOWED_ORIGINS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Request-ID",
        ],
        expose_headers=["X-Request-ID"],
    )
