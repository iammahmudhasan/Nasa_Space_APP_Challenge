@echo off
echo ===================================================================
echo     Launching NASA Earth Intelligence Agent (NEIA) System
echo     NASA Space Apps Challenge 2026 - Autonomous Scientific Agent
echo ===================================================================

echo [1/2] Starting Python FastAPI Backend on port 8000...
start "NEIA Backend" cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 8000"

echo [2/2] Starting React Vite Frontend on port 5173...
start "NEIA Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo All services launched!
echo Backend API docs: http://localhost:8000/docs
echo Frontend UI:      http://localhost:5173
echo ===================================================================
