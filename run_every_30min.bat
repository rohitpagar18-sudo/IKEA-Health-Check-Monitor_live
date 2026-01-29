@echo off
REM Run the IKEA Health Check in a continuous loop (handled by run.py)
echo [%date% %time%] Starting IKEA Health Check continuous monitoring...
python run.py
