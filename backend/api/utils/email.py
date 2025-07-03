"""
Enhanced Email Service for University System
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
import logging
from jinja2 import Environment, FileSystemLoader, Template
import os
from pathlib import Path

from config.settings import settings

logger = logging.getLogger(__name__)

class UniversityEmailService:
    """Enhanced email service for university notifications"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_from = settings.EMAIL_FROM
        self.university_name = settings.UNIVERSITY_NAME
        
        # Setup Jinja2 for email templates
        template_dir = Path("templates/email")
        template_dir.mkdir(parents=True, exist_ok=True)
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )
        
        # Create default templates if they don't exist
        self._create_default_templates()
    
    def _create_default_templates(self):
        """Create default email templates"""
        templates = {
            "enrollment_notification.html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Course Enrollment - {{ university_name }}</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .header { background-color: #1e40af; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .footer { background-color: #f3f4f6; padding: 15px; text-align: center; font-size: 12px; }
        .course-info { background-color: #e0e7ff; padding: 15px; border-radius: 5px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ university_name }}</h1>
        <h2>Course Enrollment Notification</h2>
    </div>
    
    <div class="content">
        <p>Dear {{ student_name }},</p>
        
        <p>You have been successfully enrolled in the following course:</p>
        
        <div class="course-info">
            <h3>{{ course_code }} - {{ course_title }}</h3>
            <p><strong>Lecturer:</strong> {{ lecturer_name }}</p>
            <p><strong>Schedule:</strong> {{ schedule }}</p>
            <p><strong>Classroom:</strong> {{ classroom }}</p>
        </div>
        
        <p><strong>Important:</strong> Please visit your lecturer to register your face for attendance marking before the next class.</p>
        
        <p>If you have any questions, please contact your lecturer or the academic office.</p>
        
        <p>Best regards,<br>{{ university_name }} Academic Office</p>
    </div>
    
    <div class="footer">
        <p>© {{ current_year }} {{ university_name }}. All rights reserved.</p>
    </div>
</body>
</html>
            """,
            
            "face_registration_reminder.html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Face Registration Required - {{ university_name }}</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .header { background-color: #dc2626; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .footer { background-color: #f3f4f6; padding: 15px; text-align: center; font-size: 12px; }
        .warning { background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ university_name }}</h1>
        <h2>Face Registration Required</h2>
    </div>
    
    <div class="content">
        <p>Dear {{ student_name }},</p>
        
        <div class="warning">
            <p><strong>Action Required:</strong> Your face registration for attendance marking is still pending.</p>
        </div>
        
        <p>To mark attendance for your courses, you must first register your face with your lecturer.</p>
        
        <p><strong>Please contact:</strong></p>
        <ul>
            <li><strong>Lecturer:</strong> {{ lecturer_name }}</li>
            <li><strong>Email:</strong> {{ lecturer_email }}</li>
            <li><strong>Office:</strong> {{ lecturer_office }}</li>
        </ul>
        
        <p>Face registration is mandatory before you can participate in attendance marking.</p>
        
        <p>Best regards,<br>{{ university_name }} Academic Office</p>
    </div>
    
    <div class="footer">
        <p>© {{ current_year }} {{ university_name }}. All rights reserved.</p>
    </div>
</body>
</html>
            """,
            
            "attendance_alert.html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Attendance Alert - {{ university_name }}</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .header { background-color: #f59e0b; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .footer { background-color: #f3f4f6; padding: 15px; text-align: center; font-size: 12px; }
        .alert { background-color: #fee2e2; border-left: 4px solid #dc2626; padding: 15px; margin: 15px 0; }
        .stats { background-color: #f0f9ff; padding: 15px; border-radius: 5px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ university_name }}</h1>
        <h2>Attendance Performance Alert</h2>
    </div>
    
    <div class="content">
        <p>Dear {{ student_name }},</p>
        
        <div class="alert">
            <p><strong>Warning:</strong> Your attendance rate is below the minimum requirement.</p>
        </div>
        
        <div class="stats">
            <h3>Your Attendance Summary</h3>
            <ul>
                <li><strong>Overall Attendance Rate:</strong> {{ attendance_rate }}%</li>
                <li><strong>Classes Attended:</strong> {{ classes_attended }}</li>
                <li><strong>Total Classes:</strong> {{ total_classes }}</li>
                <li><strong>Minimum Required:</strong> {{ minimum_required }}%</li>
            </ul>
        </div>
        
        <p>To avoid academic penalties, please:</p>
        <ul>
            <li>Attend all remaining classes</li>
            <li>Contact your lecturer if you have genuine reasons for absences</li>
            <li>Meet with the academic advisor if needed</li>
        </ul>
        
        <p>Your academic success is important to us. Please take immediate action to improve your attendance.</p>
        
        <p>Best regards,<br>{{ university_name }} Academic Office</p>
    </div>
    
    <div class="footer">
        <p>© {{ current_year }} {{ university_name }}. All rights reserved.</p>
    </div>
</body>
</html>
            """
        }
        
        template_dir = Path("templates/email")
        for filename, content in templates.items():
            template_path = template_dir / filename
            if not template_path.exists():
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
    
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Send email with optional HTML body and attachments"""
        
        if not self.smtp_user or not self.smtp_password:
            logger.warning("Email service not configured - SMTP credentials missing")
            return False
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.university_name} <{self.email_from}>"
            message["To"] = ", ".join(to_emails)
            
            # Add text part
            text_part = MIMEText(body, "plain", "utf-8")
            message.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, "html", "utf-8")
                message.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment['content'])
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment["filename"]}'
                    )
                    message.attach(part)
            
            # Create SMTP session and send
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.email_from, to_emails, message.as_string())
            
            logger.info(f"Email sent successfully to {to_emails}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_enrollment_notification(
        self,
        student_email: str,
        student_name: str,
        course_code: str,
        course_title: str,
        lecturer_name: str,
        schedule: Optional[str] = None,
        classroom: Optional[str] = None
    ) -> bool:
        """Send course enrollment notification"""
        
        try:
            template = self.jinja_env.get_template("enrollment_notification.html")
            
            html_content = template.render(
                university_name=self.university_name,
                student_name=student_name,
                course_code=course_code,
                course_title=course_title,
                lecturer_name=lecturer_name,
                schedule=schedule or "TBA",
                classroom=classroom or "TBA",
                current_year=datetime.now().year
            )
            
            # Plain text version
            text_content = f"""
Dear {student_name},

You have been successfully enrolled in the following course:

Course: {course_code} - {course_title}
Lecturer: {lecturer_name}
Schedule: {schedule or 'TBA'}
Classroom: {classroom or 'TBA'}

Important: Please visit your lecturer to register your face for attendance marking.

Best regards,
{self.university_name} Academic Office
            """
            
            subject = f"Enrolled in {course_code} - {self.university_name}"
            
            return self.send_email(
                to_emails=[student_email],
                subject=subject,
                body=text_content.strip(),
                html_body=html_content
            )
            
        except Exception as e:
            logger.error(f"Error sending enrollment notification: {e}")
            return False
    
    def send_face_registration_reminder(
        self,
        student_email: str,
        student_name: str,
        lecturer_name: str,
        lecturer_email: str,
        lecturer_office: Optional[str] = None
    ) -> bool:
        """Send face registration reminder"""
        
        try:
            template = self.jinja_env.get_template("face_registration_reminder.html")
            
            html_content = template.render(
                university_name=self.university_name,
                student_name=student_name,
                lecturer_name=lecturer_name,
                lecturer_email=lecturer_email,
                lecturer_office=lecturer_office or "Contact lecturer",
                current_year=datetime.now().year
            )
            
            # Plain text version
            text_content = f"""
Dear {student_name},

Action Required: Your face registration for attendance marking is still pending.

Please contact your lecturer to complete the face registration process:

Lecturer: {lecturer_name}
Email: {lecturer_email}
Office: {lecturer_office or 'Contact lecturer'}

Face registration is required before you can mark attendance.

Best regards,
{self.university_name} Academic Office
            """
            
            subject = f"Face Registration Required - {self.university_name}"
            
            return self.send_email(
                to_emails=[student_email],
                subject=subject,
                body=text_content.strip(),
                html_body=html_content
            )
            
        except Exception as e:
            logger.error(f"Error sending face registration reminder: {e}")
            return False
    
    def send_attendance_alert(
        self,
        student_email: str,
        student_name: str,
        attendance_rate: float,
        classes_attended: int,
        total_classes: int,
        minimum_required: float = 75.0
    ) -> bool:
        """Send attendance performance alert"""
        
        try:
            template = self.jinja_env.get_template("attendance_alert.html")
            
            html_content = template.render(
                university_name=self.university_name,
                student_name=student_name,
                attendance_rate=round(attendance_rate, 1),
                classes_attended=classes_attended,
                total_classes=total_classes,
                minimum_required=minimum_required,
                current_year=datetime.now().year
            )
            
            # Plain text version
            text_content = f"""
Dear {student_name},

Warning: Your attendance rate is below the minimum requirement.

Your Attendance Summary:
- Overall Attendance Rate: {attendance_rate:.1f}%
- Classes Attended: {classes_attended}
- Total Classes: {total_classes}
- Minimum Required: {minimum_required}%

Please take immediate action to improve your attendance.

Best regards,
{self.university_name} Academic Office
            """
            
            subject = f"Attendance Alert - {self.university_name}"
            
            return self.send_email(
                to_emails=[student_email],
                subject=subject,
                body=text_content.strip(),
                html_body=html_content
            )
            
        except Exception as e:
            logger.error(f"Error sending attendance alert: {e}")
            return False
    
    def send_bulk_notification(
        self,
        recipients: List[Dict[str, str]],
        subject_template: str,
        body_template: str,
        template_vars: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send bulk notifications with template variables"""
        
        results = {
            "success": [],
            "failed": [],
            "total": len(recipients)
        }
        
        for recipient in recipients:
            try:
                # Merge recipient data with template vars
                vars_merged = {**template_vars, **recipient}
                
                # Render templates
                subject = Template(subject_template).render(**vars_merged)
                body = Template(body_template).render(**vars_merged)
                
                success = self.send_email(
                    to_emails=[recipient["email"]],
                    subject=subject,
                    body=body
                )
                
                if success:
                    results["success"].append(recipient["email"])
                else:
                    results["failed"].append(recipient["email"])
                    
            except Exception as e:
                logger.error(f"Error sending to {recipient.get('email', 'unknown')}: {e}")
                results["failed"].append(recipient.get("email", "unknown"))
        
        logger.info(f"Bulk email results: {len(results['success'])} success, {len(results['failed'])} failed")
        return results
    
    def test_connection(self) -> bool:
        """Test email service connection"""
        
        if not self.smtp_user or not self.smtp_password:
            logger.error("Email credentials not configured")
            return False
        
        try:
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_user, self.smtp_password)
            
            logger.info("Email service connection successful")
            return True
            
        except Exception as e:
            logger.error(f"Email service connection failed: {e}")
            return False

# Create global instance
email_service = UniversityEmailService() if settings.SMTP_USER else None