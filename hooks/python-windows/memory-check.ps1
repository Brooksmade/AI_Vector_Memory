# Claude Code Hook - Check memory before file operations (PowerShell version)

# Get the JSON payload from stdin
$jsonPayload = [System.Console]::In.ReadToEnd()
$data = $jsonPayload | ConvertFrom-Json

# Extract tool name and file path
$toolName = $data.tool_name
$filePath = $data.tool_input.file_path

# If it's a file operation, check memory
if (($toolName -eq "Edit" -or $toolName -eq "Write" -or $toolName -eq "MultiEdit") -and $filePath) {
    # Call memory API to check for past issues
    $searchQuery = @{
        query = "$filePath error bug fix"
        max_results = 3
        similarity_threshold = 0.5
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8080/api/search" `
            -Method Post `
            -ContentType "application/json" `
            -Body $searchQuery
        
        if ($response.success) {
            $warnings = $response.data.results | Where-Object { 
                $_.similarity -gt 0.6 -and $_.preview -match "error"
            }
            
            if ($warnings) {
                foreach ($warning in $warnings) {
                    Write-Host "⚠️ Memory Warning: $($warning.title) ($($warning.date))"
                    Write-Host "   Preview: $($warning.preview.Substring(0, [Math]::Min(150, $warning.preview.Length)))..."
                }
                Write-Host ""
                Write-Host "💡 Consider checking the memory for past solutions before proceeding."
            }
        }
    } catch {
        # Silent fail - don't block operation
    }
}

exit 0