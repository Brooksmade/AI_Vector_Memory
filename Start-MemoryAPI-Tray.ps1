# Claude Memory API Server - System Tray Launcher
# This script starts the Claude Memory API server as a system tray application
# The server runs in the background without showing a console window

param(
    [switch]$Debug,
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
    Write-StatusMessage "🔍 Checking prerequisites for system tray mode..." "Info"
    
    # Check if we're in the right directory
    if (-not (Test-Path "memory_api_tray.py")) {
        Write-StatusMessage "❌ Error: memory_api_tray.py not found in current directory!" "Error"
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
    
    # Check if tray dependencies are installed
    Write-StatusMessage "📦 Checking system tray dependencies..." "Info"
    & ".\venv\Scripts\python.exe" -c "import pystray, PIL, plyer" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-StatusMessage "⚠️  Installing system tray dependencies..." "Warning"
        & ".\venv\Scripts\pip.exe" install -r requirements_api.txt
        if ($LASTEXITCODE -ne 0) {
            Write-StatusMessage "❌ Failed to install tray dependencies" "Error"
            return $false
        }
    }
    
    # Check database directory
    if (-not (Test-Path "chroma_db")) {
        Write-StatusMessage "⚠️  Warning: ChromaDB directory not found - will be created automatically" "Warning"
    }
    
    Write-StatusMessage "✅ Prerequisites check passed" "Success"
    return $true
}

function Start-TrayApplication {
    Write-StatusMessage "" "Info"
    Write-StatusMessage "========================================" "Info"
    Write-StatusMessage "   🔔 Starting System Tray Mode" "Info"
    Write-StatusMessage "========================================" "Info"
    Write-StatusMessage "" "Info"
    
    # Set environment variables
    $env:API_HOST = $Host
    $env:API_PORT = $Port
    $env:FLASK_ENV = if ($Debug) { "development" } else { "production" }
    $env:FLASK_DEBUG = if ($Debug) { "1" } else { "0" }
    $env:PYTHONPATH = Get-Location
    
    # Display configuration
    Write-StatusMessage "📍 System Tray Configuration:" "Info"
    Write-StatusMessage "   - Server URL: http://${Host}:${Port}" "Info"
    Write-StatusMessage "   - Mode: System Tray (Background)" "Info"
    Write-StatusMessage "   - Debug: $($env:FLASK_DEBUG)" "Info"
    Write-StatusMessage "   - Database: $(Get-Location)\chroma_db" "Info"
    Write-StatusMessage "" "Info"
    
    Write-StatusMessage "🔔 System Tray Features:" "Info"
    Write-StatusMessage "   - Hidden console window" "Info"
    Write-StatusMessage "   - System tray icon with status indicator" "Info"
    Write-StatusMessage "   - Right-click menu for controls" "Info"
    Write-StatusMessage "   - Automatic health monitoring" "Info"
    Write-StatusMessage "   - Windows notifications" "Info"
    Write-StatusMessage "" "Info"
    
    Write-StatusMessage "💡 Usage Instructions:" "Info"
    Write-StatusMessage "   - Look for the tray icon in your system notification area" "Info"
    Write-StatusMessage "   - Right-click the icon for options (Status, Start/Stop, Logs)" "Info"
    Write-StatusMessage "   - Double-click the icon to view server status" "Info"
    Write-StatusMessage "   - Green icon = Running, Red = Stopped, Yellow = Starting" "Info"
    Write-StatusMessage "" "Info"
    
    Write-StatusMessage "🚀 Launching system tray application..." "Info"
    Write-StatusMessage "========================================" "Info"
    Write-StatusMessage "" "Info"
    
    # Start the tray application
    try {
        # This will run in background and hide the console
        & ".\venv\Scripts\python.exe" "memory_api_tray.py"
    }
    catch {
        Write-StatusMessage "❌ Failed to start tray application: $($_.Exception.Message)" "Error"
        return $false
    }
    
    return $true
}

# Main execution
try {
    Write-StatusMessage "" "Info"
    Write-StatusMessage "========================================" "Info"
    Write-StatusMessage "   Claude Memory API - System Tray Mode" "Info"
    Write-StatusMessage "========================================" "Info"
    Write-StatusMessage "" "Info"
    
    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-StatusMessage "" "Info"
        Write-StatusMessage "Press any key to exit..." "Info"
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
    
    # Start tray application
    $success = Start-TrayApplication
    
    if (-not $success) {
        Write-StatusMessage "" "Info"
        Write-StatusMessage "Press any key to exit..." "Info"
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
}
catch {
    Write-StatusMessage "❌ Unexpected error: $($_.Exception.Message)" "Error"
    Write-StatusMessage "" "Info"
    Write-StatusMessage "Press any key to exit..." "Info"
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}