"""
Attendance Service
Business logic for attendance management
"""

from datetime import datetime, date, time, timedelta
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import logging

from config.database import get_db, SessionLocal
from api.models.user import User
from api.models.attendance import AttendanceRecord
from config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

class AttendanceService:
    """Service class for attendance operations"""
    
    def __init__(self):
        self.work_start_time = datetime.strptime(settings.WORK_START_TIME, "%H:%M").time()
        self.work_end_time = datetime.strptime(settings.WORK_END_TIME, "%H:%M").time()
        self.late_threshold_minutes = settings.LATE_THRESHOLD_MINUTES
        self.early_departure_threshold_minutes = settings.EARLY_DEPARTURE_THRESHOLD_MINUTES
    
    def calculate_attendance_status(
        self,
        check_in_time: Optional[time],
        check_out_time: Optional[time],
        attendance_date: date
    ) -> str:
        """Calculate attendance status based on check-in/out times"""
        
        if not check_in_time:
            return "absent"
        
        # Calculate late threshold
        work_start_dt = datetime.combine(attendance_date, self.work_start_time)
        late_threshold_dt = work_start_dt + timedelta(minutes=self.late_threshold_minutes)
        check_in_dt = datetime.combine(attendance_date, check_in_time)
        
        # Check if late
        is_late = check_in_dt > late_threshold_dt
        
        if not check_out_time:
            return "late" if is_late else "present"
        
        # Calculate total hours worked
        check_out_dt = datetime.combine(attendance_date, check_out_time)
        
        # Handle overnight shifts
        if check_out_dt < check_in_dt:
            check_out_dt += timedelta(days=1)
        
        total_hours = (check_out_dt - check_in_dt).total_seconds() / 3600
        
        # Determine final status
        if total_hours >= 9:  # More than 9 hours
            return "overtime"
        elif total_hours < 4:  # Less than 4 hours (half day)
            return "half_day"
        elif is_late:
            return "late"
        else:
            # Check for early departure
            work_end_dt = datetime.combine(attendance_date, self.work_end_time)
            early_threshold_dt = work_end_dt - timedelta(minutes=self.early_departure_threshold_minutes)
            
            if check_out_dt < early_threshold_dt:
                return "early_departure"
            
            return "present"
    
    def calculate_overtime_hours(
        self,
        check_in_time: time,
        check_out_time: time,
        attendance_date: date,
        standard_hours: float = 8.0
    ) -> float:
        """Calculate overtime hours"""
        
        if not check_in_time or not check_out_time:
            return 0.0
        
        check_in_dt = datetime.combine(attendance_date, check_in_time)
        check_out_dt = datetime.combine(attendance_date, check_out_time)
        
        # Handle overnight shifts
        if check_out_dt < check_in_dt:
            check_out_dt += timedelta(days=1)
        
        total_hours = (check_out_dt - check_in_dt).total_seconds() / 3600
        
        return max(0, total_hours - standard_hours)
    
    def get_user_attendance_summary(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
        db: Session
    ) -> Dict[str, Any]:
        """Get attendance summary for a user"""
        
        try:
            # Get attendance records
            records = db.query(AttendanceRecord).filter(
                and_(
                    AttendanceRecord.user_id == user_id,
                    AttendanceRecord.date >= start_date,
                    AttendanceRecord.date <= end_date
                )
            ).all()
            
            # Calculate statistics
            total_days = len(records)
            present_days = len([r for r in records if r.status in ['present', 'late', 'overtime']])
            absent_days = len([r for r in records if r.status == 'absent'])
            late_days = len([r for r in records if r.status == 'late'])
            overtime_days = len([r for r in records if r.status == 'overtime'])
            half_days = len([r for r in records if r.status == 'half_day'])
            
            total_hours = sum([r.total_hours or 0 for r in records])
            avg_hours = total_hours / max(present_days, 1)
            attendance_rate = (present_days / max(total_days, 1)) * 100
            
            # Calculate overtime hours
            overtime_hours = sum([
                self.calculate_overtime_hours(
                    r.check_in_time, r.check_out_time, r.date
                ) for r in records if r.check_in_time and r.check_out_time
            ])
            
            return {
                "user_id": user_id,
                "period": f"{start_date} to {end_date}",
                "total_days": total_days,
                "present_days": present_days,
                "absent_days": absent_days,
                "late_days": late_days,
                "overtime_days": overtime_days,
                "half_days": half_days,
                "total_hours": round(total_hours, 2),
                "avg_hours": round(avg_hours, 2),
                "overtime_hours": round(overtime_hours, 2),
                "attendance_rate": round(attendance_rate, 2),
                "punctuality_rate": round((present_days - late_days) / max(present_days, 1) * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating attendance summary: {e}")
            return {}
    
    def get_department_attendance_summary(
        self,
        department: str,
        target_date: date,
        db: Session
    ) -> Dict[str, Any]:
        """Get department attendance summary for a specific date"""
        
        try:
            # Get all users in department
            users = db.query(User).filter(
                and_(User.department == department, User.is_active == True)
            ).all()
            
            # Get attendance records for the date
            attendance_records = db.query(AttendanceRecord).join(User).filter(
                and_(
                    User.department == department,
                    AttendanceRecord.date == target_date
                )
            ).all()
            
            total_employees = len(users)
            present_count = len([r for r in attendance_records if r.status in ['present', 'late', 'overtime']])
            late_count = len([r for r in attendance_records if r.status == 'late'])
            absent_count = total_employees - len(attendance_records)
            
            return {
                "department": department,
                "date": target_date.isoformat(),
                "total_employees": total_employees,
                "present_count": present_count,
                "absent_count": absent_count,
                "late_count": late_count,
                "attendance_rate": round((present_count / max(total_employees, 1)) * 100, 2),
                "punctuality_rate": round((present_count - late_count) / max(present_count, 1) * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating department summary: {e}")
            return {}
    
    def process_daily_attendance(
        self,
        target_date: date,
        db: Session
    ) -> Dict[str, Any]:
        """Process and finalize daily attendance"""
        
        try:
            # Get all active users
            users = db.query(User).filter(User.is_active == True).all()
            
            processed_count = 0
            created_count = 0
            
            for user in users:
                # Check if attendance record exists
                existing_record = db.query(AttendanceRecord).filter(
                    and_(
                        AttendanceRecord.user_id == user.id,
                        AttendanceRecord.date == target_date
                    )
                ).first()
                
                if not existing_record:
                    # Create absent record for users who didn't check in
                    absent_record = AttendanceRecord(
                        user_id=user.id,
                        date=target_date,
                        status="absent"
                    )
                    db.add(absent_record)
                    created_count += 1
                else:
                    # Update status if needed
                    if existing_record.check_in_time and existing_record.check_out_time:
                        new_status = self.calculate_attendance_status(
                            existing_record.check_in_time,
                            existing_record.check_out_time,
                            target_date
                        )
                        
                        if new_status != existing_record.status:
                            existing_record.status = new_status
                            existing_record.updated_at = datetime.utcnow()
                    
                    processed_count += 1
            
            db.commit()
            
            logger.info(f"✅ Daily attendance processed: {processed_count} updated, {created_count} created")
            
            return {
                "date": target_date.isoformat(),
                "processed_count": processed_count,
                "created_count": created_count,
                "total_users": len(users)
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing daily attendance: {e}")
            db.rollback()
            return {}
    
    def detect_attendance_anomalies(
        self,
        user_id: int,
        days_to_check: int = 30,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Detect unusual attendance patterns"""
        
        if not db:
            db = SessionLocal()
        
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days_to_check)
            
            records = db.query(AttendanceRecord).filter(
                and_(
                    AttendanceRecord.user_id == user_id,
                    AttendanceRecord.date >= start_date,
                    AttendanceRecord.date <= end_date
                )
            ).order_by(AttendanceRecord.date).all()
            
            anomalies = []
            
            # Check for patterns
            consecutive_lates = 0
            consecutive_absents = 0
            
            for record in records:
                # Check for consecutive lates
                if record.status == 'late':
                    consecutive_lates += 1
                    if consecutive_lates >= 3:
                        anomalies.append({
                            "type": "consecutive_late",
                            "date": record.date.isoformat(),
                            "description": f"Late for {consecutive_lates} consecutive days",
                            "severity": "medium"
                        })
                else:
                    consecutive_lates = 0
                
                # Check for consecutive absents
                if record.status == 'absent':
                    consecutive_absents += 1
                    if consecutive_absents >= 2:
                        anomalies.append({
                            "type": "consecutive_absent",
                            "date": record.date.isoformat(),
                            "description": f"Absent for {consecutive_absents} consecutive days",
                            "severity": "high"
                        })
                else:
                    consecutive_absents = 0
                
                # Check for unusual check-in times
                if record.check_in_time:
                    check_in_hour = record.check_in_time.hour
                    if check_in_hour < 6 or check_in_hour > 12:
                        anomalies.append({
                            "type": "unusual_checkin",
                            "date": record.date.isoformat(),
                            "description": f"Unusual check-in time: {record.check_in_time}",
                            "severity": "low"
                        })
                
                # Check for excessive overtime
                if record.total_hours and record.total_hours > 12:
                    anomalies.append({
                        "type": "excessive_overtime",
                        "date": record.date.isoformat(),
                        "description": f"Worked {record.total_hours:.1f} hours",
                        "severity": "medium"
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"❌ Error detecting anomalies: {e}")
            return []
        finally:
            db.close()
    
    def generate_attendance_insights(
        self,
        user_id: int,
        days_to_analyze: int = 90,
        db: Session = None
    ) -> Dict[str, Any]:
        """Generate attendance insights and recommendations"""
        
        if not db:
            db = SessionLocal()
        
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days_to_analyze)
            
            records = db.query(AttendanceRecord).filter(
                and_(
                    AttendanceRecord.user_id == user_id,
                    AttendanceRecord.date >= start_date,
                    AttendanceRecord.date <= end_date
                )
            ).all()
            
            if not records:
                return {"insights": [], "recommendations": []}
            
            insights = []
            recommendations = []
            
            # Calculate basic stats
            present_days = len([r for r in records if r.status in ['present', 'late', 'overtime']])
            late_days = len([r for r in records if r.status == 'late'])
            attendance_rate = (present_days / len(records)) * 100
            
            # Attendance rate insights
            if attendance_rate >= 95:
                insights.append("Excellent attendance record")
            elif attendance_rate >= 85:
                insights.append("Good attendance record")
                recommendations.append("Aim for 95%+ attendance rate")
            else:
                insights.append("Poor attendance record")
                recommendations.append("Significant improvement needed in attendance")
            
            # Punctuality insights
            punctuality_rate = ((present_days - late_days) / max(present_days, 1)) * 100
            if punctuality_rate < 80:
                insights.append("Frequent late arrivals detected")
                recommendations.append("Focus on arriving on time consistently")
            
            # Weekly pattern analysis
            weekday_attendance = {i: 0 for i in range(7)}  # Monday = 0
            for record in records:
                if record.status in ['present', 'late', 'overtime']:
                    weekday_attendance[record.date.weekday()] += 1
            
            # Find patterns
            weekend_issues = (weekday_attendance[5] + weekday_attendance[6]) / 2  # Sat + Sun
            weekday_avg = sum(weekday_attendance[i] for i in range(5)) / 5
            
            if weekend_issues > weekday_avg:
                insights.append("Better attendance on weekends than weekdays")
            
            # Monday blues check
            if weekday_attendance[0] < weekday_avg * 0.8:
                insights.append("Monday attendance is below average")
                recommendations.append("Pay special attention to Monday attendance")
            
            # Time pattern analysis
            check_in_times = [r.check_in_time for r in records if r.check_in_time]
            if check_in_times:
                avg_check_in = sum(
                    t.hour + t.minute/60 for t in check_in_times
                ) / len(check_in_times)
                
                work_start_decimal = self.work_start_time.hour + self.work_start_time.minute/60
                
                if avg_check_in > work_start_decimal + 0.5:  # More than 30 min late on average
                    recommendations.append("Consider adjusting morning routine to arrive earlier")
            
            return {
                "period": f"{start_date} to {end_date}",
                "insights": insights,
                "recommendations": recommendations,
                "stats": {
                    "attendance_rate": round(attendance_rate, 2),
                    "punctuality_rate": round(punctuality_rate, 2),
                    "total_days_analyzed": len(records),
                    "present_days": present_days,
                    "late_days": late_days
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating insights: {e}")
            return {"insights": [], "recommendations": []}
        finally:
            db.close()

# Create service instance
attendance_service = AttendanceService()

# Export for use in other modules
__all__ = ['AttendanceService', 'attendance_service']