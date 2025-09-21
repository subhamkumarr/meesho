# Complete Solution - Run both Frontend and Backend

Write-Host "Starting Complete CatalogAI Application..." -ForegroundColor Green

# Navigate to ops directory and run docker-compose
cd ..\ops

Write-Host "Starting Backend and Frontend together..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "Application started!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Backend Health: http://localhost:8000/health/" -ForegroundColor Cyan

# Show logs
Write-Host "Showing logs (Ctrl+C to exit)..." -ForegroundColor Yellow
docker-compose logs -f