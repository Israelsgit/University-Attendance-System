"""
Analytics Routes for University System
Cleaned version - Admin role removed, lecturers have full access
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
from api.utils.security import get_current_user, get_current_lecturer, get_current_student
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
        if current_user.role == UserRole.LECTURER:
            # Lecturers get full system analytics (admin privileges)
            return await get_lecturer_dashboard(current_user, db)
        elif current_user.role == UserRole.STUDENT:
            # Students get their personal analytics
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

async def get_lecturer_dashboard(current_user: User, db: Session):
    """Get lecturer dashboard data with full system analytics"""
    
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
    
    # Get system-wide stats (lecturer has admin access)
    system_stats = await get_system_overview(db)
    
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
        "system_overview": system_stats,  # Added system overview for admin access
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

async def get_system_overview(db: Session):
    """Get system-wide overview (for lecturers with admin access)"""
    
    # Total counts
    total_students = db.query(User).filter(User.role == UserRole.STUDENT).count()
    total_lecturers = db.query(User).filter(User.role == UserRole.LECTURER).count()
    total_courses = db.query(Course).filter(Course.is_active == True).count()
    total_sessions = db.query(ClassSession).count()
    
    # Active sessions today
    today = date.today()
    active_sessions = db.query(ClassSession).filter(
        ClassSession.session_date == today
    ).count()
    
    # Overall attendance rate
    overall_attendance = db.query(
        func.avg(AttendanceRecord.attendance_percentage)
    ).scalar() or 0
    
    return {
        "total_students": total_students,
        "total_lecturers": total_lecturers,
        "total_courses": total_courses,
        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
        "overall_attendance_rate": round(float(overall_attendance), 2)
    }

@router.get("/course/{course_id}")
async def get_course_analytics(
    course_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_lecturer: User = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Get detailed analytics for a specific course (lecturers only)"""
    
    # Verify lecturer owns the course
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
    """Get analytics for a specific student (lecturers only)"""
    
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

@router.get("/trends")
async def get_attendance_trends(
    period: str = Query("month", description="Period: week, month, semester"),
    course_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get attendance trends"""
    
    if current_user.role == UserRole.STUDENT:
        # Students can only see their own trends
        trends = attendance_service.get_student_attendance_trends(
            student_id=current_user.id,
            period=period,
            course_id=course_id,
            db=db
        )
    elif current_user.role == UserRole.LECTURER:
        # Lecturers can see system-wide trends
        trends = attendance_service.get_system_attendance_trends(
            period=period,
            course_id=course_id,
            lecturer_id=current_user.id,
            db=db
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role"
        )
    
    return trends

@router.get("/export/{course_id}")
async def export_course_data(
    course_id: int,
    format: str = Query("csv", description="Export format: csv, xlsx"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_lecturer: User = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Export course attendance data (lecturers only)"""
    
    # Verify lecturer owns the course
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course or course.lecturer_id != current_lecturer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only export data for your own courses"
        )
    
    try:
        export_data = attendance_service.export_course_data(
            course_id=course_id,
            format=format,
            start_date=start_date,
            end_date=end_date,
            db=db
        )
        return export_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/my-attendance")
async def get_my_attendance_analytics(
    course_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get personal attendance analytics (students only)"""
    
    try:
        analytics = attendance_service.get_student_attendance_summary(
            student_id=current_student.id,
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

@router.get("/performance-metrics")
async def get_performance_metrics(
    current_lecturer: User = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Get system performance metrics (lecturers only - admin access)"""
    
    try:
        metrics = analytics_service.get_performance_metrics(
            lecturer_id=current_lecturer.id,
            db=db
        )
        return metrics
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get performance metrics"
        )