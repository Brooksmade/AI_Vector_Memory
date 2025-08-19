@echo off
REM Claude Code Hook - Windows wrapper for memory check

REM Read JSON from stdin and save to temp file
set TEMP_FILE=%TEMP%\claude_hook_%RANDOM%.json
powershell -Command "[Console]::In.ReadToEnd()" > %TEMP_FILE%

REM Extract tool name and file path using PowerShell
for /f "delims=" %%i in ('powershell -Command "(Get-Content '%TEMP_FILE%' | ConvertFrom-Json).tool_name"') do set TOOL_NAME=%%i
for /f "delims=" %%i in ('powershell -Command "(Get-Content '%TEMP_FILE%' | ConvertFrom-Json).tool_input.file_path"') do set FILE_PATH=%%i

REM Check if it's a file operation
if "%TOOL_NAME%"=="Edit" goto :check
if "%TOOL_NAME%"=="Write" goto :check
if "%TOOL_NAME%"=="MultiEdit" goto :check
goto :end

:check
REM Call memory API using curl
curl -s -X POST http://localhost:8080/api/search ^
  -H "Content-Type: application/json" ^
  -d "{\"query\": \"%FILE_PATH% error bug fix\", \"max_results\": 3, \"similarity_threshold\": 0.5}" ^
  | powershell -Command "$input | ConvertFrom-Json | ForEach-Object { if($_.success) { $_.data.results | Where-Object { $_.similarity -gt 0.6 -and $_.preview -match 'error' } | ForEach-Object { Write-Host \"Warning: $($_.title) - $($_.date)\" } } }"

:end
REM Clean up
del %TEMP_FILE% 2>nul
exit /b 0