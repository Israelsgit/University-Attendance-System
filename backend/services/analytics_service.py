"""
Analytics Service
Advanced analytics and reporting for attendance data
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
from api.models.user import User
from api.models.attendance import AttendanceRecord

# Configure logging
logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for attendance analytics and insights"""
    
    def __init__(self):
        self.cache = {}  # Simple in-memory cache
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
    
    def calculate_attendance_trends(
        self,
        start_date: date,
        end_date: date,
        department: Optional[str] = None,
        user_id: Optional[int] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Calculate attendance trends over time"""
        
        cache_key = self._get_cache_key(
            "attendance_trends",
            start_date=start_date,
            end_date=end_date,
            department=department,
            user_id=user_id
        )
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        if not db:
            db = SessionLocal()
        
        try:
            # Build base query
            query = db.query(AttendanceRecord).filter(
                and_(
                    AttendanceRecord.date >= start_date,
                    AttendanceRecord.date <= end_date
                )
            )
            
            if user_id:
                query = query.filter(AttendanceRecord.user_id == user_id)
            elif department:
                query = query.join(User).filter(User.department == department)
            
            records = query.all()
            
            # Group by date
            daily_stats = defaultdict(lambda: {
                'total': 0, 'present': 0, 'late': 0, 'absent': 0, 'overtime': 0
            })
            
            for record in records:
                date_str = record.date.isoformat()
                daily_stats[date_str]['total'] += 1
                
                if record.status == 'present':
                    daily_stats[date_str]['present'] += 1
                elif record.status == 'late':
                    daily_stats[date_str]['late'] += 1
                elif record.status == 'absent':
                    daily_stats[date_str]['absent'] += 1
                elif record.status == 'overtime':
                    daily_stats[date_str]['overtime'] += 1
            
            # Calculate trends
            trends = []
            for date_str, stats in sorted(daily_stats.items()):
                attendance_rate = (stats['present'] + stats['late'] + stats['overtime']) / max(stats['total'], 1) * 100
                trends.append({
                    'date': date_str,
                    'attendance_rate': round(attendance_rate, 2),
                    'total_employees': stats['total'],
                    'present': stats['present'],
                    'late': stats['late'],
                    'absent': stats['absent'],
                    'overtime': stats['overtime']
                })
            
            # Calculate moving averages
            if len(trends) >= 7:
                for i in range(6, len(trends)):
                    week_rates = [trends[j]['attendance_rate'] for j in range(i-6, i+1)]
                    trends[i]['moving_avg_7d'] = round(sum(week_rates) / 7, 2)
            
            result = {
                'period': f"{start_date} to {end_date}",
                'trends': trends,
                'summary': {
                    'total_records': len(records),
                    'avg_attendance_rate': round(np.mean([t['attendance_rate'] for t in trends]), 2) if trends else 0,
                    'best_day': max(trends, key=lambda x: x['attendance_rate']) if trends else None,
                    'worst_day': min(trends, key=lambda x: x['attendance_rate']) if trends else None
                }
            }
            
            # Cache result
            self.cache[cache_key] = {
                'data': result,
                'timestamp': datetime.now()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error calculating attendance trends: {e}")
            return {'trends': [], 'summary': {}}
        finally:
            db.close()
    
    def analyze_punctuality_patterns(
        self,
        user_id: Optional[int] = None,
        department: Optional[str] = None,
        days_back: int = 90,
        db: Session = None
    ) -> Dict[str, Any]:
        """Analyze punctuality patterns"""
        
        if not db:
            db = SessionLocal()
        
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back)
            
            # Build query
            query = db.query(AttendanceRecord).filter(
                and_(
                    AttendanceRecord.date >= start_date,
                    AttendanceRecord.check_in_time.isnot(None)
                )
            )
            
            if user_id:
                query = query.filter(AttendanceRecord.user_id == user_id)
            elif department:
                query = query.join(User).filter(User.department == department)
            
            records = query.all()
            
            # Analyze check-in times
            checkin_analysis = {
                'by_hour': defaultdict(int),
                'by_weekday': defaultdict(int),
                'late_patterns': defaultdict(int),
                'early_patterns': defaultdict(int)
            }
            
            from datetime import time as dt_time
            work_start = dt_time(9, 0)  # 9:00 AM default
            
            for record in records:
                check_in = record.check_in_time
                weekday = record.date.weekday()
                
                # Hour analysis
                checkin_analysis['by_hour'][check_in.hour] += 1
                
                # Weekday analysis
                checkin_analysis['by_weekday'][weekday] += 1
                
                # Late/early patterns
                if check_in > work_start:
                    minutes_late = (datetime.combine(date.today(), check_in) - 
                                  datetime.combine(date.today(), work_start)).seconds // 60
                    if minutes_late <= 15:
                        checkin_analysis['late_patterns']['0-15_min'] += 1
                    elif minutes_late <= 30:
                        checkin_analysis['late_patterns']['15-30_min'] += 1
                    elif minutes_late <= 60:
                        checkin_analysis['late_patterns']['30-60_min'] += 1
                    else:
                        checkin_analysis['late_patterns']['60+_min'] += 1
                else:
                    minutes_early = (datetime.combine(date.today(), work_start) - 
                                   datetime.combine(date.today(), check_in)).seconds // 60
                    if minutes_early <= 15:
                        checkin_analysis['early_patterns']['0-15_min'] += 1
                    elif minutes_early <= 30:
                        checkin_analysis['early_patterns']['15-30_min'] += 1
                    else:
                        checkin_analysis['early_patterns']['30+_min'] += 1
            
            # Calculate statistics
            total_checkins = len(records)
            on_time_count = sum(1 for r in records if r.check_in_time <= work_start)
            late_count = total_checkins - on_time_count
            
            return {
                'period': f"{start_date} to {end_date}",
                'summary': {
                    'total_checkins': total_checkins,
                    'on_time_count': on_time_count,
                    'late_count': late_count,
                    'punctuality_rate': round((on_time_count / max(total_checkins, 1)) * 100, 2)
                },
                'patterns': {
                    'hourly_distribution': dict(checkin_analysis['by_hour']),
                    'weekday_distribution': dict(checkin_analysis['by_weekday']),
                    'late_patterns': dict(checkin_analysis['late_patterns']),
                    'early_patterns': dict(checkin_analysis['early_patterns'])
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing punctuality patterns: {e}")
            return {}
        finally:
            db.close()
    
    def generate_department_comparison(
        self,
        start_date: date,
        end_date: date,
        metrics: List[str] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Generate department-wise comparison"""
        
        if not metrics:
            metrics = ['attendance_rate', 'punctuality_rate', 'avg_hours', 'overtime_rate']
        
        if not db:
            db = SessionLocal()
        
        try:
            # Get all departments
            departments = db.query(User.department).filter(
                User.is_active == True
            ).distinct().all()
            
            comparison_data = []
            
            for (dept,) in departments:
                # Get department users
                dept_users = db.query(User).filter(
                    and_(User.department == dept, User.is_active == True)
                ).all()
                
                if not dept_users:
                    continue
                
                # Get attendance records for department
                user_ids = [u.id for u in dept_users]
                records = db.query(AttendanceRecord).filter(
                    and_(
                        AttendanceRecord.user_id.in_(user_ids),
                        AttendanceRecord.date >= start_date,
                        AttendanceRecord.date <= end_date
                    )
                ).all()
                
                # Calculate metrics
                total_records = len(records)
                present_records = len([r for r in records if r.status in ['present', 'late', 'overtime']])
                late_records = len([r for r in records if r.status == 'late'])
                overtime_records = len([r for r in records if r.status == 'overtime'])
                
                total_hours = sum([r.total_hours or 0 for r in records if r.total_hours])
                avg_hours = total_hours / max(present_records, 1)
                
                dept_metrics = {
                    'department': dept,
                    'total_employees': len(dept_users),
                    'total_records': total_records,
                    'attendance_rate': round((present_records / max(total_records, 1)) * 100, 2),
                    'punctuality_rate': round(((present_records - late_records) / max(present_records, 1)) * 100, 2),
                    'avg_hours': round(avg_hours, 2),
                    'overtime_rate': round((overtime_records / max(total_records, 1)) * 100, 2)
                }
                
                comparison_data.append(dept_metrics)
            
            # Rank departments
            for metric in metrics:
                if metric in ['attendance_rate', 'punctuality_rate', 'avg_hours']:
                    # Higher is better
                    sorted_depts = sorted(comparison_data, key=lambda x: x[metric], reverse=True)
                else:
                    # Lower might be better for overtime_rate
                    sorted_depts = sorted(comparison_data, key=lambda x: x[metric])
                
                for i, dept in enumerate(sorted_depts):
                    dept[f'{metric}_rank'] = i + 1
            
            return {
                'period': f"{start_date} to {end_date}",
                'departments': comparison_data,
                'best_performing': {
                    metric: max(comparison_data, key=lambda x: x[metric]) 
                    for metric in ['attendance_rate', 'punctuality_rate']
                },
                'insights': self._generate_department_insights(comparison_data)
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating department comparison: {e}")
            return {}
        finally:
            db.close()
    
    def _generate_department_insights(self, dept_data: List[Dict]) -> List[str]:
        """Generate insights from department comparison data"""
        insights = []
        
        if not dept_data:
            return insights
        
        # Find best and worst performing departments
        best_attendance = max(dept_data, key=lambda x: x['attendance_rate'])
        worst_attendance = min(dept_data, key=lambda x: x['attendance_rate'])
        
        insights.append(
            f"{best_attendance['department']} has the highest attendance rate at {best_attendance['attendance_rate']}%"
        )
        
        if worst_attendance['attendance_rate'] < 80:
            insights.append(
                f"{worst_attendance['department']} needs attention with {worst_attendance['attendance_rate']}% attendance"
            )
        
        # Punctuality insights
        best_punctuality = max(dept_data, key=lambda x: x['punctuality_rate'])
        insights.append(
            f"{best_punctuality['department']} has the best punctuality at {best_punctuality['punctuality_rate']}%"
        )
        
        # Overtime insights
        high_overtime_depts = [d for d in dept_data if d['overtime_rate'] > 10]
        if high_overtime_depts:
            dept_names = [d['department'] for d in high_overtime_depts]
            insights.append(
                f"High overtime rates detected in: {', '.join(dept_names)}"
            )
        
        return insights
    
    def predict_attendance_trends(
        self,
        user_id: Optional[int] = None,
        department: Optional[str] = None,
        days_ahead: int = 7,
        db: Session = None
    ) -> Dict[str, Any]:
        """Predict future attendance trends based on historical data"""
        
        if not db:
            db = SessionLocal()
        
        try:
            # Get historical data (last 90 days)
            end_date = date.today()
            start_date = end_date - timedelta(days=90)
            
            query = db.query(AttendanceRecord).filter(
                AttendanceRecord.date >= start_date
            )
            
            if user_id:
                query = query.filter(AttendanceRecord.user_id == user_id)
            elif department:
                query = query.join(User).filter(User.department == department)
            
            records = query.all()
            
            # Group by weekday and calculate averages
            weekday_stats = defaultdict(lambda: {'total': 0, 'present': 0})
            
            for record in records:
                weekday = record.date.weekday()
                weekday_stats[weekday]['total'] += 1
                if record.status in ['present', 'late', 'overtime']:
                    weekday_stats[weekday]['present'] += 1
            
            # Calculate attendance rates by weekday
            weekday_rates = {}
            for weekday in range(7):  # 0 = Monday, 6 = Sunday
                stats = weekday_stats[weekday]
                if stats['total'] > 0:
                    weekday_rates[weekday] = stats['present'] / stats['total']
                else:
                    weekday_rates[weekday] = 0.85  # Default assumption
            
            # Generate predictions
            predictions = []
            current_date = date.today() + timedelta(days=1)
            
            for i in range(days_ahead):
                pred_date = current_date + timedelta(days=i)
                weekday = pred_date.weekday()
                
                # Skip weekends if it's a business
                if weekday >= 5:  # Saturday, Sunday
                    continue
                
                expected_rate = weekday_rates.get(weekday, 0.85)
                
                # Apply some seasonal adjustments (simplified)
                month = pred_date.month
                if month in [12, 1]:  # Holiday season
                    expected_rate *= 0.9
                elif month in [6, 7, 8]:  # Summer months
                    expected_rate *= 0.95
                
                predictions.append({
                    'date': pred_date.isoformat(),
                    'weekday': pred_date.strftime('%A'),
                    'expected_attendance_rate': round(expected_rate * 100, 2),
                    'confidence': self._calculate_prediction_confidence(weekday_stats[weekday]['total'])
                })
            
            return {
                'predictions': predictions,
                'historical_period': f"{start_date} to {end_date}",
                'methodology': 'Weekday-based historical average with seasonal adjustments',
                'disclaimer': 'Predictions are estimates based on historical patterns'
            }
            
        except Exception as e:
            logger.error(f"❌ Error predicting attendance trends: {e}")
            return {'predictions': []}
        finally:
            db.close()
    
    def _calculate_prediction_confidence(self, sample_size: int) -> str:
        """Calculate confidence level based on sample size"""
        if sample_size >= 10:
            return "High"
        elif sample_size >= 5:
            return "Medium"
        else:
            return "Low"
    
    def analyze_absenteeism_patterns(
        self,
        start_date: date,
        end_date: date,
        db: Session = None
    ) -> Dict[str, Any]:
        """Analyze absenteeism patterns and identify concerning trends"""
        
        if not db:
            db = SessionLocal()
        
        try:
            # Get absence records
            absence_records = db.query(AttendanceRecord).filter(
                and_(
                    AttendanceRecord.date >= start_date,
                    AttendanceRecord.date <= end_date,
                    AttendanceRecord.status == 'absent'
                )
            ).all()
            
            # Group by user
            user_absences = defaultdict(list)
            for record in absence_records:
                user_absences[record.user_id].append(record.date)
            
            # Analyze patterns
            patterns = {
                'high_absenteeism_users': [],
                'frequent_monday_absences': [],
                'frequent_friday_absences': [],
                'consecutive_absences': [],
                'seasonal_patterns': defaultdict(int)
            }
            
            for user_id, absence_dates in user_absences.items():
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    continue
                
                absence_count = len(absence_dates)
                total_days = (end_date - start_date).days + 1
                absence_rate = (absence_count / total_days) * 100
                
                # High absenteeism (>20%)
                if absence_rate > 20:
                    patterns['high_absenteeism_users'].append({
                        'user_id': user_id,
                        'name': user.name,
                        'department': user.department,
                        'absence_count': absence_count,
                        'absence_rate': round(absence_rate, 2)
                    })
                
                # Weekday patterns
                monday_absences = sum(1 for d in absence_dates if d.weekday() == 0)
                friday_absences = sum(1 for d in absence_dates if d.weekday() == 4)
                
                if monday_absences >= 3:
                    patterns['frequent_monday_absences'].append({
                        'user_id': user_id,
                        'name': user.name,
                        'monday_absences': monday_absences
                    })
                
                if friday_absences >= 3:
                    patterns['frequent_friday_absences'].append({
                        'user_id': user_id,
                        'name': user.name,
                        'friday_absences': friday_absences
                    })
                
                # Consecutive absences
                sorted_dates = sorted(absence_dates)
                consecutive_count = 1
                max_consecutive = 1
                
                for i in range(1, len(sorted_dates)):
                    if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                        consecutive_count += 1
                        max_consecutive = max(max_consecutive, consecutive_count)
                    else:
                        consecutive_count = 1
                
                if max_consecutive >= 3:
                    patterns['consecutive_absences'].append({
                        'user_id': user_id,
                        'name': user.name,
                        'max_consecutive_days': max_consecutive
                    })
                
                # Seasonal patterns
                for absence_date in absence_dates:
                    month = absence_date.month
                    patterns['seasonal_patterns'][month] += 1
            
            # Calculate overall statistics
            total_employees = db.query(User).filter(User.is_active == True).count()
            total_absences = len(absence_records)
            avg_absence_rate = (total_absences / (total_employees * total_days)) * 100 if total_employees > 0 else 0
            
            return {
                'period': f"{start_date} to {end_date}",
                'summary': {
                    'total_absences': total_absences,
                    'total_employees': total_employees,
                    'avg_absence_rate': round(avg_absence_rate, 2),
                    'employees_with_absences': len(user_absences)
                },
                'patterns': patterns,
                'recommendations': self._generate_absenteeism_recommendations(patterns)
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing absenteeism patterns: {e}")
            return {}
        finally:
            db.close()
    
    def _generate_absenteeism_recommendations(self, patterns: Dict) -> List[str]:
        """Generate recommendations based on absenteeism patterns"""
        recommendations = []
        
        if patterns['high_absenteeism_users']:
            recommendations.append(
                f"Schedule meetings with {len(patterns['high_absenteeism_users'])} employees showing high absenteeism"
            )
        
        if patterns['frequent_monday_absences']:
            recommendations.append(
                "Consider Monday wellness programs or flexible start times"
            )
        
        if patterns['frequent_friday_absences']:
            recommendations.append(
                "Review Friday workload and consider flexible Friday policies"
            )
        
        if patterns['consecutive_absences']:
            recommendations.append(
                "Implement return-to-work interviews for extended absences"
            )
        
        # Seasonal recommendations
        seasonal = patterns['seasonal_patterns']
        if seasonal:
            peak_month = max(seasonal.items(), key=lambda x: x[1])
            recommendations.append(
                f"Plan for higher absence rates in month {peak_month[0]} based on historical data"
            )
        
        return recommendations
    
    def generate_executive_dashboard(
        self,
        target_date: date = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Generate executive-level dashboard data"""
        
        if not target_date:
            target_date = date.today()
        
        if not db:
            db = SessionLocal()
        
        try:
            # Current month data
            month_start = target_date.replace(day=1)
            
            # Key metrics
            total_employees = db.query(User).filter(User.is_active == True).count()
            
            # Today's attendance
            today_records = db.query(AttendanceRecord).filter(
                AttendanceRecord.date == target_date
            ).all()
            
            today_present = len([r for r in today_records if r.check_in_time])
            today_absent = total_employees - today_present
            today_late = len([r for r in today_records if r.status == 'late'])
            
            # Month-to-date metrics
            mtd_records = db.query(AttendanceRecord).filter(
                AttendanceRecord.date >= month_start
            ).all()
            
            mtd_present = len([r for r in mtd_records if r.status in ['present', 'late', 'overtime']])
            mtd_total = len(mtd_records)
            mtd_attendance_rate = (mtd_present / max(mtd_total, 1)) * 100
            
            # Department breakdown
            dept_stats = db.query(
                User.department,
                func.count(User.id).label('total_emp'),
                func.count(AttendanceRecord.id).label('present_today')
            ).outerjoin(
                AttendanceRecord,
                and_(
                    AttendanceRecord.user_id == User.id,
                    AttendanceRecord.date == target_date,
                    AttendanceRecord.check_in_time.isnot(None)
                )
            ).filter(User.is_active == True).group_by(User.department).all()
            
            department_summary = []
            for stat in dept_stats:
                department_summary.append({
                    'department': stat.department,
                    'total_employees': stat.total_emp,
                    'present_today': stat.present_today,
                    'attendance_rate': round((stat.present_today / max(stat.total_emp, 1)) * 100, 2)
                })
            
            # Trends (last 30 days)
            trend_start = target_date - timedelta(days=30)
            trend_records = db.query(AttendanceRecord).filter(
                AttendanceRecord.date >= trend_start
            ).all()
            
            # Calculate daily attendance rates
            daily_trends = defaultdict(lambda: {'total': 0, 'present': 0})
            for record in trend_records:
                date_str = record.date.isoformat()
                daily_trends[date_str]['total'] += 1
                if record.status in ['present', 'late', 'overtime']:
                    daily_trends[date_str]['present'] += 1
            
            trend_data = []
            for date_str in sorted(daily_trends.keys()):
                stats = daily_trends[date_str]
                rate = (stats['present'] / max(stats['total'], 1)) * 100
                trend_data.append({
                    'date': date_str,
                    'attendance_rate': round(rate, 2)
                })
            
            return {
                'generated_at': datetime.now().isoformat(),
                'target_date': target_date.isoformat(),
                'overview': {
                    'total_employees': total_employees,
                    'today_present': today_present,
                    'today_absent': today_absent,
                    'today_late': today_late,
                    'today_attendance_rate': round((today_present / max(total_employees, 1)) * 100, 2),
                    'mtd_attendance_rate': round(mtd_attendance_rate, 2)
                },
                'department_breakdown': department_summary,
                'attendance_trend': trend_data[-7:],  # Last 7 days
                'alerts': self._generate_executive_alerts(db, target_date),
                'quick_stats': {
                    'best_department': max(department_summary, key=lambda x: x['attendance_rate']) if department_summary else None,
                    'departments_below_80': len([d for d in department_summary if d['attendance_rate'] < 80]),
                    'improvement_from_yesterday': self._calculate_daily_improvement(db, target_date)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating executive dashboard: {e}")
            return {}
        finally:
            db.close()
    
    def _generate_executive_alerts(self, db: Session, target_date: date) -> List[Dict]:
        """Generate alerts for executive dashboard"""
        alerts = []
        
        try:
            # Check for departments with low attendance
            dept_stats = db.query(
                User.department,
                func.count(User.id).label('total_emp'),
                func.count(AttendanceRecord.id).label('present_today')
            ).outerjoin(
                AttendanceRecord,
                and_(
                    AttendanceRecord.user_id == User.id,
                    AttendanceRecord.date == target_date,
                    AttendanceRecord.check_in_time.isnot(None)
                )
            ).filter(User.is_active == True).group_by(User.department).all()
            
            for stat in dept_stats:
                attendance_rate = (stat.present_today / max(stat.total_emp, 1)) * 100
                if attendance_rate < 70:
                    alerts.append({
                        'type': 'low_attendance',
                        'severity': 'high',
                        'message': f"{stat.department} has only {attendance_rate:.1f}% attendance today",
                        'department': stat.department
                    })
            
            # Check for high absenteeism trend
            last_week = target_date - timedelta(days=7)
            week_records = db.query(AttendanceRecord).filter(
                AttendanceRecord.date >= last_week
            ).all()
            
            total_expected = db.query(User).filter(User.is_active == True).count() * 7
            present_count = len([r for r in week_records if r.status in ['present', 'late', 'overtime']])
            week_attendance = (present_count / max(total_expected, 1)) * 100
            
            if week_attendance < 80:
                alerts.append({
                    'type': 'attendance_trend',
                    'severity': 'medium',
                    'message': f"Weekly attendance rate is {week_attendance:.1f}% - below target"
                })
            
        except Exception as e:
            logger.error(f"❌ Error generating alerts: {e}")
        
        return alerts
    
    def _calculate_daily_improvement(self, db: Session, target_date: date) -> float:
        """Calculate improvement from previous day"""
        try:
            yesterday = target_date - timedelta(days=1)
            
            # Today's rate
            today_records = db.query(AttendanceRecord).filter(
                AttendanceRecord.date == target_date
            ).all()
            today_present = len([r for r in today_records if r.check_in_time])
            today_total = db.query(User).filter(User.is_active == True).count()
            today_rate = (today_present / max(today_total, 1)) * 100
            
            # Yesterday's rate
            yesterday_records = db.query(AttendanceRecord).filter(
                AttendanceRecord.date == yesterday
            ).all()
            yesterday_present = len([r for r in yesterday_records if r.check_in_time])
            yesterday_rate = (yesterday_present / max(today_total, 1)) * 100
            
            return round(today_rate - yesterday_rate, 2)
            
        except Exception as e:
            logger.error(f"❌ Error calculating daily improvement: {e}")
            return 0.0

# Create service instance
analytics_service = AnalyticsService()

# Export for use in other modules
__all__ = ['AnalyticsService', 'analytics_service']