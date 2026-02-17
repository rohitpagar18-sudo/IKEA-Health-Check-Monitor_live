# QUICK REFERENCE GUIDE
**IKEA Health Check Monitoring Tool v2.0**

---

## 🚀 RUNNING THE APPLICATION

```bash
# Start the tool
python run.py

# The tool will:
# 1. Check all URLs from urls.txt
# 2. Log results to logs/health_check.log
# 3. Send emails ONLY when alerts occur
# 4. Generate HTML & Excel reports
```

---

## 🎯 KEY CONFIGURATION FILES

### 1. **config.ini** - Main Settings
```ini
[MONITORING]
check_interval = 60          # Test: 1 minute | Prod: 300 (5 min)
quick_check_interval = 30    # Retry check interval
alert_threshold = 3          # Email after 3 consecutive failures
```

### 2. **email_contacts.py** - Email Recipients
```python
SENDER = 'Rohit.AvinashPagar@cognizant.com'
RECIPIENTS = ['...']         # Primary recipients
CC = ['...']                 # Carbon copy
BCC = ['...']                # Blind carbon copy
```

### 3. **urls.txt** - Monitored URLs
Add one URL per line:
```
https://api.example.com
https://dashboard.example.com
https://health.example.com
```

---

## 📧 EMAIL ALERT FLOW

```
URL Fails
   ├─ Attempt 1 ❌ → No email (consecutive_failures = 1)
   ├─ Attempt 2 ❌ → No email (consecutive_failures = 2)
   └─ Attempt 3 ❌ → ✉️ EMAIL SENT! (consecutive_failures = 3)

URL Recovers
   └─ Next Check ✅ → ✉️ RECOVERY EMAIL SENT!
```

---

## 🔍 ALERT THRESHOLD EXPLAINED

**Question:** "When does the email get sent?"
**Answer:** "After 3 consecutive failures (configurable)"

### Changing Threshold

**For More Sensitive Alerts:**
```ini
alert_threshold = 2  # Email after 2 failures (faster alerts)
```

**For Less Sensitive Alerts:**
```ini
alert_threshold = 5  # Email after 5 failures (less noise)
```

---

## 📍 WHERE IS THE THRESHOLD CHECKED?

**File:** `run.py`
**Method:** `HealthCheckMonitor.handle_failure()`
**Line:** ~220 (approximately)

```python
# ============================================================================
# ALERT TRIGGER: Email is sent ONLY when consecutive failures reach threshold
# THRESHOLD LOCATION: alert_threshold from config.ini (default: 3 retries)
# ============================================================================
if self.consecutive_failures[url] == self.config['alert_threshold']:
    self.alert_sent[url] = True
    self._send_alert(url, status_code, message)
```

---

## 📊 MONITORING DASHBOARD

**Location:** `logs/index.html`

Open in browser to see:
- ✅ Currently healthy URLs
- ❌ Currently down URLs
- 📈 Failure rate
- 🔄 Response times
- 📅 Last check timestamps

Auto-refreshes every 60 seconds.

---

## 🧪 QUICK TEST

### Test Email Alert
1. Find a URL in `urls.txt`
2. Temporarily block/stop it
3. Run: `python run.py`
4. Watch console for:
   ```
   Failure #1 → [FAIL] message
   Failure #2 → [FAIL] message
   Failure #3 → ✓ [EMAIL SENT] Alert email notification sent
   ```

### Verify Email
Check inbox for "IKEA Health Check Alert" email with:
- Current status of all URLs
- HTML & Excel reports attached
- Sent to all recipients

---

## 📝 LOG FILES

**Main Log:** `logs/health_check.log`
```
2026-02-16 10:05:00 - INFO - Loaded 5 URLs for monitoring
2026-02-16 10:05:01 - INFO - [OK] https://api.example.com
2026-02-16 10:05:02 - WARNING - [FAIL] https://dead.example.com - Connection Error
```

**Alert Log:** `logs/health_check_alerts.log`
```
2026-02-16 10:05:06 - ERROR - [ALERT] https://dead.example.com DOWN - Connection Error
```

**Report:** `logs/health_check_report.json`
```json
{
  "timestamp": "2026-02-16T10:05:06",
  "total_checks": 5,
  "total_failures": 1,
  "failure_rate": "20.00%",
  "url_status_summary": { ... }
}
```

---

## 🛠️ COMMON TASKS

### Change Testing to Production (5-minute cycle)
```ini
# In config.ini
check_interval = 300  # Changed from 60
```

### Add New URL to Monitor
```
# In urls.txt - Add line:
https://new-service.example.com
```

### Change Alert Recipients
```python
# In email_contacts.py
RECIPIENTS = [
    'newemail@cognizant.com',
    'admin@cognizant.com'
]
```

### Reduce Alert Sensitivity
```ini
# In config.ini
alert_threshold = 5  # Was 3, now waits 5 failures
```

---

## ⚠️ IMPORTANT NOTES

1. **Check Interval:** Currently set to 60 sec (testing)
   - Change to 300 sec (5 min) for production

2. **Email:** Only sent when:
   - URL fails 3 consecutive times, OR
   - URL recovers after being down

3. **Quick Retries:** Failed URLs are retried every 30 sec
   - Not waiting full 60 sec check interval

4. **Reports:** Generated after each health check cycle
   - HTML: Interactive dashboard
   - Excel: Detailed status table
   - JSON: Raw data for automation

---

## 📞 CONTACT EMAILS

**Alert Recipients:**
- Rohit.AvinashPagar@cognizant.com ⭐ (Primary)
- Sksahil.Sakil@cognizant.com
- Vaishnavi.Shetti2@cognizant.com

**CC:** Bhavika.Kewalramani@cognizant.com
**BCC:** Kalyan.Gvss@cognizant.com, Eshrath.Fathima@cognizant.com

---

## ✅ VERIFICATION CHECKLIST

- [ ] Updated email_contacts.py with correct addresses
- [ ] Set check_interval = 60 for testing (config.ini)
- [ ] Verified alert_threshold = 3 (config.ini)
- [ ] Confirmed quick_check_interval = 30 (config.ini)
- [ ] Added URLs to urls.txt
- [ ] Outlook installed and running
- [ ] Tested by stopping a URL and verifying email after 3 failures
- [ ] Ready for production deployment

---

**Last Updated:** February 16, 2026
**Status:** ✅ Production Ready
