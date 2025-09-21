# Fix Docker Desktop and run containers
Write-Host "Fixing Docker issues..." -ForegroundColor Yellow

# Check if Docker Desktop is running
$dockerProcess = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
if (-not $dockerProcess) {
    Write-Host "Starting Docker Desktop..." -ForegroundColor Green
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Write-Host "Waiting for Docker Desktop to start (30 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
}

# Clean up any existing containers/images
Write-Host "Cleaning up existing containers..." -ForegroundColor Yellow
docker-compose down --remove-orphans 2>$null
docker system prune -f 2>$null

# Build and start fresh
Write-Host "Building and starting containers..." -ForegroundColor Green
docker-compose up --build -d

# Check status
Write-Host "Container status:" -ForegroundColor Cyan
docker-compose ps