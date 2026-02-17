# Email Alert Enhancement - Testing Checklist

**Enhancement:** Threshold-Based Alert Emails (Only on actual failures, not on schedule)

---

## Pre-Test Configuration

Before running tests, ensure your config is set up:

```ini
[MONITORING]
alert_threshold = 3
check_interval = 30
quick_check_interval = 30

[EMAIL_ALERTS]
enabled = false     # For initial testing - set to true after validating logs
```

---

## Test 1: Verify Alert is NOT Sent Until Threshold Reached

**Setup:**
- Add a URL that is currently offline to `urls.txt`
  Example: `https://invalid-test-url-12345678.com`
- Configure: `alert_threshold = 3`
- Configure: `enabled = false` (to avoid sending test emails)

**Run:**
```bash
python run.py
```

**Expected Behavior:**

Check 1:
```
[FAIL] https://invalid-test-url-12345678.com
[FAILURE 1/3] 2 more failure(s) needed to trigger alert email
```
✓ No email sent
✓ No alert in health_check_alerts.log

Check 2 (after 30 seconds):
```
[FAIL] https://invalid-test-url-12345678.com
[FAILURE 2/3] 1 more failure(s) needed to trigger alert email
```
✓ Still no email
✓ Still no alert in health_check_alerts.log

Check 3 (after another 30 seconds):
```
[FAIL] https://invalid-test-url-12345678.com
*** ALERT THRESHOLD REACHED (3 failures) ***
[ALERT TRIGGERED] URL has failed 3 times...
[ALERT NOT EMAILED] Email alerts are DISABLED in config.ini
⚠ [ALERT LOGGED] Alert for https://invalid-test-url-12345678.com logged but NOT emailed
```
✓ Alert is LOGGED (in health_check_alerts.log)
✓ But NO EMAIL SENT (because enabled = false)

**Verify Results:**
- [ ] Check `logs/health_check_alerts.log` - should see alert entry
- [ ] Check console output - should show "[ALERT LOGGED]" message
- [ ] Confirm no email was received

---

## Test 2: Enable Emails and Verify Alert is Sent

**Setup:**
- Keep same offline URL
- Reset the application (delete cached failure counts if needed)
- Configure: `alert_threshold = 1` (to speed up testing)
- Configure: `enabled = true`

**Run:**
```bash
python run.py
```

**Expected Behavior:**

Check 1:
```
[FAIL] https://invalid-test-url-12345678.com
*** ALERT THRESHOLD REACHED (1 failures) ***
[ALERT TRIGGERED] URL has failed 1 times...
[SENDING EMAIL] Dispatching alert email...
✓ [EMAIL SENT] Alert email notification successfully sent
```
✓ Email is SENT immediately on first failure (because threshold = 1)

**Verify Results:**
- [ ] Check email inbox - alert email received
- [ ] Check `logs/health_check_alerts.log` - alert entry recorded
- [ ] Email contains full health report with attachments
- [ ] Email subject: "IKEA Health Check Alert - Critical Service Failure Detected"

---

## Test 3: Verify No Duplicate Emails During Continued Failure

**Setup:**
- Keep same offline URL
- Continue running after alert was sent
- Configure: `alert_threshold = 1`
- Configure: `enabled = true`

**Run:**
Continue monitoring (don't stop the script)

**Expected Behavior:**

Check 2 (URL still offline):
```
[FAIL] https://invalid-test-url-12345678.com
[Already alerted - no duplicate email sent]
```
✓ Only ONE alert email sent (no duplicates)
✓ Continued failures logged but not emailed

**Verify Results:**
- [ ] Check email inbox - only ONE alert email (not multiple)
- [ ] Check logs - shows "already alerted" logic
- [ ] URL still marked as DOWN

---

## Test 4: Verify Recovery Email is Sent

**Setup:**
- URL that was previously alerted is now back online
- Configure: `enabled = true`

**Run:**
Continue monitoring the previously-failed URL until it comes back online

**Expected Behavior:**

When URL returns to UP status:
```
[OK] https://invalid-test-url-12345678.com
[RECOVERY] https://invalid-test-url-12345678.com UP after 180 seconds downtime
[RECOVERY NOTIFICATION] URL recovered...
[SENDING EMAIL] Dispatching recovery email...
✓ [EMAIL SENT] Recovery email notification successfully sent
```
✓ Recovery email is SENT
✓ Only ONE recovery email (no duplicates)

**Verify Results:**
- [ ] Check email inbox - recovery email received
- [ ] Email subject: "IKEA Health Check - Service Recovery Notification"
- [ ] Email shows downtime duration
- [ ] URL now marked as UP

---

## Test 5: Disable Emails and Verify Alerts are Logged Only

**Setup:**
- Configure: `enabled = false`
- Introduce a new failure (new offline URL)

**Run:**
```bash
python run.py
```

**Expected Behavior:**

When threshold reached:
```
*** ALERT THRESHOLD REACHED (3 failures) ***
[ALERT NOT EMAILED] Email alerts are DISABLED in config.ini
⚠ [ALERT LOGGED] Alert logged but NOT emailed (email_enabled = false)
```
✓ No email sent
✓ Alert still logged locally
✓ Clear message: "email_enabled = false"

**Verify Results:**
- [ ] No email received
- [ ] Alert logged in `logs/health_check_alerts.log`
- [ ] Console shows "[ALERT LOGGED]" message indicating disabled setting

---

## Test 6: Verify Configurable Threshold

**Setup:**
- Configure: `alert_threshold = 5` (require 5 failures before alert)
- Configure: `enabled = true`
- Introduce a new test URL failure

**Run:**
Monitor for 5+ failures

**Expected Behavior:**

Failures 1-4:
```
[FAILURE 1/5] 4 more failure(s) needed to trigger alert email
[FAILURE 2/5] 3 more failure(s) needed to trigger alert email
[FAILURE 3/5] 2 more failure(s) needed to trigger alert email
[FAILURE 4/5] 1 more failure(s) needed to trigger alert email
```
✓ No emails sent yet

Failure 5:
```
[FAILURE 5/5] 0 more failure(s) needed to trigger alert email
*** ALERT THRESHOLD REACHED (5 failures) ***
✓ [EMAIL SENT] Alert email notification successfully sent
```
✓ Email sent only on 5th failure

**Verify Results:**
- [ ] No emails on failures 1-4
- [ ] Email sent on failure 5
- [ ] Can adjust threshold to control email frequency

---

## Test 7: Verify No Scheduled/Interval Emails

**Setup:**
- Normal monitoring running
- Both URLs healthy (all UP)
- Configure: `enabled = true`
- Configure: `check_interval = 30` seconds

**Run:**
Let monitoring run for several check cycles (2+ minutes)

Expected Behavior:

Cycle 1:
```
[OK] https://example1.com
[OK] https://example2.com
[MONITORING SUMMARY] ... 
```
✓ No email (everything healthy)

Cycle 2 (30 seconds later):
```
[OK] https://example1.com
[OK] https://example2.com
[MONITORING SUMMARY] ...
```
✓ No email (still healthy)

Cycle 3 (30 seconds later):
```
[OK] https://example1.com
[OK] https://example2.com
[MONITORING SUMMARY] ...
```
✓ Still no email (everything healthy)

**Verify Results:**
- [ ] No emails received during healthy periods
- [ ] Emails are event-driven (only on failures/recoveries)
- [ ] NOT sent at fixed intervals regardless of status
- [ ] Reports are generated every cycle (HTML/Excel)
- [ ] Emails are NOT sent just because reports are generated

---

## Log File Verification Checklist

After running tests, verify these log files:

### logs/health_check.log
- [ ] Shows all health check cycles
- [ ] Shows failure progression with "[FAILURE X/Y]" format
- [ ] Shows when threshold is reached
- [ ] Shows "[ALERT TRIGGERED]" message
- [ ] Shows "[SENDING EMAIL]" message (or "NOT EMAILED" if disabled)
- [ ] Shows recovery messages

### logs/health_check_alerts.log
- [ ] Shows ALERT entries when threshold reached
- [ ] Shows RECOVERY entries when services come back up
- [ ] Chronologically ordered

### logs/health_check_report.json
- [ ] Updated after each cycle
- [ ] Shows consecutive_failures count for each URL

---

## Email Content Verification

When you receive an alert email, verify it contains:

- [ ] **Subject:** "IKEA Health Check Alert - Critical Service Failure Detected"
- [ ] **Body:** Lists currently healthy URLs and down URLs
- [ ] **Timestamp:** When alert was sent
- [ ] **Attachments:**
  - [ ] health_check_report.xlsx (Excel)
  - [ ] index.html (Dashboard)
  - [ ] health_check.log (Log file)

When you receive a recovery email, verify:
- [ ] **Subject:** "IKEA Health Check - Service Recovery Notification"
- [ ] **Body:** Shows which URL recovered and downtime duration
- [ ] Correct timestamp and downtime information

---

## Summary of Expected Behavior

| Condition | Email Sent? | Logged? | Notes |
|-----------|------------|----------|-------|
| URL fails once | ❌ No | ✓ Yes | Not at threshold yet |
| URL fails twice | ❌ No | ✓ Yes | Still not at threshold |
| URL fails 3 times (threshold) | ✓ Yes* | ✓ Yes | *Only if enabled=true |
| URL fails 4+ times | ❌ No | ✓ Yes | No duplicate emails |
| URL recovers after alert | ✓ Yes* | ✓ Yes | *Only if enabled=true |
| All URLs healthy for hours | ❌ No | ✓ Yes | No scheduled emails |
| enabled = false | ❌ No | ✓ Yes | Alerts logged locally only |

*For all cases where email is sent, enabled=true must be set in config.ini

---

## Summary

✅ **Main Goal Achieved:** Emails are sent ONLY when failures/recoveries occur, NOT on a schedule
✅ **Threshold-based:** Configurable number of failures before alert
✅ **No Duplicates:** Alert sent once per incident
✅ **Full Control:** email_enabled flag controls all email sending
✅ **Full Transparency:** All decisions logged clearly
