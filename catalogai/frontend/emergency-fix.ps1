# EMERGENCY CSS FIX - This will work!

Write-Host "EMERGENCY CSS FIX - Restarting with working styles..." -ForegroundColor Red

# Kill everything
docker stop $(docker ps -q) 2>$null
docker rm $(docker ps -aq) 2>$null

# Build fresh
Write-Host "Building with emergency CSS..." -ForegroundColor Yellow
docker build -f Dockerfile.minimal -t catalogai-emergency .

# Run
Write-Host "Starting with WORKING CSS on http://localhost:3000" -ForegroundColor Green
docker run -p 3000:3000 catalogai-emergency