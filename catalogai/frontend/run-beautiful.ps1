# Beautiful UI Fix Script

Write-Host "Building Beautiful UI..." -ForegroundColor Green

# Clean up
docker stop $(docker ps -q) 2>$null
docker rm $(docker ps -aq) 2>$null

# Build
docker build -f Dockerfile.minimal -t catalogai-beautiful .

if ($LASTEXITCODE -eq 0) {
    Write-Host "Starting Beautiful UI on http://localhost:3000" -ForegroundColor Green
    docker run -p 3000:3000 --name catalogai-beautiful catalogai-beautiful
} else {
    Write-Host "Build failed!" -ForegroundColor Red
}