#!/usr/bin/env pwsh
# SHADOW-BOX INITIALIZATION SCRIPT
# Launches privileged container environment
# OMNI-LOCK Protocol | Silent Autonomous Execution

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 59 -ForegroundColor Cyan
Write-Host "INFINITY MASTER SYSTEM - SHADOW-BOX INITIALIZATION" -ForegroundColor Green
Write-Host "Container Virtualization | OS Guardrail Bypass Active" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 59 -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host "[1/5] Verifying Docker..." -ForegroundColor Cyan
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker not found"
    }
    Write-Host "  ✓ Docker detected: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Docker not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "ACTION REQUIRED:" -ForegroundColor Yellow
    Write-Host "  Install Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor White
    Write-Host "  Or run: winget install Docker.DockerDesktop" -ForegroundColor White
    exit 1
}

# Build container
Write-Host ""
Write-Host "[2/5] Building privileged container..." -ForegroundColor Cyan
Set-Location $PSScriptRoot
docker-compose build dev-environment
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Container build failed" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Container built successfully" -ForegroundColor Green

# Start container
Write-Host ""
Write-Host "[3/5] Starting container environment..." -ForegroundColor Cyan
docker-compose up -d dev-environment
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Container start failed" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Container running" -ForegroundColor Green

# Verify Ollama connectivity
Write-Host ""
Write-Host "[4/5] Verifying Ollama connectivity..." -ForegroundColor Cyan
$ollamaTest = docker exec infinity-dev-container curl -s http://host.docker.internal:11434/api/tags 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Ollama accessible via host.docker.internal" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Ollama not accessible (will start local instance)" -ForegroundColor Yellow
    docker-compose up -d ollama
    Start-Sleep -Seconds 5
}

# Install dependencies
Write-Host ""
Write-Host "[5/5] Installing dependencies in container..." -ForegroundColor Cyan
docker exec infinity-dev-container bash -c "cd /workspace && pip install -q -r requirements.txt"
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Some dependencies may need attention" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 59 -ForegroundColor Cyan
Write-Host "✓ SHADOW-BOX ACTIVE" -ForegroundColor Green
Write-Host ""
Write-Host "Container Status:" -ForegroundColor Cyan
Write-Host "  Name:     infinity-dev-container" -ForegroundColor White
Write-Host "  Mode:     Privileged / Network Host" -ForegroundColor White
Write-Host "  Mount:    /workspace -> $(Get-Location)" -ForegroundColor White
Write-Host "  Ollama:   host.docker.internal:11434" -ForegroundColor White
Write-Host ""
Write-Host "Execute commands via:" -ForegroundColor Cyan
Write-Host "  docker exec -it infinity-dev-container bash" -ForegroundColor White
Write-Host "  docker exec infinity-dev-container python main.py" -ForegroundColor White
Write-Host ""
Write-Host "VS Code will automatically attach to this container." -ForegroundColor Yellow
Write-Host "Reopen folder in container if prompted." -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 59 -ForegroundColor Cyan
