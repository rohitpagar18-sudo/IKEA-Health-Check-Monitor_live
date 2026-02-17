# Email Alert Enhancement - Implementation Guide
**Date:** February 17, 2026  
**Feature:** Threshold-Based Alert Emails (No Scheduled Emails)

---

## Overview

The IKEA Health Check Monitoring Tool now guarantees that **email notifications are sent ONLY when an actual alert occurs**, not on any fixed schedule. This prevents unnecessary inbox notifications when there are no issues.

---

## Email Triggering Logic

### Alert Email Triggers
An email is sent when ALL of the following conditions are met:
1. A monitored URL fails consecutively `alert_threshold` times (default: **3 failures**)
2. Email notifications are **enabled** (`email_enabled = true` in config.ini)
3. This is the first time the threshold is reached for this URL (duplicate emails are prevented)

### Recovery Email Triggers
A recovery email is sent when:
1. A previously-alerted URL comes back online (status returns to UP)
2. Email notifications are **enabled** (`email_enabled = true` in config.ini)
3. An alert email was previously sent for this URL

### NO Emails Sent When
- Email alerts are disabled (`email_enabled = false` in config.ini) - Alerts are logged locally instead
- No URL failures have occurred
- A URL is still recovering (less than threshold failures)
- Regular scheduled intervals are just starting/running - Only event-driven

---

## Failure Progression Example

### Scenario: URL starts failing

```
Check 1 (Failure 1)
  ├─ Status: DOWN
  ├─ Action: Log warning (no email)
  ├─ Console: "  [FAILURE 1/3] 2 more failure(s) needed to trigger alert email"
  └─ Email Sent: NO

Check 2 (Failure 2)
  ├─ Status: DOWN
  ├─ Action: Log warning (no email)
  ├─ Console: "  [FAILURE 2/3] 1 more failure(s) needed to trigger alert email"
  └─ Email Sent: NO

Check 3 (Failure 3 - THRESHOLD REACHED)
  ├─ Status: DOWN
  ├─ Action: Threshold reached!
  ├─ Decision: Check if email_enabled = true in config.ini
  │  ├─ If TRUE:  Send alert email with full health report
  │  └─ If FALSE: Log to alert file only (no email)
  ├─ Console: "*** ALERT THRESHOLD REACHED (3 failures) ***"
  └─ Email Sent: YES (if enabled) / LOGGED ONLY (if disabled)

Check 4+ (Continued failure)
  ├─ Status: DOWN
  ├─ Action: Already sent alert, no duplicate email
  ├─ Console: "[Already alerted - no duplicate email]"
  └─ Email Sent: NO

...Later - Check N (Recovery)
  ├─ Status: UP
  ├─ Action: URL recovered!
  ├─ Decision: Previous alert was sent, send recovery email
  ├─ Console: "[RECOVERY] URL back online"
  └─ Email Sent: YES (if enabled) / LOGGED ONLY (if disabled)
```

---

## Configuration

### Enabling/Disabling Emails

Edit `config.ini`:

```ini
[EMAIL_ALERTS]
# Enable email notifications (true/false)
enabled = true      # Enable emails when threshold is reached
enabled = false     # Disable emails - alerts logged locally only
```

### Alert Threshold

Edit `config.ini`:

```ini
[MONITORING]
# Default is 3, meaning URL must fail 3 times before alert
alert_threshold = 3

# Examples:
# alert_threshold = 1     # Send alert on first failure (sensitive)
# alert_threshold = 3     # Send alert after 3 failures (default, balanced)
# alert_threshold = 5     # Send alert after 5 failures (tolerant)
```

---

## Log Indicators

### What You'll See in Logs

**Alert Progression:**
```
FAILED: https://example.com - Code: 0 - Connection Error
[FAILURE 1/3] 2 more failure(s) needed to trigger alert email
[FAILURE 2/3] 1 more failure(s) needed to trigger alert email
*** ALERT THRESHOLD REACHED (3 failures) ***
[ALERT TRIGGERED] URL has failed 3 times...
[SENDING EMAIL] Dispatching alert email for https://example.com...
✓ [EMAIL SENT] Alert email notification successfully sent
```

**If Email is Disabled:**
```
FAILED: https://example.com - Code: 0 - Connection Error
*** ALERT THRESHOLD REACHED (3 failures) ***
[ALERT NOT EMAILED] Email alerts are DISABLED in config.ini
```

**Recovery:**
```
[RECOVERY] https://example.com UP after 120 seconds downtime
[SENDING EMAIL] Dispatching recovery email for https://example.com...
✓ [EMAIL SENT] Recovery email notification successfully sent
```

---

## Key Features

✅ **No Schedule-Based Emails**
- Emails are ONLY sent when failures/recoveries occur
- No emails during normal operation

✅ **Configurable Threshold**
- Default: 3 consecutive failures triggers alert
- Easily adjusted in config.ini

✅ **Email On/Off Control**
- Single boolean flag controls all email sending
- Alerts still logged locally when disabled

✅ **No Duplicate Alerts**
- Once alert is sent, no duplicate emails for same issue
- Only recovery email breaks the silence

✅ **Full Transparency**
- All decisions logged with clear messages
- Know exactly why (or why not) an email was sent

---

## Verification Steps

### Test Alert Email Triggering

1. **Set threshold to 1 (for testing):**
   ```ini
   [MONITORING]
   alert_threshold = 1
   ```

2. **Enable emails:**
   ```ini
   [EMAIL_ALERTS]
   enabled = true
   ```

3. **Configure test URL that's down:**
   - Add a non-existent or offline URL to `urls.txt`
   - Example: `https://invalid-test-url-12345.com`

4. **Run monitoring:**
   ```bash
   python run.py
   ```
   Expected: First check failure → Alert email sent

5. **Test with emails disabled:**
   ```ini
   [EMAIL_ALERTS]
   enabled = false
   ```
   Expected: First check failure → Alert logged, but NO email sent

---

## Troubleshooting

### Emails Not Being Sent
Check in order:
1. Is `email_enabled = true` in `config.ini`? (required)
2. Have you reached `alert_threshold` consecutive failures? (required)
3. Are email credentials configured correctly? (SMTP or Outlook)
4. Check logs for specific error messages

### Too Many Emails
- Increase `alert_threshold` for more tolerance
- Or set `enabled = false` to disable emails temporarily

### Unexpected Alerts
- Check logs to see what failure is triggering the alert
- Review alert history: `health_check_alerts.log`
- Adjust URLs in `urls.txt` if expected to be down

---

## Technical Implementation

### Code Changes Made

1. **Enhanced `handle_failure()` method**
   - Now logs detailed failure progression
   - Shows how many failures until threshold is reached

2. **Guarded `_send_alert()` method**
   - Checks `email_enabled` flag before sending
   - Logs when email is skipped due to disabled setting

3. **Guarded `_send_recovery_alert()` method**
   - Checks `email_enabled` flag before sending
   - Only sends if a previous alert was actually emailed

4. **Improved Configuration**
   - Enhanced config.ini comments
   - Clear explanation of email behavior

5. **Better Logging**
   - Added "SENDING EMAIL" and "NOT EMAILED" indicators
   - Shows alert decision progression

---

## Summary

The enhancement ensures that:
- **✓ Emails are ONLY sent on actual failures** (after threshold reached)
- **✓ Emails are ONLY sent on recovery** events
- **✓ Emails are NEVER sent on a schedule**
- **✓ Users have full control** via `email_enabled` flag
- **✓ All decisions are transparently logged**

This eliminates alert fatigue while maintaining critical alert notifications.
