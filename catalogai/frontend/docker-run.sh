#!/bin/bash

# Build and run the frontend with Docker
echo "Building CatalogAI Frontend..."

# Build the Docker image
docker build -t catalogai-frontend .

# Run the container
echo "Starting frontend on http://localhost:3000"
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_BASE=http://localhost:8000 \
  -e NODE_ENV=development \
  --name catalogai-frontend-dev \
  --rm \
  catalogai-frontend

echo "Frontend stopped"