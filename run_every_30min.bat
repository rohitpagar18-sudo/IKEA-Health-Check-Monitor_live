@echo off
REM Run the IKEA Health Check every 30 minutes in a loop
:loop
    echo [%date% %time%] Running IKEA Health Check...
    python run.py --once
    echo Waiting 30 minutes before next run...
    timeout /t 1800
    goto loop
