# NASA Earth Intelligence Agent (NEIA) - PowerShell Launcher
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "    Launching NASA Earth Intelligence Agent (NEIA) System" -ForegroundColor Green
Write-Host "    NASA Space Apps Challenge 2026 - Autonomous Scientific Agent" -ForegroundColor White
Write-Host "===================================================================" -ForegroundColor Cyan

Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn app.main:app --reload --port 8000"
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "Services initialized:" -ForegroundColor Yellow
Write-Host "  Backend API:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Frontend App: http://localhost:5173" -ForegroundColor Green
Write-Host "===================================================================" -ForegroundColor Cyan
