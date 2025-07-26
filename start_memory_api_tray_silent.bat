@echo off
REM Silent startup script for Claude Memory API System Tray
REM This script starts the tray app completely silently using pythonw

cd /d "%~dp0"

REM Check if pythonw.exe exists in virtual environment
if exist "venv\Scripts\pythonw.exe" (
    REM Use pythonw for completely windowless execution
    start "" "venv\Scripts\pythonw.exe" "memory_api_tray.py" --startup
) else if exist "venv\Scripts\python.exe" (
    REM Fallback to python with hidden window
    start "" /min "venv\Scripts\python.exe" "memory_api_tray.py" --startup
) else (
    REM Last resort - try system python
    where pythonw >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        start "" pythonw "memory_api_tray.py" --startup
    ) else (
        REM If pythonw not found, try python
        where python >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            start "" /min python "memory_api_tray.py" --startup
        ) else (
            REM No Python found - create error log
            echo ERROR: Python not found in system PATH or virtual environment > startup_error.log
            echo Please ensure Python is installed and added to PATH >> startup_error.log
        )
    )
)

REM Exit immediately - the tray app runs independently
exit