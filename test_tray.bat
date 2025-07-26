@echo off
echo Testing Claude Memory API System Tray...
cd /d "%~dp0"

REM Test with pythonw.exe (no window)
if exist "venv\Scripts\pythonw.exe" (
    echo Starting with pythonw.exe (no console window)...
    "venv\Scripts\pythonw.exe" "memory_api_tray.py"
) else (
    echo pythonw.exe not found, using python.exe...
    "venv\Scripts\python.exe" "memory_api_tray.py"
)

pause