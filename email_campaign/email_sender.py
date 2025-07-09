"""
Email sender for Claude Token Resale System
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import Optional, List
import time

logger = logging.getLogger(__name__)


class EmailSender:
    """Send emails via SMTP"""
    
    def __init__(self, 
                 smtp_host: Optional[str] = None,
                 smtp_port: Optional[int] = None,
                 smtp_user: Optional[str] = None,
                 smtp_pass: Optional[str] = None,
                 from_email: Optional[str] = None):
        
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER", "")
        self.smtp_pass = smtp_pass or os.getenv("SMTP_PASS", "")
        self.from_email = from_email or os.getenv("EMAIL_FROM", "")
        
        # Validate configuration
        if not all([self.smtp_user, self.smtp_pass, self.from_email]):
            logger.warning("SMTP configuration incomplete. Email sending disabled.")
            self.enabled = False
        else:
            self.enabled = True
            logger.info(f"Email sender initialized: {self.smtp_host}:{self.smtp_port}")
    
    def send_email(self, to_email: str, subject: str, body: str, 
                   recipient_name: str = "", html_body: Optional[str] = None) -> bool:
        """Send email to recipient"""
        if not self.enabled:
            logger.error("Email sending disabled - incomplete configuration")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = str(Header(subject, 'utf-8'))
            
            # Add text body
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Add HTML body if provided
            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_bulk_emails(self, recipients: List[dict], delay: float = 1.0) -> List[dict]:
        """Send bulk emails with delay between sends"""
        results = []
        
        for i, recipient in enumerate(recipients):
            try:
                success = self.send_email(
                    to_email=recipient["email"],
                    subject=recipient["subject"],
                    body=recipient["body"],
                    recipient_name=recipient.get("name", ""),
                    html_body=recipient.get("html_body")
                )
                
                results.append({
                    "email": recipient["email"],
                    "success": success,
                    "index": i
                })
                
                # Add delay between emails to avoid rate limiting
                if i < len(recipients) - 1:
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Error sending bulk email to {recipient['email']}: {e}")
                results.append({
                    "email": recipient["email"],
                    "success": False,
                    "error": str(e),
                    "index": i
                })
        
        return results
    
    def test_connection(self) -> bool:
        """Test SMTP connection"""
        if not self.enabled:
            return False
        
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
            
            logger.info("SMTP connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return False
    
    def send_test_email(self, to_email: str) -> bool:
        """Send test email"""
        subject = "Test Email from ClaudeToken System"
        body = """This is a test email from the ClaudeToken system.

If you received this email, the email configuration is working correctly.

Best regards,
ClaudeToken Team"""
        
        return self.send_email(to_email, subject, body)
    
    def is_enabled(self) -> bool:
        """Check if email sending is enabled"""
        return self.enabled
    
    def get_config_status(self) -> dict:
        """Get configuration status"""
        return {
            "enabled": self.enabled,
            "smtp_host": self.smtp_host,
            "smtp_port": self.smtp_port,
            "smtp_user": self.smtp_user,
            "from_email": self.from_email,
            "has_password": bool(self.smtp_pass)
        }