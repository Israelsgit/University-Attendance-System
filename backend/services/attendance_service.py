# backend/services/attendance_service.py
"""
Enhanced Attendance Service for University System
Business logic for university attendance management
"""

from datetime import datetime, date, time, timedelta
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import logging
from collections import defaultdict

from config.database import get_db, SessionLocal
from api.models.user import User, UserRole
from api.models.course import Course
from api.models.class_session import ClassSession
from api.models.attendance import AttendanceRecord
from api.models.enrollment import Enrollment
from config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

class UniversityAttendanceService:
    """Enhanced service class for university attendance operations"""
    
    def __init__(self):
        self.late_threshold_minutes = settings.LATE_THRESHOLD_MINUTES
        self.minimum_attendance_percentage = settings.MINIMUM_ATTENDANCE_PERCENTAGE
    
    def calculate_attendance_status(
        self,
        marked_time: datetime,
        session_start_time: datetime,
        session_end_time: Optional[datetime] = None
    ) -> str:
        """Calculate attendance status based on marking time and session schedule"""
        
        # Calculate late threshold
        late_threshold = session_start_time + timedelta(minutes=self.late_threshold_minutes)
        
        if marked_time <= late_threshold:
            return "present"
        elif session_end_time and marked_time <= session_end_time:
            return "late"
        else:
            return "late"  # Still allow late marking during class
    
    def mark_student_attendance(
        self,
        student_id: int,
        session_id: int,
        face_confidence: float,
        recognition_method: str = "face_recognition",
        marked_by_lecturer: Optional[int] = None,
        notes: Optional[str] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Mark attendance for a student in a session"""
        
        if not db:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False
        
        try:
            # Get session details
            session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
            if not session:
                raise ValueError("Session not found")
            
            # Get student
            student = db.query(User).filter(
                and_(
                    User.id == student_id,
                    User.role == UserRole.STUDENT
                )
            ).first()
            if not student:
                raise ValueError("Student not found")
            
            # Check if already marked
            existing_attendance = db.query(AttendanceRecord).filter(
                and_(
                    AttendanceRecord.student_id == student_id,
                    AttendanceRecord.session_id == session_id
                )
            ).first()
            
            if existing_attendance:
                return {
                    "success": False,
                    "error": "Attendance already marked for this session"
                }
            
            # Calculate attendance status
            now = datetime.now()
            session_end = session.session_date + timedelta(minutes=session.duration_minutes)
            status = self.calculate_attendance_status(now, session.session_date, session_end)
            
            # Create attendance record
            attendance = AttendanceRecord(
                student_id=student_id,
                course_id=session.course_id,
                session_id=session_id,
                marked_at=now,
                status=status,
                face_confidence=face_confidence,
                recognition_method=recognition_method,
                marked_by_lecturer=marked_by_lecturer,
                notes=notes
            )
            
            db.add(attendance)
            db.commit()
            db.refresh(attendance)
            
            logger.info(f"Attendance marked: Student {student.full_name} - {status}")
            
            return {
                "success": True,
                "attendance_id": attendance.id,
                "status": status,
                "marked_at": now.isoformat(),
                "student_name": student.full_name,
                "course_code": session.course.course_code,
                "confidence": face_confidence
            }
            
        except Exception as e:
            logger.error(f"Error marking attendance: {e}")
            db.rollback()
            raise
        finally:
            if close_db:
                db.close()
    
    def get_session_attendance(
        self,
        session_id: int,
        db: Session = None
    ) -> Dict[str, Any]:
        """Get attendance records for a specific session"""
        
        if not db:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False
        
        try:
            # Get session
            session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
            if not session:
                raise ValueError("Session not found")
            
            # Get enrolled students for the course
            enrollments = db.query(Enrollment).filter(
                and_(
                    Enrollment.course_id == session.course_id,
                    Enrollment.enrollment_status == "active"
                )
            ).all()
            
            # Get attendance records for this session
            attendance_records = db.query(AttendanceRecord).filter(
                AttendanceRecord.session_id == session_id
            ).all()
            
            # Create attendance summary
            total_students = len(enrollments)
            present_students = len(attendance_records)
            absent_students = total_students - present_students
            
            present_count = len([a for a in attendance_records if a.status == "present"])
            late_count = len([a for a in attendance_records if a.status == "late"])
            
            attendance_rate = (present_students / total_students * 100) if total_students > 0 else 0
            
            # Student details
            student_details = []
            attended_student_ids = [a.student_id for a in attendance_records]
            
            for enrollment in enrollments:
                student = enrollment.student
                attendance_record = next(
                    (a for a in attendance_records if a.student_id == student.id), 
                    None
                )
                
                if attendance_record:
                    student_details.append({
                        "student_id": student.id,
                        "student_name": student.full_name,
                        "student_identifier": student.get_identifier(),
                        "status": attendance_record.status,
                        "marked_at": attendance_record.marked_at.isoformat(),
                        "confidence": attendance_record.face_confidence,
                        "method": attendance_record.recognition_method
                    })
                else:
                    student_details.append({
                        "student_id": student.id,
                        "student_name": student.full_name,
                        "student_identifier": student.get_identifier(),
                        "status": "absent",
                        "marked_at": None,
                        "confidence": None,
                        "method": None
                    })
            
            return {
                "session": {
                    "id": session.id,
                    "date": session.session_date.isoformat(),
                    "topic": session.session_topic,
                    "course_code": session.course.course_code,
                    "course_title": session.course.course_title
                },
                "summary": {
                    "total_students": total_students,
                    "present_students": present_students,
                    "absent_students": absent_students,
                    "present_count": present_count,
                    "late_count": late_count,
                    "attendance_rate": round(attendance_rate, 2)
                },
                "students": student_details
            }
            
        except Exception as e:
            logger.error(f"Error getting session attendance: {e}")
            raise
        finally:
            if close_db:
                db.close()
    
    def get_student_attendance_summary(
        self,
        student_id: int,
        course_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Get attendance summary for a student"""
        
        if not db:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False
        
        try:
            # Get student
            student = db.query(User).filter(
                and_(
                    User.id == student_id,
                    User.role == UserRole.STUDENT
                )
            ).first()
            if not student:
                raise ValueError("Student not found")
            
            # Build query for attendance records
            query = db.query(AttendanceRecord).filter(
                AttendanceRecord.student_id == student_id
            )
            
            if course_id:
                query = query.filter(AttendanceRecord.course_id == course_id)
            
            if start_date:
                query = query.filter(
                    func.date(AttendanceRecord.marked_at) >= start_date
                )
            
            if end_date:
                query = query.filter(
                    func.date(AttendanceRecord.marked_at) <= end_date
                )
            
            attendance_records = query.order_by(desc(AttendanceRecord.marked_at)).all()
            
            # Get enrolled courses
            enrollments = db.query(Enrollment).filter(
                and_(
                    Enrollment.student_id == student_id,
                    Enrollment.enrollment_status == "active"
                )
            ).all()
            
            # Calculate statistics per course
            course_stats = []
            for enrollment in enrollments:
                course = enrollment.course
                
                # Filter records for this course
                course_records = [r for r in attendance_records if r.course_id == course.id]
                
                # Get total sessions for this course
                session_query = db.query(ClassSession).filter(
                    ClassSession.course_id == course.id
                )
                
                if start_date:
                    session_query = session_query.filter(
                        func.date(ClassSession.session_date) >= start_date
                    )
                
                if end_date:
                    session_query = session_query.filter(
                        func.date(ClassSession.session_date) <= end_date
                    )
                
                total_sessions = session_query.count()
                
                # Calculate statistics
                present_count = len([r for r in course_records if r.status == "present"])
                late_count = len([r for r in course_records if r.status == "late"])
                total_attended = len(course_records)
                absent_count = total_sessions - total_attended
                
                attendance_rate = (total_attended / total_sessions * 100) if total_sessions > 0 else 0
                
                course_stats.append({
                    "course_id": course.id,
                    "course_code": course.course_code,
                    "course_title": course.course_title,
                    "total_sessions": total_sessions,
                    "present": present_count,
                    "late": late_count,
                    "absent": absent_count,
                    "attendance_rate": round(attendance_rate, 2),
                    "status": self._get_attendance_status_category(attendance_rate)
                })
            
            # Overall statistics
            total_sessions_all = sum(stat["total_sessions"] for stat in course_stats)
            total_attended_all = sum(stat["present"] + stat["late"] for stat in course_stats)
            overall_rate = (total_attended_all / total_sessions_all * 100) if total_sessions_all > 0 else 0
            
            return {
                "student": {
                    "id": student.id,
                    "name": student.full_name,
                    "identifier": student.get_identifier(),
                    "level": student.level.value if student.level else None,
                    "department": student.department
                },
                "overall_summary": {
                    "total_courses": len(course_stats),
                    "total_sessions": total_sessions_all,
                    "total_attended": total_attended_all,
                    "overall_rate": round(overall_rate, 2),
                    "status": self._get_attendance_status_category(overall_rate)
                },
                "course_statistics": course_stats,
                "recent_records": [record.to_dict() for record in attendance_records[:10]]
            }
            
        except Exception as e:
            logger.error(f"Error getting student attendance summary: {e}")
            raise
        finally:
            if close_db:
                db.close()
    
    def get_course_attendance_analytics(
        self,
        course_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Get comprehensive attendance analytics for a course"""
        
        if not db:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False
        
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
            
            # Get sessions
            session_query = db.query(ClassSession).filter(
                ClassSession.course_id == course_id
            )
            
            if start_date:
                session_query = session_query.filter(
                    func.date(ClassSession.session_date) >= start_date
                )
            
            if end_date:
                session_query = session_query.filter(
                    func.date(ClassSession.session_date) <= end_date
                )
            
            sessions = session_query.order_by(ClassSession.session_date).all()
            total_sessions = len(sessions)
            
            # Get attendance records
            attendance_query = db.query(AttendanceRecord).filter(
                AttendanceRecord.course_id == course_id
            )
            
            if start_date:
                attendance_query = attendance_query.filter(
                    func.date(AttendanceRecord.marked_at) >= start_date
                )
            
            if end_date:
                attendance_query = attendance_query.filter(
                    func.date(AttendanceRecord.marked_at) <= end_date
                )
            
            attendance_records = attendance_query.all()
            
            # Calculate overall statistics
            total_attendances = len(attendance_records)
            present_count = len([a for a in attendance_records if a.status == "present"])
            late_count = len([a for a in attendance_records if a.status == "late"])
            
            expected_total = total_students * total_sessions
            absent_count = expected_total - total_attendances
            
            overall_rate = (total_attendances / expected_total * 100) if expected_total > 0 else 0
            
            # Student-wise analysis
            student_analysis = []
            for enrollment in enrollments:
                student = enrollment.student
                student_records = [a for a in attendance_records if a.student_id == student.id]
                
                student_present = len([a for a in student_records if a.status == "present"])
                student_late = len([a for a in student_records if a.status == "late"])
                student_total = len(student_records)
                student_absent = total_sessions - student_total
                
                student_rate = (student_total / total_sessions * 100) if total_sessions > 0 else 0
                
                student_analysis.append({
                    "student_id": student.id,
                    "student_name": student.full_name,
                    "student_identifier": student.get_identifier(),
                    "present": student_present,
                    "late": student_late,
                    "absent": student_absent,
                    "attendance_rate": round(student_rate, 2),
                    "status": self._get_attendance_status_category(student_rate)
                })
            
            # Session-wise analysis
            session_analysis = []
            for session in sessions:
                session_records = [a for a in attendance_records if a.session_id == session.id]
                session_rate = (len(session_records) / total_students * 100) if total_students > 0 else 0
                
                session_analysis.append({
                    "session_id": session.id,
                    "session_date": session.session_date.isoformat(),
                    "session_topic": session.session_topic,
                    "attendees": len(session_records),
                    "attendance_rate": round(session_rate, 2),
                    "late_arrivals": len([a for a in session_records if a.status == "late"])
                })
            
            # Trend analysis
            trends = self._calculate_attendance_trends(sessions, attendance_records, total_students)
            
            return {
                "course": course.to_dict(),
                "summary": {
                    "total_students": total_students,
                    "total_sessions": total_sessions,
                    "total_attendances": total_attendances,
                    "present_count": present_count,
                    "late_count": late_count,
                    "absent_count": absent_count,
                    "overall_attendance_rate": round(overall_rate, 2)
                },
                "student_statistics": sorted(student_analysis, key=lambda x: x['attendance_rate'], reverse=True),
                "session_statistics": session_analysis,
                "trends": trends,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting course analytics: {e}")
            raise
        finally:
            if close_db:
                db.close()
    
    def _get_attendance_status_category(self, attendance_rate: float) -> str:
        """Get attendance status category based on rate"""
        if attendance_rate >= self.minimum_attendance_percentage:
            return "good"
        elif attendance_rate >= 60:
            return "warning"
        else:
            return "poor"
    
    def _calculate_attendance_trends(
        self,
        sessions: List[ClassSession],
        attendance_records: List[AttendanceRecord],
        total_students: int
    ) -> Dict[str, Any]:
        """Calculate attendance trends over time"""
        
        if not sessions:
            return {"weekly_trends": [], "monthly_trends": []}
        
        # Group sessions by week
        weekly_data = defaultdict(lambda: {"sessions": 0, "attendances": 0})
        monthly_data = defaultdict(lambda: {"sessions": 0, "attendances": 0})
        
        for session in sessions:
            week_key = session.session_date.strftime("%Y-W%U")
            month_key = session.session_date.strftime("%Y-%m")
            
            weekly_data[week_key]["sessions"] += 1
            monthly_data[month_key]["sessions"] += 1
            
            session_attendances = [a for a in attendance_records if a.session_id == session.id]
            weekly_data[week_key]["attendances"] += len(session_attendances)
            monthly_data[month_key]["attendances"] += len(session_attendances)
        
        # Calculate weekly trends
        weekly_trends = []
        for week, data in sorted(weekly_data.items()):
            expected = data["sessions"] * total_students
            rate = (data["attendances"] / expected * 100) if expected > 0 else 0
            weekly_trends.append({
                "period": week,
                "sessions": data["sessions"],
                "attendances": data["attendances"],
                "rate": round(rate, 2)
            })
        
        # Calculate monthly trends
        monthly_trends = []
        for month, data in sorted(monthly_data.items()):
            expected = data["sessions"] * total_students
            rate = (data["attendances"] / expected * 100) if expected > 0 else 0
            monthly_trends.append({
                "period": month,
                "sessions": data["sessions"],
                "attendances": data["attendances"],
                "rate": round(rate, 2)
            })
        
        return {
            "weekly_trends": weekly_trends,
            "monthly_trends": monthly_trends
        }
    
    def get_attendance_alerts(
        self,
        lecturer_id: Optional[int] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Get attendance alerts for poor performance"""
        
        if not db:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False
        
        try:
            alerts = {
                "chronic_absentees": [],
                "declining_attendance": [],
                "course_alerts": []
            }
            
            # Get courses (filter by lecturer if specified)
            course_query = db.query(Course).filter(Course.is_active == True)
            if lecturer_id:
                course_query = course_query.filter(Course.lecturer_id == lecturer_id)
            
            courses = course_query.all()
            
            for course in courses:
                # Get course analytics
                analytics = self.get_course_attendance_analytics(course.id, db=db)
                
                # Check for students with poor attendance
                for student_stat in analytics["student_statistics"]:
                    if student_stat["attendance_rate"] < 50:
                        alerts["chronic_absentees"].append({
                            "student_id": student_stat["student_id"],
                            "student_name": student_stat["student_name"],
                            "course_code": course.course_code,
                            "attendance_rate": student_stat["attendance_rate"]
                        })
                
                # Check for overall course alerts
                if analytics["summary"]["overall_attendance_rate"] < 60:
                    alerts["course_alerts"].append({
                        "course_id": course.id,
                        "course_code": course.course_code,
                        "attendance_rate": analytics["summary"]["overall_attendance_rate"],
                        "alert_type": "low_attendance"
                    })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting attendance alerts: {e}")
            raise
        finally:
            if close_db:
                db.close()

# Create global instance
attendance_service = UniversityAttendanceService()