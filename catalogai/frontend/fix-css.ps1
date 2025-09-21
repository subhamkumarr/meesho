# PowerShell script to fix CSS and restart frontend

Write-Host "Fixing CSS and restarting frontend..." -ForegroundColor Green

# Stop existing container
Write-Host "Stopping existing container..." -ForegroundColor Yellow
docker stop catalogai-frontend-dev 2>$null
docker rm catalogai-frontend-dev 2>$null

# Remove old images to force rebuild
Write-Host "Removing old images..." -ForegroundColor Yellow
docker rmi catalogai-frontend-dev 2>$null
docker rmi catalogai-frontend-minimal 2>$null

# Build with the minimal Dockerfile
Write-Host "Building with fixed CSS..." -ForegroundColor Green
docker build -f Dockerfile.minimal -t catalogai-frontend-fixed .

if ($LASTEXITCODE -eq 0) {
    Write-Host "Starting frontend with fixed CSS on http://localhost:3000" -ForegroundColor Green
    docker run -p 3000:3000 --name catalogai-frontend-dev catalogai-frontend-fixed
} else {
    Write-Host "Build failed!" -ForegroundColor Red
}