# PowerShell Module for Claude Memory API
# Import with: Import-Module E:\tools\claude-code-vector-memory\ClaudeMemory.psm1

$Global:ClaudeMemoryApiUrl = "http://localhost:8080"
$Global:ClaudeMemoryPath = "E:\tools\claude-code-vector-memory"

function Start-ClaudeMemoryAPI {
    <#
    .SYNOPSIS
    Start the Claude Memory API server
    .DESCRIPTION
    Starts the Claude Memory API server in a new PowerShell window
    .EXAMPLE
    Start-ClaudeMemoryAPI
    #>
    
    Write-Host "Starting Claude Memory API..." -ForegroundColor Cyan
    
    $startScript = @"
cd '$Global:ClaudeMemoryPath'
& '.\venv\Scripts\Activate.ps1'
python memory_api_server.py
"@
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $startScript
    
    # Wait a moment for startup
    Start-Sleep -Seconds 3
    
    # Check if started successfully
    if (Test-ClaudeMemoryAPI) {
        Write-Host "Claude Memory API started successfully" -ForegroundColor Green
        Write-Host "Available at: $Global:ClaudeMemoryApiUrl" -ForegroundColor Green
    } else {
        Write-Host "API may still be starting... check the PowerShell window" -ForegroundColor Yellow
    }
}

function Stop-ClaudeMemoryAPI {
    <#
    .SYNOPSIS
    Stop the Claude Memory API server
    .DESCRIPTION
    Stops any running Claude Memory API server processes
    .EXAMPLE
    Stop-ClaudeMemoryAPI
    #>
    
    Write-Host "Stopping Claude Memory API..." -ForegroundColor Yellow
    
    # Kill Python processes running the memory server
    Get-Process python -ErrorAction SilentlyContinue | 
        Where-Object { $_.MainWindowTitle -like "*memory_api_server*" } |
        Stop-Process -Force
    
    Write-Host "Claude Memory API stopped" -ForegroundColor Green
}

function Test-ClaudeMemoryAPI {
    <#
    .SYNOPSIS
    Test if the Claude Memory API is running
    .DESCRIPTION
    Checks if the Claude Memory API server is responding to health checks
    .EXAMPLE
    Test-ClaudeMemoryAPI
    .OUTPUTS
    Boolean - True if API is running, False otherwise
    #>
    
    try {
        $response = Invoke-RestMethod -Uri "$Global:ClaudeMemoryApiUrl/api/health" -TimeoutSec 5
        return $response.success -eq $true
    }
    catch {
        return $false
    }
}

function Get-ClaudeMemoryStatus {
    <#
    .SYNOPSIS
    Get the status of the Claude Memory API
    .DESCRIPTION
    Returns detailed status information about the Claude Memory API
    .EXAMPLE
    Get-ClaudeMemoryStatus
    #>
    
    Write-Host "Claude Memory API Status" -ForegroundColor Cyan
    Write-Host "=" * 40
    
    if (Test-ClaudeMemoryAPI) {
        try {
            $health = Invoke-RestMethod -Uri "$Global:ClaudeMemoryApiUrl/api/health"
            
            Write-Host "Status: " -NoNewline
            Write-Host "RUNNING" -ForegroundColor Green
            Write-Host "URL: $Global:ClaudeMemoryApiUrl"
            Write-Host "Documents: $($health.data.database.document_count)"
            Write-Host "Uptime: $([math]::Round($health.data.performance.uptime_seconds / 60, 1)) minutes"
            Write-Host "Requests: $($health.data.performance.total_requests)"
            Write-Host "Avg Response: $($health.data.performance.average_response_time_ms)ms"
        }
        catch {
            Write-Host "Status: " -NoNewline  
            Write-Host "PARTIAL" -ForegroundColor Yellow
            Write-Host "API responding but health check failed"
        }
    }
    else {
        Write-Host "Status: " -NoNewline
        Write-Host "STOPPED" -ForegroundColor Red
        Write-Host "Use Start-ClaudeMemoryAPI to start the service"
    }
}

function Search-ClaudeMemory {
    <#
    .SYNOPSIS
    Search Claude Memory API
    .DESCRIPTION
    Search for memories using the Claude Memory API
    .PARAMETER Query
    The search query text
    .PARAMETER MaxResults
    Maximum number of results to return (default: 3)
    .EXAMPLE
    Search-ClaudeMemory "react components"
    .EXAMPLE
    Search-ClaudeMemory -Query "python development" -MaxResults 5
    #>
    
    param(
        [Parameter(Mandatory=$true)]
        [string]$Query,
        
        [Parameter(Mandatory=$false)]
        [int]$MaxResults = 3
    )
    
    if (-not (Test-ClaudeMemoryAPI)) {
        Write-Host "Claude Memory API is not running" -ForegroundColor Red
        Write-Host "Start with: Start-ClaudeMemoryAPI" -ForegroundColor Yellow
        return
    }
    
    try {
        $searchRequest = @{
            query = $Query
            max_results = $MaxResults
        }
        
        $response = Invoke-RestMethod -Uri "$Global:ClaudeMemoryApiUrl/api/search" `
                                    -Method POST `
                                    -ContentType "application/json" `
                                    -Body ($searchRequest | ConvertTo-Json)
        
        if ($response.success) {
            Write-Host "Search Results for: '$Query'" -ForegroundColor Cyan
            Write-Host "Found $($response.data.total_results) results in $($response.data.search_time_ms)ms"
            Write-Host ""
            
            foreach ($result in $response.data.results) {
                Write-Host "Title: $($result.title)" -ForegroundColor Green
                Write-Host "   Date: $($result.date) | Similarity: $([math]::Round($result.similarity * 100, 1))%"
                Write-Host "   Technologies: $($result.metadata.technologies -join ", ")"
                Write-Host "   Preview: $($result.preview.Substring(0, [math]::Min(100, $result.preview.Length)))..."
                Write-Host ""
            }
        }
        else {
            Write-Host "Search failed: $($response.error.message)" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "Search error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Add-ClaudeMemory {
    <#
    .SYNOPSIS
    Add a new memory to Claude Memory API
    .DESCRIPTION
    Adds a new memory entry to the Claude Memory database
    .PARAMETER Content
    The content of the memory
    .PARAMETER Title
    The title of the memory
    .PARAMETER Technologies
    Array of technologies mentioned
    .EXAMPLE
    Add-ClaudeMemory -Content "Created a React component..." -Title "React Component Development"
    #>
    
    param(
        [Parameter(Mandatory=$true)]
        [string]$Content,
        
        [Parameter(Mandatory=$false)]
        [string]$Title = "PowerShell Memory Entry",
        
        [Parameter(Mandatory=$false)]
        [string[]]$Technologies = @()
    )
    
    if (-not (Test-ClaudeMemoryAPI)) {
        Write-Host "Claude Memory API is not running" -ForegroundColor Red
        return
    }
    
    try {
        $memoryRequest = @{
            content = $Content
            title = $Title
            source = "claude_code"
            technologies = $Technologies
            complexity = "medium"
        }
        
        $response = Invoke-RestMethod -Uri "$Global:ClaudeMemoryApiUrl/api/add_memory" `
                                    -Method POST `
                                    -ContentType "application/json" `
                                    -Body ($memoryRequest | ConvertTo-Json)
        
        if ($response.success) {
            Write-Host "Memory added successfully" -ForegroundColor Green
            Write-Host "ID: $($response.data.id)"
            Write-Host "Title: $($response.data.title)"
        }
        else {
            Write-Host "Failed to add memory: $($response.error.message)" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "Add memory error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Install-ClaudeMemoryStartup {
    <#
    .SYNOPSIS
    Install Claude Memory API to start automatically
    .DESCRIPTION
    Sets up the Claude Memory API to start automatically with Windows
    .EXAMPLE
    Install-ClaudeMemoryStartup
    #>
    
    Write-Host "Installing Claude Memory API auto-startup..." -ForegroundColor Cyan
    
    # Create startup script
    $startupScript = @"
# Auto-start Claude Memory API
Import-Module "$PSScriptRoot\ClaudeMemory.psm1"
Start-ClaudeMemoryAPI
"@
    
    $startupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\ClaudeMemoryAPI.ps1"
    $startupScript | Out-File -FilePath $startupPath -Encoding UTF8
    
    Write-Host "Startup script installed: $startupPath" -ForegroundColor Green
    Write-Host "Claude Memory API will start automatically with Windows" -ForegroundColor Green
}

# Export functions
Export-ModuleMember -Function Start-ClaudeMemoryAPI, Stop-ClaudeMemoryAPI, Test-ClaudeMemoryAPI, Get-ClaudeMemoryStatus, Search-ClaudeMemory, Add-ClaudeMemory, Install-ClaudeMemoryStartup

# Display help on import
Write-Host "Claude Memory API PowerShell Module Loaded" -ForegroundColor Cyan
Write-Host "Available commands:" -ForegroundColor Green
Write-Host "  Start-ClaudeMemoryAPI    - Start the API server"
Write-Host "  Stop-ClaudeMemoryAPI     - Stop the API server"
Write-Host "  Test-ClaudeMemoryAPI     - Check if API is running"
Write-Host "  Get-ClaudeMemoryStatus   - Show detailed status"
Write-Host "  Search-ClaudeMemory      - Search memories"
Write-Host "  Add-ClaudeMemory         - Add new memory"
Write-Host "  Install-ClaudeMemoryStartup - Setup auto-start"