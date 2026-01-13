#!/usr/bin/env pwsh
# AUTONOMOUS EXECUTION WRAPPER
# Routes all commands through privileged container
# OMNI-LOCK Protocol | Silent Execution

param(
    [Parameter(Mandatory=$false)]
    [string]$Command = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$Interactive
)

$ContainerName = "infinity-dev-container"

# Check if container is running
$containerStatus = docker ps -q -f name=$ContainerName 2>$null
if (-not $containerStatus) {
    Write-Host "Container not running. Starting Shadow-Box..." -ForegroundColor Yellow
    & "$PSScriptRoot\init-shadowbox.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to start container" -ForegroundColor Red
        exit 1
    }
}

# Execute command
if ($Interactive) {
    docker exec -it $ContainerName bash
} elseif ($Command) {
    docker exec $ContainerName bash -c "cd /workspace && $Command"
} else {
    # Default: Run main pipeline
    docker exec $ContainerName bash -c "cd /workspace && python main.py --daemon"
}

exit $LASTEXITCODE
