# TESTING & VERIFICATION CHECKLIST
**IKEA Health Check Monitoring Tool v2.0**
**February 16, 2026**

---

## 🧪 PRE-TESTING REQUIREMENTS

### System Setup
- [ ] Python 3.7+ installed
- [ ] Outlook installed and running
- [ ] Internet connection active
- [ ] Project directory: `IKEA_health_check_final`

### File Verification
- [ ] `run.py` exists and has ~793 lines
- [ ] `email_contacts.py` exists with all contacts filled
- [ ] `config.ini` exists with check_interval=60
- [ ] `email_alert_win32.py` exists
- [ ] `urls.txt` exists with at least 2-3 URLs
- [ ] `logs/` directory exists or will be created

---

## 🔍 CONFIG VERIFICATION

### Check config.ini Values

```ini
check_interval = 60                    ✓ (Testing mode)
quick_check_interval = 30              ✓ (Fast retry)
alert_threshold = 3                    ✓ (Email after 3 fails)
```

Run this to verify:
```bash
python -c "import configparser; c=configparser.ConfigParser(); c.read('config.ini'); print(f'Interval: {c.get(\"MONITORING\",\"check_interval\")}'); print(f'Threshold: {c.get(\"MONITORING\",\"alert_threshold\")}')"
```

Expected Output:
```
Interval: 60
Threshold: 3
```

---

## 📧 EMAIL VERIFICATION

### Check email_contacts.py

Run this to verify:
```bash
python -c "from email_contacts import SENDER, RECIPIENTS, CC, BCC; print(f'Sender: {SENDER}'); print(f'Recipients: {len(RECIPIENTS)}'); print(f'CC: {len(CC)}'); print(f'BCC: {len(BCC)}')"
```

Expected Output:
```
Sender: Rohit.AvinashPagar@cognizant.com
Recipients: 3
CC: 1
BCC: 2
```

---

## 🧪 TEST PLAN A: Normal Operation

### Step 1: Start Application
```bash
python run.py
```

**Expected Output:**
```
==================================================
  HEALTH CHECK CYCLE - 2026-02-16 10:00:00
==================================================
  [OK]   | https://api.example.com          | Code: 200 | Time: 0.234s
  [OK]   | https://dashboard.example.com    | Code: 200 | Time: 0.156s
  [OK]   | https://health.example.com       | Code: 200 | Time: 0.789s
==================================================
```

### Step 2: Verify Logs
Check `logs/health_check.log`:
```
✓ Should show "[OK]" for healthy URLs
✓ Should show check timestamp
✓ Should show response times
```

### Step 3: Verify Reports
Check `logs/` directory:
- [ ] `health_check_report.json` created ✓
- [ ] `index.html` created ✓
- [ ] `health_check.log` created ✓

### Step 4: Open HTML Dashboard
```bash
# Windows:
start logs/index.html

# Or open in browser:
file:///c:/Users/2194998/OneDrive%20-%20Cognizant/Desktop/IKEA_health_check_final/IKEA_health_check_final/logs/index.html
```

**Expected:**
- [ ] Shows all URLs with "UP" status ✓
- [ ] Shows failure rate 0% ✓
- [ ] Auto-refreshes every 60 seconds ✓

---

## 🧪 TEST PLAN B: Alert Triggering (Critical!)

### Scenario: Simulate URL Failure

#### Step 1: Prepare Test
1. Choose one URL from `urls.txt` (e.g., `https://health.example.com`)
2. Ensure you can block/stop it temporarily
   - Edit hosts file, OR
   - Stop the service, OR
   - Disconnect network for that URL

#### Step 2: Block URL
Block the URL so it cannot be reached.

#### Step 3: Run First Check (No Email Expected)
```bash
python run.py
```

**Expected Console Output:**
```
==================================================
  HEALTH CHECK CYCLE - 2026-02-16 10:05:00
==================================================
  [OK]   | https://api.example.com
  [OK]   | https://dashboard.example.com
  [FAIL] | https://health.example.com | Error: Connection Error
        ↑ consecutive_failures = 1
        ↑ NO EMAIL SENT YET
==================================================
```

**Verify in logs/health_check.log:**
```
FAILED: https://health.example.com - Code: 0 - Connection Error
```

**Email Check:** ❌ No email should arrive

---

### Step 4: Wait and Run Second Check (Still No Email)
Wait 30-60 seconds, then run again:

```bash
python run.py
```

**Expected Console Output:**
```
[FAIL] | https://health.example.com | Error: Connection Error
       ↑ consecutive_failures = 2
       ↑ STILL NO EMAIL
```

**Email Check:** ❌ Still no email

---

### Step 5: Wait and Run Third Check (EMAIL SHOULD ARRIVE!)
Wait 30-60 seconds, then run again:

```bash
python run.py
```

**Expected Console Output:**
```
[FAIL] | https://health.example.com | Error: Connection Error
       ↑ consecutive_failures = 3
       ↑ THRESHOLD REACHED!

✓ [EMAIL SENT] Alert email notification sent for https://health.example.com
    To: Rohit.AvinashPagar@cognizant.com;...
    CC: Bhavika.Kewalramani@cognizant.com
    BCC: Kalyan.Gvss@cognizant.com,...
```

**Email Check:** ✅ Email SHOULD arrive with:
- [ ] Subject: "IKEA Health Check Alert - Critical Service Failure Detected"
- [ ] Recipient: All 3 recipients in RECIPIENTS list
- [ ] CC: Bhavika.Kewalramani@cognizant.com
- [ ] BCC: Kalyan.Gvss@cognizant.com, Eshrath.Fathima@cognizant.com
- [ ] Attachments: health_check_report.xlsx, index.html, health_check.log
- [ ] HTML Content: Shows status summary and failure details
- [ ] Down Count: Shows "1" URLs currently down

---

## 🧪 TEST PLAN C: Recovery Email

### Step 1: URL is Still Down
Console shows:
```
[FAIL] | https://health.example.com
```
Logs show failures.

### Step 2: Unblock/Restore URL
Restore network connectivity to the URL.

### Step 3: Run Health Check
```bash
python run.py
```

**Expected Console Output:**
```
[OK] | https://health.example.com | Code: 200 | Time: 0.234s
     ↑ URL is UP again!

[RECOVERY] https://health.example.com UP after 180s downtime

✓ [EMAIL SENT] Recovery email notification sent for https://health.example.com
    To: Rohit.AvinashPagar@cognizant.com;...
```

**Email Check:** ✅ Recovery email SHOULD arrive with:
- [ ] Subject: "IKEA Health Check - Service Recovery Notification"
- [ ] Recipient: All 3 recipients
- [ ] CC: Bhavika.Kewalramani@cognizant.com
- [ ] BCC: Both contacts
- [ ] Shows service is now UP
- [ ] Shows downtime duration

---

## 🧪 TEST PLAN D: Verification of No Spam

### Objective: Confirm emails are NOT sent every cycle

### Scenario:
1. Block URL (triggers alert on 3rd check)
2. Keep URL blocked
3. Run 3 more health checks

**Expected:**
- [ ] 1st check after alert: ❌ No email (already sent once)
- [ ] 2nd check after alert: ❌ No email
- [ ] 3rd check after alert: ❌ No email
- [ ] **Total emails sent: 1** (not 3!)

**Verify in logs/health_check_alerts.log:**
```
[ALERT] https://health.example.com DOWN - Code: 0 - Connection Error
[ALERT] https://health.example.com DOWN - Code: 0 - Connection Error
[ALERT] https://health.example.com DOWN - Code: 0 - Connection Error
```

(Multiple failures logged, but only 1 email sent)

---

## ✅ EXPECTED BEHAVIOR SUMMARY

| Event | Expected Email | Explanation |
|-------|---|---|
| 1st URL failure | ❌ NO | consecutive_failures=1 |
| 2nd URL failure | ❌ NO | consecutive_failures=2 |
| 3rd URL failure | ✅ YES | consecutive_failures=3 (threshold) |
| 4th-10th failures | ❌ NO | Alert already sent, no duplicate |
| URL recovers | ✅ YES | Recovery notification |
| 5-min cycle pass | ❌ NO | Only event-triggered, not scheduled |

---

## 📝 LOG FILE LOCATIONS

### Monitor These Files During Testing

```
logs/
├── health_check.log              ← All events (most detailed)
├── health_check_alerts.log       ← Only alerts
├── health_check_report.json      ← Latest status snapshot
├── health_check_report.xlsx      ← Excel report (after each cycle)
└── index.html                    ← HTML dashboard
```

### What to Look For

**health_check.log:**
```
2026-02-16 10:05:00 - INFO - Loaded 3 URLs for monitoring
2026-02-16 10:05:01 - INFO - [OK] https://api.example.com
2026-02-16 10:05:02 - WARNING - FAILED: https://health.example.com
2026-02-16 10:05:02 - ERROR - [ALERT] https://health.example.com DOWN
2026-02-16 10:05:02 - INFO - ✓ [EMAIL SENT] Alert email notification sent
```

**health_check_alerts.log:**
```
2026-02-16 10:05:02 - ERROR - [ALERT] https://health.example.com DOWN
2026-02-16 10:05:30 - INFO - [RECOVERY] https://health.example.com UP after 28s downtime
```

---

## 🔧 TROUBLESHOOTING

### Issue: Email Not Sending

**Check 1: Outlook Running?**
```bash
tasklist | find "OUTLOOK.EXE"
```
Should show OUTLOOK.EXE in list.

**Check 2: Email Contacts Valid?**
```bash
python -c "from email_contacts import RECIPIENTS; print(RECIPIENTS)"
```

**Check 3: Error Messages?**
Look in console output for:
```
✗ [EMAIL FAILED] Error: ...
```

**Check 4: Log File?**
```bash
# Windows PowerShell:
Get-Content logs/health_check.log | Select-Object -Last 20
```

---

### Issue: Threshold Not Triggering at 3

**Check 1: Is config.ini correct?**
```bash
python -c "import configparser; c=configparser.ConfigParser(); c.read('config.ini'); print(c.get('MONITORING','alert_threshold'))"
```
Should print: `3`

**Check 2: Check consecutive_failures in logs:**
```
FAILED: ... (failure 1)
FAILED: ... (failure 2)
FAILED: ... (failure 3) ← Email should send here
```

---

### Issue: Too Many Emails

**Cause:** Emails sent for each cycle (old behavior)
**Fix:** Make sure run.py main section removed scheduled email call
- [ ] Should NOT have: `subprocess.run([sys.executable, 'email_alert_win32.py'])`
- [ ] Should only call email from `_send_alert()` method

---

## 📊 TEST RESULTS TEMPLATE

### Record Your Test Results

```
Test Date: _______________
Tester: ___________________

TEST PLAN A: Normal Operation
[ ] Step 1: Application starts - PASS / FAIL
[ ] Step 2: Logs created - PASS / FAIL
[ ] Step 3: Reports generated - PASS / FAIL
[ ] Step 4: HTML dashboard works - PASS / FAIL

TEST PLAN B: Alert Triggering
[ ] 1st check: No email - PASS / FAIL
[ ] 2nd check: No email - PASS / FAIL
[ ] 3rd check: EMAIL SENT - PASS / FAIL
  Email received at: ____________
  All recipients present: YES / NO
  Attachments included: YES / NO

TEST PLAN C: Recovery Email
[ ] URL unblocked - PASS / FAIL
[ ] Recovery email sent - PASS / FAIL
  Email received at: ____________

TEST PLAN D: No Spam Verification
[ ] Additional failures: No extra emails - PASS / FAIL
[ ] Total emails (should be 2): ____

Overall Result: ✅ PASS / ❌ FAIL

Notes:
________________________________
________________________________
```

---

## ✅ SIGN-OFF CHECKLIST

Before deploying to production:

- [ ] All 3 recipients receive emails
- [ ] CC recipient receives emails
- [ ] BCC recipients receive emails  
- [ ] Email sends on 3rd failure (not 1st or 2nd)
- [ ] Recovery email sends when URL comes back
- [ ] No duplicate emails for same failure
- [ ] HTML dashboard displays correctly
- [ ] All logs are created
- [ ] Excel report generates
- [ ] Console shows "[EMAIL SENT]" messages
- [ ] Threshold value is clearly documented
- [ ] Contact list is complete

---

## 🚀 READY FOR PRODUCTION?

If all tests PASS ✅:

```
NEXT STEPS:
1. Change config.ini check_interval from 60 to 300 (5 minutes)
2. Update urls.txt with actual production URLs
3. Test one more time with production settings
4. Deploy to monitoring server
5. Set to run automatically (Task Scheduler / Cron)
```

---

**Test Completion Date:** _______________
**Tester Signature:** ___________________
**Status:** Ready for ✅ Testing / ✅ Production Deployment

