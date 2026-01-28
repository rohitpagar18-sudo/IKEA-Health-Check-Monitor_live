@echo off
REM Windows Task Scheduler/cron alternative: Run health check every 30 minutes
:loop
python health_check_monitor.py --once
REM Wait 30 minutes (1800 seconds)
timeout /t 1800
GOTO loop
