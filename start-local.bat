@echo off
title Launch MCO Local Services
echo ==========================================================
echo   Starting Multichannel Commerce Operations (MCO) Locally
echo ==========================================================

echo.
echo [1/2] Starting Backend API on http://127.0.0.1:8000...
start "MCO Backend (FastAPI)" cmd /k "cd /d "%~dp0backend" && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo [2/2] Starting Frontend Dev Server on http://localhost:5173...
start "MCO Frontend (Vite)" cmd /k "cd /d "%~dp0frontend" && pnpm dev"

echo.
echo ==========================================================
echo   All services launched!
echo   - Frontend:    http://localhost:5173
echo   - Backend API: http://127.0.0.1:8000/api/v1
echo   - Swagger:     http://127.0.0.1:8000/docs
echo ==========================================================
