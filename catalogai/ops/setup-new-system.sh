#!/bin/bash
# CatalogAI New System Setup Script
# Run this on a fresh macOS/Linux system

echo "🚀 CatalogAI New System Setup"
echo "================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "\n📋 Checking Prerequisites..."

# Check Git
if command_exists git; then
    git_version=$(git --version)
    echo -e "${GREEN}✅ Git: $git_version${NC}"
else
    echo -e "${RED}❌ Git not found. Please install Git first.${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "${YELLOW}macOS: Install Xcode Command Line Tools or use Homebrew${NC}"
        echo -e "${YELLOW}brew install git${NC}"
    else
        echo -e "${YELLOW}Ubuntu/Debian: sudo apt-get install git${NC}"
        echo -e "${YELLOW}CentOS/RHEL: sudo yum install git${NC}"
    fi
    exit 1
fi

# Check Docker
if command_exists docker; then
    echo -e "${GREEN}✅ Docker found${NC}"
else
    echo -e "${RED}❌ Docker not found.${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "${YELLOW}macOS: Download Docker Desktop from https://www.docker.com/products/docker-desktop/${NC}"
    else
        echo -e "${YELLOW}Linux: Install Docker Engine${NC}"
        echo -e "${YELLOW}curl -fsSL https://get.docker.com -o get-docker.sh${NC}"
        echo -e "${YELLOW}sudo sh get-docker.sh${NC}"
        echo -e "${YELLOW}sudo usermod -aG docker \$USER${NC}"
    fi
    exit 1
fi

# Check Docker Compose
if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker Compose found${NC}"
else
    echo -e "${RED}❌ Docker Compose not found.${NC}"
    echo -e "${YELLOW}Please install Docker Compose${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${YELLOW}🐳 Docker is not running. Please start Docker Desktop or Docker service.${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "${YELLOW}Starting Docker Desktop...${NC}"
        open -a Docker
        echo -e "${YELLOW}Waiting for Docker Desktop to start (60 seconds)...${NC}"
        sleep 60
    else
        echo -e "${YELLOW}Starting Docker service...${NC}"
        sudo systemctl start docker
        sleep 10
    fi
fi

# Wait for Docker to be ready
echo -e "${YELLOW}⏳ Waiting for Docker to be ready...${NC}"
docker_ready=false
attempts=0
while [ "$docker_ready" = false ] && [ $attempts -lt 12 ]; do
    if docker version >/dev/null 2>&1; then
        docker_ready=true
        echo -e "${GREEN}✅ Docker is ready!${NC}"
    else
        sleep 5
        attempts=$((attempts + 1))
        echo -n "."
    fi
done

if [ "$docker_ready" = false ]; then
    echo -e "\n${RED}❌ Docker is not responding. Please ensure Docker is running.${NC}"
    exit 1
fi

# Setup project
echo -e "\n🏗️  Setting up CatalogAI..."

# Clean up any existing containers
echo -e "${YELLOW}Cleaning up existing containers...${NC}"
docker-compose down --remove-orphans 2>/dev/null || true
docker system prune -f 2>/dev/null || true

# Build and start containers
echo -e "${GREEN}Building and starting containers...${NC}"
if docker-compose up --build -d; then
    # Wait for services to be ready
    echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
    sleep 30
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        echo -e "${GREEN}✅ Services are running!${NC}"
        
        # Test endpoints
        echo -e "\n🧪 Testing endpoints..."
        if curl -s http://localhost:8000/health >/dev/null; then
            echo -e "${GREEN}✅ Backend health check passed${NC}"
        else
            echo -e "${YELLOW}⚠️  Backend health check failed, but container is running${NC}"
        fi
        
        if curl -s http://localhost:3000 >/dev/null; then
            echo -e "${GREEN}✅ Frontend is accessible${NC}"
        else
            echo -e "${YELLOW}⚠️  Frontend check failed, but container is running${NC}"
        fi
        
        echo -e "\n${CYAN}🎉 Setup Complete!${NC}"
        echo -e "${CYAN}================================${NC}"
        echo -e "${GREEN}Frontend: http://localhost:3000${NC}"
        echo -e "${GREEN}Backend:  http://localhost:8000${NC}"
        echo -e "${GREEN}API Docs: http://localhost:8000/docs${NC}"
        echo -e "\n${GREEN}You can now upload images and test authenticity detection!${NC}"
        
    else
        echo -e "${RED}❌ Some services failed to start. Check logs with: docker-compose logs${NC}"
    fi
else
    echo -e "${RED}❌ Failed to start containers${NC}"
    echo -e "${YELLOW}Try running: docker-compose logs${NC}"
fi

echo -e "\n${CYAN}📚 Useful Commands:${NC}"
echo -e "${WHITE}View logs:     docker-compose logs${NC}"
echo -e "${WHITE}Stop services: docker-compose down${NC}"
echo -e "${WHITE}Restart:       docker-compose restart${NC}"
echo -e "${WHITE}Status:        docker-compose ps${NC}"