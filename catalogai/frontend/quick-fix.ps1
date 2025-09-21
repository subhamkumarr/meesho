# QUICK FIX - Simple working UI

Write-Host "QUICK FIX - Building simple working UI..." -ForegroundColor Green

docker stop $(docker ps -q) 2>$null
docker rm $(docker ps -aq) 2>$null

docker build -f Dockerfile.minimal -t catalogai-simple .
docker run -p 3000:3000 --name catalogai-simple catalogai-simple