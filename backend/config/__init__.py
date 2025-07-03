"""
Configuration Package
Contains database, settings, and university-specific configurations
"""

from .database import (
    engine,
    SessionLocal,
    Base,
    get_db,
    create_tables,
    drop_tables,
    init_database,
    check_database_connection,
    get_database_info
)
from .settings import settings
from .university_settings import UniversitySettings

__all__ = [
    "engine",
    "SessionLocal", 
    "Base",
    "get_db",
    "create_tables",
    "drop_tables",
    "init_database",
    "check_database_connection",
    "get_database_info",
    "settings",
    "UniversitySettings"
]
