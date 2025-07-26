@echo off
REM Remove Claude Memory API Server (System Tray) from Windows Startup

echo.
echo ========================================
echo   Removing System Tray from Startup
echo ========================================
echo.

REM Get Windows startup folder
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "STARTUP_BAT=%STARTUP_FOLDER%\ClaudeMemoryAPI-Tray.bat"

echo 🔍 Checking for startup file...

if exist "%STARTUP_BAT%" (
    echo 🗑️ Removing startup file...
    del /f /q "%STARTUP_BAT%" 2>nul
    
    if not exist "%STARTUP_BAT%" (
        echo ✅ Successfully removed system tray from Windows startup!
        echo 🔔 The API server will no longer start automatically.
    ) else (
        echo ❌ Failed to remove startup file!
        echo Please check permissions and try running as administrator.
        echo.
        echo Attempting with attrib command...
        attrib -r -s -h "%STARTUP_BAT%" 2>nul
        del /f /q "%STARTUP_BAT%" 2>nul
        
        if not exist "%STARTUP_BAT%" (
            echo ✅ Successfully removed after clearing attributes!
        ) else (
            echo ❌ Still unable to remove. File may be in use or protected.
        )
    )
) else (
    echo ⚠️ System tray startup is not currently installed.
    echo Nothing to remove.
)

echo.
echo 📍 Startup file location: %STARTUP_BAT%
echo.

pause