"""
Email Sender using Win32 COM for Outlook
=========================================

This module provides functionality to send emails using Microsoft Outlook
via the win32com.client library with professional HTML email templates.

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

    def send_email(self, subject: str, body: str, recipient_emails: list = None, html_body: str = None):
        """
        Send an email using Outlook

        Args:
            subject: Email subject
            body: Email body content (plain text)
            recipient_emails: List of recipient emails (optional, uses default if not provided)
            html_body: HTML body content (optional, for rich formatting)
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

            # Set HTML body if provided
            if html_body:
                mail.HTMLBody = html_body

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

    def send_alert_email(self, url: str, status_code: int, message: str, report_data: dict = None):
        """
        Send an alert email for server failure

        Args:
            url: The URL that failed
            status_code: HTTP status code
            message: Error message
            report_data: Optional health check report data to include
        """
        subject = f"[ALERT] IKEA Server Health Alert: {url}"

        # Create HTML template
        html_body = self._create_alert_html_template(url, status_code, message, report_data)

        # Create plain text fallback
        body = f"""
Server Down Alert

URL: {url}
Status Code: {status_code}
Error: {message}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please investigate immediately.
"""

        if report_data:
            body += f"\n\n--- HEALTH CHECK REPORT ---\n"
            body += f"Report Timestamp: {report_data.get('timestamp', 'N/A')}\n"
            body += f"Monitoring Duration: {report_data.get('monitoring_duration_seconds', 0):.0f} seconds\n"
            body += f"Total Checks: {report_data.get('total_checks', 0)}\n"
            body += f"Total Failures: {report_data.get('total_failures', 0)}\n"
            body += f"Failure Rate: {report_data.get('failure_rate', '0%')}\n"
            body += f"URLs Monitored: {report_data.get('monitored_urls', 0)}\n\n"

            # Add URL status summary
            url_summary = report_data.get('url_status_summary', {})
            if url_summary:
                body += "URL STATUS SUMMARY:\n"
                for url_key, status in url_summary.items():
                    body += f"- {url_key}: {status.get('current_status', 'UNKNOWN')} "
                    body += f"(Failures: {status.get('consecutive_failures', 0)})\n"
                body += "\n"

        return self.send_email(subject, body.strip(), html_body=html_body)

    def send_recovery_email(self, url: str, downtime_duration_seconds: float):
        """
        Send a recovery email for server back online

        Args:
            url: The URL that recovered
            downtime_duration_seconds: Downtime duration in seconds
        """
        subject = f"[RECOVERY] IKEA Server Recovered: {url}"

        # Create HTML template
        html_body = self._create_recovery_html_template(url, downtime_duration_seconds)

        # Create plain text fallback
        body = f"""
Server Recovery Alert

URL: {url}
Is now UP and operational
Downtime Duration: {downtime_duration_seconds:.0f} seconds
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_email(subject, body.strip(), html_body=html_body)

    def _create_alert_html_template(self, url: str, status_code: int, message: str, report_data: dict = None):
        """
        Create HTML template for alert emails

        Args:
            url: The URL that failed
            status_code: HTTP status code
            message: Error message
            report_data: Optional health check report data

        Returns:
            HTML formatted email body
        """
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>IKEA Server Health Alert</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background-color: white;
                    padding: 20px;
                    margin: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    background-color: #dc3545;
                    color: white;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .alert-icon {{
                    font-size: 24px;
                    margin-right: 10px;
                }}
                .status-info {{
                    background-color: #f8d7da;
                    border: 1px solid #f5c6cb;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 15px 0;
                }}
                .status-label {{
                    font-weight: bold;
                    color: #721c24;
                }}
                .report-section {{
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 15px 0;
                }}
                .report-title {{
                    font-weight: bold;
                    color: #495057;
                    margin-bottom: 10px;
                }}
                .metric {{
                    display: flex;
                    justify-content: space-between;
                    padding: 5px 0;
                    border-bottom: 1px solid #e9ecef;
                }}
                .metric:last-child {{
                    border-bottom: none;
                }}
                .metric-label {{
                    font-weight: bold;
                }}
                .metric-value {{
                    color: #6c757d;
                }}
                .url-status {{
                    margin-top: 10px;
                }}
                .url-item {{
                    padding: 5px 0;
                    border-bottom: 1px solid #e9ecef;
                }}
                .url-up {{
                    color: #28a745;
                }}
                .url-down {{
                    color: #dc3545;
                    font-weight: bold;
                }}
                .footer {{
                    margin-top: 20px;
                    padding-top: 15px;
                    border-top: 1px solid #dee2e6;
                    font-size: 12px;
                    color: #6c757d;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <span class="alert-icon">🚨</span>
                    <strong>IKEA Server Health Alert</strong>
                </div>

                <div class="status-info">
                    <div class="status-label">CRITICAL: Server Down</div>
                    <p><strong>URL:</strong> {url}</p>
                    <p><strong>Status Code:</strong> {status_code}</p>
                    <p><strong>Error:</strong> {message}</p>
                    <p><strong>Time:</strong> {current_time}</p>
                </div>

                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 15px 0;">
                    <strong>⚠️ Action Required:</strong> Please investigate immediately and take necessary corrective actions.
                </div>
        """

        if report_data:
            html += f"""
                <div class="report-section">
                    <div class="report-title">📊 Health Check Report Summary</div>

                    <div class="metric">
                        <span class="metric-label">Report Timestamp:</span>
                        <span class="metric-value">{report_data.get('timestamp', 'N/A')}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Monitoring Duration:</span>
                        <span class="metric-value">{report_data.get('monitoring_duration_seconds', 0):.0f} seconds</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Total Checks:</span>
                        <span class="metric-value">{report_data.get('total_checks', 0)}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Total Failures:</span>
                        <span class="metric-value">{report_data.get('total_failures', 0)}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Failure Rate:</span>
                        <span class="metric-value">{report_data.get('failure_rate', '0%')}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">URLs Monitored:</span>
                        <span class="metric-value">{report_data.get('monitored_urls', 0)}</span>
                    </div>

                    <div class="url-status">
                        <strong>URL Status Summary:</strong>
            """

            url_summary = report_data.get('url_status_summary', {})
            if url_summary:
                for url_key, status in url_summary.items():
                    status_class = "url-up" if status.get('current_status') == 'UP' else "url-down"
                    html += f"""
                        <div class="url-item {status_class}">
                            • {url_key}: {status.get('current_status', 'UNKNOWN')}
                            (Failures: {status.get('consecutive_failures', 0)})
                        </div>
                    """
            else:
                html += "<div class='url-item'>No URL data available</div>"

            html += """
                    </div>
                </div>
            """

        html += f"""
                <div class="footer">
                    <p>This alert was generated by the IKEA Health Check Monitoring System</p>
                    <p>For support, contact the system administrator</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def _create_recovery_html_template(self, url: str, downtime_duration_seconds: float):
        """
        Create HTML template for recovery emails

        Args:
            url: The URL that recovered
            downtime_duration_seconds: Downtime duration in seconds

        Returns:
            HTML formatted email body
        """
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>IKEA Server Recovery</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background-color: white;
                    padding: 20px;
                    margin: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    background-color: #28a745;
                    color: white;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .recovery-icon {{
                    font-size: 24px;
                    margin-right: 10px;
                }}
                .status-info {{
                    background-color: #d4edda;
                    border: 1px solid #c3e6cb;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 15px 0;
                }}
                .status-label {{
                    font-weight: bold;
                    color: #155724;
                }}
                .metric {{
                    display: flex;
                    justify-content: space-between;
                    padding: 5px 0;
                    border-bottom: 1px solid #e9ecef;
                }}
                .metric:last-child {{
                    border-bottom: none;
                }}
                .metric-label {{
                    font-weight: bold;
                }}
                .metric-value {{
                    color: #6c757d;
                }}
                .footer {{
                    margin-top: 20px;
                    padding-top: 15px;
                    border-top: 1px solid #dee2e6;
                    font-size: 12px;
                    color: #6c757d;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <span class="recovery-icon">✅</span>
                    <strong>IKEA Server Recovery Notification</strong>
                </div>

                <div class="status-info">
                    <div class="status-label">RESOLVED: Server Back Online</div>
                    <p><strong>URL:</strong> {url}</p>
                    <p><strong>Status:</strong> UP and operational</p>
                    <p><strong>Time:</strong> {current_time}</p>
                </div>

                <div class="metric">
                    <span class="metric-label">Total Downtime:</span>
                    <span class="metric-value">{downtime_duration_seconds:.0f} seconds</span>
                </div>

                <div style="background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px; margin: 15px 0;">
                    <strong>ℹ️ Status:</strong> The server has recovered and is functioning normally. Monitoring continues.
                </div>

                <div class="footer">
                    <p>This notification was generated by the IKEA Health Check Monitoring System</p>
                    <p>System monitoring remains active</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html


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
