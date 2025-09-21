#!/bin/bash

echo "Building and running CatalogAI Frontend in development mode..."

# Stop and remove existing container if it exists
docker stop catalogai-frontend-dev 2>/dev/null || true
docker rm catalogai-frontend-dev 2>/dev/null || true

# Build the development image
echo "Building development image..."
docker build -f Dockerfile.dev -t catalogai-frontend-dev .

# Run the container
echo "Starting frontend on http://localhost:3000"
echo "API will connect to http://localhost:8000 (make sure backend is running)"

docker run -it \
  --name catalogai-frontend-dev \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_BASE=http://localhost:8000 \
  -e NODE_ENV=development \
  catalogai-frontend-dev

echo "Frontend stopped"