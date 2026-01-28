# Getting Started Checklist - IKEA Health Check Monitor

Use this checklist to ensure everything is properly set up and running.

## ✅ Pre-Installation (5 minutes)

- [ ] Python 3.7+ is installed
  - Check: Open PowerShell and run `python --version`
  - If not: Download from https://www.python.org/downloads/
  - Make sure "Add Python to PATH" is checked during installation

- [ ] You have internet connectivity
  - Check: Run `ping google.com`

- [ ] You have write access to the project folder
  - Check: Can create files in `C:\Users\2194998\OneDrive - Cognizant\Desktop\IKEA_health _check\`

## ✅ Installation (5 minutes)

- [ ] Navigate to project folder
  ```powershell
  cd "c:\Users\2194998\OneDrive - Cognizant\Desktop\IKEA_health _check"
  ```

- [ ] Install dependencies
  ```powershell
  pip install -r requirements.txt
  ```
  - Should see: "Successfully installed requests-X.X.X urllib3-X.X.X"

- [ ] Verify installation
  ```powershell
  python -c "import requests; print('OK')"
  ```
  - Should output: `OK`

## ✅ Verification (5 minutes)

- [ ] Run diagnostic tests
  ```powershell
  python test_monitor.py all
  ```
  - Should complete without critical errors
  - Files should show all green checkmarks (✓)

- [ ] Verify URLs are accessible
  - Check: `python test_monitor.py connectivity`
  - At least some URLs should show status 200

- [ ] Check configuration
  - Check: `python test_monitor.py config`
  - Should show valid configuration values

## ✅ Configuration (Optional - 5 minutes)

- [ ] Run setup wizard (optional)
  ```powershell
  python setup_config.py
  ```
  - Customize monitoring intervals
  - Configure email alerts (if desired)
  - Review and save configuration

- [ ] Review config.ini
  - Check: `notepad config.ini`
  - Verify settings match your requirements

- [ ] Verify urls.txt
  - Check: `notepad urls.txt`
  - Should have 15 URLs
  - Each URL should start with `http://`

## ✅ First Test Run (10 minutes)

- [ ] Start the monitor
  ```powershell
  python health_check_monitor.py
  ```

- [ ] Watch for 2-3 check cycles (10-15 minutes)
  - Should see ✓ for healthy URLs
  - Should see ✗ for any failed URLs
  - Check intervals show in console

- [ ] Verify log files created
  - Check: `ls logs/`
  - Should see:
    - `health_check.log` (growing)
    - `health_check_alerts.log`
    - `health_check_report.json`

- [ ] Generate a test report
  - Open new PowerShell window
  - Run: `python report_generator.py`
  - Should show status table with all 15 URLs

- [ ] Stop the monitor
  - Press `Ctrl+C`
  - Should say: "Monitoring stopped by user"

## ✅ Report Generation (5 minutes)

- [ ] Generate console report
  ```powershell
  python report_generator.py
  ```
  - Should show summary and table

- [ ] Generate HTML report
  ```powershell
  python report_generator.py html report.html
  start report.html
  ```
  - Should open in browser
  - Should show dashboard with status cards

- [ ] Generate CSV report
  ```powershell
  python report_generator.py csv report.csv
  ```
  - Should create report.csv file
  - Can open in Excel

## ✅ Email Setup (Optional - 10 minutes)

- [ ] Decide if you want email alerts
  - No: Skip to continuous monitoring
  - Yes: Continue below

- [ ] Get SMTP credentials
  - For Gmail: https://myaccount.google.com/apppasswords
  - Select "Mail" and "Windows"
  - Generate and copy 16-character password

- [ ] Run configuration wizard
  ```powershell
  python setup_config.py
  ```
  - Enter SMTP details
  - Enter sender email
  - Enter app password
  - Enter recipient emails

- [ ] Test email functionality
  - Edit health_check_monitor.py (find `Config.ENABLE_EMAIL_ALERTS = False`)
  - Change to `True` temporarily
  - Run: `python health_check_monitor.py`
  - Force failure or wait for failure
  - Check if alert email arrives
  - Change back to `False`

## ✅ Continuous Monitoring (5 minutes)

### Option 1: Manual Monitoring
- [ ] Keep PowerShell window open
  ```powershell
  python health_check_monitor.py
  ```
- [ ] Monitor stays running until you close the window

### Option 2: Windows Task Scheduler (Recommended)
- [ ] Open Task Scheduler (`Win + R` → `taskschd.msc`)
- [ ] Follow TASK_SCHEDULER_SETUP.md to create task
- [ ] Set to run at startup
- [ ] Restart computer to test
- [ ] Verify task ran:
  ```powershell
  Get-Content logs/health_check.log -Tail 20
  ```

### Option 3: Background Process
- [ ] Use batch file:
  ```powershell
  .\start_monitor.bat
  ```
- [ ] Window will stay open
- [ ] Can minimize it

## ✅ Monitoring Verification (Ongoing)

Daily checks:
- [ ] Monitor is still running
  ```powershell
  Get-Process python
  ```

- [ ] Logs are updating
  ```powershell
  Get-ChildItem logs/ | Sort-Object LastWriteTime -Descending | Select -First 3
  ```

- [ ] No critical errors
  ```powershell
  Get-Content logs/health_check_alerts.log -Tail 10
  ```

Weekly checks:
- [ ] Generate weekly report
  ```powershell
  python report_generator.py html weekly_report.html
  ```

- [ ] Review failure patterns
  - Which URLs fail most?
  - Are there time-based patterns?
  - Do failures correlate with events?

- [ ] Check disk space
  ```powershell
  Get-ChildItem logs/ | Measure-Object -Property Length -Sum
  ```

## ✅ Troubleshooting

If you encounter issues:

1. **URLs not loading**
   ```powershell
   python test_monitor.py connectivity
   Test-Connection -ComputerName google.com
   ```

2. **Missing packages**
   ```powershell
   pip install -r requirements.txt
   pip show requests
   ```

3. **Permission errors**
   - Run PowerShell as Administrator
   - Check folder permissions
   - Try `icacls "C:\path\to\folder" /grant:r "%username%":(OI)(CI)F`

4. **Script crashes**
   ```powershell
   python health_check_monitor.py 2>&1 | Tee crash.log
   cat crash.log
   ```

5. **Email not working**
   - Verify SMTP server and port: `telnet smtp.gmail.com 587`
   - Check password is app password, not regular password
   - Review `logs/health_check.log` for errors
   - Test credentials in Python:
     ```python
     import smtplib
     smtplib.SMTP('smtp.gmail.com', 587).starttls()
     ```

## ✅ Documentation Review

Recommended reading (in order):

1. [ ] PROJECT_SUMMARY.md (This overview)
2. [ ] QUICKSTART.md (Fast setup)
3. [ ] README.md (Complete reference)
4. [ ] config.ini (Configuration options)
5. [ ] TASK_SCHEDULER_SETUP.md (If running 24/7)

## ✅ Final Setup Confirmation

Before considering setup complete:

- [ ] All diagnostic tests pass (`python test_monitor.py all`)
- [ ] Monitor runs successfully for at least 30 minutes
- [ ] At least one report is generated and readable
- [ ] Logs are being created and updated
- [ ] You understand how to:
  - Start/stop monitoring
  - Generate reports
  - Check logs
  - Enable email alerts
  - Set up continuous monitoring

- [ ] You have documented:
  - Where the project folder is
  - How to start monitoring
  - How to check status
  - Who to contact if issues occur

## 🎉 You're All Set!

Once all checkboxes are complete, your IKEA Health Check Monitor is ready for production use.

### What to do next:
1. Set up continuous monitoring via Windows Task Scheduler
2. Create daily/weekly report review process
3. Document your alerts contact list
4. Brief your team on the system
5. Monitor for the first week closely, then adjust as needed

### Keep in mind:
- **Logs directory**: Grows by ~1-10 MB per day
- **Reports**: Generated on demand, no automatic storage
- **Monitoring**: Runs 24/7 once configured
- **Alerts**: Can be sent to multiple recipients
- **Performance**: Low resource usage (<5% CPU, <100 MB RAM)

### Support:
- Check `README.md` for detailed documentation
- Review logs in `logs/` directory for specific issues
- Run `python test_monitor.py` to diagnose problems
- Check Windows Event Viewer for task-related issues

---

**Questions?** Review the documentation files or check the logs for error messages.

**Ready to deploy?** Set up continuous monitoring via Windows Task Scheduler and configure email alerts!
