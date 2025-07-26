@echo off
echo Checking Windows Startup folder...
echo.
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
echo Startup folder: %STARTUP_FOLDER%
echo.
echo Files in startup:
dir "%STARTUP_FOLDER%" /b 2>nul || echo [Empty]
echo.
echo Claude-related files:
dir "%STARTUP_FOLDER%\*Claude*.*" /b 2>nul || echo [None]
dir "%STARTUP_FOLDER%\*memory*.*" /b 2>nul || echo [None]