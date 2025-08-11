"""
University-specific Configuration Settings
Updated to remove admin role and match Bowen University structure
"""

import os
from typing import List
from datetime import datetime

class UniversitySettings:
    """University-specific settings"""
    
    # University Information
    UNIVERSITY_NAME: str = "Bowen University"
    UNIVERSITY_SHORT_NAME: str = "BU"
    UNIVERSITY_EMAIL_DOMAIN: str = "bowen.edu.ng"
    STUDENT_EMAIL_DOMAIN: str = "student.bowen.edu.ng"
    
    # Academic Structure - Updated to match Bowen University
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
    
    # Email Settings for Notifications (Removed admin notifications)
    LECTURER_EMAIL_NOTIFICATIONS: bool = True
    STUDENT_EMAIL_NOTIFICATIONS: bool = True
    
    # Department Mappings - Updated to match Bowen University structure
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
    
    # Department Codes for ID Generation
    DEPARTMENT_CODES = {
        "Computer Science": "CSC",
        "Information Technology": "ITF", 
        "Cyber Security": "CYB",
        "Software Engineering": "SEN",
        "Communication Arts": "CAR",
        "Mass Communication": "MCM",
        "Electrical and Electronics Engineering": "EEE",
        "Mechatronics Engineering": "MCE",
        "Chemistry and Industrial Chemistry": "CHM",
        "Food Science and Technology": "FST",
        "Mathematics and Statistics": "MTH",
        "Physics and Solar Energy": "PHY",
        "Anatomy": "ANA",
        "Physiotherapy": "PTH",
        "Medical Laboratory Science": "MLS",
        "Medicine and Surgery": "MED",
        "Nursing Science": "NUR",
        "Nutrition and Dietetics": "NTD",
        "Public Health": "PHT",
        "Accounting & Finance": "ACC",
        "Political Science": "POL",
        "Business Administration": "BUS",
        "Industrial Relations & Personnel Management": "IRP",
        "International Relations": "INR",
        "Sociology": "SOC",
        "Law": "LAW",
        "Architecture": "ARC",
        "Surveying and Geoinformatics": "SUR",
        "English Language": "ENG",
        "History and International Studies": "HIS",
        "Philosophy and Religious Studies": "PRS",
        "Music": "MUS",
        "Theatre Arts": "THA"
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
    
    # Role-based Permissions (No Admin Role)
    LECTURER_PERMISSIONS = [
        "create_course",
        "manage_course", 
        "enroll_student",
        "manage_attendance",
        "view_analytics",
        "export_data",
        "register_student_face",
        "system_administration"
    ]
    
    STUDENT_PERMISSIONS = [
        "mark_attendance",
        "view_own_attendance", 
        "register_own_face",
        "view_own_courses"
    ]
    
    @classmethod
    def get_department_by_college(cls, college: str) -> List[str]:
        """Get departments for a specific college"""
        return cls.DEPARTMENT_MAPPINGS.get(college, [])
    
    @classmethod
    def get_department_code(cls, department: str) -> str:
        """Get department code for ID generation"""
        return cls.DEPARTMENT_CODES.get(department, "GEN")
    
    @classmethod
    def is_valid_email_domain(cls, email: str) -> bool:
        """Check if email domain is valid for the university"""
        return email.endswith(f"@{cls.UNIVERSITY_EMAIL_DOMAIN}") or \
               email.endswith(f"@{cls.STUDENT_EMAIL_DOMAIN}")
    
    @classmethod
    def is_student_email(cls, email: str) -> bool:
        """Check if email is a student email"""
        return email.endswith(f"@{cls.STUDENT_EMAIL_DOMAIN}")
    
    @classmethod
    def is_staff_email(cls, email: str) -> bool:
        """Check if email is a staff email"""
        return email.endswith(f"@{cls.UNIVERSITY_EMAIL_DOMAIN}") and not cls.is_student_email(email)
    
    @classmethod
    def generate_student_id(cls, department: str, year: str = None) -> str:
        """Generate student ID format: BU/CSC/21/0001"""
        if not year:
            year = str(datetime.now().year)[2:]
        
        dept_code = cls.get_department_code(department)
        return f"{cls.UNIVERSITY_SHORT_NAME}/{dept_code}/{year}/XXXX"
    
    @classmethod
    def generate_staff_id(cls, department: str) -> str:
        """Generate staff ID format: BU/CSC/2024"""
        dept_code = cls.get_department_code(department)
        year = datetime.now().year
        return f"{cls.UNIVERSITY_SHORT_NAME}/{dept_code}/{year}"
    
    @classmethod
    def get_all_departments(cls) -> List[str]:
        """Get all departments across all colleges"""
        departments = []
        for college_depts in cls.DEPARTMENT_MAPPINGS.values():
            departments.extend(college_depts)
        return sorted(departments)
    
    @classmethod
    def validate_matric_number_format(cls, matric_number: str) -> bool:
        """Validate matriculation number format"""
        import re
        pattern = r'^BU/[A-Z]{3}/\d{2}/\d{4}$'
        return bool(re.match(pattern, matric_number.upper()))
    
    @classmethod
    def validate_staff_id_format(cls, staff_id: str) -> bool:
        """Validate staff ID format"""
        import re
        pattern = r'^BU/[A-Z]{3}/\d{4}$'
        return bool(re.match(pattern, staff_id.upper()))
    
    @classmethod
    def get_user_permissions(cls, role: str) -> List[str]:
        """Get permissions for a user role"""
        if role.lower() == "lecturer":
            return cls.LECTURER_PERMISSIONS
        elif role.lower() == "student":
            return cls.STUDENT_PERMISSIONS
        else:
            return []