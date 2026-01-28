"""
Email Sender using Win32 COM for Outlook
=========================================

This module provides functionality to send emails using Microsoft Outlook
via the win32com.client library.

Configuration:
- SENDER_EMAIL: The email address to use as sender
- RECIPIENT_EMAILS: List of recipient email addresses

To change sender/recipients, simply modify the variables at the top of this file.
"""

import win32com.client as win32
from datetime import datetime
import logging

# ============================================================================
# Email Configuration
# ============================================================================

# Sender email address
SENDER_EMAIL = "Rohit.AvinashPagar@cognizant.com"

# Recipient email addresses (list)
RECIPIENT_EMAILS = ["Sksahil.Sakil@cognizant.com"]

# ============================================================================
# Email Sender Class
# ============================================================================

class OutlookEmailSender:
    """Email sender using Microsoft Outlook via win32com"""

    def __init__(self):
        """Initialize the Outlook email sender"""
        self.logger = logging.getLogger(__name__)
        self.outlook = None

    def _get_outlook_app(self):
        """Get or create Outlook application instance"""
        if self.outlook is None:
            try:
                self.outlook = win32.Dispatch('outlook.application')
                self.logger.info("Outlook application initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Outlook: {str(e)}")
                raise
        return self.outlook

    def send_email(self, subject: str, body: str, recipient_emails: list = None):
        """
        Send an email using Outlook

        Args:
            subject: Email subject
            body: Email body content
            recipient_emails: List of recipient emails (optional, uses default if not provided)
        """
        if recipient_emails is None:
            recipient_emails = RECIPIENT_EMAILS

        try:
            outlook = self._get_outlook_app()
            mail = outlook.CreateItem(0)  # 0 = olMailItem

            # Set email properties
            mail.Subject = subject
            mail.Body = body
            mail.To = '; '.join(recipient_emails)

            # Set sender if different from default account
            if SENDER_EMAIL:
                mail.SentOnBehalfOfName = SENDER_EMAIL

            # Send the email
            mail.Send()

            self.logger.info(f"Email sent successfully to {recipient_emails}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email: {str(e)}")
            return False

    def send_alert_email(self, url: str, status_code: int, message: str):
        """
        Send an alert email for server failure

        Args:
            url: The URL that failed
            status_code: HTTP status code
            message: Error message
        """
        subject = f"🚨 IKEA Server Health Alert: {url}"
        body = f"""
Server Down Alert

URL: {url}
Status Code: {status_code}
Error: {message}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please investigate immediately.
"""
        return self.send_email(subject, body.strip())

    def send_recovery_email(self, url: str, downtime_duration_seconds: float):
        """
        Send a recovery email for server back online

        Args:
            url: The URL that recovered
            downtime_duration_seconds: Downtime duration in seconds
        """
        subject = f"✓ IKEA Server Recovered: {url}"
        body = f"""
Server Recovery Alert

URL: {url}
Is now UP and operational
Downtime Duration: {downtime_duration_seconds:.0f} seconds
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_email(subject, body.strip())


# ============================================================================
# Convenience Functions
# ============================================================================

def send_email(subject: str, body: str, recipient_emails: list = None):
    """
    Convenience function to send an email

    Args:
        subject: Email subject
        body: Email body
        recipient_emails: List of recipients (optional)
    """
    sender = OutlookEmailSender()
    return sender.send_email(subject, body, recipient_emails)

def send_alert(url: str, status_code: int, message: str):
    """
    Convenience function to send alert email

    Args:
        url: Failed URL
        status_code: HTTP status code
        message: Error message
    """
    sender = OutlookEmailSender()
    return sender.send_alert_email(url, status_code, message)

def send_recovery(url: str, downtime_seconds: float):
    """
    Convenience function to send recovery email

    Args:
        url: Recovered URL
        downtime_seconds: Downtime in seconds
    """
    sender = OutlookEmailSender()
    return sender.send_recovery_email(url, downtime_seconds)


# ============================================================================
# Test Function
# ============================================================================

if __name__ == "__main__":
    # Test the email sender
    logging.basicConfig(level=logging.INFO)

    print("Testing Outlook Email Sender...")
    print(f"Sender: {SENDER_EMAIL}")
    print(f"Recipients: {RECIPIENT_EMAILS}")

    # Test email
    test_subject = "Test Email from IKEA Health Check"
    test_body = f"""
This is a test email sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

If you received this, the Outlook email integration is working correctly.
"""

    success = send_email(test_subject, test_body)
    if success:
        print("✓ Test email sent successfully!")
    else:
        print("✗ Failed to send test email. Check Outlook configuration.")
