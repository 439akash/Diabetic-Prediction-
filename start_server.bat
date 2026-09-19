@echo off
echo Starting DiaPredict Local Server...
py serve.py
if %ERRORLEVEL% NEQ 0 (
    python serve.py
)
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Could not find Python. Please install Python from python.org
    pause
)
pause
