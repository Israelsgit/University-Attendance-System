"""
Attendance Routes
Handles attendance check-in/check-out, history, and management
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import datetime, date, timedelta
from typing import Optional, List
import logging

from config.database import get_db
from api.models.user import User
from api.models.attendance import AttendanceRecord
from api.schemas.attendance import (
    AttendanceResponse, AttendanceCreate, AttendanceUpdate,
    AttendanceHistory, AttendanceStats, CheckInOut
)
from api.utils.security import get_current_user
from services.face_recognition import face_recognition_service
from config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.get("/today", response_model=AttendanceResponse)
async def get_today_attendance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get today's attendance record for current user
    """
    try:
        today = date.today()
        
        attendance = db.query(AttendanceRecord).filter(
            and_(
                AttendanceRecord.user_id == current_user.id,
                AttendanceRecord.date == today
            )
        ).first()
        
        if not attendance:
            # Create empty attendance record for today
            attendance = AttendanceRecord(
                user_id=current_user.id,
                date=today,
                status="absent"
            )
        
        return {"attendance": attendance.to_dict()}
        
    except Exception as e:
        logger.error(f"❌ Error getting today's attendance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get today's attendance"
        )

@router.post("/check-in", response_model=CheckInOut)
async def face_check_in(
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check in using face recognition
    """
    try:
        today = date.today()
        now = datetime.now()
        
        # Check if already checked in today
        existing_attendance = db.query(AttendanceRecord).filter(
            and_(
                AttendanceRecord.user_id == current_user.id,
                AttendanceRecord.date == today
            )
        ).first()
        
        if existing_attendance and existing_attendance.check_in_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already checked in today"
            )
        
        # Validate image
        if image.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image format"
            )
        
        # Read image data
        image_data = await image.read()
        
        # Process face recognition
        if current_user.face_encoding:
            # Verify against stored face encoding
            result = face_recognition_service.verify_face_against_user(
                image_data, current_user.face_encoding
            )
            
            if not result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result["error"]
                )
            
            if not result["is_match"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Face verification failed. Confidence: {result['confidence']:.2f}"
                )
            
            confidence = result["confidence"]
        else:
            # Process with general face recognition system
            result = face_recognition_service.process_image(image_data)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result["error"]
                )
            
            recognition = result["recognition"]
            if not recognition["recognized"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Face not recognized. Confidence: {recognition['confidence']:.2f}"
                )
            
            confidence = recognition["confidence"]
        
        # Determine status based on time
        work_start = datetime.strptime(settings.WORK_START_TIME, "%H:%M").time()
        late_threshold = (datetime.combine(today, work_start) + 
                         timedelta(minutes=settings.LATE_THRESHOLD_MINUTES)).time()
        
        if now.time() > late_threshold:
            status_value = "late"
        else:
            status_value = "present"
        
        # Create or update attendance record
        if existing_attendance:
            existing_attendance.check_in_time = now.time()
            existing_attendance.status = status_value
            existing_attendance.check_in_method = "face_recognition"
            existing_attendance.face_confidence = confidence
            existing_attendance.location = "Main Office"  # Can be dynamic
            attendance = existing_attendance
        else:
            attendance = AttendanceRecord(
                user_id=current_user.id,
                date=today,
                check_in_time=now.time(),
                status=status_value,
                check_in_method="face_recognition",
                face_confidence=confidence,
                location="Main Office"
            )
            db.add(attendance)
        
        db.commit()
        db.refresh(attendance)
        
        logger.info(f"✅ User checked in: {current_user.email} at {now.time()}")
        
        return {
            "success": True,
            "message": "Checked in successfully",
            "timestamp": now.isoformat(),
            "status": status_value,
            "confidence": confidence,
            "location": "Main Office"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Check-in error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Check-in failed"
        )

@router.post("/check-out", response_model=CheckInOut)
async def face_check_out(
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check out using face recognition
    """
    try:
        today = date.today()
        now = datetime.now()
        
        # Check if checked in today
        attendance = db.query(AttendanceRecord).filter(
            and_(
                AttendanceRecord.user_id == current_user.id,
                AttendanceRecord.date == today
            )
        ).first()
        
        if not attendance or not attendance.check_in_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not checked in today"
            )
        
        if attendance.check_out_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already checked out today"
            )
        
        # Validate image
        if image.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image format"
            )
        
        # Read image data
        image_data = await image.read()
        
        # Process face recognition (same logic as check-in)
        if current_user.face_encoding:
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
            result = face_recognition_service.process_image(image_data)
            
            if not result["success"] or not result["recognition"]["recognized"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Face not recognized"
                )
            
            confidence = result["recognition"]["confidence"]
        
        # Calculate total hours
        check_in_datetime = datetime.combine(today, attendance.check_in_time)
        total_hours = (now - check_in_datetime).total_seconds() / 3600
        
        # Determine final status
        work_end = datetime.strptime(settings.WORK_END_TIME, "%H:%M").time()
        early_threshold = (datetime.combine(today, work_end) - 
                          timedelta(minutes=settings.EARLY_DEPARTURE_THRESHOLD_MINUTES)).time()
        
        if total_hours >= 8:
            if total_hours > 9:
                final_status = "overtime"
            else:
                final_status = "present"
        elif now.time() < early_threshold:
            final_status = "early_departure"
        else:
            final_status = attendance.status  # Keep existing status
        
        # Update attendance record
        attendance.check_out_time = now.time()
        attendance.total_hours = round(total_hours, 2)
        attendance.status = final_status
        attendance.check_out_method = "face_recognition"
        
        db.commit()
        db.refresh(attendance)
        
        logger.info(f"✅ User checked out: {current_user.email} at {now.time()}")
        
        return {
            "success": True,
            "message": "Checked out successfully",
            "timestamp": now.isoformat(),
            "status": final_status,
            "confidence": confidence,
            "total_hours": round(total_hours, 2),
            "location": "Main Office"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Check-out error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Check-out failed"
        )

@router.post("/manual-check-in")
async def manual_check_in(
    reason: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manual check-in with reason
    """
    try:
        today = date.today()
        now = datetime.now()
        
        # Check if already checked in
        existing_attendance = db.query(AttendanceRecord).filter(
            and_(
                AttendanceRecord.user_id == current_user.id,
                AttendanceRecord.date == today
            )
        ).first()
        
        if existing_attendance and existing_attendance.check_in_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already checked in today"
            )
        
        # Determine status
        work_start = datetime.strptime(settings.WORK_START_TIME, "%H:%M").time()
        late_threshold = (datetime.combine(today, work_start) + 
                         timedelta(minutes=settings.LATE_THRESHOLD_MINUTES)).time()
        
        status_value = "late" if now.time() > late_threshold else "present"
        
        # Create or update attendance
        if existing_attendance:
            existing_attendance.check_in_time = now.time()
            existing_attendance.status = status_value
            existing_attendance.check_in_method = "manual"
            existing_attendance.notes = reason
            existing_attendance.location = "Main Office"
            attendance = existing_attendance
        else:
            attendance = AttendanceRecord(
                user_id=current_user.id,
                date=today,
                check_in_time=now.time(),
                status=status_value,
                check_in_method="manual",
                notes=reason,
                location="Main Office"
            )
            db.add(attendance)
        
        db.commit()
        db.refresh(attendance)
        
        logger.info(f"✅ Manual check-in: {current_user.email} - {reason}")
        
        return {
            "success": True,
            "message": "Manual check-in recorded",
            "timestamp": now.isoformat(),
            "status": status_value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Manual check-in error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Manual check-in failed"
        )

@router.post("/manual-check-out")
async def manual_check_out(
    reason: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manual check-out with reason
    """
    try:
        today = date.today()
        now = datetime.now()
        
        # Get today's attendance
        attendance = db.query(AttendanceRecord).filter(
            and_(
                AttendanceRecord.user_id == current_user.id,
                AttendanceRecord.date == today
            )
        ).first()
        
        if not attendance or not attendance.check_in_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not checked in today"
            )
        
        if attendance.check_out_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already checked out today"
            )
        
        # Calculate total hours
        check_in_datetime = datetime.combine(today, attendance.check_in_time)
        total_hours = (now - check_in_datetime).total_seconds() / 3600
        
        # Update attendance
        attendance.check_out_time = now.time()
        attendance.total_hours = round(total_hours, 2)
        attendance.check_out_method = "manual"
        if attendance.notes:
            attendance.notes += f" | Check-out: {reason}"
        else:
            attendance.notes = f"Check-out: {reason}"
        
        # Update status if needed
        if total_hours >= 8:
            if total_hours > 9:
                attendance.status = "overtime"
            elif attendance.status == "late":
                pass  # Keep late status
            else:
                attendance.status = "present"
        
        db.commit()
        db.refresh(attendance)
        
        logger.info(f"✅ Manual check-out: {current_user.email} - {reason}")
        
        return {
            "success": True,
            "message": "Manual check-out recorded",
            "timestamp": now.isoformat(),
            "total_hours": round(total_hours, 2)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Manual check-out error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Manual check-out failed"
        )

@router.get("/history", response_model=List[AttendanceHistory])
async def get_attendance_history(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get attendance history with filters
    """
    try:
        query = db.query(AttendanceRecord).filter(
            AttendanceRecord.user_id == current_user.id
        )
        
        # Apply filters
        if start_date:
            query = query.filter(AttendanceRecord.date >= start_date)
        
        if end_date:
            query = query.filter(AttendanceRecord.date <= end_date)
        
        if status:
            query = query.filter(AttendanceRecord.status == status)
        
        # Order by date descending
        query = query.order_by(desc(AttendanceRecord.date))
        
        # Apply pagination
        attendance_records = query.offset(offset).limit(limit).all()
        
        return [record.to_dict() for record in attendance_records]
        
    except Exception as e:
        logger.error(f"❌ Error getting attendance history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get attendance history"
        )

@router.get("/weekly-stats", response_model=AttendanceStats)
async def get_weekly_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get weekly attendance statistics
    """
    try:
        # Get current week dates
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Get this week's attendance
        weekly_records = db.query(AttendanceRecord).filter(
            and_(
                AttendanceRecord.user_id == current_user.id,
                AttendanceRecord.date >= week_start,
                AttendanceRecord.date <= week_end
            )
        ).all()
        
        # Calculate stats
        present_days = len([r for r in weekly_records if r.status in ['present', 'late', 'overtime']])
        total_hours = sum([r.total_hours or 0 for r in weekly_records])
        avg_hours = total_hours / max(present_days, 1)
        
        # Get monthly data for trends
        month_start = today.replace(day=1)
        monthly_records = db.query(AttendanceRecord).filter(
            and_(
                AttendanceRecord.user_id == current_user.id,
                AttendanceRecord.date >= month_start
            )
        ).all()
        
        monthly_present = len([r for r in monthly_records if r.status in ['present', 'late', 'overtime']])
        monthly_total_days = len(monthly_records)
        attendance_rate = (monthly_present / max(monthly_total_days, 1)) * 100
        
        return {
            "present_days": present_days,
            "total_days": 5,  # Working days in a week
            "avg_hours": round(avg_hours, 2),
            "total_hours": round(total_hours, 2),
            "attendance_rate": round(attendance_rate, 2),
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting weekly stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get weekly statistics"
        )

@router.get("/monthly-stats")
async def get_monthly_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get monthly attendance statistics
    """
    try:
        # Get current month
        today = date.today()
        month_start = today.replace(day=1)
        
        # Get this month's records
        monthly_records = db.query(AttendanceRecord).filter(
            and_(
                AttendanceRecord.user_id == current_user.id,
                AttendanceRecord.date >= month_start
            )
        ).all()
        
        # Calculate comprehensive stats
        total_days = len(monthly_records)
        present_days = len([r for r in monthly_records if r.status in ['present', 'late', 'overtime']])
        late_days = len([r for r in monthly_records if r.status == 'late'])
        overtime_days = len([r for r in monthly_records if r.status == 'overtime'])
        absent_days = len([r for r in monthly_records if r.status == 'absent'])
        
        total_hours = sum([r.total_hours or 0 for r in monthly_records])
        avg_hours = total_hours / max(present_days, 1)
        attendance_rate = (present_days / max(total_days, 1)) * 100
        
        # Overtime hours
        overtime_hours = sum([
            (r.total_hours or 0) - 8 for r in monthly_records 
            if r.total_hours and r.total_hours > 8
        ])
        
        return {
            "total_days": total_days,
            "present_days": present_days,
            "absent_days": absent_days,
            "late_days": late_days,
            "overtime_days": overtime_days,
            "total_hours": round(total_hours, 2),
            "avg_hours": round(avg_hours, 2),
            "overtime_hours": round(overtime_hours, 2),
            "attendance_rate": round(attendance_rate, 2),
            "month": month_start.strftime("%Y-%m")
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting monthly stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get monthly statistics"
        )

@router.put("/{attendance_id}")
async def update_attendance(
    attendance_id: int,
    attendance_update: AttendanceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update attendance record (admin/manager only)
    """
    try:
        # Check permissions
        if not current_user.can_manage_attendance():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Get attendance record
        attendance = db.query(AttendanceRecord).filter(
            AttendanceRecord.id == attendance_id
        ).first()
        
        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )
        
        # Update fields
        update_data = attendance_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(attendance, field):
                setattr(attendance, field, value)
        
        # Recalculate total hours if times changed
        if attendance.check_in_time and attendance.check_out_time:
            check_in_dt = datetime.combine(attendance.date, attendance.check_in_time)
            check_out_dt = datetime.combine(attendance.date, attendance.check_out_time)
            total_hours = (check_out_dt - check_in_dt).total_seconds() / 3600
            attendance.total_hours = round(total_hours, 2)
        
        attendance.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(attendance)
        
        logger.info(f"✅ Attendance updated by {current_user.email}: {attendance_id}")
        
        return {"message": "Attendance updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Attendance update error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Attendance update failed"
        )

@router.delete("/{attendance_id}")
async def delete_attendance(
    attendance_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete attendance record (admin only)
    """
    try:
        # Check permissions
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Get and delete attendance record
        attendance = db.query(AttendanceRecord).filter(
            AttendanceRecord.id == attendance_id
        ).first()
        
        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )
        
        db.delete(attendance)
        db.commit()
        
        logger.info(f"✅ Attendance deleted by {current_user.email}: {attendance_id}")
        
        return {"message": "Attendance record deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Attendance deletion error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Attendance deletion failed"
        )