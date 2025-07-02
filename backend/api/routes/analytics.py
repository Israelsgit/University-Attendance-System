"""
Analytics Routes
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
from api.models.user import User
from api.models.attendance import AttendanceRecord
from api.schemas.attendance import AttendanceStats, MonthlyStats, DepartmentAttendance, LiveAttendance
from api.schemas.common import SuccessResponse
from api.utils.security import get_current_user
from services.analytics_service import AnalyticsService

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize analytics service
analytics_service = AnalyticsService()

@router.get("/dashboard")
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard analytics data"""
    try:
        today = date.today()
        
        # Check permissions
        if not current_user.can_view_analytics():
            # Return limited data for regular users
            return await get_user_dashboard(current_user, db)
        
        # Get total users
        total_users = db.query(User).filter(User.is_active == True).count()
        
        # Get today's attendance
        today_attendance = db.query(AttendanceRecord).filter(
            AttendanceRecord.date == today
        ).all()
        
        checked_in = len([a for a in today_attendance if a.check_in_time])
        not_checked_in = total_users - checked_in
        late_arrivals = len([a for a in today_attendance if a.status == 'late'])
        early_departures = len([a for a in today_attendance if a.status == 'early_departure'])
        
        # Department-wise data
        departments = db.query(User.department, func.count(User.id)).filter(
            User.is_active == True
        ).group_by(User.department).all()
        
        dept_data = []
        for dept_name, dept_count in departments:
            dept_attendance = [a for a in today_attendance 
                             if a.user and a.user.department == dept_name]
            present_count = len([a for a in dept_attendance if a.check_in_time])
            
            dept_data.append(DepartmentAttendance(
                department=dept_name,
                total_employees=dept_count,
                present_today=present_count,
                absent_today=dept_count - present_count,
                late_today=len([a for a in dept_attendance if a.status == 'late']),
                attendance_rate=round((present_count / dept_count) * 100, 2) if dept_count > 0 else 0
            ))
        
        return LiveAttendance(
            total_employees=total_users,
            checked_in=checked_in,
            not_checked_in=not_checked_in,
            late_arrivals=late_arrivals,
            early_departures=early_departures,
            current_time=datetime.now().isoformat(),
            departments=dept_data
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard data"
        )

async def get_user_dashboard(current_user: User, db: Session):
    """Get dashboard data for regular users"""
    today = date.today()
    
    # Get user's today attendance
    today_attendance = db.query(AttendanceRecord).filter(
        and_(
            AttendanceRecord.user_id == current_user.id,
            AttendanceRecord.date == today
        )
    ).first()
    
    # Get monthly stats
    month_start = today.replace(day=1)
    monthly_records = db.query(AttendanceRecord).filter(
        and_(
            AttendanceRecord.user_id == current_user.id,
            AttendanceRecord.date >= month_start
        )
    ).all()
    
    present_days = len([r for r in monthly_records if r.status in ['present', 'late', 'overtime']])
    total_days = len(monthly_records)
    attendance_rate = (present_days / max(total_days, 1)) * 100
    
    return {
        "user_dashboard": True,
        "today_status": today_attendance.status if today_attendance else "absent",
        "check_in_time": today_attendance.check_in_time.isoformat() if today_attendance and today_attendance.check_in_time else None,
        "check_out_time": today_attendance.check_out_time.isoformat() if today_attendance and today_attendance.check_out_time else None,
        "monthly_attendance_rate": round(attendance_rate, 2),
        "monthly_present_days": present_days,
        "monthly_total_days": total_days
    }

@router.get("/attendance-trends")
async def get_attendance_trends(
    period: str = Query("weekly", pattern="^(weekly|monthly|yearly)$"),
    department: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get attendance trends over time"""
    try:
        # Check permissions
        if not current_user.can_view_analytics():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        today = date.today()
        
        if period == "weekly":
            # Last 8 weeks
            start_date = today - timedelta(weeks=8)
            date_format = "%Y-W%U"  # Year-Week format
        elif period == "monthly":
            # Last 12 months
            start_date = today - timedelta(days=365)
            date_format = "%Y-%m"  # Year-Month format
        else:  # yearly
            # Last 5 years
            start_date = today - timedelta(days=1825)
            date_format = "%Y"  # Year format
        
        # Build query
        query = db.query(
            func.strftime(date_format, AttendanceRecord.date).label('period'),
            func.count(AttendanceRecord.id).label('total_records'),
            func.sum(func.case([(AttendanceRecord.status.in_(['present', 'late', 'overtime']), 1)], else_=0)).label('present_count'),
            func.sum(func.case([(AttendanceRecord.status == 'late', 1)], else_=0)).label('late_count'),
            func.sum(func.case([(AttendanceRecord.status == 'overtime', 1)], else_=0)).label('overtime_count')
        ).filter(AttendanceRecord.date >= start_date)
        
        if department:
            query = query.join(User).filter(User.department == department)
        
        trends = query.group_by('period').order_by('period').all()
        
        trend_data = []
        for trend in trends:
            attendance_rate = (trend.present_count / max(trend.total_records, 1)) * 100
            trend_data.append({
                "period": trend.period,
                "total_records": trend.total_records,
                "present_count": trend.present_count,
                "late_count": trend.late_count,
                "overtime_count": trend.overtime_count,
                "attendance_rate": round(attendance_rate, 2)
            })
        
        return {"trends": trend_data, "period": period}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting attendance trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get attendance trends"
        )

@router.get("/department-comparison")
async def get_department_comparison(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get department-wise attendance comparison"""
    try:
        # Check permissions
        if not current_user.can_view_analytics():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Default to current month if dates not provided
        if not start_date or not end_date:
            today = date.today()
            start_date = today.replace(day=1)
            end_date = today
        
        # Get department-wise statistics
        dept_stats = db.query(
            User.department,
            func.count(User.id).label('total_employees'),
            func.count(AttendanceRecord.id).label('total_records'),
            func.sum(func.case([(AttendanceRecord.status.in_(['present', 'late', 'overtime']), 1)], else_=0)).label('present_count'),
            func.sum(func.case([(AttendanceRecord.status == 'late', 1)], else_=0)).label('late_count'),
            func.sum(func.case([(AttendanceRecord.status == 'overtime', 1)], else_=0)).label('overtime_count'),
            func.avg(AttendanceRecord.total_hours).label('avg_hours')
        ).outerjoin(
            AttendanceRecord,
            and_(
                AttendanceRecord.user_id == User.id,
                AttendanceRecord.date >= start_date,
                AttendanceRecord.date <= end_date
            )
        ).filter(User.is_active == True).group_by(User.department).all()
        
        comparison_data = []
        for stats in dept_stats:
            attendance_rate = (stats.present_count / max(stats.total_records, 1)) * 100 if stats.total_records else 0
            punctuality_rate = ((stats.present_count - stats.late_count) / max(stats.present_count, 1)) * 100 if stats.present_count else 0
            
            comparison_data.append({
                "department": stats.department,
                "total_employees": stats.total_employees,
                "attendance_rate": round(attendance_rate, 2),
                "punctuality_rate": round(punctuality_rate, 2),
                "avg_hours": round(stats.avg_hours or 0, 2),
                "overtime_rate": round((stats.overtime_count / max(stats.total_records, 1)) * 100, 2) if stats.total_records else 0
            })
        
        return {
            "departments": comparison_data,
            "period": f"{start_date} to {end_date}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting department comparison: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get department comparison"
        )

@router.get("/monthly-summary")
async def get_monthly_summary(
    year: int = Query(default=None),
    month: int = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly attendance summary"""
    try:
        # Check permissions
        if not current_user.can_view_analytics():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Default to current month
        today = date.today()
        if not year:
            year = today.year
        if not month:
            month = today.month
        
        # Get month date range
        start_date = date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = date(year, month, last_day)
        
        # Get attendance records for the month
        records = db.query(AttendanceRecord).filter(
            and_(
                AttendanceRecord.date >= start_date,
                AttendanceRecord.date <= end_date
            )
        ).all()
        
        # Calculate statistics
        total_records = len(records)
        present_records = len([r for r in records if r.status in ['present', 'late', 'overtime']])
        late_records = len([r for r in records if r.status == 'late'])
        overtime_records = len([r for r in records if r.status == 'overtime'])
        absent_records = len([r for r in records if r.status == 'absent'])
        
        total_hours = sum([r.total_hours or 0 for r in records])
        avg_hours = total_hours / max(present_records, 1)
        
        # Daily breakdown
        daily_stats = {}
        for i in range(1, last_day + 1):
            day_date = date(year, month, i)
            day_records = [r for r in records if r.date == day_date]
            
            daily_stats[i] = {
                "date": day_date.isoformat(),
                "total": len(day_records),
                "present": len([r for r in day_records if r.status in ['present', 'late', 'overtime']]),
                "late": len([r for r in day_records if r.status == 'late']),
                "absent": len([r for r in day_records if r.status == 'absent'])
            }
        
        return {
            "year": year,
            "month": month,
            "summary": {
                "total_records": total_records,
                "present_records": present_records,
                "late_records": late_records,
                "overtime_records": overtime_records,
                "absent_records": absent_records,
                "total_hours": round(total_hours, 2),
                "avg_hours": round(avg_hours, 2),
                "attendance_rate": round((present_records / max(total_records, 1)) * 100, 2)
            },
            "daily_breakdown": daily_stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting monthly summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get monthly summary"
        )

@router.get("/overtime-analysis")
async def get_overtime_analysis(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overtime analysis"""
    try:
        # Check permissions
        if not current_user.can_view_analytics():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Default to current month
        if not start_date or not end_date:
            today = date.today()
            start_date = today.replace(day=1)
            end_date = today
        
        # Get overtime records
        overtime_records = db.query(AttendanceRecord).join(User).filter(
            and_(
                AttendanceRecord.date >= start_date,
                AttendanceRecord.date <= end_date,
                or_(
                    AttendanceRecord.status == 'overtime',
                    AttendanceRecord.total_hours > 8
                )
            )
        ).all()
        
        # Calculate overtime statistics
        total_overtime_hours = sum([
            max((r.total_hours or 0) - 8, 0) for r in overtime_records
        ])
        
        # Top overtime employees
        user_overtime = {}
        for record in overtime_records:
            user_id = record.user_id
            overtime_hours = max((record.total_hours or 0) - 8, 0)
            
            if user_id not in user_overtime:
                user_overtime[user_id] = {
                    "user_name": record.user.name,
                    "employee_id": record.user.employee_id,
                    "department": record.user.department,
                    "total_overtime": 0,
                    "overtime_days": 0
                }
            
            user_overtime[user_id]["total_overtime"] += overtime_hours
            user_overtime[user_id]["overtime_days"] += 1
        
        # Sort by total overtime
        top_overtime = sorted(
            user_overtime.values(),
            key=lambda x: x["total_overtime"],
            reverse=True
        )[:10]
        
        # Department-wise overtime
        dept_overtime = {}
        for record in overtime_records:
            dept = record.user.department
            overtime_hours = max((record.total_hours or 0) - 8, 0)
            
            if dept not in dept_overtime:
                dept_overtime[dept] = {"total_hours": 0, "count": 0}
            
            dept_overtime[dept]["total_hours"] += overtime_hours
            dept_overtime[dept]["count"] += 1
        
        return {
            "period": f"{start_date} to {end_date}",
            "summary": {
                "total_overtime_hours": round(total_overtime_hours, 2),
                "total_overtime_instances": len(overtime_records),
                "avg_overtime_per_instance": round(total_overtime_hours / max(len(overtime_records), 1), 2)
            },
            "top_overtime_employees": top_overtime,
            "department_breakdown": dept_overtime
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting overtime analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get overtime analysis"
        )

@router.get("/attendance-patterns")
async def get_attendance_patterns(
    user_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get attendance patterns analysis"""
    try:
        # Check permissions
        if user_id and not current_user.can_view_user(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # If no user_id provided and user is not admin, use current user
        if not user_id and not current_user.can_view_analytics():
            user_id = current_user.id
        
        # Build query
        query = db.query(AttendanceRecord)
        if user_id:
            query = query.filter(AttendanceRecord.user_id == user_id)
        
        # Get last 3 months of data
        three_months_ago = date.today() - timedelta(days=90)
        records = query.filter(AttendanceRecord.date >= three_months_ago).all()
        
        # Analyze patterns
        patterns = {
            "weekly_pattern": [0] * 7,  # Monday to Sunday
            "monthly_pattern": {},
            "late_pattern": [0] * 7,
            "early_checkout_pattern": [0] * 7,
            "avg_checkin_time": {},
            "avg_checkout_time": {}
        }
        
        for record in records:
            weekday = record.date.weekday()  # 0 = Monday
            
            # Weekly attendance pattern
            if record.status in ['present', 'late', 'overtime']:
                patterns["weekly_pattern"][weekday] += 1
            
            # Late pattern
            if record.status == 'late':
                patterns["late_pattern"][weekday] += 1
            
            # Early checkout pattern
            if record.status == 'early_departure':
                patterns["early_checkout_pattern"][weekday] += 1
            
            # Check-in time patterns
            if record.check_in_time:
                day_name = calendar.day_name[weekday]
                if day_name not in patterns["avg_checkin_time"]:
                    patterns["avg_checkin_time"][day_name] = []
                patterns["avg_checkin_time"][day_name].append(
                    record.check_in_time.hour + record.check_in_time.minute / 60
                )
            
            # Check-out time patterns
            if record.check_out_time:
                day_name = calendar.day_name[weekday]
                if day_name not in patterns["avg_checkout_time"]:
                    patterns["avg_checkout_time"][day_name] = []
                patterns["avg_checkout_time"][day_name].append(
                    record.check_out_time.hour + record.check_out_time.minute / 60
                )
        
        # Calculate averages
        for day in patterns["avg_checkin_time"]:
            times = patterns["avg_checkin_time"][day]
            patterns["avg_checkin_time"][day] = round(sum(times) / len(times), 2) if times else 0
        
        for day in patterns["avg_checkout_time"]:
            times = patterns["avg_checkout_time"][day]
            patterns["avg_checkout_time"][day] = round(sum(times) / len(times), 2) if times else 0
        
        return {
            "user_id": user_id,
            "analysis_period": f"{three_months_ago} to {date.today()}",
            "patterns": patterns
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting attendance patterns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get attendance patterns"
        )