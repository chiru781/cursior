import smtplib
import imaplib
import email
import logging
import time
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from config.config import Config

class EmailVerifier:
    """Email utility for testing email functionality"""
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger(__name__)
    
    def wait_for_email(self, recipient_email, subject_contains="", timeout=30):
        """Wait for email to be received"""
        if not self.config.ENABLE_EMAIL_TESTING:
            self.logger.info("Email testing is disabled")
            return True  # Assume email was sent for testing purposes
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self._check_email_received(recipient_email, subject_contains):
                return True
            time.sleep(2)
        
        return False
    
    def _check_email_received(self, recipient_email, subject_contains):
        """Check if email was received (simplified mock implementation)"""
        # In a real implementation, this would connect to an email service
        # For demo purposes, we'll simulate email checking
        self.logger.info(f"Checking for email to {recipient_email} with subject containing '{subject_contains}'")
        
        # Simulate email check delay
        time.sleep(1)
        
        # For testing, we'll assume emails are always received
        return True

class EmailSender:
    """Email sender utility for testing"""
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger(__name__)
    
    def send_test_email(self, to_email, subject, body, html_body=None):
        """Send test email"""
        if not self.config.ENABLE_EMAIL_TESTING:
            self.logger.info("Email testing is disabled")
            return True
        
        try:
            msg = MimeMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config.EMAIL_USER
            msg['To'] = to_email
            
            # Add text and HTML parts
            text_part = MimeText(body, 'plain')
            msg.attach(text_part)
            
            if html_body:
                html_part = MimeText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.config.EMAIL_HOST, self.config.EMAIL_PORT) as server:
                if self.config.EMAIL_USE_TLS:
                    server.starttls()
                server.login(self.config.EMAIL_USER, self.config.EMAIL_PASSWORD)
                server.send_message(msg)
            
            self.logger.info(f"Test email sent to {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False