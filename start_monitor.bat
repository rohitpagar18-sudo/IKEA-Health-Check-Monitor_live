@echo off
REM IKEA Health Check Monitor - Startup Script for Windows
REM This script starts the health check monitor and creates a log window

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo IKEA SERVER HEALTH CHECK MONITOR
echo ============================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if requirements are installed
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install requirements
        pause
        exit /b 1
    )
)

REM Check if urls.txt exists
if not exist "urls.txt" (
    echo ERROR: urls.txt not found!
    echo Please ensure urls.txt exists in the current directory
    pause
    exit /b 1
)

echo Starting health check monitor...
echo.
echo URLs being monitored:
type urls.txt
echo.
echo ============================================================================
echo Monitoring started. Check logs/ directory for detailed logs.
echo Logs:
echo   - health_check.log        (All activities)
echo   - health_check_alerts.log (Alerts only)
echo   - health_check_report.json (Status report)
echo.
echo Press Ctrl+C to stop monitoring
echo ============================================================================
echo.

REM Start the monitor
python health_check_monitor.py

if errorlevel 1 (
    echo.
    echo ERROR: Health check monitor encountered an error
    echo Check the error message above and logs/health_check.log for details
    pause
)

endlocal
