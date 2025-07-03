"""
Analytics Routes for University System
Handles attendance analytics, reports, and dashboard data
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, extract
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import logging
import calendar

from config.database import get_db
from api.models.user import User, UserRole
from api.models.course import Course
from api.models.attendance import AttendanceRecord
from api.models.class_session import ClassSession
from api.models.enrollment import Enrollment
from api.schemas.common import SuccessResponse
from api.utils.security import get_current_user, get_current_lecturer, get_current_admin
from services.analytics_service import analytics_service
from services.attendance_service import attendance_service

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard analytics data based on user role"""
    try:
        if current_user.role == UserRole.ADMIN:
            # Admin gets university-wide analytics
            return await get_admin_dashboard(current_user, db)
        elif current_user.role == UserRole.LECTURER:
            # Lecturer gets their courses analytics
            return await get_lecturer_dashboard(current_user, db)
        elif current_user.role == UserRole.STUDENT:
            # Student gets their personal analytics
            return await get_student_dashboard(current_user, db)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid user role"
            )
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard data"
        )

async def get_admin_dashboard(current_user: User, db: Session):
    """Get admin dashboard data"""
    
    # Get university overview
    overview = analytics_service.get_university_overview(db)
    
    # Get recent alerts
    alerts = attendance_service.get_attendance_alerts(db=db)
    
    return {
        "user_role": "admin",
        "overview": overview,
        "alerts": alerts,
        "generated_at": datetime.now().isoformat()
    }

async def get_lecturer_dashboard(current_user: User, db: Session):
    """Get lecturer dashboard data"""
    
    # Get lecturer's courses
    courses = db.query(Course).filter(
        and_(
            Course.lecturer_id == current_user.id,
            Course.is_active == True
        )
    ).all()
    
    # Get analytics for each course
    course_analytics = []
    total_students = 0
    total_sessions = 0
    
    for course in courses:
        analytics = attendance_service.get_course_attendance_analytics(course.id, db=db)
        course_analytics.append(analytics)
        total_students += analytics["summary"]["total_students"]
        total_sessions += analytics["summary"]["total_sessions"]
    
    # Get lecturer's alerts
    alerts = attendance_service.get_attendance_alerts(lecturer_id=current_user.id, db=db)
    
    # Calculate overall statistics
    overall_rate = 0
    if course_analytics:
        overall_rate = sum(c["summary"]["overall_attendance_rate"] for c in course_analytics) / len(course_analytics)
    
    return {
        "user_role": "lecturer",
        "summary": {
            "total_courses": len(courses),
            "total_students": total_students,
            "total_sessions": total_sessions,
            "overall_attendance_rate": round(overall_rate, 2)
        },
        "courses": course_analytics,
        "alerts": alerts,
        "generated_at": datetime.now().isoformat()
    }

async def get_student_dashboard(current_user: User, db: Session):
    """Get student dashboard data"""
    
    # Get student's attendance summary
    summary = attendance_service.get_student_attendance_summary(current_user.id, db=db)
    
    return {
        "user_role": "student",
        "summary": summary,
        "generated_at": datetime.now().isoformat()
    }

@router.get("/course/{course_id}")
async def get_course_analytics(
    course_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_lecturer: User = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Get detailed analytics for a specific course"""
    
    # Verify lecturer owns the course (unless admin)
    if current_lecturer.role != UserRole.ADMIN:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course or course.lecturer_id != current_lecturer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view analytics for your own courses"
            )
    
    try:
        analytics = attendance_service.get_course_attendance_analytics(
            course_id=course_id,
            start_date=start_date,
            end_date=end_date,
            db=db
        )
        return analytics
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/student/{student_id}")
async def get_student_analytics(
    student_id: int,
    course_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_lecturer: User = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Get analytics for a specific student"""
    
    try:
        summary = attendance_service.get_student_attendance_summary(
            student_id=student_id,
            course_id=course_id,
            start_date=start_date,
            end_date=end_date,
            db=db
        )
        return summary
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/department/{department}")
async def get_department_analytics(
    department: str,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get analytics for a department (admin only)"""
    
    try:
        # Get students in department
        students = db.query(User).filter(
            and_(
                User.department == department,
                User.role == UserRole.STUDENT,
                User.is_active == True
            )
        ).all()
        
        # Get courses in department
        courses = db.query(Course).join(User).filter(
            and_(
                User.department == department,
                User.role == UserRole.LECTURER,
                Course.is_active == True
            )
        ).all()
        
        # Calculate department statistics
        total_students = len(students)
        total_courses = len(courses)
        
        # Get attendance records for department students
        attendance_records = db.query(AttendanceRecord).join(User).filter(
            and_(
                User.department == department,
                User.role == UserRole.STUDENT
            )
        ).count()
        
        # Get total possible attendance
        total_sessions = db.query(ClassSession).join(Course).join(User).filter(
            and_(
                User.department == department,
                User.role == UserRole.LECTURER
            )
        ).count()
        
        expected_attendance = total_sessions * total_students
        attendance_rate = (attendance_records / expected_attendance * 100) if expected_attendance > 0 else 0
        
        return {
            "department": department,
            "summary": {
                "total_students": total_students,
                "total_courses": total_courses,
                "total_sessions": total_sessions,
                "attendance_records": attendance_records,
                "attendance_rate": round(attendance_rate, 2)
            },
            "students": [student.to_dict() for student in students[:10]],  # Limit for performance
            "courses": [course.to_dict() for course in courses]
        }
        
    except Exception as e:
        logger.error(f"Error getting department analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get department analytics"
        )

@router.get("/alerts")
async def get_attendance_alerts(
    current_lecturer: User = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Get attendance alerts"""
    
    try:
        lecturer_id = current_lecturer.id if current_lecturer.role != UserRole.ADMIN else None
        alerts = attendance_service.get_attendance_alerts(lecturer_id=lecturer_id, db=db)
        return alerts
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get alerts"
        )

@router.get("/reports/attendance")
async def generate_attendance_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    course_id: Optional[int] = Query(None),
    department: Optional[str] = Query(None),
    format: str = Query("json", regex="^(json|csv)$"),
    current_lecturer: User = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Generate attendance report"""
    
    try:
        # Build query based on parameters
        query = db.query(AttendanceRecord).filter(
            and_(
                func.date(AttendanceRecord.marked_at) >= start_date,
                func.date(AttendanceRecord.marked_at) <= end_date
            )
        )
        
        if course_id:
            query = query.filter(AttendanceRecord.course_id == course_id)
        
        if department:
            query = query.join(User).filter(User.department == department)
        
        # For non-admin lecturers, only show their courses
        if current_lecturer.role != UserRole.ADMIN:
            query = query.join(Course).filter(Course.lecturer_id == current_lecturer.id)
        
        records = query.all()
        
        # Format response
        report_data = []
        for record in records:
            report_data.append({
                "date": record.marked_at.date().isoformat(),
                "time": record.marked_at.time().isoformat(),
                "student_name": record.student.full_name,
                "student_id": record.student.get_identifier(),
                "course_code": record.course.course_code,
                "course_title": record.course.course_title,
                "status": record.status,
                "confidence": record.face_confidence,
                "method": record.recognition_method
            })
        
        if format == "csv":
            # TODO: Implement CSV export
            return {"message": "CSV export not yet implemented"}
        
        return {
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "filters": {
                "course_id": course_id,
                "department": department
            },
            "total_records": len(report_data),
            "data": report_data,
            "generated_at": datetime.now().isoformat(),
            "generated_by": current_lecturer.full_name
        }
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report"
        )