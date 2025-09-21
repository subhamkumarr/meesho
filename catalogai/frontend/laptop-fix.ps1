# Laptop-Optimized UI Fix

Write-Host "Fixing UI for 15-inch laptop..." -ForegroundColor Green

docker stop $(docker ps -q) 2>$null
docker rm $(docker ps -aq) 2>$null

docker build -f Dockerfile.minimal -t catalogai-laptop .

if ($LASTEXITCODE -eq 0) {
    Write-Host "Starting laptop-optimized UI on http://localhost:3000" -ForegroundColor Green
    docker run -p 3000:3000 --name catalogai-laptop catalogai-laptop
} else {
    Write-Host "Build failed!" -ForegroundColor Red
}