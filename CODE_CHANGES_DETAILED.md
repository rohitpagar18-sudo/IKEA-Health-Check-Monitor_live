# CODE CHANGES - DETAILED REVIEW
**IKEA Health Check Monitoring Tool v2.0**
**February 16, 2026**

---

## 📄 FILE 1: email_contacts.py

### ✅ UPDATED WITH:
- Correct sender email
- All recipients added
- CC and BCC addresses populated

### Current Content:
```python
# email_contacts.py
# Define sender, recipients, cc, and bcc for use in email_alert_win32.py

SENDER = 'Rohit.AvinashPagar@cognizant.com'

RECIPIENTS = [
    'Rohit.AvinashPagar@cognizant.com',
    'Sksahil.Sakil@cognizant.com',
    'Vaishnavi.Shetti2@cognizant.com'
]

CC = [
    'Bhavika.Kewalramani@cognizant.com'
]

BCC = [
    'Kalyan.Gvss@cognizant.com',
    'Eshrath.Fathima@cognizant.com'
]
```

**Changes Made:**
- ✅ Added 2 additional recipients (Sksahil, Vaishnavi)
- ✅ Added CC recipient (Bhavika)
- ✅ Added 2 BCC recipients (Kalyan, Eshrath)
- ✅ Removed redundant/commented code

---

## 📄 FILE 2: config.ini

### ✅ UPDATED TESTING PARAMETERS:

**Before:**
```ini
check_interval = 300
quick_check_interval = 60
alert_threshold = 2
```

**After:**
```ini
# NOTE: Set to 60 seconds (1 minute) for testing. 
# Change to 300 for production (5 minutes)
check_interval = 60

quick_check_interval = 30

# RETRY THRESHOLD: Number of consecutive failures before sending alert email
# When a URL fails, it is retried up to this threshold.
# Email alert is triggered ONLY when consecutive failures reach this threshold
# THRESHOLD LOCATION: This value is checked in HealthCheckMonitor.handle_failure() method
alert_threshold = 3
```

**Changes Made:**
- ✅ Changed check_interval to 60 seconds for testing
- ✅ Changed quick_check_interval to 30 seconds (faster retries)
- ✅ Changed alert_threshold to 3 (default 3 retries before email)
- ✅ Added detailed comments explaining retry behavior

---

## 📄 FILE 3: run.py

### ✅ MAJOR CHANGES:

#### 1️⃣ Module Docstring (Lines 1-23)

**Before:**
```python
"""
IKEA SERVER HEALTH CHECK MONITORING TOOL - UNIFIED RUNNER
==========================================================

Single script to run all health checks, generate reports, and create Excel/HTML outputs.
No external dependencies required - everything is self-contained.

Usage:
    python run.py              # Run single check cycle
    python run.py --continuous # Run continuous monitoring
    python run.py --report     # Generate report from latest data
"""
```

**After:**
```python
"""
IKEA SERVER HEALTH CHECK MONITORING TOOL - UNIFIED RUNNER
==========================================================

Single script to run all health checks, generate reports, and create Excel/HTML outputs.
Email alerts are triggered ONLY when a URL fails consecutively after the configured
retry threshold (default: 3 retries). This prevents unnecessary inbox notifications.

No external dependencies required - everything is self-contained.

Usage:
    python run.py              # Run single check cycle
    python run.py --continuous # Run continuous monitoring
    python run.py --report     # Generate report from latest data

ALERT TRIGGERING LOGIC:
- When a URL health check FAILS, consecutive_failures counter increments
- On each retry (quick check), the URL is checked again
- Only when consecutive_failures reaches alert_threshold (default: 3),
  an alert email is sent with a full health report
- Once the URL recovers (returns to UP state), a recovery email is sent
- This ensures minimal alert fatigue while maintaining critical notifications
"""
```

**Changes:**
- ✅ Added explanation of alert-triggered email system
- ✅ Added detailed alert triggering logic description
- ✅ Removed implication of continuous scheduled emails

---

#### 2️⃣ ConfigLoader.load() Method (Line ~75)

**Before:**
```python
'alert_threshold': config.getint('MONITORING', 'alert_threshold', fallback=2),
'quick_check_interval': config.getint('MONITORING', 'quick_check_interval', fallback=60),
```

**After:**
```python
'quick_check_interval': config.getint('MONITORING', 'quick_check_interval', fallback=30),
# RETRY THRESHOLD: Email alert is sent only after this many consecutive failures
# Default is 3, meaning URL must fail 3 times before an alert is triggered
'alert_threshold': config.getint('MONITORING', 'alert_threshold', fallback=3),
```

**Changes:**
- ✅ Updated quick_check_interval default from 60→30
- ✅ Updated alert_threshold default from 2→3
- ✅ Added inline comments explaining alert threshold

---

#### 3️⃣ ConfigLoader.get_defaults() Method (Line ~96)

**Before:**
```python
'check_interval': 300,
'quick_check_interval': 60,
'alert_threshold': 2,
```

**After:**
```python
'check_interval': 300,
'quick_check_interval': 30,
'alert_threshold': 3,
```

**Changes:**
- ✅ Synchronized default values with config loading

---

#### 4️⃣ HealthCheckMonitor.__init__() Method (Line ~135)

**Before:**
```python
# Status tracking
self.status_history: Dict[str, List[Dict]] = defaultdict(list)
self.consecutive_failures: Dict[str, int] = defaultdict(int)
self.downtime_start: Dict[str, datetime] = {}

# Statistics
self.total_checks = 0
```

**After:**
```python
# Status tracking
self.status_history: Dict[str, List[Dict]] = defaultdict(list)
self.consecutive_failures: Dict[str, int] = defaultdict(int)
self.downtime_start: Dict[str, datetime] = {}

# ALERT TRACKING: Track which URLs have already sent alert emails
# to avoid duplicate emails for the same issue
self.alert_sent: Dict[str, bool] = defaultdict(bool)

# Statistics
self.total_checks = 0
```

**Changes:**
- ✅ Added alert_sent dictionary to track which URLs have sent alerts
- ✅ Prevents duplicate alert emails for the same failure

---

#### 5️⃣ handle_failure() Method (Line ~185)

**Before:**
```python
def handle_failure(self, url: str, status_code: int, message: str):
    """Handle URL health check failure"""
    self.consecutive_failures[url] += 1
    
    self.logger.warning(f"FAILED: {url} - Code: {status_code} - {message}")
    
    if self.consecutive_failures[url] == 1:
        self.downtime_start[url] = datetime.now()
    
    if self.consecutive_failures[url] == self.config['alert_threshold']:
        self._send_alert(url, status_code, message)
```

**After:**
```python
def handle_failure(self, url: str, status_code: int, message: str):
    """Handle URL health check failure - TRIGGER EMAIL ALERT WHEN THRESHOLD IS REACHED"""
    self.consecutive_failures[url] += 1
    
    self.logger.warning(f"FAILED: {url} - Code: {status_code} - {message}")
    
    if self.consecutive_failures[url] == 1:
        self.downtime_start[url] = datetime.now()
    
    # ============================================================================
    # ALERT TRIGGER: Email is sent ONLY when consecutive failures reach threshold
    # THRESHOLD LOCATION: alert_threshold from config.ini (default: 3 retries)
    # This means: 1st fail -> no email, 2nd fail -> no email, 3rd fail -> EMAIL SENT
    # ============================================================================
    if self.consecutive_failures[url] == self.config['alert_threshold']:
        # Mark that alert has been sent for this URL
        self.alert_sent[url] = True
        self._send_alert(url, status_code, message)
```

**Changes:**
- ✅ Added detailed comments about threshold location
- ✅ Sets alert_sent flag when email triggered
- ✅ Clarifies exact retry behavior

---

#### 6️⃣ handle_success() Method (Line ~207)

**Before:**
```python
def handle_success(self, url: str):
    """Handle URL health check success"""
    was_down = self.consecutive_failures[url] >= self.config['alert_threshold']
    
    if was_down:
        downtime_duration = datetime.now() - self.downtime_start.get(url, datetime.now())
        self.logger.info(f"[RECOVERY] {url} UP after {downtime_duration.total_seconds():.0f}s downtime")
        self._send_recovery_alert(url, downtime_duration)
    
    self.consecutive_failures[url] = 0
    self.downtime_start.pop(url, None)
```

**After:**
```python
def handle_success(self, url: str):
    """Handle URL health check success - SEND RECOVERY ALERT IF PREVIOUSLY DOWN"""
    was_down = self.consecutive_failures[url] >= self.config['alert_threshold']
    
    if was_down and self.alert_sent[url]:
        # Send recovery alert only if alert was previously sent
        downtime_duration = datetime.now() - self.downtime_start.get(url, datetime.now())
        self.logger.info(f"[RECOVERY] {url} UP after {downtime_duration.total_seconds():.0f}s downtime")
        self._send_recovery_alert(url, downtime_duration)
        # Mark alert as no longer active for this URL
        self.alert_sent[url] = False
    
    self.consecutive_failures[url] = 0
    self.downtime_start.pop(url, None)
```

**Changes:**
- ✅ Added check for alert_sent flag before sending recovery email
- ✅ Only sends recovery email if an alert was previously sent
- ✅ Resets alert_sent flag when URL recovers

---

#### 7️⃣ _send_alert() Method (Line ~227)

**Before:**
```python
def _send_alert(self, url: str, status_code: int, message: str):
    """Send alert for URL failure"""
    alert_msg = f"[ALERT] {url} DOWN - Code: {status_code} - {message}"
    self.alert_logger.error(alert_msg)
    self.logger.error(alert_msg)
```

**After:**
```python
def _send_alert(self, url: str, status_code: int, message: str):
    """Send alert for URL failure - TRIGGER EMAIL NOTIFICATION"""
    alert_msg = f"[ALERT] {url} DOWN - Code: {status_code} - {message}"
    self.alert_logger.error(alert_msg)
    self.logger.error(alert_msg)
    
    # Generate reports and send email when alert threshold is reached
    self.logger.info(f"[ALERT TRIGGERED] Generating report and sending email for {url}")
    self._generate_report()
    
    # Send email via email_alert_win32.py with alert flag
    try:
        # Call email script with flag indicating this is an alert
        subprocess.run(
            [sys.executable, 'email_alert_win32.py', '--alert'],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"\n✓ [EMAIL SENT] Alert email notification sent for {url}")
        self.logger.info(f"✓ [EMAIL SENT] Alert email notification sent for {url}")
    except subprocess.CalledProcessError as e:
        self.logger.error(f"✗ Failed to send email alert: {e.stderr}")
        print(f"\n✗ [EMAIL FAILED] Could not send alert email for {url}")
    except Exception as e:
        self.logger.error(f"✗ Error sending email alert: {str(e)}")
        print(f"\n✗ [EMAIL FAILED] Error: {str(e)}")
```

**Changes:**
- ✅ Now generates reports when alert is triggered
- ✅ Sends email via subprocess with '--alert' flag
- ✅ Added try/except for error handling
- ✅ Prints success/failure message to console
- ✅ Logs all events to file

---

#### 8️⃣ _send_recovery_alert() Method (Line ~256)

**Before:**
```python
def _send_recovery_alert(self, url: str, downtime_duration: timedelta):
    """Send alert for URL recovery"""
    alert_msg = f"[RECOVERY] {url} UP after {downtime_duration.total_seconds():.0f}s downtime"
    self.alert_logger.info(alert_msg)
    self.logger.warning(alert_msg)
```

**After:**
```python
def _send_recovery_alert(self, url: str, downtime_duration: timedelta):
    """Send alert for URL recovery"""
    alert_msg = f"[RECOVERY] {url} UP after {downtime_duration.total_seconds():.0f}s downtime"
    self.alert_logger.info(alert_msg)
    self.logger.warning(alert_msg)
    
    # Generate reports and send recovery email
    self.logger.info(f"[RECOVERY NOTIFICATION] Generating report and sending recovery email for {url}")
    self._generate_report()
    
    # Send recovery email
    try:
        subprocess.run(
            [sys.executable, 'email_alert_win32.py', '--recovery'],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"\n✓ [EMAIL SENT] Recovery email notification sent for {url}")
        self.logger.info(f"✓ [EMAIL SENT] Recovery email notification sent for {url}")
    except subprocess.CalledProcessError as e:
        self.logger.error(f"✗ Failed to send recovery email: {e.stderr}")
        print(f"\n✗ [EMAIL FAILED] Could not send recovery email for {url}")
    except Exception as e:
        self.logger.error(f"✗ Error sending recovery email: {str(e)}")
        print(f"\n✗ [EMAIL FAILED] Error: {str(e)}")
```

**Changes:**
- ✅ Now generates reports before sending recovery email
- ✅ Sends email via subprocess with '--recovery' flag
- ✅ Added comprehensive error handling
- ✅ Prints status to console with ✓/✗ indicators

---

#### 9️⃣ Main Section (Line ~720)

**Before:**
```python
if __name__ == "__main__":
    config = ConfigLoader.load()
    check_interval = config.get('check_interval', 300)
    while True:
        monitor = HealthCheckMonitor(config)
        if monitor.urls:
            monitor.run_single_check_cycle()
            monitor.print_summary()
            # Generate reports
            generator = ReportGenerator(config)
            generator.generate_html_report()
            try:
                generator.generate_excel_report()
            except Exception as e:
                print(f"  ⚠ Excel report generation skipped: {str(e)}")
            # Send email alert
            try:
                subprocess.run([sys.executable, 'email_alert_win32.py'], check=True)
            except Exception as e:
                print(f"  ⚠ Email alert failed: {str(e)}")
        else:
            print("\n  ✗ ERROR: No URLs found in urls.txt\n")
        print(f"\n[*] Waiting {check_interval//60} minutes before next health check...\n")
        time.sleep(check_interval)
```

**After:**
```python
if __name__ == "__main__":
    config = ConfigLoader.load()
    check_interval = config.get('check_interval', 300)
    while True:
        monitor = HealthCheckMonitor(config)
        if monitor.urls:
            monitor.run_single_check_cycle()
            monitor.print_summary()
            # Generate reports (email alerts are triggered by monitor._send_alert() when threshold is reached)
            generator = ReportGenerator(config)
            generator.generate_html_report()
            try:
                generator.generate_excel_report()
            except Exception as e:
                print(f"  ⚠ Excel report generation skipped: {str(e)}")
        else:
            print("\n  ✗ ERROR: No URLs found in urls.txt\n")
        print(f"\n[*] Waiting {check_interval} seconds ({check_interval//60} minute(s)) before next health check...\n")
        time.sleep(check_interval)
```

**Changes:**
- ✅ REMOVED: Scheduled email sending at every cycle
- ✅ ADDED: Comment explaining email trigger mechanism
- ✅ IMPROVED: Wait message shows seconds and minutes

---

## 📄 FILE 4: email_alert_win32.py

### ✅ ENHANCED WITH:

#### 1️⃣ Imports (Line 1)

**Before:**
```python
import win32com.client as win32
from pathlib import Path
import os
from email_contacts import SENDER, RECIPIENTS, CC, BCC
```

**After:**
```python
import win32com.client as win32
from pathlib import Path
import os
import sys
from email_contacts import SENDER, RECIPIENTS, CC, BCC
```

**Changes:**
- ✅ Added `import sys` for command-line argument handling

---

#### 2️⃣ send_alert_email() Function (Line 6)

**Before:**
```python
def send_alert_email(sender, recipients, subject, body_html, attachments=None, cc=None, bcc=None):
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = recipients if isinstance(recipients, str) else ';'.join(recipients)
    if cc:
        mail.CC = cc if isinstance(cc, str) else ';'.join(cc)
    if bcc:
        mail.BCC = bcc if isinstance(bcc, str) else ';'.join(bcc)
    mail.Subject = subject
    mail.HTMLBody = body_html
    if attachments:
        for file in attachments:
            if Path(file).exists():
                mail.Attachments.Add(str(file))
    mail.Send()
```

**After:**
```python
def send_alert_email(sender, recipients, subject, body_html, attachments=None, cc=None, bcc=None):
    """Send email using Outlook"""
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = recipients if isinstance(recipients, str) else ';'.join(recipients)
    if cc:
        mail.CC = cc if isinstance(cc, str) else ';'.join(cc)
    if bcc:
        mail.BCC = bcc if isinstance(bcc, str) else ';'.join(bcc)
    mail.Subject = subject
    mail.HTMLBody = body_html
    if attachments:
        for file in attachments:
            if Path(file).exists():
                mail.Attachments.Add(str(file))
    mail.Send()
    print(f"[✓] Email sent successfully!")
    print(f"    To: {mail.To}")
    if cc:
        print(f"    CC: {mail.CC}")
    if bcc:
        print(f"    BCC: {mail.BCC}")
```

**Changes:**
- ✅ Added docstring
- ✅ Added success message after sending
- ✅ Prints recipient details to console

---

#### 3️⃣ send_health_check_alert() Function Signature (Line 27)

**Before:**
```python
def send_health_check_alert():
    # Configurable details
    sender = SENDER
    recipients = RECIPIENTS
    cc = CC
    bcc = BCC
    subject = 'IKEA Health Check Alert - Automated Report'
```

**After:**
```python
def send_health_check_alert(alert_type='alert'):
    """
    Send health check alert email
    
    Args:
        alert_type: 'alert' for failure alerts, 'recovery' for recovery notifications
    """
    # ============================================================================
    # EMAIL CONFIGURATION: Contacts and Recipients
    # ============================================================================
    sender = SENDER
    recipients = RECIPIENTS
    cc = CC
    bcc = BCC
    
    # Customize subject based on alert type
    if alert_type == 'recovery':
        subject = 'IKEA Health Check - Service Recovery Notification'
    else:
        subject = 'IKEA Health Check Alert - Critical Service Failure Detected'
```

**Changes:**
- ✅ Added alert_type parameter
- ✅ Added comprehensive docstring
- ✅ Added section headers in comments
- ✅ Dynamic subject based on alert type

---

#### 4️⃣ Report Paths Section (Line ~50)

**Before:**
```python
    # Paths
    logs_dir = Path(__file__).parent / 'logs'
    excel = logs_dir / 'health_check_report.xlsx'
    html = logs_dir / 'index.html'
    log = logs_dir / 'health_check.log'
    # Parse summary from log (look for MONITORING SUMMARY block)
```

**After:**
```python
    # ============================================================================
    # REPORT AND ATTACHMENT PATHS
    # ============================================================================
    logs_dir = Path(__file__).parent / 'logs'
    excel = logs_dir / 'health_check_report.xlsx'
    html = logs_dir / 'index.html'
    log = logs_dir / 'health_check.log'
    
    # ============================================================================
    # PARSE ALERT SUMMARY FROM LOG FILES
    # ============================================================================
```

**Changes:**
- ✅ Added section headers for clarity
- ✅ Better code organization

---

#### 5️⃣ Main Execution Section (Line ~120)

**Before:**
```python
if __name__ == '__main__':
    send_health_check_alert()
```

**After:**
```python
if __name__ == '__main__':
    # ============================================================================
    # ALERT TYPE HANDLING
    # Determine if this is an alert or recovery notification
    # Called with: python email_alert_win32.py [--alert] [--recovery]
    # ============================================================================
    alert_type = 'alert'  # Default is alert
    
    if '--recovery' in sys.argv:
        alert_type = 'recovery'
        print("\n" + "="*60)
        print("  SENDING RECOVERY NOTIFICATION EMAIL")
        print("="*60 + "\n")
    else:
        print("\n" + "="*60)
        print("  SENDING ALERT NOTIFICATION EMAIL")
        print("="*60 + "\n")
    
    send_health_check_alert(alert_type=alert_type)
    print("\n" + "="*60 + "\n")
```

**Changes:**
- ✅ Added command-line argument handling (--alert, --recovery)
- ✅ Prints header indicating email type
- ✅ Passes alert_type to function
- ✅ Better visual feedback

---

## 📊 SUMMARY OF CHANGES

| Component | Before | After | Impact |
|-----------|--------|-------|--------|
| **Email Frequency** | Every cycle | Only on alerts | 🔴 → 🟢 (reduced noise) |
| **Alert Threshold** | 2 failures | 3 failures | Better transient handling |
| **Test Cycle** | 5 minutes | 1 minute | Faster testing |
| **Quick Retry** | 60 seconds | 30 seconds | Quicker failure detection |
| **Email Recipients** | Incomplete | Complete | All stakeholders included |
| **Recovery Email** | Not sent | Auto-sent | Better operational awareness |
| **Console Feedback** | Minimal | Detailed | Better visibility |
| **Email Status** | Silent | Printed | Confirmation on screen |

---

## ✅ VERIFICATION

All files have been successfully updated:
- ✅ `email_contacts.py` - Complete contact list
- ✅ `config.ini` - Testing parameters set, thresholds documented
- ✅ `run.py` - Email-on-alert logic implemented
- ✅ `email_alert_win32.py` - Alert type handling added

**Ready for testing!** 🚀

---

**Generated:** February 16, 2026
**Status:** ✅ All Changes Complete
