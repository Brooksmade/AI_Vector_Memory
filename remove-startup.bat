@echo off
REM Remove Claude Memory API Server from Windows Startup

echo.
echo ========================================
echo   Removing from Windows Startup
echo ========================================
echo.

REM Get startup folder
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "STARTUP_BAT=%STARTUP_FOLDER%\ClaudeMemoryAPI.bat"

REM Check if startup file exists
if exist "%STARTUP_BAT%" (
    echo 🗑️ Removing startup file...
    del "%STARTUP_BAT%"
    
    if not exist "%STARTUP_BAT%" (
        echo ✅ Successfully removed from Windows startup!
        echo The API server will no longer start automatically.
    ) else (
        echo ❌ Failed to remove startup file!
        echo Please delete manually: %STARTUP_BAT%
    )
) else (
    echo ℹ️ Startup file not found - nothing to remove.
    echo Location checked: %STARTUP_BAT%
)

echo.
pause