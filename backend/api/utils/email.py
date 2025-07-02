"""
Email Utilities for AttendanceAI API
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path
import asyncio
import aiofiles
from jinja2 import Environment, FileSystemLoader
from datetime import datetime, date

from config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

class EmailService:
    """Email service for sending notifications"""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        
        # Setup Jinja2 environment for email templates
        template_dir = Path("templates/email")
        template_dir.mkdir(parents=True, exist_ok=True)
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )
    
    def _create_smtp_connection(self):
        """Create SMTP connection"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            return server
        except Exception as e:
            logger.error(f"❌ Failed to create SMTP connection: {e}")
            raise
    
    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None
    ) -> bool:
        """Send email"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # Add text body
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML body if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    await self._add_attachment(msg, file_path)
            
            # Combine all recipients
            all_recipients = to_emails[:]
            if cc_emails:
                all_recipients.extend(cc_emails)
            if bcc_emails:
                all_recipients.extend(bcc_emails)
            
            # Send email
            server = self._create_smtp_connection()
            server.send_message(msg, to_addrs=all_recipients)
            server.quit()
            
            logger.info(f"✅ Email sent successfully to {len(all_recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return False
    
    async def _add_attachment(self, msg: MIMEMultipart, file_path: str):
        """Add attachment to email"""
        try:
            async with aiofiles.open(file_path, 'rb') as f:
                file_data = await f.read()
            
            # Create attachment
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(file_data)
            encoders.encode_base64(attachment)
            
            # Add header
            filename = Path(file_path).name
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename={filename}'
            )
            
            msg.attach(attachment)
            
        except Exception as e:
            logger.error(f"❌ Failed to add attachment {file_path}: {e}")
    
    async def send_template_email(
        self,
        template_name: str,
        to_emails: List[str],
        subject: str,
        template_data: Dict[str, Any],
        attachments: Optional[List[str]] = None
    ) -> bool:
        """Send email using template"""
        try:
            # Load and render HTML template
            try:
                template = self.jinja_env.get_template(f"{template_name}.html")
                html_body = template.render(**template_data)
            except Exception:
                html_body = None
                logger.warning(f"HTML template {template_name}.html not found")
            
            # Create text version
            try:
                text_template = self.jinja_env.get_template(f"{template_name}.txt")
                text_body = text_template.render(**template_data)
            except Exception:
                # Fallback to basic text
                text_body = f"Subject: {subject}\n\nThis is an automated message from AttendanceAI."
                logger.warning(f"Text template {template_name}.txt not found, using fallback")
            
            return await self.send_email(
                to_emails=to_emails,
                subject=subject,
                body=text_body,
                html_body=html_body,
                attachments=attachments
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to send template email: {e}")
            return False
    
    # Specific email methods
    async def send_welcome_email(self, user_email: str, user_name: str, temp_password: str) -> bool:
        """Send welcome email to new user"""
        template_data = {
            'user_name': user_name,
            'user_email': user_email,
            'temp_password': temp_password,
            'login_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/login",
            'support_email': self.from_email,
            'company_name': "AttendanceAI"
        }
        
        return await self.send_template_email(
            template_name="welcome",
            to_emails=[user_email],
            subject="Welcome to AttendanceAI - Your Account Details",
            template_data=template_data
        )
    
    async def send_password_reset_email(self, user_email: str, user_name: str, reset_token: str) -> bool:
        """Send password reset email"""
        template_data = {
            'user_name': user_name,
            'reset_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}",
            'expiry_hours': 24,
            'support_email': self.from_email
        }
        
        return await self.send_template_email(
            template_name="password_reset",
            to_emails=[user_email],
            subject="Password Reset Request - AttendanceAI",
            template_data=template_data
        )
    
    async def send_leave_request_notification(
        self,
        manager_email: str,
        manager_name: str,
        employee_name: str,
        leave_type: str,
        start_date: date,
        end_date: date,
        reason: str,
        request_id: int
    ) -> bool:
        """Send leave request notification to manager"""
        template_data = {
            'manager_name': manager_name,
            'employee_name': employee_name,
            'leave_type': leave_type.replace('_', ' ').title(),
            'start_date': start_date.strftime('%B %d, %Y'),
            'end_date': end_date.strftime('%B %d, %Y'),
            'total_days': (end_date - start_date).days + 1,
            'reason': reason,
            'review_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/admin/leave-requests/{request_id}",
            'dashboard_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/admin/dashboard"
        }
        
        return await self.send_template_email(
            template_name="leave_request",
            to_emails=[manager_email],
            subject=f"Leave Request from {employee_name}",
            template_data=template_data
        )
    
    async def send_leave_approval_email(
        self,
        employee_email: str,
        employee_name: str,
        leave_type: str,
        start_date: date,
        end_date: date,
        approved_by: str,
        status: str
    ) -> bool:
        """Send leave approval/rejection email to employee"""
        template_data = {
            'employee_name': employee_name,
            'leave_type': leave_type.replace('_', ' ').title(),
            'start_date': start_date.strftime('%B %d, %Y'),
            'end_date': end_date.strftime('%B %d, %Y'),
            'status': status.title(),
            'approved_by': approved_by,
            'dashboard_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/dashboard"
        }
        
        subject = f"Leave Request {status.title()} - AttendanceAI"
        template_name = "leave_approval" if status == "approved" else "leave_rejection"
        
        return await self.send_template_email(
            template_name=template_name,
            to_emails=[employee_email],
            subject=subject,
            template_data=template_data
        )
    
    async def send_attendance_reminder(self, user_email: str, user_name: str) -> bool:
        """Send attendance reminder email"""
        template_data = {
            'user_name': user_name,
            'current_time': datetime.now().strftime('%I:%M %p'),
            'checkin_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/attendance",
            'dashboard_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/dashboard"
        }
        
        return await self.send_template_email(
            template_name="attendance_reminder",
            to_emails=[user_email],
            subject="Attendance Reminder - AttendanceAI",
            template_data=template_data
        )
    
    async def send_monthly_report(
        self,
        user_email: str,
        user_name: str,
        report_data: Dict[str, Any],
        report_file_path: Optional[str] = None
    ) -> bool:
        """Send monthly attendance report"""
        template_data = {
            'user_name': user_name,
            'month_year': report_data.get('month_year'),
            'total_days': report_data.get('total_days', 0),
            'present_days': report_data.get('present_days', 0),
            'absent_days': report_data.get('absent_days', 0),
            'late_days': report_data.get('late_days', 0),
            'total_hours': report_data.get('total_hours', 0),
            'avg_hours': report_data.get('avg_hours', 0),
            'attendance_rate': report_data.get('attendance_rate', 0),
            'dashboard_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/dashboard"
        }
        
        attachments = [report_file_path] if report_file_path else None
        
        return await self.send_template_email(
            template_name="monthly_report",
            to_emails=[user_email],
            subject=f"Monthly Attendance Report - {report_data.get('month_year')}",
            template_data=template_data,
            attachments=attachments
        )
    
    async def send_bulk_notification(
        self,
        template_name: str,
        recipients: List[Dict[str, str]],  # [{'email': '', 'name': '', ...}]
        subject: str,
        common_data: Dict[str, Any] = None
    ) -> Dict[str, int]:
        """Send bulk notifications"""
        results = {'sent': 0, 'failed': 0}
        
        for recipient in recipients:
            try:
                template_data = {**(common_data or {}), **recipient}
                
                success = await self.send_template_email(
                    template_name=template_name,
                    to_emails=[recipient['email']],
                    subject=subject,
                    template_data=template_data
                )
                
                if success:
                    results['sent'] += 1
                else:
                    results['failed'] += 1
                
                # Small delay to avoid overwhelming SMTP server
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Failed to send email to {recipient.get('email')}: {e}")
                results['failed'] += 1
        
        return results

# Email template creation helpers
def create_email_templates():
    """Create default email templates"""
    templates_dir = Path("templates/email")
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    # Welcome email template
    welcome_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
            .content { padding: 30px; background: #f9f9f9; }
            .credentials { background: #fff; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #4CAF50; }
            .button { 
                display: inline-block; 
                background: #4CAF50; 
                color: white; 
                padding: 12px 25px; 
                text-decoration: none; 
                border-radius: 5px; 
                margin: 20px 0;
            }
            .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to {{ company_name }}!</h1>
            </div>
            <div class="content">
                <h2>Hello {{ user_name }},</h2>
                <p>Welcome to our attendance management system! Your account has been created successfully.</p>
                
                <div class="credentials">
                    <h3>Your login credentials:</h3>
                    <p><strong>Email:</strong> {{ user_email }}<br>
                    <strong>Temporary Password:</strong> <code>{{ temp_password }}</code></p>
                </div>
                
                <p><strong>Important:</strong> Please change your password after your first login for security.</p>
                
                <p style="text-align: center;">
                    <a href="{{ login_url }}" class="button">Login Now</a>
                </p>
                
                <p>If you have any questions, please contact support at {{ support_email }}.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 {{ company_name }}. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    welcome_txt = """
    Welcome to {{ company_name }}!
    
    Hello {{ user_name }},
    
    Welcome to our attendance management system! Your account has been created successfully.
    
    Your login credentials:
    Email: {{ user_email }}
    Temporary Password: {{ temp_password }}
    
    IMPORTANT: Please change your password after your first login for security.
    
    Login at: {{ login_url }}
    
    If you have any questions, please contact support at {{ support_email }}.
    
    © 2025 {{ company_name }}. All rights reserved.
    """
    
    # Password reset template
    password_reset_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #FF9800; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
            .content { padding: 30px; background: #f9f9f9; }
            .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .button { 
                display: inline-block; 
                background: #FF9800; 
                color: white; 
                padding: 12px 25px; 
                text-decoration: none; 
                border-radius: 5px; 
                margin: 20px 0;
            }
            .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Password Reset Request</h1>
            </div>
            <div class="content">
                <h2>Hello {{ user_name }},</h2>
                <p>We received a request to reset your password for your AttendanceAI account.</p>
                
                <div class="warning">
                    <p><strong>Security Note:</strong> This link will expire in {{ expiry_hours }} hours for your security.</p>
                </div>
                
                <p style="text-align: center;">
                    <a href="{{ reset_url }}" class="button">Reset Password</a>
                </p>
                
                <p>If you didn't request this password reset, please ignore this email or contact support.</p>
                <p>For security reasons, this link will only work once.</p>
                
                <p>If you need help, contact us at {{ support_email }}.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 AttendanceAI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    password_reset_txt = """
    Password Reset Request
    
    Hello {{ user_name }},
    
    We received a request to reset your password for your AttendanceAI account.
    
    Please click the following link to reset your password:
    {{ reset_url }}
    
    This link will expire in {{ expiry_hours }} hours for your security.
    
    If you didn't request this password reset, please ignore this email.
    
    For help, contact us at {{ support_email }}.
    
    © 2025 AttendanceAI. All rights reserved.
    """
    
    # Leave request notification template
    leave_request_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #2196F3; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
            .content { padding: 30px; background: #f9f9f9; }
            .leave-details { background: #fff; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #2196F3; }
            .button { 
                display: inline-block; 
                background: #2196F3; 
                color: white; 
                padding: 12px 25px; 
                text-decoration: none; 
                border-radius: 5px; 
                margin: 10px 5px;
            }
            .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Leave Request Approval Needed</h1>
            </div>
            <div class="content">
                <h2>Hello {{ manager_name }},</h2>
                <p>{{ employee_name }} has submitted a leave request that requires your approval.</p>
                
                <div class="leave-details">
                    <h3>Leave Details:</h3>
                    <p><strong>Employee:</strong> {{ employee_name }}</p>
                    <p><strong>Leave Type:</strong> {{ leave_type }}</p>
                    <p><strong>Start Date:</strong> {{ start_date }}</p>
                    <p><strong>End Date:</strong> {{ end_date }}</p>
                    <p><strong>Total Days:</strong> {{ total_days }}</p>
                    <p><strong>Reason:</strong> {{ reason }}</p>
                </div>
                
                <p style="text-align: center;">
                    <a href="{{ review_url }}" class="button">Review Request</a>
                </p>
                
                <p>Please review and respond to this request at your earliest convenience.</p>
                
                <p><a href="{{ dashboard_url }}">Go to Dashboard</a></p>
            </div>
            <div class="footer">
                <p>&copy; 2025 AttendanceAI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    leave_request_txt = """
    Leave Request Approval Needed
    
    Hello {{ manager_name }},
    
    {{ employee_name }} has submitted a leave request that requires your approval.
    
    Leave Details:
    Employee: {{ employee_name }}
    Leave Type: {{ leave_type }}
    Start Date: {{ start_date }}
    End Date: {{ end_date }}
    Total Days: {{ total_days }}
    Reason: {{ reason }}
    
    Please review and respond to this request at your earliest convenience.
    
    Review at: {{ review_url }}
    Dashboard: {{ dashboard_url }}
    
    © 2025 AttendanceAI. All rights reserved.
    """
    
    # Attendance reminder template
    attendance_reminder_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #FF5722; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
            .content { padding: 30px; background: #f9f9f9; }
            .reminder { background: #fff; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #FF5722; }
            .button { 
                display: inline-block; 
                background: #FF5722; 
                color: white; 
                padding: 12px 25px; 
                text-decoration: none; 
                border-radius: 5px; 
                margin: 20px 0;
            }
            .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Attendance Reminder</h1>
            </div>
            <div class="content">
                <h2>Hello {{ user_name }},</h2>
                
                <div class="reminder">
                    <p><strong>Reminder:</strong> You haven't checked in yet today.</p>
                    <p><strong>Current Time:</strong> {{ current_time }}</p>
                </div>
                
                <p>Please check in as soon as possible to ensure accurate attendance tracking.</p>
                
                <p style="text-align: center;">
                    <a href="{{ checkin_url }}" class="button">Check In Now</a>
                </p>
                
                <p>If you're experiencing issues with check-in, please contact your supervisor or IT support.</p>
                
                <p><a href="{{ dashboard_url }}">Go to Dashboard</a></p>
            </div>
            <div class="footer">
                <p>&copy; 2025 AttendanceAI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    attendance_reminder_txt = """
    Attendance Reminder
    
    Hello {{ user_name }},
    
    REMINDER: You haven't checked in yet today.
    Current Time: {{ current_time }}
    
    Please check in as soon as possible to ensure accurate attendance tracking.
    
    Check in at: {{ checkin_url }}
    Dashboard: {{ dashboard_url }}
    
    If you're experiencing issues, please contact your supervisor or IT support.
    
    © 2025 AttendanceAI. All rights reserved.
    """
    
    # Monthly report template
    monthly_report_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #673AB7; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
            .content { padding: 30px; background: #f9f9f9; }
            .stats { background: #fff; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .stat-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }
            .button { 
                display: inline-block; 
                background: #673AB7; 
                color: white; 
                padding: 12px 25px; 
                text-decoration: none; 
                border-radius: 5px; 
                margin: 20px 0;
            }
            .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Monthly Attendance Report</h1>
                <p>{{ month_year }}</p>
            </div>
            <div class="content">
                <h2>Hello {{ user_name }},</h2>
                <p>Here's your attendance summary for {{ month_year }}:</p>
                
                <div class="stats">
                    <h3>Attendance Statistics</h3>
                    <div class="stat-row">
                        <span>Total Working Days:</span>
                        <strong>{{ total_days }}</strong>
                    </div>
                    <div class="stat-row">
                        <span>Present Days:</span>
                        <strong>{{ present_days }}</strong>
                    </div>
                    <div class="stat-row">
                        <span>Absent Days:</span>
                        <strong>{{ absent_days }}</strong>
                    </div>
                    <div class="stat-row">
                        <span>Late Days:</span>
                        <strong>{{ late_days }}</strong>
                    </div>
                    <div class="stat-row">
                        <span>Total Hours:</span>
                        <strong>{{ total_hours }}</strong>
                    </div>
                    <div class="stat-row">
                        <span>Average Hours/Day:</span>
                        <strong>{{ avg_hours }}</strong>
                    </div>
                    <div class="stat-row">
                        <span>Attendance Rate:</span>
                        <strong>{{ attendance_rate }}%</strong>
                    </div>
                </div>
                
                <p style="text-align: center;">
                    <a href="{{ dashboard_url }}" class="button">View Dashboard</a>
                </p>
                
                <p>Keep up the great work! If you have any questions about your attendance, please contact HR.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 AttendanceAI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    monthly_report_txt = """
    Monthly Attendance Report - {{ month_year }}
    
    Hello {{ user_name }},
    
    Here's your attendance summary for {{ month_year }}:
    
    Attendance Statistics:
    - Total Working Days: {{ total_days }}
    - Present Days: {{ present_days }}
    - Absent Days: {{ absent_days }}
    - Late Days: {{ late_days }}
    - Total Hours: {{ total_hours }}
    - Average Hours/Day: {{ avg_hours }}
    - Attendance Rate: {{ attendance_rate }}%
    
    Keep up the great work!
    
    View your dashboard: {{ dashboard_url }}
    
    If you have any questions about your attendance, please contact HR.
    
    © 2025 AttendanceAI. All rights reserved.
    """
    
    # Leave approval templates
    leave_approval_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
            .content { padding: 30px; background: #f9f9f9; }
            .approval-box { background: #e8f5e8; border: 1px solid #4CAF50; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .button { 
                display: inline-block; 
                background: #4CAF50; 
                color: white; 
                padding: 12px 25px; 
                text-decoration: none; 
                border-radius: 5px; 
                margin: 20px 0;
            }
            .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Leave Request {{ status }}</h1>
            </div>
            <div class="content">
                <h2>Hello {{ employee_name }},</h2>
                
                <div class="approval-box">
                    <h3>✅ Good News! Your leave request has been {{ status }}.</h3>
                    <p><strong>Leave Type:</strong> {{ leave_type }}</p>
                    <p><strong>Start Date:</strong> {{ start_date }}</p>
                    <p><strong>End Date:</strong> {{ end_date }}</p>
                    <p><strong>Approved by:</strong> {{ approved_by }}</p>
                </div>
                
                <p>Please make sure to coordinate with your team before your leave period.</p>
                
                <p style="text-align: center;">
                    <a href="{{ dashboard_url }}" class="button">View Dashboard</a>
                </p>
                
                <p>If you have any questions, please contact your manager or HR.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 AttendanceAI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    leave_rejection_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #f44336; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
            .content { padding: 30px; background: #f9f9f9; }
            .rejection-box { background: #ffebee; border: 1px solid #f44336; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .button { 
                display: inline-block; 
                background: #f44336; 
                color: white; 
                padding: 12px 25px; 
                text-decoration: none; 
                border-radius: 5px; 
                margin: 20px 0;
            }
            .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Leave Request {{ status }}</h1>
            </div>
            <div class="content">
                <h2>Hello {{ employee_name }},</h2>
                
                <div class="rejection-box">
                    <h3>❌ Your leave request has been {{ status }}.</h3>
                    <p><strong>Leave Type:</strong> {{ leave_type }}</p>
                    <p><strong>Start Date:</strong> {{ start_date }}</p>
                    <p><strong>End Date:</strong> {{ end_date }}</p>
                    <p><strong>Reviewed by:</strong> {{ approved_by }}</p>
                </div>
                
                <p>Please speak with your manager to discuss alternative dates or arrangements.</p>
                
                <p style="text-align: center;">
                    <a href="{{ dashboard_url }}" class="button">View Dashboard</a>
                </p>
                
                <p>You can submit a new leave request with different dates if needed.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 AttendanceAI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Daily summary template
    daily_summary_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 700px; margin: 0 auto; padding: 20px; }
            .header { background: #607D8B; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
            .content { padding: 30px; background: #f9f9f9; }
            .summary-card { background: #fff; padding: 20px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #607D8B; }
            .dept-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            .dept-table th, .dept-table td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            .dept-table th { background: #f5f5f5; }
            .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
            .stat-box { background: #fff; padding: 15px; border-radius: 5px; text-align: center; border: 1px solid #ddd; }
            .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Daily Attendance Summary</h1>
                <p>{{ date }}</p>
            </div>
            <div class="content">
                <h2>Hello {{ recipient_name }},</h2>
                
                <div class="stat-grid">
                    <div class="stat-box">
                        <h3>{{ total_employees }}</h3>
                        <p>Total Employees</p>
                    </div>
                    <div class="stat-box">
                        <h3>{{ present_count }}</h3>
                        <p>Present Today</p>
                    </div>
                    <div class="stat-box">
                        <h3>{{ absent_count }}</h3>
                        <p>Absent Today</p>
                    </div>
                    <div class="stat-box">
                        <h3>{{ attendance_rate }}%</h3>
                        <p>Attendance Rate</p>
                    </div>
                </div>
                
                <div class="summary-card">
                    <h3>Department Breakdown</h3>
                    <table class="dept-table">
                        <thead>
                            <tr>
                                <th>Department</th>
                                <th>Total</th>
                                <th>Present</th>
                                <th>Rate</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for dept in department_stats %}
                            <tr>
                                <td>{{ dept.department }}</td>
                                <td>{{ dept.total }}</td>
                                <td>{{ dept.present }}</td>
                                <td>{{ dept.rate }}%</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                
                {% if late_count > 0 %}
                <div class="summary-card">
                    <h3>Late Arrivals: {{ late_count }}</h3>
                    <p>Please follow up with employees who arrived late today.</p>
                </div>
                {% endif %}
            </div>
            <div class="footer">
                <p>&copy; 2025 AttendanceAI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Write all templates to files
    templates = {
        "welcome.html": welcome_html,
        "welcome.txt": welcome_txt,
        "password_reset.html": password_reset_html,
        "password_reset.txt": password_reset_txt,
        "leave_request.html": leave_request_html,
        "leave_request.txt": leave_request_txt,
        "leave_approval.html": leave_approval_html,
        "leave_approval.txt": """
Leave Request Approved

Hello {{ employee_name }},

Good news! Your leave request has been {{ status }}.

Leave Details:
- Leave Type: {{ leave_type }}
- Start Date: {{ start_date }}
- End Date: {{ end_date }}
- Approved by: {{ approved_by }}

Please coordinate with your team before your leave period.

View your dashboard: {{ dashboard_url }}

© 2025 AttendanceAI. All rights reserved.
        """,
        "leave_rejection.html": leave_rejection_html,
        "leave_rejection.txt": """
Leave Request Rejected

Hello {{ employee_name }},

Your leave request has been {{ status }}.

Leave Details:
- Leave Type: {{ leave_type }}
- Start Date: {{ start_date }}
- End Date: {{ end_date }}
- Reviewed by: {{ approved_by }}

Please speak with your manager to discuss alternative arrangements.

View your dashboard: {{ dashboard_url }}

© 2025 AttendanceAI. All rights reserved.
        """,
        "attendance_reminder.html": attendance_reminder_html,
        "attendance_reminder.txt": attendance_reminder_txt,
        "monthly_report.html": monthly_report_html,
        "monthly_report.txt": monthly_report_txt,
        "daily_summary.html": daily_summary_html,
        "daily_summary.txt": """
Daily Attendance Summary - {{ date }}

Hello {{ recipient_name }},

Today's Attendance Overview:
- Total Employees: {{ total_employees }}
- Present Today: {{ present_count }}
- Absent Today: {{ absent_count }}
- Late Arrivals: {{ late_count }}
- Attendance Rate: {{ attendance_rate }}%

Department Breakdown:
{% for dept in department_stats %}
{{ dept.department }}: {{ dept.present }}/{{ dept.total }} ({{ dept.rate }}%)
{% endfor %}

© 2025 AttendanceAI. All rights reserved.
        """,
    }
    
    for filename, content in templates.items():
        template_path = templates_dir / filename
        if not template_path.exists():  # Don't overwrite existing templates
            with open(template_path, "w", encoding="utf-8") as f:
                f.write(content)
    
    logger.info("✅ Email templates created successfully")

# Initialize email service
email_service = EmailService()

# Create templates on import
try:
    if hasattr(settings, 'SMTP_SERVER') and settings.SMTP_SERVER:
        create_email_templates()
    else:
        logger.warning("⚠️ SMTP not configured - email service disabled")
except Exception as e:
    logger.warning(f"⚠️ Could not create email templates: {e}")

# Export for use in other modules
__all__ = ['EmailService', 'email_service', 'create_email_templates']