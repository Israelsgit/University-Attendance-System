"""
Enhanced Attendance Routes for University System
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import datetime, date, timedelta
from typing import Optional, List
import logging

from config.database import get_db
from api.models.user import User, UserRole
from api.models.course import Course
from api.models.class_session import ClassSession
from api.models.attendance import AttendanceRecord
from api.models.enrollment import Enrollment
from api.schemas.attendance import (
    AttendanceResponse, AttendanceCreate, AttendanceMarkingResponse,
    StudentAttendanceStats, CourseAttendanceStats, AttendanceAnalytics
)
from api.utils.security import get_current_user, get_current_lecturer
from services.face_recognition import face_recognition_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/mark/{session_id}")
async def mark_attendance_via_face(
    session_id: int,
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark attendance for a class session using face recognition"""
    
    # Get class session
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class session not found"
        )
    
    # Check if session is active
    if not session.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attendance marking is not active for this session"
        )
    
    # For students: Check if enrolled in the course
    if current_user.role == UserRole.STUDENT:
        enrollment = db.query(Enrollment).filter(
            and_(
                Enrollment.student_id == current_user.id,
                Enrollment.course_id == session.course_id,
                Enrollment.enrollment_status == "active"
            )
        ).first()
        
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not enrolled in this course"
            )
        
        # Check if already marked attendance
        existing_attendance = db.query(AttendanceRecord).filter(
            and_(
                AttendanceRecord.student_id == current_user.id,
                AttendanceRecord.session_id == session_id
            )
        ).first()
        
        if existing_attendance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attendance already marked for this session"
            )
        
        # Check if face is registered
        if not current_user.is_face_registered:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Face not registered. Please see your lecturer to register your face."
            )
        
        student_to_mark = current_user
    
    # For lecturers: They can mark attendance for any student in their course
    elif current_user.role == UserRole.LECTURER:
        if session.course.lecturer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only mark attendance for your own courses"
            )
        
        # Process image to identify student
        image_data = await image.read()
        result = face_recognition_service.identify_student(image_data)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        if not result["recognized"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not recognized. Student may need to register their face."
            )
        
        # Get identified student
        student_to_mark = db.query(User).filter(User.id == result["user_id"]).first()
        if not student_to_mark:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Identified student not found in database"
            )
        
        # Check if student is enrolled
        enrollment = db.query(Enrollment).filter(
            and_(
                Enrollment.student_id == student_to_mark.id,
                Enrollment.course_id == session.course_id,
                Enrollment.enrollment_status == "active"
            )
        ).first()
        
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student {student_to_mark.full_name} is not enrolled in this course"
            )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students and lecturers can mark attendance"
        )
    
    # Process face recognition for verification
    if current_user.role == UserRole.STUDENT:
        image_data = await image.read()
        result = face_recognition_service.verify_face_against_user(
            image_data, current_user.face_encoding
        )
        
        if not result["success"] or not result["is_match"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Face verification failed"
            )
        
        confidence = result["confidence"]
    else:
        confidence = result["confidence"]
    
    # Determine attendance status based on time
    now = datetime.now()
    session_start_time = session.session_date
    late_threshold = session_start_time + timedelta(minutes=15)  # 15 minutes late threshold
    
    if now <= late_threshold:
        attendance_status = "present"
    else:
        attendance_status = "late"
    
    # Create attendance record
    attendance = AttendanceRecord(
        student_id=student_to_mark.id,
        course_id=session.course_id,
        session_id=session_id,
        marked_at=now,
        status=attendance_status,
        face_confidence=confidence,
        recognition_method="face_recognition",
        marked_by_lecturer=current_user.id if current_user.role == UserRole.LECTURER else None
    )
    
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    logger.info(f"✅ Attendance marked: {student_to_mark.full_name} - {attendance_status}")
    
    return {
        "success": True,
        "message": f"Attendance marked successfully for {student_to_mark.full_name}",
        "student_name": student_to_mark.full_name,
        "matric_number": student_to_mark.matric_number,
        "status": attendance_status,
        "confidence": confidence,
        "marked_at": now.isoformat()
    }

@router.get("/course/{course_id}/analytics")
async def get_course_attendance_analytics(
    course_id: int,
    current_lecturer: User = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Get attendance analytics for a course (lecturer only)"""
    
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
            detail="You can only view analytics for your own courses"
        )
    
    # Get enrolled students
    enrollments = db.query(Enrollment).filter(
        and_(
            Enrollment.course_id == course_id,
            Enrollment.enrollment_status == "active"
        )
    ).all()
    
    total_students = len(enrollments)
    
    # Get all sessions for the course
    sessions = db.query(ClassSession).filter(ClassSession.course_id == course_id).all()
    total_sessions = len(sessions)
    
    # Get all attendance records for the course
    attendance_records = db.query(AttendanceRecord).filter(
        AttendanceRecord.course_id == course_id
    ).all()
    
    # Calculate statistics
    total_attendances = len(attendance_records)
    present_count = len([a for a in attendance_records if a.status == "present"])
    late_count = len([a for a in attendance_records if a.status == "late"])
    absent_count = (total_students * total_sessions) - total_attendances
    
    # Calculate attendance rate
    if total_students > 0 and total_sessions > 0:
        attendance_rate = (total_attendances / (total_students * total_sessions)) * 100
    else:
        attendance_rate = 0
    
    # Student-wise statistics
    student_stats = []
    for enrollment in enrollments:
        student = enrollment.student
        student_attendances = [a for a in attendance_records if a.student_id == student.id]
        
        present = len([a for a in student_attendances if a.status == "present"])
        late = len([a for a in student_attendances if a.status == "late"])
        absent = total_sessions - len(student_attendances)
        
        rate = (len(student_attendances) / total_sessions * 100) if total_sessions > 0 else 0
        
        student_stats.append({
            "matric_number": student.matric_number,
            "student_name": student.full_name,
            "student_identifier": student.matric_number,
            "present": present,
            "late": late,
            "absent": absent,
            "attendance_rate": round(rate, 2)
        })
    
    # Session-wise statistics
    session_stats = []
    for session in sessions:
        session_attendances = [a for a in attendance_records if a.session_id == session.id]
        
        session_stats.append({
            "session_id": session.id,
            "session_date": session.session_date.isoformat(),
            "session_topic": session.session_topic,
            "attendees": len(session_attendances),
            "attendance_rate": (len(session_attendances) / total_students * 100) if total_students > 0 else 0
        })
    
    return {
        "course": course.to_dict(),
        "summary": {
            "total_students": total_students,
            "total_sessions": total_sessions,
            "total_attendances": total_attendances,
            "present_count": present_count,
            "late_count": late_count,
            "absent_count": absent_count,
            "overall_attendance_rate": round(attendance_rate, 2)
        },
        "student_statistics": student_stats,
        "session_statistics": session_stats
    }

@router.get("/student/my-attendance")
async def get_my_attendance(
    course_id: Optional[int] = Query(None),
    current_student: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get attendance records for current student"""
    
    if current_student.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    # Build query
    query = db.query(AttendanceRecord).filter(
        AttendanceRecord.student_id == current_student.id
    )
    
    if course_id:
        query = query.filter(AttendanceRecord.course_id == course_id)
    
    attendance_records = query.order_by(desc(AttendanceRecord.marked_at)).all()
    
    # Get enrolled courses for summary
    enrollments = db.query(Enrollment).filter(
        and_(
            Enrollment.student_id == current_student.id,
            Enrollment.enrollment_status == "active"
        )
    ).all()
    
    # Calculate course-wise statistics
    course_stats = []
    for enrollment in enrollments:
        course = enrollment.course
        
        # Get total sessions for this course
        total_sessions = db.query(ClassSession).filter(
            ClassSession.course_id == course.id
        ).count()
        
        # Get student's attendance for this course
        course_attendances = [a for a in attendance_records if a.course_id == course.id]
        
        present = len([a for a in course_attendances if a.status == "present"])
        late = len([a for a in course_attendances if a.status == "late"])
        absent = total_sessions - len(course_attendances)
        
        rate = (len(course_attendances) / total_sessions * 100) if total_sessions > 0 else 0
        
        course_stats.append({
            "course": course.to_dict(),
            "total_sessions": total_sessions,
            "present": present,
            "late": late,
            "absent": absent,
            "attendance_rate": round(rate, 2)
        })
    
    return {
        "student": current_student.to_dict(),
        "attendance_records": [record.to_dict() for record in attendance_records],
        "course_statistics": course_stats
    }

@router.post("/session/{session_id}/activate")
async def activate_attendance_marking(
    session_id: int,
    current_lecturer: User = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Activate attendance marking for a session (lecturer only)"""
    
    # Get session
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check if lecturer owns the course
    if session.course.lecturer_id != current_lecturer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only activate attendance for your own courses"
        )
    
    # Activate session
    session.is_active = True
    db.commit()
    
    return {"message": "Attendance marking activated for this session"}

@router.post("/session/{session_id}/deactivate")
async def deactivate_attendance_marking(
    session_id: int,
    current_lecturer: User = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Deactivate attendance marking for a session (lecturer only)"""
    
    # Get session
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check if lecturer owns the course
    if session.course.lecturer_id != current_lecturer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only deactivate attendance for your own courses"
        )
    
    # Deactivate and complete session
    session.is_active = False
    session.is_completed = True
    db.commit()
    
    return {"message": "Attendance marking deactivated and session completed"}