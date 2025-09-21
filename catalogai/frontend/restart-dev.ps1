# PowerShell script to restart the development server

Write-Host "Restarting CatalogAI Frontend..." -ForegroundColor Green

# Stop existing container
Write-Host "Stopping existing container..." -ForegroundColor Yellow
docker stop catalogai-frontend-dev 2>$null
docker rm catalogai-frontend-dev 2>$null

# Remove old image to force rebuild
Write-Host "Removing old image..." -ForegroundColor Yellow
docker rmi catalogai-frontend-dev 2>$null

# Build and run
Write-Host "Building and starting..." -ForegroundColor Green
docker build -f Dockerfile.minimal -t catalogai-frontend-dev .

if ($LASTEXITCODE -eq 0) {
    Write-Host "Starting on http://localhost:3000" -ForegroundColor Green
    docker run -p 3000:3000 --name catalogai-frontend-dev catalogai-frontend-dev
} else {
    Write-Host "Build failed!" -ForegroundColor Red
}