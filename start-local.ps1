Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Starting Multichannel Commerce Operations (MCO) Locally  " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$root = $PSScriptRoot

# 1. Start Backend FastAPI in separate window
Write-Host "`n[1/2] Launching Backend API on http://127.0.0.1:8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\backend'; .venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

# 2. Start Frontend Vite in separate window
Write-Host "[2/2] Launching Frontend Dev Server on http://localhost:5173..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; pnpm dev"

Write-Host "`nAll services are starting up!" -ForegroundColor Green
Write-Host "  • Frontend App:   http://localhost:5173" -ForegroundColor White
Write-Host "  • Backend API:    http://127.0.0.1:8000/api/v1" -ForegroundColor White
Write-Host "  • Swagger Docs:   http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "==========================================================`n" -ForegroundColor Cyan
