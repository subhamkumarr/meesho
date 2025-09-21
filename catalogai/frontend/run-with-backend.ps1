# Run Frontend with Backend Connection

Write-Host "Starting Frontend with Backend Connection..." -ForegroundColor Green

# Stop existing containers
docker stop catalogai-laptop catalogai-backend 2>$null
docker rm catalogai-laptop catalogai-backend 2>$null

# Start backend first
Write-Host "Starting Backend..." -ForegroundColor Yellow
docker run -d --name catalogai-backend -p 8000:8000 -e DB_URL=sqlite:///app.db -e THRESH_AUTH=0.15 -e THRESH_SYN=0.70 -e MAX_IMAGE_MB=8 -e LOG_LEVEL=INFO catalogai-backend

# Wait for backend to start
Start-Sleep -Seconds 5

# Build and start frontend
Write-Host "Building Frontend..." -ForegroundColor Yellow
docker build -f Dockerfile.minimal -t catalogai-laptop .

Write-Host "Starting Frontend connected to Backend..." -ForegroundColor Green
docker run -p 3000:3000 --name catalogai-laptop --link catalogai-backend:backend -e NEXT_PUBLIC_API_BASE=http://localhost:8000 catalogai-laptop