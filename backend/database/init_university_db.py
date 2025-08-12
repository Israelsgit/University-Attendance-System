"""
Database Initialization Script for University Attendance System
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json
import logging

from config.database import Base, get_db
from config.settings import settings
from config.university_settings import UniversitySettings
from api.models.user import User, UserRole, StudentLevel
from api.models.course import Course
from api.models.enrollment import Enrollment
from api.models.class_session import ClassSession
from api.models.attendance import AttendanceRecord
from api.utils.security import get_password_hash

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    """Create database and tables"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        return engine
    except Exception as e:
        logger.error(f"❌ Error creating database: {e}")
        raise

def create_sample_data(engine):
    """Create sample data for the university system"""
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).count() > 0:
            logger.info("Sample data already exists, skipping creation")
            return
        
        # Create Sample Lecturers
        lecturers_data = [
            {
                "full_name": "Dr. John Adebayo",
                "email": f"j.adebayo@{UniversitySettings.UNIVERSITY_EMAIL_DOMAIN}",
                "staff_id": UniversitySettings.generate_staff_id(department_code="CSC"),
                "college": UniversitySettings.COLLEGES[0],
                "department": UniversitySettings.get_department_by_college(UniversitySettings.COLLEGES[0])[0],
                "phone": "+234-803-123-4567"
            },
            {
                "full_name": "Prof. Sarah Okonkwo",
                "email": f"s.okonkwo@{UniversitySettings.UNIVERSITY_EMAIL_DOMAIN}",
                "staff_id": UniversitySettings.generate_staff_id(department_code="CSC"),
                "college": UniversitySettings.COLLEGES[0],
                "department": UniversitySettings.get_department_by_college(UniversitySettings.COLLEGES[0])[0],
                "phone": "+234-805-987-6543"
            },
            {
                "full_name": "Dr. Michael Oluwaseun",
                "email": f"m.oluwaseun@{UniversitySettings.UNIVERSITY_EMAIL_DOMAIN}",
                "staff_id": UniversitySettings.generate_staff_id(department_code="CSC"),
                "college": UniversitySettings.COLLEGES[0],
                "department": UniversitySettings.get_department_by_college(UniversitySettings.COLLEGES[0])[0],
                "phone": "+234-807-111-2222"
            }
        ]
        
        lecturers = []
        for lecturer_data in lecturers_data:
            lecturer = User(
                **lecturer_data,
                hashed_password=get_password_hash("lecturer123"),
                university=UniversitySettings.UNIVERSITY_NAME,
                role=UserRole.LECTURER,
                employment_date=datetime.now() - timedelta(days=365),
                is_active=True,
                is_verified=True,
                is_face_registered=True
            )
            db.add(lecturer)
            lecturers.append(lecturer)
        
        db.commit()
        
        # Create Sample Courses
        courses_data = [
            {
                "course_code": "CSC 438",
                "course_title": "Web Programming",
                "course_unit": 3,
                "semester": UniversitySettings.CURRENT_SEMESTER,
                "academic_session": UniversitySettings.CURRENT_SESSION,
                "level": UniversitySettings.STUDENT_LEVELS[3],
                "class_days": "Monday,Wednesday,Friday",
                "class_time_start": "08:00",
                "class_time_end": "10:00",
                "classroom": "Lab A",
                "lecturer_id": lecturers[0].id,
                "description": "Introduction to web development using modern frameworks",
                "max_students": 50
            },
            {
                "course_code": "CSC 442",
                "course_title": "Artificial Intelligence",
                "course_unit": 3,
                "semester": UniversitySettings.CURRENT_SEMESTER,
                "academic_session": UniversitySettings.CURRENT_SESSION,
                "level": UniversitySettings.STUDENT_LEVELS[3],
                "class_days": "Tuesday,Thursday",
                "class_time_start": "10:00",
                "class_time_end": "12:00",
                "classroom": "LT1",
                "lecturer_id": lecturers[1].id,
                "description": "Fundamentals of AI and machine learning",
                "max_students": 60
            },
            {
                "course_code": "CSC 406",
                "course_title": "Software Engineering",
                "course_unit": 3,
                "semester": UniversitySettings.CURRENT_SEMESTER,
                "academic_session": UniversitySettings.CURRENT_SESSION,
                "level": UniversitySettings.STUDENT_LEVELS[3],
                "class_days": "Monday,Thursday",
                "class_time_start": "14:00",
                "class_time_end": "16:00",
                "classroom": "LT2",
                "lecturer_id": lecturers[2].id,
                "description": "Software development methodologies and best practices",
                "max_students": 45
            },
            {
                "course_code": "CSC 201",
                "course_title": "Data Structures and Algorithms",
                "course_unit": 4,
                "semester": UniversitySettings.CURRENT_SEMESTER,
                "academic_session": UniversitySettings.CURRENT_SESSION,
                "level": UniversitySettings.STUDENT_LEVELS[1],
                "class_days": "Tuesday,Wednesday,Friday",
                "class_time_start": "08:00",
                "class_time_end": "10:00",
                "classroom": "Lab B",
                "lecturer_id": lecturers[0].id,
                "description": "Fundamental data structures and algorithmic thinking",
                "max_students": 80
            },
            {
                "course_code": "CSC 301",
                "course_title": "Database Management Systems",
                "course_unit": 3,
                "semester": UniversitySettings.CURRENT_SEMESTER,
                "academic_session": UniversitySettings.CURRENT_SESSION,
                "level": UniversitySettings.STUDENT_LEVELS[2],
                "class_days": "Monday,Wednesday",
                "class_time_start": "12:00",
                "class_time_end": "14:00",
                "classroom": "Lab C",
                "lecturer_id": lecturers[1].id,
                "description": "Database design, implementation and management",
                "max_students": 55
            }
        ]
        
        courses = []
        for course_data in courses_data:
            # Parse time strings
            from datetime import time
            course_data["class_time_start"] = time.fromisoformat(course_data["class_time_start"])
            course_data["class_time_end"] = time.fromisoformat(course_data["class_time_end"])
            
            course = Course(**course_data)
            db.add(course)
            courses.append(course)
        
        db.commit()
        
        # Create Sample Students
        students_data = [
            # 400 Level Students
            {
                "full_name": "Olumide Adebisi",
                "email": f"o.adebisi@student.{UniversitySettings.UNIVERSITY_EMAIL_DOMAIN}",
                "matric_number": UniversitySettings.generate_student_id(level=StudentLevel.LEVEL_400.value, department_code="CSC", year="18"),
                "level": StudentLevel.LEVEL_400,
                "phone": "+234-802-111-1111"
            },
            {
                "full_name": "Chioma Okwu",
                "email": f"c.okwu@student.{UniversitySettings.UNIVERSITY_EMAIL_DOMAIN}",
                "matric_number": UniversitySettings.generate_student_id(level=StudentLevel.LEVEL_400.value, department_code="CSC", year="18"),
                "level": StudentLevel.LEVEL_400,
                "phone": "+234-803-222-2222"
            },
            {
                "full_name": "Ibrahim Musa",
                "email": f"i.musa@student.{UniversitySettings.UNIVERSITY_EMAIL_DOMAIN}",
                "matric_number": UniversitySettings.generate_student_id(level=StudentLevel.LEVEL_400.value, department_code="CSC", year="18"),
                "level": StudentLevel.LEVEL_400,
                "phone": "+234-804-333-3333"
            },
            {
                "full_name": "Blessing Edet",
                "email": f"b.edet@student.{UniversitySettings.UNIVERSITY_EMAIL_DOMAIN}",
                "matric_number": UniversitySettings.generate_student_id(level=StudentLevel.LEVEL_400.value, department_code="CSC", year="18"),
                "level": StudentLevel.LEVEL_400,
                "phone": "+234-805-444-4444"
            },
            {
                "full_name": "Emeka Nwosu",
                "email": f"e.nwosu@student.{UniversitySettings.UNIVERSITY_EMAIL_DOMAIN}",
                "matric_number": UniversitySettings.generate_student_id(level=StudentLevel.LEVEL_400.value, department_code="CSC", year="18"),
                "level": StudentLevel.LEVEL_400,
                "phone": "+234-806-555-5555"
            },
            # 300 Level Students
            {
                "full_name": "Fatima Hassan",
                "email": f"f.hassan@student.{UniversitySettings.UNIVERSITY_EMAIL_DOMAIN}",
                "matric_number": UniversitySettings.generate_student_id(level=StudentLevel.LEVEL_300.value, department_code="CSC", year="19"),
                "level": StudentLevel.LEVEL_300,
                "phone": "+234-807-666-6666"
            },
            {
                "full_name": "David Okafor",
                "email": f"d.okafor@student.{UniversitySettings.UNIVERSITY_EMAIL_DOMAIN}",
                "matric_number": UniversitySettings.generate_student_id(level=StudentLevel.LEVEL_300.value, department_code="CSC", year="19"),
                "level": StudentLevel.LEVEL_300,
                "phone": "+234-808-777-7777"
            },
            # 200 Level Students
            {
                "full_name": "Grace Alozie",
                "email": f"g.alozie@student.{UniversitySettings.UNIVERSITY_EMAIL_DOMAIN}",
                "matric_number": UniversitySettings.generate_student_id(level=StudentLevel.LEVEL_200.value, department_code="CSC", year="20"),
                "level": StudentLevel.LEVEL_200,
                "phone": "+234-809-888-8888"
            },
            {
                "full_name": "Samuel Adamu",
                "email": f"s.adamu@student.{UniversitySettings.UNIVERSITY_EMAIL_DOMAIN}",
                "matric_number": UniversitySettings.generate_student_id(level=StudentLevel.LEVEL_200.value, department_code="CSC", year="20"),
                "level": StudentLevel.LEVEL_200,
                "phone": "+234-810-999-9999"
            },
            {
                "full_name": "Aminat Balogun",
                "email": f"a.balogun@student.{UniversitySettings.UNIVERSITY_EMAIL_DOMAIN}",
                "matric_number": UniversitySettings.generate_student_id(level=StudentLevel.LEVEL_200.value, department_code="CSC", year="20"),
                "level": StudentLevel.LEVEL_200,
                "phone": "+234-811-000-0000"
            }
        ]
        
        students = []
        for student_data in students_data:
            student = User(
                **student_data,
                hashed_password=get_password_hash("student123"),
                university=UniversitySettings.UNIVERSITY_NAME,
                college=UniversitySettings.COLLEGES[0],
                department=UniversitySettings.get_department_by_college(UniversitySettings.COLLEGES[0])[0],
                programme=UniversitySettings.get_department_by_college(UniversitySettings.COLLEGES[0])[0],
                role=UserRole.STUDENT,
                admission_date=datetime.now() - timedelta(days=int(student_data["level"].value) * 365 / 100),
                is_active=True,
                is_verified=False,  # Students need to register face
                is_face_registered=False
            )
            db.add(student)
            students.append(student)
        
        db.commit()
        
        # Create Enrollments
        # Enroll 400 level students in 400 level courses
        level_400_students = [s for s in students if s.level == StudentLevel.LEVEL_400]
        level_400_courses = [c for c in courses if c.level == UniversitySettings.STUDENT_LEVELS[3]]
        
        for student in level_400_students:
            for course in level_400_courses:
                enrollment = Enrollment(
                    student_id=student.id,
                    course_id=course.id,
                    enrollment_status="active"
                )
                db.add(enrollment)
        
        # Enroll 300 level students in 300 level courses
        level_300_students = [s for s in students if s.level == StudentLevel.LEVEL_300]
        level_300_courses = [c for c in courses if c.level == UniversitySettings.STUDENT_LEVELS[2]]
        
        for student in level_300_students:
            for course in level_300_courses:
                enrollment = Enrollment(
                    student_id=student.id,
                    course_id=course.id,
                    enrollment_status="active"
                )
                db.add(enrollment)
        
        # Enroll 200 level students in 200 level courses
        level_200_students = [s for s in students if s.level == StudentLevel.LEVEL_200]
        level_200_courses = [c for c in courses if c.level == UniversitySettings.STUDENT_LEVELS[1]]
        
        for student in level_200_students:
            for course in level_200_courses:
                enrollment = Enrollment(
                    student_id=student.id,
                    course_id=course.id,
                    enrollment_status="active"
                )
                db.add(enrollment)
        
        db.commit()
        
        # Create Sample Class Sessions and Attendance Records
        import random
        from datetime import date, timedelta
        
        # Create sessions for the past 4 weeks
        for week in range(4):
            week_start = date.today() - timedelta(weeks=week+1)
            
            for course in courses:
                if course.class_days:
                    days = course.class_days.split(",")
                    for day_name in days:
                        # Map day names to weekday numbers
                        day_mapping = {
                            "Monday": 0, "Tuesday": 1, "Wednesday": 2,
                            "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
                        }
                        
                        if day_name in day_mapping:
                            # Find the date for this day in the week
                            days_ahead = day_mapping[day_name] - week_start.weekday()
                            if days_ahead < 0:
                                days_ahead += 7
                            session_date = week_start + timedelta(days=days_ahead)
                            
                            # Create class session
                            session = ClassSession(
                                course_id=course.id,
                                session_date=datetime.combine(session_date, course.class_time_start),
                                session_topic=f"Week {5-week} - {course.course_title}",
                                session_type="lecture",
                                duration_minutes=120,
                                is_active=False,
                                is_completed=True,
                                attendance_marked_by=course.lecturer_id
                            )
                            db.add(session)
                            db.commit()
                            db.refresh(session)
                            
                            # Create attendance records for enrolled students
                            enrollments = db.query(Enrollment).filter(
                                Enrollment.course_id == course.id
                            ).all()
                            
                            for enrollment in enrollments:
                                # 85% chance of attendance, with some late arrivals
                                if random.random() < 0.85:
                                    status = "late" if random.random() < 0.15 else "present"
                                    
                                    attendance = AttendanceRecord(
                                        student_id=enrollment.student_id,
                                        course_id=course.id,
                                        session_id=session.id,
                                        marked_at=session.session_date + timedelta(minutes=random.randint(0, 20)),
                                        status=status,
                                        face_confidence=random.uniform(0.85, 0.98),
                                        recognition_method="face_recognition",
                                        location=course.classroom
                                    )
                                    db.add(attendance)
        
        db.commit()
        
        logger.info("✅ Sample data created successfully")
        logger.info(f"📧 Lecturer login: j.adebayo@{UniversitySettings.UNIVERSITY_EMAIL_DOMAIN} / lecturer123")
        logger.info(f"📧 Student login: o.adebisi@student.{UniversitySettings.UNIVERSITY_EMAIL_DOMAIN} / student123")
        
    except Exception as e:
        logger.error(f"❌ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main initialization function"""
    try:
        logger.info("🚀 Initializing University Attendance System Database...")
        
        # Create database and tables
        engine = create_database()
        
        # Create sample data
        create_sample_data(engine)
        
        logger.info("✅ Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    main()