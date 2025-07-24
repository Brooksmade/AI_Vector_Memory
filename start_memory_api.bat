@echo off
REM Claude Memory API Server - Windows Startup Script
REM This script starts the Memory API server with proper environment setup

echo.
echo ========================================
echo   Claude Memory API Server Startup
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Error: Virtual environment not found!
    echo.
    echo Please run the following commands first:
    echo   python -m venv venv
    echo   venv\Scripts\activate.bat
    echo   pip install -r requirements.txt
    echo   pip install -r requirements_api.txt
    echo.
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "memory_api_server.py" (
    echo ❌ Error: API server file not found!
    echo Please ensure memory_api_server.py exists in this directory.
    pause
    exit /b 1
)

if not exist "chroma_db" (
    echo ⚠️  Warning: ChromaDB directory not found!
    echo The database will be created automatically on first run.
    echo.
)

REM Check if Flask is installed
echo 🔍 Checking dependencies...
call venv\Scripts\activate.bat
python -c "import flask, flask_cors, flask_limiter" 2>nul
if errorlevel 1 (
    echo ❌ Error: Required dependencies not installed!
    echo.
    echo Installing dependencies...
    pip install -r requirements_api.txt
    if errorlevel 1 (
        echo Failed to install dependencies.
        pause
        exit /b 1
    )
)

REM Check system resources
echo 📊 System Check:
echo   - Virtual environment: ✅ Active
echo   - Python version: 
python --version
echo   - Memory API dependencies: ✅ Installed
echo   - Database path: %cd%\chroma_db
echo.

REM Set environment variables for production
set FLASK_ENV=production
set FLASK_DEBUG=0
set PYTHONPATH=%cd%

echo 🚀 Starting Claude Memory API Server...
echo.
echo 📍 Server will be available at: http://localhost:8080
echo 🔗 Integration endpoints:
echo   - Search:     POST /api/search
echo   - Add Memory: POST /api/add_memory  
echo   - Health:     GET  /api/health
echo   - List:       GET  /api/memories
echo.
echo 💡 Usage Examples:
echo   curl -X GET http://localhost:8080/api/health
echo   curl -X POST http://localhost:8080/api/search -H "Content-Type: application/json" -d "{\"query\":\"python flask\"}"
echo.
echo ⏸️  Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start the server
python memory_api_server.py

REM Handle server shutdown
echo.
echo 🛑 Server stopped.
echo.
pause