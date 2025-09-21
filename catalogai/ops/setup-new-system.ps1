# CatalogAI New System Setup Script
# Run this on a fresh Windows system

Write-Host "🚀 CatalogAI New System Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "⚠️  Please run as Administrator for best results" -ForegroundColor Yellow
}

# Function to check if command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Check prerequisites
Write-Host "`n📋 Checking Prerequisites..." -ForegroundColor Green

# Check Git
if (Test-Command git) {
    $gitVersion = git --version
    Write-Host "✅ Git: $gitVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Git not found. Please install from: https://git-scm.com/" -ForegroundColor Red
    exit 1
}

# Check Docker
if (Test-Command docker) {
    Write-Host "✅ Docker found" -ForegroundColor Green
} else {
    Write-Host "❌ Docker not found. Installing Docker Desktop..." -ForegroundColor Yellow
    Write-Host "Please download and install Docker Desktop from:" -ForegroundColor Yellow
    Write-Host "https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    
    # Try to download Docker Desktop
    try {
        $dockerUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
        $dockerInstaller = "$env:TEMP\DockerDesktopInstaller.exe"
        Write-Host "Downloading Docker Desktop..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $dockerUrl -OutFile $dockerInstaller
        Write-Host "Starting Docker Desktop installer..." -ForegroundColor Yellow
        Start-Process -FilePath $dockerInstaller -Wait
        Write-Host "Please complete Docker Desktop installation and restart this script." -ForegroundColor Yellow
        exit 0
    } catch {
        Write-Host "Failed to download Docker Desktop. Please install manually." -ForegroundColor Red
        exit 1
    }
}

# Start Docker Desktop if not running
$dockerProcess = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
if (-not $dockerProcess) {
    Write-Host "🐳 Starting Docker Desktop..." -ForegroundColor Yellow
    try {
        Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        Write-Host "Waiting for Docker Desktop to start (60 seconds)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 60
    } catch {
        Write-Host "Could not start Docker Desktop automatically. Please start it manually." -ForegroundColor Yellow
    }
}

# Wait for Docker to be ready
Write-Host "⏳ Waiting for Docker to be ready..." -ForegroundColor Yellow
$dockerReady = $false
$attempts = 0
while (-not $dockerReady -and $attempts -lt 12) {
    try {
        docker version | Out-Null
        $dockerReady = $true
        Write-Host "✅ Docker is ready!" -ForegroundColor Green
    } catch {
        Start-Sleep -Seconds 5
        $attempts++
        Write-Host "." -NoNewline -ForegroundColor Yellow
    }
}

if (-not $dockerReady) {
    Write-Host "`n❌ Docker is not responding. Please ensure Docker Desktop is running." -ForegroundColor Red
    exit 1
}

# Setup project
Write-Host "`n🏗️  Setting up CatalogAI..." -ForegroundColor Green

# Clean up any existing containers
Write-Host "Cleaning up existing containers..." -ForegroundColor Yellow
docker-compose down --remove-orphans 2>$null
docker system prune -f 2>$null

# Build and start containers
Write-Host "Building and starting containers..." -ForegroundColor Green
try {
    docker-compose up --build -d
    
    # Wait for services to be ready
    Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    # Check if services are running
    $containers = docker-compose ps --services --filter "status=running"
    if ($containers -contains "backend" -and $containers -contains "frontend") {
        Write-Host "✅ All services are running!" -ForegroundColor Green
        
        # Test endpoints
        Write-Host "`n🧪 Testing endpoints..." -ForegroundColor Green
        try {
            $backendHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
            Write-Host "✅ Backend health check passed" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Backend health check failed, but container is running" -ForegroundColor Yellow
        }
        
        try {
            $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 10
            if ($frontendResponse.StatusCode -eq 200) {
                Write-Host "✅ Frontend is accessible" -ForegroundColor Green
            }
        } catch {
            Write-Host "⚠️  Frontend check failed, but container is running" -ForegroundColor Yellow
        }
        
        Write-Host "`n🎉 Setup Complete!" -ForegroundColor Cyan
        Write-Host "================================" -ForegroundColor Cyan
        Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
        Write-Host "Backend:  http://localhost:8000" -ForegroundColor Green
        Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green
        Write-Host "`nYou can now upload images and test authenticity detection!" -ForegroundColor Green
        
    } else {
        Write-Host "❌ Some services failed to start. Check logs with: docker-compose logs" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Failed to start containers: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Try running: docker-compose logs" -ForegroundColor Yellow
}

Write-Host "`n📚 Useful Commands:" -ForegroundColor Cyan
Write-Host "View logs:     docker-compose logs" -ForegroundColor White
Write-Host "Stop services: docker-compose down" -ForegroundColor White
Write-Host "Restart:       docker-compose restart" -ForegroundColor White
Write-Host "Status:        docker-compose ps" -ForegroundColor White