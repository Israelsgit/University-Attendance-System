"""
Email Service for University System
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging
from jinja2 import Template

from config.settings import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Email service for notifications"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_from = settings.EMAIL_FROM
        
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """Send email to recipients"""
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.email_from
            message["To"] = ", ".join(to_emails)
            
            # Add text part
            text_part = MIMEText(body, "plain")
            message.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, "html")
                message.attach(html_part)
            
            # Create SMTP session
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
        lecturer_name: str
    ) -> bool:
        """Send enrollment notification to student"""
        
        subject = f"Enrolled in {course_code} - {settings.UNIVERSITY_NAME}"
        
        body = f"""
Dear {student_name},

You have been successfully enrolled in the following course:

Course: {course_code} - {course_title}
Lecturer: {lecturer_name}
University: {settings.UNIVERSITY_NAME}

Please visit the lecturer to register your face for attendance marking.

Best regards,
{settings.UNIVERSITY_NAME} Academic Office
        """
        
        return self.send_email([student_email], subject, body)
    
    def send_face_registration_reminder(
        self,
        student_email: str,
        student_name: str,
        lecturer_name: str,
        lecturer_email: str
    ) -> bool:
        """Send face registration reminder"""
        
        subject = f"Face Registration Required - {settings.UNIVERSITY_NAME}"
        
        body = f"""
Dear {student_name},

This is a reminder that you need to register your face for attendance marking.

Please contact your lecturer {lecturer_name} ({lecturer_email}) to complete the face registration process.

This is required before you can mark attendance for your courses.

Best regards,
{settings.UNIVERSITY_NAME} Academic Office
        """
        
        return self.send_email([student_email], subject, body)

# Create global instance
email_service = EmailService() if settings.SMTP_USER else None