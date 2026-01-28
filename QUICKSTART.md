# Quick Start Guide - IKEA Health Check Monitor

## 5-Minute Setup

### Step 1: Install Dependencies (1 minute)

Open PowerShell and navigate to the project directory:

```powershell
cd "c:\Users\2194998\OneDrive - Cognizant\Desktop\IKEA_health _check"
pip install -r requirements.txt
```

### Step 2: Verify Setup (1 minute)

Run the health check script:

```powershell
python health_check_monitor.py
```

You should see:
- A list of 15 URLs being monitored
- Health check cycle starting
- Status updates with checkmarks (✓) and X marks (✗)

**Press Ctrl+C to stop the script**

### Step 3: Check the Logs (1 minute)

Open the `logs/` folder created by the script:

```powershell
explorer "logs\"
```

You'll see:
- `health_check.log` - All activities
- `health_check_alerts.log` - Only alerts
- `health_check_report.json` - Current status report

### Step 4: Generate Your First Report (1 minute)

In the same directory, run:

```powershell
python report_generator.py
```

This displays a text report of current server status.

### Step 5: Run Continuously (Optional)

To keep monitoring running in the background:

```powershell
# Option 1: Run in the same terminal
python health_check_monitor.py

# Option 2: Run in a new terminal window (recommended)
Start-Process powershell -ArgumentList "-NoExit", "-Command `"cd '$((pwd))'; python health_check_monitor.py`""
```

## Common Tasks

### View HTML Dashboard

```powershell
python report_generator.py html health_report.html
start health_report.html
```

### Export to CSV

```powershell
python report_generator.py csv health_report.csv
```

### View Real-time Logs

```powershell
Get-Content logs/health_check.log -Wait
```

### View Only Alerts

```powershell
Get-Content logs/health_check_alerts.log -Wait
```

## Configuration Tips

### Faster Checking

Edit `config.ini` and change:
```ini
check_interval = 60  # Check every 1 minute instead of 5
```

### Longer Timeouts

For slower networks:
```ini
request_timeout = 20  # 20 seconds instead of 10
```

### Email Alerts

To enable email notifications:

1. Edit `config.ini`:
```ini
enabled = true
sender_email = your_email@gmail.com
sender_password = your_app_password
recipient_emails = admin@ikea.com,ops@ikea.com
```

2. For Gmail, get an App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Generate an app password for "Mail" and "Windows"
   - Copy the 16-character password to `sender_password`

## File Structure

```
IKEA_health _check/
├── health_check_monitor.py      # Main monitoring script
├── report_generator.py          # Report generation tool
├── urls.txt                     # List of URLs to monitor
├── config.ini                   # Configuration file
├── requirements.txt             # Python dependencies
├── README.md                    # Full documentation
├── QUICKSTART.md                # This file
└── logs/                        # Created automatically
    ├── health_check.log
    ├── health_check_alerts.log
    └── health_check_report.json
```

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'requests'"

```powershell
pip install requests
```

### URLs not loading or showing connection errors

1. Check your internet connection:
```powershell
Test-Connection google.com
```

2. Check if URLs are accessible:
```powershell
Invoke-WebRequest http://retat085-lx4020.ikea.com:7003/web/ -TimeoutSec 10
```

3. Check for proxy/firewall issues with your IT team

### High CPU or Memory Usage

Increase the check interval:
```ini
check_interval = 600  # Check every 10 minutes
```

## Next Steps

1. ✅ Run the monitoring script for 30 minutes to collect baseline data
2. ✅ Review the HTML report to understand your server status
3. ✅ Configure email alerts if you want automatic notifications
4. ✅ Set up the script to run as a Windows Service (see README.md)
5. ✅ Create a dashboard in your monitoring tool (Grafana, etc.)

## Support

- Full documentation: See `README.md`
- Log files: Check `logs/health_check.log`
- Configuration: Edit `config.ini`
- URL list: Edit `urls.txt`

---

**That's it! Your health check monitor is now running.** 🎉
