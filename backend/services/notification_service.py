"""
Notification Service
Handles various types of notifications (email, SMS, push)
"""

import asyncio
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging

from config.database import SessionLocal
from api.models.user import User
from api.models.attendance import AttendanceRecord
from api.utils.email import email_service
from config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

class NotificationService:
    """Service for managing notifications"""
    
    def __init__(self):
        self.email_enabled = bool(settings.SMTP_SERVER)
        self.sms_enabled = False  # Can be configured later
        self.push_enabled = False  # Can be configured later
    
    async def send_attendance_reminder(
        self,
        user_ids: Optional[List[int]] = None,
        db: Session = None
    ) -> Dict[str, int]:
        """Send attendance reminders to users who haven't checked in"""
        
        if not db:
            db = SessionLocal()
        
        results = {"sent": 0, "failed": 0, "skipped": 0}
        
        try:
            current_time = datetime.now().time()
            work_start = datetime.strptime(settings.WORK_START_TIME, "%H:%M").time()
            
            # Only send reminders after work start time
            if current_time < work_start:
                logger.info("🕐 Too early to send attendance reminders")
                return results
            
            # Get users who haven't checked in today
            today = date.today()
            
            # Build query for users without attendance today
            query = db.query(User).filter(User.is_active == True)
            
            if user_ids:
                query = query.filter(User.id.in_(user_ids))
            
            # Exclude users who already checked in
            checked_in_users = db.query(AttendanceRecord.user_id).filter(
                and_(
                    AttendanceRecord.date == today,
                    AttendanceRecord.check_in_time.isnot(None)
                )
            ).subquery()
            
            users_to_remind = query.filter(
                ~User.id.in_(checked_in_users)
            ).all()
            
            logger.info(f"📧 Sending attendance reminders to {len(users_to_remind)} users")
            
            for user in users_to_remind:
                try:
                    if self.email_enabled and user.email:
                        success = await email_service.send_attendance_reminder(
                            user_email=user.email,
                            user_name=user.name
                        )
                        
                        if success:
                            results["sent"] += 1
                            logger.debug(f"✅ Reminder sent to {user.email}")
                        else:
                            results["failed"] += 1
                            logger.warning(f"❌ Failed to send reminder to {user.email}")
                    else:
                        results["skipped"] += 1
                        logger.debug(f"⏭️ Skipped {user.email} (email not configured)")
                
                except Exception as e:
                    logger.error(f"❌ Error sending reminder to {user.email}: {e}")
                    results["failed"] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in attendance reminder service: {e}")
            return results
        finally:
            db.close()
    
    async def send_daily_summary(
        self,
        target_date: Optional[date] = None,
        recipient_roles: List[str] = None,
        db: Session = None
    ) -> Dict[str, int]:
        """Send daily attendance summary to managers/admins"""
        
        if not db:
            db = SessionLocal()
        
        if not target_date:
            target_date = date.today()
        
        if not recipient_roles:
            recipient_roles = ["admin", "manager", "hr"]
        
        results = {"sent": 0, "failed": 0}
        
        try:
            # Get recipients
            recipients = db.query(User).filter(
                and_(
                    User.is_active == True,
                    User.role.in_(recipient_roles)
                )
            ).all()
            
            # Calculate daily summary
            total_employees = db.query(User).filter(User.is_active == True).count()
            
            attendance_records = db.query(AttendanceRecord).filter(
                AttendanceRecord.date == target_date
            ).all()
            
            present_count = len([r for r in attendance_records if r.check_in_time])
            late_count = len([r for r in attendance_records if r.status == 'late'])
            absent_count = total_employees - present_count
            
            # Department breakdown
            from sqlalchemy import func
            dept_stats = db.query(
                User.department,
                func.count(User.id).label('total'),
                func.count(AttendanceRecord.id).label('present')
            ).outerjoin(
                AttendanceRecord,
                and_(
                    AttendanceRecord.user_id == User.id,
                    AttendanceRecord.date == target_date,
                    AttendanceRecord.check_in_time.isnot(None)
                )
            ).filter(User.is_active == True).group_by(User.department).all()
            
            summary_data = {
                "date": target_date.strftime("%B %d, %Y"),
                "total_employees": total_employees,
                "present_count": present_count,
                "absent_count": absent_count,
                "late_count": late_count,
                "attendance_rate": round((present_count / max(total_employees, 1)) * 100, 2),
                "department_stats": [
                    {
                        "department": stat.department,
                        "total": stat.total,
                        "present": stat.present,
                        "rate": round((stat.present / max(stat.total, 1)) * 100, 2)
                    }
                    for stat in dept_stats
                ]
            }
            
            # Send to recipients
            for recipient in recipients:
                try:
                    if self.email_enabled and recipient.email:
                        success = await email_service.send_template_email(
                            template_name="daily_summary",
                            to_emails=[recipient.email],
                            subject=f"Daily Attendance Summary - {target_date.strftime('%B %d, %Y')}",
                            template_data={
                                "recipient_name": recipient.name,
                                **summary_data
                            }
                        )
                        
                        if success:
                            results["sent"] += 1
                        else:
                            results["failed"] += 1
                
                except Exception as e:
                    logger.error(f"❌ Error sending summary to {recipient.email}: {e}")
                    results["failed"] += 1
            
            logger.info(f"📊 Daily summary sent: {results['sent']} successful, {results['failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in daily summary service: {e}")
            return results
        finally:
            db.close()
    
    async def send_monthly_reports(
        self,
        target_month: Optional[int] = None,
        target_year: Optional[int] = None,
        user_ids: Optional[List[int]] = None,
        db: Session = None
    ) -> Dict[str, int]:
        """Send monthly attendance reports to users"""
        
        if not db:
            db = SessionLocal()
        
        today = date.today()
        if not target_month:
            target_month = today.month - 1 if today.month > 1 else 12
        if not target_year:
            target_year = today.year if today.month > 1 else today.year - 1
        
        results = {"sent": 0, "failed": 0}
        
        try:
            # Get month date range
            import calendar
            start_date = date(target_year, target_month, 1)
            last_day = calendar.monthrange(target_year, target_month)[1]
            end_date = date(target_year, target_month, last_day)
            
            # Get users
            query = db.query(User).filter(User.is_active == True)
            if user_ids:
                query = query.filter(User.id.in_(user_ids))
            
            users = query.all()
            
            month_name = calendar.month_name[target_month]
            
            for user in users:
                try:
                    # Calculate user's monthly stats
                    records = db.query(AttendanceRecord).filter(
                        and_(
                            AttendanceRecord.user_id == user.id,
                            AttendanceRecord.date >= start_date,
                            AttendanceRecord.date <= end_date
                        )
                    ).all()
                    
                    total_days = len(records)
                    present_days = len([r for r in records if r.status in ['present', 'late', 'overtime']])
                    absent_days = len([r for r in records if r.status == 'absent'])
                    late_days = len([r for r in records if r.status == 'late'])
                    total_hours = sum([r.total_hours or 0 for r in records])
                    avg_hours = total_hours / max(present_days, 1)
                    attendance_rate = (present_days / max(total_days, 1)) * 100
                    
                    report_data = {
                        "month_year": f"{month_name} {target_year}",
                        "total_days": total_days,
                        "present_days": present_days,
                        "absent_days": absent_days,
                        "late_days": late_days,
                        "total_hours": round(total_hours, 2),
                        "avg_hours": round(avg_hours, 2),
                        "attendance_rate": round(attendance_rate, 2)
                    }
                    
                    if self.email_enabled and user.email:
                        success = await email_service.send_monthly_report(
                            user_email=user.email,
                            user_name=user.name,
                            report_data=report_data
                        )
                        
                        if success:
                            results["sent"] += 1
                        else:
                            results["failed"] += 1
                
                except Exception as e:
                    logger.error(f"❌ Error sending report to {user.email}: {e}")
                    results["failed"] += 1
            
            logger.info(f"📈 Monthly reports sent: {results['sent']} successful, {results['failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in monthly reports service: {e}")
            return results
        finally:
            db.close()
    
    async def send_overtime_alert(
        self,
        user_id: int,
        overtime_hours: float,
        date: date,
        db: Session = None
    ) -> bool:
        """Send overtime alert to user and their manager"""
        
        if not db:
            db = SessionLocal()
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Prepare alert data
            alert_data = {
                "user_name": user.name,
                "employee_id": user.employee_id,
                "overtime_hours": round(overtime_hours, 2),
                "date": date.strftime("%B %d, %Y"),
                "department": user.department
            }
            
            recipients = [user.email] if user.email else []
            
            # Add manager if exists
            if user.manager and user.manager.email:
                recipients.append(user.manager.email)
                alert_data["manager_name"] = user.manager.name
            
            # Add HR/Admin
            hr_admins = db.query(User).filter(
                and_(
                    User.is_active == True,
                    or_(User.role == "hr", User.role == "admin")
                )
            ).all()
            
            for admin in hr_admins:
                if admin.email and admin.email not in recipients:
                    recipients.append(admin.email)
            
            if self.email_enabled and recipients:
                success = await email_service.send_template_email(
                    template_name="overtime_alert",
                    to_emails=recipients,
                    subject=f"Overtime Alert - {user.name}",
                    template_data=alert_data
                )
                
                if success:
                    logger.info(f"🚨 Overtime alert sent for {user.name}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error sending overtime alert: {e}")
            return False
        finally:
            db.close()
    
    async def send_absence_alert(
        self,
        user_id: int,
        consecutive_days: int,
        db: Session = None
    ) -> bool:
        """Send alert for consecutive absences"""
        
        if not db:
            db = SessionLocal()
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            alert_data = {
                "user_name": user.name,
                "employee_id": user.employee_id,
                "consecutive_days": consecutive_days,
                "department": user.department,
                "date": date.today().strftime("%B %d, %Y")
            }
            
            # Send to manager and HR
            recipients = []
            if user.manager and user.manager.email:
                recipients.append(user.manager.email)
            
            hr_admins = db.query(User).filter(
                and_(
                    User.is_active == True,
                    or_(User.role == "hr", User.role == "admin")
                )
            ).all()
            
            for admin in hr_admins:
                if admin.email and admin.email not in recipients:
                    recipients.append(admin.email)
            
            if self.email_enabled and recipients:
                success = await email_service.send_template_email(
                    template_name="absence_alert",
                    to_emails=recipients,
                    subject=f"Absence Alert - {user.name} ({consecutive_days} days)",
                    template_data=alert_data
                )
                
                if success:
                    logger.info(f"🚨 Absence alert sent for {user.name}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error sending absence alert: {e}")
            return False
        finally:
            db.close()
    
    def schedule_notifications(self):
        """Schedule periodic notifications"""
        # This would typically use a task scheduler like Celery
        # For now, we'll implement basic scheduling logic
        
        async def notification_scheduler():
            while True:
                try:
                    current_time = datetime.now().time()
                    
                    # Send attendance reminders at 9:30 AM
                    if current_time.hour == 9 and current_time.minute == 30:
                        await self.send_attendance_reminder()
                    
                    # Send daily summary at 6 PM
                    if current_time.hour == 18 and current_time.minute == 0:
                        await self.send_daily_summary()
                    
                    # Check for monthly reports (1st day of month at 9 AM)
                    if (datetime.now().day == 1 and 
                        current_time.hour == 9 and 
                        current_time.minute == 0):
                        await self.send_monthly_reports()
                    
                    # Wait 1 minute before next check
                    await asyncio.sleep(60)
                    
                except Exception as e:
                    logger.error(f"❌ Error in notification scheduler: {e}")
                    await asyncio.sleep(60)
        
        # Run scheduler in background
        return asyncio.create_task(notification_scheduler())

# Create service instance
notification_service = NotificationService()

# Export for use in other modules
__all__ = ['NotificationService', 'notification_service']