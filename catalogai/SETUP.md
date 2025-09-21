# CatalogAI Setup Guide

Complete setup instructions for running CatalogAI on any system.

## Prerequisites

### Required Software
- **Git** - Version control
- **Docker Desktop** - Container runtime
- **Node.js** (v18+) - For local development
- **Python** (3.11+) - For local development

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **OS**: Windows 10/11, macOS, or Linux

## Quick Start (Docker - Recommended)

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd catalogai
```

### 2. Install Docker Desktop
- **Windows**: Download from [docker.com](https://www.docker.com/products/docker-desktop/)
- **macOS**: Download from [docker.com](https://www.docker.com/products/docker-desktop/)
- **Linux**: Follow [Docker installation guide](https://docs.docker.com/engine/install/)

### 3. Start Docker Desktop
Make sure Docker Desktop is running before proceeding.

### 4. Run the Application
```bash
cd ops
docker-compose up --build -d
```

### 5. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 6. Verify Setup
```bash
# Check container status
docker-compose ps

# View logs if needed
docker-compose logs
```

## Local Development Setup

### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run initial setup**
```bash
cd ../data/seeds
python seed_run.py
cd ../../backend
```

5. **Start backend server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Start development server**
```bash
npm run dev
```

4. **Access application**
- Frontend: http://localhost:3000

## Troubleshooting

### Docker Issues

**Docker Desktop not starting:**
```bash
# Windows - Run as Administrator
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Wait 30 seconds, then try again
cd ops
docker-compose up --build -d
```

**Port conflicts:**
```bash
# Stop existing containers
docker-compose down

# Check what's using ports
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Kill processes if needed
taskkill /PID <process-id> /F
```

**Container build failures:**
```bash
# Clean Docker cache
docker system prune -a

# Rebuild from scratch
docker-compose up --build --force-recreate
```

### Local Development Issues

**Python dependencies:**
```bash
# Upgrade pip first
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v
```

**Node.js issues:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Model training fails:**
```bash
# Ensure you're in the right directory
cd data/seeds
python seed_run.py

# Check if artifacts are created
ls -la ../../backend/app/pipeline/artifacts/
```

## Environment Variables

Create `.env` files if needed:

### Backend (.env)
```env
DB_URL=sqlite:///app.db
THRESH_AUTH=0.15
THRESH_SYN=0.70
MAX_IMAGE_MB=8
LOG_LEVEL=INFO
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

## System-Specific Notes

### Windows
- Use PowerShell or Command Prompt
- Ensure Docker Desktop has WSL2 enabled
- May need to run as Administrator for Docker

### macOS
- Use Terminal
- Install Homebrew for easier package management
- Docker Desktop requires macOS 10.15+

### Linux
- Use terminal
- Install Docker Engine instead of Docker Desktop
- May need to add user to docker group:
```bash
sudo usermod -aG docker $USER
```

## Verification Steps

1. **Check all services are running:**
```bash
# Docker method
docker-compose ps

# Local method
curl http://localhost:8000/health
curl http://localhost:3000
```

2. **Test image upload:**
- Go to http://localhost:3000
- Upload a test image
- Verify you get authenticity results

3. **Check admin panel:**
- Go to http://localhost:3000/admin
- Verify threshold controls work
- Test model retraining

## Performance Tips

- **Docker**: Allocate at least 4GB RAM to Docker Desktop
- **Local**: Use SSD storage for better performance
- **Network**: Ensure stable internet for initial setup

## Getting Help

1. **Check logs:**
```bash
# Docker logs
docker-compose logs backend
docker-compose logs frontend

# Local logs
# Backend logs appear in terminal
# Frontend logs in browser console
```

2. **Common issues:**
- Port 3000/8000 already in use
- Docker Desktop not running
- Python/Node.js version incompatibility
- Missing dependencies

3. **Reset everything:**
```bash
# Docker reset
docker-compose down -v
docker system prune -a
docker-compose up --build

# Local reset
# Delete venv, node_modules
# Reinstall everything
```

## Next Steps

After successful setup:
1. Upload test images to verify functionality
2. Explore the admin panel for threshold tuning
3. Check the scans history page
4. Review API documentation at `/docs`

## Support

For issues not covered here:
1. Check the main README.md
2. Review RUNBOOK.md for operational details
3. Check GitHub issues
4. Contact the development team