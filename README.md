# IKEA Server Health Check Monitor

## Overview

This is an automated health check monitoring tool designed to continuously monitor IKEA server URLs, detect downtime, and provide timely alerts for proactive resolution. It helps improve operational visibility and reduces the risk of disruptions to store activities.

## Features

✅ **Continuous URL Monitoring** - Automatically checks server availability at configurable intervals
✅ **Health Status Tracking** - Maintains detailed history of each URL's health status
✅ **Automatic Alerting** - Sends alerts when servers go down or come back online
✅ **Email Notifications** - Optional email alerts for critical failures (requires SMTP configuration)
✅ **Comprehensive Logging** - Detailed logs for audit trails and troubleshooting
✅ **JSON Reporting** - Machine-readable reports for integration with other tools
✅ **HTML & CSV Reports** - User-friendly report generation in multiple formats
✅ **Response Time Tracking** - Monitors server response times for performance analysis
✅ **Failure Rate Statistics** - Overall and per-URL failure rate tracking
✅ **Downtime Duration Tracking** - Records how long each outage lasted

## Monitored URLs

The tool monitors the following 15 IKEA server endpoints:

1. http://retat085-lx4020.ikea.com:7003/web/
2. http://rca1270-lx4020.ikea.com:7003/web/
3. http://rus1100-lx4020.ikea.com:7003/web/
4. http://retse470-lx4020.ikea.com:7003/web/
5. http://retro500-lx4030.ikea.com:7003/web/
6. http://retpl307-lx4030.ikea.com:7003/web/
7. http://rjp1176-lx4020.ikea.com:7003/web/
8. http://retit295-lx4020.ikea.com:7003/web/
9. http://retin629-lx4020.ikea.com:7003/web/
10. http://itseelm-lx44097.ikea.com:7003/web/
11. http://rgb1010-lx4020.ikea.com:7003/web/
12. http://retfr562-lx4020.ikea.com:7003/web/
13. http://retes502-lx4030.ikea.com:7003/web/
14. http://res12852-lx4030.ikea.com:7003/web/
15. http://retdk172-lx4020.ikea.com:7003/web/

## Installation

### 1. Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
python health_check_monitor.py
```

You should see the list of URLs being monitored and the health check cycle starting.

## Configuration

### Basic Configuration (config.ini)

Edit `config.ini` to customize monitoring parameters:

```ini
[MONITORING]
check_interval = 300              # Seconds between checks (default: 5 minutes)
quick_check_interval = 60         # Quick check interval for failed URLs (1 minute)
request_timeout = 10              # Request timeout in seconds
alert_threshold = 2               # Consecutive failures before alerting

[LOGGING]
log_directory = logs              # Where to store log files
log_file = health_check.log       # Main log file
alert_log_file = health_check_alerts.log

[EMAIL_ALERTS]
enabled = false                   # Set to true to enable email alerts
smtp_server = smtp.gmail.com
sender_email = your_email@gmail.com
sender_password = your_app_password
recipient_emails = admin@ikea.com,ops@ikea.com
```

### Email Configuration (Optional)

To enable email alerts:

1. Set `enabled = true` in `config.ini`
2. Configure SMTP credentials:
   - For Gmail: Use an [App Password](https://support.google.com/accounts/answer/185833)
   - For other providers: Use your email provider's SMTP settings
3. Update recipient email addresses

## Usage

### 1. Start Monitoring

```bash
python health_check_monitor.py
```

The tool will:
- Load URLs from `urls.txt`
- Start checking each URL every 5 minutes
- Create a `logs/` directory for storing logs and reports
- Display status updates in the console
- Log all activities to `logs/health_check.log`

### 2. View Real-time Status

Monitor the console output while the script runs. You'll see:
- ✓ Checkmarks for healthy servers
- ✗ X marks for failed servers
- Status codes and response times
- Alert notifications when issues are detected

### 3. Generate Reports

While monitoring is running, you can generate reports in another terminal:

#### Console Report
```bash
python report_generator.py
```

#### HTML Report
```bash
python report_generator.py html health_check_report.html
```

Then open `health_check_report.html` in your browser.

#### CSV Report
```bash
python report_generator.py csv health_check_report.csv
```

## Log Files

The tool creates logs in the `logs/` directory:

- **health_check.log** - Detailed log of all health checks and activities
- **health_check_alerts.log** - Only alert messages (downs and recoveries)
- **health_check_report.json** - Machine-readable status report

## Understanding the Output

### Console Output Example

```
================================================================================
IKEA SERVER HEALTH CHECK MONITORING TOOL
================================================================================

URLs being monitored:
--------------------------------------------------------------------------------
 1. http://retat085-lx4020.ikea.com:7003/web/
 2. http://rca1270-lx4020.ikea.com:7003/web/
[... more URLs ...]
--------------------------------------------------------------------------------

================================================================================
Starting health check cycle...
================================================================================
✓ http://retat085-lx4020.ikea.com:7003/web/ - Status: 200 - Response Time: 0.234s
✓ http://rca1270-lx4020.ikea.com:7003/web/ - Status: 200 - Response Time: 0.189s
✗ http://retse470-lx4020.ikea.com:7003/web/ - Status: 0 - Connection error
[... more results ...]
```

### Alert Messages

When a server goes down:
```
ERROR - 🚨 ALERT: Server Down
URL: http://retse470-lx4020.ikea.com:7003/web/
Status Code: 0
Error: Connection error
Time: 2025-01-28 14:30:45
Consecutive Failures: 2
```

When a server comes back online:
```
WARNING - ✓ RECOVERY: Server Back Online
URL: http://retse470-lx4020.ikea.com:7003/web/
Downtime Duration: 300 seconds
```

## Monitoring Strategy

### Check Intervals

- **Normal Mode**: Checks run every 5 minutes (300 seconds)
- **Quick Check Mode**: When any URL is down, checks run every 1 minute (60 seconds) for faster recovery detection

### Alert Mechanism

- **Trigger**: 2 consecutive failed checks
- **On Recovery**: Immediate alert with downtime duration
- **Email Alerts**: Optional notifications for critical failures

### Healthy Status Codes

The following HTTP status codes indicate a healthy server:
- 200 (OK)
- 201 (Created)
- 202 (Accepted)
- 204 (No Content)
- 301 (Moved Permanently)
- 302 (Found)
- 304 (Not Modified)
- 307 (Temporary Redirect)
- 308 (Permanent Redirect)

## Troubleshooting

### Issue: "No URLs found" error

**Solution**: Ensure `urls.txt` exists in the same directory as the script and contains valid URLs.

### Issue: Connection errors for all URLs

**Solution**: 
1. Check your internet connection
2. Verify the URLs are accessible from your network
3. Check if there's a proxy or firewall blocking access

### Issue: Email alerts not working

**Solution**:
1. Verify SMTP credentials in `config.ini`
2. If using Gmail, ensure you've generated an App Password
3. Check firewall settings - port 587 might be blocked
4. Enable "Less secure app access" if using older Gmail accounts

### Issue: Script uses high CPU

**Solution**: Increase `check_interval` in `config.ini` to run checks less frequently

## Performance Considerations

- **CPU Usage**: Minimal - mainly I/O bound operations
- **Memory Usage**: ~50-100 MB depending on history size
- **Network Usage**: ~1-2 KB per check per URL
- **Disk Usage**: ~1-10 MB per day for logs

## Integration Examples

### Running as Windows Service

Use NSSM (Non-Sucking Service Manager) or Task Scheduler:

```powershell
# Using Task Scheduler
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "C:\path\to\health_check_monitor.py"
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "IKEA Health Check"
```

### Integration with Monitoring Tools

The `health_check_report.json` file can be read by:
- Prometheus (via custom exporter)
- Grafana (via JSON data source)
- ELK Stack (via Logstash)
- Splunk (via HTTP Event Collector)

## Development

To extend the monitoring tool:

1. **Add Custom Checks**: Modify `check_url_health()` in `health_check_monitor.py`
2. **Custom Alerts**: Extend `_send_alert()` to integrate with your alerting system
3. **Additional Metrics**: Add fields to the report generation logic

## Support

For issues or questions:

1. Check the `logs/` directory for detailed error messages
2. Review `health_check.log` for system-level issues
3. Verify `urls.txt` format and URL accessibility
4. Ensure all dependencies are installed: `pip install -r requirements.txt`

## License

This tool is provided for IKEA internal use.

## Version

Version 1.0.0 - January 2025

---

**Remember**: Configure email alerts appropriately and monitor the logs regularly for best results!
