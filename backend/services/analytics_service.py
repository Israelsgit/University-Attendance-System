"""
Enhanced Analytics Service for University System
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, extract
import pandas as pd
import numpy as np
from collections import defaultdict
import logging

from config.database import SessionLocal
from api.models.user import User, UserRole
from api.models.course import Course
from api.models.attendance import AttendanceRecord
from api.models.class_session import ClassSession
from api.models.enrollment import Enrollment

logger = logging.getLogger(__name__)

class UniversityAnalyticsService:
    """Enhanced analytics service for university attendance system"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
    
    def _get_cache_key(self, method_name: str, **kwargs) -> str:
        """Generate cache key for method and parameters"""
        return f"{method_name}_{hash(str(sorted(kwargs.items())))}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key].get('timestamp')
        if not cached_time:
            return False
        
        return (datetime.now() - cached_time).seconds < self.cache_duration
    
    def get_university_overview(self, db: Session = None) -> Dict[str, Any]:
        """Get overall university attendance statistics"""
        
        cache_key = self._get_cache_key("university_overview")
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        if not db:
            db = SessionLocal()
        
        try:
            # Total counts
            total_students = db.query(User).filter(User.role == UserRole.STUDENT).count()
            total_lecturers = db.query(User).filter(User.role == UserRole.LECTURER).count()
            total_courses = db.query(Course).filter(Course.is_active == True).count()
            total_sessions = db.query(ClassSession).count()
            
            # Active sessions today
            today = date.today()
            active_sessions_today = db.query(ClassSession).filter(
                and_(
                    func.date(ClassSession.session_date) == today,
                    ClassSession.is_active == True
                )
            ).count()
            
            # Attendance statistics
            total_attendance_records = db.query(AttendanceRecord).count()
            present_today = db.query(AttendanceRecord).filter(
                and_(
                    func.date(AttendanceRecord.marked_at) == today,
                    AttendanceRecord.status.in_(["present", "late"])
                )
            ).count()
            
            # Calculate overall attendance rate
            if total_sessions > 0 and total_students > 0:
                expected_total = total_sessions * total_students
                attendance_rate = (total_attendance_records / expected_total) * 100 if expected_total > 0 else 0
            else:
                attendance_rate = 0
            
            # Department breakdown
            department_stats = self._get_department_breakdown(db)
            
            # Recent trends (last 7 days)
            weekly_trends = self._get_weekly_trends(db)
            
            result = {
                "overview": {
                    "total_students": total_students,
                    "total_lecturers": total_lecturers,
                    "total_courses": total_courses,
                    "total_sessions": total_sessions,
                    "active_sessions_today": active_sessions_today,
                    "present_today": present_today,
                    "overall_attendance_rate": round(attendance_rate, 2)
                },
                "department_breakdown": department_stats,
                "weekly_trends": weekly_trends,
                "generated_at": datetime.now().isoformat()
            }
            
            # Cache result
            self.cache[cache_key] = {
                'data': result,
                'timestamp': datetime.now()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting university overview: {e}")
            raise
        finally:
            if not db:
                db.close()
    
    def _get_department_breakdown(self, db: Session) -> List[Dict[str, Any]]:
        """Get attendance breakdown by department"""
        
        departments = db.query(User.department, func.count(User.id)).filter(
            User.role == UserRole.STUDENT,
            User.is_active == True
        ).group_by(User.department).all()
        
        department_stats = []
        
        for dept_name, student_count in departments:
            # Get attendance for this department
            dept_attendance = db.query(AttendanceRecord).join(User).filter(
                User.department == dept_name,
                User.role == UserRole.STUDENT
            ).count()
            
            # Get total possible attendance (sessions * students)
            dept_sessions = db.query(ClassSession).join(Course).join(User).filter(
                User.department == dept_name,
                User.role == UserRole.LECTURER
            ).count()
            
            expected_attendance = dept_sessions * student_count
            attendance_rate = (dept_attendance / expected_attendance * 100) if expected_attendance > 0 else 0
            
            department_stats.append({
                "department": dept_name,
                "total_students": student_count,
                "total_sessions": dept_sessions,
                "attendance_records": dept_attendance,
                "attendance_rate": round(attendance_rate, 2)
            })
        
        return department_stats
    
    def _get_weekly_trends(self, db: Session) -> List[Dict[str, Any]]:
        """Get attendance trends for the last 7 days"""
        
        trends = []
        today = date.today()
        
        for i in range(7):
            check_date = today - timedelta(days=i)
            
            # Get attendance for this date
            day_attendance = db.query(AttendanceRecord).filter(
                func.date(AttendanceRecord.marked_at) == check_date
            ).count()
            
            # Get sessions for this date
            day_sessions = db.query(ClassSession).filter(
                func.date(ClassSession.session_date) == check_date
            ).count()
            
            trends.append({
                "date": check_date.isoformat(),
                "attendance_count": day_attendance,
                "sessions_count": day_sessions,
                "day_name": check_date.strftime("%A")
            })
        
        return trends[::-1]  # Reverse to get chronological order
    
    def get_course_detailed_analytics(
        self, 
        course_id: int, 
        db: Session = None
    ) -> Dict[str, Any]:
        """Get detailed analytics for a specific course"""
        
        if not db:
            db = SessionLocal()
        
        try:
            # Get course
            course = db.query(Course).filter(Course.id == course_id).first()
            if not course:
                raise ValueError("Course not found")
            
            # Get enrolled students
            enrollments = db.query(Enrollment).filter(
                and_(
                    Enrollment.course_id == course_id,
                    Enrollment.enrollment_status == "active"
                )
            ).all()
            
            total_students = len(enrollments)
            
            # Get all sessions
            sessions = db.query(ClassSession).filter(
                ClassSession.course_id == course_id
            ).order_by(ClassSession.session_date).all()
            
            total_sessions = len(sessions)
            
            # Get all attendance records
            attendance_records = db.query(AttendanceRecord).filter(
                AttendanceRecord.course_id == course_id
            ).all()
            
            # Calculate statistics
            present_count = len([a for a in attendance_records if a.status == "present"])
            late_count = len([a for a in attendance_records if a.status == "late"])
            total_attendances = len(attendance_records)
            
            # Expected total attendances
            expected_total = total_students * total_sessions
            absent_count = expected_total - total_attendances
            
            # Overall attendance rate
            attendance_rate = (total_attendances / expected_total * 100) if expected_total > 0 else 0
            
            # Student-wise analysis
            student_analysis = []
            for enrollment in enrollments:
                student = enrollment.student
                student_attendances = [a for a in attendance_records if a.student_id == student.id]
                
                student_present = len([a for a in student_attendances if a.status == "present"])
                student_late = len([a for a in student_attendances if a.status == "late"])
                student_total = len(student_attendances)
                student_absent = total_sessions - student_total
                
                student_rate = (student_total / total_sessions * 100) if total_sessions > 0 else 0
                
                student_analysis.append({
                    "student_id": student.id,
                    "student_name": student.full_name,
                    "student_identifier": student.get_identifier(),
                    "present": student_present,
                    "late": student_late,
                    "absent": student_absent,
                    "total_attended": student_total,
                    "attendance_rate": round(student_rate, 2),
                    "status": "good" if student_rate >= 75 else "warning" if student_rate >= 60 else "poor"
                })
            
            # Session-wise analysis
            session_analysis = []
            for session in sessions:
                session_attendances = [a for a in attendance_records if a.session_id == session.id]
                session_rate = (len(session_attendances) / total_students * 100) if total_students > 0 else 0
                
                session_analysis.append({
                    "session_id": session.id,
                    "session_date": session.session_date.isoformat(),
                    "session_topic": session.session_topic,
                    "attendees": len(session_attendances),
                    "attendance_rate": round(session_rate, 2),
                    "late_arrivals": len([a for a in session_attendances if a.status == "late"])
                })
            
            # Attendance patterns
            patterns = self._analyze_attendance_patterns(attendance_records, sessions)
            
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
                "student_statistics": sorted(student_analysis, key=lambda x: x['attendance_rate'], reverse=True),
                "session_statistics": session_analysis,
                "patterns": patterns,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting course analytics: {e}")
            raise
        finally:
            if not db:
                db.close()
    
    def _analyze_attendance_patterns(
        self, 
        attendance_records: List[AttendanceRecord], 
        sessions: List[ClassSession]
    ) -> Dict[str, Any]:
        """Analyze attendance patterns"""
        
        patterns = {
            "best_attendance_day": None,
            "worst_attendance_day": None,
            "peak_attendance_time": None,
            "chronic_absentees": [],
            "perfect_attendees": [],
            "improvement_trends": [],
            "decline_trends": []
        }
        
        if not attendance_records or not sessions:
            return patterns
        
        # Day of week analysis
        day_attendance = defaultdict(int)
        day_sessions = defaultdict(int)
        
        for session in sessions:
            day_name = session.session_date.strftime("%A")
            day_sessions[day_name] += 1
        
        for record in attendance_records:
            if record.session and record.session.session_date:
                day_name = record.session.session_date.strftime("%A")
                day_attendance[day_name] += 1
        
        # Calculate day rates
        day_rates = {}
        for day, count in day_attendance.items():
            if day_sessions[day] > 0:
                day_rates[day] = count / day_sessions[day]
        
        if day_rates:
            patterns["best_attendance_day"] = max(day_rates, key=day_rates.get)
            patterns["worst_attendance_day"] = min(day_rates, key=day_rates.get)
        
        return patterns

# Create global instance
analytics_service = UniversityAnalyticsService()
