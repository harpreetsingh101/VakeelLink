# VakeelLink PowerShell Launcher
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "         Starting VakeelLink AI Legal Platform          " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$backendDir = Join-Path $PSScriptRoot "Vakeel-link-main\backend"
Set-Location $backendDir

Write-Host "Launching server at http://127.0.0.1:8000 ..." -ForegroundColor Green
Start-Process "http://127.0.0.1:8000"

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
