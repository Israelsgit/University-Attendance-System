"""
University-specific Configuration Settings
"""

import os
from typing import List

class UniversitySettings:
    """University-specific settings"""
    
    # University Information
    UNIVERSITY_NAME: str = "Bowen University"
    UNIVERSITY_SHORT_NAME: str = "BU"
    UNIVERSITY_EMAIL_DOMAIN: str = "bowen.edu.ng"
    
    # Academic Structure
    COLLEGES: List[str] = [
        "College of Computing and Communication Studies",
        "College of Agriculture and Engineering Sciences", 
        "College of Health Sciences",
        "College of Social and Management Sciences",
        "College of Law",
        "College of Liberal Studies",
        "College of Environmental Sciences"
    ]
    
    SEMESTERS: List[str] = [
        "First Semester",
        "Second Semester", 
        "Rain Semester"
    ]
    
    STUDENT_LEVELS: List[str] = ["100", "200", "300", "400", "500"]
    
    # Academic Calendar
    CURRENT_SESSION: str = "2024/2025"
    CURRENT_SEMESTER: str = "First Semester"
    
    # Attendance Settings
    LATE_THRESHOLD_MINUTES: int = 15
    MINIMUM_ATTENDANCE_PERCENTAGE: float = 75.0
    
    # Face Recognition Settings
    FACE_CONFIDENCE_THRESHOLD: float = 0.85
    FACE_VERIFICATION_THRESHOLD: float = 0.80
    
    # File Upload Settings
    MAX_FACE_IMAGE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/jpg", "image/png"]
    
    # Email Settings for Notifications
    LECTURER_EMAIL_NOTIFICATIONS: bool = True
    STUDENT_EMAIL_NOTIFICATIONS: bool = True
    ADMIN_EMAIL_NOTIFICATIONS: bool = True
    
    # Department Mappings
    DEPARTMENT_MAPPINGS = {
        "College of Computing and Communication Studies": [
            "Computer Science",
            "Information Technology", 
            "Cyber Security",
            "Software Engineering",
            "Communication Arts",
            "Mass Communication"
        ],
        "College of Agriculture and Engineering Sciences": [
            "Electrical and Electronics Engineering",
            "Mechatronics Engineering",
            "Chemistry and Industrial Chemistry",
            "Food Science and Technology",
            "Mathematics and Statistics",
            "Physics and Solar Energy"
        ],
        "College of Health Sciences": [
            "Anatomy",
            "Physiotherapy",
            "Medical Laboratory Science",
            "Medicine and Surgery",
            "Nursing Science",
            "Nutrition and Dietetics",
            "Public Health"
        ],
        "College of Social and Management Sciences": [
            "Accounting & Finance",
            "Political Science",
            "Business Administration",
            "Industrial Relations & Personnel Management",
            "International Relations",
            "Sociology"
        ],
        "College of Law": [
            "Law"
        ],
        "College of Environmental Sciences": [
            "Architecture",
            "Surveying and Geoinformatics",
        ],
        "College of Liberal Studies": [
            "English Language",
            "History and International Studies",
            "Philosophy and Religious Studies",
            "Music",
            "Theatre Arts"
        ]
    }
    
    # Default Class Schedule
    DEFAULT_CLASS_DURATION: int = 60  # minutes
    CLASS_TIME_SLOTS = [
        ("08:00", "10:00"),
        ("10:00", "12:00"), 
        ("12:00", "14:00"),
        ("14:00", "16:00"),
        ("16:00", "18:00")
    ]
    
    # Attendance Analytics Settings
    ANALYTICS_CACHE_DURATION: int = 300  # 5 minutes
    GENERATE_REPORTS_ASYNC: bool = True
    
    @classmethod
    def get_department_by_college(cls, college: str) -> List[str]:
        """Get departments for a specific college"""
        return cls.DEPARTMENT_MAPPINGS.get(college, [])
    
    @classmethod
    def is_valid_email_domain(cls, email: str) -> bool:
        """Check if email domain is valid for the university"""
        return email.endswith(f"@{cls.UNIVERSITY_EMAIL_DOMAIN}") or \
               email.endswith(f"@student.{cls.UNIVERSITY_EMAIL_DOMAIN}")
    
    @classmethod
    def generate_student_id(cls, level: str, department_code: str = "CSC", year: str = None) -> str:
        """Generate student ID format"""
        if not year:
            year = str(datetime.now().year)[2:]
        return f"{cls.UNIVERSITY_SHORT_NAME}{year}{department_code}XXXX"
    
    @classmethod
    def generate_staff_id(cls, department_code: str = "CSC") -> str:
        """Generate staff ID format"""
        return f"{cls.UNIVERSITY_SHORT_NAME}/{department_code}/XXXX"