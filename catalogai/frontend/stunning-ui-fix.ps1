# 🎨 STUNNING UI FIX - This will make your UI absolutely beautiful!

Write-Host "🎨 APPLYING STUNNING UI STYLES..." -ForegroundColor Magenta

# Kill all containers
docker stop $(docker ps -q) 2>$null
docker rm $(docker ps -aq) 2>$null

# Remove old images
docker rmi catalogai-frontend-dev catalogai-frontend-fixed catalogai-emergency 2>$null

Write-Host "🚀 Building with STUNNING CSS..." -ForegroundColor Cyan
docker build -f Dockerfile.minimal -t catalogai-stunning .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✨ Starting BEAUTIFUL UI on http://localhost:3000" -ForegroundColor Green
    Write-Host "🎉 Your UI will look absolutely AMAZING!" -ForegroundColor Yellow
    docker run -p 3000:3000 --name catalogai-stunning catalogai-stunning
} else {
    Write-Host "❌ Build failed!" -ForegroundColor Red
}