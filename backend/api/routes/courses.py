"""
Course Management Routes for University System
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, time

from config.database import get_db
from api.models.user import User, UserRole
from api.models.course import Course
from api.models.enrollment import Enrollment
from api.models.class_session import ClassSession
from api.schemas.course import (
    CourseCreate, CourseUpdate, CourseResponse, 
    EnrollmentCreate, ClassSessionCreate
)
from api.utils.security import get_current_user, get_current_lecturer

router = APIRouter()

@router.post("/", response_model=CourseResponse)
async def create_course(
    course_data: CourseCreate,
    current_lecturer: User = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Create a new course (lecturer only)"""
    
    # Check if course code already exists
    if db.query(Course).filter(Course.course_code == course_data.course_code).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course code already exists"
        )
    
    # Parse class times
    class_time_start = None
    class_time_end = None
    
    if course_data.class_time_start:
        class_time_start = time.fromisoformat(course_data.class_time_start)
    if course_data.class_time_end:
        class_time_end = time.fromisoformat(course_data.class_time_end)
    
    # Create course
    course = Course(
        course_code=course_data.course_code,
        course_title=course_data.course_title,
        course_unit=course_data.course_unit,
        semester=course_data.semester,
        academic_session=course_data.academic_session,
        level=course_data.level,
        class_days=",".join(course_data.class_days) if course_data.class_days else None,
        class_time_start=class_time_start,
        class_time_end=class_time_end,
        classroom=course_data.classroom,
        lecturer_id=current_lecturer.id,
        description=course_data.description,
        prerequisites=course_data.prerequisites,
        max_students=course_data.max_students
    )
    
    db.add(course)
    db.commit()
    db.refresh(course)
    
    return {"course": course.to_dict(), "message": "Course created successfully"}

@router.get("/my-courses", response_model=List[CourseResponse])
async def get_my_courses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get courses based on user role"""
    
    if current_user.role == UserRole.LECTURER:
        # Get courses taught by lecturer
        courses = db.query(Course).filter(Course.lecturer_id == current_user.id).all()
    elif current_user.role == UserRole.STUDENT:
        # Get enrolled courses
        enrollments = db.query(Enrollment).filter(
            and_(
                Enrollment.student_id == current_user.id,
                Enrollment.enrollment_status == "active"
            )
        ).all()
        courses = [enrollment.course for enrollment in enrollments]
    else:
        # Remove admin fallback logic
        courses = []
    
    return [{"course": course.to_dict()} for course in courses]

@router.post("/{course_id}/enroll")
async def enroll_student(
    course_id: int,
    student_email: str,
    current_lecturer: User = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Enroll a student in a course (lecturer only)"""
    
    # Get course
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if lecturer owns the course
    if course.lecturer_id != current_lecturer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only enroll students in your own courses"
        )
    
    # Get student
    student = db.query(User).filter(
        and_(
            User.email == student_email,
            User.role == UserRole.STUDENT
        )
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Check if already enrolled
    existing_enrollment = db.query(Enrollment).filter(
        and_(
            Enrollment.student_id == student.id,
            Enrollment.course_id == course_id
        )
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student already enrolled in this course"
        )
    
    # Create enrollment
    enrollment = Enrollment(
        student_id=student.id,
        course_id=course_id,
        enrollment_status="active"
    )
    
    db.add(enrollment)
    db.commit()
    
    return {"message": f"Student {student.full_name} enrolled successfully"}

@router.post("/{course_id}/sessions", response_model=dict)
async def create_class_session(
    course_id: int,
    session_data: ClassSessionCreate,
    current_lecturer: User = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Create a new class session (lecturer only)"""
    
    # Get course
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if lecturer owns the course
    if course.lecturer_id != current_lecturer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create sessions for your own courses"
        )
    
    # Create class session
    session = ClassSession(
        course_id=course_id,
        session_date=session_data.session_date,
        session_topic=session_data.session_topic,
        session_type=session_data.session_type,
        duration_minutes=session_data.duration_minutes,
        notes=session_data.notes,
        attendance_marked_by=current_lecturer.id
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {"message": "Class session created successfully", "session_id": session.id}