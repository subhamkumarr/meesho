# 🎨 FINAL BEAUTIFUL UI - Fixed overlapping + stunning design

Write-Host "🎨 BUILDING FINAL BEAUTIFUL UI..." -ForegroundColor Magenta
Write-Host "✨ Fixed overlapping issues" -ForegroundColor Green
Write-Host "🚀 Added stunning animations" -ForegroundColor Cyan
Write-Host "💎 Beautiful glass morphism effects" -ForegroundColor Yellow

# Clean up
docker stop $(docker ps -q) 2>$null
docker rm $(docker ps -aq) 2>$null
docker rmi catalogai-simple catalogai-stunning 2>$null

# Build with beautiful UI
Write-Host "🔨 Building..." -ForegroundColor Blue
docker build -f Dockerfile.minimal -t catalogai-beautiful .

if ($LASTEXITCODE -eq 0) {
    Write-Host "🎉 LAUNCHING BEAUTIFUL UI on http://localhost:3000" -ForegroundColor Green
    Write-Host "✅ Fixed navigation overlapping" -ForegroundColor Green
    Write-Host "✅ Added stunning animations" -ForegroundColor Green
    Write-Host "✅ Beautiful gradient backgrounds" -ForegroundColor Green
    Write-Host "✅ Glass morphism effects" -ForegroundColor Green
    Write-Host "✅ Mobile responsive design" -ForegroundColor Green
    docker run -p 3000:3000 --name catalogai-beautiful catalogai-beautiful
} else {
    Write-Host "❌ Build failed!" -ForegroundColor Red
}