"""
Database Package
Contains database initialization and migration scripts
"""

from .init_university_db import main as init_university_database

__all__ = [
    "init_university_database"
]