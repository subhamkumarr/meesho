# PowerShell script to run CatalogAI Frontend in development mode

Write-Host "Building and running CatalogAI Frontend in development mode..." -ForegroundColor Green

# Stop and remove existing container if it exists
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker stop catalogai-frontend-dev 2>$null
docker rm catalogai-frontend-dev 2>$null

# Build the development image
Write-Host "Building development image (no cache)..." -ForegroundColor Yellow
docker rmi catalogai-frontend-dev 2>$null
docker build --no-cache -f Dockerfile.simple -t catalogai-frontend-dev .

if ($LASTEXITCODE -eq 0) {
    # Run the container
    Write-Host "Starting frontend on http://localhost:3000" -ForegroundColor Green
    Write-Host "API will connect to http://localhost:8000 (make sure backend is running)" -ForegroundColor Cyan
    
    docker run -it --name catalogai-frontend-dev -p 3000:3000 -e NEXT_PUBLIC_API_BASE=http://localhost:8000 -e NODE_ENV=development catalogai-frontend-dev
} else {
    Write-Host "Build failed!" -ForegroundColor Red
}

Write-Host "Frontend stopped" -ForegroundColor Yellow