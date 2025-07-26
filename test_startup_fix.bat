@echo off
echo Testing startup fixes...
echo.

REM Kill any existing processes
echo Killing any existing memory API processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *memory_api*" 2>nul
taskkill /F /IM pythonw.exe /FI "WINDOWTITLE eq *memory_api*" 2>nul
timeout /t 2 >nul

echo.
echo Starting memory API tray (should not open Notepad)...
call start_memory_api_tray_silent.bat

timeout /t 10

echo.
echo Checking if server is running...
curl -s http://localhost:8080/api/health > test_health.json 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Server is running!
    type test_health.json
) else (
    echo ❌ Server is not responding
)

echo.
echo Check the system tray for the Memory API icon.
echo.
pause