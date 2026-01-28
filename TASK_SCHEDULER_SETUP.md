# Setting Up Windows Task Scheduler for Continuous Monitoring

This guide helps you set up the IKEA Health Check Monitor to run automatically at startup or on a schedule.

## Option 1: Run at Windows Startup (Recommended)

### Step 1: Open Task Scheduler
Press `Win + R`, type `taskschd.msc` and press Enter.

### Step 2: Create New Task
1. Right-click "Task Scheduler Library" → Select "Create New Task"
2. Name: `IKEA Health Check Monitor`
3. Description: `Automated monitoring of IKEA server URLs`
4. Select "Run whether user is logged in or not"
5. Click "Change User or Group" and select your user account

### Step 3: Configure Trigger
1. Go to "Triggers" tab
2. Click "New..."
3. Set trigger as "At startup"
4. Check "Enabled"
5. Click OK

### Step 4: Configure Action
1. Go to "Actions" tab
2. Click "New..."
3. Action: "Start a program"
4. Program: `python.exe`
5. Arguments: `"C:\Users\2194998\OneDrive - Cognizant\Desktop\IKEA_health _check\health_check_monitor.py"`
6. Start in: `C:\Users\2194998\OneDrive - Cognizant\Desktop\IKEA_health _check`
7. Click OK

### Step 5: Configure Conditions (Optional)
1. Go to "Conditions" tab
2. Uncheck "Stop if the computer switches to battery power" (if desired)
3. Check "Wake the computer to run this task"

### Step 6: Configure Settings
1. Go to "Settings" tab
2. Check "Run task as soon as possible after a scheduled start is missed"
3. Set "If the task fails, restart every: 5 minutes"
4. Set "Stop the task if it runs longer than: 3 days"
5. Click OK

### Step 7: Confirm Credentials
When prompted, enter your Windows password and click OK.

## Option 2: Run at Specific Time

### Example: Run every 6 hours

1. Follow Steps 1-2 above
2. In "Triggers" tab, click "New..."
3. Set trigger as "On a schedule"
4. Repeat task every 6 hours
5. Continue with Steps 4-7 above

## Option 3: Run Every Hour (For Active Monitoring)

1. Follow Steps 1-2 above
2. In "Triggers" tab, click "New..."
3. Set:
   - Begin the task: "On a schedule"
   - Repeat task every: "1 hour"
   - Duration: "Indefinitely" (or set end date)
4. Continue with Steps 4-7 above

## Using PowerShell (Advanced)

If you prefer command-line setup:

```powershell
# Run as Administrator
$taskPath = "IKEA_Health_Check"
$taskName = "Monitor"
$scriptPath = "C:\Users\2194998\OneDrive - Cognizant\Desktop\IKEA_health _check\health_check_monitor.py"
$workingDir = "C:\Users\2194998\OneDrive - Cognizant\Desktop\IKEA_health _check"

# Create trigger (at startup)
$trigger = New-ScheduledTaskTrigger -AtStartup

# Create action
$action = New-ScheduledTaskAction -Execute "python.exe" `
    -Argument """$scriptPath""" `
    -WorkingDirectory $workingDir

# Create settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register the task
Register-ScheduledTask -TaskPath $taskPath -TaskName $taskName `
    -Trigger $trigger -Action $action -Settings $settings `
    -Description "IKEA Server Health Check Monitor" -Force
```

## Using Batch Script (Simpler)

```batch
@echo off
REM Create Windows scheduled task for health check monitor
REM Run as Administrator

set SCRIPT_PATH=C:\Users\2194998\OneDrive - Cognizant\Desktop\IKEA_health _check\health_check_monitor.py
set WORK_DIR=C:\Users\2194998\OneDrive - Cognizant\Desktop\IKEA_health _check

REM Create task at startup
schtasks /create /tn "IKEA_Health_Check\Monitor" ^
    /tr "python.exe %SCRIPT_PATH%" ^
    /sc onstart /rl highest /f

echo Task created successfully!
```

## Viewing Running Tasks

### In Task Scheduler
1. Open Task Scheduler
2. Navigate to: Task Scheduler Library → IKEA_Health_Check
3. Right-click "Monitor" → "Run" to run immediately
4. Right-click "Monitor" → "Properties" to edit

### In PowerShell
```powershell
# List all tasks
Get-ScheduledTask | grep IKEA

# Get task details
Get-ScheduledTask -TaskPath "\IKEA_Health_Check\" -TaskName "Monitor"

# Run task immediately
Start-ScheduledTask -TaskPath "\IKEA_Health_Check\" -TaskName "Monitor"

# Stop running task
Stop-ScheduledTask -TaskPath "\IKEA_Health_Check\" -TaskName "Monitor"
```

## Checking Task Status

### Method 1: Task Scheduler GUI
Open Task Scheduler and look for "IKEA_Health_Check" → "Monitor"
- "Status" column shows if it's running
- "Last Run Result" shows success (0) or error codes

### Method 2: Check Log Files
```powershell
# View latest 50 lines of health check log
Get-Content "C:\Users\2194998\OneDrive - Cognizant\Desktop\IKEA_health _check\logs\health_check.log" -Tail 50

# Monitor logs in real-time
Get-Content "C:\Users\2194998\OneDrive - Cognizant\Desktop\IKEA_health _check\logs\health_check.log" -Wait
```

### Method 3: Check Process
```powershell
# See if Python script is running
Get-Process python -ErrorAction SilentlyContinue | Select-Object ProcessName, CPU, Memory

# Count running Python processes
(Get-Process python -ErrorAction SilentlyContinue | Measure-Object).Count
```

## Troubleshooting

### Task Won't Run at Startup

**Problem**: Task created but doesn't run at startup

**Solutions**:
1. Verify "Run whether user is logged in or not" is selected
2. Check "Run with highest privileges"
3. Ensure user account password is set (task won't run without password)
4. Look at event logs: Event Viewer → Windows Logs → System
5. Check script path doesn't have spaces (use quotes if needed)

### Python Not Found

**Problem**: Error "Python not found" or "python.exe cannot be executed"

**Solutions**:
1. Use full path to Python: `C:\Python39\python.exe`
2. Add Python to PATH environment variable
3. Verify Python installation: Run `python --version` in PowerShell
4. Check in Settings → System → Advanced → Environment Variables

### Task Keeps Stopping

**Problem**: Task starts but stops after a few minutes

**Solutions**:
1. Increase "Stop the task if it runs longer than" setting (set to 3 days or more)
2. Check "Run task as soon as possible" in Settings tab
3. Check Windows power settings aren't sleeping the computer
4. Review logs in `health_check.log` for errors

### Logs Not Being Created

**Problem**: No logs directory or files being created

**Solutions**:
1. Verify working directory is set correctly
2. Check user account has write permissions to script folder
3. Run task manually from Task Scheduler to see error messages
4. Check event logs in Event Viewer

### Email Alerts Not Sending

**Problem**: Task runs but email alerts aren't sent

**Solutions**:
1. Verify email is enabled in `config.ini`
2. Check SMTP credentials are correct
3. Verify firewall allows outbound SMTP (port 587 or 25)
4. Check `health_check.log` for email-related errors
5. Test email settings by running script manually

## Removing the Task

### Using Task Scheduler GUI
1. Open Task Scheduler
2. Right-click the task → "Delete"
3. Confirm deletion

### Using PowerShell
```powershell
# As Administrator
Unregister-ScheduledTask -TaskPath "\IKEA_Health_Check\" -TaskName "Monitor" -Confirm:$false
```

### Using Command Prompt
```cmd
REM As Administrator
schtasks /delete /tn "IKEA_Health_Check\Monitor" /f
```

## Monitoring Multiple Instances

If you want to run multiple monitoring schedules:

```powershell
# Example: Different intervals for different URL groups
Register-ScheduledTask -TaskName "IKEA_Monitor_Fast" -Trigger @(New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)) ...
Register-ScheduledTask -TaskName "IKEA_Monitor_Reports" -Trigger @(New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)) ...
```

## Best Practices

1. ✅ Use "Run whether user is logged in or not" for continuous monitoring
2. ✅ Set restart on failure to automatically recover from issues
3. ✅ Configure long timeout (3 days) so task won't be killed
4. ✅ Check logs regularly to verify monitoring is working
5. ✅ Test task manually before relying on it
6. ✅ Document the setup in your change log
7. ✅ Monitor task's status periodically
8. ✅ Set up email alerts for critical failures

## Verification Checklist

After setup, verify:
- [ ] Task appears in Task Scheduler
- [ ] Task status is "Ready" (not "Running" or "Disabled")
- [ ] Last Run Result shows "0" (success)
- [ ] Last Run Time is recent (within last hour)
- [ ] Log files are being updated in `logs/` directory
- [ ] Reports are being generated
- [ ] No errors in Windows Event Viewer

## Need Help?

1. Check Task Scheduler History (right-click task → Properties → History)
2. Review Windows Event Viewer (Event Viewer → Windows Logs → System)
3. Check application logs in `logs/health_check.log`
4. Verify script works manually: `python health_check_monitor.py`
5. Test configuration: `python test_monitor.py`

---

**Your health check monitor is now set to run automatically!** 🚀
