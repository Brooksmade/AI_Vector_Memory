# Claude Memory API Server - PowerShell Startup Script
# This script provides a more advanced startup experience with health checks and monitoring

param(
    [switch]$Debug,
    [switch]$SkipHealthCheck,
    [string]$Port = "8080",
    [string]$Host = "localhost"
)

# Colors for output
$ErrorColor = "Red"
$WarningColor = "Yellow" 
$SuccessColor = "Green"
$InfoColor = "Cyan"

function Write-StatusMessage {
    param([string]$Message, [string]$Status = "Info")
    
    $color = switch ($Status) {
        "Error" { $ErrorColor }
        "Warning" { $WarningColor }
        "Success" { $SuccessColor }
        default { $InfoColor }
    }
    
    Write-Host $Message -ForegroundColor $color
}

function Test-Prerequisites {
    Write-StatusMessage "🔍 Checking prerequisites..." "Info"
    
    # Check if we're in the right directory
    if (-not (Test-Path "memory_api_server.py")) {
        Write-StatusMessage "❌ Error: memory_api_server.py not found in current directory!" "Error"
        Write-StatusMessage "Please run this script from the claude-code-vector-memory directory." "Error"
        return $false
    }
    
    # Check virtual environment
    if (-not (Test-Path "venv\Scripts\python.exe")) {
        Write-StatusMessage "❌ Error: Virtual environment not found!" "Error"
        Write-StatusMessage "Please create virtual environment first:" "Info"
        Write-StatusMessage "  python -m venv venv" "Info"
        Write-StatusMessage "  .\venv\Scripts\Activate.ps1" "Info"
        Write-StatusMessage "  pip install -r requirements.txt" "Info"
        Write-StatusMessage "  pip install -r requirements_api.txt" "Info"
        return $false
    }
    
    # Check database directory
    if (-not (Test-Path "chroma_db")) {
        Write-StatusMessage "⚠️  Warning: ChromaDB directory not found - will be created automatically" "Warning"
    }
    
    Write-StatusMessage "✅ Prerequisites check passed" "Success"
    return $true
}

function Test-Dependencies {
    Write-StatusMessage "📦 Checking Python dependencies..." "Info"
    
    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"
    
    # Test required packages
    $required_packages = @("flask", "flask_cors", "flask_limiter", "chromadb", "pydantic")
    $missing_packages = @()
    
    foreach ($package in $required_packages) {
        try {
            & python -c "import $package" 2>$null
            if ($LASTEXITCODE -ne 0) {
                $missing_packages += $package
            }
        }
        catch {
            $missing_packages += $package
        }
    }
    
    if ($missing_packages.Count -gt 0) {
        Write-StatusMessage "❌ Missing packages: $($missing_packages -join ', ')" "Error"
        Write-StatusMessage "Installing missing dependencies..." "Info"
        
        try {
            & pip install -r requirements_api.txt
            Write-StatusMessage "✅ Dependencies installed successfully" "Success"
        }
        catch {
            Write-StatusMessage "❌ Failed to install dependencies" "Error"
            return $false
        }
    }
    
    Write-StatusMessage "✅ All dependencies are installed" "Success"
    return $true
}

function Start-APIServer {
    Write-StatusMessage "" "Info"
    Write-StatusMessage "========================================" "Info"
    Write-StatusMessage "   🚀 Starting Claude Memory API Server" "Info"
    Write-StatusMessage "========================================" "Info"
    Write-StatusMessage "" "Info"
    
    # Set environment variables
    $env:FLASK_ENV = if ($Debug) { "development" } else { "production" }
    $env:FLASK_DEBUG = if ($Debug) { "1" } else { "0" }
    $env:PYTHONPATH = Get-Location
    
    # Display server information
    Write-StatusMessage "📍 Server Configuration:" "Info"
    Write-StatusMessage "   - URL: http://${Host}:${Port}" "Info"
    Write-StatusMessage "   - Mode: $($env:FLASK_ENV)" "Info"
    Write-StatusMessage "   - Debug: $($env:FLASK_DEBUG)" "Info"
    Write-StatusMessage "   - Database: $(Get-Location)\chroma_db" "Info"
    Write-StatusMessage "" "Info"
    
    Write-StatusMessage "🔗 Available Endpoints:" "Info"
    Write-StatusMessage "   - POST /api/search           - Search memories" "Info"
    Write-StatusMessage "   - POST /api/add_memory       - Add new memory" "Info"
    Write-StatusMessage "   - GET  /api/health           - Health check" "Info"
    Write-StatusMessage "   - GET  /api/memories         - List memories" "Info"
    Write-StatusMessage "   - DELETE /api/memory/<id>    - Delete memory" "Info"
    Write-StatusMessage "   - POST /api/reindex          - Rebuild index" "Info"
    Write-StatusMessage "" "Info"
    
    Write-StatusMessage "💡 Quick Test Commands:" "Info"
    Write-StatusMessage "   curl -X GET http://${Host}:${Port}/api/health" "Info"
    Write-StatusMessage "   curl -X POST http://${Host}:${Port}/api/search -H 'Content-Type: application/json' -d '{\"query\":\"test\"}'" "Info"
    Write-StatusMessage "" "Info"
    
    Write-StatusMessage "⏸️  Press Ctrl+C to stop the server" "Warning"
    Write-StatusMessage "========================================" "Info"
    Write-StatusMessage "" "Info"
    
    # Start the server
    try {
        & python memory_api_server.py
    }
    catch {
        Write-StatusMessage "❌ Server startup failed: $($_.Exception.Message)" "Error"
        return $false
    }
    finally {
        Write-StatusMessage "" "Info"
        Write-StatusMessage "🛑 Server stopped." "Warning"
    }
    
    return $true
}

function Test-ServerHealth {
    if ($SkipHealthCheck) {
        return $true
    }
    
    Write-StatusMessage "🏥 Performing health check..." "Info"
    
    # Wait a moment for server to start
    Start-Sleep -Seconds 2
    
    try {
        $response = Invoke-RestMethod -Uri "http://${Host}:${Port}/api/health" -Method Get -TimeoutSec 10
        
        if ($response.success -eq $true) {
            Write-StatusMessage "✅ Health check passed" "Success"
            Write-StatusMessage "   - Status: $($response.data.status)" "Info"
            Write-StatusMessage "   - Document count: $($response.data.database.document_count)" "Info"
            return $true
        }
        else {
            Write-StatusMessage "❌ Health check failed: Server returned error" "Error"
            return $false
        }
    }
    catch {
        Write-StatusMessage "⚠️  Health check skipped: $($_.Exception.Message)" "Warning"
        return $true  # Continue anyway
    }
}

# Main execution
try {
    Write-StatusMessage "" "Info"
    Write-StatusMessage "========================================" "Info"
    Write-StatusMessage "   Claude Memory API Server Launcher" "Info"
    Write-StatusMessage "========================================" "Info"
    Write-StatusMessage "" "Info"
    
    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        exit 1
    }
    
    # Check dependencies
    if (-not (Test-Dependencies)) {
        exit 1
    }
    
    # Start server
    $success = Start-APIServer
    
    if (-not $success) {
        exit 1
    }
}
catch {
    Write-StatusMessage "❌ Unexpected error: $($_.Exception.Message)" "Error"
    exit 1
}
finally {
    Write-StatusMessage "" "Info"
    Write-StatusMessage "Press any key to exit..." "Info"
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}