"""
API Routes Package
Contains all API endpoint definitions for the university system
"""

from . import auth, courses, attendance, users, analytics

__all__ = [
    "auth",
    "courses", 
    "attendance",
    "users",
    "analytics"
]

# Create a list of all routers for easy import in main app
def get_all_routers():
    """Return all routers for registration in main app"""
    return [
        (auth.router, "/auth", ["Authentication"]),
        (courses.router, "/courses", ["Courses"]),
        (attendance.router, "/attendance", ["Attendance"]),
        (users.router, "/users", ["Users"]),
        (analytics.router, "/analytics", ["Analytics"])
    ]