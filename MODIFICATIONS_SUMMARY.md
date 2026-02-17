# IKEA HEALTH CHECK - MODIFICATIONS & ENHANCEMENTS
**Date: February 16, 2026**
**Version: 2.0 - Alert-Based Email Notification System**

---

## 📋 EXECUTIVE SUMMARY

The IKEA Health Check Monitoring Tool has been enhanced to implement **event-driven email alerts** instead of scheduled notifications. This prevents inbox spam while maintaining critical failure detection.

### Key Improvement
✅ **Emails are NOW sent ONLY when alerts occur** - not at every scheduled interval
✅ **Emails sent ONLY after 3rd consecutive failure retry** - not on first failure
✅ **Recovery emails sent when service comes back online**
✅ **Testing cycle reduced to 1 minute** for quick validation

---

## 🎯 EMAIL ALERT TRIGGERING LOGIC

### When Email IS Sent:
1. **Failure Alert Email** - Triggered when a URL fails 3 consecutive health checks
   - User sees email only when connection problem persists after 3 retries
   
2. **Recovery Email** - Triggered when a previously failed URL comes back online
   - User is notified that the service has recovered

### When Email is NOT Sent:
- ❌ First failure (consecutive_failures = 1) → No email
- ❌ Second failure (consecutive_failures = 2) → No email
- ❌ Transient network hiccups → No email (unless persists through 3 checks)
- ❌ Each scheduled cycle → No automatic batch emails

---

## 📍 THRESHOLD LOCATION & CONFIGURATION

### Alert Threshold Setting
**File:** `config.ini`
**Section:** `[MONITORING]`
**Key:** `alert_threshold`
**Default Value:** `3`

```ini
# RETRY THRESHOLD: Number of consecutive failures before sending alert email
# When a URL fails, it is retried up to this threshold.
# Email alert is triggered ONLY when consecutive failures reach this threshold (default: 3 retries)
# THRESHOLD LOCATION: This value is checked in HealthCheckMonitor.handle_failure() method
alert_threshold = 3
```

### How It Works
```
Failure #1 → consecutive_failures = 1 → No email
Failure #2 → consecutive_failures = 2 → No email
Failure #3 → consecutive_failures = 3 → ✉️ EMAIL SENT
```

### To Change Threshold
Edit `config.ini` and update `alert_threshold` value:
- `alert_threshold = 2` → Email after 2 failures
- `alert_threshold = 5` → Email after 5 failures

---

## 📧 EMAIL CONFIGURATION

### Email Contacts Updated
**File:** `email_contacts.py`

```python
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

### To Update Recipients
1. Edit `email_contacts.py`
2. Modify the respective lists (RECIPIENTS, CC, BCC)
3. Save and restart the application

---

## ⏱️ TESTING CONFIGURATION

### Current Settings for Testing
**File:** `config.ini`

```ini
# Test Cycle: 1 minute (60 seconds)
check_interval = 60

# Quick check interval for failed URLs (30 seconds)
quick_check_interval = 30
```

### For Production
Change `check_interval` back to `300` seconds (5 minutes):
```ini
check_interval = 300  # 5 minutes for production
```

---

## 🔄 EXECUTION FLOW - EMAIL ALERT TRIGGER

```
┌─────────────────────────────────────────────────────────────┐
│ START: Run Health Check Cycle                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │ Check Each URL Health │
         └────────┬──────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
       YES                 NO
        │                   │
        ▼                   ▼
    ✅ URL UP         ❌ URL DOWN
        │              consecutive_failures++
        │                   │
        │              ┌────▼────────────────┐
        │              │ consecutive_failures│
        │              │ == alert_threshold? │
        │              └────┬────────────────┘
        │                   │
        │               YES │ NO
        │                   │  │
        │                   ▼  ▼
        │              EMAIL  NEXT
        │              SENT   CHECK
        │               │
        │        ┌──────┴──────────────────┐
        │        │ WAIT: quick_check_inter-│
        │        │ val (30 sec) before     │
        │        │ retrying failed URL     │
        │        └──────┬──────────────────┘
        │               │
        │        ┌──────▼──────┐
        │        │ Retry Check │
        │        └──────┬──────┘
        │               │
        │        [Loop back to check]
        │
        └──────────┬─────────┐
                   │         │
              RECOVERY       CONTINUE
              EMAIL SENT     MONITORING
```

---

## 📝 CODE MODIFICATIONS

### 1. **run.py** - Main Changes

#### Added Comments & Documentation
```python
# ALERT TRACKING: Track which URLs have already sent alert emails
self.alert_sent: Dict[str, bool] = defaultdict(bool)

# RETRY THRESHOLD: Email alert is sent only after this many consecutive failures
# Default is 3, meaning URL must fail 3 times before an alert is triggered
'alert_threshold': config.getint('MONITORING', 'alert_threshold', fallback=3)
```

#### Updated handle_failure() Method
```python
# ============================================================================
# ALERT TRIGGER: Email is sent ONLY when consecutive failures reach threshold
# THRESHOLD LOCATION: alert_threshold from config.ini (default: 3 retries)
# This means: 1st fail -> no email, 2nd fail -> no email, 3rd fail -> EMAIL SENT
# ============================================================================
if self.consecutive_failures[url] == self.config['alert_threshold']:
    self.alert_sent[url] = True
    self._send_alert(url, status_code, message)
```

#### Updated _send_alert() Method
```python
def _send_alert(self, url: str, status_code: int, message: str):
    """Send alert for URL failure - TRIGGER EMAIL NOTIFICATION"""
    # Generate reports and send email when alert threshold is reached
    self._generate_report()
    
    # Send email via email_alert_win32.py with alert flag
    try:
        subprocess.run(
            [sys.executable, 'email_alert_win32.py', '--alert'],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"\n✓ [EMAIL SENT] Alert email notification sent for {url}")
    except Exception as e:
        print(f"\n✗ [EMAIL FAILED] Error: {str(e)}")
```

#### Updated _send_recovery_alert() Method
```python
def _send_recovery_alert(self, url: str, downtime_duration: timedelta):
    """Send alert for URL recovery"""
    # Send recovery email
    subprocess.run(
        [sys.executable, 'email_alert_win32.py', '--recovery'],
        check=True,
        capture_output=True,
        text=True
    )
    print(f"\n✓ [EMAIL SENT] Recovery email notification sent for {url}")
```

#### Removed Scheduled Email Logic
**Before:**
```python
# REMOVED: This sent emails every check cycle
subprocess.run([sys.executable, 'email_alert_win32.py'], check=True)
```

**After:**
```python
# Emails are triggered by monitor._send_alert() when threshold is reached
# No longer sends emails at every scheduled interval
```

### 2. **email_alert_win32.py** - Enhanced

#### Added Email Sending Status Messages
```python
def send_alert_email(...):
    mail.Send()
    print(f"[✓] Email sent successfully!")
    print(f"    To: {mail.To}")
    if cc:
        print(f"    CC: {mail.CC}")
    if bcc:
        print(f"    BCC: {mail.BCC}")
```

#### Added Alert Type Parameter
```python
def send_health_check_alert(alert_type='alert'):
    """
    Send health check alert email
    Args:
        alert_type: 'alert' for failure alerts, 'recovery' for recovery notifications
    """
    if alert_type == 'recovery':
        subject = 'IKEA Health Check - Service Recovery Notification'
    else:
        subject = 'IKEA Health Check Alert - Critical Service Failure Detected'
```

#### Enhanced Main Execution
```python
if __name__ == '__main__':
    alert_type = 'alert'  # Default
    
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
```

### 3. **config.ini** - Configuration Updates

```ini
# Test cycle: 1 minute (60 seconds)
check_interval = 60

# Quick retry interval: 30 seconds
quick_check_interval = 30

# Alert threshold: Email after 3 consecutive failures
alert_threshold = 3
```

### 4. **email_contacts.py** - Complete Update

```python
SENDER = 'Rohit.AvinashPagar@cognizant.com'
RECIPIENTS = [
    'Rohit.AvinashPagar@cognizant.com',
    'Sksahil.Sakil@cognizant.com',
    'Vaishnavi.Shetti2@cognizant.com'
]
CC = ['Bhavika.Kewalramani@cognizant.com']
BCC = ['Kalyan.Gvss@cognizant.com', 'Eshrath.Fathima@cognizant.com']
```

---

## 🧪 TESTING THE ENHANCEMENTS

### Test Scenario 1: Alert Threshold
1. Start the application: `python run.py`
2. Stop a monitored URL/service
3. Observe:
   - Failure #1 → Logged but no email
   - Failure #2 → Logged but no email  
   - Failure #3 → **Email sent!** ✓

### Test Scenario 2: Recovery Email
1. After alert email is sent (Failure #3)
2. Restart the failed URL/service
3. Observe:
   - Next health check succeeds
   - **Recovery email sent!** ✓

### Test Scenario 3: Quick Checks
1. URL fails → consecutive_failures = 1
2. Wait 30 seconds (quick_check_interval)
3. Automatic retry check runs
4. Continue until failure #3 triggers email

---

## 📊 MONITORING THE SYSTEM

### Log Files Location
- **Main Log:** `logs/health_check.log` - All health check events
- **Alert Log:** `logs/health_check_alerts.log` - Only alert events
- **Report:** `logs/health_check_report.json` - Latest status snapshot

### Console Output Example
```
[EMAIL SENT] Alert email notification sent for https://example.com
    To: Rohit.AvinashPagar@cognizant.com;Sksahil.Sakil@cognizant.com
    CC: Bhavika.Kewalramani@cognizant.com
    BCC: Kalyan.Gvss@cognizant.com,Eshrath.Fathima@cognizant.com
```

---

## ✅ BENEFITS

| Feature | Before | After |
|---------|--------|-------|
| **Email Frequency** | Every scheduled cycle | Only on alerts |
| **Alert Sensitivity** | On 1st failure | On 3rd failure (configurable) |
| **Transient Issues** | Email sent | Ignored (unless persistent) |
| **Recovery Notification** | Manual check | Automatic email |
| **Inbox Noise** | High (many false alarms) | Low (real issues only) |

---

## 🔧 TROUBLESHOOTING

### Emails Not Sending?
1. Check if Outlook is installed and running
2. Verify contacts in `email_contacts.py`
3. Check console output for error messages
4. Review `logs/health_check.log` for details

### Alert Not Triggering?
1. Verify `alert_threshold` in `config.ini`
2. Check `logs/health_check_alerts.log` for alert events
3. Ensure email_alert_win32.py exists in project root

### Too Many / Too Few Alerts?
1. Adjust `alert_threshold` in config.ini (default: 3)
2. Adjust `quick_check_interval` for faster/slower retries
3. Review failure patterns in HTML dashboard

---

## 📞 SUPPORT CONTACTS

**Email Group for Alerts:**
- Rohit.AvinashPagar@cognizant.com (Primary)
- Sksahil.Sakil@cognizant.com
- Vaishnavi.Shetti2@cognizant.com

**CC:** Bhavika.Kewalramani@cognizant.com
**BCC:** Kalyan.Gvss@cognizant.com, Eshrath.Fathima@cognizant.com

---

## 📅 VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-02-16 | Alert-based email system, 3-retry threshold, testing cycle 1min |
| 1.0 | 2026-02-15 | Initial release with scheduled emails |

---

## 🎓 NEXT STEPS

1. ✅ Review these modifications
2. ✅ Test with 1-minute cycle (current config)
3. ✅ Verify email notifications work
4. ✅ Change to production settings (5-minute cycle)
5. ✅ Deploy to monitoring environment

---

**Generated:** February 16, 2026
**System:** IKEA Server Health Check Monitoring Tool v2.0
**Status:** ✅ Ready for Production Testing
