"""
IKEA Server Health Check Monitoring Tool
========================================

This script continuously monitors the health status of IKEA server URLs.
It checks availability, detects downtime, and logs alerts for proactive resolution.

Features:
- Continuous monitoring with configurable intervals
- HTTP status code validation
- Response time tracking
- Automatic alerting on failures
- Comprehensive logging
- Email notifications (optional)
- Detailed reporting
"""

import requests
import time
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import threading
from collections import defaultdict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============================================================================
# Configuration
# ============================================================================

class Config:
    """Configuration settings for the health check monitor"""
    
    # URLs file path
    URLS_FILE = "urls.txt"
    
    # Check intervals (in seconds)
    CHECK_INTERVAL = 300  # 5 minutes between checks
    QUICK_CHECK_INTERVAL = 60  # 1 minute for failed URLs
    
    # Timeout settings
    REQUEST_TIMEOUT = 10  # seconds
    
    # HTTP status codes that indicate success
    HEALTHY_STATUS_CODES = [200, 201, 202, 204, 301, 302, 304, 307, 308]
    
    # Logging
    LOG_DIR = "logs"
    LOG_FILE = "health_check.log"
    ALERT_LOG_FILE = "health_check_alerts.log"
    REPORT_FILE = "health_check_report.json"
    
    # Alert thresholds
    CONSECUTIVE_FAILURES_THRESHOLD = 2  # Alert after 2 consecutive failures
    
    # Email notifications (set to True to enable)
    ENABLE_EMAIL_ALERTS = False
    EMAIL_CONFIG = {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "your_email@gmail.com",
        "sender_password": "your_app_password",
        "recipient_emails": ["admin@ikea.com", "ops@ikea.com"]
    }

# ============================================================================
# Logger Setup
# ============================================================================

def setup_logging():
    """Configure logging for both console and file output"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path(Config.LOG_DIR)
    log_dir.mkdir(exist_ok=True)
    
    # Main logger
    logger = logging.getLogger("HealthCheck")
    logger.setLevel(logging.DEBUG)
    
    # File handler for detailed logs
    file_handler = logging.FileHandler(log_dir / Config.LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler for important messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Alert logger (separate file for alerts)
    alert_logger = logging.getLogger("AlertLog")
    alert_logger.setLevel(logging.WARNING)
    alert_handler = logging.FileHandler(log_dir / Config.ALERT_LOG_FILE)
    alert_handler.setFormatter(formatter)
    alert_logger.addHandler(alert_handler)
    
    return logger, alert_logger


# ============================================================================
# Health Check Engine
# ============================================================================

class HealthCheckMonitor:
    """Main health check monitoring engine"""
    
    def __init__(self, urls_file: str):
        """
        Initialize the health check monitor
        
        Args:
            urls_file: Path to file containing URLs to monitor
        """
        self.logger, self.alert_logger = setup_logging()
        self.urls = self._load_urls(urls_file)
        self.logger.info(f"Loaded {len(self.urls)} URLs for monitoring")
        
        # Status tracking
        self.status_history: Dict[str, List[Dict]] = defaultdict(list)
        self.consecutive_failures: Dict[str, int] = defaultdict(int)
        self.last_alert_sent: Dict[str, datetime] = {}
        self.downtime_start: Dict[str, datetime] = {}
        
        # Statistics
        self.total_checks = 0
        self.total_failures = 0
        self.start_time = datetime.now()
        
    def _load_urls(self, urls_file: str) -> List[str]:
        """Load URLs from file"""
        try:
            with open(urls_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            return urls
        except FileNotFoundError:
            self.logger.error(f"URLs file not found: {urls_file}")
            return []
    
    def check_url_health(self, url: str) -> Tuple[bool, int, float, str]:
        """
        Check the health of a single URL
        
        Args:
            url: URL to check
            
        Returns:
            Tuple of (is_healthy, status_code, response_time, message)
        """
        try:
            start_time = time.time()
            response = requests.get(
                url,
                timeout=Config.REQUEST_TIMEOUT,
                allow_redirects=True
            )
            response_time = time.time() - start_time
            
            is_healthy = response.status_code in Config.HEALTHY_STATUS_CODES
            
            return is_healthy, response.status_code, response_time, "OK"
        
        except requests.exceptions.Timeout:
            return False, 0, Config.REQUEST_TIMEOUT, "Request timeout"
        except requests.exceptions.ConnectionError:
            return False, 0, 0, "Connection error"
        except requests.exceptions.RequestException as e:
            return False, 0, 0, f"Request error: {str(e)}"
        except Exception as e:
            return False, 0, 0, f"Unexpected error: {str(e)}"
    
    def record_status(self, url: str, is_healthy: bool, status_code: int, 
                     response_time: float, message: str):
        """Record the status check result"""
        status_entry = {
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "status": "UP" if is_healthy else "DOWN",
            "status_code": status_code,
            "response_time": f"{response_time:.3f}s",
            "message": message
        }
        
        self.status_history[url].append(status_entry)
        
        # Keep only last 1000 entries per URL
        if len(self.status_history[url]) > 1000:
            self.status_history[url] = self.status_history[url][-1000:]
    
    def handle_failure(self, url: str, status_code: int, message: str):
        """Handle URL health check failure"""
        self.consecutive_failures[url] += 1
        
        # Log the failure
        self.logger.warning(f"Health check FAILED for {url} - Code: {status_code} - {message}")
        
        # Mark downtime start
        if self.consecutive_failures[url] == 1:
            self.downtime_start[url] = datetime.now()
        
        # Send alert if threshold is reached
        if self.consecutive_failures[url] == Config.CONSECUTIVE_FAILURES_THRESHOLD:
            self._send_alert(url, status_code, message)
    
    def handle_success(self, url: str):
        """Handle URL health check success"""
        was_down = self.consecutive_failures[url] >= Config.CONSECUTIVE_FAILURES_THRESHOLD
        
        if was_down:
            downtime_duration = datetime.now() - self.downtime_start.get(url, datetime.now())
            self.logger.info(
                f"✓ {url} is now UP after {downtime_duration.total_seconds():.0f}s downtime"
            )
            self._send_recovery_alert(url, downtime_duration)
        
        self.consecutive_failures[url] = 0
        self.downtime_start.pop(url, None)
    
    def _send_alert(self, url: str, status_code: int, message: str):
        """Send alert for URL failure"""
        alert_message = (
            f"🚨 ALERT: Server Down\n"
            f"URL: {url}\n"
            f"Status Code: {status_code}\n"
            f"Error: {message}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Consecutive Failures: {self.consecutive_failures[url]}"
        )
        
        self.alert_logger.error(alert_message)
        self.logger.error(f"ALERT TRIGGERED: {url}")
        
        # Send email if enabled
        if Config.ENABLE_EMAIL_ALERTS:
            self._send_email_alert(url, status_code, message)
    
    def _send_recovery_alert(self, url: str, downtime_duration: timedelta):
        """Send alert for URL recovery"""
        alert_message = (
            f"✓ RECOVERY: Server Back Online\n"
            f"URL: {url}\n"
            f"Downtime Duration: {downtime_duration.total_seconds():.0f} seconds\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        self.alert_logger.info(alert_message)
        self.logger.warning(alert_message)
        
        # Send recovery email if enabled
        if Config.ENABLE_EMAIL_ALERTS:
            self._send_recovery_email(url, downtime_duration)
    
    def _send_email_alert(self, url: str, status_code: int, message: str):
        """Send email alert (requires valid SMTP configuration)"""
        if not Config.ENABLE_EMAIL_ALERTS:
            return
        
        try:
            config = Config.EMAIL_CONFIG
            msg = MIMEMultipart()
            msg['From'] = config['sender_email']
            msg['To'] = ', '.join(config['recipient_emails'])
            msg['Subject'] = f"🚨 IKEA Server Health Alert: {url}"
            
            body = (
                f"Server Down Alert\n\n"
                f"URL: {url}\n"
                f"Status Code: {status_code}\n"
                f"Error: {message}\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Consecutive Failures: {self.consecutive_failures[url]}\n\n"
                f"Please investigate immediately."
            )
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
                server.starttls()
                server.login(config['sender_email'], config['sender_password'])
                server.send_message(msg)
            
            self.logger.info(f"Email alert sent for {url}")
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {str(e)}")
    
    def _send_recovery_email(self, url: str, downtime_duration: timedelta):
        """Send recovery email alert"""
        if not Config.ENABLE_EMAIL_ALERTS:
            return
        
        try:
            config = Config.EMAIL_CONFIG
            msg = MIMEMultipart()
            msg['From'] = config['sender_email']
            msg['To'] = ', '.join(config['recipient_emails'])
            msg['Subject'] = f"✓ IKEA Server Recovered: {url}"
            
            body = (
                f"Server Recovery Alert\n\n"
                f"URL: {url}\n"
                f"Is now UP and operational\n"
                f"Downtime Duration: {downtime_duration.total_seconds():.0f} seconds\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
                server.starttls()
                server.login(config['sender_email'], config['sender_password'])
                server.send_message(msg)
            
            self.logger.info(f"Recovery email sent for {url}")
        except Exception as e:
            self.logger.error(f"Failed to send recovery email: {str(e)}")
    
    def run_single_check_cycle(self):
        """Run a single health check cycle for all URLs"""
        self.logger.info("=" * 80)
        self.logger.info("Starting health check cycle...")
        self.logger.info("=" * 80)
        
        for url in self.urls:
            is_healthy, status_code, response_time, message = self.check_url_health(url)
            
            self.record_status(url, is_healthy, status_code, response_time, message)
            self.total_checks += 1
            
            if is_healthy:
                status_icon = "✓"
                self.logger.info(
                    f"{status_icon} {url} - Status: {status_code} - "
                    f"Response Time: {response_time:.3f}s"
                )
                self.handle_success(url)
            else:
                status_icon = "✗"
                self.logger.warning(
                    f"{status_icon} {url} - Status: {status_code} - {message}"
                )
                self.handle_failure(url, status_code, message)
                self.total_failures += 1
        
        self._generate_report()
        self.logger.info("Health check cycle completed\n")
    
    def _generate_report(self):
        """Generate and save health check report"""
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "monitoring_duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "total_checks": self.total_checks,
            "total_failures": self.total_failures,
            "failure_rate": f"{(self.total_failures / max(self.total_checks, 1) * 100):.2f}%",
            "monitored_urls": len(self.urls),
            "url_status_summary": {}
        }
        
        for url in self.urls:
            latest_status = self.status_history[url][-1] if self.status_history[url] else {}
            failed_count = self.consecutive_failures[url]
            
            report_data["url_status_summary"][url] = {
                "current_status": latest_status.get("status", "UNKNOWN"),
                "consecutive_failures": failed_count,
                "last_check": latest_status.get("timestamp", "N/A"),
                "last_status_code": latest_status.get("status_code", "N/A"),
                "last_response_time": latest_status.get("response_time", "N/A")
            }
        
        # Save report
        log_dir = Path(Config.LOG_DIR)
        report_path = log_dir / Config.REPORT_FILE
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return report_data
    
    def get_status_summary(self) -> Dict:
        """Get current status summary"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "healthy_urls": 0,
            "unhealthy_urls": 0,
            "urls_status": {}
        }
        
        for url in self.urls:
            latest_status = self.status_history[url][-1] if self.status_history[url] else None
            
            if latest_status:
                is_healthy = latest_status["status"] == "UP"
                if is_healthy:
                    summary["healthy_urls"] += 1
                else:
                    summary["unhealthy_urls"] += 1
                
                summary["urls_status"][url] = latest_status
        
        return summary
    
    def start_continuous_monitoring(self, duration_hours: int = None):
        """
        Start continuous monitoring
        
        Args:
            duration_hours: How long to run (None for indefinite)
        """
        self.logger.info(f"Starting continuous monitoring...")
        if duration_hours:
            self.logger.info(f"Will run for {duration_hours} hours")
        else:
            self.logger.info("Running indefinitely (press Ctrl+C to stop)")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours) if duration_hours else None
        
        try:
            while True:
                self.run_single_check_cycle()
                
                # Check if we should stop
                if end_time and datetime.now() >= end_time:
                    break
                
                # Determine wait time
                wait_time = Config.CHECK_INTERVAL
                
                # Quick check if any URL is down
                if any(self.consecutive_failures[url] > 0 for url in self.urls):
                    wait_time = Config.QUICK_CHECK_INTERVAL
                
                self.logger.info(f"Next check in {wait_time} seconds...")
                time.sleep(wait_time)
        
        except KeyboardInterrupt:
            self.logger.info("\nMonitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Error during monitoring: {str(e)}")
        finally:
            self._print_final_summary()
    
    def _print_final_summary(self):
        """Print final monitoring summary"""
        duration = datetime.now() - self.start_time
        
        summary_text = (
            "\n" + "=" * 80 + "\n"
            "MONITORING SUMMARY\n"
            "=" * 80 + "\n"
            f"Monitoring Duration: {duration}\n"
            f"Total Checks Performed: {self.total_checks}\n"
            f"Total Failures: {self.total_failures}\n"
            f"Overall Failure Rate: {(self.total_failures / max(self.total_checks, 1) * 100):.2f}%\n"
            f"URLs Monitored: {len(self.urls)}\n"
        )
        
        current_status = self.get_status_summary()
        summary_text += f"Currently Healthy: {current_status['healthy_urls']}\n"
        summary_text += f"Currently Down: {current_status['unhealthy_urls']}\n"
        summary_text += "=" * 80 + "\n"
        
        self.logger.info(summary_text)
        print(summary_text)


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    print("\n" + "=" * 80)
    print("IKEA SERVER HEALTH CHECK MONITORING TOOL")
    print("=" * 80 + "\n")
    
    # Create monitor
    monitor = HealthCheckMonitor(Config.URLS_FILE)
    
    if not monitor.urls:
        print("ERROR: No URLs found in configuration file!")
        return
    
    # Print URLs being monitored
    print("URLs being monitored:")
    print("-" * 80)
    for i, url in enumerate(monitor.urls, 1):
        print(f"{i:2d}. {url}")
    print("-" * 80 + "\n")
    
    # Start monitoring
    try:
        # Run continuous monitoring (indefinite)
        monitor.start_continuous_monitoring()
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
